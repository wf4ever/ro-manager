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
from rocommand.ro_manifest import RDF, DCTERMS, ROTERMS, RO, ORE

from TestConfig import ro_test_config
from StdoutContext import SwitchStdout

import TestROSupport

# Local ro_config for testing
ro_config = {
    "annotationTypes": ro_annotation.annotationTypes
    }

cwd        = os.getcwd()
robase     = ro_test_config.ROBASEDIR
robase_abs = os.path.abspath(ro_test_config.ROBASEDIR)

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

    def testGetFileUri(self):
        self.assertEquals(ro_manifest.getFileUri("/example/a/b.txt"),
                          rdflib.URIRef("file:///example/a/b.txt"))
        self.assertEquals(ro_manifest.getFileUri("a/b.txt"),
                          rdflib.URIRef("file://%s/a/b.txt"%(cwd)))
        self.assertEquals(ro_manifest.getFileUri("/example/ro/dir/a/b/d/"),
                          rdflib.URIRef("file:///example/ro/dir/a/b/d/"))
        self.assertEquals(ro_manifest.getFileUri("a/b/d/"),
                          rdflib.URIRef("file://%s/a/b/d/"%(cwd)))
        return

    def testGetUriFile(self):
        self.assertEquals(ro_manifest.getUriFile(rdflib.URIRef("file:///example/a/b.txt")), "/example/a/b.txt")
        self.assertEquals(ro_manifest.getUriFile(rdflib.URIRef("/example/a/b.txt")), "/example/a/b.txt")
        self.assertEquals(ro_manifest.getUriFile(rdflib.URIRef("a/b.txt")), "a/b.txt")
        return

    def testGetRoUri(self):
        self.assertEquals(ro_manifest.getRoUri("/example/ro/dir"), rdflib.URIRef("file:///example/ro/dir/"))
        self.assertEquals(ro_manifest.getRoUri("/example/ro/dir/"), rdflib.URIRef("file:///example/ro/dir/"))
        self.assertEquals(ro_manifest.getRoUri("ro/dir"), rdflib.URIRef("file://%s/ro/dir/"%(cwd)))
        self.assertEquals(ro_manifest.getRoUri("ro/dir/"), rdflib.URIRef("file://%s/ro/dir/"%(cwd)))
        self.assertEquals(ro_manifest.getRoUri(robase+"/ro/dir"), rdflib.URIRef("file://%s/ro/dir/"%(robase_abs)))
        self.assertEquals(ro_manifest.getRoUri(robase+"/ro/dir/"), rdflib.URIRef("file://%s/ro/dir/"%(robase_abs)))
        return

    def testGetComponentUri(self):
        self.assertEquals(ro_manifest.getComponentUri("/example/ro/dir", "a/b.txt"),
                          rdflib.URIRef("file:///example/ro/dir/a/b.txt"))
        self.assertEquals(ro_manifest.getComponentUri("/example/ro/dir/", "a/b.txt"),
                          rdflib.URIRef("file:///example/ro/dir/a/b.txt"))
        self.assertEquals(ro_manifest.getComponentUri("ro/dir", "a/b.txt"),
                          rdflib.URIRef("file://%s/ro/dir/a/b.txt"%(cwd)))
        self.assertEquals(ro_manifest.getComponentUri("ro/dir/", "a/b.txt"),
                          rdflib.URIRef("file://%s/ro/dir/a/b.txt"%(cwd)))
        self.assertEquals(ro_manifest.getComponentUri("/example/ro/dir", "a/b/d/"),
                          rdflib.URIRef("file:///example/ro/dir/a/b/d/"))
        self.assertEquals(ro_manifest.getComponentUri("/example/ro/dir/", "a/b/d/"),
                          rdflib.URIRef("file:///example/ro/dir/a/b/d/"))
        self.assertEquals(ro_manifest.getComponentUri("ro/dir", "a/b/d/"),
                          rdflib.URIRef("file://%s/ro/dir/a/b/d/"%(cwd)))
        self.assertEquals(ro_manifest.getComponentUri("ro/dir/", "a/b/d/"),
                          rdflib.URIRef("file://%s/ro/dir/a/b/d/"%(cwd)))
        return

    def testGetComponentUriRel(self):
        self.assertEquals(ro_manifest.getComponentUriRel("/example/ro/dir", "a/b.txt"),
                          rdflib.URIRef("a/b.txt"))
        self.assertEquals(ro_manifest.getComponentUriRel("/example/ro/dir/", "a/b.txt"),
                          rdflib.URIRef("a/b.txt"))
        self.assertEquals(ro_manifest.getComponentUriRel("ro/dir", "a/b.txt"),
                          rdflib.URIRef("a/b.txt"))
        self.assertEquals(ro_manifest.getComponentUriRel("ro/dir/", "a/b.txt"),
                          rdflib.URIRef("a/b.txt"))
        self.assertEquals(ro_manifest.getComponentUriRel("/example/ro/dir", "a/b/d/"),
                          rdflib.URIRef("a/b/d/"))
        self.assertEquals(ro_manifest.getComponentUriRel("/example/ro/dir/", "a/b/d/"),
                          rdflib.URIRef("a/b/d/"))
        self.assertEquals(ro_manifest.getComponentUriRel("ro/dir", "a/b/d/"),
                          rdflib.URIRef("a/b/d/"))
        self.assertEquals(ro_manifest.getComponentUriRel("ro/dir/", "a/b/d/"),
                          rdflib.URIRef("a/b/d/"))
        self.assertEquals(ro_manifest.getComponentUriRel("/example/ro/dir", ""),
                          rdflib.URIRef(""))
        self.assertEquals(ro_manifest.getComponentUriRel("/example/ro/dir/", ""),
                          rdflib.URIRef(""))
        self.assertEquals(ro_manifest.getComponentUriRel("ro/dir", ""),
                          rdflib.URIRef(""))
        self.assertEquals(ro_manifest.getComponentUriRel("ro/dir/", ""),
                          rdflib.URIRef(""))
        self.assertEquals(ro_manifest.getComponentUriRel("/example/ro/dir", "/example/ro/dir/a/b.txt"),
                          rdflib.URIRef("a/b.txt"))
        self.assertEquals(ro_manifest.getComponentUriRel("/example/ro/dir/", "/example/ro/dir/a/b.txt"),
                          rdflib.URIRef("a/b.txt"))
        self.assertEquals(ro_manifest.getComponentUriRel("ro/dir", "%s/ro/dir/a/b.txt"%(cwd)),
                          rdflib.URIRef("a/b.txt"))
        self.assertEquals(ro_manifest.getComponentUriRel("ro/dir/", "%s/ro/dir/a/b.txt"%(cwd)),
                          rdflib.URIRef("a/b.txt"))
        self.assertEquals(ro_manifest.getComponentUriRel("/example/ro/dir", "/example/ro/dir/a/b/d/"),
                          rdflib.URIRef("a/b/d/"))
        self.assertEquals(ro_manifest.getComponentUriRel("/example/ro/dir/", "/example/ro/dir/a/b/d/"),
                          rdflib.URIRef("a/b/d/"))
        self.assertEquals(ro_manifest.getComponentUriRel("ro/dir", "%s/ro/dir/a/b/d/"%(cwd)),
                          rdflib.URIRef("a/b/d/"))
        self.assertEquals(ro_manifest.getComponentUriRel("ro/dir/", "%s/ro/dir/a/b/d/"%(cwd)),
                          rdflib.URIRef("a/b/d/"))
        self.assertEquals(ro_manifest.getComponentUriRel("/example/ro/dir", "/example/ro/dir/"),
                          rdflib.URIRef(""))
        self.assertEquals(ro_manifest.getComponentUriRel("/example/ro/dir/", "/example/ro/dir/"),
                          rdflib.URIRef(""))
        self.assertEquals(ro_manifest.getComponentUriRel("ro/dir", "%s/ro/dir/"%(cwd)),
                          rdflib.URIRef(""))
        self.assertEquals(ro_manifest.getComponentUriRel("ro/dir/", "%s/ro/dir/"%(cwd)),
                          rdflib.URIRef(""))
        # Test supplied file: URI string
        self.assertEquals(ro_manifest.getComponentUriRel("/example/ro/dir", "file:///example/ro/dir/a/b.txt"),
                          rdflib.URIRef("a/b.txt"))
        self.assertEquals(ro_manifest.getComponentUriRel("/example/ro/dir/", "file:///example/ro/dir/a/b.txt"),
                          rdflib.URIRef("a/b.txt"))
        self.assertEquals(ro_manifest.getComponentUriRel("/example/ro/dir", "file:///example/ro/dir/a/b/d/"),
                          rdflib.URIRef("a/b/d/"))
        self.assertEquals(ro_manifest.getComponentUriRel("/example/ro/dir/", "file:///example/ro/dir/a/b/d/"),
                          rdflib.URIRef("a/b/d/"))
        self.assertEquals(ro_manifest.getComponentUriRel("/example/ro/dir", "file:///example/ro/dir/"),
                          rdflib.URIRef(""))
        self.assertEquals(ro_manifest.getComponentUriRel("/example/ro/dir/", "file:///example/ro/dir/"),
                          rdflib.URIRef(""))
        # Test supplied file: URI
        self.assertEquals(ro_manifest.getComponentUriRel("/example/ro/dir",
                                                         rdflib.URIRef("file:///example/ro/dir/a/b.txt")),
                          rdflib.URIRef("a/b.txt"))
        self.assertEquals(ro_manifest.getComponentUriRel("/example/ro/dir/",
                                                         rdflib.URIRef("file:///example/ro/dir/a/b.txt")),
                          rdflib.URIRef("a/b.txt"))
        self.assertEquals(ro_manifest.getComponentUriRel("/example/ro/dir", 
                                                         rdflib.URIRef("file:///example/ro/dir/a/b/d/")),
                          rdflib.URIRef("a/b/d/"))
        self.assertEquals(ro_manifest.getComponentUriRel("/example/ro/dir/", 
                                                         rdflib.URIRef("file:///example/ro/dir/a/b/d/")),
                          rdflib.URIRef("a/b/d/"))
        self.assertEquals(ro_manifest.getComponentUriRel("/example/ro/dir",
                                                         rdflib.URIRef("file:///example/ro/dir/")),
                          rdflib.URIRef(""))
        self.assertEquals(ro_manifest.getComponentUriRel("/example/ro/dir/", 
                                                         rdflib.URIRef("file:///example/ro/dir/")),
                          rdflib.URIRef(""))
        return

    def testGetGraphRoUri(self):
        rodir = self.createTestRo("data/ro-test-1", "RO test graph", "ro-testRoGraph")
        rograph = ro_manifest.readManifestGraph(rodir)
        self.assertEquals(ro_manifest.getGraphRoUri(rodir, rograph),
                          rdflib.URIRef("file://%s/RO_test_graph/"%(robase_abs)))
        self.deleteTestRo(rodir)
        return

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
        annotationfilebase = ro_annotation.createSimpleAnnotationBody(
            ro_config, rodir, roresource, attrdict)
        # Ann-%04d%02d%02d-%04d-%s.rdf
        self.assertRegexpMatches(annotationfilebase,
            r"Ann-\d\d\d\d\d\d\d\d-\d+-RO_test_annotation\.rdf", 
            msg="Unexpected filename form for annotation: "+annotationfilebase)
        annotationfilename = ro_annotation.makeAnnotationFilename(rodir, annotationfilebase)
        annotationgraph    = ro_annotation.readAnnotationBody(rodir, annotationfilename)
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
        self.deleteTestRo(rodir)
        return

    def testCreateReadFileAnnotationBody(self):
        """
        Test function to create simple annotation body
        """
        rodir = self.createTestRo("data/ro-test-1", "RO test annotation", "ro-testRoAnnotate")
        roresource = "subdir1/subdir1-file.txt"
        attrdict = {
            "type":         "Test file",
            "description":  "File in test research object",
            "note":         "File in research object created for annotation testing",
            "title":        "Test file in RO",
            "created":      "2011-12-07"
            }
        annotationfilebase = ro_annotation.createSimpleAnnotationBody(
            ro_config, rodir, roresource, attrdict)
        # Ann-%04d%02d%02d-%04d-%s.rdf
        self.assertRegexpMatches(annotationfilebase,
            r"Ann-\d\d\d\d\d\d\d\d-\d+-subdir1-file\.txt\.rdf", 
            msg="Unexpected filename form for annotation: "+annotationfilebase)
        annotationfilename = ro_annotation.makeAnnotationFilename(rodir, annotationfilebase)
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
        self.deleteTestRo(rodir)
        return

    def testGetInitialRoAnnotations(self):
        rodir = self.createTestRo("data/ro-test-1", "Test init RO annotation", "ro-testRoAnnotate")
        roresource = "."
        # Retrieve the anotations
        annotations = ro_annotation.getRoAnnotations(rodir)
        rouri = ro_manifest.getRoUri(rodir)
        expected_annotations = (
            [ (rouri, DCTERMS.description,  rdflib.Literal('Test init RO annotation'))
            , (rouri, DCTERMS.title,        rdflib.Literal('Test init RO annotation'))
            , (rouri, DCTERMS.created,      rdflib.Literal('unknown'))
            , (rouri, DCTERMS.creator,      rdflib.Literal('Test User'))
            , (rouri, DCTERMS.identifier,   rdflib.Literal('ro-testRoAnnotate'))
            , (rouri, RDF.type,             RO.ResearchObject)
            ])
        for i in range(6+1):      # Annotations + aggregations
            next = annotations.next()
            log.debug("Next %s"%(repr(next)))
            if ( next not in expected_annotations and 
                 next[1] != DCTERMS.created       and
                 next[1] != ORE.aggregates        ):
                self.assertTrue(False, "Not expected (%d) %s"%(i, repr(next)))
        self.assertRaises(StopIteration, annotations.next)
        self.deleteTestRo(rodir)
        return

    def testAddGetRoAnnotations(self):
        rodir = self.createTestRo("data/ro-test-1", "Test add RO annotation", "ro-testRoAnnotate")
        roresource = "."
        # Add anotations for RO
        ro_annotation.addSimpleAnnotation(ro_config, rodir, roresource, 
            "type",         "Research Object")
        ro_annotation.addSimpleAnnotation(ro_config, rodir, roresource, 
            "note",         "Research object created for annotation testing")
        ro_annotation.addSimpleAnnotation(ro_config, rodir, roresource, 
            "description",  "Added description")
        # Retrieve the anotations
        annotations = ro_annotation.getRoAnnotations(rodir)
        rouri = ro_manifest.getRoUri(rodir)
        expected_annotations = (
            [ (rouri, DCTERMS.description,  rdflib.Literal('Test add RO annotation'))
            , (rouri, DCTERMS.title,        rdflib.Literal('Test add RO annotation'))
            , (rouri, DCTERMS.created,      rdflib.Literal('unknown'))
            , (rouri, DCTERMS.creator,      rdflib.Literal('Test User'))
            , (rouri, DCTERMS.identifier,   rdflib.Literal('ro-testRoAnnotate'))
            , (rouri, RDF.type,             RO.ResearchObject)
            , (rouri, DCTERMS.type,         rdflib.Literal('Research Object'))
            , (rouri, ROTERMS.note,         rdflib.Literal('Research object created for annotation testing'))
            , (rouri, DCTERMS.description,  rdflib.Literal('Added description'))
            ])
        for i in range(9+4):      # Annotations + aggregations
            next = annotations.next()
            log.debug("Next %s"%(repr(next)))
            if ( next not in expected_annotations and 
                 next[1] != DCTERMS.created       and
                 next[1] != ORE.aggregates        ):
                self.assertTrue(False, "Not expected (%d) %s"%(i, repr(next)))
        self.assertRaises(StopIteration, annotations.next)
        self.deleteTestRo(rodir)
        return

    def testRemoveGetRoAnnotations(self):
        rodir = self.createTestRo("data/ro-test-1", "Test remove RO annotation", "ro-testRoAnnotate")
        roresource = "."
        # Replace anotations for RO
        ro_annotation.removeSimpleAnnotation(ro_config, rodir, roresource, 
            "type",         "Research Object")
        ro_annotation.removeSimpleAnnotation(ro_config, rodir, roresource, 
            "title",        "Test remove RO annotation")
        ro_annotation.removeSimpleAnnotation(ro_config, rodir, roresource, 
            "description",  None)
        ro_annotation.removeSimpleAnnotation(ro_config, rodir, roresource, 
            "note",         "Research object created for annotation testing")
        ro_annotation.removeSimpleAnnotation(ro_config, rodir, roresource, 
            "created",      None)
        # Retrieve the anotations
        annotations = ro_annotation.getRoAnnotations(rodir)
        rouri = ro_manifest.getRoUri(rodir)
        expected_annotations = (
            [ (rouri, DCTERMS.creator,      rdflib.Literal('Test User'))
            , (rouri, DCTERMS.identifier,   rdflib.Literal('ro-testRoAnnotate'))
            , (rouri, RDF.type,             RO.ResearchObject)
            ])
        def testNextAnnotation(tag):
            next = annotations.next()
            log.debug("Next %s"%(repr(next)))
            if ( next not in expected_annotations and 
                 next[1] != DCTERMS.created       and
                 next[1] != ORE.aggregates        ):
                self.assertTrue(False, "Not expected (%s) %s"%(tag, repr(next)))
            return
        testNextAnnotation("1")
        testNextAnnotation("2")
        testNextAnnotation("3")
        testNextAnnotation("4")
        self.assertRaises(StopIteration, annotations.next)
        self.deleteTestRo(rodir)
        return

    def testReplaceGetRoAnnotations(self):
        rodir = self.createTestRo("data/ro-test-1", "Test replace RO annotation", "ro-testRoAnnotate")
        roresource = "."
        # Replace anotations for RO
        ro_annotation.replaceSimpleAnnotation(ro_config, rodir, roresource, 
            "type",         "Research Object")
        ro_annotation.replaceSimpleAnnotation(ro_config, rodir, roresource, 
            "description",  "Replacement description")
        ro_annotation.replaceSimpleAnnotation(ro_config, rodir, roresource, 
            "note",         "Research object for annotation replacement testing")
        ro_annotation.replaceSimpleAnnotation(ro_config, rodir, roresource, 
            "title",        "Replacement title")
        ro_annotation.replaceSimpleAnnotation(ro_config, rodir, roresource, 
            "created",      "2011-12-07")
        # Retrieve the anotations
        annotations = ro_annotation.getRoAnnotations(rodir)
        rouri = ro_manifest.getRoUri(rodir)
        expected_annotations = (
            [ (rouri, DCTERMS.type,         rdflib.Literal('Research Object'))
            , (rouri, DCTERMS.title,        rdflib.Literal('Replacement title'))
            , (rouri, DCTERMS.description,  rdflib.Literal('Replacement description'))
            , (rouri, ROTERMS.note,         rdflib.Literal('Research object for annotation replacement testing'))
            , (rouri, DCTERMS.created,      rdflib.Literal('2011-12-07'))
            , (rouri, DCTERMS.creator,      rdflib.Literal('Test User'))
            , (rouri, DCTERMS.identifier,   rdflib.Literal('ro-testRoAnnotate'))
            , (rouri, RDF.type,             RO.ResearchObject)
            ])
        for i in range(8+1):      # Annotations + aggregations
            next = annotations.next()
            log.debug("Next %s"%(repr(next)))
            if ( next not in expected_annotations and 
                 next[1] != ORE.aggregates        ):
                self.assertTrue(False, "Not expected (%d) %s"%(i, repr(next)))
        self.assertRaises(StopIteration, annotations.next)
        self.deleteTestRo(rodir)
        return

    def testAddGetFileAnnotations(self):
        rodir = self.createTestRo("data/ro-test-1", "Test add file annotation", "ro-testRoAnnotate")
        roresource = "subdir1/subdir1-file.txt"
        # Add anotations for file
        ro_annotation.addSimpleAnnotation(ro_config, rodir, roresource, 
            "type",         "Test file")
        ro_annotation.addSimpleAnnotation(ro_config, rodir, roresource, 
            "description",  "File in test research object")
        ro_annotation.addSimpleAnnotation(ro_config, rodir, roresource, 
            "note",         "Research object file created for annotation testing")
        ro_annotation.addSimpleAnnotation(ro_config, rodir, roresource, 
            "title",        "Test file in RO")
        ro_annotation.addSimpleAnnotation(ro_config, rodir, roresource, 
            "created",      "2011-12-07")
        ro_annotation.addSimpleAnnotation(ro_config, rodir, roresource, 
            "rdf:type",     ROTERMS.resource)
        # Retrieve the file anotations
        annotations = ro_annotation.getFileAnnotations(rodir, roresource)
        resourceuri = ro_manifest.getComponentUri(rodir, roresource)
        log.debug("resourceuri: %s"%(resourceuri))
        expected_annotations = (
            [ (resourceuri, DCTERMS.type,         rdflib.Literal('Test file'))
            , (resourceuri, DCTERMS.description,  rdflib.Literal('File in test research object'))
            , (resourceuri, ROTERMS.note,         rdflib.Literal('Research object file created for annotation testing'))
            , (resourceuri, DCTERMS.title,        rdflib.Literal('Test file in RO'))
            , (resourceuri, DCTERMS.created,      rdflib.Literal('2011-12-07'))
            , (resourceuri, RDF.type,             ROTERMS.resource)
            ])
        def testNextAnnotation(tag):
            next = annotations.next()
            log.debug("Next %s"%(repr(next)))
            if not next in expected_annotations:
                self.assertTrue(False, "Not expected (%s) %s"%(tag, repr(next)))
            return
        testNextAnnotation("1")
        testNextAnnotation("2")
        testNextAnnotation("3")
        testNextAnnotation("4")
        testNextAnnotation("5")
        testNextAnnotation("6")
        self.assertRaises(StopIteration, annotations.next)
        self.deleteTestRo(rodir)
        return

    # @@TODO: test remove file annotation

    def testAddGetAllAnnotations(self):
        rodir = self.createTestRo("data/ro-test-1", "Test get all annotations", "ro-testRoAnnotate")
        roresource = "subdir1/subdir1-file.txt"
        # Add anotations for file
        ro_annotation.addSimpleAnnotation(ro_config, rodir, roresource, 
            "type",         "Test file")
        ro_annotation.addSimpleAnnotation(ro_config, rodir, roresource, 
            "description",  "File in test research object")
        ro_annotation.addSimpleAnnotation(ro_config, rodir, roresource, 
            "note",         "Research object file created for annotation testing")
        ro_annotation.addSimpleAnnotation(ro_config, rodir, roresource, 
            "title",        "Test file in RO")
        ro_annotation.addSimpleAnnotation(ro_config, rodir, roresource, 
            "created",      "2011-12-07")
        ro_annotation.addSimpleAnnotation(ro_config, rodir, roresource, 
            "rdf:type",     ROTERMS.resource)
        # Retrieve the file anotations
        annotations = ro_annotation.getAllAnnotations(rodir)
        rouri       = ro_manifest.getRoUri(rodir)
        resourceuri = ro_manifest.getComponentUri(rodir, roresource)
        log.debug("resourceuri: %s"%(resourceuri))
        expected_annotations = (
            [ (rouri,       DCTERMS.description,  rdflib.Literal('Test get all annotations'))
            , (rouri,       DCTERMS.title,        rdflib.Literal('Test get all annotations'))
            , (rouri,       DCTERMS.created,      rdflib.Literal('unknown'))
            , (rouri,       DCTERMS.creator,      rdflib.Literal('Test User'))
            , (rouri,       DCTERMS.identifier,   rdflib.Literal('ro-testRoAnnotate'))
            , (rouri,       RDF.type,             RO.ResearchObject)
            , (resourceuri, DCTERMS.type,         rdflib.Literal('Test file'))
            , (resourceuri, DCTERMS.description,  rdflib.Literal('File in test research object'))
            , (resourceuri, ROTERMS.note,         rdflib.Literal('Research object file created for annotation testing'))
            , (resourceuri, DCTERMS.title,        rdflib.Literal('Test file in RO'))
            , (resourceuri, DCTERMS.created,      rdflib.Literal('2011-12-07'))
            , (resourceuri, RDF.type,             ROTERMS.resource)
            ])
        for i in range(12+1+6):      # Annotations + aggregations
            next = annotations.next()
            log.debug("Next %s"%(repr(next)))
            if ( next not in expected_annotations and 
                 next[1] != DCTERMS.created       and
                 next[1] != ORE.aggregates        ):
                self.assertTrue(False, "Not expected (%d) %s"%(i, repr(next)))
        self.assertRaises(StopIteration, annotations.next)
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
            , "testGetFileUri"
            , "testGetUriFile"
            , "testGetRoUri"
            , "testGetComponentUri"
            , "testGetComponentUriRel"
            , "testGetGraphRoUri"
            , "testGetAnnotationByName"
            , "testGetAnnotationByUri"
            , "testGetAnnotationNameByUri"
            , "testMakeAnnotationFilename"
            , "testCreateReadRoAnnotationBody"
            , "testCreateReadFileAnnotationBody"
            , "testGetInitialRoAnnotations"
            , "testAddGetRoAnnotations"
            , "testRemoveGetRoAnnotations"
            , "testReplaceGetRoAnnotations"
            , "testAddGetFileAnnotations"
            , "testAddGetAllAnnotations"
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
