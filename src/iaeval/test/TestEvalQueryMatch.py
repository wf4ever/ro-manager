#!/usr/bin/python

"""
Module to test RO manager minim access functions

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

from rocommand import ro_manifest
from rocommand.ro_metadata import ro_metadata
from rocommand.ro_annotation import annotationTypes, annotationPrefixes

from rocommand.test import TestROSupport
from rocommand.test import TestConfig

from iaeval import ro_minim
from iaeval.ro_minim import MINIM

from iaeval import ro_eval_minim

# Base directory for RO tests in this module
testbase = os.path.dirname(os.path.realpath(__file__))

# Local ro_config for testing
ro_config = {
    "annotationTypes":      annotationTypes,
    "annotationPrefixes":   annotationPrefixes
    }

# Test suite
class TestEvalQueryMatch(TestROSupport.TestROSupport):
    """
    Test ro annotation commands
    """
    def setUp(self):
        super(TestEvalQueryMatch, self).setUp()
        return

    def tearDown(self):
        super(TestEvalQueryMatch, self).tearDown()
        return

    # Setup local config for Minim tests

    def setupConfig(self):
        return self.setupTestBaseConfig(testbase)

    # Actual tests follow

    def testNull(self):
        assert True, 'Null test failed'

    def testEvalQueryTestModelMin(self):
        """
        Evaluate RO against minimal Minim description using just QueryTestRules
        """
        self.setupConfig()
        rodir = self.createTestRo(testbase, "test-data-2", "RO test minim", "ro-testMinim")
        rouri = ro_manifest.getRoUri(rodir)
        self.populateTestRo(testbase, rodir)
        rometa = ro_metadata(ro_config, rodir)
        (g, evalresult) = ro_eval_minim.evaluate(rometa,
            "Minim-UserRequirements2-min.rdf",    # Minim file
            "data/UserRequirements-astro.ods",    # Target resource
            "create")                             # Purpose
        log.debug("ro_eval_minim.evaluate result:\n----\n%s"%(repr(evalresult)))
        self.assertIn(MINIM.fullySatisfies,     evalresult['summary'])
        self.assertIn(MINIM.nominallySatisfies, evalresult['summary'])
        self.assertIn(MINIM.minimallySatisfies, evalresult['summary'])
        self.assertEquals(evalresult['missingMust'],    [])
        self.assertEquals(evalresult['missingShould'],  [])
        self.assertEquals(evalresult['missingMay'],     [])
        self.assertEquals(evalresult['rouri'],          rometa.getRoUri())
        self.assertEquals(evalresult['minimuri'],       rometa.getComponentUri("Minim-UserRequirements2-min.rdf"))
        self.assertEquals(evalresult['target'],         "data/UserRequirements-astro.ods")
        self.assertEquals(evalresult['purpose'],        "create")
        self.assertEquals(evalresult['constrainturi'],
            rometa.getComponentUriAbs("Minim-UserRequirements2-min.rdf#create/data/UserRequirements-astro.ods"))
        self.assertEquals(evalresult['modeluri'],
            rometa.getComponentUriAbs("Minim-UserRequirements2-min.rdf#runnableRO"))
        self.deleteTestRo(rodir)
        return

    def testEvalQueryTestModelExists(self):
        """
        Evaluate RO against minimal Minim description using just QueryTestRules
        """
        self.setupConfig()
        rodir = self.createTestRo(testbase, "test-data-2", "RO test minim", "ro-testMinim")
        rouri = ro_manifest.getRoUri(rodir)
        self.populateTestRo(testbase, rodir)
        rometa = ro_metadata(ro_config, rodir)
        resuri = rometa.getComponentUriAbs("data/UserRequirements-astro.ods")
        rometa.addSimpleAnnotation(resuri, "rdfs:label", "Test label")
        # Now run evaluation against test RO
        (g, evalresult) = ro_eval_minim.evaluate(rometa,
            "Minim-UserRequirements2-exists.rdf", # Minim file
            "data/UserRequirements-astro.ods",    # Target resource
            "create")                             # Purpose
        log.debug("ro_eval_minim.evaluate result:\n----\n%s"%(repr(evalresult)))
        self.assertIn(MINIM.fullySatisfies,     evalresult['summary'])
        self.assertIn(MINIM.nominallySatisfies, evalresult['summary'])
        self.assertIn(MINIM.minimallySatisfies, evalresult['summary'])
        self.assertEquals(evalresult['missingMust'],    [])
        self.assertEquals(evalresult['missingShould'],  [])
        self.assertEquals(evalresult['missingMay'],     [])
        self.assertEquals(evalresult['rouri'],          rometa.getRoUri())
        self.assertEquals(evalresult['minimuri'],       rometa.getComponentUri("Minim-UserRequirements2-exists.rdf"))
        self.assertEquals(evalresult['target'],         "data/UserRequirements-astro.ods")
        self.assertEquals(evalresult['purpose'],        "create")
        self.assertEquals(evalresult['constrainturi'],
            rometa.getComponentUriAbs("Minim-UserRequirements2-exists.rdf#create/data/UserRequirements-astro.ods"))
        self.assertEquals(evalresult['modeluri'],
            rometa.getComponentUriAbs("Minim-UserRequirements2-exists.rdf#runnableRO"))
        self.deleteTestRo(rodir)
        return

    def testEvalQueryTestModel(self):
        """
        Evaluate RO against Minim description using just QueryTestRules
        """
        self.setupConfig()
        rodir = self.createTestRo(testbase, "test-data-2", "RO test minim", "ro-testMinim")
        rouri = ro_manifest.getRoUri(rodir)
        self.populateTestRo(testbase, rodir)
        rometa = ro_metadata(ro_config, rodir)
        resuri = rometa.getComponentUriAbs("data/UserRequirements-astro.ods")
        rometa.addSimpleAnnotation(resuri, "rdfs:label", "Test label")
        # Now run evaluation against test RO
        (g, evalresult) = ro_eval_minim.evaluate(rometa,
            "Minim-UserRequirements2.rdf",        # Minim file
            "data/UserRequirements-astro.ods",    # Target resource
            "create")                             # Purpose
        log.debug("ro_eval_minim.evaluate result:\n----\n%s"%(repr(evalresult)))
        self.assertIn(MINIM.fullySatisfies,     evalresult['summary'])
        self.assertIn(MINIM.nominallySatisfies, evalresult['summary'])
        self.assertIn(MINIM.minimallySatisfies, evalresult['summary'])
        self.assertEquals(evalresult['missingMust'],    [])
        self.assertEquals(evalresult['missingShould'],  [])
        self.assertEquals(evalresult['missingMay'],     [])
        self.assertEquals(evalresult['rouri'],          rometa.getRoUri())
        self.assertEquals(evalresult['minimuri'],       rometa.getComponentUri("Minim-UserRequirements2.rdf"))
        self.assertEquals(evalresult['target'],         "data/UserRequirements-astro.ods")
        self.assertEquals(evalresult['purpose'],        "create")
        self.assertEquals(evalresult['constrainturi'],
            rometa.getComponentUriAbs("Minim-UserRequirements2.rdf#create/data/UserRequirements-astro.ods"))
        self.assertEquals(evalresult['modeluri'],
            rometa.getComponentUriAbs("Minim-UserRequirements2.rdf#runnableRO"))
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
            , "testEvalQueryTestModelMin"
            , "testEvalQueryTestModelExists"
            , "testEvalQueryTestModel"
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
    return TestUtils.getTestSuite(TestEvalQueryMatch, testdict, select=select)

if __name__ == "__main__":
    TestUtils.runTests("TestEvalQueryMatch.log", getTestSuite, sys.argv)

# End.
