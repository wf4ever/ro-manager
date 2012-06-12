'''
Created on 14-09-2011

@author: piotrhol
'''

import sys
if __name__ == "__main__":
    sys.path.append("../..")

from MiscLib import TestUtils
import os.path
import random
import string
from rocommand.test import TestROSupport
from sync.RosrsApi import RosrsApi
from rocommand.test.TestConfig import ro_test_config
from zipfile import ZipFile

# Base directory for RO tests in this module
testbase = os.path.dirname(os.path.abspath(__file__))

class TestRosrsApi(TestROSupport.TestROSupport):
    
    """
    Test ro annotation commands
    """
    def setUp(self):
        super(TestRosrsApi, self).setUp()
        self.setupConfig()
        self.ident1 = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(16))
        self.ident2 = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(16))
        self.rodir = self.createTestRo(testbase, "../../rocommand/test/data/ro-test-1", self.ident1, self.ident1)
        return

    def tearDown(self):
        super(TestRosrsApi, self).tearDown()
        self.deleteTestRo(self.rodir)
        try:
            api = RosrsApi(ro_test_config.ROSRS_URI, ro_test_config.ROSRS_ACCESS_TOKEN)
            ros = api.getRos()
            for ro in ros:
                try:
                    api.deleteRoByUrl(ro)
                except:
                    pass
        except:
            pass
        return

    # Setup local config for local tests

    def setupConfig(self):
        return self.setupTestBaseConfig(testbase)
    
    def testNull(self):
        assert True, 'Null test failed'

    def testROCreation(self):
        api = RosrsApi(ro_test_config.ROSRS_URI, ro_test_config.ROSRS_ACCESS_TOKEN)
        api.postRo(self.ident1)
        api.putFile(self.ident1, "folderX/fileY.txt", "text/plain", open(os.path.join(self.rodir, "subdir1/subdir1-file.txt")))
        api.deleteFile(self.ident1, "folderX/fileY.txt")
        api.deleteRo(self.ident1)
        
    def testGetRoAsZip(self):
        api = RosrsApi(ro_test_config.ROSRS_URI, ro_test_config.ROSRS_ACCESS_TOKEN)
        api.postRo(self.ident1)
        api.putFile(self.ident1, "folderX/fileY.txt", "text/plain", open(os.path.join(self.rodir, "subdir1/subdir1-file.txt")))
        verzip = api.getRoAsZip(self.ident1)
        zipfile = ZipFile(verzip)
        self.assertEquals(len(zipfile.read("folderX/fileY.txt")), os.path.getsize(os.path.join(self.rodir, "subdir1/subdir1-file.txt")), "FileY size must be the same")
        self.assertTrue(len(zipfile.read(".ro/manifest.rdf")) > 0, "Size of manifest.rdf must be greater than 0")
        api.deleteRo(self.ident1)
        return
    
    def testGetRos(self):
        api = RosrsApi(ro_test_config.ROSRS_URI, ro_test_config.ROSRS_ACCESS_TOKEN)
        api.postRo(self.ident1)
        api.postRo(self.ident2)
        ros = api.getRos()
        self.assertSetEqual(set(ros), { ro_test_config.ROSRS_URI + "/ROs/" + self.ident1 + "/", ro_test_config.ROSRS_URI + "/ROs/" + self.ident2 + "/" }, "Returned ROs are not correct")
        api.deleteRo(self.ident1)
        api.deleteRo(self.ident2)
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
            , "testROCreation"
            , "testGetRoAsZip"
            , "testGetRos"
            ],
        "integration":
            [ "testIntegration"
            ],
        "pending":
            [ "testPending"
            ]
        }
    return TestUtils.getTestSuite(TestRosrsApi, testdict, select=select)

if __name__ == "__main__":
    TestUtils.runTests("TestRosrsApi.log", getTestSuite, sys.argv)
