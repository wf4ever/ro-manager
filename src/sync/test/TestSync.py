'''
Created on 14-09-2011

@author: piotrhol
'''

import sys
if __name__ == "__main__":
    sys.path.append("../..")

import unittest
from sync.RosrsSync import RosrsSync
from sync.test.TestConfig import ro_test_config
from zipfile import ZipFile
import os

class Test(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        try:
            sync = RosrsSync(ro_test_config.ROSRS_URI, ro_test_config.ROSRS_USERNAME, ro_test_config.ROSRS_PASSWORD)
            sync.deleteWorkspace()
        except:
            pass
    
    def testROCreation(self):
        sync = RosrsSync(ro_test_config.ROSRS_URI, ro_test_config.ROSRS_USERNAME, ro_test_config.ROSRS_PASSWORD)
        sync.postWorkspace()
        sync.postRo(ro_test_config.RO_ID)
        ver1 = sync.postVersion(ro_test_config.RO_ID, ro_test_config.VER_ID)
        sync.putFile(ro_test_config.RO_ID, ro_test_config.VER_ID, "folderX/fileY.txt", "text/plain", open("data/ro-test-1/file1.txt"))
        sync.postVersionAsCopy(ro_test_config.RO_ID, ro_test_config.VER_ID_2, ver1)
        sync.deleteFile(ro_test_config.RO_ID, ro_test_config.VER_ID, "folderX/fileY.txt")
        sync.deleteVersion(ro_test_config.RO_ID, ro_test_config.VER_ID)
        sync.deleteVersion(ro_test_config.RO_ID, ro_test_config.VER_ID_2)
        sync.deleteRo(ro_test_config.RO_ID)
        sync.deleteWorkspace()
        
    @unittest.skip("putManifest not yet implemented")
    def testPutManifest(self):
        sync = RosrsSync(ro_test_config.ROSRS_URI, ro_test_config.ROSRS_USERNAME, ro_test_config.ROSRS_PASSWORD)
        sync.postWorkspace()
        sync.postRo(ro_test_config.RO_ID)
        sync.postVersion(ro_test_config.RO_ID, ro_test_config.VER_ID)
        res = sync.putManifest(ro_test_config.RO_ID, ro_test_config.VER_ID,
                               open("data/"+ro_test_config.ROMANIFESTPATH))
        self.assertIsNotNone(res, "Put manifest must be implemented")
        sync.deleteWorkspace()
        return
        
    def testGetVersionAsZip(self):
        sync = RosrsSync(ro_test_config.ROSRS_URI, ro_test_config.ROSRS_USERNAME, ro_test_config.ROSRS_PASSWORD)
        sync.postWorkspace()
        sync.postRo(ro_test_config.RO_ID)
        sync.postVersion(ro_test_config.RO_ID, ro_test_config.VER_ID)
        sync.putFile(ro_test_config.RO_ID, ro_test_config.VER_ID, "folderX/fileY.txt", "text/plain", open("data/ro-test-1/file1.txt"))
        verzip = sync.getVersionAsZip(ro_test_config.RO_ID, ro_test_config.VER_ID)
        zipfile = ZipFile(verzip)
        self.assertEquals(len(zipfile.read("folderX/fileY.txt")), os.path.getsize("data/ro-test-1/file1.txt"), "FileY size must be the same")
        self.assertTrue(len(zipfile.read("manifest.rdf")) > 0, "Size of manifest.rdf must be greater than 0")
        sync.deleteWorkspace()
        return
    
    def testGetRos(self):
        sync = RosrsSync(ro_test_config.ROSRS_URI, ro_test_config.ROSRS_USERNAME, ro_test_config.ROSRS_PASSWORD)
        sync.postWorkspace()
        sync.postRo(ro_test_config.RO_ID)
        sync.postRo(ro_test_config.RO_ID_2)
        ros = sync.getRos()
        self.assertSetEqual(ros, { ro_test_config.RO_ID, ro_test_config.RO_ID_2 }, "Returned ROs are not correct")
        sync.deleteWorkspace()
        return
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testROCreation']
    unittest.main()
