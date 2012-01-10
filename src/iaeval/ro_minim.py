# ro_manifest.py

"""
Research Object manifest read, write, decode functions
"""

#import sys
#import os
#import os.path
#import re
import urlparse
import logging

log = logging.getLogger(__name__)

#import MiscLib.ScanDirectories

import rdflib
import rdflib.namespace
#from rdflib import URIRef, Namespace, BNode
#from rdflib import Literal

#import ro_settings

from rocommand import ro_manifest

minim   = rdflib.URIRef("http://purl.org/minim/minim#")

MINIM   = ro_manifest.makeNamespace(minim,
            [ "Constraint", "Model", "Requirement", "RequirementRule", "SoftwareSupport"
            , "hasConstraint", "forPurpose", "onResource", "toModel"
            , "hasMustRequirement", "hasShouldRequirement", "hasMayRequirement", "hasRequirement"
            , "isDerivedBy"
            , "aggregatePresent", "derivesRequirement"
            , "environment", "command", "response"
            ])


def getElementUri(minimbase, elemname):
    """
    Returns URI of element in Minim file
    
    minimbase   is the URI of the Minim file containing the required element
    elemname    is the relative URI of the element - commonly a fragment identifier
    """
    #log.debug("getElementUri: ro_dir %s, path %s"%(ro_dir, path))
    return rdflib.URIRef(urlparse.urljoin(str(minimbase), elemname))
    #return rdflib.URIRef("file://"+os.path.normpath(os.path.join(os.path.abspath(ro_dir), path)))

def readMinimGraph(minimuri):
    """
    Read Minim file, return RDF Graph.
    """
    minimgraph = rdflib.Graph()
    minimgraph.parse(minimuri)
    return minimgraph

# End.
