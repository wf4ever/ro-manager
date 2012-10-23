#!/usr/bin/env python

"""
Module to test RO SRS APIfunctions
"""

import os, os.path
import sys
import unittest
import logging
import json
import re
import StringIO
import httplib
import urlparse
import rdflib, rdflib.graph

if __name__ == "__main__":
    # Add main project directory and ro manager directories at start of python path
    sys.path.insert(0, "../..")
    sys.path.insert(0, "..")

from MiscLib import TestUtils

from ro_namespaces import RDF, RDFS, ORE, RO, DCTERMS, AO
from ROSRS_Session import ROSRS_Error, ROSRS_Session, testSplitValues, testParseLinks
from TestConfig import ro_test_config

# Logging object
log = logging.getLogger(__name__)

# Base directory for file access tests in this module
testbase = os.path.dirname(__file__)

# Test config details

class Config:
    #ROSRS_API_URI = "http://localhost:8082/ROs/"
    ROSRS_API_URI = ro_test_config.ROSRS_URI            # "http://sandbox.wf4ever-project.org/rodl/ROs/"
    #AUTHORIZATION = "0522a6c6-7000-43df-8"
    AUTHORIZATION = ro_test_config.ROSRS_ACCESS_TOKEN   
    TEST_RO_NAME  = "TestSessionRO"
    TEST_RO_PATH  = TEST_RO_NAME+"/"
    TEST_RO_URI   = ROSRS_API_URI+TEST_RO_PATH

# Test cases

