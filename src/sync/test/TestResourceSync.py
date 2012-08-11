'''
Created on 15-09-2011

@author: piotrhol
'''
import sys
if __name__ == "__main__":
    # Add main project directory and ro manager directories at start of python path
    sys.path.insert(0, "../..")
    sys.path.insert(0, "..")

import logging
import random
import string
import os.path
from MiscLib import TestUtils
from rocommand.test import TestROSupport
from rocommand.test.TestConfig import ro_test_config
from sync.RosrsApi import RosrsApi
from sync.ResourceSync import ResourceSync

# Logging object
log = logging.getLogger(__name__)

# Base directory for RO tests in this module
testbase = os.path.dirname(os.path.abspath(__file__))

class TestResourceSync(TestROSupport.TestROSupport):
    
    files = ["subdir1/subdir1-file.txt"
             , "subdir2/subdir2-file.txt"
             , "README-ro-test-1"
             , ".ro/manifest.rdf"
             , "minim.rdf" ]

    fileToModify = "subdir1/subdir1-file.txt"
    fileToDelete = "README-ro-test-1"
    fileToReplace = "README-ro-test-2"
    fileToTouch = 'subdir2/subdir2-file.txt'
    
    modifiedFileContent = """lorem ipsum
ora et labora"""

    def setUp(self):
        super(TestResourceSync, self).setUp()
        self.setupConfig()
        self.ident1 = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(16))
        self.rodir = self.createTestRo(testbase, "../../rocommand/test/data/ro-test-1", self.ident1, self.ident1)
        self.workspacedir = os.path.join(testbase, ro_test_config.ROBASEDIR)
        try:
            self.__sync = RosrsApi(ro_test_config.ROSRS_URI, ro_test_config.ROSRS_ACCESS_TOKEN)
        except:
            pass
        logging.basicConfig()
        logging.getLogger("sync.ResourceSync").setLevel(logging.INFO)
        
        tmpFiles = set()
        for f in self.files:
            tmpFiles.add(os.path.join(self.rodir, f))
        self.files = tmpFiles
        self.fileToModify = os.path.join(self.rodir, self.fileToModify)
        self.fileToDelete = os.path.join(self.rodir, self.fileToDelete)
        self.fileToReplace = os.path.join(self.rodir, self.fileToReplace)
        self.fileToTouch = os.path.join(self.rodir, self.fileToTouch)
        return

    def tearDown(self):
        super(TestResourceSync, self).tearDown()
        self.deleteTestRo(self.rodir)
        try:
            self.__sync.deleteRo(self.ident1)
        except:
            pass
        return
    
    # Setup local config for local tests

    def setupConfig(self):
        return self.setupTestBaseConfig(testbase)

    def testNull(self):
        assert True, 'Null test failed'

    def testSyncRecources(self):
        self.__sync.postRo(self.ident1)
        back = ResourceSync(self.__sync)
        
        (sent, deleted) = back.pushAllResources(self.rodir, force = True)
        self.assertEquals(sent, self.files, "Sent files are not equal")
        self.assertEquals(deleted, set())

        os.rename(self.fileToDelete, self.fileToReplace)
        os.utime(self.fileToTouch, None)
        with open(self.fileToModify, 'a') as f:
            f.write("foobar")
            f.close()
        
        (sent, deleted) = back.pushAllResources(self.rodir)
        self.assertEquals(sent, {self.fileToReplace, self.fileToModify}, "New sent file")
        self.assertEquals(deleted, {self.fileToDelete}, "Deleted file")

        (sent, deleted) = back.pushAllResources(self.rodir)
        self.assertEquals(sent, set())
        self.assertEquals(deleted, set())
        os.rename(self.fileToReplace, self.fileToDelete)
        return
    
    def testSyncWorkspace(self):
        back = ResourceSync(self.__sync)
        self.assertRaises(Exception, back.pushAllResourcesInWorkspace, self.workspacedir, force = True)
        back = ResourceSync(self.__sync)
        (sent, deleted) = back.pushAllResourcesInWorkspace(self.workspacedir, True, True)
        log.debug("testSyncWorkspace: files: [%s]"%(", ".join(self.files)))
        log.debug("testSyncWorkspace: sent: [%s]"%(", ".join(sent)))
        self.assertSetEqual(sent, self.files, "Send all workspace resource")
        self.assertSetEqual(deleted, set())
        self.assertTupleEqual((set(), set()), back.pushAllResourcesInWorkspace(self.workspacedir), 
                              "Sync workspace after creating RO")
        return
    
    def testSaveLoadRegistries(self):
        back = ResourceSync(self.__sync)
        (sent, deleted) = back.pushAllResourcesInWorkspace(self.workspacedir, True, True)
        self.assertEquals(sent, self.files, "Send all workspace resource")
        self.assertEquals(deleted, set())
        back = ResourceSync(self.__sync)
        self.assertTupleEqual((set(), set()), back.pushAllResourcesInWorkspace(self.workspacedir), 
                              "Sync workspace after loading registries")
        back = ResourceSync(self.__sync)
        (sent, deleted) = back.pushAllResourcesInWorkspace(self.workspacedir, True, True)
        self.assertEquals(sent, self.files, "Send all workspace resource")
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
            ],
        "component":
            [ "testComponents"
            , "testSyncRecources"
            , "testSyncWorkspace"
            , "testSaveLoadRegistries"
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
