#!/usr/bin/env python

import sys, unittest

if __name__ == "__main__":
    # Add main project directory and ro manager directories at start of python path
    sys.path.insert(0, "..")
    sys.path.insert(0, "../..")
    sys.path.insert(0, "../../iaeval/test")
    sys.path.insert(0, "../../sync/test")

import TestConfig
import TestBasicCommands
import TestAnnotationUtils
import TestManifest
import TestROMetadata
import TestAnnotations
import TestLinks
import TestMinimAccess
import TestEvalChecklist
import TestROSRS_Session
import TestROSRSMetadata
import TestSyncCommands
import TestRemoteROMetadata
import TestRosrsSync

# Code to run unit tests from all library test modules
def getTestSuite(select="unit"):
    suite = unittest.TestSuite()
    suite.addTest(TestBasicCommands.getTestSuite(select=select))
    suite.addTest(TestAnnotationUtils.getTestSuite(select=select))
    suite.addTest(TestManifest.getTestSuite(select=select))
    suite.addTest(TestROMetadata.getTestSuite(select=select))
    suite.addTest(TestAnnotations.getTestSuite(select=select))
    suite.addTest(TestLinks.getTestSuite(select=select))
    suite.addTest(TestMinimAccess.getTestSuite(select=select))
    suite.addTest(TestEvalChecklist.getTestSuite(select=select))
    if select != "unit":
        suite.addTest(TestROSRS_Session.getTestSuite(select=select))
        suite.addTest(TestRosrsSync.getTestSuite(select=select))
        suite.addTest(TestRemoteROMetadata.getTestSuite(select=select))
        suite.addTest(TestROSRSMetadata.getTestSuite(select=select))
        suite.addTest(TestSyncCommands.getTestSuite(select=select))
    return suite

from MiscLib import TestUtils

def runTestSuite():
    """
    Transfer function for setup.py script ro-manager-test
    """
    base = os.path.dirname(__file__)
    #print "Run test suite assuming base path "+base
    sys.path.insert(0, os.path.normpath(base+"/..") )
    sys.path.insert(0, os.path.normpath(base+"/../..") )
    sys.path.insert(0, os.path.normpath(base+"/../../iaeval/test") )
    sys.path.insert(0, os.path.normpath(base+"/../../sync/test") )
    #print "Path: "+repr(sys.path)
    TestUtils.runTests("TestAll", getTestSuite, sys.argv)
    return 0

if __name__ == "__main__":
    print "By default, runs quick tests only."
    print "Use \"python TestAll.py all\" to run all tests"
    TestUtils.runTests("TestAll", getTestSuite, sys.argv)

# End.
