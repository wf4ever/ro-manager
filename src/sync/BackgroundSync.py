'''
Created on 15-09-2011

@author: piotrhol
'''

from SyncRegistry import SyncRegistry
import mimetypes
import logging
from os.path import isdir, exists, join
from os import listdir, walk
import pickle

log = logging.getLogger(__name__)

class BackgroundResourceSync(object):
    '''
    classdocs
    '''
   
    REGISTRIES_FILE = "registries.json"

    def __init__(self, rosrsSync, resetRegistries = False):
        '''
        Constructor
        '''
        self.rosrsSync = rosrsSync
        if resetRegistries:
            self.syncRegistries = dict()
        else:
            self.syncRegistries = self.__loadRegistries()
        mimetypes.init()
        
    def pushAllResourcesInWorkspace(self, srcDirectory, createROVersions = False):
        '''
        Scans all directories in srcDirectory as ROs, then all subdirectories as their versions.
        For each RO version pushes all changes to ROSRS.
        
        If createROVersions is True, this method will try to create RO and versions before pushing
        the resources. Otherwise, an exception will be raised if a directory is found without its
        corresponding RO or version in ROSRS.
        '''
        sentFiles = set()
        deletedFiles = set()
        for ro in listdir(srcDirectory):
            roDirectory = join(srcDirectory, ro)
            if isdir(roDirectory):
                if createROVersions:
                    try:
                        self.rosrsSync.postRo(ro)
                    except:
                        log.debug("Failed to create RO %s" % ro)
                for ver in listdir(roDirectory):
                    verDirectory = join(roDirectory, ver)
                    if isdir(verDirectory):
                        if createROVersions:
                            try:
                                self.rosrsSync.postVersion(ro, ver)
                            except:
                                log.debug("Failed to create version %s" % ver)
                        (s, d) = self.pushAllResources(ro, ver, verDirectory)
                        sentFiles = sentFiles.union(s)
                        deletedFiles = deletedFiles.union(d)
                    else:
                        log.warn("%s is a file in RO, it should probably be moved somewhere" % verDirectory)
            else:
                log.warn("%s is a file in workspace, it should probably be moved somewhere" % roDirectory)
        return (sentFiles, deletedFiles)
        
    def pushAllResources(self, roId, versionId, srcDirectory):
        '''
        Scans a given RO version directory for files that have been modified since last synchronization
        and pushes them to ROSRS. Modification is detected by checking modification times and checksums.
        '''
        sentFiles = self.__scanDirectories4Put(roId, versionId, srcDirectory)
        deletedFiles = self.__scanRegistries4Delete(roId, versionId, srcDirectory)
        self.__saveRegistries()
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
        if put:
            contentType = mimetypes.guess_type(filepath)[0]
            fileObject = open(filepath)
            log.debug("Put file %s" % filepath)
            self.rosrsSync.putFile(roId, versionId, rosrsFilepath, contentType, fileObject)
            self.syncRegistries[filepath] = SyncRegistry(filepath)
        return put
    
    def __scanRegistries4Delete(self, roId, versionId, srcdir):
        deletedFiles = set()
        for r in self.syncRegistries.viewvalues():
            if r.filename.startswith(srcdir):
                if not exists(r.filename):
                    log.debug("Delete file %s" % r.filename)
                    deletedFiles.add(r.filename)
                    rosrsFilepath = r.filename[len(srcdir) + 1:]
                    try:
                        self.rosrsSync.deleteFile(roId, versionId, rosrsFilepath)
                    except:
                        log.debug("File %s did not exist in ROSRS" % r.filename)
        for f in deletedFiles:
            del self.syncRegistries[f]
        return deletedFiles
    
    def __loadRegistries(self):
        try:
            rf = open(self.REGISTRIES_FILE, 'r')
            return pickle.load(rf)
        except:
            return dict()
        
    def __saveRegistries(self):
        rf = open(self.REGISTRIES_FILE, 'w')
        pickle.dump(self.syncRegistries, rf)
        return
        
