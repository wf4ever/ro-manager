'''
Created on 15-09-2011

@author: piotrhol
'''
import unittest
from sync.RosrsSync import RosrsSync
from sync.BackgroundSync import BackgroundResourceSync
from sync.test.TestConfig import ro_test_config
import logging
from os import rename, utime
from os.path import exists

class Test(unittest.TestCase):
    
    files1 = { 'data/ro-test-1/.ro_manifest/manifest.rdf', 
             'data/ro-test-1/file1.txt',
             'data/ro-test-1/file3.jpg',
             'data/ro-test-1/file with spaces.txt',
             'data/ro-test-1/subdir1/file2.txt',
             'data/ro-test-1/README-ro-test-1' }
    fileToDelete = 'data/ro-test-1/file1.txt'
    fileToReplace = 'data/ro-test-1/file1beta.txt'
    fileToTouch = 'data/ro-test-1/file with spaces.txt'
    fileToModify = 'data/ro-test-1/subdir1/file2.txt'

    filesAll = { 'data/ro-test-1/.ro_manifest/manifest.rdf',
                 'data/ro-test-1/file1.txt',
                 'data/ro-test-1/file3.jpg',
                 'data/ro-test-1/file with spaces.txt',
                 'data/ro-test-1/subdir1/file2.txt',
                 'data/ro-test-1/README-ro-test-1',
                 'data/ro-test-2/file4.txt' }
    
    modifiedFileContent = """lorem ipsum
ora et labora"""

    def setUp(self):
        self.__sync = RosrsSync(ro_test_config.ROSRS_HOST, ro_test_config.ROSRS_USERNAME, ro_test_config.ROSRS_PASSWORD)
        self.__sync.postWorkspace()
        self.__sync.postRo(ro_test_config.RO_ID)
        self.__sync.postVersion(ro_test_config.RO_ID, ro_test_config.VER_ID)
        logging.basicConfig()
        logging.getLogger("sync.BackgroundSync").setLevel(logging.DEBUG)
        return

    def tearDown(self):
        self.__sync.deleteWorkspace()
        if (exists(self.fileToReplace)):
            rename(self.fileToReplace, self.fileToDelete)
        with open(self.fileToModify, 'w') as f:
            f.write(self.modifiedFileContent)
            f.close()
        return

    def testSyncRecources(self):
        back = BackgroundResourceSync(self.__sync, True)
        
        (sent, deleted) = back.pushAllResources(ro_test_config.RO_ID, "data/%s" % ro_test_config.RO_DIR)
        self.assertEquals(sent, self.files1, "Sent files1 are not equal")
        self.assertEquals(deleted, set())

        rename(self.fileToDelete, self.fileToReplace)
        utime(self.fileToTouch, None)
        with open(self.fileToModify, 'a') as f:
            f.write("foobar")
            f.close()
        
        (sent, deleted) = back.pushAllResources(ro_test_config.RO_ID, "data/%s" % ro_test_config.RO_DIR)
        self.assertEquals(sent, {self.fileToReplace, self.fileToModify}, "New sent file")
        self.assertEquals(deleted, {self.fileToDelete}, "Deleted file")

        (sent, deleted) = back.pushAllResources(ro_test_config.RO_ID, "data/%s" % ro_test_config.RO_DIR)
        self.assertEquals(sent, set())
        self.assertEquals(deleted, set())
        rename(self.fileToReplace, self.fileToDelete)
        return
    
    def testSyncWorkspace(self):
        back = BackgroundResourceSync(self.__sync, True)
        self.assertRaises(Exception, back.pushAllResourcesInWorkspace, "data")
        (sent, deleted) = back.pushAllResourcesInWorkspace("data", True)
        self.assertEquals(sent, self.filesAll, "Send all workspace resource")
        self.assertEquals(deleted, set())
        self.assertTupleEqual((set(), set()), back.pushAllResourcesInWorkspace("data"), 
                              "Sync workspace after creating RO")
        return
    
    def testSaveLoadRegistries(self):
        back = BackgroundResourceSync(self.__sync, True)
        (sent, deleted) = back.pushAllResourcesInWorkspace("data", True)
        self.assertEquals(sent, self.filesAll, "Send all workspace resource")
        self.assertEquals(deleted, set())
        back = BackgroundResourceSync(self.__sync, False)
        self.assertTupleEqual((set(), set()), back.pushAllResourcesInWorkspace("data"), 
                              "Sync workspace after loading registries")
        back = BackgroundResourceSync(self.__sync, True)
        (sent, deleted) = back.pushAllResourcesInWorkspace("data", True)
        self.assertEquals(sent, self.filesAll, "Send all workspace resource")
        self.assertEquals(deleted, set())
        return
    
    def testGetRoId(self):
        back = BackgroundResourceSync(self.__sync)
        roId = back.getRoId("data/ro-test-1")
        self.assertEquals(roId, "ro1-identifier", "Wrong RO id read from manifest")
        roId = back.getRoId("data/ro-test-2")
        self.assertIsNone(roId, "RO id should be None when there is no manifest")
        pass
    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testSyncRecources']
    unittest.main()
