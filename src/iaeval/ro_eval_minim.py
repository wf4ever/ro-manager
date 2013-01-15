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

from rocommand.ro_uriutils   import isLiveUri, resolveUri
from rocommand.ro_namespaces import RDF, RDFS, ORE, DCTERMS
from rocommand.ro_metadata   import ro_metadata
import ro_minim
from ro_minim import MINIM, RESULT

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
    
    The function returns a pair of values (minimgraph, evalresult)
    
    minimgraph is a cpy of the minim graph on which the evaluation was based.
    
    The evalresult indicates a summary and details of the analysis; e.g.
      { 'summary':        [MINIM.fullySatisfies, MINIM.nominallySatisfies, MINIM.minimallySatisfies]
      , 'missingMust':    []
      , 'missingShould':  []
      , 'missingMay':     []
      , 'rouri':          rouri
      , 'roid':           roid
      , 'description':    rodesc
      , 'minimuri':       minim
      , 'target':         target
      , 'purpose':        purpose
      , 'constrainturi':  constraint['uri']
      , 'modeluri':       model['uri']
      }
    """
    # Locate the constraint model requirements
    rouri        = rometa.getRoUri()
    roid         = rometa.getResourceValue(rouri, DCTERMS.identifier)
    if roid == None:
        roid = str(rouri)
        if roid.endswith('/'): roid = roid[0:-1]
        roid = roid.rpartition('/')[2]
    rodesc       = ( rometa.getResourceValue(rouri, DCTERMS.description) or
                     rometa.getResourceValue(rouri, DCTERMS.title) or
                     roid )
    minimuri     = rometa.getComponentUri(minim)
    minimgraph   = ro_minim.readMinimGraph(minimuri)
    constraint   = ro_minim.getConstraint(minimgraph, rouri, target, purpose)
    cbindings    = { 'targetro':   constraint['targetro_actual']
                   , 'targetres':  constraint['targetres_actual']
                   , 'onresource': constraint['onresource_actual']
                   }
    assert constraint != None, "Missing minim:Constraint for target %s, purpose %s"%(target, purpose)
    model        = ro_minim.getModel(minimgraph, constraint['model'])
    assert model != None, "Missing minim:Model for target %s, purpose %s"%(target, purpose)
    requirements = ro_minim.getRequirements(minimgraph, model['uri'])
    # Evaluate the individual model requirements
    reqeval = []
    for r in requirements:
        log.info("evaluate: %s %s"%(r['level'],str(r['uri'])))
        if 'datarule' in r:
            # @@TODO: factor to separate function?
            #         (This is a deprecated form, as it locks the rule to a particular resource)
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
            log.debug("- Software %s: response %s,  satisfied %s"%
                      (cmnd, resp, "OK" if satisfied else "Fail"))
        elif 'contentmatchrule' in r:
            (satisfied, bindings) = evalContentMatch(rometa, r['contentmatchrule'], cbindings)
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
        , 'roid':           roid
        , 'description':    rodesc
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

def evalResultGraph(graph, evalresult):
    """
    This function combines the results from the evaluate function (above) to return
    a single RDF result graph that is the result of the checklist evaluation service, 
    and also is returned when RDF output is requested by 'ro evaluate checklist'.
    
    graph       is the minim graph used for the evaluation.
                The supplied graph is updated and returned by this function.
    evalresult  is the evaluation result returned by the evaluation
    """
    graph.bind("rdf",     RDF.baseUri)
    graph.bind("rdfs",    RDFS.baseUri)
    graph.bind("dcterms", DCTERMS.baseUri)
    graph.bind("result",  RESULT.baseUri)
    graph.bind("minim",   MINIM.baseUri)
    rouri     = rdflib.URIRef(evalresult['rouri'])
    targeturi = rdflib.URIRef(resolveUri(evalresult['target'], evalresult['rouri']))
    graph.add( (rouri, DCTERMS.identifier,     rdflib.Literal(evalresult['roid']))         )
    graph.add( (rouri, RDFS.label,             rdflib.Literal(evalresult['roid']))         )
    graph.add( (rouri, DCTERMS.description,    rdflib.Literal(evalresult['description']))  )
    graph.add( (rouri, MINIM.testedConstraint, rdflib.URIRef(evalresult['constrainturi'])) )
    graph.add( (rouri, MINIM.testedPurpose,    rdflib.Literal(evalresult['purpose']))      )
    graph.add( (rouri, MINIM.testedTarget,     targeturi)                                  )
    graph.add( (rouri, MINIM.minimUri,         rdflib.URIRef(evalresult['minimuri']))      )
    graph.add( (rouri, MINIM.modelUri,         rdflib.URIRef(evalresult['modeluri']))      )
    for level in evalresult['summary']:
        log.info("RO %s, level %s, model %s"%(rouri,level,evalresult['modeluri']))
        graph.add( (rouri, level, rdflib.URIRef(evalresult['modeluri'])) )
    # Add details for all items tested...
    def addRequirementsDetail(satisfied, results, satlevel):
        for (req, binding) in results:
            b = rdflib.BNode()
            msg = formatRule(satisfied, req, binding)
            graph.add( (rouri, satlevel, b) )
            graph.add( (b, MINIM.tryRequirement, req['uri']) )
            graph.add( (b, MINIM.tryMessage, rdflib.Literal(msg)) )
            for k in binding:
                b2 = rdflib.BNode()
                graph.add( (b,  RESULT.binding,  b2) )
                graph.add( (b2, RESULT.variable, rdflib.Literal(k)) )
                graph.add( (b2, RESULT.value,    rdflib.Literal(binding[k])) )
    addRequirementsDetail(True,  evalresult['satisfied'], MINIM.satisfied)
    addRequirementsDetail(False, evalresult['missingMay'], MINIM.missingMay)
    addRequirementsDetail(False, evalresult['missingShould'], MINIM.missingShould)
    addRequirementsDetail(False, evalresult['missingMust'], MINIM.missingMust)
    return graph

def evalContentMatch(rometa, rule, constraintbinding):
    """
    rometa      ro_metadata for RO to test
    rule        requirement rule to evaluate
    constraintbinding
                value bindings generated by constraint matching:
                'targetro', 'targetres' and 'onresource'
    """
    log.debug("evalContentMatch: rule: \n  %s, \nconstraintbinding:\n  %s"%(repr(rule), repr(constraintbinding)))
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
    simplebinding = constraintbinding.copy()
    if rule['forall']:
        exists   = rule['exists']
        template = rule['template']
        islive   = rule['islive']
        assert (exists or template or islive), (
            "minim:forall construct requires "+
            "minim:aggregatesTemplate, minim:isLiveTemplate and/or minim:exists value")
        if template:  template = str(template).strip()
        if islive:    islive   = str(islive).strip()
        queryparams = (
            { 'queryverb': "SELECT * WHERE"
            , 'querypattern': rule['forall']
            })
        query = querytemplate%queryparams
        log.debug(" - forall query: "+query)
        ### @@TODO: Why is this failing?
        # resp  = rometa.queryAnnotations(query, initBindings=constraintbinding)
        resp  = rometa.queryAnnotations(query)
        log.debug(" - forall resp: "+repr(resp))
        for binding in resp:
            satisfied = False
            # Extract keys and values from query result to return with result
            simplebinding = constraintbinding.copy()
            for k in binding:
                if not isinstance(k,rdflib.BNode):
                    simplebinding[str(k)] = str(binding[k])
                    # @@TODO remove this when rdflib bug resolved 
                    if str(k) in ['if', 'of'] and str(binding[k])[:5] not in ["file:","http:"]:
                        # Houston, we have a problem...
                        agraph = rometa.roannotations
                        log.warning( "--------------------" )
                        log.debug( "Graph: "+agraph.serialize(format="xml") )
                        log.warning( "Query: "+query )
                        log.warning( "Response bindings: "+repr(resp) )
                        log.warning( "--------------------" )
                        ### assert False, "Aborted"
            if exists:
                # existence query against forall results
                existsparams = (
                    { 'queryverb': "ASK"
                    , 'querypattern': exists
                    })
                query = querytemplate%existsparams
                log.debug("evalContentMatch RO test exists: \nquery: %s \nbinding: %s"%
                          (query, repr(binding)))
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
        log.debug("- query %s"%(query))
        satisfied = rometa.queryAnnotations(query)
        log.debug("- satisfied %s"%(satisfied))
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
