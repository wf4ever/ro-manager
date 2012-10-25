# ro_eval_minim.py

"""
Research Object evaluation withj respoect to a MINIM description
"""

#import sys
#import os
#import os.path
#import urlparse
import re
import subprocess
import logging

log = logging.getLogger(__name__)

import rdflib
#import rdflib.namespace
#from rdflib import URIRef, Namespace, BNode
#from rdflib import Literal
from uritemplate import uritemplate

from rocommand.ro_uriutils   import isLiveUri
from rocommand.ro_namespaces import RDF, RDFS, ORE
from rocommand.ro_metadata   import ro_metadata
import ro_minim
from ro_minim import MINIM

def evaluate(rometa, minim, target, purpose):
    """
    Evaluate a RO against a minimum information model for a particular
    purpose with respect to a particular target resource.

    rometa      is an ro_metadata object used to access the RO being evaluated
    minim       is a URI-reference (relative to the RO, or absolute) of the
                minim description to be used.
    target      is a URI-reference (relative to the RO, or absolute) of a 
                target resource with respect to which the evaluation is
                performed.
    purpose     is a string that identifies a purpose w.r.t. the target for
                which completeness will be evaluated.
                
    'target' and 'purpose' are ued together to select a particular minim Model
    that will be used for the evaluation.  For example, to evaluate whether an 
    RO is sufficiently complete to support creation (a purpose) of a specified
    output file (a target).
    
    There are two main steps to the evaluation process:
    1. locate the minim model constraint for the target resource and purpose
    2. evaluate the RO against the selected model.
    
    The result indicates a summary and details of the analysis; e.g.
    { 'summary':       [MINIM.fullySatisfies, MINIM.nominallySatisfies, MINIM.minimallySatisfies]
    , 'missingMust':   []
    , 'missingShould': []
    , 'missingMay':    []
    , 'rouri':          rouri
    , 'minimuri':       minim
    , 'target':         target
    , 'purpose':        purpose
    , 'constrainturi':  constraint['uri']
    , 'modeluri':       model['uri']
    }
    """
    # Locate the constraint model requirements
    rouri        = rometa.getRoUri()
    minimuri     = rometa.getComponentUri(minim)
    minimgraph   = ro_minim.readMinimGraph(minimuri)
    constraint   = ro_minim.getConstraint(minimgraph, rouri, target, purpose)
    assert constraint != None, "Missing minim:Constraint for target %s, purpose %s"%(target, purpose)
    model        = ro_minim.getModel(minimgraph, constraint['model'])
    assert model != None, "Missing minim:Model for target %s, purpose %s"%(target, purpose)
    requirements = ro_minim.getRequirements(minimgraph, model['uri'])
    # Evaluate the individual model requirements
    reqeval = []
    for r in requirements:
        if 'datarule' in r:
            # @@TODO: factor to separate function?
            satisfied = rometa.roManifestContains( (rouri, ORE.aggregates, r['datarule']['aggregates']) )
            reqeval.append((r,satisfied,{}))
            log.debug("- %s: %s"%(repr((rouri, ORE.aggregates, r['datarule']['aggregates'])), satisfied))
        elif 'softwarerule' in r:
            # @@TODO: factor to separate function
            cmnd = r['softwarerule']['command']
            resp = r['softwarerule']['response']
            log.debug("softwarerule: %s -> %s"%(cmnd,resp))
            out = unicode(subprocess.check_output(cmnd.split(), stderr=subprocess.STDOUT))
            exp = re.compile(resp)
            satisfied = exp.match(out)
            reqeval.append((r,satisfied,{}))
            log.debug("- Software %s: response %s,  satisfied %s"%(cmnd, resp, "OK" if satisfied else "Fail"))
        elif 'contentmatchrule' in r:
            (satisfied, bindings) = evalContentMatch(rometa, r['contentmatchrule'])
            reqeval.append((r,satisfied,bindings))
            log.debug("- ContentMatch: rule %s, bindings %s, satisfied %s"%
                      (repr(r['contentmatchrule']), repr(bindings), "OK" if satisfied else "Fail"))
        else:
            raise ValueError("Unrecognized requirement rule: %s"%repr(r.keys()))
    # Evaluate overall satisfaction of model
    sat_levels = (
        { 'MUST':   MINIM.minimallySatisfies
        , 'SHOULD': MINIM.nominallySatisfies
        , 'MAY':    MINIM.fullySatisfies
        })
    eval_result = (
        { 'summary':        []
        , 'missingMust':    []
        , 'missingShould':  []
        , 'missingMay':     []
        , 'satisfied':      []
        , 'rouri':          rouri
        , 'minimuri':       minimuri
        , 'target':         target
        , 'purpose':        purpose
        , 'constrainturi':  constraint['uri']
        , 'modeluri':       model['uri']
        })
    for (r, satisfied, binding) in reqeval:
        if satisfied:
            eval_result['satisfied'].append((r, binding))
        else:
            if r['level'] == "MUST":
                eval_result['missingMust'].append((r, binding))
                sat_levels['MUST']   = None
                sat_levels['SHOULD'] = None
                sat_levels['MAY']    = None
            elif r['level'] == "SHOULD":
                eval_result['missingShould'].append((r, binding))
                sat_levels['SHOULD'] = None
                sat_levels['MAY']    = None
            elif r['level'] == "MAY":
                eval_result['missingMay'].append((r, binding))
                sat_levels['MAY'] = None
    eval_result['summary'] = [ sat_levels[k] for k in sat_levels if sat_levels[k] ]
    return (minimgraph, eval_result)

