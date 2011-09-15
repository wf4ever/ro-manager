'''
Created on 15-09-2011

@author: piotrhol
'''

from SyncRegistry import SyncRegistry
import mimetypes
import logging
from os.path import isdir, exists
from os import listdir

log = logging.getLogger(__name__)

class BackgroundResourceSync(object):
    '''
    classdocs
    '''
   

    def __init__(self, rosrsSync):
        '''
        Constructor
        '''
        self.__rosrsSync = rosrsSync
        self.__syncRegistries = dict()
        mimetypes.init()
        
    def syncAllResourcesInWorkspace(self, srcDirectory):
        sentFiles = set()
        deletedFiles = set()
        for ro in listdir(srcDirectory):
            roDirectory = srcDirectory + "/" + ro
            if isdir(roDirectory):
                for ver in listdir(roDirectory):
                    verDirectory = roDirectory + "/" + ver
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
        sentFiles = self.__scanDirectories4Put(roId, versionId, srcDirectory, srcDirectory)
        deletedFiles = self.__scanRegistries4Delete(roId, versionId, srcDirectory)
        return (sentFiles, deletedFiles)
    
    def __scanDirectories4Put(self, roId, versionId, versiondir, srcdir):
        """
        Scan all sub-directories in a given source directory.
        Exceptions are thrown back to the calling program.
        """
        directoryList = listdir(srcdir)
        sentFiles = set()
        for directoryComponent in directoryList:
            path = srcdir + "/" + directoryComponent
            if isdir(path):
                log.debug("Adding Directory %s " % (path))
                sentFiles = sentFiles.union(self.__scanDirectories4Put(roId, versionId, versiondir, path))
            else:
                if (self.__checkFilePut__(roId, versionId, versiondir, path)):
                    sentFiles.add(path)
        return sentFiles
    
    def __checkFilePut__(self, roId, versionId, versiondir, filepath):
        assert filepath.startswith(versiondir)
        rosrsFilepath = filepath[len(versiondir) + 1:]
        if rosrsFilepath == "manifest.rdf":
            return
        put = True
        if (filepath in self.__syncRegistries):
            put = self.__syncRegistries[filepath].hasBeenModified()
        else:
            self.__syncRegistries[filepath] = SyncRegistry(filepath)
        if put:
            contentType = mimetypes.guess_type(filepath)[0]
            fileObject = open(filepath)
            log.debug("Put file %s" % filepath)
            self.__rosrsSync.putFile(roId, versionId, rosrsFilepath, contentType, fileObject)
        return put
    
    def __scanRegistries4Delete(self, roId, versionId, srcdir):
        deletedFiles = set()
        for r in self.__syncRegistries.viewvalues():
            if r.filename.startswith(srcdir):
                if not exists(r.filename):
                    log.debug("Delete file %s" % r.filename)
                    deletedFiles.add(r.filename)
                    rosrsFilepath = r.filename[len(srcdir) + 1:]
                    self.__rosrsSync.deleteFile(roId, versionId, rosrsFilepath)
        for f in deletedFiles:
            self.__syncRegistries[f] = None
        return deletedFiles
        
