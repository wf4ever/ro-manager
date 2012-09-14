# ro_manifest.py

"""
Research Object manifest read, write, decode functions
"""

import sys
import os
import os.path
import re
import urlparse
import urllib
import logging

log = logging.getLogger(__name__)

import MiscLib.ScanDirectories

import rdflib
###import rdflib.namespace
#from rdflib import URIRef, Namespace, BNode
#from rdflib import Literal

import ro_settings
from ro_namespaces import RDF, DCTERMS, RO, AO, ORE

def makeManifestFilename(rodir):
    return os.path.join(rodir, ro_settings.MANIFEST_DIR+"/", ro_settings.MANIFEST_FILE)

def readManifestGraph(rodir):
    """
    Read manifest file for research object, return RDF Graph of manifest values.
    """
    manifestfilename = makeManifestFilename(rodir)
    log.debug("readManifestGraph: "+manifestfilename)
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
    ro_graph = readManifestGraph(ro_dir)
    subject  = getRoUri(ro_dir)
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

def old_getRoUri(ro_dir):
    return getFileUri(os.path.abspath(ro_dir)+"/")

def getRoUri(roref):
    uri = roref
    if urlparse.urlsplit(uri).scheme == "":
        base = "file://"+urllib.pathname2url(os.path.abspath(os.getcwd()))+"/"
        uri  = urlparse.urljoin(base, urllib.pathname2url(roref))
    if not uri.endswith("/"): uri += "/" 
    return rdflib.URIRef(uri)

def getComponentUri(ro_dir, path):
    """
    Return URI for component where relative reference is treated as a file path
    """
    if urlparse.urlsplit(path).scheme == "":
        path = urlparse.urljoin(str(getRoUri(ro_dir)), urllib.pathname2url(path))
    return rdflib.URIRef(path)

def getComponentUriAbs(ro_dir, path):
    """
    Return absolute URI for component where relative reference is treated as a URI reference
    """
    return rdflib.URIRef(urlparse.urljoin(str(getRoUri(ro_dir)), path))

def getComponentUriRel(ro_dir, path):
    #log.debug("getComponentUriRel: ro_dir %s, path %s"%(ro_dir, path))
    file_uri = urlparse.urlunsplit(urlparse.urlsplit(str(getComponentUriAbs(ro_dir, path))))
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
