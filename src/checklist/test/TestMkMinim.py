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
import rdflib

log = logging.getLogger(__name__)

if __name__ == "__main__":
    # Add main project directory at start of python path
    sys.path.insert(0, "../..")

from MiscUtils import TestUtils

from rocommand import ro
from rocommand import ro_utils
from rocommand import ro_manifest
from rocommand.ro_namespaces import RDF, DCTERMS, RO, AO, ORE

from rocommand.test import TestROSupport
from rocommand.test import TestConfig
from rocommand.test import StdoutContext

from checklist.grid import (GridCSV, GridExcel)
from checklist import gridmatch 
from checklist import checklist_template 
from checklist import mkminim

# Base directory for RO tests in this module
testbase = os.path.dirname(os.path.realpath(__file__))

# Test suite
class TestMkMinim(TestROSupport.TestROSupport):
    """
    Test ro annotation commands
    """
    def setUp(self):
        super(TestMkMinim, self).setUp()
        return

    def tearDown(self):
        super(TestMkMinim, self).tearDown()
        return

    # Setup local config for Minim tests

    def setupConfig(self):
        return self.setupTestBaseConfig(testbase)

    # Annotate RO with metadata file
    def annotateResource(self, testbase, rodir, resref, annref):
        """
        Annotate named resource with named annotation resource
        Names are appended to the RO directory.

        Returns RO directory.
        """
        # $RO annotate $resuri -g $annuri
        args = [
            "ro", "annotate", rodir+"/"+resref, "-g", rodir+"/"+annref
            ]
        with StdoutContext.SwitchStdout(self.outstr):
            configdir = self.getConfigDir(testbase)
            robasedir = self.getRoBaseDir(testbase)
            status    = ro.runCommand(configdir, robasedir, args)
        outtxt = self.outstr.getvalue()
        assert status == 0, outtxt
        self.outstr = StringIO.StringIO()
        return rodir

    # Actual tests follow

    def testNull(self):
        assert True, 'Null test failed'

    def testSetupConfig(self):
        (configdir, robasedir) = self.setupConfig()
        config = ro_utils.readconfig(configdir)
        self.assertEqual(config["robase"],          os.path.abspath(robasedir))
        self.assertEqual(config["rosrs_uri"],       TestConfig.ro_test_config.ROSRS_URI)
        self.assertEqual(config["rosrs_access_token"],  TestConfig.ro_test_config.ROSRS_ACCESS_TOKEN)
        self.assertEqual(config["username"],        TestConfig.ro_test_config.ROBOXUSERNAME)
        self.assertEqual(config["useremail"],       TestConfig.ro_test_config.ROBOXEMAIL)
        return

    def testGridRead(self):
        """
        Basic test that Minim test file can be read
        """
        self.setupConfig()
        rodir     = self.createTestRo(testbase, "testro", "RO for Minim creation test", "ro-testMkMinim")
        rouri     = ro_manifest.getRoUri(rodir)
        gridname  = "TestMkMinim.csv"
        griduri   = ro_manifest.getComponentUri(rodir, gridname)
        gridcsv   = os.path.join(rodir, gridname)
        with open(gridcsv, "rU") as gridfile:
            grid = GridCSV(gridfile, baseuri=griduri, dialect=csv.excel)
        self.assertEqual(grid[0][0], "Minim definition for MkMinim testing")
        self.deleteTestRo(rodir)
        return

    def testGridMatch(self):
        self.setupConfig()
        rodir     = self.createTestRo(testbase, "testro", "RO for Minim creation test", "ro-testMkMinim")
        rouri     = ro_manifest.getRoUri(rodir)
        gridname  = "TestMkMinim.csv"
        gridcsv   = os.path.join(rodir, gridname)
        gridbase  = ""
        with open(gridcsv, "rU") as gridfile:
            grid = GridCSV(gridfile, baseuri=gridbase, dialect=csv.excel)
        self.assertEqual(grid[0][0], "Minim definition for MkMinim testing")

        (d,(r,c)) = checklist_template.checklist.match(grid, 0, 0)
        self.assertEquals(r, 87, "newrow (%d)"%(r))
        self.assertEquals(c, 1,  "newcol (%d)"%(c))
        ### print repr(d)
        self.assertEquals(d["matchtemplate"],       'checklist',                        "matchtemplate")
        self.assertEquals(d["prefixes"]['ro'],      'http://purl.org/wf4ever/ro#',      "Prefix 'ro'")
        self.assertEquals(d["prefixes"]['minim'],   'http://purl.org/minim/minim#',     "Prefix 'minim'")
        self.assertEquals(d["prefixes"]['ao'],      'http://purl.org/ao/',              "Prefix 'ao'")
        self.assertEquals(d["prefixes"]['ex'],      'http://example.org/',              "Prefix 'ex'")

        self.assertEquals(len(d["checklists"]), 2, "Checklist count")
        self.assertEquals(d["checklists"][0]["model"],          '#model_test1',    "Checklist[1] model")
        self.assertEquals(d["checklists"][0]["target_urit"],    '{+targetro}',     "Checklist[1] uri")
        self.assertEquals(d["checklists"][0]["purpose"],        'test1',           "Checklist[1] purpose")
        self.assertEquals(d["checklists"][1]["model"],          '#model_test2',    "Checklist[2] model")
        self.assertEquals(d["checklists"][1]["target_urit"],    '{+targetro}',     "Checklist[2] uri")
        self.assertEquals(d["checklists"][1]["purpose"],        'test2',           "Checklist[2] purpose")

        self.assertEquals(len(d["models"]), 2, "Model count")
        self.assertEquals(d["models"][0]["modelid"],            '#model_test1',      "Model[1] id")
        self.assertEquals(len(d["models"][0]["items"]), 7,      "Model[1] item count")

        self.assertEquals(d["models"][1]["modelid"],            '#model_test2',      "Model[2] id")
        self.assertEquals(len(d["models"][1]["items"]), 5,      "Model[2] item count")

        self.assertEquals(len(d["requirements"]), 7, "Requirement count (%d found)"%(len(d["requirements"])))
        self.assertEquals(d["requirements"][0]["reqid"],            '#req_exists')
        self.assertEquals(d["requirements"][0]["exists"],           '?file rdf:type ex:Part')
        self.assertEquals(d["requirements"][0]["pass"],             'File exists as a part')
        self.assertEquals(d["requirements"][0]["fail"],             'File as part does not exist')
        self.assertEquals(d["requirements"][0].get("miss"),         None)

        self.assertEquals(d["requirements"][1]["reqid"],            '#req_foreach_exists')
        self.assertEquals(d["requirements"][1]["foreach"],          '?file rdf:type ex:Part')
        self.assertEquals(d["requirements"][1]["result_mod"],       'ORDER BY ?file')
        self.assertEquals(d["requirements"][1]["exists"],           '?file ex:partOf [ rdf:type ex:Whole ]')
        self.assertEquals(d["requirements"][1]["pass"],             'Files as part are partOf some indicated whole')
        self.assertEquals(d["requirements"][1]["fail"],             'File as part %(file)s is not part of some whole')

        self.assertEquals(d["requirements"][2]["reqid"],            '#req_foreach_aggregated')
        self.assertEquals(d["requirements"][2]["foreach"],          '?file rdf:type ex:Part')
        self.assertEquals(d["requirements"][2]["aggregates"],       '{+file}')
        self.assertEquals(d["requirements"][2]["pass"],             'All file as part resources are aggregated in RO')
        self.assertEquals(d["requirements"][2]["fail"],             'File as part %(file)s is not aggregated in RO')
        self.assertEquals(d["requirements"][2]["miss"],             'No file as part definitions are present')

        self.assertEquals(d["requirements"][6]["reqid"],            '#req_python')
        self.assertEquals(d["requirements"][6]["command"],          'python --version')
        self.assertEquals(d["requirements"][6]["response"],         '^Python 2\.7.*$')
        self.assertEquals(d["requirements"][6]["pass"],             'Python 2.7.x present')
        self.assertEquals(d["requirements"][6]["fail"],             'Python 2.7.x not present')

        self.deleteTestRo(rodir)
        return

    def testMkMinim(self):
        self.setupConfig()
        rodir     = self.createTestRo(testbase, "testro", "RO for testMkMinim", "ro-testMkMinim")
        rouri     = ro_manifest.getRoUri(rodir)
        # Create minim graph from CSV file
        # NOTE: a base URI may be specoified when decoding the grid or when constructing the minim
        #       graph.  The Minim graph uses its own relative references, so for consistency it may 
        #       be necessary to pass the grid base URI to mkminim.  The code below does this.
        gridname  = "TestMkMinim.csv"
        griduri   = ro_manifest.getComponentUri(rodir, gridname)
        gridcsv   = os.path.join(rodir, gridname)
        gridbase  = "http://example.org/base/"
        with open(gridcsv, "rU") as gridfile:
            grid = GridCSV(gridfile, baseuri=gridbase, dialect=csv.excel)
        (status, minimgr) = mkminim.mkminim(grid, baseuri=grid.resolveUri(""))
        self.assertEquals(status, 0)
        # Read expected graph
        graphname = os.path.join(rodir, "TestMkMinim.ttl")
        expectgr  = rdflib.Graph()
        with open(graphname) as expectfile:
            expectgr.parse(file=expectfile, publicID=gridbase, format="turtle")
        # Check content of minim graph
        ###minimgr.serialize(sys.stdout, format="turtle")
        self.checkTargetGraph(minimgr.graph(), expectgr, msg="Not found in constructed minim graph")

        self.deleteTestRo(rodir)
        return

    def testChecklistEval(self):
        """
        Test checklist evaluation with generated Minim file
        """
        self.setupConfig()
        rodir     = self.createTestRo(testbase, "testro", "RO for testMkMinim", "ro-testMkMinim")
        self.populateTestRo(testbase, rodir)
        self.annotateResource(testbase, rodir, "", "FileAnnotations.ttl")
        rouri     = ro_manifest.getRoUri(rodir)
        # Create minim graph from CSV file
        gridname  = "TestMkMinim.csv"
        griduri   = ro_manifest.getComponentUri(rodir, gridname)
        gridcsv   = os.path.join(rodir, gridname)
        gridbase  = "http://example.org/base/"
        with open(gridcsv, "rU") as gridfile:
            grid = GridCSV(gridfile, baseuri=gridbase, dialect=csv.excel)
        (status, minimgr) = mkminim.mkminim(grid, baseuri=grid.resolveUri(""))
        self.assertEquals(status, 0)
        # Write Minim
        minimname = "TestMkMinim_minim.ttl"
        with open(rodir+"/"+minimname, "w") as minimfile:
            minimgr.serialize(minimfile, format="turtle")
        # Evaluate checklist
        minimuri = ro_manifest.getComponentUri(rodir, minimname)
        minimpurpose = "test1"
        args = [ "ro", "evaluate", "checklist"
               , "-a"
               , "-d", rodir+"/"
               , minimname
               , minimpurpose
               , "."
               ]
        self.outstr.seek(0)
        with StdoutContext.SwitchStdout(self.outstr):
            status = ro.runCommand(
                os.path.join(testbase, TestConfig.ro_test_config.CONFIGDIR),
                os.path.join(testbase, TestConfig.ro_test_config.ROBASEDIR),
                args)
        outtxt = self.outstr.getvalue()
        assert status == 0, "Status %d, outtxt: %s"%(status,outtxt)
        log.debug("status %d, outtxt: %s"%(status, outtxt))
        # Check response returned
        expect = (
            [ "Research Object file://%s/:"%(rodir)
            , "Fully complete for test1 of resource ."
            , "Satisfied requirements:"
            , "  At least 3 file as part values are present"
            , "  At most 3 file as part values are present"
            , "  All file as part resources are accessible (live)"
            , "  All file as part resources are aggregated in RO"
            , "  Python 2.7.x present"
            , "  Files as part are partOf some indicated whole"
            , "  File exists as a part"
            , "Research object URI:     %s"%(rouri)
            , "Minimum information URI: %s"%(minimuri)
            ])
        self.outstr.seek(0)
        for line in self.outstr:
            self.assertIn(str(line)[:-1], expect)
        self.deleteTestRo(rodir)
        return

    def testChecklistEvalExcel(self):
        """
        Test checklist evaluation with generated Minim file from Excel source
        """
        self.setupConfig()
        rodir     = self.createTestRo(testbase, "testro", "RO for testMkMinim", "ro-testMkMinim")
        self.populateTestRo(testbase, rodir)
        self.annotateResource(testbase, rodir, "", "FileAnnotations.ttl")
        rouri     = ro_manifest.getRoUri(rodir)
        # Create minim graph from CSV file
        gridname  = "TestMkMinim.xls"
        griduri   = ro_manifest.getComponentUri(rodir, gridname)
        gridxls   = os.path.join(rodir, gridname)
        gridbase  = "http://example.org/base/"
        grid = GridExcel(gridxls, baseuri=gridbase)
        (status, minimgr) = mkminim.mkminim(grid, baseuri=grid.resolveUri(""))
        self.assertEquals(status, 0)
        # Write Minim
        minimname = "TestMkMinim_minim.ttl"
        with open(rodir+"/"+minimname, "w") as minimfile:
            minimgr.serialize(minimfile, format="turtle")
        # Evaluate checklist
        minimuri = ro_manifest.getComponentUri(rodir, minimname)
        minimpurpose = "test1"
        args = [ "ro", "evaluate", "checklist"
               , "-a"
               , "-d", rodir+"/"
               , minimname
               , minimpurpose
               , "."
               ]
        self.outstr.seek(0)
        with StdoutContext.SwitchStdout(self.outstr):
            status = ro.runCommand(
                os.path.join(testbase, TestConfig.ro_test_config.CONFIGDIR),
                os.path.join(testbase, TestConfig.ro_test_config.ROBASEDIR),
                args)
        outtxt = self.outstr.getvalue()
        assert status == 0, "Status %d, outtxt: %s"%(status,outtxt)
        log.debug("status %d, outtxt: %s"%(status, outtxt))
        # Check response returned
        expect = (
            [ "Research Object file://%s/:"%(rodir)
            , "Fully complete for test1 of resource ."
            , "Satisfied requirements:"
            , "  At least 3 file as part values are present"
            , "  At most 3 file as part values are present"
            , "  All file as part resources are accessible (live)"
            , "  All file as part resources are aggregated in RO"
            , "  Python 2.7.x present"
            , "  Files as part are partOf some indicated whole"
            , "  File exists as a part"
            , "Research object URI:     %s"%(rouri)
            , "Minimum information URI: %s"%(minimuri)
            ])
        self.outstr.seek(0)
        for line in self.outstr:
            self.assertIn(str(line)[:-1], expect)
        self.deleteTestRo(rodir)
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
            , "testSetupConfig"
            , "testGridRead"
            , "testGridMatch"
            , "testMkMinim"
            , "testChecklistEval"
            , "testChecklistEvalExcel"
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
    return TestUtils.getTestSuite(TestMkMinim, testdict, select=select)

if __name__ == "__main__":
    TestUtils.runTests("TestMkMinim.log", getTestSuite, sys.argv)

# End.
