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
from MiscLib import TestUtils

class TestEvo(TestROEVOSupport.TestROEVOSupport):
    
    TEST_RO_ID = "ro-manager-evo-test-ro"
    TEST_SNAPHOT_RO_ID = "ro-manager-test-evo-snaphot-ro"
    TEST_SNAPHOT_ID = "ro-manager-test-evo-snaphot"
    
    def setUp(self):
        super(TestEvo, self).setUp()
        self.rosrs = ROSRS_Session(ro_test_config.ROSRS_URI, accesskey=ro_test_config.ROSRS_ACCESS_TOKEN)
        (status, reason) = self.rosrs.deleteRO(self.TEST_RO_ID+"/")
        (status, reason, rouri, manifest) = self.rosrs.createRO(self.TEST_RO_ID,
            "Test RO for ROEVO", "Test Creator", "2012-09-06")
        return

    def tearDown(self):
        (status, reason) = self.rosrs.deleteRO(self.TEST_RO_ID+"/")
        (status, reason) = self.rosrs.deleteRO(self.TEST_SNAPHOT_ID+"/")
        super(TestEvo, self).tearDown()
        return

    
    def testSnapshot(self):
        rosrs = ROSRS_Session(ro_test_config.ROSRS_URI, ro_test_config.ROSRS_ACCESS_TOKEN)
        assert self.createSnapshot(self.TEST_RO_ID + "/", self.TEST_SNAPHOT_ID, False) == "DONE"
        (status, reason, data, evo_type) = rosrs.getROEvolution(ro_test_config.ROSRS_URI + self.TEST_SNAPHOT_ID + "/" )
        assert  evo_type == 3
        self.freeze(ro_test_config.ROSRS_URI + self.TEST_SNAPHOT_ID + "/" )
        (status, reason, data, evo_type) = rosrs.getROEvolution(ro_test_config.ROSRS_URI + self.TEST_SNAPHOT_ID + "/" )
        assert  evo_type == 1
        (status, reason) = self.rosrs.deleteRO(self.TEST_RO_ID+"/")
        (status, reason) = self.rosrs.deleteRO(self.TEST_SNAPHOT_ID+"/")
                
    def testArchive(self):
        rosrs = ROSRS_Session(ro_test_config.ROSRS_URI, ro_test_config.ROSRS_ACCESS_TOKEN)
        assert self.createArchive(self.TEST_RO_ID + "/", self.TEST_SNAPHOT_ID, False) == "DONE"
        (status, reason, data, evo_type) = rosrs.getROEvolution(ro_test_config.ROSRS_URI + self.TEST_SNAPHOT_ID + "/" )
        assert  evo_type == 3
        self.freeze(ro_test_config.ROSRS_URI + self.TEST_SNAPHOT_ID + "/" )
        (status, reason, data, evo_type) = rosrs.getROEvolution(ro_test_config.ROSRS_URI + self.TEST_SNAPHOT_ID + "/" )
        assert  evo_type == 2
        (status, reason) = self.rosrs.deleteRO(self.TEST_RO_ID+"/")
        (status, reason) = self.rosrs.deleteRO(self.TEST_SNAPHOT_ID+"/")
    
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
