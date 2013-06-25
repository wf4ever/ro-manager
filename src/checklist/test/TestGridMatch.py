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
        self.base = "/foo/bar#"
        with open(csvname, "rU") as csvfile:
            self.grid = gridmatch.GridCSV(self.base, csvfile, dialect=csv.excel)
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

    def testGridMatchAltValues(self):
        gm = ( (gridmatch.value("alt", "1") + gridmatch.text("Checklist:")) 
             | (gridmatch.value("alt", "2") + gridmatch.text("Target"))
             )
        (d,(r,c)) = gm.match(self.grid, 17, 0)
        self.assertEquals(d, {"alt": "1"}, "expected 1st alternative match")
        self.assertEquals(r, 18, "newrow mismatch")
        self.assertEquals(c, 1,  "newcol mismatch")
        (d,(r,c)) = gm.match(self.grid, 17, 1)
        self.assertEquals(d, {"alt": "2"}, "expected 2nd alternative match")
        self.assertEquals(r, 18, "newrow mismatch")
        self.assertEquals(c, 2,  "newcol mismatch")
        return

    def testGridMatchOptValue(self):
        gm = (gridmatch.value("alt", "1") + gridmatch.text("Checklist:")).optional()
        (d,(r,c)) = gm.match(self.grid, 17, 0)
        self.assertEquals(d, {"alt": "1"}, "expected optional match")
        self.assertEquals(r, 18, "newrow mismatch")
        self.assertEquals(c, 1,  "newcol mismatch")
        (d,(r,c)) = gm.match(self.grid, 17, 1)
        self.assertEquals(d, {}, "optional no-match match")
        self.assertEquals(r, 17, "newrow mismatch")
        self.assertEquals(c, 1,  "newcol mismatch")
        return

    def testGridMatchMinimModel(self):
        # Model:,#experiment_complete_model,,,,This model defines information that must be satisfied by the target RO for the target RO to be considered a complete and fully-described workflow experiment.,
        # Items:,Level,Rule,,,,
        # 010,SHOULD,#RO_has_hypothesys,,,RO should contain a resource describing the hypothesis the experiment is intended to test,
        # 020,SHOULD,#RO_has_sketch,,,RO should contain a resource that is a high level sketch of the workflow that is used to test the hypothesys,
        # 030,MUST,#WF_accessible,,,The RO must contain an accessible workflow definition,
        # 040,MUST,#WF_services_accessible,,,All services used by the workflow must be live,
        # 050,MUST,#RO_has_inputdata,,,The RO must specify input data that is used by the workflow,
        # 060,SHOULD,#RO_has_conclusion,,,The RO should contain a resource that describes outcomes and conclusions obtained by running the workflow. ,
        save   = gridmatch.save  
        text   = gridmatch.text
        refval = gridmatch.refval
        anyval = gridmatch.anyval
        gm = ( ( text("Model:") + refval("model_uri") ) //
               ( text("Items:") ) //
               ( anyval("seq")  + save("level") + (text("MUST") | text("SHOULD") | text("MAY")) + refval("req_uri") ).repeatdown("item", min=1)
             )
        (d,(r,c)) = gm.match(self.grid, 21, 0)
        self.assertEquals(r, 29, "newrow mismatch")
        self.assertEquals(c, 3,  "newcol mismatch")
        base = self.base
        self.assertEquals(d["model_uri"], base+"experiment_complete_model", "model_uri (%s)"%(d["model_uri"]))
        self.assertEquals(d["item"][0]["seq"],      "010",                          "seq[0]"  )
        self.assertEquals(d["item"][0]["level"],    "SHOULD",                       "level[0]")
        self.assertEquals(d["item"][0]["req_uri"],  base+"RO_has_hypothesys",       "seq[0]"  )
        self.assertEquals(d["item"][1]["seq"],      "020",                          "seq[1]"  )
        self.assertEquals(d["item"][1]["level"],    "SHOULD",                       "level[1]")
        self.assertEquals(d["item"][1]["req_uri"],  base+"RO_has_sketch",           "seq[1]"  )
        self.assertEquals(d["item"][2]["seq"],      "030",                          "seq[2]"  )
        self.assertEquals(d["item"][2]["level"],    "MUST",                         "level[2]")
        self.assertEquals(d["item"][2]["req_uri"],  base+"WF_accessible",           "seq[2]"  )
        self.assertEquals(d["item"][3]["seq"],      "040",                          "seq[3]"  )
        self.assertEquals(d["item"][3]["level"],    "MUST",                         "level[3]")
        self.assertEquals(d["item"][3]["req_uri"],  base+"WF_services_accessible",  "seq[3]"  )
        self.assertEquals(d["item"][4]["seq"],      "050",                          "seq[4]"  )
        self.assertEquals(d["item"][4]["level"],    "MUST",                         "level[4]")
        self.assertEquals(d["item"][4]["req_uri"],  base+"RO_has_inputdata",        "seq[4]"  )
        self.assertEquals(d["item"][5]["seq"],      "060",                          "seq[5]"  )
        self.assertEquals(d["item"][5]["level"],    "SHOULD",                       "level[5]")
        self.assertEquals(d["item"][5]["req_uri"],  base+"RO_has_conclusion",       "seq[5]"  )
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
            , "testGridMatchAltValues"
            , "testGridMatchOptValue"
            , "testGridMatchMinimModel"
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
