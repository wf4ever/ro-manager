'''
Created on 15-09-2011

@author: piotrhol
'''

from time import time
from os import path
import hashlib

class SyncRegistry:
    '''
    classdocs
    '''
    
    filename = None
    lastSyncTime = None
    checksum = None


    def __init__(self, filename, time = time(), checksum = None):
        '''
        Constructor
        '''
        self.filename = filename
        self.lastSyncTime = time
        self.checksum = self.__calculateMd5()
        
    def hasBeenModified(self):
        if (path.getmtime(self.filename) > self.lastSyncTime):
            if (self.__calculateMd5() != self.checksum):
                return True
        return False
        
    def __calculateMd5(self):
        m = hashlib.md5()
        with open(self.filename) as f:
            for line in f:
                m.update(line)
            f.close()
        return m.hexdigest()
        
    