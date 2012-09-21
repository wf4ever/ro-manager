# ro_metadata.py

"""
Research Object metadata (manifest and annotations) access class
"""

import sys
import os
import os.path
import re
import urllib
import urlparse
import logging

log = logging.getLogger(__name__)

import MiscLib.ScanDirectories

import rdflib
import rdflib.namespace
#from rdflib import Namespace, URIRef, BNode, Literal
# Set up to use SPARQL
#rdflib.plugin.register(
#    'sparql', rdflib.query.Processor,
#    'rdfextras.sparql.processor', 'Processor')
#rdflib.plugin.register(
#    'sparql', rdflib.query.Result,
#    'rdfextras.sparql.query', 'SPARQLQueryResult')

import ro_settings
from ro_namespaces import RDF, RO, ORE, AO, DCTERMS, RDFS
from ro_uriutils import isFileUri, resolveUri, resolveFileAsUri, getFilenameFromUri, isLiveUri, retrieveUri
import ro_manifest
import ro_annotation
import json
import urllib2
import tempfile

# Class for ROSRS errors

class ROSRS_Error(Exception):

    def __init__(self, msg="ROSRS_Error", value=None, srsuri=None):
        self._msg    = msg
        self._value  = value
        self._srsuri = srsuri
        return

    def __str__(self):
        txt = self._msg
        if self._srsuri: txt += " for "+str(self._srsuri)
        if self._value:  txt += ": "+repr(self._value)
        return txt

    def __repr__(self):
        return ( "ROSRS_Error(%s, value=%s, srsuri=%s)"%
                 (repr(self._msg), repr(self._value), repr(self._srsuri)))

def createRO(httpsession, roid, title = None, creator = None, date = None):
    """
    Create a new RO, return (status, reason, uri, manifest):
        roid        can be provided as an alternative to rouri if the Research Object
                    needs to be created
    status+reason: 201 Created or 409 Exists
    uri+manifest: URI and copy of manifest as RDF graph if 201 status,
                  otherwise None and response data as diagnostic

    NOTE: this method has been adapted from TestApi_ROSRS
    """
    reqheaders   = {
        "slug":     roid
        }
    roinfo = {
        "id":       roid,
        "title":    title,
        "creator":  creator,
        "date":     date
        }
    roinfotext = json.dumps(roinfo)
    (status, reason, headers, data) = httpsession.doRequestRDF("",
        method="POST", body=roinfotext, reqheaders=reqheaders)
    log.debug("ROSRS_session.createRO: %03d %s: %s"%(status, reason, repr(data)))
    if status == 201:
        return (status, reason, rdflib.URIRef(headers["location"]), data)
    if status == 409:
        return (status, reason, None, data)
    #@@TODO: Create annotations for title, creator, date??
    raise ROSRS_Error("Error creating RO", "%03d %s"%(status, reason), httpsession.baseuri())

def deleteRO(httpsession, rouri):
    """
    Delete this RO, return (status, reason):
    status+reason: 204 No Content or 404 Not Found
    """
    (status, reason, _, data) = httpsession.doRequest(rouri,
        method="DELETE")
    log.debug("ROSRS_session.deleteRO: %03d %s: %s"%(status, reason, repr(data)))
    if status in [204, 404]:
        return (status, reason)
    raise ROSRS_Error("Error deleting RO", "%03d %s"%(status, reason), httpsession.baseuri())

def getAsZip(rouri):
    """
    Retrieves a Research Object version from ROSRS as a zip.
    
    Parameters: ROSRS URL, username, password, RO id, version id
    """
    req = urllib2.Request(rouri)
    req.add_header("Accept", "application/zip")
    res = urllib2.urlopen(req)
    
    tmp = tempfile.TemporaryFile()
    while True:
        packet = res.read()
        if not packet:
            break
        tmp.write(packet)
    res.close()
    log.debug("Ro %s retrieved as zip" % rouri)
    return tmp

