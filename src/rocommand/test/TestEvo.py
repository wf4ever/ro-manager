import sys
from rocommand.test.TestConfig import ro_test_config
if __name__ == "__main__":
    # Add main project directory and ro manager directories at start of python path
    sys.path.insert(0, "../..")
    sys.path.insert(0, "..")

#internal
import TestROSupport

from ROSRS_Session import ROSRS_Session
#external
from MiscLib import TestUtils

class TestEvo(TestROSupport.TestROSupport):
    
    TEST_RO_ID = "test-evo-ro"
    TEST_SNAPHOT_RO_ID = "test-evo-snaphot-ro"
    TEST_SNAPHOT_ID = "test-evo-snaphot"
    
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
        return
    
    def testArchive(self):

        return
     
    def testFreeze(self):
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
            [ 
            ],
        "component":
            [ "testSnapshot"
            , "testArchive"
            , "testFreeze"
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
