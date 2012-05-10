#!/usr/bin/env python
# $Id: TestAll.py 1047 2009-01-15 14:48:58Z graham $
#
# Unit testing for WebBrick library functions (Functions.py)
# See http://pyunit.sourceforge.net/pyunit.html
#

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
import TestAnnotations
import TestROMetadata
import TestMinimAccess
import TestEvalChecklist
import TestRosrsApi
import TestResourceSync
import TestSyncCommands

# Code to run unit tests from all library test modules
def getTestSuite(select="unit"):
    suite = unittest.TestSuite()
    suite.addTest(TestBasicCommands.getTestSuite(select=select))
    suite.addTest(TestAnnotationUtils.getTestSuite(select=select))
    suite.addTest(TestManifest.getTestSuite(select=select))
    suite.addTest(TestAnnotations.getTestSuite(select=select))
    suite.addTest(TestROMetadata.getTestSuite(select=select))
    suite.addTest(TestMinimAccess.getTestSuite(select=select))
    suite.addTest(TestEvalChecklist.getTestSuite(select=select))
    suite.addTest(TestRosrsApi.getTestSuite(select=select))
    suite.addTest(TestResourceSync.getTestSuite(select=select))
    suite.addTest(TestSyncCommands.getTestSuite(select=select))
    return suite

from MiscLib import TestUtils

if __name__ == "__main__":
    print "By default, runs quick tests only."
    print "Use \"python TestAll.py all\" to run all tests"
    TestUtils.runTests("TestAll", getTestSuite, sys.argv)

# End.
