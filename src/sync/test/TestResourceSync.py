'''
Created on 15-09-2011

@author: piotrhol
'''
import sys
if __name__ == "__main__":
    sys.path.append("../..")

import logging
from MiscLib import TestUtils
from os import rename, utime
from os.path import exists
from rocommand.test import TestROSupport
from sync.RosrsApi import RosrsApi
from sync.ResourceSync import ResourceSync
from sync.test.TestConfig import ro_test_config

class TestResourceSync(TestROSupport.TestROSupport):
    
    files1 = { 'data/ro-test-1/.ro/manifest.rdf',
             'data/ro-test-1/file1.txt',
             'data/ro-test-1/file3.jpg',
             'data/ro-test-1/file with spaces.txt',
             'data/ro-test-1/subdir1/file2.txt',
             'data/ro-test-1/README-ro-test-1' }
    fileToDelete = 'data/ro-test-1/file1.txt'
    fileToReplace = 'data/ro-test-1/file1beta.txt'
    fileToTouch = 'data/ro-test-1/file with spaces.txt'
    fileToModify = 'data/ro-test-1/subdir1/file2.txt'

    filesAll = { 'data/ro-test-1/.ro/manifest.rdf',
                 'data/ro-test-1/file1.txt',
                 'data/ro-test-1/file3.jpg',
                 'data/ro-test-1/file with spaces.txt',
                 'data/ro-test-1/subdir1/file2.txt',
                 'data/ro-test-1/README-ro-test-1' }
    
    modifiedFileContent = """lorem ipsum
ora et labora"""

    def setUp(self):
        try:
            self.__sync = RosrsApi(ro_test_config.ROSRS_URI, ro_test_config.ROSRS_ACCESS_TOKEN)
        except:
            pass
        logging.basicConfig()
        logging.getLogger("sync.ResourceSync").setLevel(logging.INFO)
        return

    def tearDown(self):
        try:
            self.__sync.deleteRo(ro_test_config.RO_ID)
        except:
            pass
        if (exists(self.fileToReplace)):
            rename(self.fileToReplace, self.fileToDelete)
        with open(self.fileToModify, 'w') as f:
            f.write(self.modifiedFileContent)
            f.close()
        return
    
    def testNull(self):
        assert True, 'Null test failed'

    def testSyncRecources(self):
        self.__sync.postRo(ro_test_config.RO_ID)
        back = ResourceSync(self.__sync)
        
        (sent, deleted) = back.pushAllResources("data/%s" % ro_test_config.RO_ID, force = True)
        self.assertEquals(sent, self.files1, "Sent files1 are not equal")
        self.assertEquals(deleted, set())

        rename(self.fileToDelete, self.fileToReplace)
        utime(self.fileToTouch, None)
        with open(self.fileToModify, 'a') as f:
            f.write("foobar")
            f.close()
        
        (sent, deleted) = back.pushAllResources("data/%s" % ro_test_config.RO_ID)
        self.assertEquals(sent, {self.fileToReplace, self.fileToModify}, "New sent file")
        self.assertEquals(deleted, {self.fileToDelete}, "Deleted file")

        (sent, deleted) = back.pushAllResources("data/%s" % ro_test_config.RO_ID)
        self.assertEquals(sent, set())
        self.assertEquals(deleted, set())
        rename(self.fileToReplace, self.fileToDelete)
        return
    
    def testSyncWorkspace(self):
        back = ResourceSync(self.__sync)
        self.assertRaises(Exception, back.pushAllResourcesInWorkspace, "data", force = True)
        back = ResourceSync(self.__sync)
        (sent, deleted) = back.pushAllResourcesInWorkspace("data", True, True)
        self.assertSetEqual(sent, self.filesAll, "Send all workspace resource")
        self.assertSetEqual(deleted, set())
        self.assertTupleEqual((set(), set()), back.pushAllResourcesInWorkspace("data"), 
                              "Sync workspace after creating RO")
        return
    
    def testSaveLoadRegistries(self):
        back = ResourceSync(self.__sync)
        (sent, deleted) = back.pushAllResourcesInWorkspace("data", True, True)
        self.assertEquals(sent, self.filesAll, "Send all workspace resource")
        self.assertEquals(deleted, set())
        back = ResourceSync(self.__sync)
        self.assertTupleEqual((set(), set()), back.pushAllResourcesInWorkspace("data"), 
                              "Sync workspace after loading registries")
        back = ResourceSync(self.__sync)
        (sent, deleted) = back.pushAllResourcesInWorkspace("data", True, True)
        self.assertEquals(sent, self.filesAll, "Send all workspace resource")
        self.assertEquals(deleted, set())
        return
    
def getTestSuite(select="unit"):
    """
    Get test suite

    select  is one of the following:
            "unit"      return suite of unit tests only
            "component" return suite of unit and component tests
            "all"       return suite of unit, component and integration tests
            "pending"   return suite of pending tests
            name        a single named test to be run
    """
    testdict = {
        "unit":
            [ "testUnits"
            , "testNull"
            , "testSyncRecources"
            , "testSyncWorkspace"
            , "testSaveLoadRegistries"
            ],
        "component":
            [ "testComponents"
            ],
        "integration":
            [ "testIntegration"
            ],
        "pending":
            [ "testPending"
            ]
        }
    return TestUtils.getTestSuite(TestResourceSync, testdict, select=select)

if __name__ == "__main__":
    TestUtils.runTests("TestResourceSync.log", getTestSuite, sys.argv)
