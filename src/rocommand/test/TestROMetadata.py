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
from rocommand.ro_namespaces import RDF, RO, AO, ORE, DCTERMS, ROTERMS

from TestConfig import ro_test_config
from StdoutContext import SwitchStdout

import TestROSupport

# Base directory for RO tests in this module
testbase = os.path.dirname(os.path.realpath(__file__))

# Local ro_config for testing
ro_config = {
    "annotationTypes":      ro_annotation.annotationTypes,
    "annotationPrefixes":   ro_annotation.annotationPrefixes,
    "rosrs_uri":            ro_test_config.ROSRS_URI,           # "http://sandbox.wf4ever-project.org/rodl/ROs/"
    "rosrs_access_token":   ro_test_config.ROSRS_ACCESS_TOKEN,  # "47d5423c-b507-4e1c-8", 
    }

cwd        = os.getcwd()
robase     = ro_test_config.ROBASEDIR
robase_abs = os.path.abspath(ro_test_config.ROBASEDIR)

class TestROMetadata(TestROSupport.TestROSupport):
    """
    Test ro metadata handling
    """
    def setUp(self):
        super(TestROMetadata, self).setUp()
        return

    def tearDown(self):
        super(TestROMetadata, self).tearDown()
        return

    # Actual tests follow

    def testNull(self):
        assert True, 'Null test failed'

    def testCreateGraphRoUri(self):
        rodir = self.createTestRo(testbase, "data/ro-test-1", "RO test graph", "ro-testRoGraph")
        romd  = ro_metadata.ro_metadata(ro_config, rodir)
        self.assertEquals(romd.rouri, rdflib.URIRef("file://%s/RO_test_graph/"%(robase_abs)))
        self.deleteTestRo(rodir)
        return

    def testUpdateGraph(self):
        # No separate test - subsumed by other tests?
        return

    def testCreateReadRoAnnotationBody(self):
        """
        Test function to create & read a simple annotation body on an RO
        """
        rodir = self.createTestRo(testbase, "data/ro-test-1", "RO test annotation", "ro-testRoAnnotate")
        romd  = ro_metadata.ro_metadata(ro_config, rodir)
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
        annotationfile = romd._createAnnotationBody(roresource, attrdict)
        # Ann-%04d%02d%02d-%04d-%s.rdf
        self.assertRegexpMatches(annotationfile,
            r"^\.ro/Ann-\d\d\d\d\d\d\d\d-\d+-RO_test_annotation\.rdf",
            msg="Unexpected filename form for annotation: "+annotationfile)
        annotationgraph = romd._readAnnotationBody(annotationfile)
        attrpropdict = {
            "type":         DCTERMS.type,
            # @@TODO "keywords":     DCTERMS.subject,
            "description":  DCTERMS.description,
            "format":       DCTERMS.format,
            "note":         ROTERMS.note,
            "title":        DCTERMS.title,
            "created":      DCTERMS.created
            }
        s = romd.getComponentUri(roresource)
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
        Test function to create & read a simple annotation body on a component file of an RO
        """
        rodir = self.createTestRo(testbase, "data/ro-test-1", "RO test annotation", "ro-testRoAnnotate")
        romd  = ro_metadata.ro_metadata(ro_config, rodir)
        roresource = "subdir1/subdir1-file.txt"
        attrdict = {
            "type":         "Test file",
            "description":  "File in test research object",
            "note":         "File in research object created for annotation testing",
            "title":        "Test file in RO",
            "created":      "2011-12-07"
            }
        annotationfile = romd._createAnnotationBody(roresource, attrdict)
        # Ann-%04d%02d%02d-%04d-%s.rdf
        self.assertRegexpMatches(annotationfile,
            r"^\.ro/Ann-\d\d\d\d\d\d\d\d-\d+-subdir1-file\.txt\.rdf",
            msg="Unexpected filename form for annotation: "+annotationfile)
        annotationgraph = romd._readAnnotationBody(annotationfile)
        attrpropdict = {
            "type":         DCTERMS.type,
            "description":  DCTERMS.description,
            "note":         ROTERMS.note,
            "title":        DCTERMS.title,
            "created":      DCTERMS.created
            }
        s = romd.getComponentUri(roresource)
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
        rodir = self.createTestRo(testbase, "data/ro-test-1",
            "Test init RO annotation", "ro-testRoAnnotate")
        romd  = ro_metadata.ro_metadata(ro_config, rodir)
        roresource = "."
        # Retrieve the anotations
        annotations = romd.getRoAnnotations()
        rouri = romd.getRoUri()
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
            #log.debug("Next %s"%(repr(next)))
            if ( next not in expected_annotations and
                 next[1] != DCTERMS.created       and
                 next[1] != ORE.aggregates        ):
                self.assertTrue(False, "Not expected (%d) %s"%(i, repr(next)))
        self.assertRaises(StopIteration, annotations.next)
        self.deleteTestRo(rodir)
        return

    def testAddGetRoAnnotations(self):
        rodir = self.createTestRo(testbase, "data/ro-test-1",
            "Test add RO annotation", "ro-testRoAnnotate")
        romd  = ro_metadata.ro_metadata(ro_config, rodir)
        roresource = "."
        # Add anotations for RO
        romd.addSimpleAnnotation(roresource, "type", "Research Object")
        romd.addSimpleAnnotation(roresource, "note", "Research object for annotation testing")
        romd.addSimpleAnnotation(roresource, "description", "Added description")
        # Retrieve the anotations
        annotations = romd.getRoAnnotations()
        rouri = romd.getRoUri()
        expected_annotations = (
            [ (rouri, DCTERMS.description,  rdflib.Literal('Test add RO annotation'))
            , (rouri, DCTERMS.title,        rdflib.Literal('Test add RO annotation'))
            , (rouri, DCTERMS.created,      rdflib.Literal('unknown'))
            , (rouri, DCTERMS.creator,      rdflib.Literal('Test User'))
            , (rouri, DCTERMS.identifier,   rdflib.Literal('ro-testRoAnnotate'))
            , (rouri, RDF.type,             RO.ResearchObject)
            , (rouri, DCTERMS.type,         rdflib.Literal('Research Object'))
            , (rouri, ROTERMS.note,         rdflib.Literal('Research object for annotation testing'))
            , (rouri, DCTERMS.description,  rdflib.Literal('Added description'))
            ])
        for i in range(9+4+3):      # Annotations + aggregations + aggregated annotations
            next = annotations.next()
            #log.debug("Next %s"%(repr(next)))
            if ( next not in expected_annotations and
                 next[1] != DCTERMS.created       and
                 next[1] != ORE.aggregates        ):
                self.assertTrue(False, "Not expected (%d) %s"%(i, repr(next)))
        self.assertRaises(StopIteration, annotations.next)
        self.deleteTestRo(rodir)
        return

    def testAddRoAnnotationIsAggregated(self):
        rodir = self.createTestRo(testbase, "data/ro-test-1",
            "Test add RO annotation", "ro-testRoAnnotate")
        romd  = ro_metadata.ro_metadata(ro_config, rodir)
        roresource = "."
        # Add anotations for RO
        romd.addSimpleAnnotation(roresource, "note", "Research object for annotation testing")
        # Retrieve the anotations
        rouri           = romd.getRoUri()
        addedannotation = (rouri, ROTERMS.note, rdflib.Literal('Research object for annotation testing'))
        annotations     = romd.getRoAnnotations()
        self.assertIn(addedannotation, annotations)
        for (a, p) in romd.manifestgraph.subject_predicates(object=rouri):
            if p in [AO.annotatesResource, RO.annotatesAggregatedResource]:
                b = romd.manifestgraph.value(subject=a, predicate=AO.body)
                if str(romd.getComponentUriRel(b)) != ro_test_config.ROMANIFESTPATH:
                    aggregate_annbody = (rouri, ORE.aggregates, b)
                    self.assertIn(aggregate_annbody, romd.manifestgraph)
        self.deleteTestRo(rodir)
        return

    def testRemoveGetRoAnnotations(self):
        rodir = self.createTestRo(testbase, "data/ro-test-1",
            "Test remove RO annotation", "ro-testRoAnnotate")
        romd  = ro_metadata.ro_metadata(ro_config, rodir)
        roresource = "."
        # Remove some anotations for RO
        romd.removeSimpleAnnotation(roresource, "type", "Research Object")
        romd.removeSimpleAnnotation(roresource, "title", "Test remove RO annotation")
        romd.removeSimpleAnnotation(roresource, "description",  None)
        romd.removeSimpleAnnotation(roresource, "note", "Research object for annotation testing")
        romd.removeSimpleAnnotation(roresource, "created", None)
        # Retrieve the anotations
        annotations = romd.getRoAnnotations()
        rouri = romd.getRoUri()
        expected_annotations = (
            [ (rouri, DCTERMS.creator,      rdflib.Literal('Test User'))
            , (rouri, DCTERMS.identifier,   rdflib.Literal('ro-testRoAnnotate'))
            , (rouri, RDF.type,             RO.ResearchObject)
            ])
        for i in range(4):
            next = annotations.next()
            #log.debug("Next %s"%(repr(next)))
            if ( next not in expected_annotations and
                 next[1] != DCTERMS.created       and
                 next[1] != ORE.aggregates        ):
                self.assertTrue(False, "Not expected (%d) %s"%(i, repr(next)))
        self.assertRaises(StopIteration, annotations.next)
        self.deleteTestRo(rodir)
        return

    def testReplaceGetRoAnnotations(self):
        rodir = self.createTestRo(testbase, "data/ro-test-1",
            "Test replace RO annotation", "ro-testRoAnnotate")
        romd  = ro_metadata.ro_metadata(ro_config, rodir)
        roresource = "."
        # Replace anotations for RO
        romd.replaceSimpleAnnotation(roresource, "type",        "Research Object")
        romd.replaceSimpleAnnotation(roresource, "description", "Replacement description")
        romd.replaceSimpleAnnotation(roresource, "note", "Research object for annotation replacement testing")
        romd.replaceSimpleAnnotation(roresource, "title",       "Replacement title")
        romd.replaceSimpleAnnotation(roresource, "created",     "2011-12-07")
        # Retrieve the anotations
        annotations = romd.getRoAnnotations()
        rouri = romd.getRoUri()
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
            #log.debug("Next %s"%(repr(next)))
            if ( next not in expected_annotations and
                 next[1] != ORE.aggregates        ):
                self.assertTrue(False, "Not expected (%d) %s"%(i, repr(next)))
        self.assertRaises(StopIteration, annotations.next)
        self.deleteTestRo(rodir)
        return

    def testAddGetFileAnnotations(self):
        rodir = self.createTestRo(testbase, "data/ro-test-1", "Test add file annotation", "ro-testRoAnnotate")
        romd  = ro_metadata.ro_metadata(ro_config, rodir)
        roresource = "subdir1/subdir1-file.txt"
        # Add anotations for file
        romd.addSimpleAnnotation(roresource, "type",        "Test file")
        romd.addSimpleAnnotation(roresource, "description", "File in test research object")
        romd.addSimpleAnnotation(roresource, "note", "Research object file created for annotation testing")
        romd.addSimpleAnnotation(roresource, "title",       "Test file in RO")
        romd.addSimpleAnnotation(roresource, "created",     "2011-12-07")
        romd.addSimpleAnnotation(roresource, "rdf:type",    ROTERMS.resource)
        # Retrieve the file anotations
        annotations = romd.getFileAnnotations(roresource)
        resourceuri = romd.getComponentUri(roresource)
        log.debug("resourceuri: %s"%(resourceuri))
        expected_annotations = (
            [ (resourceuri, DCTERMS.type,         rdflib.Literal('Test file'))
            , (resourceuri, DCTERMS.description,  rdflib.Literal('File in test research object'))
            , (resourceuri, ROTERMS.note,         rdflib.Literal('Research object file created for annotation testing'))
            , (resourceuri, DCTERMS.title,        rdflib.Literal('Test file in RO'))
            , (resourceuri, DCTERMS.created,      rdflib.Literal('2011-12-07'))
            , (resourceuri, RDF.type,             ROTERMS.resource)
            ])
        for i in range(6):
            next = annotations.next()
            #log.debug("Next %s"%(repr(next)))
            if ( next not in expected_annotations):
                self.assertTrue(False, "Not expected (%d) %s"%(i, repr(next)))
        self.assertRaises(StopIteration, annotations.next)
        self.deleteTestRo(rodir)
        return

    def testRemoveGetFileAnnotations(self):
        rodir = self.createTestRo(testbase, "data/ro-test-1",
            "Test remove file annotation", "ro-testRoAnnotate")
        romd  = ro_metadata.ro_metadata(ro_config, rodir)
        roresource = "subdir1/subdir1-file.txt"
        # Add anotations for file
        romd.addSimpleAnnotation(roresource, "type",        "Test file")
        romd.addSimpleAnnotation(roresource, "description", "File in test research object")
        romd.addSimpleAnnotation(roresource, "note", "Research object file created for annotation testing")
        romd.addSimpleAnnotation(roresource, "title",       "Test file in RO")
        romd.addSimpleAnnotation(roresource, "created",     "2011-12-07")
        romd.addSimpleAnnotation(roresource, "rdf:type",    ROTERMS.resource)
        # Remove annotations
        romd.removeSimpleAnnotation(roresource, "description", "File in test research object")
        romd.removeSimpleAnnotation(roresource, "note",        None)
        # Retrieve the file anotations
        annotations = romd.getFileAnnotations(roresource)
        resourceuri = romd.getComponentUri(roresource)
        log.debug("resourceuri: %s"%(resourceuri))
        expected_annotations = (
            [ (resourceuri, DCTERMS.type,         rdflib.Literal('Test file'))
            , (resourceuri, DCTERMS.title,        rdflib.Literal('Test file in RO'))
            , (resourceuri, DCTERMS.created,      rdflib.Literal('2011-12-07'))
            , (resourceuri, RDF.type,             ROTERMS.resource)
            ])
        for i in range(4):
            next = annotations.next()
            #log.debug("Next %s"%(repr(next)))
            if ( next not in expected_annotations):
                self.assertTrue(False, "Not expected (%d) %s"%(i, repr(next)))
        self.assertRaises(StopIteration, annotations.next)
        self.deleteTestRo(rodir)
        return

    def testAddGetAllAnnotations(self):
        rodir = self.createTestRo(testbase, "data/ro-test-1",
            "Test get all annotations", "ro-testRoAnnotate")
        romd  = ro_metadata.ro_metadata(ro_config, rodir)
        roresource = "subdir1/subdir1-file.txt"
        # Add anotations for file
        romd.addSimpleAnnotation(roresource, "type",        "Test file")
        romd.addSimpleAnnotation(roresource, "description", "File in test research object")
        romd.addSimpleAnnotation(roresource, "note", "Research object file created for annotation testing")
        romd.addSimpleAnnotation(roresource, "title",       "Test file in RO")
        romd.addSimpleAnnotation(roresource, "created",     "2011-12-07")
        romd.addSimpleAnnotation(roresource, "rdf:type",    ROTERMS.resource)
        # Retrieve the file anotations
        annotations = romd.getAllAnnotations()
        rouri       = romd.getRoUri()
        resourceuri = romd.getComponentUri(roresource)
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
        for i in range(12+1+6+6):      # Annotations + aggregations + aggregated annotations
            next = annotations.next()
            #log.debug("Next %s"%(repr(next)))
            if ( next not in expected_annotations and
                 next[1] != DCTERMS.created       and
                 next[1] != ORE.aggregates        ):
                self.assertTrue(False, "Not expected (%d) %s"%(i, repr(next)))
        self.assertRaises(StopIteration, annotations.next)
        self.deleteTestRo(rodir)
        return

    def testAddGetAnnotationValues(self):
        rodir = self.createTestRo(testbase, "data/ro-test-1",
            "Test get annotation values", "ro-testRoAnnotate")
        romd  = ro_metadata.ro_metadata(ro_config, rodir)
        roresource = "subdir1/subdir1-file.txt"
        # Add anotations for file
        romd.addSimpleAnnotation(roresource, "type",         "Test file")
        romd.addSimpleAnnotation(roresource, "description",  "File in test research object")
        romd.addSimpleAnnotation(roresource, "rdf:type",     ROTERMS.resource)
        # Retrieve the anotations
        values = romd.getAnnotationValues(".", "title")
        self.assertEquals(values.next(), rdflib.Literal('Test get annotation values'))
        self.assertRaises(StopIteration, values.next)
        values = romd.getAnnotationValues(".", "rdf:type")
        self.assertEquals(values.next(), RO.ResearchObject)
        self.assertRaises(StopIteration, values.next)
        values = romd.getAnnotationValues(roresource, "type")
        self.assertEquals(values.next(), rdflib.Literal('Test file'))
        self.assertRaises(StopIteration, values.next)
        values = romd.getAnnotationValues(roresource, "description")
        self.assertEquals(values.next(), rdflib.Literal('File in test research object'))
        self.assertRaises(StopIteration, values.next)
        values = romd.getAnnotationValues(roresource, "rdf:type")
        self.assertEquals(values.next(), ROTERMS.resource)
        self.assertRaises(StopIteration, values.next)
        # Clean up
        self.deleteTestRo(rodir)
        return

    def testAddAggregatedResources(self):
        """
        Test function that adds aggregated resources to a research object manifest
        """
        rodir = self.createTestRo(testbase, "data/ro-test-1", "RO test aggregation", "ro-testRoAggregation")
        romd  = ro_metadata.ro_metadata(ro_config, rodir)
        romd.addAggregatedResources(rodir, recurse=True)
        def URIRef(path):
            return romd.getComponentUri(path)
        s = romd.getRoUri()
        g = rdflib.Graph()
        g.add( (s, RDF.type,            RO.ResearchObject                  ) )
        g.add( (s, ORE.aggregates,      URIRef("README-ro-test-1")         ) )
        g.add( (s, ORE.aggregates,      URIRef("subdir1/subdir1-file.txt") ) )
        g.add( (s, ORE.aggregates,      URIRef("subdir2/subdir2-file.txt") ) )
        self.checkManifestGraph(rodir, g)
        n = rdflib.Graph()
        n.add( (s, ORE.aggregates,      URIRef("subdir1/") ) )
        n.add( (s, ORE.aggregates,      URIRef("subdir2/") ) )
        self.checkManifestGraphOmits(rodir, n)
        self.deleteTestRo(rodir)
        return

    def testAddAggregatedResourcesWithDirs(self):
        """
        Test function that adds aggregated resources to a research object manifest
        """
        rodir = self.createTestRo(testbase, "data/ro-test-1", "RO test aggregation", "ro-testRoAggregation")
        romd  = ro_metadata.ro_metadata(ro_config, rodir)
        romd.addAggregatedResources(rodir, recurse=True, includeDirs=True)
        def URIRef(path):
            return romd.getComponentUri(path)
        s = romd.getRoUri()
        g = rdflib.Graph()
        g.add( (s, RDF.type,            RO.ResearchObject                  ) )
        g.add( (s, ORE.aggregates,      URIRef("README-ro-test-1")         ) )
        g.add( (s, ORE.aggregates,      URIRef("subdir1/") ) )
        g.add( (s, ORE.aggregates,      URIRef("subdir1/subdir1-file.txt") ) )
        g.add( (s, ORE.aggregates,      URIRef("subdir2/") ) )
        g.add( (s, ORE.aggregates,      URIRef("subdir2/subdir2-file.txt") ) )
        self.checkManifestGraph(rodir, g)
        self.deleteTestRo(rodir)
        return

    def testGetAggregatedResources(self):
        """
        Test function that enumerates aggregated resources to a research object manifest
        """
        rodir = self.createTestRo(testbase, "data/ro-test-1", "RO test aggregation", "ro-testRoAggregation")
        romd  = ro_metadata.ro_metadata(ro_config, rodir)
        romd.addAggregatedResources(rodir, recurse=True)
        def URIRef(path):
            return romd.getComponentUriAbs(path)
        resources = (
          [ URIRef("README-ro-test-1")
          , URIRef("minim.rdf")
          , URIRef("subdir1/subdir1-file.txt")
          , URIRef("subdir2/subdir2-file.txt")
          , URIRef("filename%20with%20spaces.txt")
          , URIRef("filename%23with%23hashes.txt")
          ])
        c = 0
        for r in romd.getAggregatedResources():
            if romd.getResourceType(r) != RO.AggregatedAnnotation:
                c += 1
                self.assertIn(r, resources)
        self.assertEqual(c, len(resources))
        self.deleteTestRo(rodir)
        return

    def testQueryAnnotations(self):
        rodir = self.createTestRo(testbase, "data/ro-test-1",
            "Test query annotations", "ro-testRoAnnotate")
        romd  = ro_metadata.ro_metadata(ro_config, rodir)
        roresource = "subdir1/subdir1-file.txt"
        # Add anotations for file
        romd.addSimpleAnnotation(roresource, "type",        "Test file")
        romd.addSimpleAnnotation(roresource, "description", "File in test research object")
        romd.addSimpleAnnotation(roresource, "note", "Research object file created for annotation testing")
        romd.addSimpleAnnotation(roresource, "title",       "Test file in RO")
        romd.addSimpleAnnotation(roresource, "created",     "2011-12-07")
        romd.addSimpleAnnotation(roresource, "rdf:type",    ROTERMS.resource)
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
                    dcterms:creator "Test User" .
                ?file rdf:type roterms:resource ;
                    dcterms:type "Test file" ;
                    dcterms:created "2011-12-07" .
            }
            """)
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
                    dcterms:creator "Test User" .
                ?file rdf:type roterms:resource ;
                    dcterms:type "Test file" ;
                    dcterms:created ?date .
            }
            """)
        rouri       = romd.getRoUri()
        resourceuri = romd.getComponentUri(roresource)
        resp = romd.queryAnnotations(query)
        self.assertEqual(resp[0]['ro'],   rouri)
        self.assertEqual(resp[0]['file'], romd.getComponentUri(roresource))
        self.assertEqual(resp[0]['date'], rdflib.Literal("2011-12-07"))
        self.deleteTestRo(rodir)
        return

    def testQueryAnnotationsWithMissingGraph(self):
        """
        This test is included to ensure that queries still work as expected when
        the manifest contains a reference to a non-existent manifest graph
        """
        rodir = self.createTestRo(testbase, "data/ro-test-1",
            "Test query annotations", "ro-testRoAnnotate")
        romd  = ro_metadata.ro_metadata(ro_config, rodir)
        roresource = "subdir1/subdir1-file.txt"
        # Add anotations for file
        romd.addSimpleAnnotation(roresource, "type",        "Test file")
        romd.addSimpleAnnotation(roresource, "description", "File in test research object")
        romd.addSimpleAnnotation(roresource, "note", "Research object file created for annotation testing")
        romd.addSimpleAnnotation(roresource, "title",       "Test file in RO")
        romd.addSimpleAnnotation(roresource, "created",     "2011-12-07")
        romd.addSimpleAnnotation(roresource, "rdf:type",    ROTERMS.resource)
        # Apply non-exietent graph annotation
        annotation_graph_filename = os.path.join(os.path.abspath(rodir), "annotate-none.rdf")
        romd.addGraphAnnotation(roresource, annotation_graph_filename)
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
                    dcterms:creator "Test User" .
                ?file rdf:type roterms:resource ;
                    dcterms:type "Test file" ;
                    dcterms:created "2011-12-07" .
            }
            """)
        resp = romd.queryAnnotations(query)
        self.assertTrue(resp, "Expected 'True' result for query: %s")
        self.deleteTestRo(rodir)
        return

    def testQueryAnnotationsRemote(self):
        romd  = ro_metadata.ro_metadata(
            ro_config,
            "http://andros.zoo.ox.ac.uk/workspace/wf4ever-ro-catalogue/v0.1/simple-requirements/"
            )
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
                    dcterms:creator "Test user" ;
                    ore:aggregates ?file .
            }
            """)
        resp = romd.queryAnnotations(query)
        self.assertTrue(resp, "Expected 'True' result for query: %s")
        query = (queryprefixes +
            """
            ASK
            {
                ?ro rdf:type ro:ResearchObject ;
                    dcterms:creator "Not user" .
            }
            """)
        resp = romd.queryAnnotations(query)
        self.assertFalse(resp, "Expected 'False' result for query: %s")
        query = (queryprefixes +
            """
            SELECT * WHERE
            {
                ?ro rdf:type ro:ResearchObject ;
                    dcterms:creator "Test user" ;
                    ore:aggregates ?file .
            }
            """)
        rouri       = romd.getRoUri()
        resourceuri = romd.getComponentUri("README")
        resp = romd.queryAnnotations(query)
        self.assertEqual(resp[0]['ro'],   rouri)
        aggs = [ respn['file'] for respn in resp ]
        self.assertIn( resourceuri, aggs, repr(aggs))
        return

    # URI tests

    def testGetRoUri(self):
        def testUri(rodir, uristring):
            romd  = ro_metadata.ro_metadata(ro_config, rodir, dummysetupfortest=True)
            self.assertEquals(romd.getRoUri(), rdflib.URIRef(uristring))
            return
        testUri("/example/ro/dir",  "file:///example/ro/dir/" )
        testUri("/example/ro/dir/", "file:///example/ro/dir/" )
        testUri("ro/dir",           "file://%s/ro/dir/"%(cwd) )
        testUri("ro/dir/",          "file://%s/ro/dir/"%(cwd) )
        testUri(robase+"/ro/dir",   "file://%s/ro/dir/"%(robase_abs) )
        testUri(robase+"/ro/dir/",  "file://%s/ro/dir/"%(robase_abs) )
        return

    def testGetComponentUri(self):
        def testUri(rodir, path, uristring):
            romd  = ro_metadata.ro_metadata(ro_config, rodir, dummysetupfortest=True)
            self.assertEquals(romd.getComponentUri(path), rdflib.URIRef(uristring))
            return
        testUri("/example/ro/dir",  "a/b.txt", "file:///example/ro/dir/a/b.txt" )
        testUri("/example/ro/dir/", "a/b.txt", "file:///example/ro/dir/a/b.txt" )
        testUri("ro/dir",           "a/b.txt", "file://%s/ro/dir/a/b.txt"%(cwd) )
        testUri("ro/dir/",          "a/b.txt", "file://%s/ro/dir/a/b.txt"%(cwd) )
        testUri("/example/ro/dir",  "a/b/d/",  "file:///example/ro/dir/a/b/d/"  )
        testUri("/example/ro/dir/", "a/b/d/",  "file:///example/ro/dir/a/b/d/"  )
        testUri("ro/dir",           "a/b/d/",  "file://%s/ro/dir/a/b/d/"%(cwd)  )
        testUri("ro/dir/",          "a/b/d/",  "file://%s/ro/dir/a/b/d/"%(cwd)  )
        return

    def testGetComponentUriRel(self):
        def testUri(rodir, path, uristring):
            romd  = ro_metadata.ro_metadata(ro_config, rodir, dummysetupfortest=True)
            self.assertEquals(romd.getComponentUriRel(path), rdflib.URIRef(uristring))
            return

        testUri("/example/ro/dir",  "a/b.txt",  "a/b.txt" )
        testUri("/example/ro/dir/", "a/b.txt",  "a/b.txt" )
        testUri("ro/dir",           "a/b.txt",  "a/b.txt" )
        testUri("ro/dir/",          "a/b.txt",  "a/b.txt" )
        testUri("/example/ro/dir",  "a/b/d/",   "a/b/d/"  )
        testUri("/example/ro/dir/", "a/b/d/",   "a/b/d/"  )
        testUri("ro/dir",           "a/b/d/",   "a/b/d/"  )
        testUri("ro/dir/",          "a/b/d/",   "a/b/d/"  )
        testUri("/example/ro/dir",  "",         ""        )
        testUri("/example/ro/dir/", "",         ""        )
        testUri("ro/dir",           "",         ""        )
        testUri("ro/dir/",          "",         ""        )

        testUri("/example/ro/dir",  "/example/ro/dir/a/b.txt",  "a/b.txt" )
        testUri("/example/ro/dir/", "/example/ro/dir/a/b.txt",  "a/b.txt" )
        testUri("ro/dir",           "%s/ro/dir/a/b.txt"%(cwd),  "a/b.txt" )
        testUri("ro/dir/",          "%s/ro/dir/a/b.txt"%(cwd),  "a/b.txt" )
        testUri("/example/ro/dir",  "/example/ro/dir/a/b/d/",   "a/b/d/" )
        testUri("/example/ro/dir/", "/example/ro/dir/a/b/d/",   "a/b/d/" )
        testUri("ro/dir",           "%s/ro/dir/a/b/d/"%(cwd),   "a/b/d/" )
        testUri("ro/dir/",          "%s/ro/dir/a/b/d/"%(cwd),   "a/b/d/" )
        testUri("/example/ro/dir",  "/example/ro/dir/",         "" )
        testUri("/example/ro/dir/", "/example/ro/dir/",         "" )
        testUri("ro/dir",           "%s/ro/dir/"%(cwd),         "" )
        testUri("ro/dir/",          "%s/ro/dir/"%(cwd),         "" )

        testUri("/example/ro/dir",  "file:///example/ro/dir/a/b.txt",   "a/b.txt" )
        testUri("/example/ro/dir/", "file:///example/ro/dir/a/b.txt",   "a/b.txt" )
        testUri("/example/ro/dir",  "file:///example/ro/dir/a/b/d/",    "a/b/d/" )
        testUri("/example/ro/dir/", "file:///example/ro/dir/a/b/d/",    "a/b/d/" )
        testUri("/example/ro/dir",  "file:///example/ro/dir/",          "" )
        testUri("/example/ro/dir/", "file:///example/ro/dir/",          "" )
        return

    def testGetComponentUriRelUri(self):
        """
        Same as previous tests, but with path supplied as rdflib.URIRef value rather than string
        """
        def testUri(rodir, path, uristring):
            romd  = ro_metadata.ro_metadata(ro_config, rodir, dummysetupfortest=True)
            self.assertEquals(romd.getComponentUriRel(rdflib.URIRef(path)), rdflib.URIRef(uristring))
            return

        testUri("/example/ro/dir",  "a/b.txt",  "a/b.txt" )
        testUri("/example/ro/dir/", "a/b.txt",  "a/b.txt" )
        testUri("ro/dir",           "a/b.txt",  "a/b.txt" )
        testUri("ro/dir/",          "a/b.txt",  "a/b.txt" )
        testUri("/example/ro/dir",  "a/b/d/",   "a/b/d/"  )
        testUri("/example/ro/dir/", "a/b/d/",   "a/b/d/"  )
        testUri("ro/dir",           "a/b/d/",   "a/b/d/"  )
        testUri("ro/dir/",          "a/b/d/",   "a/b/d/"  )
        testUri("/example/ro/dir",  "",         ""        )
        testUri("/example/ro/dir/", "",         ""        )
        testUri("ro/dir",           "",         ""        )
        testUri("ro/dir/",          "",         ""        )

        testUri("/example/ro/dir",  "/example/ro/dir/a/b.txt",  "a/b.txt" )
        testUri("/example/ro/dir/", "/example/ro/dir/a/b.txt",  "a/b.txt" )
        testUri("ro/dir",           "%s/ro/dir/a/b.txt"%(cwd),  "a/b.txt" )
        testUri("ro/dir/",          "%s/ro/dir/a/b.txt"%(cwd),  "a/b.txt" )
        testUri("/example/ro/dir",  "/example/ro/dir/a/b/d/",   "a/b/d/" )
        testUri("/example/ro/dir/", "/example/ro/dir/a/b/d/",   "a/b/d/" )
        testUri("ro/dir",           "%s/ro/dir/a/b/d/"%(cwd),   "a/b/d/" )
        testUri("ro/dir/",          "%s/ro/dir/a/b/d/"%(cwd),   "a/b/d/" )
        testUri("/example/ro/dir",  "/example/ro/dir/",         "" )
        testUri("/example/ro/dir/", "/example/ro/dir/",         "" )
        testUri("ro/dir",           "%s/ro/dir/"%(cwd),         "" )
        testUri("ro/dir/",          "%s/ro/dir/"%(cwd),         "" )

        testUri("/example/ro/dir",  "file:///example/ro/dir/a/b.txt",   "a/b.txt" )
        testUri("/example/ro/dir/", "file:///example/ro/dir/a/b.txt",   "a/b.txt" )
        testUri("/example/ro/dir",  "file:///example/ro/dir/a/b/d/",    "a/b/d/" )
        testUri("/example/ro/dir/", "file:///example/ro/dir/a/b/d/",    "a/b/d/" )
        testUri("/example/ro/dir",  "file:///example/ro/dir/",          "" )
        testUri("/example/ro/dir/", "file:///example/ro/dir/",          "" )
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
            , "testCreateGraphRoUri"
            , "testCreateReadRoAnnotationBody"
            , "testCreateReadFileAnnotationBody"
            , "testGetInitialRoAnnotations"
            , "testAddGetRoAnnotations"
            , "testAddRoAnnotationIsAggregated"
            , "testRemoveGetRoAnnotations"
            , "testReplaceGetRoAnnotations"
            , "testAddGetFileAnnotations"
            , "testRemoveGetFileAnnotations"
            , "testAddGetAllAnnotations"
            , "testAddGetAnnotationValues"
            , "testQueryAnnotations"
            , "testQueryAnnotationsWithMissingGraph"
            , "testGetRoUri"
            , "testGetComponentUri"
            , "testGetComponentUriRel"
            , "testGetComponentUriRelUri"
            , "testAddAggregatedResources"
            , "testAddAggregatedResourcesWithDirs"
            , "testGetAggregatedResources"
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
    return TestUtils.getTestSuite(TestROMetadata, testdict, select=select)

if __name__ == "__main__":
    TestUtils.runTests("TestROMetadata.log", getTestSuite, sys.argv)

# End.
