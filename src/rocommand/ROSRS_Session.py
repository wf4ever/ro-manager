"""
RO SRS session client implementation 
"""

import json # Used for service/resource info parsing
import re   # Used for link header parsing
#import httplib
import urlparse
import rdflib.graph
import logging
import time

from xml.dom import minidom
from urlparse import urljoin
from httplib2 import Http
from rdflib.term import URIRef

from MiscUtils.HttpSession import HTTP_Session

import ro_prefixes
from ro_namespaces import RDF, ORE, RO, AO, ROEVO
from ro_utils import EvoType

# Logging object
log = logging.getLogger(__name__)

# Annotation content types

ANNOTATION_CONTENT_TYPES = (
    { "application/rdf+xml":    "xml"
    , "text/turtle":            "turtle"
    , "text/n3":                "n3"
    , "text/nt":                "nt"
    , "application/json":       "jsonld"
    , "application/xhtml":      "rdfa"
    })

ANNOTATION_TEMPLATE = ("""<?xml version="1.0" encoding="UTF-8"?>
    <rdf:RDF
       xmlns:ro="http://purl.org/wf4ever/ro#"
       xmlns:ao="http://purl.org/ao/"
       xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
       xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
       xml:base="%(xmlbase)s"
    >
       <ro:AggregatedAnnotation>
         <ao:annotatesResource rdf:resource="%(resuri)s" />
         <ao:body rdf:resource="%(bodyuri)s" />
       </ro:AggregatedAnnotation>
    </rdf:RDF>
    """)

# Class for ROSRS errors

class ROSRS_Error(Exception):

    def __init__(self, msg="ROSRS_Error", value=None, srsuri=None):
        self._msg    = msg
        self._value  = value
        self._srsuri = srsuri
        return

    def __str__(self):
        txt = self._msg
        if self._srsuri: txt += " for srsuri "+str(self._srsuri)
        if self._value:  txt += ": "+repr(self._value)
        return txt

    def __repr__(self):
        return ( "ROSRS_Error(%s, value=%s, srsuri=%s)"%
                 (repr(self._msg), repr(self._value), repr(self._srsuri)))

# Get URI for resource in RO, returned as rdflib.URIRef value

def getResourceUri(rouri, resuriref):
    return URIRef(urlparse.urljoin(str(rouri), str(resuriref)))

# Class for handling ROSRS access

