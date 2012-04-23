'''
Created on 14-09-2011

@author: piotrhol
'''

import sys
if __name__ == "__main__":
    sys.path.append("../..")

from MiscLib import TestUtils
import os.path
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
        self.rodir = self.createTestRo(testbase, "../../rocommand/test/data/ro-test-1", "RO test resource sync", "ro-testResourceSync")
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
        api.postRo(ro_test_config.RO_ID)
        api.putFile(ro_test_config.RO_ID, "folderX/fileY.txt", "text/plain", open(os.path.join(self.rodir, "subdir1/subdir1-file.txt")))
        api.deleteFile(ro_test_config.RO_ID, "folderX/fileY.txt")
        api.deleteRo(ro_test_config.RO_ID)
        
    def testGetRoAsZip(self):
        api = RosrsApi(ro_test_config.ROSRS_URI, ro_test_config.ROSRS_ACCESS_TOKEN)
        api.postRo(ro_test_config.RO_ID)
        api.putFile(ro_test_config.RO_ID, "folderX/fileY.txt", "text/plain", open(os.path.join(self.rodir, "subdir1/subdir1-file.txt")))
        verzip = api.getRoAsZip(ro_test_config.RO_ID)
        zipfile = ZipFile(verzip)
        self.assertEquals(len(zipfile.read("folderX/fileY.txt")), os.path.getsize(os.path.join(self.rodir, "subdir1/subdir1-file.txt")), "FileY size must be the same")
        self.assertTrue(len(zipfile.read(".ro/manifest.rdf")) > 0, "Size of manifest.rdf must be greater than 0")
        api.deleteRo(ro_test_config.RO_ID)
        return
    
    def testGetRos(self):
        api = RosrsApi(ro_test_config.ROSRS_URI, ro_test_config.ROSRS_ACCESS_TOKEN)
        api.postRo(ro_test_config.RO_ID)
        api.postRo(ro_test_config.RO_ID_2)
        ros = api.getRos()
        self.assertSetEqual(set(ros), { ro_test_config.ROSRS_URI + "/ROs/" + ro_test_config.RO_ID + "/", ro_test_config.ROSRS_URI + "/ROs/" + ro_test_config.RO_ID_2 + "/" }, "Returned ROs are not correct")
        api.deleteRo(ro_test_config.RO_ID)
        api.deleteRo(ro_test_config.RO_ID_2)
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
            , "testROCreation"
            , "testGetRoAsZip"
            , "testGetRos"
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
    return TestUtils.getTestSuite(TestRosrsApi, testdict, select=select)

if __name__ == "__main__":
    TestUtils.runTests("TestRosrsApi.log", getTestSuite, sys.argv)
