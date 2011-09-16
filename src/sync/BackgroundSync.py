'''
Created on 15-09-2011

@author: piotrhol
'''

from SyncRegistry import SyncRegistry
import mimetypes
import logging
from os.path import isdir, exists, join
from os import listdir, walk

log = logging.getLogger(__name__)

class BackgroundResourceSync(object):
    '''
    classdocs
    '''
   

    def __init__(self, rosrsSync):
        '''
        Constructor
        '''
        self.rosrsSync = rosrsSync
        self.syncRegistries = dict()
        mimetypes.init()
        
    def syncAllResourcesInWorkspace(self, srcDirectory):
        sentFiles = set()
        deletedFiles = set()
        for ro in listdir(srcDirectory):
            roDirectory = join(srcDirectory, ro)
            if isdir(roDirectory):
                for ver in listdir(roDirectory):
                    verDirectory = join(roDirectory, ver)
                    if isdir(verDirectory):
                        (s, d) = self.syncAllResources(ro, ver, verDirectory)
                        sentFiles = sentFiles.union(s)
                        deletedFiles = deletedFiles.union(d)
                    else:
                        log.warn("%s is a file in RO, it should probably be moved somewhere" % verDirectory)
            else:
                log.warn("%s is a file in workspace, it should probably be moved somewhere" % roDirectory)
        return (sentFiles, deletedFiles)
        
    def syncAllResources(self, roId, versionId, srcDirectory):
        sentFiles = self.__scanDirectories4Put(roId, versionId, srcDirectory)
        deletedFiles = self.__scanRegistries4Delete(roId, versionId, srcDirectory)
        return (sentFiles, deletedFiles)
    
    def __scanDirectories4Put(self, roId, versionId, srcdir):
        sentFiles = set()
        for root, dirs, files in walk(srcdir):
            for f in files:
                filepath = join(root, f)
                if (self.__checkFile4Put(roId, versionId, srcdir, filepath)):
                    sentFiles.add(filepath)
        return sentFiles
    
    def __checkFile4Put(self, roId, versionId, versiondir, filepath):
        assert filepath.startswith(versiondir)
        rosrsFilepath = filepath[len(versiondir) + 1:]
        if rosrsFilepath == "manifest.rdf":
            return
        put = True
        if (filepath in self.syncRegistries):
            put = self.syncRegistries[filepath].hasBeenModified()
        else:
            self.syncRegistries[filepath] = SyncRegistry(filepath)
        if put:
            contentType = mimetypes.guess_type(filepath)[0]
            fileObject = open(filepath)
            log.debug("Put file %s" % filepath)
            self.rosrsSync.putFile(roId, versionId, rosrsFilepath, contentType, fileObject)
        return put
    
    def __scanRegistries4Delete(self, roId, versionId, srcdir):
        deletedFiles = set()
        for r in self.syncRegistries.viewvalues():
            if r.filename.startswith(srcdir):
                if not exists(r.filename):
                    log.debug("Delete file %s" % r.filename)
                    deletedFiles.add(r.filename)
                    rosrsFilepath = r.filename[len(srcdir) + 1:]
                    self.rosrsSync.deleteFile(roId, versionId, rosrsFilepath)
        for f in deletedFiles:
            self.syncRegistries[f] = None
        return deletedFiles
        