def evalContentMatch(rometa, rule):
    querytemplate = """
        PREFIX rdf:        <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs:       <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl:        <http://www.w3.org/2002/07/owl#>
        PREFIX xsd:        <http://www.w3.org/2001/XMLSchema#>
        PREFIX xml:        <http://www.w3.org/XML/1998/namespace>
        PREFIX ro:         <http://purl.org/wf4ever/ro#>
        PREFIX wfprov:     <http://purl.org/wf4ever/wfprov#>
        PREFIX wfdesc:     <http://purl.org/wf4ever/wfdesc#>
        PREFIX rdfg:       <http://www.w3.org/2004/03/trix/rdfg-1/>
        PREFIX ore:        <http://www.openarchives.org/ore/terms/>
        PREFIX ao:         <http://purl.org/ao/>
        PREFIX dcterms:    <http://purl.org/dc/terms/>
        PREFIX foaf:       <http://xmlns.com/foaf/0.1/>

        %(queryverb)s
        {
          %(querypattern)s
        }
        """
    satisfied     = True
    simplebinding = {}
    if rule['forall']:
        exists   = rule['exists']
        template = rule['template']
        islive   = rule['islive']
        assert (exists or template or islive), (
            "minim:forall construct requires "+
            "minim:aggregatesTemplate, minim:isLiveTemplate and/or minim:exists value")
        queryparams = (
            { 'queryverb': "SELECT * WHERE"
            , 'querypattern': rule['forall']
            })
        query = querytemplate%queryparams
        resp  = rometa.queryAnnotations(query)
        for binding in resp:
            satisfied = False
            # Extract keys and values from query result
            simplebinding = {}
            for k in binding:
                ###print "key: "+repr(k) 
                if not isinstance(k,rdflib.BNode):
                    simplebinding[str(k)] = str(binding[k])
                    # @@TODO remove this when rdflib bug resolved 
                    if str(k) in ['if', 'of'] and str(binding[k])[:5] not in ["file:","http:"]:
                        # Houston, we have a problem...
                        agraph = rometa.roannotations
                        print "--------------------"
                        print "Graph: "+agraph.serialize(format="xml")
                        print "Query: "+query
                        print "Response bindings: "+repr(resp)
                        print "--------------------"
                        assert False, "Aborted"
            if exists:
                # existence query against forall results
                existsparams = (
                    { 'queryverb': "ASK"
                    , 'querypattern': exists
                    })
                query = querytemplate%existsparams
                log.debug("***** evalContentMatch RO test exists: \nquery: %s \nbinding: %s)"%(query, repr(binding)))
                satisfied = rometa.queryAnnotations(query,initBindings=binding)
            if template:
                # Construct URI for file from template
                # Uses code copied from http://code.google.com/p/uri-templates
                fileref = uritemplate.expand(template, simplebinding)
                fileuri = rometa.getComponentUri(fileref)
                # Test if URI is aggregated
                log.debug("evalContentMatch RO aggregates %s (%s)"%(fileref, str(fileuri)))
                satisfied = rometa.roManifestContains( (rometa.getRoUri(), ORE.aggregates, fileuri) )
            if islive:
                # Construct URI for file from template
                # Uses code copied from http://code.google.com/p/uri-templates
                fileref = uritemplate.expand(islive, simplebinding)
                fileuri = rometa.getComponentUri(fileref)
                # Test if URI is live (accessible)
                log.debug("evalContentMatch RO islive %s (%s)"%(fileref, str(fileuri)))
                satisfied = isLiveUri(fileuri)
            log.debug("evalContentMatch (forall) RO satisfied %s"%(satisfied))
            if not satisfied: break
    elif rule['exists']:
        queryparams = (
            { 'queryverb': "ASK"
            , 'querypattern': rule['exists']
            })
        query = querytemplate%queryparams
        satisfied = rometa.queryAnnotations(query)
    else:
        raise ValueError("Unrecognized content match rule: %s"%repr(rule))
    return (satisfied,simplebinding)

