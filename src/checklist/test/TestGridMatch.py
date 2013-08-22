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

from MiscUtils import TestUtils

from checklist.grid import (GridCSV, GridExcel)
from checklist import gridmatch 
from checklist import checklist_template 

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
        self.base = ""
        with open(csvname, "rU") as csvfile:
            self.grid = GridCSV(csvfile, baseuri=self.base, dialect=csv.excel)
        return

    def tearDown(self):
        super(TestGridMatch, self).tearDown()
        return

    # Actual tests follow

    def testNull(self):
        assert True, 'Null test failed'

    def testSimpleTextMatch(self):
        gm = gridmatch.text("Checklists:")
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
        gm = gridmatch.text("Checklists:") + gridmatch.text("Target")
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
        gm = gridmatch.save("foo") + gridmatch.text("Checklists:")
        (d,(r,c)) = gm.match(self.grid, 17, 0)
        self.assertEquals(d, {"foo": "Checklists:"}, "expected saved cell value")
        self.assertEquals(r, 18, "newrow mismatch")
        self.assertEquals(c, 1,  "newcol mismatch")
        gm = gridmatch.text("Checklists:") + gridmatch.save("foo")
        (d,(r,c)) = gm.match(self.grid, 17, 0)
        self.assertEquals(d, {"foo": "Target"}, "expected saved cell value")
        self.assertEquals(r, 17, "newrow mismatch")
        self.assertEquals(c, 1,  "newcol mismatch")
        return

    def testGridMatchAltValues(self):
        gm = ( (gridmatch.value("alt", "1") + gridmatch.text("Checklists:")) 
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
        gm = (gridmatch.value("alt", "1") + gridmatch.text("Checklists:")).optional()
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
        self.base = "/foo/bar#"
        self.grid.baseUri(self.base)
        (d,(r,c)) = gm.match(self.grid, 21, 0)
        self.assertEquals(r, 29, "newrow mismatch")
        self.assertEquals(c, 3,  "newcol mismatch")
        base = self.base
        self.assertEquals(d["model_uri"], base+"experiment_complete_model", "model_uri (%s)"%(d["model_uri"]))
        self.assertEquals(d["item"][0]["seq"],      "010",                          "seq[0] (%s)"%(d["item"][0]["seq"])  )
        self.assertEquals(d["item"][0]["level"],    "SHOULD",                       "level[0]")
        self.assertEquals(d["item"][0]["req_uri"],  base+"RO_has_hypothesis",       "seq[0]"  )
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

    def testGridMatchChecklist(self):
        """
        Test match of full checklist using the defined checklist template
        """
        (d,(r,c)) = checklist_template.checklist.match(self.grid, 0, 0)
        self.assertEquals(r, 72, "newrow (%d)"%(r))
        self.assertEquals(c, 1,  "newcol (%d)"%(c))
        base = self.base
        ### print repr(d)
        self.assertEquals(d["matchtemplate"],       'checklist',                        "matchtemplate")
        self.assertEquals(d["prefixes"]['ro'],      'http://purl.org/wf4ever/ro#',      "Prefix 'ro'")
        self.assertEquals(d["prefixes"]['minim'],   'http://purl.org/minim/minim#',     "Prefix 'minim'")
        self.assertEquals(d["prefixes"]['ao'],      'http://purl.org/ao/',              "Prefix 'ao'")
        self.assertEquals(d["prefixes"]['wfdesc'],  'http://purl.org/wf4ever/wfdesc#',  "Prefix 'wfdesc'")
        self.assertEquals(d["prefixes"]['wfprov'],  'http://purl.org/wf4ever/wfprov#',  "Prefix 'wfprov'")
        self.assertEquals(d["prefixes"]['wf4ever'], 'http://purl.org/wf4ever/wf4ever#', "Prefix 'wf4ever'")

        self.assertEquals(len(d["checklists"]), 2, "Checklist count")
        self.assertEquals(d["checklists"][0]["model"],       '#experiment_complete_model', "Checklist[1] model")
        self.assertEquals(d["checklists"][0]["target_urit"], '{+targetro}',                "Checklist[1] uri")
        self.assertEquals(d["checklists"][0]["purpose"],     'ready-to-release',           "Checklist[1] purpose")
        self.assertEquals(d["checklists"][1]["model"],       '#wf_accessible_model',       "Checklist[2] model")
        self.assertEquals(d["checklists"][1]["target_urit"], '{+targetro}',                "Checklist[2] uri")
        self.assertEquals(d["checklists"][1]["purpose"],     'wf-accessible',              "Checklist[2] purpose")

        self.assertEquals(len(d["models"]), 2, "Model count")
        self.assertEquals(d["models"][0]["modelid"],       '#experiment_complete_model', "Model[1] id")
        self.assertEquals(len(d["models"][0]["items"]), 6, "Model[1] item count")
        self.assertEquals(d["models"][0]["items"][1]["seq"],    '020',              "Model[1] Item[2] seq")
        self.assertEquals(d["models"][0]["items"][1]["level"],  'SHOULD',           "Model[1] Item[2] level")
        self.assertEquals(d["models"][0]["items"][1]["reqid"],  '#RO_has_sketch',   "Model[1] Item[2] reqid")
        self.assertEquals(d["models"][0]["items"][3]["seq"],    '040',              "Model[1] Item[2] seq")
        self.assertEquals(d["models"][0]["items"][3]["level"],  'MUST',             "Model[1] Item[2] level")
        self.assertEquals(d["models"][0]["items"][3]["reqid"],  '#WF_services_accessible', "Model[1] Item[2] reqid")

        self.assertEquals(d["models"][1]["modelid"],       '#wf_accessible_model',    "Model[2] id")
        self.assertEquals(len(d["models"][1]["items"]), 1, "Model[2] item count")
        self.assertEquals(d["models"][1]["items"][0]["seq"],    '030',              "Model[2] Item[1] seq")
        self.assertEquals(d["models"][1]["items"][0]["level"],  'MUST',             "Model[2] Item[1] level")
        self.assertEquals(d["models"][1]["items"][0]["reqid"],  '#WF_accessible',   "Model[2] Item[1] reqid")

        self.assertEquals(len(d["requirements"]), 6, "Requirement count")
        self.assertEquals(d["requirements"][0]["reqid"],        '#RO_has_hypothesis')
        self.assertEquals(d["requirements"][0]["exists"],       '?hypothesis rdf:type roterms:Hypothesis')
        self.assertEquals(d["requirements"][0]["pass"],         'Experiment hypothesis is present')
        self.assertEquals(d["requirements"][0]["fail"],         'Experiment hypothesis is not present')
        self.assertEquals(d["requirements"][0].get("miss"),     None)
        self.assertEquals(d["requirements"][2]["reqid"],        '#WF_accessible')
        self.assertEquals(d["requirements"][2]["foreach"],      '?wf rdf:type wfdesc:Workflow ;\n  rdfs:label ?wflab ;\n  wfdesc:hasWorkflowDefinition ?wfdef')
        self.assertEquals(d["requirements"][2].get("result_mod"), None)       
        self.assertEquals(d["requirements"][2]["islive"],       '{+wfdef}')
        self.assertEquals(d["requirements"][2]["pass"],         'All workflow definitions are accessible')
        self.assertEquals(d["requirements"][2]["fail"],         'The definition for workflow <i>%(wflab)s</i> is not accessible')
        self.assertEquals(d["requirements"][2]["miss"],         'No workflow definitions are present')
        self.assertEquals(d["requirements"][3]["reqid"],        '#WF_services_accessible')
        self.assertEquals(d["requirements"][3]["foreach"],      '?pr rdf:type wfdesc:Process ;\n  rdfs:label ?prlab .\n    { ?pr wf4ever:serviceURI ?pruri }\n  UNION\n    { ?pr wf4ever:wsdlURI ?pruri }')
        self.assertEquals(d["requirements"][3]["result_mod"],   'ORDER BY ?prlab')       
        self.assertEquals(d["requirements"][3]["islive"],       '{+pruri}')
        self.assertEquals(d["requirements"][3]["pass"],         'All web services used by workflows are accessible')
        self.assertEquals(d["requirements"][3]["fail"],         'One or more web services used by a workflow are inaccessible, including <a href="%(pruri)s"><i>%(prlab)s</i></a>')
        self.assertEquals(d["requirements"][3]["miss"],         'No web services are referenced by any workflow')

        return

    def testGridMatchChecklistExcel(self):
        """
        Test match of full checklist in an excel file, using the defined checklist template
        """
        # Override grid deined in setup()
        xlsname = testbase+"/TestGridMatch.xls"
        log.debug("Excel file: %s"%xlsname)
        self.base = ""
        self.grid = GridExcel(xlsname, baseuri=self.base)
        # Now run the tests
        self.testGridMatchChecklist()
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
            , "testGridMatchChecklist"
            , "testGridMatchChecklistExcel"
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
