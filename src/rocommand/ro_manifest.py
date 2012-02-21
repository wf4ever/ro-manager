# ro_manifest.py

"""
Research Object manifest read, write, decode functions
"""

import sys
import os
import os.path
import re
import urlparse
import logging

log = logging.getLogger(__name__)

import MiscLib.ScanDirectories

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

#oxds    = rdflib.URIRef("http://vocab.ox.ac.uk/dataset/schema#")
dcterms = rdflib.URIRef("http://purl.org/dc/terms/")
roterms = rdflib.URIRef("http://ro.example.org/ro/terms/")
ao      = rdflib.URIRef("http://purl.org/ao/")
ore     = rdflib.URIRef("http://www.openarchives.org/ore/terms/")
foaf    = rdflib.URIRef("http://xmlns.com/foaf/0.1/")
ro      = rdflib.URIRef("http://purl.org/wf4ever/ro#")
wfprov  = rdflib.URIRef("http://purl.org/wf4ever/wfprov#")
wfdesc  = rdflib.URIRef("http://purl.org/wf4ever/wfdesc#")

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
#@@TODO: remove this...
#OXDS    = makeNamespace(oxds, ["Grouping"])
DCTERMS = makeNamespace(dcterms, 
            [ "identifier", "description", "title", "creator", "created"
            , "subject", "format", "type"
            ])
#@@TODO: remove this...
ROTERMS = makeNamespace(roterms, 
            [ "note", "resource"
            ])
RO = makeNamespace(ro, 
            [ "ResearchObject", "AggregatedAnnotation"
            , "annotatesAggregatedResource"
            ])
ORE = makeNamespace(ore, 
            [ "Aggregation", "AggregatedResource"
            , "aggregates"
            ])
AO = makeNamespace(ao, 
            [ "Annotation"
            , "body"
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
    subject  = rdfGraph.value(None, RDF.type, RO.ResearchObject)
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

def notHidden(f):
    return re.match("\.|.*/\.", f) == None

def addAggregatedResources(ro_dir, ro_file, recurse=True):
    log.debug("addAggregatedResources: dir %s, file %s"%(ro_dir, ro_file))
    ro_graph = readManifestGraph(ro_dir)
    if ro_file.endswith(os.path.sep):
        ro_file = ro_file[0:-1]
    rofiles = [ro_file]
    if os.path.isdir(ro_file):
        rofiles = filter( notHidden,
                            MiscLib.ScanDirectories.CollectDirectoryContents(
                                os.path.abspath(ro_file), baseDir=os.path.abspath(ro_dir), 
                                listDirs=False, listFiles=True, recursive=recurse, appendSep=False)
                        )
    s = getComponentUri(ro_dir, ".")
    for f in rofiles:
        log.debug("- file %s"%f)
        stmt = (s, ORE.aggregates, getComponentUri(ro_dir, f))
        if stmt not in ro_graph: ro_graph.add(stmt)
    writeManifestGraph(ro_dir, ro_graph)
    return

def getAggregatedResources(ro_dir):
    """
    Returns iterator over all resources aggregated by a manifest.
    
    Each value returned by the iterator is a resource URI.
    """
    ro_graph = ro_manifest.readManifestGraph(ro_dir)
    subject  = ro_manifest.getRoUri(ro_dir)
    log.debug("getAggregatedResources %s"%str(subject))
    for r in ro_graph.objects(subject=subject, predicate=ORE.aggregates):
        yield r
    return

def getFileUri(path):
    """
    Like getComponentUri, except that path may be relative to the current directory
    """
    filebase = "file://"
    if not path.startswith(filebase):
        path = filebase+os.path.join(os.getcwd(), path)
    return rdflib.URIRef(path)

def getUriFile(uri):
    """
    Return file path string corresponding to supplied RO or RO component URI
    """
    filebase = "file://"
    uri = str(uri)
    if uri.startswith(filebase):
        uri = uri[len(filebase):]
    return uri

def getRoUri(ro_dir):
    return getFileUri(os.path.abspath(ro_dir)+"/")

def getComponentUri(ro_dir, path):
    #log.debug("getComponentUri: ro_dir %s, path %s"%(ro_dir, path))
    return rdflib.URIRef(urlparse.urljoin(str(getRoUri(ro_dir)), path))
    #return rdflib.URIRef("file://"+os.path.normpath(os.path.join(os.path.abspath(ro_dir), path)))

def getComponentUriRel(ro_dir, path):
    #log.debug("getComponentUriRel: ro_dir %s, path %s"%(ro_dir, path))
    file_uri = urlparse.urlunsplit(urlparse.urlsplit(str(getComponentUri(ro_dir, path))))
    ro_uri   = urlparse.urlunsplit(urlparse.urlsplit(str(getRoUri(ro_dir))))
    #log.debug("getComponentUriRel: ro_uri %s, file_uri %s"%(ro_uri, file_uri))
    if ro_uri is not None and file_uri.startswith(ro_uri):
        file_uri_rel = file_uri.replace(ro_uri, "", 1)
    else:
        file_uri_rel = path
    #log.debug("getComponentUriRel: file_uri_rel %s"%(file_uri_rel))
    return rdflib.URIRef(file_uri_rel)

def getGraphRoUri(rodir, rograph):
    """
    Extract graph URI from supplied manifest graph
    """
    return rograph.value(None, RDF.type, RO.ResearchObject)

# End.