def format(eval_result, options, ostr):
    """
    Formats a completeness evaluation report, and writes it to the supplied stream.
    
    eval_result is the result of evaluation from ro_eval_completeness.evaluate
    options     a dictionary that provides options to control the formatting (see below)
    ostr        is a stream to which the formatted result is written

    options currently has just one field:
    options['detail'] = "summary", "must", "should", "may" or "full"
    """
    s_any     = ["full", "may", "should", "must", "summary"]
    s_must    = ["full", "may", "should", "must"]
    s_should  = ["full", "may", "should"]
    s_may     = ["full", "may"]
    s_full    = ["full"]
    def put(detail, line):
        if options['detail'] in detail:
            ostr.write(line)
            ostr.write("\n")
        return
    put(s_any, "Research Object %(rouri)s:"%eval_result)
    summary_text= ( "Fully complete"     if MINIM.fullySatisfies     in eval_result['summary'] else
                    "Nominally complete" if MINIM.nominallySatisfies in eval_result['summary'] else
                    "Minimally complete" if MINIM.minimallySatisfies in eval_result['summary'] else
                    "Incomplete")
    put(s_any, summary_text+" for %(purpose)s of resource %(target)s"%(eval_result))
    if eval_result['missingMust']:
        put(s_must, "Unsatisfied MUST requirements:")
        for m in eval_result['missingMust']:
            put(s_must, "  "+formatRule(False, *m))
    if eval_result['missingShould']:
        put(s_should, "Unsatisfied SHOULD requirements:")
        for m in eval_result['missingShould']:
            put(s_should, "  "+formatRule(False, *m))
    if eval_result['missingMay']:
        put(s_may, "Unsatisfied MAY requirements:")
        for m in eval_result['missingMay']:
            put(s_may, "  "+formatRule(False, *m))
    if eval_result['satisfied']:
        put(s_full, "Satisfied requirements:")
        for m in eval_result['satisfied']:
            put(s_full, "  "+formatRule(True, *m))
    put(s_full, "Research object URI:     %(rouri)s"%(eval_result))
    put(s_full, "Minimum information URI: %(minimuri)s"%(eval_result))
    return

def formatRule(satisfied, rule, bindings):
    """
    Format a rule for a missing/satisfied report
    """
    templateindex = "showpass" if satisfied else "showfail"
    if 'datarule' in rule:
        ruledict = rule['datarule']
        templatedefault = "Aggregates resource %(aggregates)s"
    elif 'softwarerule' in rule:
        ruledict = rule['softwarerule']
        templatedefault = "Environment '%(command)s' matches '%(response)s'"
    elif 'contentmatchrule' in rule:
        ruledict = rule['contentmatchrule']
        if ruledict['exists']:
            templatedefault = "Match for %(exists)s"
        else:
            templatedefault = "Aggregate %(template)s for matching %(forall)s"
    else:
        ruledict = { 'rule': repr(rule), 'show': None, templateindex: None }
        templatedefault = "Unrecognized rule: %(rule)s"
    template = ruledict[templateindex] or ruledict["show"] or templatedefault
    bindings.update(ruledict)
    return template%bindings

# End.
