#!/usr/bin/python

"""
Module to test RO metadata handling class
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

from rocommand import ro_settings
from rocommand import ro_metadata
from rocommand import ro_annotation
from rocommand.ro_namespaces import RDF, RDFS, ORE, RO, ROEVO, AO, DCTERMS

from ROSRS_Session import ROSRS_Error, ROSRS_Session

from TestConfig import ro_test_config
from StdoutContext import SwitchStdout

import TestROSupport

# Base directory for RO tests in this module
#testbase = os.path.dirname(os.path.realpath(__file__))

# Local ro_config for testing
ro_config = {
    "annotationTypes":      ro_annotation.annotationTypes,
    "annotationPrefixes":   ro_annotation.annotationPrefixes,
    "rosrs_uri":            ro_test_config.ROSRS_URI,           # "http://sandbox.wf4ever-project.org/rodl/ROs/"
    "rosrs_access_token":   ro_test_config.ROSRS_ACCESS_TOKEN,  # "47d5423c-b507-4e1c-8", 
    }

class Config:
    #ROSRS_API_URI = "http://localhost:8082/ROs/"
    ROSRS_API_URI = ro_test_config.ROSRS_URI            # "http://sandbox.wf4ever-project.org/rodl/ROs/"
    AUTHORIZATION = ro_test_config.ROSRS_ACCESS_TOKEN   # "47d5423c-b507-4e1c-8"
    TEST_RO_NAME  = "TestROSRSMetadataRO"
    TEST_RO_PATH  = TEST_RO_NAME+"/"
    TEST_RO_URI   = ROSRS_API_URI+TEST_RO_PATH
    TEST_RESOURCE = "test/file.txt"
    TEST_EXTERNAL = "http://example.com/external/resource.txt"

cwd        = os.getcwd()
robase     = ro_test_config.ROBASEDIR
robase_abs = os.path.abspath(ro_test_config.ROBASEDIR)

class TestROSRSMetadata(TestROSupport.TestROSupport):
    """
    Test ro metadata access via ROSRS API
    """

    def setUp(self):
        super(TestROSRSMetadata, self).setUp()
        self.rosrs = ROSRS_Session(Config.ROSRS_API_URI,
            accesskey=Config.AUTHORIZATION)
        # Clean up from previous runs
        self.rosrs.deleteRO(Config.TEST_RO_PATH)
        return

    def tearDown(self):
        super(TestROSRSMetadata, self).tearDown()
        # Clean up
        self.rosrs.deleteRO(Config.TEST_RO_PATH)
        self.rosrs.close()
        return

    def createTestRO(self):
        (status, reason, rouri, manifest) = self.rosrs.createRO(Config.TEST_RO_NAME,
            "Test RO for ROSRSMetadata", "TestROSRSMetadata.py", "2012-09-11")
        self.assertEqual(status, 201)
        # Include manifest as annotation of RO
        (s1, r1, h1, manifesturi, manifest) = self.rosrs.getROManifest(rouri)
        self.assertEqual(s1, 200)
        (s2, r2, annuri) = self.rosrs.createROAnnotationExt(
            rouri, rouri, manifesturi)
        self.assertEqual(s2, 201)
        # Aggregate internal resource
        rescontent = "Resource content\n"
        (s3, r3, proxyuri, resuri) = self.rosrs.aggregateResourceInt(
            rouri, Config.TEST_RESOURCE, ctype="text/plain", body=rescontent)
        self.assertEqual(s3, 201)
        self.assertEqual(r3, "Created")
        self.assertEqual(str(resuri), str(rouri)+Config.TEST_RESOURCE)
        # Aggregate external resource
        externaluri = rdflib.URIRef(Config.TEST_EXTERNAL)
        (s4, r4, proxyuri, resuri) = self.rosrs.aggregateResourceExt(
            rouri, externaluri)
        self.assertEqual(s4, 201)
        self.assertEqual(r4, "Created")
        self.assertEqual(str(resuri), Config.TEST_EXTERNAL)
        return (status, reason, rouri, manifest)

    def createTestAnnotation(self, rouri, resuri, resref):
        annbody = """<?xml version="1.0" encoding="UTF-8"?>
            <rdf:RDF
               xmlns:dct="http://purl.org/dc/terms/"
               xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
               xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
               xml:base="%(rouri)s"
            >
              <rdf:Description rdf:about="%(resuri)s">
                <dct:title>Title for %(resref)s</dct:title>
                <rdfs:seeAlso rdf:resource="http://example.org/test" />
              </rdf:Description>
            </rdf:RDF>
            """%{"rouri": str(rouri), "resuri": str(resuri), "resref": resref}
        agraph = rdflib.graph.Graph()
        agraph.parse(data=annbody, format="xml")
        (status, reason, annuri, bodyuri) = self.rosrs.createROAnnotationInt(
            rouri, resuri, agraph)
        self.assertEqual(status, 201)
        return (status, reason, annuri, bodyuri)

    # Actual tests follow

    def testNull(self):
        assert True, 'Null test failed'

    def testCreateRoMetadata(self):
        """
        Test creation of ro_metadata object, and basic access to manifest content
        """
        (status, reason, rouri, manifest) = self.createTestRO()
        self.assertEqual(status, 201)
        self.assertEqual(reason, "Created")
        self.assertEqual(str(rouri), Config.TEST_RO_URI)
        self.assertIn((rouri, RDF.type, RO.ResearchObject), manifest)
        romd   = ro_metadata.ro_metadata(ro_config, rouri)
        resuri = romd.getComponentUriAbs(Config.TEST_RESOURCE)
        exturi = romd.getComponentUriAbs(Config.TEST_EXTERNAL)
        resref = Config.TEST_RESOURCE
        (status, reason, annuri, bodyuri) = self.createTestAnnotation(rouri, resuri, resref)
        self.assertEqual(status, 201)
        self.assertEqual(reason, "Created")
        #
        self.assertEquals(romd.rouri, rouri)
        self.assertTrue(romd.roManifestContains((rouri, RDF.type, RO.ResearchObject)))
        self.assertTrue(romd.roManifestContains((rouri, ORE.aggregates, resuri)))
        self.assertTrue(romd.roManifestContains((rouri, ORE.aggregates, exturi)))
        return

    def testReadRoAnnotationBody(self):
        """
        Test function to create & read a simple annotation body on an RO
        """
        (status, reason, rouri, manifest) = self.createTestRO()
        self.assertEqual(status, 201)
        romd   = ro_metadata.ro_metadata(ro_config, rouri)
        resuri = romd.getComponentUriAbs(Config.TEST_RESOURCE)
        resref = Config.TEST_RESOURCE
        (status, reason, bodyuri, agraph) = self.createTestAnnotation(rouri, resuri, resref)
        self.assertEqual(status, 201)
        # Retrieve annotations
        anns = list(romd.getFileAnnotations(Config.TEST_RESOURCE))
        self.assertIn((resuri, DCTERMS.title, rdflib.Literal("Title for "+Config.TEST_RESOURCE)), anns)
        self.assertIn((resuri, RDFS.seeAlso,  rdflib.URIRef("http://example.org/test")),  anns)
        return

    def testGetInitialRoAnnotations(self):
        (status, reason, rouri, manifest) = self.createTestRO()
        self.assertEqual(status, 201)
        romd   = ro_metadata.ro_metadata(ro_config, rouri)
        # Retrieve the anotations
        annotations = romd.getRoAnnotations()
        rouri = romd.getRoUri()
        expected_annotations = (
            [ (rouri, RDF.type,             RO.ResearchObject)
            , (rouri, RDF.type,             ROEVO.LiveRO)
            , (rouri, ORE.isDescribedBy,    romd.getComponentUriAbs(ro_test_config.ROMANIFESTPATH))
            #, (rouri, DCTERMS.description,  rdflib.Literal('Test init RO annotation'))
            #, (rouri, DCTERMS.title,        rdflib.Literal('Test init RO annotation'))
            #, (rouri, DCTERMS.created,      rdflib.Literal('unknown'))
            #, (rouri, DCTERMS.creator,      rdflib.Literal('Test User'))
            #, (rouri, DCTERMS.identifier,   rdflib.Literal('ro-testRoAnnotate'))
            ])
        count = 0
        for next in list(annotations):
            if ( not isinstance(next[2], rdflib.BNode) and
                 not next[1] in [ORE.aggregates, DCTERMS.created, DCTERMS.creator] ):
                log.debug("- next %s"%(str(next[0])) )
                log.debug("       - (%s, %s)"%(str(next[1]),str(next[2])) )
                if next in expected_annotations:
                    count += 1
                else:
                    self.assertTrue(False, "Not expected (%d) %s"%(count, repr(next)))
        self.assertEqual(count,3)
        return

    def testQueryAnnotations(self):
        (status, reason, rouri, manifest) = self.createTestRO()
        self.assertEqual(status, 201)
        romd   = ro_metadata.ro_metadata(ro_config, rouri)
        resuri = romd.getComponentUriAbs(Config.TEST_RESOURCE)
        resref = Config.TEST_RESOURCE
        (status, reason, bodyuri, agraph) = self.createTestAnnotation(rouri, resuri, resref)
        self.assertEqual(status, 201)
        # Query the file anotations
        queryprefixes = """
            PREFIX rdf:        <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX ro:         <http://purl.org/wf4ever/ro#>
            PREFIX ore:        <http://www.openarchives.org/ore/terms/>
            PREFIX ao:         <http://purl.org/ao/>
            PREFIX dcterms:    <http://purl.org/dc/terms/>
            PREFIX roterms:    <http://ro.example.org/ro/terms/>
            """
        query = (queryprefixes +
            """
            ASK
            {
                ?ro rdf:type ro:ResearchObject ;
                    dcterms:creator ?user .
            }
            """)
        resp = romd.queryAnnotations(query)
        self.assertTrue(resp, "Expected 'True' result for query: %s"%(query))
        query = (queryprefixes +
            """
            ASK
            {
                <%(resuri)s> dcterms:title ?title .
            }
            """%{"resuri": str(resuri)})
        resp = romd.queryAnnotations(query)
        self.assertTrue(resp, "Expected 'True' result for query: %s"%(query))
        query = (queryprefixes +
            """
            ASK
            {
                ?ro rdf:type ro:ResearchObject ;
                    dcterms:creator "Not user" .
            }
            """)
        resp = romd.queryAnnotations(query)
        self.assertFalse(resp, "Expected 'False' result for query: %s"%(query))
        query = (queryprefixes +
            """
            SELECT * WHERE
            {
                ?ro rdf:type ro:ResearchObject ;
                    ore:aggregates ?file .
                ?file dcterms:title ?title .
            }
            """)
        rouri       = romd.getRoUri()
        resp = romd.queryAnnotations(query)
        self.assertEqual(resp[0]['ro'],    rouri)
        self.assertEqual(resp[0]['file'],  resuri)
        self.assertEqual(resp[0]['title'], rdflib.Literal("Title for %s"%(Config.TEST_RESOURCE)))
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
            , "testCreateRoMetadata"
            , "testReadRoAnnotationBody"
            , "testGetInitialRoAnnotations"
            , "testQueryAnnotations"
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
    return TestUtils.getTestSuite(TestROSRSMetadata, testdict, select=select)

if __name__ == "__main__":
    TestUtils.runTests("TestROSRSMetadata.log", getTestSuite, sys.argv)

# End.