class ro_remote_metadata(object):
    """
    Class for accessing metadata of an RO stored by a ROSR service
    """

    def __init__(self, roconfig, httpsession, rouri, dummysetupfortest=False):
        """
        Initialize: read manifest from object at given directory into local RDF graph

        roconfig    is the research object manager configuration, supplied as a dictionary
        rouri       a URI reference that refers to the Research Object to be accessed
        """
        self.roconfig = roconfig 
        self.httpsession = httpsession       
        if not rouri.endswith("/"): rouri += "/"
        self.rouri = rouri
        self.manifestgraph = None
        self.roannotations = None
        self.manifesturi  = self.getManifestUri()
        self.dummyfortest = dummysetupfortest
        self._loadManifest()
        # Get RO URI from manifest
        # May be different from computed value if manifest has absolute URI
        self.rouri = self.manifestgraph.value(None, RDF.type, RO.ResearchObject)
        return

    def error(self, msg, value=None):
        return ROSRS_Error(msg=msg, value=value, srsuri=self.httpsession.baseuri())


    def delete(self):
        """
        Delete this RO, return (status, reason):
        status+reason: 204 No Content or 404 Not Found
        """
        return deleteRO(self.httpsession, self.rouri)

    def _loadManifest(self, refresh = False):
        if self.manifestgraph and not refresh: return self.manifestgraph
        self.manifestgraph = rdflib.Graph()
        if self.dummyfortest:
            # Fake minimal manifest graph for testing
            self.manifestgraph.add( (self.rouri, RDF.type, RO.ResearchObject) )
        else:
            # Read manifest graph
            self.manifestgraph.parse(self.manifesturi)
        return self.manifestgraph

    def _loadAnnotations(self):
        if self.roannotations: return self.roannotations
        # Assemble annotation graph
        # NOTE: the manifest itself is included as an annotation by the RO setup
        self._loadManifest()
        self.roannotations = rdflib.Graph()
        for (ann_node, subject) in self.manifestgraph.subject_objects(predicate=RO.annotatesAggregatedResource):
            ann_uri   = self.manifestgraph.value(subject=ann_node, predicate=AO.body)
            self._readAnnotationBody(ann_uri, self.roannotations)
        log.debug("roannotations graph:\n"+self.roannotations.serialize())
        return self.roannotations
    

#    def updateManifest(self):
#        """
#        Write updated manifest file for research object
#        """
#        self.manifestgraph.serialize(
#            destination=self.getManifestFilename(), format='xml',
#            base=self.rouri, xml_base="..")
#        return

