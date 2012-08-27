'''
Created on 22-08-2012

@author: piotrhol
'''

from SyncRegistry import SyncRegistry
import logging
import urllib2
import httplib
import urlparse
import json
import rdflib
from rocommand import ro_remote_metadata

log = logging.getLogger(__name__)

class ResourceSync(object):
    '''
    classdocs
    '''
   
    ACTION_CREATE_RO = 1
    ACTION_RO_EXISTS = 2
    ACTION_AGGREGATE_INTERNAL = 3
    ACTION_AGGREGATE_EXTERNAL = 4
    ACTION_UPDATE_OVERWRITE_NEWER = 5
    ACTION_UPDATE = 5
    ACTION_SKIP = 7
    ACTION_DELETE = 8
    
    RESPONSE_YES = 1
    RESPONSE_NO = 2

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
        return
                
    def pushResearchObject(self, localRo, roid, force = False):
        '''
        Scans a given RO version directory for files that have been modified since last synchronization
        and pushes them to ROSRS. Modification is detected by checking modification times and checksums.
        '''
        (status, _, rouri, _) = self.createRO(roid, None, None, None)
        if status == 409:
            # we'll assume we have rights to modify it and we'll see later
            log.info("Research Object %s already exists."%(roid))
            rouri = urlparse.urljoin(self.srsuri, roid)
            yield (self.ACTION_RO_EXISTS, rouri)
        else:
            yield (self.ACTION_CREATE_RO, rouri)
        
        remoteRo = ro_remote_metadata.ro_remote_metadata(None, rouri)

        for res in localRo.getAggregatedResources():
            resuri = urlparse.urljoin(rouri, res)
            if not remoteRo.isAggregatedResource(resuri):
                log.debug("ResourceSync.pushResearchObject: %s does was not aggregated in the remote RO"%(resuri))
                if localRo.isInternalResource(resuri):
                    log.debug("ResourceSync.pushResearchObject: %s is internal"%(resuri))
                    yield (self.ACTION_AGGREGATE_INTERNAL, resuri)
                    remoteRo.aggregateResourceInt(rouri, 
                                              localRo.getComponentUriRel(resuri), 
                                              localRo.getResourceType(resuri), 
                                              urllib2.urlopen(localRo.getComponentUri(resuri)))
                elif localRo.isExternalResource(resuri):
                    log.debug("ResourceSync.pushResearchObject: %s is external"%(resuri))
                    yield (self.ACTION_AGGREGATE_EXTERNAL, resuri)
                    remoteRo.aggregateResourceExt(rouri, localRo.getComponentUri(resuri))
                else:
                    log.error("ResourceSync.pushResearchObject: %s is neither internal nor external"%(resuri))
            else:
                log.debug("ResourceSync.pushResearchObject: %s does was already aggregated in the remote RO"%(resuri))
                if localRo.isInternalResource(localRo, resuri):
                    log.debug("ResourceSync.pushResearchObject: %s is internal"%(res))
                    # Get remote ETag
                    (status, reason, headers, _) = remoteRo.getHead(resuri)
                    if status != 200:
                        raise self.error("Error retrieving RO resource", "%03d %s (%s)"%(status, reason, resuri))
                    currentETag = headers["ETag"];
                    currentChecksum = localRo.calculateChecksum(res)
                    # Check locally stored ETag
                    previousETag = localRo.getRegistries()[res]["ETag"]
                    previousChecksum = localRo.getRegistries()[res]["checksum"]
                    if not previousETag or previousETag != currentETag:
                        yield (self.ACTION_UPDATE_OVERWRITE_NEWER, res)
                        (status, reason, headers, resuri) = remoteRo.updateResourceInt(resuri, 
                                                   localRo.getResourceType(resuri),
                                                   urllib2.urlopen(localRo.getComponentUri(resuri)))
                        localRo.getRegistries()[res]["ETag"] = headers["ETag"]
                        localRo.getRegistries()[res]["checksum"] = currentChecksum
                    else:
                        if not previousChecksum or previousChecksum != currentChecksum:
                            log.debug("ResourceSync.pushResearchObject: %s has been modified"%(resuri))
                            yield (self.ACTION_UPDATE_OVERWRITE, res)
                            (status, reason, headers, resuri) = remoteRo.updateResourceInt(resuri, 
                                                       localRo.getResourceType(resuri),
                                                       urllib2.urlopen(localRo.getComponentUri(resuri)))
                            localRo.getRegistries()[res]["ETag"] = headers["ETag"]
                            localRo.getRegistries()[res]["checksum"] = currentChecksum
                        else:
                            log.debug("ResourceSync.pushResearchObject: %s has NOT been modified"%(resuri))
                            yield (self.ACTION_SKIP, res)
                elif localRo.isExternalResource(resuri):
                    log.debug("ResourceSync.pushResearchObject: %s is external"%(resuri))
                    yield (self.ACTION_SKIP, resuri)
                else:
                    log.error("ResourceSync.pushResearchObject: %s is neither internal nor external"%(resuri))
        
        for res in remoteRo.getAggregatedResources():
            if not localRo.isAggregatedResource(res):
                log.debug("ResourceSync.pushResearchObject: %s will be deaggregated"%(res))
                yield (self.ACTION_DELETE, res)
                remoteRo.deaggregateResource(res)
            pass            
                    
        for ann in localRo.getAllAnnotations():
            pass
        localRo.saveRegistries()
        return
    
    def createRO(self, roid, title, creator, date):
        """
        Create a new RO, return (status, reason, uri, manifest):
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
        (status, reason, headers, data) = self.doRequestRDF("",
            method="POST", body=roinfotext, reqheaders=reqheaders)
        log.debug("ROSRS_session.createRO: %03d %s: %s"%(status, reason, repr(data)))
        if status == 201:
            return (status, reason, rdflib.URIRef(headers["location"]), data)
        if status == 409:
            return (status, reason, None, data)
        #@@TODO: Create annotations for title, creator, date??
        raise self.error("Error creating RO", "%03d %s"%(status, reason))
    
        
