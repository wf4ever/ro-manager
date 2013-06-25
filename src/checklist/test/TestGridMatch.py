#!/usr/bin/env python

"""
Module to test combinator-based grid match functions
"""

import os, os.path
import sys
import re
import shutil
import unittest
import logging
import datetime
import StringIO
import json
import csv

log = logging.getLogger(__name__)

if __name__ == "__main__":
    # Add main project directory at start of python path
    sys.path.insert(0, "../..")

from MiscLib import TestUtils

from checklist import gridmatch 

# Base directory for RO tests in this module
testbase = os.path.dirname(os.path.realpath(__file__))

# Test suite
class TestGridMatch(unittest.TestCase):
    """
    Test ro annotation commands
    """
    def setUp(self):
        super(TestGridMatch, self).setUp()
        # Set up grid for testing
        csvname = testbase+"/TestGridMatch.csv"
        log.debug("CSV file: %s"%csvname)
        with open(csvname, "r") as csvfile:
            self.grid = gridmatch.GridCSV(csvfile, dialect=csv.excel)
        return

    def tearDown(self):
        super(TestGridMatch, self).tearDown()
        return

    # Actual tests follow

    def testNull(self):
        assert True, 'Null test failed'

    def testSimpleTextMatch(self):
        gm = gridmatch.text("Checklist:")
        (d,(r,c)) = gm.match(self.grid, 17, 0)
        self.assertEquals(d, {}, "expected empty dictionary")
        self.assertEquals(r, 18, "newrow mismatch")
        self.assertEquals(c, 1,  "newcol mismatch")
        return

    def testSimpleTextMatch_fail(self):
        gm = gridmatch.text("Checklist_not:")
        try:
            (d,(r,c)) = gm.match(self.grid, 17, 0)
        except gridmatch.GridMatchError, e:
            log.debug("GridMatchError: %s"%(e))
        except Exception, e:
            self.assertTrue(False, "Expected GridMatchError exception, got %d"%(e))
        else:
            log.debug("Matched: d: %s, r: %d, c:%d"%(repr(d), r, c))
            self.assertTrue(False, "Expected GridMatchError exception, got success: %s, %d, %d"%(repr(d), r, c))
        return

    def testGridMatchNextCol(self):
        gm = gridmatch.text("Checklist:") + gridmatch.text("Target")
        (d,(r,c)) = gm.match(self.grid, 17, 0)
        self.assertEquals(d, {}, "expected empty dictionary")
        self.assertEquals(r, 18, "newrow mismatch")
        self.assertEquals(c, 2,  "newcol mismatch")
        return

    def testGridMatchNextRow(self):
        gm = gridmatch.text("Target") // gridmatch.text("{+targetro}")
        (d,(r,c)) = gm.match(self.grid, 17, 1)
        self.assertEquals(d, {}, "expected empty dictionary")
        self.assertEquals(r, 19, "newrow mismatch")
        self.assertEquals(c, 2,  "newcol mismatch")
        return

    def testGridMatchAlt(self):
        gm = gridmatch.text("Checklist:") | gridmatch.text("Target")
        (d,(r,c)) = gm.match(self.grid, 17, 0)
        self.assertEquals(d, {}, "expected empty dictionary")
        self.assertEquals(r, 18, "newrow mismatch")
        self.assertEquals(c, 2,  "newcol mismatch")
        return

    def testSaveSimpleTextMatch(self):
        gm = gridmatch.save("foo") + gridmatch.text("Checklist:")
        (d,(r,c)) = gm.match(self.grid, 17, 0)
        self.assertEquals(d, {"foo": "Checklist:"}, "expected saved cell value")
        self.assertEquals(r, 18, "newrow mismatch")
        self.assertEquals(c, 1,  "newcol mismatch")
        gm = gridmatch.text("Checklist:") + gridmatch.save("foo")
        (d,(r,c)) = gm.match(self.grid, 17, 0)
        self.assertEquals(d, {"foo": "Target"}, "expected saved cell value")
        self.assertEquals(r, 17, "newrow mismatch")
        self.assertEquals(c, 1,  "newcol mismatch")
        return

    # Sentinel/placeholder tests

    def testUnits(self):
        assert (True)

    def testComponents(self):
        assert (True)

    def testIntegration(self):
        assert (True)

    def testPending(self):
        assert (False), "Pending tests follow"

# Assemble test suite

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
            , "testSimpleTextMatch"
            , "testSimpleTextMatch_fail"
            , "testGridMatchNextCol"
            , "testGridMatchNextRow"
            , "testSaveSimpleTextMatch"
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
    return TestUtils.getTestSuite(TestGridMatch, testdict, select=select)

if __name__ == "__main__":
    TestUtils.runTests("TestGridMatch.log", getTestSuite, sys.argv)

# End.
