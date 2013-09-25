import sys 

if __name__ == "__main__":
    # Add main project directory and ro manager directories at start of python path
    sys.path.insert(0, "../..")
    sys.path.insert(0, "..")

#internal
import rocommand.ro as ro
import TestROEVOSupport
from ROSRS_Session import ROSRS_Session
from TestConfig import ro_test_config
from StdoutContext import SwitchStdout
#external
from MiscUtils import TestUtils

class TestEvo(TestROEVOSupport.TestROEVOSupport):
    
    TEST_RO_ID = "ro-manager-evo-test-ro"
    TEST_SNAPHOT_RO_ID = "ro-manager-test-evo-snaphot-ro"
    TEST_SNAPHOT_ID = "ro-manager-test-evo-snaphot"
    TEST_CREATED_RO_ID = ""
    
    def setUp(self):
        super(TestEvo, self).setUp()
        self.rosrs = ROSRS_Session(ro_test_config.ROSRS_URI, accesskey=ro_test_config.ROSRS_ACCESS_TOKEN)
        (status, reason) = self.rosrs.deleteRO(self.TEST_RO_ID+"/")
        (status, reason, rouri, manifest) = self.rosrs.createRO(self.TEST_RO_ID,
            "Test RO for ROEVO", "Test Creator", "2012-09-06")
        self.TEST_CREATED_RO_ID = rouri
        return

    def tearDown(self):
        (status, reason) = self.rosrs.deleteRO(self.TEST_RO_ID+"/")
        (status, reason) = self.rosrs.deleteRO(self.TEST_SNAPHOT_ID+"/")
        (status, reason) = self.rosrs.deleteRO(self.TEST_CREATED_RO_ID)
        super(TestEvo, self).tearDown()
        return
    
    def testSnapshot(self):
        rosrs = ROSRS_Session(ro_test_config.ROSRS_URI, ro_test_config.ROSRS_ACCESS_TOKEN)
        (copy_status, snapshot_uri) = self.createSnapshot(self.TEST_CREATED_RO_ID, self.TEST_SNAPHOT_ID, False) 
        assert copy_status == "DONE"
        (status, reason, data, evo_type) = rosrs.getROEvolution(snapshot_uri)
        assert  evo_type == 3
        self.freeze(snapshot_uri)
        (status, reason, data, evo_type) = rosrs.getROEvolution(snapshot_uri)
        assert  evo_type == 1
        (status, reason) = self.rosrs.deleteRO(self.TEST_CREATED_RO_ID)
        (status, reason) = self.rosrs.deleteRO(snapshot_uri)
                
    def testArchive(self):
        rosrs = ROSRS_Session(ro_test_config.ROSRS_URI, ro_test_config.ROSRS_ACCESS_TOKEN)
        (copy_status, archiveUri) = self.createArchive(self.TEST_CREATED_RO_ID, self.TEST_SNAPHOT_ID, False) 
        assert copy_status == "DONE"
        (status, reason, data, evo_type) = rosrs.getROEvolution(archiveUri)
        assert  evo_type == 3
        self.freeze(archiveUri)
        (status, reason, data, evo_type) = rosrs.getROEvolution(archiveUri)
        assert  evo_type == 2
        (status, reason) = self.rosrs.deleteRO(self.TEST_CREATED_RO_ID)
        (status, reason) = self.rosrs.deleteRO(archiveUri)
    
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
            [ 
            ],
        "component":
            [ "testSnapshot"
            , "testArchive"
            ],
        "integration":
            [ 
            ],
        "pending":
            [ 
            ]
        }
    return TestUtils.getTestSuite(TestEvo, testdict, select=select)

if __name__ == "__main__":
    TestUtils.runTests("TestEvo.log", getTestSuite, sys.argv)
