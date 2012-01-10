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

# Base directory for RO tests in this module
testbase = os.path.dirname(__name__)

class TestMinimAccess(TestROSupport.TestROSupport):
    """
    Test ro annotation commands
    """
    def setUp(self):
        super(TestMinimAccess, self).setUp()
        return

    def tearDown(self):
        super(TestMinimAccess, self).tearDown()
        return

    # Setup local config for Minim tests
    def setupConfig(self):
        basedir   = os.path.dirname(__name__)
        configdir = os.path.join(basedir, TestConfig.ro_test_config.CONFIGDIR)
        robasedir = os.path.join(basedir, TestConfig.ro_test_config.ROBASEDIR)
        ro_utils.resetconfig(configdir)
        args = [
            "ro", "config",
            "-b", robasedir,
            "-r", TestConfig.ro_test_config.ROSRS_URI,
            "-u", TestConfig.ro_test_config.ROSRS_USERNAME,
            "-p", TestConfig.ro_test_config.ROSRS_PASSWORD,
            "-n", TestConfig.ro_test_config.ROBOXUSERNAME,
            "-e", TestConfig.ro_test_config.ROBOXEMAIL
            ]
        with StdoutContext.SwitchStdout(self.outstr):
            status = ro.runCommand(configdir, robasedir, args)
            assert status == 0
        self.assertEqual(self.outstr.getvalue().count("ro config"), 0)
        return (configdir, robasedir)

    # Actual tests follow

    def testNull(self):
        assert True, 'Null test failed'

    def TestSetupConfig(self):
        (configdir, robasedir) = self.setupConfig()
        config = ro_utils.readconfig(configdir)
        self.assertEqual(config["robase"],          os.path.abspath(robasedir))
        self.assertEqual(config["rosrs_uri"],       TestConfig.ro_test_config.ROSRS_URI)
        self.assertEqual(config["rosrs_username"],  TestConfig.ro_test_config.ROSRS_USERNAME)
        self.assertEqual(config["rosrs_password"],  TestConfig.ro_test_config.ROSRS_PASSWORD)
        self.assertEqual(config["username"],        TestConfig.ro_test_config.ROBOXUSERNAME)
        self.assertEqual(config["useremail"],       TestConfig.ro_test_config.ROBOXEMAIL)
        return

    def TestMinimRead(self):
        """
        Basic test that Minim test file can be read
        """
        (configdir, robasedir) = self.setupConfig()
        rodir      = self.createTestRo(testbase, "data", "RO test minim", "ro-testMinim")
        rouri      = ro_manifest.getRoUri(rodir)
        minimbase  = ro_manifest.getComponentUri(rodir, "Minim-UserRequirements-gen.json.rdf")
        target     = ro_manifest.getComponentUri(rodir, "docs/UserRequirements-gen.csv")
        constraint = ro_minim.getElementUri(minimbase, "#create/docs/UserRequirements-gen.csv")
        model      = ro_minim.getElementUri(minimbase, "#runnableRequirementRO")
        g = ro_minim.readMinimGraph(minimbase)
        for stmt in g:
            log.debug("-- %s"%(repr(stmt)))
        expected_minim = (
            [ (target,     MINIM.hasConstraint, constraint                                          )
            , (constraint, MINIM.forPurpose,    rdflib.Literal('create UserRequirements-gen.csv')   )
            , (constraint, MINIM.onResource,    rouri                                               )
            , (constraint, MINIM.toModel,       model                                               )
            , (model,      RDF.type,            MINIM.Model                                         )
            ])
        self.checkTargetGraph(g, expected_minim, msg="Not found in Minim")
        self.deleteTestRo(rodir)
        return



    def ZZZtestAddAggregatedResources(self):
        """
        Test function that adds aggregated resources to a research object manifest
        """
        rodir = self.createTestRo(testbase, "data/ro-test-1", "RO test annotation", "ro-testRoAnnotate")
        ro_manifest.addAggregatedResources(rodir, rodir, recurse=True)
        def URIRef(path):
            return ro_manifest.getComponentUri(rodir, path)
        s = ro_manifest.getComponentUri(rodir, "")
        g = rdflib.Graph()
        g.add( (s, RDF.type,            RO.ResearchObject                  ) )
        g.add( (s, ORE.aggregates,      URIRef("README-ro-test-1")         ) )
        g.add( (s, ORE.aggregates,      URIRef("subdir1/subdir1-file.txt") ) )
        g.add( (s, ORE.aggregates,      URIRef("subdir2/subdir2-file.txt") ) )
        self.checkManifestGraph(rodir, g)
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
            , "TestSetupConfig"
            , "TestMinimRead"
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
    return TestUtils.getTestSuite(TestMinimAccess, testdict, select=select)

if __name__ == "__main__":
    TestUtils.runTests("TestMinimAccess.log", getTestSuite, sys.argv)

# End.
