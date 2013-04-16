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

from rocommand import ro_utils
from rocommand import ro_manifest
from rocommand.ro_namespaces import RDF, DCTERMS, RO, AO, ORE

from rocommand.test import TestROSupport
from rocommand.test import TestConfig

from iaeval import ro_minim
from iaeval.ro_minim import MINIM

# Base directory for RO tests in this module
testbase = os.path.dirname(os.path.realpath(__file__))

# Test suite
class TestMinimAccess2(TestROSupport.TestROSupport):
    """
    Test ro annotation commands
    """
    def setUp(self):
        super(TestMinimAccess2, self).setUp()
        return

    def tearDown(self):
        super(TestMinimAccess2, self).tearDown()
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
        self.assertEqual(config["rosrs_access_token"],  TestConfig.ro_test_config.ROSRS_ACCESS_TOKEN)
        self.assertEqual(config["username"],        TestConfig.ro_test_config.ROBOXUSERNAME)
        self.assertEqual(config["useremail"],       TestConfig.ro_test_config.ROBOXEMAIL)
        return

    def testMinimRead(self):
        """
        Basic test that Minim test file can be read
        """
        self.setupConfig()
        rodir      = self.createTestRo(testbase, "test-data-2", "RO test minim", "ro-testMinim")
        rouri      = ro_manifest.getRoUri(rodir)
        minimbase  = ro_manifest.getComponentUri(rodir, "Minim-UserRequirements2.rdf")
        target     = ro_manifest.getComponentUri(rodir, "data/UserRequirements-astro.ods")
        constraint = ro_minim.getElementUri(minimbase, "#create/data/UserRequirements-astro.ods")
        model      = ro_minim.getElementUri(minimbase, "#runnableRO")
        g = ro_minim.readMinimGraph(minimbase)
        expected_minim = (
            [ (target,     MINIM.hasChecklist,  constraint                                          )
            , (constraint, MINIM.forPurpose,    rdflib.Literal('create UserRequirements-astro.ods') )
            , (constraint, MINIM.toModel,       model                                               )
            , (model,      RDF.type,            MINIM.Model                                         )
            ])
        self.checkTargetGraph(g, expected_minim, msg="Not found in Minim")
        self.deleteTestRo(rodir)
        return

    def testGetConstraints(self):
        self.setupConfig()
        rodir      = self.createTestRo(testbase, "test-data-2", "RO test minim", "ro-testMinim")
        rouri      = ro_manifest.getRoUri(rodir)
        minimbase  = ro_manifest.getComponentUri(rodir, "Minim-UserRequirements2.rdf")
        model      = ro_minim.getElementUri(minimbase, "#runnableRO")
        constraint = ro_minim.getElementUri(minimbase, "#create/data/UserRequirements-astro.ods")
        # Read Minim as graph, scan constraints and look for expected value
        minimgraph = ro_minim.readMinimGraph(minimbase)
        constraints = ro_minim.getConstraints(minimgraph)
        expected_found = False
        for c in constraints:
            if ( c['target']   == ro_manifest.getComponentUri(rodir, "data/UserRequirements-astro.ods") and
                 c['purpose']  == rdflib.Literal("create UserRequirements-astro.ods")                   and
                 c['model']    == model                                                                 and
                 c['uri']      == constraint ) :
                expected_found = True
                break
        self.assertTrue(expected_found, "Expected constraint not found in minim")
        return

    def testGetConstraint(self):
        self.setupConfig()
        rodir      = self.createTestRo(testbase, "test-data-2", "RO test minim", "ro-testMinim")
        rouri      = ro_manifest.getRoUri(rodir)
        minimbase  = ro_manifest.getComponentUri(rodir, "Minim-UserRequirements2.rdf")
        model      = ro_minim.getElementUri(minimbase, "#runnableRO")
        constraint = ro_minim.getElementUri(minimbase, "#create/data/UserRequirements-astro.ods")
        minimgraph = ro_minim.readMinimGraph(minimbase)
        c = ro_minim.getConstraint(minimgraph, rodir,
            "data/UserRequirements-astro.ods",
            r"create.*UserRequirements-astro\.ods")
        self.assertIsNotNone(c, "Constraint not found")
        self.assertEquals(c['target'],   ro_manifest.getComponentUri(rodir, "data/UserRequirements-astro.ods"))
        self.assertEquals(c['purpose'],  rdflib.Literal("create UserRequirements-astro.ods"))
        self.assertEquals(c['model'],    model)
        self.assertEquals(c['uri'],      constraint)
        return

    def testGetModels(self):
        self.setupConfig()
        rodir      = self.createTestRo(testbase, "test-data-2", "RO test minim", "ro-testMinim")
        rouri      = ro_manifest.getRoUri(rodir)
        minimbase  = ro_manifest.getComponentUri(rodir, "Minim-UserRequirements2.rdf")
        model      = ro_minim.getElementUri(minimbase, "#runnableRO")
        minimgraph = ro_minim.readMinimGraph(minimbase)
        models     = ro_minim.getModels(minimgraph)
        expected_found = False
        for m in models:
            if ( m['label']  == rdflib.Literal("Runnable RO") and
                 m['uri']    == model ) :
                expected_found = True
                break
        self.assertTrue(expected_found, "Expected model not found in minim")
        return
    
    def testGetModel(self):
        self.setupConfig()
        rodir      = self.createTestRo(testbase, "test-data-2", "RO test minim", "ro-testMinim")
        rouri      = ro_manifest.getRoUri(rodir)
        minimbase  = ro_manifest.getComponentUri(rodir, "Minim-UserRequirements2.rdf")
        model      = ro_minim.getElementUri(minimbase, "#runnableRO")
        minimgraph = ro_minim.readMinimGraph(minimbase)
        m = ro_minim.getModel(minimgraph, model)
        self.assertEquals(m['label'], rdflib.Literal("Runnable RO"))
        self.assertEquals(m['uri'],   model)
        return

    def testGetRequirements(self):
        def compare_reqs(req_expect, req_found):
            for k in req_expect:
                if not k in req_found:
                    log.debug("- not found: %s"%(k))
                    return False
                elif isinstance(req_expect[k], dict) and isinstance(req_found[k], dict):
                    if not compare_reqs(req_expect[k], req_found[k]): return False
                elif req_found[k] != req_expect[k]:
                    log.debug("- not found: %s: %s != %s "%(k,req_expect[k],req_found[k]))
                    return False
            return True
        self.setupConfig()
        rodir        = self.createTestRo(testbase, "test-data-2", "RO test minim", "ro-testMinim")
        rouri        = ro_manifest.getRoUri(rodir)
        minimbase    = ro_manifest.getComponentUri(rodir, "Minim-UserRequirements2.rdf")
        model        = ro_minim.getElementUri(minimbase, "#runnableRO")
        minimgraph   = ro_minim.readMinimGraph(minimbase)
        requirements = ro_minim.getRequirements(minimgraph, model)
        expected_found = False
        r1 = (
            { 'level': "MUST"
            , 'label': rdflib.Literal("aggregates data/UserRequirements-astro.ods")
            , 'querytestrule':
              { 'query':        rdflib.Literal("?ro a ro:ResearchObject")
              , 'resultmod':    None
              , 'aggregates_t': rdflib.Literal("data/UserRequirements-astro.ods")
              }
            , 'uri': ro_minim.getElementUri(minimbase, "#isAggregated/data/UserRequirements-astro.ods") 
            })
        r2 = (
            { 'level': "MUST"
            , 'label': rdflib.Literal("accessible data/UserRequirements-astro.ods")
            , 'querytestrule':
              { 'query':        rdflib.Literal("?ro a ro:ResearchObject")
              , 'resultmod':    None
              , 'islive_t':     rdflib.Literal("data/UserRequirements-astro.ods")
              }
            , 'uri': ro_minim.getElementUri(minimbase, "#isAccessible/data/UserRequirements-astro.ods") 
            })
        r3 = (
            { 'level': "MUST"
            , 'label': rdflib.Literal("labeled data/UserRequirements-astro.ods")
            , 'querytestrule':
              { 'query':        rdflib.Literal("?ro a ro:ResearchObject")
              , 'resultmod':    rdflib.Literal("ORDER BY ?ro")
              , 'exists':       rdflib.Literal("<data/UserRequirements-astro.ods> rdfs:label ?label")
              }
            , 'uri': ro_minim.getElementUri(minimbase, "#isLabeled/data/UserRequirements-astro.ods") 
            })
        r1_found = r2_found = r3_found = False
        for r in requirements:
            log.debug("requirement: %s"%(repr(r)))
            if compare_reqs(r1, r): r1_found = True
            if compare_reqs(r2, r): r2_found = True
            if compare_reqs(r3, r): r3_found = True
        self.assertTrue(r1_found, "Expected requirement(1) not found in minim")
        self.assertTrue(r2_found, "Expected requirement(2) not found in minim")
        self.assertTrue(r3_found, "Expected requirement(3) not found in minim")
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
            , "testMinimRead"
            , "testGetConstraints"
            , "testGetConstraint"
            , "testGetModels"
            , "testGetModel"
            , "testGetRequirements"
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
    return TestUtils.getTestSuite(TestMinimAccess2, testdict, select=select)

if __name__ == "__main__":
    TestUtils.runTests("TestMinimAccess2.log", getTestSuite, sys.argv)

# End.
