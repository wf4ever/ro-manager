'''
Created on 15-09-2011

@author: piotrhol
'''
import sys
import urlparse
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
from rocommand.ro_metadata import ro_metadata
from rocommand.ro_remote_metadata import ro_remote_metadata, createRO, deleteRO
from rocommand.HTTPSession import HTTP_Session
from rocommand import ro_rosrs_sync

# Logging object
log = logging.getLogger(__name__)

# Base directory for RO tests in this module
testbase = os.path.dirname(os.path.abspath(__file__))

class TestRosrsSync(TestROSupport.TestROSupport):
    

    def setUp(self):
        super(TestRosrsSync, self).setUp()
        self.rosrs = HTTP_Session(ro_test_config.ROSRS_URI,
            accesskey=ro_test_config.ROSRS_ACCESS_TOKEN)
        return

    def tearDown(self):
        super(TestRosrsSync, self).tearDown()
        self.rosrs.close()
        return
    
    # Setup local config for local tests

    def setupConfig(self):
        return self.setupTestBaseConfig(testbase)

    def testNull(self):
        assert True, 'Null test failed'

    def testPush(self):
        rodir = self.createTestRo(testbase, "data/ro-test-1", "RO test push", "ro-testRoPush")
        localRo  = ro_metadata(ro_test_config, rodir)
        deleteRO(self.rosrs, urlparse.urljoin(self.rosrs.baseuri(), "TestPushRO/"))
        (_,_,rouri,_) = createRO(self.rosrs, "TestPushRO")
        remoteRo = ro_remote_metadata(ro_test_config, self.rosrs, rouri)
        remoteRo.aggregateResourceExt("http://www.example.org")
        
        for (action, resuri) in ro_rosrs_sync.pushResearchObject(localRo, remoteRo):
            pass
        
        remoteRo.delete()
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
            , "testPush"
            ],
        "integration":
            [ "testIntegration"
            ],
        "pending":
            [ "testPending"
            ]
        }
    return TestUtils.getTestSuite(TestRosrsSync, testdict, select=select)

if __name__ == "__main__":
    TestUtils.runTests("TestRosrsSync.log", getTestSuite, sys.argv)
