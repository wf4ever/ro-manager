# ro_manifest.py

"""
Research Object manifest read, write, decode functions
"""

import os.path

import rdflib
from rdflib.namespace import RDF
#from rdflib import URIRef, Namespace, BNode
#from rdflib import Literal

import ro_settings

class Namespace(object):
    def __init__(self):
        return

def makeNamespace(baseUri, names):
    ns = Namespace()
    for name in names:
        setattr(ns, name, rdflib.URIRef(baseUri+name))
    return ns

oxds    = rdflib.URIRef("http://vocab.ox.ac.uk/dataset/schema#")
dcterms = rdflib.URIRef("http://purl.org/dc/terms/")

OXDS    = makeNamespace(oxds, ["Grouping"])
DCTERMS = makeNamespace(dcterms, ["identifier", "description", "title", "creator", "created"])

def makeManifestFilename(rodir):
    return os.path.join(rodir, ro_settings.MANIFEST_DIR+"/", ro_settings.MANIFEST_FILE)

def readManifestGraph(rodir):
    """
    Read manifest file for research object, return RDF Graph of manifest values.
    """
    manifestfilename = makeManifestFilename(rodir)
    rdfGraph = rdflib.Graph()
    rdfGraph.parse(manifestfilename)
    return rdfGraph

def readManifest(rodir):
    """
    Read manifest file for research object, return dictionary of manifest values.
    """
    rdfGraph = readManifestGraph(rodir)
    subject  = rdfGraph.value(None, RDF.type, OXDS.Grouping)
    strsubject = ""
    if isinstance(subject, rdflib.URIRef): strsubject = str(subject)
    manifestDict = {
        'ropath':         rodir,
        'rouri':          strsubject,
        'roident':        rdfGraph.value(subject, DCTERMS.identifier,  None),
        'rotitle':        rdfGraph.value(subject, DCTERMS.title,       None),
        'rocreator':      rdfGraph.value(subject, DCTERMS.creator,     None),
        'rocreated':      rdfGraph.value(subject, DCTERMS.created,     None),
        'rodescription':  rdfGraph.value(subject, DCTERMS.description, None),
        }
    return manifestDict

# End.
