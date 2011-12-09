#!/usr/bin/python

"""
Module to test RO manager annotation support utilities

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

#from rocommand import ro
#from rocommand import ro_utils
from rocommand import ro_settings
from rocommand import ro_manifest
from rocommand import ro_annotation
from rocommand.ro_manifest import RDF, DCTERMS, ROTERMS, OXDS

from TestConfig import ro_test_config
from StdoutContext import SwitchStdout

import TestROSupport

# Local ro_config for testing
ro_config = {
    "annotationTypes": ro_annotation.annotationTypes
    }

class TestAnnotationUtils(TestROSupport.TestROSupport):
    """
    Test ro annotation commands
    """
    def setUp(self):
        super(TestAnnotationUtils, self).setUp()
        return

    def tearDown(self):
        super(TestAnnotationUtils, self).tearDown()
        return

    # Actual tests follow

    def testNull(self):
        assert True, 'Null test failed'

    def testGetAnnotationByName(self):
        def testAnnotaton(name, expecteduri, expectedtype):
            (apred, atype) = ro_annotation.getAnnotationByName(ro_config, name)
            self.assertEqual(apred, expecteduri)
            self.assertEqual(atype, expectedtype)
            return 
        self.assertEqual(RDF.type, rdflib.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"))
        testAnnotaton("title",          DCTERMS.title,          "string")
        testAnnotaton("description",    DCTERMS.description,    "text")
        testAnnotaton("rdf:type",       RDF.type,               "resource")
        # testAnnotaton(rdflib.URIRef("http://example.org/foo"),  "<http://example.org/foo>")
        return

    def testGetAnnotationByUri(self):
        def testAnnotaton(uri, expectedname, expectedtype):
            (aname, atype) = ro_annotation.getAnnotationByUri(ro_config, uri)
            self.assertEqual(aname, expectedname)
            self.assertEqual(atype, expectedtype)
            return 
        testAnnotaton(DCTERMS.title,          "title",          "string")
        testAnnotaton(DCTERMS.description,    "description",    "text")
        testAnnotaton(RDF.type,               "rdf:type",       "resource")
        return

    def testGetAnnotationNameByUri(self):
        def testAnnotatonName(uri, name):
            roconfig = {
                "annotationTypes": ro_annotation.annotationTypes
                }
            self.assertEqual(ro_annotation.getAnnotationNameByUri(roconfig, uri), name)
            return 
        self.assertEqual(RDF.type, rdflib.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"))
        testAnnotatonName(DCTERMS.title,        "title")
        testAnnotatonName(DCTERMS.description,  "description")
        testAnnotatonName(RDF.type,             "rdf:type")
        testAnnotatonName(rdflib.URIRef("http://example.org/foo"),  "<http://example.org/foo>")
        return

    def testMakeAnnotationFilename(self):
        rodir = "/example/ro/dir"
        def testAnnotationFileName(filename, expectedname):
            aname = ro_annotation.makeAnnotationFilename(rodir, filename)
            self.assertEqual(aname, expectedname)
            return
        testAnnotationFileName("a/b", "%s/%s/a/b"%(rodir, ro_settings.MANIFEST_DIR))
        testAnnotationFileName("a/",  "%s/%s/a/"%(rodir, ro_settings.MANIFEST_DIR))
        return

    def testCreateReadRoAnnotationBody(self):
        """
        Test function to create simple annotation body
        """
        rodir = self.createTestRo("data/ro-test-1", "RO test annotation", "ro-testRoAnnotate")
        roresource = "."
        attrdict = {
            "type":         "Research Object",
            # @@TODO: handle lists "keywords":     ["test", "research", "object"],
            "description":  "Test research object",
            "format":       "application/vnd.wf4ever.ro",
            "note":         "Research object created for annotation testing",
            "title":        "Test research object",
            "created":      "2011-12-07"
            }
        annotationfilename = ro_annotation.createSimpleAnnotationBody(
            ro_config, rodir, roresource, attrdict)
        # Ann-%04d%02d%02d-%04d-%s.rdf
        self.assertRegexpMatches(annotationfilename,
            r"Ann-\d\d\d\d\d\d\d\d-\d+-RO_test_annotation\.rdf", 
            msg="Unexpected filename form for annotation: "+annotationfilename)
        annotationgraph = ro_annotation.readAnnotationBody(rodir, annotationfilename)
        attrpropdict = {
            "type":         DCTERMS.type,
            # @@TODO "keywords":     DCTERMS.subject,
            "description":  DCTERMS.description,
            "format":       DCTERMS.format,
            "note":         ROTERMS.note,
            "title":        DCTERMS.title,
            "created":      DCTERMS.created
            }
        s = ro_manifest.getComponentUri(rodir, roresource)
        log.debug("annotation subject %s"%repr(s))
        for k in attrpropdict:
            p = attrpropdict[k]
            log.debug("annotation predicate %s"%repr(p))
            v = attrdict[k]
            a = annotationgraph.value(s, p, None)
            log.debug("annotation value %s"%repr(a))
            #self.assertEqual(len(a), 1, "Singleton result expected")
            self.assertEqual(a, v)
        return

    def testCreateReadFileAnnotationBody(self):
        """
        Test function to create simple annotation body
        """
        rodir = self.createTestRo("data/ro-test-1", "RO test annotation", "ro-testRoAnnotate")
        roresource = "subdir1/subdir1-file.txt"
        attrdict = {
            "type":         "Research Object",
            "description":  "Test research object",
            "note":         "Research object created for annotation testing",
            "title":        "Test research object",
            "created":      "2011-12-07"
            }
        annotationfilename = ro_annotation.createSimpleAnnotationBody(
            ro_config, rodir, roresource, attrdict)
        # Ann-%04d%02d%02d-%04d-%s.rdf
        self.assertRegexpMatches(annotationfilename,
            r"Ann-\d\d\d\d\d\d\d\d-\d+-subdir1-file\.txt\.rdf", 
            msg="Unexpected filename form for annotation: "+annotationfilename)
        annotationgraph = ro_annotation.readAnnotationBody(rodir, annotationfilename)
        attrpropdict = {
            "type":         DCTERMS.type,
            "description":  DCTERMS.description,
            "note":         ROTERMS.note,
            "title":        DCTERMS.title,
            "created":      DCTERMS.created
            }
        s = ro_manifest.getComponentUri(rodir, roresource)
        log.debug("annotation subject %s"%repr(s))
        for k in attrpropdict:
            p = attrpropdict[k]
            log.debug("annotation predicate %s"%repr(p))
            v = attrdict[k]
            a = annotationgraph.value(s, p, None)
            log.debug("annotation value %s"%repr(a))
            #self.assertEqual(len(a), 1, "Singleton result expected")
            self.assertEqual(a, v)
        return

    def testAddGetRoAnnotations(self):
        rodir = self.createTestRo("data/ro-test-1", "RO test annotation", "ro-testRoAnnotate")
        roresource = "."
        # Add anotations for RO
        ro_annotation.addSimpleAnnotation(ro_config, rodir, roresource, 
            "type",         "Research Object")
        ro_annotation.addSimpleAnnotation(ro_config, rodir, roresource, 
            "description",  "Test research object")
        ro_annotation.addSimpleAnnotation(ro_config, rodir, roresource, 
            "note",         "Research object created for annotation testing")
        ro_annotation.addSimpleAnnotation(ro_config, rodir, roresource, 
            "title",        "Test research object")
        ro_annotation.addSimpleAnnotation(ro_config, rodir, roresource, 
            "created",      "2011-12-07")
        # Retrieve the anotations
        annotations = ro_annotation.getRoAnnotations(rodir)
        rouri = ro_manifest.getRoUri(rodir)
        expected_annotations = (
            [ (rouri, DCTERMS.type,         "...")
            , (rouri, DCTERMS.description,  rdflib.Literal('RO test annotation'))
            , (rouri, ROTERMS.note,         "...")
            , (rouri, DCTERMS.title,        rdflib.Literal('RO test annotation'))
            , (rouri, DCTERMS.created,      rdflib.Literal('unknown'))
            , (rouri, DCTERMS.creator,      rdflib.Literal('Test User'))
            , (rouri, DCTERMS.identifier,   rdflib.Literal('ro-testRoAnnotate'))
            , (rouri, RDF.type,             OXDS.Grouping)
            ])
        def testNextAnnotation(tag):
            next = annotations.next()
            log.debug("Next %s"%(repr(next)))
            if not next in expected_annotations and next[1] != DCTERMS.created:
                self.assertTrue(False, "Not expected (%s) %s"%(tag, repr(next)))
            return
        testNextAnnotation("1")
        testNextAnnotation("2")
        testNextAnnotation("3")
        testNextAnnotation("4")
        testNextAnnotation("5")
        testNextAnnotation("6")
        #testNextAnnotation("7")
        self.assertRaises(StopIteration, annotations.next)
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
            , "testGetAnnotationByName"
            , "testGetAnnotationByUri"
            , "testGetAnnotationNameByUri"
            , "testMakeAnnotationFilename"
            , "testCreateReadRoAnnotationBody"
            , "testCreateReadFileAnnotationBody"
            , "testAddGetRoAnnotations"
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
    return TestUtils.getTestSuite(TestAnnotationUtils, testdict, select=select)

if __name__ == "__main__":
    TestUtils.runTests("TestAnnotationUtils.log", getTestSuite, sys.argv)

# End.