class TestROSRS_Session(unittest.TestCase):
    """
    This test suite tests the ROSRS_Session client implementation of the ROSRS API
    """

    def setUp(self):
        super(TestROSRS_Session, self).setUp()
        self.rosrs = ROSRS_Session(Config.ROSRS_API_URI,
            accesskey=Config.AUTHORIZATION)
        # Clean up from previous runs
        self.rosrs.deleteRO(Config.TEST_RO_PATH)
        return

    def tearDown(self):
        super(TestROSRS_Session, self).tearDown()
        # Clean up
        self.rosrs.deleteRO(Config.TEST_RO_PATH)
        self.rosrs.close()
        return

    def createTestRO(self):
        (status, reason, rouri, manifest) = self.rosrs.createRO(Config.TEST_RO_NAME,
            "Test RO for ROSRS_Session", "TestROSRS_Session.py", "2012-09-06")
        self.assertEqual(status, 201)
        return (status, reason, rouri, manifest)

    # Actual tests follow

    def testHelpers(self):
        testSplitValues()
        testParseLinks()
        return

    def testListROs(self):
        ros = self.rosrs.listROs()
        return

    def testCreateRO(self):
        (status, reason, rouri, manifest) = self.createTestRO()
        self.assertEqual(status, 201)
        self.assertEqual(reason, "Created")
        self.assertEqual(str(rouri), Config.TEST_RO_URI)
        self.assertIn((rouri, RDF.type, RO.ResearchObject), manifest)
        rolist = self.rosrs.listROs()
        self.assertIn(Config.TEST_RO_URI, [ r["uri"] for r in rolist ])
        return

    def testDeleteRO(self):
        (status, reason, rouri, manifest) = self.createTestRO()
        self.assertEqual(status, 201)
        # Test that new RO is in collection
        rolist = self.rosrs.listROs()
        self.assertIn(Config.TEST_RO_URI, [ r["uri"] for r in rolist ])
        # Delete RO
        (status, reason) = self.rosrs.deleteRO(Config.TEST_RO_PATH)
        self.assertEqual(status, 204)
        self.assertEqual(reason, "No Content")
        # Test that new RO is not in collection
        rolist = self.rosrs.listROs()
        self.assertNotIn(Config.TEST_RO_URI, [ r["uri"] for r in rolist ])
        # Delete again
        (status, reason) = self.rosrs.deleteRO(Config.TEST_RO_PATH)
        self.assertEqual(status, 404)
        self.assertEqual(reason, "Not Found")
        return

    def testGetROManifest(self):
        (status, reason, rouri, manifest) = self.createTestRO()
        self.assertEqual(status, 201)
        # Get manifest
        (status, reason, headers, manifesturi, manifest) = self.rosrs.getROManifest(rouri)
        self.assertEqual(status, 200)
        self.assertEqual(reason, "OK")
        self.assertEqual(headers["content-type"], "application/rdf+xml")
        # Check manifest RDF graph
        self.assertIn((rouri, RDF.type, RO.ResearchObject), manifest)
        self.assertIn((rouri, DCTERMS.creator, None), manifest)
        self.assertIn((rouri, DCTERMS.created, None), manifest)
        self.assertIn((rouri, ORE.isDescribedBy, manifesturi), manifest)
        return

    def testGetROPage(self):
        (status, reason, rouri, manifest) = self.createTestRO()
        self.assertEqual(status, 201)
        # Get landing page
        (status, reason, headers, pageuri, page) = self.rosrs.getROLandingPage(rouri)
        self.assertEqual(status, 200)
        self.assertEqual(reason, "OK")
        self.assertEqual(headers["content-type"], "text/html;charset=UTF-8")
        return

    def testGetROZip(self):
        (status, reason, rouri, manifest) = self.createTestRO()
        self.assertEqual(status, 201)
        # Get manifest
        (status, reason, headers, datauri, data) = self.rosrs.getROZip(rouri)
        self.assertEqual(status, 200)
        self.assertEqual(reason, "OK")
        self.assertEqual(headers["content-type"], "application/zip")
        # @@TODO test content of zip (data)?
        return

    def testAggregateResourceInt(self):
        (status, reason, rouri, manifest) = self.createTestRO()
        self.assertEqual(status, 201)
        # Aggregate internal resource
        rescontent = "Resource content\n"
        (status, reason, proxyuri, resuri) = self.rosrs.aggregateResourceInt(
            rouri, "test/path", ctype="text/plain", body=rescontent)
        self.assertEqual(status, 201)
        self.assertEqual(reason, "Created")
        self.assertEqual(str(resuri), str(rouri)+"test/path")
        # GET content
        (status, reason, headers, uri, data) = self.rosrs.getROResource(
            "test/path", rouri)
        self.assertEqual(status, 200)
        self.assertEqual(headers["content-type"], "text/plain")
        self.assertEqual(data, rescontent)
        # GET proxy
        (getproxyuri, manifest) = self.rosrs.getROResourceProxy(
            "test/path", rouri=rouri)
        self.assertEqual(getproxyuri, proxyuri)
        return

    def testDeleteResourceInt(self):
        (status, reason, rouri, manifest) = self.createTestRO()
        self.assertEqual(status, 201)
        # Create test resource
        rescontent = "Resource content\n"
        (status, reason, proxyuri, resuri) = self.rosrs.aggregateResourceInt(
            rouri, "test/path", ctype="text/plain", body=rescontent)
        self.assertEqual(status, 201)
        # GET content
        (status, reason, headers, uri, data) = self.rosrs.getROResource(
            "test/path", rouri)
        self.assertEqual(status, 200)
        # Delete resource
        (status, reason) = self.rosrs.removeResource(rouri, resuri)
        self.assertEqual(status, 204)
        self.assertEqual(reason, "No Content")
        # Check that resource is no longer available
        (status, reason, headers, uri, data) = self.rosrs.getROResource(resuri)
        self.assertEqual(status, 404)
        return

    def testAggregateResourceExt(self):
        (status, reason, rouri, manifest) = self.createTestRO()
        self.assertEqual(status, 201)
        # Aggregate external resource
        externaluri = rdflib.URIRef("http://example.com/external/resource.txt")
        (status, reason, proxyuri, resuri) = self.rosrs.aggregateResourceExt(
            rouri, externaluri)
        self.assertEqual(status, 201)
        self.assertEqual(reason, "Created")
        self.assertEqual(resuri, externaluri)
        # GET proxy (note: using rdflib.URIRef value for path)
        (getproxyuri, manifest) = self.rosrs.getROResourceProxy(
            externaluri, rouri)
        self.assertEqual(getproxyuri, proxyuri)
        return

    def testDeleteResourceExt(self):
        (status, reason, rouri, manifest) = self.createTestRO()
        self.assertEqual(status, 201)
        # Create test resource
        externaluri = rdflib.URIRef("http://example.com/external/resource.txt")
        (status, reason, proxyuri, resuri) = self.rosrs.aggregateResourceExt(
            rouri, externaluri)
        self.assertEqual(status, 201)
        # GET proxy (note: using rdfliob.URIRef for path)
        (getproxyuri, manifest) = self.rosrs.getROResourceProxy(
            externaluri, rouri)
        self.assertEqual(getproxyuri, proxyuri)
        # Delete resource
        (status, reason) = self.rosrs.removeResource(rouri, resuri)
        self.assertEqual(status, 204)
        self.assertEqual(reason, "No Content")
        (getproxyuri, manifest) = self.rosrs.getROResourceProxy(
            externaluri, rouri)
        self.assertIsNone(getproxyuri)
        self.assertIsNotNone(manifest)
        return

    def testGetROResource(self):
        (status, reason, rouri, manifest) = self.createTestRO()
        self.assertEqual(status, 201)
        # Create test resource
        rescontent = "Resource content\n"
        (status, reason, proxyuri, resuri) = self.rosrs.aggregateResourceInt(
            rouri, "test/path", ctype="text/plain", body=rescontent)
        self.assertEqual(status, 201)
        # GET content
        (status, reason, headers, uri, data) = self.rosrs.getROResource(
            "test/path", rouri)
        self.assertEqual(status, 200)
        self.assertEqual(reason, "OK")
        self.assertEqual(headers["content-type"], "text/plain")
        self.assertEqual(data, rescontent)
        return

    def testGetROResourceRDF(self):
        (status, reason, rouri, manifest) = self.createTestRO()
        self.assertEqual(status, 201)
        # Create internal test resource
        rescontent = """<?xml version="1.0" encoding="UTF-8"?>
            <rdf:RDF
               xmlns:dct="http://purl.org/dc/terms/"
               xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
            >
              <rdf:Description rdf:about="http://example.org/file1.txt">
                <dct:title>Title for file1.txt</dct:title>
              </rdf:Description>
            </rdf:RDF>
            """
        (status, reason, proxyuri, resuri) = self.rosrs.aggregateResourceInt(
            rouri, "test/file1.rdf", ctype="application/rdf+xml", body=rescontent)
        self.assertEqual(status, 201)
        # Get resource content
        (status, reason, headers, uri, graph)= self.rosrs.getROResourceRDF(
            "test/file1.rdf", rouri=rouri)
        self.assertEqual(status, 200)
        self.assertEqual(reason, "OK")
        self.assertEqual(headers["content-type"], "application/rdf+xml")
        s = rdflib.URIRef("http://example.org/file1.txt")
        self.assertIn((s, DCTERMS.title, rdflib.Literal("Title for file1.txt")), graph)
        return

    def testGetROResourceProxy(self):
        (status, reason, rouri, manifest) = self.createTestRO()
        self.assertEqual(status, 201)
        # Create internal test resource
        rescontent = "Resource content\n"
        (status, reason, proxyuri, resuri) = self.rosrs.aggregateResourceInt(
            rouri, "test/path", ctype="text/plain", body=rescontent)
        self.assertEqual(status, 201)
        # Get resource proxy
        (getproxyuri, manifest) = self.rosrs.getROResourceProxy(
            "test/path", rouri=rouri)
        self.assertEqual(getproxyuri, proxyuri)
        return

    def testCreateROAnnotationInt(self):
        (status, reason, rouri, manifest) = self.createTestRO()
        self.assertEqual(status, 201)
        # Create internal test resource
        rescontent = "Resource content\n"
        (status, reason, proxyuri, resuri) = self.rosrs.aggregateResourceInt(
            rouri, "test/file.txt", ctype="text/plain", body=rescontent)
        self.assertEqual(status, 201)
        # Create internal annotation
        annbody = """<?xml version="1.0" encoding="UTF-8"?>
            <rdf:RDF
               xmlns:dct="http://purl.org/dc/terms/"
               xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
               xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
               xml:base="%s"
            >
              <rdf:Description rdf:about="test/file.txt">
                <dct:title>Title for test/file.txt</dct:title>
                <rdfs:seeAlso rdf:resource="http://example.org/test" />
              </rdf:Description>
            </rdf:RDF>
            """%(str(rouri))
        agraph = rdflib.graph.Graph()
        agraph.parse(data=annbody, format="xml")
        (status, reason, annuri, bodyuri) = self.rosrs.createROAnnotationInt(
            rouri, resuri, agraph)
        self.assertEqual(status, 201)
        self.assertEqual(reason, "Created")
        # Retrieve annotation URIs
        auris = list(self.rosrs.getROAnnotationUris(rouri, resuri))
        self.assertIn(annuri, auris)
        buris = list(self.rosrs.getROAnnotationBodyUris(rouri, resuri))
        ### self.assertIn(bodyuri, buris)
        # Retrieve annotation
        (status, reason, bodyuri, anngr) = self.rosrs.getROAnnotation(annuri)
        self.assertEqual(status, 200)
        self.assertEqual(reason, "OK")
        self.assertIn((resuri, DCTERMS.title, rdflib.Literal("Title for test/file.txt")), anngr)
        self.assertIn((resuri, RDFS.seeAlso,  rdflib.URIRef("http://example.org/test")),  anngr)
        return

    def testGetROAnnotationGraph(self):
        (status, reason, rouri, manifest) = self.createTestRO()
        self.assertEqual(status, 201)
        # Create internal test resource
        rescontent = "Resource content\n"
        (status, reason, proxyuri, resuri) = self.rosrs.aggregateResourceInt(
            rouri, "test/file.txt", ctype="text/plain", body=rescontent)
        self.assertEqual(status, 201)
        # Create internal annotation
        annbody = """<?xml version="1.0" encoding="UTF-8"?>
            <rdf:RDF
               xmlns:dct="http://purl.org/dc/terms/"
               xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
               xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
               xml:base="%s"
            >
              <rdf:Description rdf:about="test/file.txt">
                <dct:title>Title for test/file.txt</dct:title>
                <rdfs:seeAlso rdf:resource="http://example.org/test" />
              </rdf:Description>
            </rdf:RDF>
            """%(str(rouri))
        agraph = rdflib.graph.Graph()
        agraph.parse(data=annbody, format="xml")
        (status, reason, annuri, bodyuri) = self.rosrs.createROAnnotationInt(
            rouri, resuri, agraph)
        self.assertEqual(status, 201)
        self.assertEqual(reason, "Created")
        # Retrieve merged annotations
        anngr = self.rosrs.getROAnnotationGraph(rouri, resuri)
        annts = list(anngr.triples((None, None, None)))
        self.assertIn((resuri, DCTERMS.title, rdflib.Literal("Title for test/file.txt")), annts)
        self.assertIn((resuri, RDFS.seeAlso,  rdflib.URIRef("http://example.org/test")),  annts)
        return

    def testCreateROAnnotationExt(self):
        (status, reason, rouri, manifest) = self.createTestRO()
        self.assertEqual(status, 201)
        # Create external test resource
        (status, reason, proxyuri, resuri) = self.rosrs.aggregateResourceExt(
            rouri, rdflib.URIRef("http://example.org/ext"))
        self.assertEqual(status, 201)
        # Create annotation using external body reference
        bodyuri = rdflib.URIRef("http://example.org/ext/ann.rdf")
        (status, reason, annuri) = self.rosrs.createROAnnotationExt(rouri, resuri, bodyuri)
        self.assertEqual(status, 201)
        self.assertEqual(reason, "Created")
        # Retrieve annotation URIs
        auris = list(self.rosrs.getROAnnotationUris(rouri, resuri))
        self.assertIn(annuri, auris)
        buris = list(self.rosrs.getROAnnotationBodyUris(rouri, resuri))
        ### self.assertIn(bodyuri, buris)
        return

    def testUpdateROAnnotationInt(self):
        (status, reason, rouri, manifest) = self.createTestRO()
        self.assertEqual(status, 201)
        # Create internal test resource
        rescontent = "Resource content\n"
        (status, reason, proxyuri, resuri) = self.rosrs.aggregateResourceInt(
            rouri, "test/file.txt", ctype="text/plain", body=rescontent)
        self.assertEqual(status, 201)
        # Create internal annotation
        annbody1 = """<?xml version="1.0" encoding="UTF-8"?>
            <rdf:RDF
               xmlns:dct="http://purl.org/dc/terms/"
               xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
               xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
               xml:base="%s"
            >
              <rdf:Description rdf:about="test/file.txt">
                <dct:title>Title 1</dct:title>
                <rdfs:seeAlso rdf:resource="http://example.org/test1" />
              </rdf:Description>
            </rdf:RDF>
            """%(str(rouri))
        agraph1 = rdflib.graph.Graph()
        agraph1.parse(data=annbody1, format="xml")
        (status, reason, annuri, bodyuri1) = self.rosrs.createROAnnotationInt(
            rouri, resuri, agraph1)
        self.assertEqual(status, 201)
        self.assertEqual(reason, "Created")
        # Retrieve annotation URIs
        auris1 = list(self.rosrs.getROAnnotationUris(rouri, resuri))
        self.assertIn(annuri, auris1)
        buris1 = list(self.rosrs.getROAnnotationBodyUris(rouri, resuri))
        ### self.assertIn(bodyuri1, buris1)
        # Retrieve annotation
        (status, reason, auri1, anngr1a) = self.rosrs.getROAnnotation(annuri)
        self.assertEqual(status, 200)
        self.assertEqual(reason, "OK")
        annts1a = list(anngr1a.triples((None, None, None)))
        self.assertIn((resuri, DCTERMS.title, rdflib.Literal("Title 1")),                 annts1a)
        self.assertIn((resuri, RDFS.seeAlso,  rdflib.URIRef("http://example.org/test1")), annts1a)
        # Retrieve merged annotations
        anngr1b = self.rosrs.getROAnnotationGraph(rouri, resuri)
        annts1b = list(anngr1b.triples((None, None, None)))
        self.assertIn((resuri, DCTERMS.title, rdflib.Literal("Title 1")),                 annts1b)
        self.assertIn((resuri, RDFS.seeAlso,  rdflib.URIRef("http://example.org/test1")), annts1b)
        # Update internal annotation
        annbody2 = """<?xml version="1.0" encoding="UTF-8"?>
            <rdf:RDF
               xmlns:dct="http://purl.org/dc/terms/"
               xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
               xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
               xml:base="%s"
            >
              <rdf:Description rdf:about="test/file.txt">
                <dct:title>Title 2</dct:title>
                <rdfs:seeAlso rdf:resource="http://example.org/test2" />
              </rdf:Description>
            </rdf:RDF>
            """%(str(rouri))
        agraph2 = rdflib.graph.Graph()
        agraph2.parse(data=annbody2, format="xml")
        (status, reason, bodyuri2) = self.rosrs.updateROAnnotationInt(
            rouri, annuri, resuri, agraph2)
        self.assertEqual(status, 200)
        self.assertEqual(reason, "OK")
        # Retrieve annotation URIs
        auris2 = list(self.rosrs.getROAnnotationUris(rouri, resuri))
        self.assertIn(annuri, auris2)
        buris2 = list(self.rosrs.getROAnnotationBodyUris(rouri, resuri))
        ### self.assertIn(bodyuri2, buris2)
        # Retrieve annotation
        (status, reason, auri2a, anngr2a) = self.rosrs.getROAnnotation(annuri)
        annts2a = list(anngr2a.triples((None, None, None)))
        self.assertEqual(status, 200)
        self.assertEqual(reason, "OK")
        self.assertNotIn((resuri, DCTERMS.title, rdflib.Literal("Title 1")),                 annts2a)
        self.assertNotIn((resuri, RDFS.seeAlso,  rdflib.URIRef("http://example.org/test1")), annts2a)
        self.assertIn((resuri, DCTERMS.title, rdflib.Literal("Title 2")),                    annts2a)
        self.assertIn((resuri, RDFS.seeAlso,  rdflib.URIRef("http://example.org/test2")),    annts2a)
        # Retrieve merged annotations
        anngr2b = self.rosrs.getROAnnotationGraph(rouri, resuri)
        annts2b = list(anngr2b.triples((None, None, None)))
        self.assertNotIn((resuri, DCTERMS.title, rdflib.Literal("Title 1")),                 annts2b)
        self.assertNotIn((resuri, RDFS.seeAlso,  rdflib.URIRef("http://example.org/test1")), annts2b)
        self.assertIn((resuri, DCTERMS.title, rdflib.Literal("Title 2")),                    annts2b)
        self.assertIn((resuri, RDFS.seeAlso,  rdflib.URIRef("http://example.org/test2")),    annts2b)
        return

    def testUpdateROAnnotationExt(self):
        (status, reason, rouri, manifest) = self.createTestRO()
        self.assertEqual(status, 201)
        # Create external test resource
        (status, reason, proxyuri, resuri) = self.rosrs.aggregateResourceExt(
            rouri, rdflib.URIRef("http://example.org/ext"))
        self.assertEqual(status, 201)
        # Create annotation using external body reference
        bodyuri1 = rdflib.URIRef("http://example.org/ext/ann1.rdf")
        (status, reason, annuri) = self.rosrs.createROAnnotationExt(rouri, resuri, bodyuri1)
        self.assertEqual(status, 201)
        self.assertEqual(reason, "Created")
        # Retrieve annotation URIs
        auris1 = list(self.rosrs.getROAnnotationUris(rouri, resuri))
        self.assertIn(annuri, auris1)
        buris1 = list(self.rosrs.getROAnnotationBodyUris(rouri, resuri))
        self.assertIn(bodyuri1, buris1)
        # Update annotation using external body reference
        bodyuri2 = rdflib.URIRef("http://example.org/ext/ann2.rdf")
        (status, reason, annuri) = self.rosrs.createROAnnotationExt(rouri, resuri, bodyuri2)
        self.assertEqual(status, 201)
        self.assertEqual(reason, "Created")
        # Retrieve annotation URIs
        auris2 = list(self.rosrs.getROAnnotationUris(rouri, resuri))
        self.assertIn(annuri, auris2)
        buris2 = list(self.rosrs.getROAnnotationBodyUris(rouri, resuri))
        self.assertIn(bodyuri1, buris2)
        return

    def testRemoveROAnnotation(self):
        (status, reason, rouri, manifest) = self.createTestRO()
        self.assertEqual(status, 201)
        # Create internal test resource
        rescontent = "Resource content\n"
        (status, reason, proxyuri, resuri) = self.rosrs.aggregateResourceInt(
            rouri, "test/file.txt", ctype="text/plain", body=rescontent)
        self.assertEqual(status, 201)
        # Create internal annotation
        annbody = """<?xml version="1.0" encoding="UTF-8"?>
            <rdf:RDF
               xmlns:dct="http://purl.org/dc/terms/"
               xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
               xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
               xml:base="%s"
            >
              <rdf:Description rdf:about="test/file.txt">
                <dct:title>Title for test/file.txt</dct:title>
                <rdfs:seeAlso rdf:resource="http://example.org/test" />
              </rdf:Description>
            </rdf:RDF>
            """%(str(rouri))
        agraph = rdflib.graph.Graph()
        agraph.parse(data=annbody, format="xml")
        (status, reason, annuri, bodyuri) = self.rosrs.createROAnnotationInt(
            rouri, resuri, agraph)
        self.assertEqual(status, 201)
        self.assertEqual(reason, "Created")
        # Retrieve annotation URIs
        auris = list(self.rosrs.getROAnnotationUris(rouri, resuri))
        self.assertIn(annuri, auris)
        buris = list(self.rosrs.getROAnnotationBodyUris(rouri, resuri))
        ### self.assertIn(bodyuri, buris)
        # Remove the annotation
        (status, reason) = self.rosrs.removeROAnnotation(rouri, annuri)
        self.assertEqual(status, 204)
        self.assertEqual(reason, "No Content")
        # Retrieve annotation URIs
        auris = list(self.rosrs.getROAnnotationUris(rouri, resuri))
        self.assertNotIn(annuri, auris)
        buris = list(self.rosrs.getROAnnotationBodyUris(rouri, resuri))
        ### self.assertNotIn(bodyuri, buris)
        return

    # Evolution tests

    def testCopyRO(self):
        return

    def testCancelCopyRO(self):
        return

    def testUpdateROStatus(self):
        return

    def testGetROEvolution(self):
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
            , "testHelpers"
            , "testListROs"
            , "testCreateRO"
            , "testDeleteRO"
            , "testGetROManifest"
            , "testGetROPage"
            , "testGetROZip"
            # Resource tests
            , "testAggregateResourceInt"
            , "testDeleteResourceInt"
            , "testAggregateResourceExt"
            , "testDeleteResourceExt"
            , "testGetROResource"
            , "testGetROResourceRDF"
            , "testGetROResourceProxy"
            # Annotation tests
            , "testCreateROAnnotationInt"
            , "testGetROAnnotationGraph"
            , "testCreateROAnnotationExt"
            , "testUpdateROAnnotationInt"
            , "testUpdateROAnnotationExt"
            , "testRemoveROAnnotation"
            # Evolution tests
            , "testCopyRO"
            , "testCancelCopyRO"
            , "testUpdateROStatus"
            , "testGetROEvolution"
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
    return TestUtils.getTestSuite(TestROSRS_Session, testdict, select=select)

if __name__ == "__main__":
    TestUtils.runTests("TestROSRS_Session.log", getTestSuite, sys.argv)

# End.
