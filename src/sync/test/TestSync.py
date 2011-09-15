'''
Created on 14-09-2011

@author: piotrhol
'''
import unittest
import sys
from sync.RosrsSync import RosrsSync
from sync.test.TestConfig import ro_test_config


if __name__ == "__main__":
    # Add main project directory and ro manager directories to python path
    sys.path.append("../..")
    sys.path.append("..")

class Test(unittest.TestCase):
    
    RO_ID = "testRO"
    VER_ID = "version1"
    VER_ID_2 = "version2"

    def testROCreation(self):
        sync = RosrsSync(ro_test_config.ROSRS_HOST, ro_test_config.ROSRS_USERNAME, ro_test_config.ROSRS_PASSWORD)
        sync.post_workspace()
        sync.post_ro(self.RO_ID)
        ver1 = sync.post_version(self.RO_ID, self.VER_ID)
#        sync.put_manifest(self.RO_ID, self.VER_ID, open("data/manifest.rdf"))
        sync.put_file(self.RO_ID, self.VER_ID, "folderX/fileY.txt", "text/plain", open("data/file1.txt"))
        sync.post_version_as_copy(self.RO_ID, self.VER_ID_2, ver1)
        sync.delete_file(self.RO_ID, self.VER_ID, "folderX/fileY.txt")
        sync.delete_version(self.RO_ID, self.VER_ID)
        sync.delete_version(self.RO_ID, self.VER_ID_2)
        sync.delete_ro(self.RO_ID)
        sync.delete_workspace()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testROCreation']
    unittest.main()
