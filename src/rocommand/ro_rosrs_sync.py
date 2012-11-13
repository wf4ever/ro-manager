'''
Created on 22-08-2012

@author: piotrhol
'''

import logging
import rdflib
import mimetypes

from rocommand import ro_uriutils
from rocommand.ro_remote_metadata import ROSRS_Error

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
ACTION_ERROR = 10

def pushResearchObject(localRo, remoteRo, force = False):
    '''
    Scans a given RO version directory for files that have been modified since last synchronization
    and pushes them to ROSRS. Modification is detected by checking modification times and checksums.
    '''
    push = PushResearchObject(localRo, remoteRo, force)
    for (action, uri) in push.push():
        yield (action, uri)
    return

class PushResearchObject:
    
    def __init__(self, localRo, remoteRo, force = False):
        self._localRo = localRo
        self._remoteRo = remoteRo
        self._force = force
    
    def push(self):        
        mimetypes.init()
        for localResuri in self._localRo.getAggregatedResources():
            for (action, uri) in self.__uploadLocalResource(localResuri):
                yield (action, uri)
        self._remoteRo.reloadManifest()
        
        for resuri in self._remoteRo.getAggregatedResources():
            for (action, uri) in self.__checkRemoteResource(resuri):
                yield (action, uri)
        self._remoteRo.reloadManifest()
                    
        for (ann_node, ann_body, ann_target) in self._localRo.getAllAnnotationNodes():
            for (action, uri) in self.__uploadLocalAnnotation(ann_node, ann_body, ann_target):
                yield (action, uri)
        self._remoteRo.reloadManifest()
                
        for (ann_node, ann_body, ann_target) in self._remoteRo.getAllAnnotationNodes():
            for (action, uri) in self.__checkRemoteAnnotation(ann_node):
                yield (action, uri)
        self._remoteRo.reloadManifest()
        
        self._localRo.saveRegistries()
        return
    
    def __uploadLocalResource(self, localResuri):
        try:
            respath = self._localRo.getComponentUriRel(localResuri)
            if not self._remoteRo.isAggregatedResource(respath):
                for (action, uri) in self.__createResource(localResuri, respath):
                    yield (action, uri)
            else:
                for (action, uri) in self.__updateResource(localResuri, respath):
                    yield (action, uri)
        except Exception as e:
            log.error("Error when processing resource %s: %s"%(localResuri, e))
            yield (ACTION_ERROR, e)

    
    def __createResource(self, localResuri, respath):
        log.debug("ResourceSync.pushResearchObject: %s does was not aggregated in the remote RO"%(respath))
        if self._localRo.isInternalResource(localResuri):
            log.debug("ResourceSync.pushResearchObject: %s is internal"%(localResuri))
            if self._localRo.isAnnotationNode(respath):
                # annotations are handled separately
                pass
            else:
                yield (ACTION_AGGREGATE_INTERNAL, respath)
                filename = ro_uriutils.getFilenameFromUri(localResuri)
                currentChecksum = self._localRo.calculateChecksum(filename)
                rf = open(filename, 'r')
                (status, reason, headers, resuri) = self._remoteRo.aggregateResourceInt(
                                          respath, 
                                          mimetypes.guess_type(respath)[0], 
                                          rf)
                self._localRo.getRegistries()["%s,etag"%filename] = headers.get("etag", None)
                self._localRo.getRegistries()["%s,checksum"%filename] = currentChecksum
        elif self._localRo.isExternalResource(localResuri):
            log.debug("ResourceSync.pushResearchObject: %s is external"%(localResuri))
            yield (ACTION_AGGREGATE_EXTERNAL, respath)
            self._localRo.aggregateResourceExt(respath)
        else:
            log.error("ResourceSync.pushResearchObject: %s is neither internal nor external"%(localResuri))
            
    def __updateResource(self, localResuri, respath):
        log.debug("ResourceSync.pushResearchObject: %s does was already aggregated in the remote RO"%(respath))
        if self._localRo.isInternalResource(localResuri):
            log.debug("ResourceSync.pushResearchObject: %s is internal"%(localResuri))
            if self._localRo.isAnnotationNode(respath):
                # annotations are handled separately
                pass
            else:
                log.debug("ResourceSync.pushResearchObject: %s is a resource"%(localResuri))
                # Get remote ETag
                (status, reason, headers) = self._remoteRo.getHead(respath)
                if status != 200:
                    raise Exception("Error retrieving RO resource", "%03d %s (%s)"%(status, reason, respath))
                filename = ro_uriutils.getFilenameFromUri(localResuri)
                currentETag = headers.get("etag", None)
                currentChecksum = self._localRo.calculateChecksum(filename)
                # Check locally stored ETag
                previousETag = self._localRo.getRegistries().get("%s,etag"%filename, None)
                previousChecksum = self._localRo.getRegistries().get("%s,checksum"%filename, None)
                if not previousETag or previousETag != currentETag or not previousChecksum or previousChecksum != currentChecksum:
                    rf = open(ro_uriutils.getFilenameFromUri(localResuri), 'r')
                    try:
                        (status, reason, headers, resuri) = self._remoteRo.updateResourceInt(respath, 
                                                   mimetypes.guess_type(localResuri)[0],
                                                   rf)
                        self._localRo.getRegistries()["%s,etag"%filename] = headers.get("etag", None)
                        self._localRo.getRegistries()["%s,checksum"%filename] = currentChecksum
                        if not previousETag or previousETag != currentETag:
                            log.debug("ResourceSync.pushResearchObject: %s has been modified in ROSRS (ETag was %s is %s)"%(respath, previousETag, currentETag))
                            yield (ACTION_UPDATE_OVERWRITE, respath)
                        elif not previousChecksum or previousChecksum != currentChecksum:
                            log.debug("ResourceSync.pushResearchObject: %s has been modified locally (checksum was %s is %s)"%(respath, previousChecksum, currentChecksum))
                            yield (ACTION_UPDATE, respath)
                    except ROSRS_Error as e:
                        yield (ACTION_ERROR, e)
                else:
                    log.debug("ResourceSync.pushResearchObject: %s has NOT been modified"%(respath))
                    yield (ACTION_SKIP, respath)
        elif self._localRo.isExternalResource(localResuri):
            log.debug("ResourceSync.pushResearchObject: %s is external"%(localResuri))
            yield (ACTION_SKIP, localResuri)
        else:
            log.error("ResourceSync.pushResearchObject: %s is neither internal nor external"%(localResuri))

    def __checkRemoteResource(self, resuri):
        respath = self._remoteRo.getComponentUriRel(resuri)
        if not self._localRo.isAggregatedResource(respath):
            if self._remoteRo.isAnnotationNode(respath):
                # annotations are handled separately
                pass
            else:
                log.debug("ResourceSync.pushResearchObject: %s will be deaggregated"%(resuri))
                try:
                    self._remoteRo.deaggregateResource(resuri)
                    yield (ACTION_DELETE, resuri)
                except ROSRS_Error as e:
                    yield (ACTION_ERROR, e)
                        
                
    def __uploadLocalAnnotation(self, ann_node, ann_body, ann_target):
        annpath = self._localRo.getComponentUriRel(ann_node)
        bodypath = self._localRo.getComponentUriRel(ann_body)
        targetpath = self._localRo.getComponentUriRel(ann_target)
        if isinstance(ann_node, rdflib.BNode) or not self._remoteRo.isAnnotationNode(annpath):
            log.debug("ResourceSync.pushResearchObject: %s is a new annotation"%(annpath))
            try:
                (_, _, remote_ann_node_uri) = self._remoteRo.addAnnotationNode(bodypath, targetpath)
                remote_ann_node_path = self._remoteRo.getComponentUriRel(remote_ann_node_uri)
                self._localRo.replaceUri(ann_node, self._localRo.getComponentUriAbs(remote_ann_node_path))
                yield (ACTION_AGGREGATE_ANNOTATION, remote_ann_node_path)
            except ROSRS_Error as e:
                yield (ACTION_ERROR, e)
        else:
            log.debug("ResourceSync.pushResearchObject: %s is an existing annotation"%(annpath))
            self._remoteRo.updateAnnotationNode(annpath, bodypath, targetpath)
            yield (ACTION_UPDATE_ANNOTATION, ann_node)
            
    def __checkRemoteAnnotation(self, ann_node):
        annpath = self._remoteRo.getComponentUriRel(ann_node)
        if not self._localRo.isAnnotationNode(annpath):
            log.debug("ResourceSync.pushResearchObject: annotation %s will be deleted"%(ann_node))
            try:
                self._remoteRo.deleteAnnotationNode(ann_node)
                yield (ACTION_DELETE_ANNOTATION, ann_node)
            except ROSRS_Error as e:
                yield (ACTION_ERROR, e)
        pass

def pushZipRO(localRo, remoteRo, force = False):
    return
