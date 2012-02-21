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
    # Add main project directory and ro manager directories at start of python path
    sys.path.insert(0, "../..")
    sys.path.insert(0, "..")

import rdflib

from MiscLib import TestUtils

from rocommand import ro
from rocommand import ro_utils
from rocommand import ro_manifest
from rocommand import ro_annotation
from rocommand.ro_namespaces import RDF, DCTERMS, RO, AO, ORE

from TestConfig import ro_test_config
from StdoutContext import SwitchStdout

import TestROSupport

# Base directory for RO tests in this module
testbase = os.path.dirname(__file__)

# Local ro_config for testing
#ro_config = {
#    "annotationTypes": ro_annotation.annotationTypes
#    }

class TestManifest(TestROSupport.TestROSupport):
    """
    Test ro annotation commands
    """
    def setUp(self):
        super(TestManifest, self).setUp()
        return

    def tearDown(self):
        super(TestManifest, self).tearDown()
        return

    # Actual tests follow

    def testNull(self):
        assert True, 'Null test failed'

    def testManifestContent(self):
        """
        Test content of newly created manifest
        """
        rodir = self.createTestRo(testbase, "data/ro-test-1", "RO test annotation", "ro-testRoAnnotate")
        ro_graph = ro_manifest.readManifestGraph(rodir)
        self.checkManifestGraph(rodir, ro_graph)
        s = ro_manifest.getComponentUri(rodir, "")
        g = rdflib.Graph()
        g.add( (s, RDF.type,            RO.ResearchObject                            ) )
        g.add( (s, DCTERMS.creator,     rdflib.Literal(ro_test_config.ROBOXUSERNAME) ) )
        g.add( (s, DCTERMS.description, rdflib.Literal("RO test annotation")         ) )
        g.add( (s, DCTERMS.title,       rdflib.Literal("RO test annotation")         ) )
        g.add( (s, DCTERMS.identifier,  rdflib.Literal("ro-testRoAnnotate")          ) )
        self.checkManifestGraph(rodir, g)
        self.deleteTestRo(rodir)
        return

    def testAddAggregatedResources(self):
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

    def testAddAggregatedResourcesCommand(self):
        """
        Test function that adds aggregated resources to a research object manifest
        """
        rodir = self.createTestRo(testbase, "data/ro-test-1", "RO test annotation", "ro-testRoAnnotate")
        args = [
            "ro", "add", "-v", "-a",
            "-d", rodir,
            rodir
            ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
        outtxt = self.outstr.getvalue()
        assert status == 0, outtxt
        log.debug("outtxt %s"%outtxt)
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
            , "testManifestContent"
            , "testAddAggregatedResources"
            , "testAddAggregatedResourcesCommand"
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
    return TestUtils.getTestSuite(TestManifest, testdict, select=select)

if __name__ == "__main__":
    TestUtils.runTests("TestManifest.log", getTestSuite, sys.argv)

# End.
