'''
Created on 22-08-2012

@author: piotrhol
'''

import logging
import urllib2
import httplib
import urlparse
import rdflib

log = logging.getLogger(__name__)

class ro_rosrs_sync(object):
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
        return
                
    def pushResearchObject(self, localRo, remoteRo, force = False):
        '''
        Scans a given RO version directory for files that have been modified since last synchronization
        and pushes them to ROSRS. Modification is detected by checking modification times and checksums.
        '''        
        for res in localRo.getAggregatedResources():
            resuri = urlparse.urljoin(remoteRo.getRoUri(), res)
            if not remoteRo.isAggregatedResource(resuri):
                log.debug("ResourceSync.pushResearchObject: %s does was not aggregated in the remote RO"%(resuri))
                if localRo.isInternalResource(resuri):
                    log.debug("ResourceSync.pushResearchObject: %s is internal"%(resuri))
                    yield (self.ACTION_AGGREGATE_INTERNAL, resuri)
                    remoteRo.aggregateResourceInt(remoteRo.getRoUri(), 
                                              localRo.getComponentUriRel(resuri), 
                                              localRo.getResourceType(resuri), 
                                              urllib2.urlopen(localRo.getComponentUri(resuri)))
                elif localRo.isExternalResource(resuri):
                    log.debug("ResourceSync.pushResearchObject: %s is external"%(resuri))
                    yield (self.ACTION_AGGREGATE_EXTERNAL, resuri)
                    remoteRo.aggregateResourceExt(remoteRo.getRoUri(), localRo.getComponentUri(resuri))
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
    
    
        
