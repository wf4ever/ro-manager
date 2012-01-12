#!/usr/bin/python

"""
Module to test RO manager manifest and aggregation commands

See: http://www.wf4ever-project.org/wiki/display/docs/RO+management+tool
"""

import os, os.path
import sys
import re
import shutil
import unittest
import logging
import datetime
import StringIO
try:
    # Running Python 2.5 with simplejson?
    import simplejson as json
except ImportError:
    import json

log = logging.getLogger(__name__)

if __name__ == "__main__":
    # Add main project directory at start of python path
    sys.path.insert(0, "../..")

import rdflib

from MiscLib import TestUtils

from rocommand import ro
from rocommand import ro_utils
from rocommand import ro_manifest
from rocommand.ro_manifest import RDF, DCTERMS, ROTERMS, RO, AO, ORE

from rocommand.test import TestROSupport
from rocommand.test import TestConfig
from rocommand.test import StdoutContext

from iaeval import ro_minim
from iaeval.ro_minim import MINIM

from iaeval import ro_eval_completeness

# Base directory for RO tests in this module
testbase = os.path.dirname(os.path.abspath(__file__))

class TestEvalCompleteness(TestROSupport.TestROSupport):
    """
    Test ro annotation commands
    """
    def setUp(self):
        super(TestEvalCompleteness, self).setUp()
        return

    def tearDown(self):
        super(TestEvalCompleteness, self).tearDown()
        return

    # Setup local config for Minim tests

    def setupConfig(self):
        return self.setupTestBaseConfig(testbase)

    # Actual tests follow

    def testNull(self):
        assert True, 'Null test failed'

    def testSetupConfig(self):
        (configdir, robasedir) = self.setupConfig()
        config = ro_utils.readconfig(configdir)
        self.assertEqual(config["robase"],          os.path.abspath(robasedir))
        self.assertEqual(config["rosrs_uri"],       TestConfig.ro_test_config.ROSRS_URI)
        self.assertEqual(config["rosrs_username"],  TestConfig.ro_test_config.ROSRS_USERNAME)
        self.assertEqual(config["rosrs_password"],  TestConfig.ro_test_config.ROSRS_PASSWORD)
        self.assertEqual(config["username"],        TestConfig.ro_test_config.ROBOXUSERNAME)
        self.assertEqual(config["useremail"],       TestConfig.ro_test_config.ROBOXEMAIL)
        return

    def testEvalAllPresent(self):
        """
        Evaluate complete RO against Minim description 
        """
        self.setupConfig()
        rodir      = self.createTestRo(testbase, "data", "RO test minim", "ro-testMinim")
        self.populateTestRo(testbase, rodir)
        evalresult = ro_eval_completeness.evaluate(
            rodir,                                      # RO location
            "Minim-UserRequirements.rdf",               # Minim file
            "docs/UserRequirements-astro.csv",          # Target resource
            "create")                                   # Purpose
        self.assertIn(MINIM.fullySatisfies,     evalresult['summary'])
        self.assertIn(MINIM.nominallySatisfies, evalresult['summary'])
        self.assertIn(MINIM.minimallySatisfies, evalresult['summary'])
        self.assertEquals(evalresult['missingMust'],   [])
        self.assertEquals(evalresult['missingShould'], [])
        self.assertEquals(evalresult['missingMay'],    [])
        self.deleteTestRo(rodir)
        return

    def testEvalMustMissing(self):
        """
        Evaluate complete RO against Minim description 
        """
        self.setupConfig()
        rodir      = self.createTestRo(testbase, "data", "RO test minim", "ro-testMinim")
        self.populateTestRo(testbase, rodir)
        rouri      = ro_manifest.getRoUri(rodir)
        minimbase  = ro_manifest.getComponentUri(rodir, "Minim-UserRequirements.rdf")
        modeluri   = ro_minim.getElementUri(minimbase, "#missingMustRequirement")
        evalresult = ro_eval_completeness.evaluate(
            rodir,                                      # RO location
            "Minim-UserRequirements.rdf",               # Minim file
            "docs/UserRequirements-bio.csv",            # Target resource
            "create")                                   # Purpose
        missing_must = (
            { 'level': "MUST"
            , 'model': modeluri 
            , 'label': rdflib.Literal("aggregates data/UserRequirements-bio.ods")
            , 'datarule':
              { 'aggregates': ro_manifest.getComponentUri(rodir, "data/UserRequirements-bio.ods")
              , 'derives':    ro_minim.getElementUri(minimbase, "#isPresent/data/UserRequirements-bio.ods")
              }
            , 'uri': ro_minim.getElementUri(minimbase, "#isPresent/data/UserRequirements-bio.ods") 
            })
        self.maxDiff=None
        self.assertEquals(evalresult['summary'],       [])
        self.assertEquals(evalresult['missingMust'],   [missing_must])
        self.assertEquals(evalresult['missingShould'], [])
        self.assertEquals(evalresult['missingMay'],    [])
        self.deleteTestRo(rodir)
        return

    def testEvalShouldMissing(self):
        """
        Evaluate complete RO against Minim description 
        """
        self.setupConfig()
        rodir      = self.createTestRo(testbase, "data", "RO test minim", "ro-testMinim")
        self.populateTestRo(testbase, rodir)
        rouri      = ro_manifest.getRoUri(rodir)
        minimbase  = ro_manifest.getComponentUri(rodir, "Minim-UserRequirements.rdf")
        modeluri   = ro_minim.getElementUri(minimbase, "#missingShouldRequirement")
        evalresult = ro_eval_completeness.evaluate(
            rodir,                                      # RO location
            "Minim-UserRequirements.rdf",               # Minim file
            "docs/UserRequirements-bio.html",           # Target resource
            "create")                                   # Purpose
        missing_should = (
            { 'level': "SHOULD"
            , 'model': modeluri 
            , 'label': rdflib.Literal("aggregates docs/missing.css")
            , 'datarule':
              { 'aggregates': ro_manifest.getComponentUri(rodir, "docs/missing.css")
              , 'derives':    ro_minim.getElementUri(minimbase, "#isPresent/docs/missing.css")
              }
            , 'uri': ro_minim.getElementUri(minimbase, "#isPresent/docs/missing.css") 
            })
        self.maxDiff=None
        self.assertEquals(evalresult['summary'],       [MINIM.minimallySatisfies])
        self.assertEquals(evalresult['missingMust'],   [])
        self.assertEquals(evalresult['missingShould'], [missing_should])
        self.assertEquals(evalresult['missingMay'],    [])
        self.deleteTestRo(rodir)
        return

    def testEvalMayMissing(self):
        """
        Evaluate complete RO against Minim description 
        """
        self.setupConfig()
        rodir      = self.createTestRo(testbase, "data", "RO test minim", "ro-testMinim")
        self.populateTestRo(testbase, rodir)
        rouri      = ro_manifest.getRoUri(rodir)
        minimbase  = ro_manifest.getComponentUri(rodir, "Minim-UserRequirements.rdf")
        modeluri   = ro_minim.getElementUri(minimbase, "#missingMayRequirement")
        evalresult = ro_eval_completeness.evaluate(
            rodir,                                      # RO location
            "Minim-UserRequirements.rdf",               # Minim file
            "docs/UserRequirements-bio.pdf",            # Target resource
            "create")                                   # Purpose
        missing_may = (
            { 'level': "MAY"
            , 'model': modeluri 
            , 'label': rdflib.Literal("aggregates docs/missing.css")
            , 'datarule':
              { 'aggregates': ro_manifest.getComponentUri(rodir, "docs/missing.css")
              , 'derives':    ro_minim.getElementUri(minimbase, "#isPresent/docs/missing.css")
              }
            , 'uri': ro_minim.getElementUri(minimbase, "#isPresent/docs/missing.css") 
            })
        self.maxDiff=None
        self.assertEquals(evalresult['summary'],       [MINIM.nominallySatisfies, MINIM.minimallySatisfies])
        self.assertEquals(evalresult['missingMust'],   [])
        self.assertEquals(evalresult['missingShould'], [])
        self.assertEquals(evalresult['missingMay'],    [missing_may])
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
            , "testEvalAllPresent"
            , "testEvalMustMissing"
            , "testEvalShouldMissing"
            , "testEvalMayMissing"
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
    return TestUtils.getTestSuite(TestEvalCompleteness, testdict, select=select)

if __name__ == "__main__":
    TestUtils.runTests("TestEvalCompleteness.log", getTestSuite, sys.argv)

# End.
