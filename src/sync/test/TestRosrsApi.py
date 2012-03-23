'''
Created on 14-09-2011

@author: piotrhol
'''

import sys
if __name__ == "__main__":
    sys.path.append("../..")

from MiscLib import TestUtils
from os.path import getsize
from rocommand.test import TestROSupport
from sync.RosrsApi import RosrsApi
from sync.test.TestConfig import ro_test_config
from zipfile import ZipFile

class TestRosrsApi(TestROSupport.TestROSupport):
    
    """
    Test ro annotation commands
    """
    def setUp(self):
        super(TestRosrsApi, self).setUp()
        return

    def tearDown(self):
        super(TestRosrsApi, self).tearDown()
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

    def testNull(self):
        assert True, 'Null test failed'

    def testROCreation(self):
        api = RosrsApi(ro_test_config.ROSRS_URI, ro_test_config.ROSRS_ACCESS_TOKEN)
        api.postRo(ro_test_config.RO_ID)
        api.putFile(ro_test_config.RO_ID, "folderX/fileY.txt", "text/plain", open("data/ro-test-1/file1.txt"))
        api.deleteFile(ro_test_config.RO_ID, "folderX/fileY.txt")
        api.deleteRo(ro_test_config.RO_ID)
        
    def testGetRoAsZip(self):
        api = RosrsApi(ro_test_config.ROSRS_URI, ro_test_config.ROSRS_ACCESS_TOKEN)
        api.postRo(ro_test_config.RO_ID)
        api.putFile(ro_test_config.RO_ID, "folderX/fileY.txt", "text/plain", open("data/ro-test-1/file1.txt"))
        verzip = api.getRoAsZip(ro_test_config.RO_ID)
        zipfile = ZipFile(verzip)
        self.assertEquals(len(zipfile.read("folderX/fileY.txt")), getsize("data/ro-test-1/file1.txt"), "FileY size must be the same")
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
