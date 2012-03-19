# ro_eval_completeness.py

"""
Research Object manifest read, write, decode functions
"""

#import sys
#import os
#import os.path
#import urlparse
import re
import subprocess
import logging

log = logging.getLogger(__name__)

#import rdflib
#import rdflib.namespace
#from rdflib import URIRef, Namespace, BNode
#from rdflib import Literal

from rocommand.ro_namespaces import RDF, RDFS, ORE
from rocommand.ro_metadata  import ro_metadata
import ro_minim
from ro_minim import MINIM

def evaluate(rometa, minim, target, purpose):
    """
    Evaluate a RO against a minimuminformation model for a particular
    purpose with respect to a particular targetresource.

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
    constraint   = ro_minim.getConstraint(minimgraph, rometa.getRoDir(), target, purpose)
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
            reqeval.append((r,satisfied))
            log.debug("- %s: %s"%(repr((rouri, ORE.aggregates, r['datarule']['aggregates'])), satisfied))
        elif 'softwarerule' in r:
            # @@TODO: factor to separate function
            cmnd = r['softwarerule']['command']
            resp = r['softwarerule']['response']
            out = unicode(subprocess.check_output(cmnd.split(), stderr=subprocess.STDOUT))
            exp = re.compile(resp)
            satisfied = exp.match(out)
            reqeval.append((r,satisfied))
            log.debug("- Software %s: response %s,  satisfied %s"%(cmnd, resp, "OK" if satisfied else "Fail"))
        elif 'contentmatchrule' in r:
            satisfied = evalContentMatch(rometa, r['contentmatchrule'])
            reqeval.append((r,satisfied))
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
        , 'rodir':          rometa.getRoDir()
        , 'rouri':          rouri
        , 'minimuri':       minimuri
        , 'target':         target
        , 'purpose':        purpose
        , 'constrainturi':  constraint['uri']
        , 'modeluri':       model['uri']
        })
    for (r, satisfied) in reqeval:
        if not satisfied:
            if r['level'] == "MUST":
                eval_result['missingMust'].append(r)
                sat_levels['MUST']   = False
                sat_levels['SHOULD'] = False
                sat_levels['MAY']    = False
            elif r['level'] == "SHOULD":
                eval_result['missingShould'].append(r)
                sat_levels['SHOULD'] = False
                sat_levels['MAY']    = False
            elif r['level'] == "MAY":
                eval_result['missingMay'].append(r)
                sat_levels['MAY'] = False
    eval_result['summary'] = [ sat_levels[k] for k in sat_levels if sat_levels[k] ]
    return eval_result

def evalContentMatch(rometa, rule):
    querytemplate = """
        @prefix rdf:        <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        @prefix rdfs:       <http://www.w3.org/2000/01/rdf-schema#>
        @prefix owl:        <http://www.w3.org/2002/07/owl#>
        @prefix xsd:        <http://www.w3.org/2001/XMLSchema#>
        @prefix xml:        <http://www.w3.org/XML/1998/namespace>
        @prefix ro:         <http://purl.org/wf4ever/ro#>
        @prefix wfprov:     <http://purl.org/wf4ever/wfprov#>
        @prefix wfdesc:     <http://purl.org/wf4ever/wfdesc#>
        @prefix rdfg:       <http://www.w3.org/2004/03/trix/rdfg-1/>
        @prefix ore:        <http://www.openarchives.org/ore/terms/>
        @prefix ao:         <http://purl.org/ao/>
        @prefix dcterms:    <http://purl.org/dc/terms/>
        @prefix foaf:       <http://xmlns.com/foaf/0.1/>

        %(queryverb)s
        {
          %(querypattern)s
        }
        """
    if rule['exists']:
        queryparams = (
            { 'queryverb': "ASK"
            , 'querypattern': rule['exists']
            })

@@@@@@ add query methods to ro_metadata; manifest, annotations, all?  @@@@@@@@

    elif rule['forall']:
        queryparams = (
            { 'queryverb': "SELECT * WHERE"
            , 'querypattern': rule['exists']
            })
        ...
    else:
        raise ValueError("Unrecognized content match rule: %s"%repr(rule))
    assert False, "@@TODO implement evalContentMatch"
    return satisfied

def format(eval_result, options, ostr):
    """
    Formats a completeness evaluation report, and writes it to the supplied stream.
    
    eval_result is the result of evaluation from ro_eval_completeness.evaluate
    options     a dictionary that provides options to control the formatting (see below)
    ostr        is a stream to which the formatted result is written

    options currently has just one field:
    options['detail'] = "summary" or "full"
    
    More options may be introduced later.
    """
    any  = ["summary","full"]
    full = ["full"]
    def put(detail, line):
        if options['detail'] in detail:
            ostr.write(line)
            ostr.write("\n")
        return
    put(any, "Research Object %(rodir)s:"%eval_result)
    summary_text= ( "Fully complete"     if MINIM.fullySatisfies     in eval_result['summary'] else
                    "Nominally complete" if MINIM.nominallySatisfies in eval_result['summary'] else
                    "Minimally complete" if MINIM.minimallySatisfies in eval_result['summary'] else
                    "Incomplete")
    put(any, summary_text+" for %(purpose)s of resource %(target)s"%(eval_result))
    for m in eval_result['missingMust']:
        put(full, "Missing MUST resource:   %s"%(m['datarule']['aggregates']))
    for m in eval_result['missingShould']:
        put(full, "Missing SHOULD resource: %s"%(m['datarule']['aggregates']))
    for m in eval_result['missingMay']:
        put(full, "Missing MAY resource:    %s"%(m['datarule']['aggregates']))
    put(full, "Research object URI:     %(rouri)s"%(eval_result))
    put(full, "Minimum information URI: %(minimuri)s"%(eval_result))
    return

# End.
