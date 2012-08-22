'''
Created on 22-08-2012

@author: piotrhol
'''

from SyncRegistry import SyncRegistry
import mimetypes
import logging
from os.path import exists, join
import pickle
import urllib2
import httplib
import urlparse
import json
import rdflib

log = logging.getLogger(__name__)

class ResourceSync(object):
    '''
    classdocs
    '''
   
    REGISTRIES_FILE = ".registries.pickle"

    def __init__(self, srsuri, accesskey):
        '''
        Constructor
        '''
        log.debug("ResourceSync.__init__: srsuri "+srsuri)
        self._srsuri    = srsuri
        self._key       = accesskey
        parseduri       = urlparse.urlsplit(srsuri)
        self._srsscheme = parseduri.scheme
        self._srshost   = parseduri.netloc
        self._srspath   = parseduri.path
        self._httpcon   = httplib.HTTPConnection(self._srshost)
        mimetypes.init()
        return
                
    def pushResearchObject(self, roMetadata, force = False):
        '''
        Scans a given RO version directory for files that have been modified since last synchronization
        and pushes them to ROSRS. Modification is detected by checking modification times and checksums.
        '''
        for res in roMetadata.getAggregatedResources():
            if self.__isInternalResource(roMetadata, res):
                log.debug("ResourceSync.pushResearchObject: %s is internal"%(res))
                if self.__isInternalResourceModified(roMetadata, res):
                    log.debug("ResourceSync.pushResearchObject: %s has been modified"%(res))
                    self.aggregateResourceInt(roMetadata.getRoUri(), 
                                              roMetadata.getComponentUriRel(res), 
                                              roMetadata.getResourceType(res), 
                                              urllib2.urlopen(roMetadata.getComponentUri(res)))
                else:
                    log.debug("ResourceSync.pushResearchObject: %s has NOT been modified"%(res))
                    pass
            elif self.__isExternalResource(roMetadata, res):
                log.debug("ResourceSync.pushResearchObject: %s is external"%(res))
                self.aggregateResourceExt(roMetadata.getRoUri(), roMetadata.getComponentUri(res))
            else:
                log.error("ResourceSync.pushResearchObject: %s is neither internal nor external"%(res))
        for ann in roMetadata.getAllAnnotations():
            pass
        return
    
    def createRO(self, id, title, creator, date):
        """
        Create a new RO, return (status, reason, uri, manifest):
        status+reason: 201 Created or 409 Exists
        uri+manifest: URI and copy of manifest as RDF graph if 201 status,
                      otherwise None and response data as diagnostic

        NOTE: this method has been adapted from TestApi_ROSRS
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

    def aggregateResourceInt(
            self, rouri, respath, ctype="application/octet-stream", body=None):
        """
        Aggegate internal resource
        Return (status, reason, proxyuri, resuri), where status is 200 or 201

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
        (status, reason, headers, data) = self.doRequest(rouri,
            method="POST", ctype="application/vnd.wf4ever.proxy",
            reqheaders=reqheaders, body=proxydata)
        if status != 201:
            raise self.error("Error creating aggregation proxy",
                            "%d03 %s (%s)"%(status, reason, respath))
        proxyuri = rdflib.URIRef(headers["location"])
        links    = self.parseLinks(headers)
        if "http://www.openarchives.org/ore/terms/proxyFor" not in links:
            raise self.error("No ore:proxyFor link in create proxy response",
                            "Proxy URI %s"%str(proxyuri))
        resuri   = rdflib.URIRef(links["http://www.openarchives.org/ore/terms/proxyFor"])
        # PUT resource content to indicated URI
        (status, reason, headers, data) = self.doRequest(resuri,
            method="PUT", ctype=ctype, body=body)
        if status not in [200,201]:
            raise self.error("Error creating aggregated resource content",
                "%d03 %s (%s)"%(status, reason, respath))
        return (status, reason, proxyuri, resuri)

    def aggregateResourceExt(self, rouri, resuri):
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
        (status, reason, headers, data) = self.doRequest(rouri,
            method="POST", ctype="application/vnd.wf4ever.proxy",
            body=proxydata)
        if status != 201:
            raise self.error("Error creating aggregation proxy",
                "%d03 %s (%s)"%(status, reason, str(resuri)))
        proxyuri = rdflib.URIRef(headers["location"])
        links    = self.parseLinks(headers)
        return (status, reason, proxyuri, rdflib.URIRef(resuri))
    
    # STUBS
    def __isInternalResource(self, roMetadata, res):
        return

    def __isExternalResource(self, roMetadata, res):
        return
    
    def __isExternalResourceModified(self, roMetadata, res):
        return

    # Should be used
    def __checkFile4Put(self, roId, roDirectory, filepath):
        assert filepath.startswith(roDirectory)
        rosrsFilepath = filepath[len(roDirectory) + 1:]
        put = True
        if (filepath in self.syncRegistries):
            put = self.syncRegistries[filepath].hasBeenModified()
        if put:
            contentType = mimetypes.guess_type(filepath)[0]
            fileObject = open(filepath)
            log.debug("Put file %s" % filepath)
            self.rosrsSync.putFile(roId, rosrsFilepath, contentType, fileObject)
            self.syncRegistries[filepath] = SyncRegistry(filepath)
        return put
    
    def __scanRegistries4Delete(self, roId, roDirectory):
        deletedFiles = set()
        for r in self.syncRegistries.viewvalues():
            if r.filename.startswith(roDirectory):
                if not exists(r.filename):
                    log.debug("Delete file %s" % r.filename)
                    deletedFiles.add(r.filename)
                    rosrsFilepath = r.filename[len(roDirectory) + 1:]
                    try:
                        self.rosrsSync.deleteFile(roId, rosrsFilepath)
                    except:
                        log.debug("File %s did not exist in ROSRS" % r.filename)
        for f in deletedFiles:
            del self.syncRegistries[f]
        return deletedFiles
    
    def __loadRegistries(self, roDirectory):
        try:
            rf = open(join(roDirectory, self.REGISTRIES_FILE), 'r')
            return pickle.load(rf)
        except:
            return dict()
        
    def __saveRegistries(self, roDirectory):
        rf = open(join(roDirectory, self.REGISTRIES_FILE), 'w')
        pickle.dump(self.syncRegistries, rf)
        return
        
