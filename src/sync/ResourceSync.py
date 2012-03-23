'''
Created on 15-09-2011

@author: piotrhol
'''

from SyncRegistry import SyncRegistry
import mimetypes
import logging
from os.path import isdir, exists, join, basename
from os import listdir, walk
import pickle
from rocommand import ro_manifest
import urllib2

log = logging.getLogger(__name__)

class ResourceSync(object):
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
        
    def pushAllResourcesInWorkspace(self, srcDirectory, createRO = False):
        '''
        Scans all directories in srcDirectory as RO versions. 
        For each RO pushes all changes to ROSRS.
        
        If createRO is True, this method will try to create RO before pushing
        the resources. Otherwise, an exception will be raised if a directory is found without its
        corresponding RO in ROSRS.
        '''
        sentFiles = set()
        deletedFiles = set()
        for ro in listdir(srcDirectory):
            roDirectory = join(srcDirectory, ro)
            if isdir(roDirectory):
                try:
                    ro_manifest.readManifest(roDirectory)
                except:
                    log.debug("Not a valid RO: %s" % roDirectory)
                    continue
                (s, d) = self.pushAllResources(roDirectory, createRO)
                sentFiles = sentFiles.union(s)
                deletedFiles = deletedFiles.union(d)
            else:
                log.warn("%s is a file in workspace, it should probably be moved somewhere" % roDirectory)
        return (sentFiles, deletedFiles)
        
    def pushAllResources(self, roDirectory, createRO = False):
        '''
        Scans a given RO version directory for files that have been modified since last synchronization
        and pushes them to ROSRS. Modification is detected by checking modification times and checksums.
        '''
        roId = urllib2.quote(basename(roDirectory)) 
        ro_manifest.readManifest(roDirectory)
        if createRO:
            try:
                self.rosrsSync.postRo(roId)
            except:
                log.debug("Failed to create RO %s" % roId)
        sentFiles = self.__scanDirectories4Put(roId, roDirectory)
        deletedFiles = self.__scanRegistries4Delete(roId, roDirectory)
        self.__saveRegistries()
        return (sentFiles, deletedFiles)
    
    def __scanDirectories4Put(self, roId, srcdir):
        sentFiles = set()
        for root, dirs, files in walk(srcdir):
            for f in files:
                filepath = join(root, f)
                if self.__checkFile4Put(roId, srcdir, filepath):
                    sentFiles.add(filepath)
        return sentFiles
    
    def __checkFile4Put(self, roId, srcdir, filepath):
        assert filepath.startswith(srcdir)
        rosrsFilepath = filepath[len(srcdir) + 1:]
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
    
    def __scanRegistries4Delete(self, roId, srcdir):
        deletedFiles = set()
        for r in self.syncRegistries.viewvalues():
            if r.filename.startswith(srcdir):
                if not exists(r.filename):
                    log.debug("Delete file %s" % r.filename)
                    deletedFiles.add(r.filename)
                    rosrsFilepath = r.filename[len(srcdir) + 1:]
                    try:
                        self.rosrsSync.deleteFile(roId, rosrsFilepath)
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
        
