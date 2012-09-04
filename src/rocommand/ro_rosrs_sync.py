'''
Created on 22-08-2012

@author: piotrhol
'''

import logging
import urllib2
import rdflib

log = logging.getLogger(__name__)

ACTION_CREATE_RO = 1
ACTION_RO_EXISTS = 2
ACTION_AGGREGATE_INTERNAL = 3
ACTION_AGGREGATE_EXTERNAL = 4
ACTION_UPDATE_OVERWRITE = 5
ACTION_UPDATE = 5
ACTION_SKIP = 7
ACTION_DELETE = 8

RESPONSE_YES = 1
RESPONSE_NO = 2

def pushResearchObject(localRo, remoteRo, force = False):
    '''
    Scans a given RO version directory for files that have been modified since last synchronization
    and pushes them to ROSRS. Modification is detected by checking modification times and checksums.
    '''        
    for localResuri in localRo.getAggregatedResources():
        respath = localRo.getComponentUriRel(localResuri)
        if not remoteRo.isAggregatedResource(respath):
            log.debug("ResourceSync.pushResearchObject: %s does was not aggregated in the remote RO"%(respath))
            if localRo.isInternalResource(localResuri):
                log.debug("ResourceSync.pushResearchObject: %s is internal"%(localResuri))
                yield (ACTION_AGGREGATE_INTERNAL, respath)
                remoteRo.aggregateResourceInt(
                                         respath, 
                                          localRo.getResourceType(respath), 
                                          urllib2.urlopen(localRo.getComponentUri(localResuri)))
            elif localRo.isExternalResource(localResuri):
                log.debug("ResourceSync.pushResearchObject: %s is external"%(localResuri))
                yield (ACTION_AGGREGATE_EXTERNAL, respath)
                remoteRo.aggregateResourceExt(respath)
            else:
                log.error("ResourceSync.pushResearchObject: %s is neither internal nor external"%(localResuri))
        else:
            log.debug("ResourceSync.pushResearchObject: %s does was already aggregated in the remote RO"%(respath))
            if localRo.isInternalResource(localResuri):
                log.debug("ResourceSync.pushResearchObject: %s is internal"%(localResuri))
                # Get remote ETag
                (status, reason, headers) = remoteRo.getHead(respath)
                if status != 200:
                    raise Exception("Error retrieving RO resource", "%03d %s (%s)"%(status, reason, respath))
                currentETag = headers["ETag"];
                currentChecksum = localRo.calculateChecksum(localResuri)
                # Check locally stored ETag
                previousETag = localRo.getRegistries()[localResuri]["ETag"]
                previousChecksum = localRo.getRegistries()[localResuri]["checksum"]
                if not previousETag or previousETag != currentETag:
                    yield (ACTION_UPDATE_OVERWRITE, respath)
                    (status, reason, headers, resuri) = remoteRo.updateResourceInt(respath, 
                                               localRo.getResourceType(respath),
                                               urllib2.urlopen(localRo.getComponentUri(respath)))
                    localRo.getRegistries()[localResuri]["ETag"] = headers["ETag"]
                    localRo.getRegistries()[localResuri]["checksum"] = currentChecksum
                else:
                    if not previousChecksum or previousChecksum != currentChecksum:
                        log.debug("ResourceSync.pushResearchObject: %s has been modified"%(resuri))
                        yield (ACTION_UPDATE_OVERWRITE, resuri)
                        (status, reason, headers, resuri) = remoteRo.updateResourceInt(resuri, 
                                                   localRo.getResourceType(localResuri),
                                                   urllib2.urlopen(localRo.getComponentUri(localResuri)))
                        localRo.getRegistries()[localResuri]["ETag"] = headers["ETag"]
                        localRo.getRegistries()[localResuri]["checksum"] = currentChecksum
                    else:
                        log.debug("ResourceSync.pushResearchObject: %s has NOT been modified"%(localResuri))
                        yield (ACTION_SKIP, localResuri)
            elif localRo.isExternalResource(localResuri):
                log.debug("ResourceSync.pushResearchObject: %s is external"%(localResuri))
                yield (ACTION_SKIP, localResuri)
            else:
                log.error("ResourceSync.pushResearchObject: %s is neither internal nor external"%(localResuri))
    
    for resuri in remoteRo.getAggregatedResources():
        respath = remoteRo.getComponentUriRel(resuri)
        if not localRo.isAggregatedResource(respath):
            log.debug("ResourceSync.pushResearchObject: %s will be deaggregated"%(resuri))
            yield (ACTION_DELETE, resuri)
            remoteRo.deaggregateResource(resuri)
        pass            
                
    for ann in localRo.getAllAnnotations():
        pass
    localRo.saveRegistries()
    return
    
    
        
