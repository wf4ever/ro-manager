#!/usr/bin/python

"""
Module to test remote RO metadata handling class
"""

import os.path
import sys
import logging
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
import uuid

from MiscLib import TestUtils

from rocommand import ro_remote_metadata
from rocommand.ROSRS_Session import ROSRS_Session
from rocommand.ro_namespaces import RO
from rocommand.ro_annotation import annotationTypes

from TestConfig import ro_test_config

from zipfile import ZipFile

import TestROSupport

# Base directory for RO tests in this module
testbase = os.path.dirname(__file__)

# Local ro_config for testing
ro_config = {
    "annotationTypes": annotationTypes
    }

cwd        = os.getcwd()
robase     = ro_test_config.ROBASEDIR
robase_abs = os.path.abspath(ro_test_config.ROBASEDIR)

class TestRemoteROMetadata(TestROSupport.TestROSupport):
    """
    Test ro metadata handling
    """
    def setUp(self):
        super(TestRemoteROMetadata, self).setUp()
        self.remoteRo = None
        return

    def tearDown(self):
        super(TestRemoteROMetadata, self).tearDown()
        if self.remoteRo:
            self.remoteRo.delete()
        return

    # Actual tests follow

    def testNull(self):
        assert True, 'Null test failed'
        
    def testCreateRo(self):
        httpsession = ROSRS_Session(ro_test_config.ROSRS_URI, ro_test_config.ROSRS_ACCESS_TOKEN)
        roid = "romanagertest-" + str(uuid.uuid4())  
        (status, reason, rouri, _) = ro_remote_metadata.createRO(httpsession, roid)
        if status == 409:
            log.debug("TestRemoteROMetadata: RO already exists %03d %s"%(status, reason)) 
        self.remoteRo = ro_remote_metadata.ro_remote_metadata(ro_config, httpsession, rouri)
        return

    def testAddGetAggregatedResources(self):
        """
        Test function that adds aggregated resources to a research object manifest
        """
        httpsession = ROSRS_Session(ro_test_config.ROSRS_URI, ro_test_config.ROSRS_ACCESS_TOKEN)
        roid = "romanagertest-" + str(uuid.uuid4())      
        (_, _, rouri, _) = ro_remote_metadata.createRO(httpsession, roid)
        self.remoteRo = ro_remote_metadata.ro_remote_metadata(ro_config, httpsession, rouri)
        def URIRef(path):
            return self.remoteRo.getComponentUriAbs(path)
        def verifyResources(resources):
            c = 0
            for r in self.remoteRo.getAggregatedResources():
                if self.remoteRo.getResourceType(r) != RO.AggregatedAnnotation:
                    c += 1
                    self.assertIn(r, resources)
            self.assertEqual(c, len(resources))
            return
        self.remoteRo.aggregateResourceInt("internal/1", "text/plain", "ipsum lorem")
        self.assertTrue(self.remoteRo.isAggregatedResource("internal/1"))
        self.assertFalse(self.remoteRo.isAggregatedResource("http://www.google.com"))
        verifyResources([
                         URIRef("internal/1")
          ])
        self.remoteRo.aggregateResourceExt("http://www.google.com")
        self.assertTrue(self.remoteRo.isAggregatedResource("internal/1"))
        self.assertTrue(self.remoteRo.isAggregatedResource("http://www.google.com"))
        verifyResources([
                         URIRef("internal/1")
                         , URIRef("http://www.google.com")
          ])
        self.remoteRo.deaggregateResource(URIRef("internal/1"))
        self.assertFalse(self.remoteRo.isAggregatedResource("internal/1"))
        self.assertTrue(self.remoteRo.isAggregatedResource("http://www.google.com"))
        verifyResources([
                         URIRef("http://www.google.com")
          ])
        self.remoteRo.deaggregateResource(URIRef("http://www.google.com"))
        self.assertFalse(self.remoteRo.isAggregatedResource("internal/1"))
        self.assertFalse(self.remoteRo.isAggregatedResource("http://www.google.com"))
        verifyResources([])
        return

    def testClassifyAggregatedResources(self):
        """
        Test functions that identify external and internal resource
        """
        httpsession = ROSRS_Session(ro_test_config.ROSRS_URI, ro_test_config.ROSRS_ACCESS_TOKEN)
        roid = "romanagertest-" + str(uuid.uuid4())      
        (_, _, rouri, _) = ro_remote_metadata.createRO(httpsession, roid)
        self.remoteRo = ro_remote_metadata.ro_remote_metadata(ro_config, httpsession, rouri)
        def URIRef(path):
            return self.remoteRo.getComponentUriAbs(path)
        self.remoteRo.aggregateResourceInt("internal/1", "text/plain", "ipsum lorem")
        self.remoteRo.aggregateResourceExt("http://www.google.com")
        self.assertTrue(self.remoteRo.isResourceInternal(URIRef("internal/1")))
        self.assertFalse(self.remoteRo.isResourceExternal(URIRef("internal/1")))
        self.assertFalse(self.remoteRo.isResourceInternal(URIRef("http://www.google.com")))
        self.assertTrue(self.remoteRo.isResourceExternal(URIRef("http://www.google.com")))
        return

    def testGetAsZip(self):
        httpsession = ROSRS_Session(ro_test_config.ROSRS_URI, ro_test_config.ROSRS_ACCESS_TOKEN)
        roid = "romanagertest-" + str(uuid.uuid4())      
        (_, _, rouri, _) = ro_remote_metadata.createRO(httpsession, roid)
        self.remoteRo = ro_remote_metadata.ro_remote_metadata(ro_config, httpsession, rouri)
        self.remoteRo.aggregateResourceInt("internal/1", "text/plain", "ipsum lorem")
        zipdata = ro_remote_metadata.getAsZip(rouri)
        zipfile = ZipFile(zipdata)
        self.assertEquals(len(zipfile.read("internal/1")), len("ipsum lorem"), "File size must be the same")
        self.assertTrue(len(zipfile.read(".ro/manifest.rdf")) > 0, "Size of manifest.rdf must be greater than 0")
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
            , "testCreateRo"
            , "testAddGetAggregatedResources"
            , "testClassifyAggregatedResources"
            , "testGetAsZip"
            ],
        "component":
            [ "testComponents"
            ],
        "integration":
            [ "testIntegration"
            ],
        "pending":
            [ "testPending"
            , "testQueryAnnotationsRemote"
            ]
        }
    return TestUtils.getTestSuite(TestRemoteROMetadata, testdict, select=select)

if __name__ == "__main__":
    TestUtils.runTests("TestROMetadata.log", getTestSuite, sys.argv)

# End.
