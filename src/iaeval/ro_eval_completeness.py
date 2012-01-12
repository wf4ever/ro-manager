# ro_manifest.py

"""
Research Object manifest read, write, decode functions
"""

#import sys
#import os
#import os.path
#import re
#import urlparse
import logging

log = logging.getLogger(__name__)

#import rdflib
#import rdflib.namespace
#from rdflib import URIRef, Namespace, BNode
#from rdflib import Literal

from rocommand import ro_manifest
from rocommand.ro_manifest import RDF, RDFS, ORE
import ro_minim
from ro_minim import MINIM

def evaluate(rodir, minim, target, purpose):
    """
    Evaluate a RO against a minimuminformation model for a particular
    purpose with respect to a particular targetresource.
    
    There are two main steps top this process:
    1. locate the minim model constraint for the target resource and purpose
    2. evaluate the RO against the selected model.
    
    The result indicates a summary and details of the analysis; e.g.
    { 'summary':       [MINIM.fullySatisfies, MINIM.nominallySatisfies, MINIM.minimallySatisfies]
    , 'missingMust':   []
    , 'missingShould': []
    , 'missingMay':    []
    }
    """
    # Locate the constraint model requirements
    rouri        = ro_manifest.getRoUri(rodir)
    rograph      = ro_manifest.readManifestGraph(rodir)
    minimuri     = ro_manifest.getComponentUri(rodir, minim)
    minimgraph   = ro_minim.readMinimGraph(minimuri)
    constraint   = ro_minim.getConstraint(minimgraph, rodir, target, purpose)
    assert constraint != None, "Missing minim:Constraint for target %s, purpose %s"%(target, purpose)
    model        = ro_minim.getModel(minimgraph, constraint['model'])
    assert model != None, "Missing minim:Model for target %s, purpose %s"%(target, purpose)
    requirements = ro_minim.getRequirements(minimgraph, model['uri'])
    # Evaluate the individual model requirements
    reqeval = []
    for r in requirements:
        if 'datarule' in r:
            satisfied = (rouri, ORE.aggregates, r['datarule']['aggregates']) in rograph
            reqeval.append((r,satisfied))
            log.debug("- %s: %s"%(repr((rouri, ORE.aggregates, r['datarule']['aggregates'])), satisfied))
    # Evaluate overall satisfaction of model
    sat_levels = (
        { 'MUST':   MINIM.minimallySatisfies
        , 'SHOULD': MINIM.nominallySatisfies
        , 'MAY':    MINIM.fullySatisfies
        })
    eval_result = (
        { 'summary':       []
        , 'missingMust':   []
        , 'missingShould': []
        , 'missingMay':    []
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

# End.
