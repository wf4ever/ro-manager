# $Id: TestAll.py 1047 2009-01-15 14:48:58Z graham $
#
# Unit testing for WebBrick library functions (Functions.py)
# See http://pyunit.sourceforge.net/pyunit.html
#

import sys, unittest, logging

# Add main library directory to python path
sys.path.append("../..")

import TestTestUtils
import TestFunctions
import TestCombinators
import TestDomHelpers
import TestScanFiles
import TestScanDirectories
import TestNetUtils
import TestSuperGlobal

# Code to run unit tests from all library test modules
def getTestSuite(select="unit"):
    suite = unittest.TestSuite()
    suite.addTest(TestTestUtils.getTestSuite(select=select))
    suite.addTest(TestFunctions.getTestSuite())
    suite.addTest(TestCombinators.getTestSuite())
    suite.addTest(TestDomHelpers.getTestSuite())
    suite.addTest(TestScanFiles.getTestSuite())
    suite.addTest(TestScanDirectories.getTestSuite())
    suite.addTest(TestNetUtils.getTestSuite())
    suite.addTest(TestSuperGlobal.getTestSuite())
    return suite

from MiscLib import TestUtils

if __name__ == "__main__":
    TestUtils.runTests("TestAll", getTestSuite, sys.argv)

# End.