class ROSRS_Session(HTTP_Session):
    
    """
    Client access class for RO SRS - creates a session to access a single ROSRS endpoint,
    and provides methods to access ROs and RO resources via the RO SRS API.
    
    See:
    * http://www.wf4ever-project.org/wiki/display/docs/RO+SRS+interface+6
    * http://www.wf4ever-project.org/wiki/display/docs/RO+evolution+API
    
    Related:
    * http://www.wf4ever-project.org/wiki/display/docs/User+Management+2
    """

    def __init__(self, srsuri, accesskey = None):
        log.debug("ROSRS_Session.__init__: srsuri "+srsuri)
        super(ROSRS_Session, self).__init__(srsuri, accesskey)
        self._srsuri    = srsuri
        return

    def close(self):
        super(ROSRS_Session, self).close()
        # self._key = None
        # self._httpcon.close()
        return

    def baseuri(self):
        return self._srsuri

    def error(self, msg, value=None):
        return ROSRS_Error(msg=msg, value=value, srsuri=self._srsuri)

    def listROs(self):
        """
        List ROs in service

        Result is list of dictionaries, where dict["uri"] is the URI of an RO.
        """
        (status, reason, headers, data) = self.doRequest("")
        if status < 200 or status >= 300:
            raise self.error("Error listing ROs", "%03d %s"%(status, reason))
        log.debug("ROSRS_session.listROs: %s"%(repr(data)))
        urilist = data.splitlines()
        return [ { "uri" : u } for u in urilist ]

    def createRO(self, id, title, creator, date):
        """
        Create a new RO, return (status, reason, uri, manifest):
        status+reason: 201 Created or 409 Exists
        uri+manifest: URI and copy of manifest as RDF graph if 201 status,
                      otherwise None and response data as diagnostic
        """
        reqheaders   = {
            "slug":     id
            }
        roinfo = {
            "id":       id,
            "title":    title,
            "creator":  creator,
            "date":     date
            }
        roinfotext = json.dumps(roinfo)
        (status, reason, headers, data) = self.doRequestRDF("",
            method="POST", body=roinfotext, reqheaders=reqheaders)
        log.debug("ROSRS_session.createRO: %03d %s: %s"%(status, reason, repr(data)))
        if status == 201:
            return (status, reason, rdflib.URIRef(headers["location"]), data)
        if status == 409:
            return (status, reason, None, data)
        #@@TODO: Create annotations for title, creator, date??
        raise self.error("Error creating RO", "%03d %s"%(status, reason))

    def deleteRO(self, rouri, purge=False):
        """
        Delete an RO
        Return (status, reason), where status is 204 or 404
        """
        reqheaders=None
        if purge:
            reqheaders={"Purge": "True"}
        (status, reason, headers, data) = self.doRequest(rouri,
            method="DELETE", reqheaders=reqheaders)
        if status in [204, 404]:
            return (status, reason)
        raise self.error("Error deleting RO", "%03d %s (%s)"%(status, reason, str(rouri)))

    def getROResource(self, resuriref, rouri=None, accept=None, reqheaders=None):
        """
        Retrieve resource from RO
        Return (status, reason, headers, data), where status is 200 or 404 or redirect code
        """
        resuri = str(resuriref)
        if rouri:
            resuri = getResourceUri(rouri, resuri)
        (status, reason, headers, uri, data) = self.doRequestFollowRedirect(resuri,
            method="GET", accept=accept, reqheaders=reqheaders)
        if status in [200, 404]:
            return (status, reason, headers, URIRef(uri), data)
        raise self.error("Error retrieving RO resource", "%03d %s (%s)"%(status, reason, resuriref))

    def getROResourceRDF(self, resuri, rouri=None, reqheaders=None):
        """
        Retrieve RDF resource from RO
        Return (status, reason, headers, data), where status is 200 or 404
        """
        if rouri:
            resuri = getResourceUri(rouri, resuri)
        (status, reason, headers, uri, data) = self.doRequestRDFFollowRedirect(resuri,
            method="GET", reqheaders=reqheaders)
        if status in [200, 404]:
            return (status, reason, headers, URIRef(uri), data)
        raise self.error("Error retrieving RO RDF resource", "%03d %s (%s)"%(status, reason, resuri))

    def getROResourceProxy(self, resuriref, rouri):
        """
        Retrieve proxy description for resource.
        Return (proxyuri, manifest)
        """
        (status, reason, headers, manifesturi, manifest) = self.getROManifest(rouri)
        if status not in [200,404]:
            raise self.error("Error retrieving RO manifest", "%03d %s"%
                             (status, reason))
        proxyuri = None
        if status == 200:
            resuri = getResourceUri(rouri, resuriref)
            proxyterms = list(manifest.subjects(predicate=ORE.proxyFor, object=resuri))
            log.debug("getROResourceProxy proxyterms: %s"%(repr(proxyterms)))
            if len(proxyterms) == 1:
                proxyuri = proxyterms[0]
        return (proxyuri, manifest)

    def getROManifest(self, rouri):
        """
        Retrieve an RO manifest
        Return (status, reason, headers, uri, data), where status is 200 or 404
        """
        (status, reason, headers, uri, data) = self.doRequestRDFFollowRedirect(rouri,
            method="GET")
        log.debug("getROManifest %s, status %d, len %d"%(uri, status, len(data or [])))
        if status in [200, 404]:
            return (status, reason, headers, URIRef(uri), data)
        log.info("Error %03d %s retrieving %s"%(status, reason, uri))
        log.debug("Headers %s"%(repr(headers)))
        raise self.error("Error retrieving RO manifest",
            "%03d %s"%(status, reason))

    def getROLandingPage(self, rouri):
        """
        Retrieve an RO landing page
        Return (status, reason, headers, uri, data), where status is 200 or 404
        """
        (status, reason, headers, uri, data) = self.doRequestFollowRedirect(rouri,
            method="GET", accept="text/html")
        if status in [200, 404]:
            return (status, reason, headers, URIRef(uri), data)
        raise self.error("Error retrieving RO landing page",
            "%03d %s"%(status, reason))

    def getROZip(self, rouri):
        """
        Retrieve an RO as ZIP file
        Return (status, reason, headers, data), where status is 200 or 404
        """
        (status, reason, headers, uri, data) = self.doRequestFollowRedirect(rouri,
            method="GET", accept="application/zip")
        if status in [200, 404]:
            return (status, reason, headers, URIRef(uri), data)
        raise self.error("Error retrieving RO as ZIP file",
            "%03d %s"%(status, reason))

    def aggregateResourceInt(self,
        rouri, respath=None, ctype="application/octet-stream", body=None):
        """
        Aggegate internal resource
        Return (status, reason, proxyuri, resuri), where status is 200 or 201
        """
        # POST (empty) proxy value to RO ...
        reqheaders = respath and { "slug": respath }
        proxydata = ("""
            <rdf:RDF
              xmlns:ore="http://www.openarchives.org/ore/terms/"
              xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" >
              <ore:Proxy>
              </ore:Proxy>
            </rdf:RDF>
            """)
        (status, reason, headers, data) = self.doRequest(rouri,
            method="POST", ctype="application/vnd.wf4ever.proxy",
            reqheaders=reqheaders, body=proxydata)
        if status != 201:
            raise self.error("Error creating aggregation proxy",
                            "%03d %s (%s)"%(status, reason, respath))
        proxyuri = rdflib.URIRef(headers["location"])
        links    = self.parseLinks(headers)
        log.debug("- links: "+repr(links))
        log.debug("- ORE.proxyFor: "+str(ORE.proxyFor))
        if str(ORE.proxyFor) not in links:
            raise self.error("No ore:proxyFor link in create proxy response",
                            "Proxy URI %s"%str(proxyuri))
        resuri   = rdflib.URIRef(links[str(ORE.proxyFor)])
        # PUT resource content to indicated URI
        (status, reason, headers, data) = self.doRequest(resuri,
            method="PUT", ctype=ctype, body=body)
        if status not in [200,201]:
            raise self.error("Error creating aggregated resource content",
                "%03d %s (%s)"%(status, reason, respath))
        return (status, reason, proxyuri, resuri)

    def aggregateResourceExt(self, rouri, resuri):
        """
        Aggegate external resource
        Return (status, reason, proxyuri, resuri), where status is 200 or 201
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
        (status, reason, headers, data) = self.doRequest(rouri,
            method="POST", ctype="application/vnd.wf4ever.proxy",
            body=proxydata)
        if status != 201:
            raise self.error("Error creating aggregation proxy",
                "%03d %s (%s)"%(status, reason, str(resuri)))
        proxyuri = rdflib.URIRef(headers["location"])
        links    = self.parseLinks(headers)
        return (status, reason, proxyuri, rdflib.URIRef(resuri))

    def removeResource(self, rouri, resuri):
        """
        Remove resource from aggregation (internal or external)
        return (status, reason), where status is 204 No content or 404 Not found
        """
        # Find proxy for resource
        (proxyuri, manifest) = self.getROResourceProxy(resuri, rouri)
        if proxyuri == None:
            return (404, "Resource proxy not found in manifest")
        assert isinstance(proxyuri, rdflib.URIRef)
        # Delete proxy
        (status, reason, headers, uri, data) = self.doRequestFollowRedirect(proxyuri,
            method="DELETE")
        return (status, reason)

    def createROAnnotationBody(self, rouri, anngr):
        """
        Create an annotation body from a supplied annnotation graph.
        
        Returns: (status, reason, bodyuri)
        """
        # Create annotation body
        (status, reason, bodyproxyuri, bodyuri) = self.aggregateResourceInt(rouri,
            ctype="application/rdf+xml",
            body=anngr.serialize(format="xml"))
        if status != 201:
            raise self.error("Error creating annotation body resource",
                "%03d %s (%s)"%(status, reason, str(rouri)))
        return (status, reason, bodyuri)

    def createAnnotationRDF(self, rouri, resuri, bodyuri):
        """
        Create entity body for annotation
        """
        annotation = (ANNOTATION_TEMPLATE%
            { "xmlbase": str(rouri)
            , "resuri": str(resuri)
            , "bodyuri": str(bodyuri)
            })
        return annotation

    def createROAnnotation(self, rouri, resuri, bodyuri):
        """
        Create an annotation stub for supplied resource using indicated body
        
        Returns: (status, reason, annuri)
        """
        annotation = self.createAnnotationRDF(rouri, resuri, bodyuri)
        (status, reason, headers, data) = self.doRequest(rouri,
            method="POST",
            ctype="application/vnd.wf4ever.annotation",
            body=annotation)
        if status != 201:
            raise self.error("Error creating annotation",
                "%03d %s (%s)"%(status, reason, str(resuri)))
        annuri   = rdflib.URIRef(headers["location"])
        return (status, reason, annuri)

    def createROAnnotationInt(self, rouri, resuri, anngr):
        """
        Create internal annotation
        
        Return (status, reason, annuri, bodyuri)
        """
        (status, reason, bodyuri) = self.createROAnnotationBody(rouri, anngr)
        if status == 201:
            (status, reason, annuri) = self.createROAnnotation(rouri, resuri, bodyuri)
        return (status, reason, annuri, bodyuri)

    def createROAnnotationExt(self, rouri, resuri, bodyuri):
        """
        Creeate a resource annotation using an existing (possibly external) annotation body
        
        Returns: (status, reason, annuri)
        """
        (status, reason, annuri) = self.createROAnnotation(rouri, resuri, bodyuri)
        return (status, reason, annuri)

    def updateROAnnotation(self, rouri, annuri, resuri, bodyuri):
        """
        Update an indicated annotation for supplied resource using indiocated body
        
        Returns: (status, reason)
        """
        annotation = self.createAnnotationRDF(rouri, resuri, bodyuri)
        (status, reason, headers, data) = self.doRequest(annuri,
            method="PUT",
            ctype="application/vnd.wf4ever.annotation",
            body=annotation)
        if status != 200:
            raise self.error("Error updating annotation",
                "%03d %s (%s)"%(status, reason, str(resuri)))
        return (status, reason)

    def updateROAnnotationInt(self, rouri, annuri, resuri, anngr):
        """
        Update an annotation with a new internal annotation body

        returns: (status, reason, bodyuri)
        """
        (status, reason, bodyuri) = self.createROAnnotationBody(rouri, anngr)
        assert status == 201
        (status, reason) = self.updateROAnnotation(rouri, annuri, resuri, bodyuri)
        return (status, reason, bodyuri)

    def updateROAnnotationExt(self, rouri, annuri, bodyuri):
        """
        Update an annotation with an existing (possibly external) annotation body

        returns: (status, reason)
        """
        assert False, "@@TODO Not fully implemented - need to GET current annotation and extract annotated resource to resuri"
        (status, reason) = self.updateROAnnotation(rouri, annuri, resuri, bodyuri)
        return (status, reason)

    def getROAnnotationUris(self, rouri, resuri=None):
        """
        Enumerate annnotation URIs associated with a resource
        (or all annotations for an RO) 
        
        Returns an iterator over annotation URIs
        """
        (status, reason, headers, manifesturi, manifest) = self.getROManifest(rouri)
        if status != 200:
            raise self.error("No manifest",
                "%03d %s (%s)"%(status, reason, str(rouri)))
        for (a,p) in manifest.subject_predicates(object=resuri):
            if p in [AO.annotatesResource,RO.annotatesAggregatedResource]:
                yield a
        return

    def getROAnnotationBodyUris(self, rouri, resuri=None):
        """
        Enumerate annnotation body URIs associated with a resource
        (or all annotations for an RO) 
        
        Returns an iterator over annotation URIs
        """
        ### This works, but needs an additional HTTP operation for each annotation
        # for annuri in self.getROAnnotationUris(rouri, resuri):
        #     yield self.getROAnnotationBodyUri(annuri)
        (status, reason, headers, manifesturi, manifest) = self.getROManifest(rouri)
        if status != 200:
            raise self.error("No manifest",
                "%03d %s (%s)"%(status, reason, str(rouri)))
        ###log.info(manifest.serialize(format="xml"))
        for (a,p) in manifest.subject_predicates(object=resuri):
            if p in [AO.annotatesResource,RO.annotatesAggregatedResource]:
                yield manifest.value(subject=a, predicate=AO.body)
        return

    def getROAnnotationBodyUri(self, annuri):
        """
        # Retrieve annotation for given annotation URI
        """
        #(status, reason, headers, uri, anngr) = self.getROResourceRDF(annuri)
        #bodyuri = anngr.value(subject=annuri, predicate=AO.body)
        #return bodyuri
        (status, reason, headers, anngr) = self.doRequestRDF(annuri)
        if status != 303:
            raise self.error("No redirect from annnotation URI",
                "%03d %s (%s)"%(status, reason, str(annuri)))
        return rdflib.URIRef(headers['location'])

    def getROAnnotationGraph(self, rouri, resuri=None):
        """
        Build RDF graph of annnotations associated with a resource
        (or all annotations for an RO) 
        
        Returns graph of merged annotations
        """
        agraph = rdflib.graph.Graph()
        for (prefix, uri) in ro_prefixes.prefixes:
            agraph.bind(prefix, rdflib.namespace.Namespace(uri))
        buris = set(self.getROAnnotationBodyUris(rouri, resuri))
        ###log.info("getROAnnotationGraph: %r"%([ str(b) for b in buris]))
        for buri in buris:
            (status, reason, headers, curi, data) = self.doRequestRDFFollowRedirect(buri, 
                graph=agraph, exthost=True)
            log.debug("getROAnnotationGraph: %03d %s reading %s"%(status, reason, buri))
            if status != 200:
                log.error("getROAnnotationGraph: %03d %s reading %s"%(status, reason, buri))
        return agraph

    def getROAnnotation(self, annuri):
        """
        Retrieve annotation for given annotation URI
        
        Returns: (status, reason, bodyuri, anngr)
        """
        (status, reason, headers, uri, anngr) = self.getROResourceRDF(annuri)
        return (status, reason, uri, anngr)

    def removeROAnnotation(self, rouri, annuri):
        """
        Remove annotation at given annotation URI
        
        Returns: (status, reason)
        """
        (status, reason, headers, data) = self.doRequest(annuri,
            method="DELETE")
        return (status, reason)

    # ---------------------------------------------
    # RO Evolution
    # ---------------------------------------------
    # See: http://www.wf4ever-project.org/wiki/display/docs/RO+evolution+API

    # Need to fugure out how deferred values can work, associated with copyuri
    # e.g. poll, notification subscribe, sync options

    def copyRO(self, oldrouri, slug):
        assert False, "@@TODO"
        return (status, reason, copyuri)
        # copyuri ->  Deferred(oldrouri, rotype, rostatus, newrouri)

    def cancelCopyRO(self, copyuri):
        assert False, "@@TODO"
        return (status, reason)

    def updateROStatus(self, rouri, rostatus):
        assert False, "@@TODO"
        return (status, reason, updateuri)

    def getROEvolution(self, rouri):
        #if len(rouri.split(self._srsuri))>1:
            #rouri = rouri.split(self._srsuri)[-1]
        (manifest_status, manifest_reason, manifest_headers, manifest_data) = (
            self.doRequest(uripath=urljoin(rouri,".ro/manifest.rdf"), accept="application/rdf+xml"))
        if manifest_status == 404:
            return (manifest_status, manifest_reason, manifest_data, None)
        (manifest_status, manifest_reason, manifest_headers, manifest_data) = self.doRequest(uripath=rouri, accept="application/rdf+xml")
        if manifest_status == 404 or not "link" in manifest_headers:
            if manifest_status == 401:
                print "Unauthorised operation"
                return None
            return (manifest_status, manifest_reason, manifest_data, None)
        parssed_header_uri =  manifest_headers["link"].split(">; rel=")[0][1:]
        (evolution_status, evolution_reason, evolution_headers, evolution_data) = self.doRequest(uripath=parssed_header_uri,accept="text/turtle")
        if evolution_status == 404:
            return (evolution_status, evolution_reason, evolution_data, EvoType.UNDEFINED)
        graph = rdflib.Graph()
        graph.parse(data=evolution_data, format="n3")
        try:
            (graph.objects(getResourceUri(self._srsuri, rouri), ROEVO.isFinalized)).next()
            return (evolution_status, evolution_reason, evolution_data, EvoType.UNDEFINED)
        except StopIteration  as error:            
            try:
                return (evolution_status, evolution_reason, evolution_data,
                        self.checkType(graph.objects(getResourceUri(self._srsuri, rouri), RDF.type)))
            except StopIteration  as error:
                return (evolution_status, evolution_reason, evolution_data, EvoType.UNDEFINED)
            
    def checkType(self,graph_objects): 
        for rdf_class in graph_objects:
           if rdf_class == ROEVO.LiveRO:
               return EvoType.LIVE
           if rdf_class == ROEVO.SnapshotRO:
               return EvoType.SNAPSHOT
           if rdf_class == ROEVO.ArchivedRO: 
               return EvoType.ARCHIVE
        return EvoType.UNDEFINED
            
    def getJob(self, rouri):
        h = Http()
        DOMTree = minidom.parseString(h.request(rouri)[-1])
        cNodes = DOMTree.childNodes
        status =  cNodes[0].getElementsByTagName("status")[0].childNodes[0].toxml()
        target =  cNodes[0].getElementsByTagName("target")[0].childNodes[0].toxml()
        if len(cNodes[0].getElementsByTagName("finalize")) == 1 and len(cNodes[0].getElementsByTagName("type")[0]) == 1:
            finalize =  cNodes[0].getElementsByTagName("finalize")[0].childNodes[0].toxml()
            type =  cNodes[0].getElementsByTagName("type")[0].childNodes[0].toxml()
            return (status,target,finalize,type)
        if len(cNodes[0].getElementsByTagName("processed_resources")) == 1 and len(cNodes[0].getElementsByTagName("submitted_resources")) == 1 :
            processed_resources = cNodes[0].getElementsByTagName("processed_resources")[0].firstChild.nodeValue
            submitted_resources = cNodes[0].getElementsByTagName("submitted_resources")[0].firstChild.nodeValue
            return (status,target,processed_resources,submitted_resources,"ZIP_JOB")
        return (status,target)

            
# End.
