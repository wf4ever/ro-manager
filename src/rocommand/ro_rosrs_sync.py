'''
Created on 22-08-2012

@author: piotrhol
'''

import logging
import rdflib
import mimetypes

from rocommand import ro_uriutils

log = logging.getLogger(__name__)

ACTION_AGGREGATE_INTERNAL = 1
ACTION_AGGREGATE_EXTERNAL = 2
ACTION_AGGREGATE_ANNOTATION = 3
ACTION_UPDATE_OVERWRITE = 4
ACTION_UPDATE = 5
ACTION_UPDATE_ANNOTATION = 6
ACTION_SKIP = 7
ACTION_DELETE = 8
ACTION_DELETE_ANNOTATION = 9

def pushResearchObject(localRo, remoteRo, force = False):
    '''
    Scans a given RO version directory for files that have been modified since last synchronization
    and pushes them to ROSRS. Modification is detected by checking modification times and checksums.
    '''        
    mimetypes.init()
    for localResuri in localRo.getAggregatedResources():
        respath = localRo.getComponentUriRel(localResuri)
        if not remoteRo.isAggregatedResource(respath):
            log.debug("ResourceSync.pushResearchObject: %s does was not aggregated in the remote RO"%(respath))
            if localRo.isInternalResource(localResuri):
                log.debug("ResourceSync.pushResearchObject: %s is internal"%(localResuri))
                if localRo.isAnnotationNode(respath):
                    # annotations are handled separately
                    pass
                else:
                    yield (ACTION_AGGREGATE_INTERNAL, respath)
                    filename = ro_uriutils.getFilenameFromUri(localResuri)
                    currentChecksum = localRo.calculateChecksum(filename)
                    rf = open(filename, 'r')
                    (status, reason, headers, resuri) = remoteRo.aggregateResourceInt(
                                              respath, 
                                              mimetypes.guess_type(respath)[0], 
                                              rf)
                    localRo.getRegistries()["%s,etag"%filename] = headers.get("etag", None)
                    localRo.getRegistries()["%s,checksum"%filename] = currentChecksum
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
                if localRo.isAnnotationNode(respath):
                    # annotations are handled separately
                    pass
                else:
                    log.debug("ResourceSync.pushResearchObject: %s is a resource"%(localResuri))
                    # Get remote ETag
                    (status, reason, headers) = remoteRo.getHead(respath)
                    if status != 200:
                        raise Exception("Error retrieving RO resource", "%03d %s (%s)"%(status, reason, respath))
                    filename = ro_uriutils.getFilenameFromUri(localResuri)
                    currentETag = headers.get("etag", None)
                    currentChecksum = localRo.calculateChecksum(filename)
                    # Check locally stored ETag
                    previousETag = localRo.getRegistries().get("%s,etag"%filename, None)
                    previousChecksum = localRo.getRegistries().get("%s,checksum"%filename, None)
                    overwrite = False
                    if not previousETag or previousETag != currentETag:
                        log.debug("ResourceSync.pushResearchObject: %s has been modified in ROSRS (ETag was %s is %s)"%(respath, previousETag, currentETag))
                        yield (ACTION_UPDATE_OVERWRITE, respath)
                        overwrite = True
                    elif not previousChecksum or previousChecksum != currentChecksum:
                        log.debug("ResourceSync.pushResearchObject: %s has been modified locally (checksum was %s is %s)"%(respath, previousChecksum, currentChecksum))
                        yield (ACTION_UPDATE, respath)
                        overwrite = True
                    if overwrite:
                        rf = open(ro_uriutils.getFilenameFromUri(localResuri), 'r')
                        (status, reason, headers, resuri) = remoteRo.updateResourceInt(respath, 
                                                   mimetypes.guess_type(localResuri)[0],
                                                   rf)
                        localRo.getRegistries()["%s,etag"%filename] = headers.get("etag", None)
                        localRo.getRegistries()["%s,checksum"%filename] = currentChecksum
                    else:
                        log.debug("ResourceSync.pushResearchObject: %s has NOT been modified"%(respath))
                        yield (ACTION_SKIP, respath)
            elif localRo.isExternalResource(localResuri):
                log.debug("ResourceSync.pushResearchObject: %s is external"%(localResuri))
                yield (ACTION_SKIP, localResuri)
            else:
                log.error("ResourceSync.pushResearchObject: %s is neither internal nor external"%(localResuri))
    
    for resuri in remoteRo.getAggregatedResources():
        respath = remoteRo.getComponentUriRel(resuri)
        if not localRo.isAggregatedResource(respath):
            if remoteRo.isAnnotationNode(respath):
                # annotations are handled separately
                pass
            else:
                log.debug("ResourceSync.pushResearchObject: %s will be deaggregated"%(resuri))
                yield (ACTION_DELETE, resuri)
                remoteRo.deaggregateResource(resuri)
        pass            
                
    for (ann_node, ann_body, ann_target) in localRo.getAllAnnotationNodes():
        annpath = localRo.getComponentUriRel(ann_node)
        bodypath = localRo.getComponentUriRel(ann_body)
        targetpath = localRo.getComponentUriRel(ann_target)
        if isinstance(ann_node, rdflib.BNode) or not remoteRo.isAnnotationNode(annpath):
            log.debug("ResourceSync.pushResearchObject: %s is a new annotation"%(annpath))
            (_, _, remote_ann_node_uri) = remoteRo.addAnnotationNode(bodypath, targetpath)
            remote_ann_node_path = remoteRo.getComponentUriRel(remote_ann_node_uri)
            localRo.replaceUri(ann_node, localRo.getComponentUriAbs(remote_ann_node_path))
            yield (ACTION_AGGREGATE_ANNOTATION, remote_ann_node_path)
        else:
            log.debug("ResourceSync.pushResearchObject: %s is an existing annotation"%(annpath))
            remoteRo.updateAnnotationNode(annpath, bodypath, targetpath)
            yield (ACTION_UPDATE_ANNOTATION, ann_node)
            
    for (ann_node, ann_body, ann_target) in remoteRo.getAllAnnotationNodes():
        annpath = remoteRo.getComponentUriRel(ann_node)
        if not localRo.isAnnotationNode(annpath):
            log.debug("ResourceSync.pushResearchObject: annotation %s will be deleted"%(ann_node))
            yield (ACTION_DELETE_ANNOTATION, ann_node)
            remoteRo.deleteAnnotationNode(ann_node)
        pass
    
    localRo.saveRegistries()
    return
    
    
        
