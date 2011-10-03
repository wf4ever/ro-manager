'''
Created on 14-09-2011

@author: piotrhol
'''
import unittest
from sync.RosrsSync import RosrsSync
from sync.test.TestConfig import ro_test_config


class Test(unittest.TestCase):
    
    def testROCreation(self):
        sync = RosrsSync(ro_test_config.ROSRS_URI, ro_test_config.ROSRS_USERNAME, ro_test_config.ROSRS_PASSWORD)
        sync.postWorkspace()
        sync.postRo(ro_test_config.RO_ID)
        ver1 = sync.postVersion(ro_test_config.RO_ID, ro_test_config.VER_ID)
#        sync.put_manifest(self.RO_ID, self.VER_ID, open("data/manifest.rdf"))
        sync.putFile(ro_test_config.RO_ID, ro_test_config.VER_ID, "folderX/fileY.txt", "text/plain", open("data/ro-test-1/file1.txt"))
        sync.postVersionAsCopy(ro_test_config.RO_ID, ro_test_config.VER_ID_2, ver1)
        sync.deleteFile(ro_test_config.RO_ID, ro_test_config.VER_ID, "folderX/fileY.txt")
        sync.deleteVersion(ro_test_config.RO_ID, ro_test_config.VER_ID)
        sync.deleteVersion(ro_test_config.RO_ID, ro_test_config.VER_ID_2)
        sync.deleteRo(ro_test_config.RO_ID)
        sync.deleteWorkspace()
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testROCreation']
    unittest.main()