#    def addAggregatedResources(self, ro_file, recurse=True):
#        """
#        Scan a local directory and add files found to the RO aggregation
#        """
#        def notHidden(f):
#            return re.match("\.|.*/\.", f) == None
#        log.debug("addAggregatedResources: ref %s, file %s"%(self.roref, ro_file))
#        self.getRoFilename()  # Check that we have one
#        if ro_file.endswith(os.path.sep):
#            ro_file = ro_file[0:-1]
#        rofiles = [ro_file]
#        if os.path.isdir(ro_file):
#            rofiles = filter( notHidden,
#                                MiscLib.ScanDirectories.CollectDirectoryContents(
#                                    os.path.abspath(ro_file), baseDir=os.path.abspath(self.roref),
#                                    listDirs=False, listFiles=True, recursive=recurse, appendSep=False)
#                            )
#        s = self.getRoUri()
#        for f in rofiles:
#            log.debug("- file %s"%f)
#            stmt = (s, ORE.aggregates, self.getComponentUri(f))
#            if stmt not in self.manifestgraph: self.manifestgraph.add(stmt)
#        self.updateManifest()
#        return

    def getAggregatedResources(self):
        """
        Returns iterator over all resources aggregated by a manifest.

        Each value returned by the iterator is an aggregated resource URI
        """
        log.debug("getAggregatedResources: uri %s"%(self.rouri))
        for r in self.manifestgraph.objects(subject=self.rouri, predicate=ORE.aggregates):
            yield r
        return
    
    def isAggregatedResource(self, respath):
        '''
        Returns true if the manifest says that the research object aggregates the
        resource. Resource URI is resolved against the RO URI unless it's absolute.
        '''
        log.debug("isAggregatedResource: ro uri %s res uri %s"%(self.rouri, respath))
        resuri = self.getComponentUriAbs(respath)
        return (self.rouri, ORE.aggregates, resuri) in self.manifestgraph

    def isResourceInternal(self, resuri):
        '''
        Check if the resource is internal, i.e. should the resource content be uploaded
        to the ROSR service. Returns true if the resource URI has the RO URI as a prefix.
        '''
        return resuri.startswith(self.rouri)

    def isResourceExternal(self, resuri):
        '''
        Check if the resource is external, i.e. can be aggregated as a URI reference.
        Returns true if the URI has 'http' or 'https' scheme.
        '''
        parseduri = urlparse.urlsplit(resuri)
        return parseduri.scheme in ["http", "https"] and not self.isResourceInternal(resuri)

    def aggregateResourceInt(
            self, respath, ctype="application/octet-stream", body=None):
        """
        Aggegate internal resource
        Return (status, reason, proxyuri, resuri), where status is 201

        NOTE: this method has been adapted from TestApi_ROSRS
        """
        # POST (empty) proxy value to RO ...
        reqheaders = { "slug": respath }
        proxydata = ("""
            <rdf:RDF
              xmlns:ore="http://www.openarchives.org/ore/terms/"
              xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" >
              <ore:Proxy>
              </ore:Proxy>
            </rdf:RDF>
            """)
        (status, reason, headers, data) = self.httpsession.doRequest(self.rouri,
            method="POST", ctype="application/vnd.wf4ever.proxy",
            reqheaders=reqheaders, body=proxydata)
        if status != 201:
            raise self.error("Error creating aggregation proxy",
                            "%d03 %s (%s)"%(status, reason, respath))
        proxyuri = rdflib.URIRef(headers["location"])
        links    = self.httpsession.parseLinks(headers)
        if "http://www.openarchives.org/ore/terms/proxyFor" not in links:
            raise self.error("No ore:proxyFor link in create proxy response",
                            "Proxy URI %s"%str(proxyuri))
        resuri   = rdflib.URIRef(links["http://www.openarchives.org/ore/terms/proxyFor"])
        # PUT resource content to indicated URI
        log.debug("Ctype=%s"%ctype)
        (status, reason, headers, _) = self.httpsession.doRequest(resuri,
            method="PUT", ctype=ctype, body=body)
        if status not in [200,201]:
            raise self.error("Error creating aggregated resource content",
                "%d03 %s (%s)"%(status, reason, respath))
        self._loadManifest(refresh = True)
        return (status, reason, headers, resuri)

    def updateResourceInt(
            self, respath, ctype="application/octet-stream", body=None):
        """
        Update an already aggregated internal resource
        Return (status, reason, None, resuri), where status is 200

        NOTE: this method has been adapted from TestApi_ROSRS
        """
        resuri = self.getComponentUriAbs(respath)
        # PUT resource content to indicated URI
        (status, reason, headers, _) = self.httpsession.doRequest(
            resuri, method="PUT", ctype=ctype, body=body)
        if status != 200:
            raise self.error("Error updating aggregated resource content",
                "%d03 %s (%s)"%(status, reason, respath))
        return (status, reason, headers, respath)

    def aggregateResourceExt(self, resuri):
        """
        Aggegate internal resource
        Return (status, reason, proxyuri, resuri), where status is 200 or 201

        NOTE: this method has been adapted from TestApi_ROSRS
        """
        # Aggegate external resource: POST proxy ...
        proxydata = ("""
            <rdf:RDF
              xmlns:ore="http://www.openarchives.org/ore/terms/"
              xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" >
              <ore:Proxy>
                <ore:proxyFor rdf:resource="%s" />
              </ore:Proxy>
            </rdf:RDF>
            """)%str(resuri)
        (status, reason, headers, data) = self.httpsession.doRequest(self.rouri,
            method="POST", ctype="application/vnd.wf4ever.proxy",
            body=proxydata)
        if status != 201:
            raise self.error("Error creating aggregation proxy",
                "%d03 %s (%s)"%(status, reason, str(resuri)))
        proxyuri = rdflib.URIRef(headers["location"])
        self._loadManifest(refresh = True)
        return (status, reason, proxyuri, rdflib.URIRef(resuri))
    
    def getROResourceProxy(self, resuriref):
        """
        Retrieve proxy description for resource.
        Return (proxyuri, manifest), where status is 200 or 404
        """
        resuri = self.getComponentUriAbs(resuriref)
        proxyterms = list(self.manifestgraph.subjects(
            predicate=rdflib.term.URIRef(u'http://www.openarchives.org/ore/terms/proxyFor'), object=resuri))
        log.debug("getROResourceProxy proxyterms: %s"%(repr(proxyterms)))
        proxyuri = None
        if len(proxyterms) == 1:
            proxyuri = proxyterms[0]
        return proxyuri

    def deaggregateResource(self, resuriref):
        """
        Deaggregate an aggregated resource. In case of an internal resource, its
        content is deleted.
        Return (status, reason, None, resuri), where status is 204 or 404
        """
        proxyuri = self.getROResourceProxy(resuriref)
        if not proxyuri:
            raise self.error("Could not find proxy for %s"%str(resuriref))
        (status, reason, headers, _) = self.httpsession.doRequest(
            proxyuri, method="DELETE")
        if status == 307:
            (status, reason, headers, _) = self.httpsession.doRequest(
                    headers["location"], method="DELETE")
        if status != 204:
            raise self.error("Error deleting aggregated resource",
                "%d03 %s (%s)"%(status, reason, resuriref))
        self._loadManifest(refresh = True)
        return (status, reason, headers, resuriref)

    def getHead(self, resuriref):
        """
        Retrieve resource from RO
        Return (status, reason, headers), where status is 200 or 404
        """
        resuri = self.getComponentUriAbs(resuriref)
        (status, reason, headers, _) = self.httpsession.doRequest(resuri,
            method="HEAD")
        if status in [200, 404]:
            return (status, reason, headers)
        raise self.error("Error retrieving RO resource", "%03d %s (%s)"%(status, reason, resuriref))

    def isAnnotationNode(self, respath):
        '''
        Returns true if the manifest says that the research object aggregates the
        annotation and it is an ro:AggregatedAnnotation.
        Resource URI is resolved against the RO URI unless it's absolute.
        '''
        log.debug("isAnnotationNode: ro uri %s res uri %s"%(self.rouri, respath))
        resuri = self.getComponentUriAbs(respath)
        return (self.rouri, ORE.aggregates, resuri) in self.manifestgraph and \
            (resuri, RDF.type, RO.AggregatedAnnotation) in self.manifestgraph
            
    def addAnnotationNode(self, bodypath, targetpath):
        """
        Aggregate an annotation of an existing resource using an existing annotation
        body.
        Return (status, reason, annuri), where status is 201

        NOTE: this method has been adapted from TestApi_ROSRS
        """
        annotation = """<?xml version="1.0" encoding="UTF-8"?>
            <rdf:RDF
               xmlns:ro="http://purl.org/wf4ever/ro#"
               xmlns:ao="http://purl.org/ao/"
               xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
               xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
               xml:base="%s"
            >
               <ro:AggregatedAnnotation>
                 <ao:annotatesResource rdf:resource="%s" />
                 <ao:body rdf:resource="%s" />
               </ro:AggregatedAnnotation>
            </rdf:RDF>
            """%(str(self.rouri), str(targetpath), str(bodypath))
        (status, reason, headers, _) = self.httpsession.doRequest(self.rouri,
            method="POST",
            ctype="application/vnd.wf4ever.annotation",
            body=annotation)
        if status != 201:
            raise self.error("Error creating annotation",
                "%d03 %s"%(status, reason))
        annuri = rdflib.URIRef(headers["location"])
        self._loadManifest(refresh = True)
        return (status, reason, rdflib.URIRef(annuri))
    
    def updateAnnotationNode(self, annpath, bodypath, targetpath):
        """
        Update an aggregated annotation of an existing resource using an 
        existing annotation body.
        Return (status, reason), where status is 200

        NOTE: this method has been adapted from TestApi_ROSRS
        """
        annuri = self.getComponentUriAbs(annpath)
        annotation = """<?xml version="1.0" encoding="UTF-8"?>
            <rdf:RDF
               xmlns:ro="http://purl.org/wf4ever/ro#"
               xmlns:ao="http://purl.org/ao/"
               xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
               xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
               xml:base="%s"
            >
               <ro:AggregatedAnnotation>
                 <ao:annotatesResource rdf:resource="%s" />
                 <ao:body rdf:resource="%s" />
               </ro:AggregatedAnnotation>
            </rdf:RDF>
            """%(str(self.rouri), str(targetpath), str(bodypath))
        (status, reason, _, _) = self.httpsession.doRequest(annuri,
            method="PUT",
            ctype="application/vnd.wf4ever.annotation",
            body=annotation)
        if status != 200:
            raise self.error("Error updating annotation",
                "%d03 %s (%s)"%(status, reason, annuri))
        self._loadManifest(refresh = True)
        return (status, reason)

    def deleteAnnotationNode(self, annpath):
        """
        Deaggregate an aggregated annotation.
        Return (status, reason, headers, resuri), where status is 204 or 404
        """
        annuri = self.getComponentUriAbs(annpath)
        (status, reason, headers, _) = self.httpsession.doRequest(
            annuri, method="DELETE")
        if not status in [204, 404]:
            raise self.error("Error deleting aggregated annotation",
                "%d03 %s (%s)"%(status, reason, annuri))
        self._loadManifest(refresh = True)
        return (status, reason, headers, annuri)

    def getAllAnnotationNodes(self):
        """
        Returns iterator over all annotations aggregated within the RO

        Each value returned by the iterator is a (annuri, bodyuri, target) triple.
        """
        for (ann_node, ann_target) in self.manifestgraph.subject_objects(predicate=RO.annotatesAggregatedResource):
            ann_body   = self.manifestgraph.value(subject=ann_node, predicate=AO.body)
            yield (ann_node, ann_body, ann_target)
        return
    
    # Support methods for accessing the manifest graph

    def _getRoManifestGraph(self):
        """
        Returns RDF graph containing RO manifest
        """
        return self.manifestgraph

    def roManifestContains(self, stmt):
        """
        Returns True if the RO manifest contains a statement matching the supplied triple.
        """
        return stmt in self.manifestgraph

    def getResourceValue(self, resource, predicate):
        """
        Returns value for resource whose URI is supplied assocfiated with indicated predicate
        """
        return self.manifestgraph.value(subject=resource, predicate=predicate, object=None)

    def getResourceType(self, resource):
        """
        Returns type of resource whose URI is supplied
        """
        return self.getResourceValue(resource, RDF.type)

    def getRoMetadataDict(self):
        """
        Returns dictionary of metadata about the RO from the manifest graph
        """
        strsubject = ""
        if isinstance(self.rouri, rdflib.URIRef): strsubject = str(self.rouri)
        manifestDict = {
            'ropath':         self.getRoFilename(),
            'rouri':          strsubject,
            'roident':        self.getResourceValue(self.rouri, DCTERMS.identifier  ),
            'rotitle':        self.getResourceValue(self.rouri, DCTERMS.title       ),
            'rocreator':      self.getResourceValue(self.rouri, DCTERMS.creator     ),
            'rocreated':      self.getResourceValue(self.rouri, DCTERMS.created     ),
            'rodescription':  self.getResourceValue(self.rouri, DCTERMS.description ),
            }
        return manifestDict

    # Support methods for accessing RO and component URIs

    def getRoRef(self):
        """
        Returns RO URI reference supplied (which may be a local file directory string)
        """
        return self.roref

    def getRoUri(self):
        return self.rouri

    def getComponentUri(self, path):
        """
        Return URI for component where relative reference is treated as a file path
        """
        ###return rdflib.URIRef(urlparse.urljoin(str(self.getRoUri()), path))
        if urlparse.urlsplit(path).scheme == "":
            path = resolveUri("", str(self.getRoUri()), path)
        return rdflib.URIRef(path)

    def getComponentUriAbs(self, path):
        """
        Return absolute URI for component where relative reference is treated as a URI reference
        """
        return rdflib.URIRef(urlparse.urljoin(str(self.getRoUri()), path))

    def getComponentUriRel(self, path):
        file_uri = urlparse.urlunsplit(urlparse.urlsplit(str(self.getComponentUri(path))))
        ro_uri   = urlparse.urlunsplit(urlparse.urlsplit(str(self.getRoUri())))
        if ro_uri is not None and file_uri.startswith(ro_uri):
            file_uri_rel = file_uri.replace(ro_uri, "", 1)
        else:
            file_uri_rel = path
        return rdflib.URIRef(file_uri_rel)

    def isRoMetadataRef(self, uri):
        """
        Test if supplied URI is a reference to the current RO metadata area
        """
        urirel = self.getComponentUriRel(uri)
        return str(urirel).startswith(ro_settings.MANIFEST_DIR+"/")

    def getManifestUri(self):
        return self.getComponentUri(ro_settings.MANIFEST_DIR+"/"+ro_settings.MANIFEST_FILE)

    def isLocalFileRo(self):
        """
        Test current RO URI to see if it is a local file system reference
        """
        return isFileUri(self.getRoUri())

    def getRoFilename(self):
        return getFilenameFromUri(self.getRoUri())

    def getManifestFilename(self):
        """
        Return manifesrt file name: used for local updates
        """
        return os.path.join(self.getRoFilename(), ro_settings.MANIFEST_DIR+"/",
                            ro_settings.MANIFEST_FILE)

# End.

