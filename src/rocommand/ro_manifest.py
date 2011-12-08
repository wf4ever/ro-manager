# ro_manifest.py

"""
Research Object manifest read, write, decode functions
"""

import sys
import os
import os.path
import urlparse
import logging

log = logging.getLogger(__name__)

import rdflib
import rdflib.namespace
#from rdflib import URIRef, Namespace, BNode
#from rdflib import Literal

import ro_settings

class Namespace(object):
    def __init__(self, baseUri):
        self.baseUri = baseUri
        return

def makeNamespace(baseUri, names):
    ns = Namespace(baseUri)
    for name in names:
        setattr(ns, name, rdflib.URIRef(baseUri+name))
    return ns

oxds    = rdflib.URIRef("http://vocab.ox.ac.uk/dataset/schema#")
dcterms = rdflib.URIRef("http://purl.org/dc/terms/")
roterms = rdflib.URIRef("http://ro.example.org/ro/terms/")

RDF     = makeNamespace(rdflib.namespace.RDF.uri,
            [ "Seq", "Bag", "Alt", "Statement", "Property", "XMLLiteral", "List", "PlainLiteral"
            , "subject", "predicate", "object", "type", "value", "first", "rest"
            , "nil"
            ])
RDFS    = makeNamespace(rdflib.namespace.RDFS.uri,
            [ "Resource", "Class", "subClassOf", "subPropertyOf", "comment", "label"
            , "domain", "range", "seeAlso", "isDefinedBy", "Literal", "Container"
            , "ContainerMembershipProperty", "member", "Datatype"
            ])
OXDS    = makeNamespace(oxds, ["Grouping"])
DCTERMS = makeNamespace(dcterms, 
            [ "identifier", "description", "title", "creator", "created"
            , "subject", "format", "type"
            ])
ROTERMS = makeNamespace(roterms, 
            [ "note"
            ])

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

def writeManifestGraph(rodir, rograph):
    """
    Write manifest file for research object given RDF graph of contents
    """
    manifestfilename = makeManifestFilename(rodir)
    rograph.serialize(destination=manifestfilename, format='xml', base=getRoUri(rodir), xml_base="..")
    return

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

def getRoUri(ro_dir):
    return rdflib.URIRef("file://"+os.path.abspath(ro_dir)+"/")

def getComponentUri(ro_dir, path):
    #log.debug("getComponentUri: ro_dir %s, path %s"%(ro_dir, path))
    return rdflib.URIRef(urlparse.urljoin(getRoUri(ro_dir), path))
    #return rdflib.URIRef("file://"+os.path.normpath(os.path.join(os.path.abspath(ro_dir), path)))

def getComponentUriRel(ro_dir, path):
    #log.debug("getComponentUriRel: ro_dir %s, path %s"%(ro_dir, path))
    file_uri = urlparse.urlunsplit(urlparse.urlsplit(getComponentUri(ro_dir, path)))
    ro_uri   = urlparse.urlunsplit(urlparse.urlsplit(getRoUri(ro_dir)))
    #log.debug("getComponentUriRel: ro_uri %s, file_uri %s"%(ro_uri, file_uri))
    if ro_uri is not None and file_uri.startswith(ro_uri):
        file_uri_rel = file_uri.replace(ro_uri, "", 1)
    else:
        file_uri_rel = path
    #log.debug("getComponentUriRel: file_uri_rel %s"%(file_uri_rel))
    return file_uri_rel

def getGraphRoUri(rodir, rograph):
    return str(rograph.value(None, RDF.type, OXDS.Grouping))

# End.
