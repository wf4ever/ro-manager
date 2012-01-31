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
from sync.RosrsSync import RosrsSync
from sync.test.TestConfig import ro_test_config
from zipfile import ZipFile

class TestSync(TestROSupport.TestROSupport):
    
    """
    Test ro annotation commands
    """
    def setUp(self):
        super(TestSync, self).setUp()
        return

    def tearDown(self):
        super(TestSync, self).tearDown()
        try:
            sync = RosrsSync(ro_test_config.ROSRS_URI, ro_test_config.ROSRS_ACCESS_TOKEN)
            try:
                sync.deleteRo(ro_test_config.RO_ID)
            except:
                pass
            try:
                sync.deleteRo(ro_test_config.RO_ID_2)
            except:
                pass
        except:
            pass
        return

    def testNull(self):
        assert True, 'Null test failed'

    def testROCreation(self):
        sync = RosrsSync(ro_test_config.ROSRS_URI, ro_test_config.ROSRS_ACCESS_TOKEN)
        sync.postRo(ro_test_config.RO_ID)
        sync.putFile(ro_test_config.RO_ID, "folderX/fileY.txt", "text/plain", open("data/ro-test-1/file1.txt"))
        sync.deleteFile(ro_test_config.RO_ID, "folderX/fileY.txt")
        sync.deleteRo(ro_test_config.RO_ID)
        
    def testGetRoAsZip(self):
        sync = RosrsSync(ro_test_config.ROSRS_URI, ro_test_config.ROSRS_ACCESS_TOKEN)
        sync.postRo(ro_test_config.RO_ID)
        sync.putFile(ro_test_config.RO_ID, "folderX/fileY.txt", "text/plain", open("data/ro-test-1/file1.txt"))
        verzip = sync.getRoAsZip(ro_test_config.RO_ID)
        zipfile = ZipFile(verzip)
        self.assertEquals(len(zipfile.read("folderX/fileY.txt")), getsize("data/ro-test-1/file1.txt"), "FileY size must be the same")
        self.assertTrue(len(zipfile.read(".ro/manifest.rdf")) > 0, "Size of manifest.rdf must be greater than 0")
        sync.deleteRo(ro_test_config.RO_ID)
        return
    
    def testGetRos(self):
        sync = RosrsSync(ro_test_config.ROSRS_URI, ro_test_config.ROSRS_ACCESS_TOKEN)
        sync.postRo(ro_test_config.RO_ID)
        sync.postRo(ro_test_config.RO_ID_2)
        ros = sync.getRos()
        self.assertSetEqual(set(ros), { ro_test_config.ROSRS_URI + "/ROs/" + ro_test_config.RO_ID + "/", ro_test_config.ROSRS_URI + "/ROs/" + ro_test_config.RO_ID_2 + "/" }, "Returned ROs are not correct")
        sync.deleteRo(ro_test_config.RO_ID)
        sync.deleteRo(ro_test_config.RO_ID_2)
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
    return TestUtils.getTestSuite(TestSync, testdict, select=select)

if __name__ == "__main__":
    TestUtils.runTests("TestSync.log", getTestSuite, sys.argv)
