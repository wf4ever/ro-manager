#!/usr/bin/python

"""
Module to test RO manager annotation commands

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
from rocommand.ro_namespaces import RDF, RDFS, DCTERMS, RO, AO, ORE

from TestConfig import ro_test_config
from StdoutContext import SwitchStdout

import TestROSupport

# Base directory for RO tests in this module
testbase = os.path.dirname(os.path.abspath(__file__))

# Local ro_config for testing
ro_config = {
    "annotationTypes":      ro_annotation.annotationTypes,
    "annotationPrefixes":   ro_annotation.annotationPrefixes
    }

class TestAnnotations(TestROSupport.TestROSupport):
    """
    Test ro annotation commands
    """
    def setUp(self):
        super(TestAnnotations, self).setUp()
        return

    def tearDown(self):
        super(TestAnnotations, self).tearDown()
        return

    # Actual tests follow

    def testNull(self):
        assert True, 'Null test failed'

    def testAnnotate(self):
        """
        Annotate file in created RO

        ro annotate file attribute-name [ attribute-value ]
        """
        rodir = self.createTestRo(testbase, "data/ro-test-1", "RO test annotation", "ro-testRoAnnotate")
        args = [
            "ro", "annotate", rodir+"/"+"subdir1/subdir1-file.txt", "title", "subdir1-file title",
            "-v",
            ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
        outtxt = self.outstr.getvalue()
        assert status == 0, outtxt
        log.debug("outtxt %s"%outtxt)
        #self.assertRegexpMatches(outtxt, "annotation.*dc:title")
        # Read manifest and check for annotation
        values = ro_annotation._getAnnotationValues(ro_config, rodir, "subdir1/subdir1-file.txt", "title")
        self.assertEquals(values.next(), rdflib.Literal("subdir1-file title"))
        self.assertRaises(StopIteration, values.next)
        # Clean up
        self.deleteTestRo(rodir)
        return

    def annotateTest(self, anntype, annvalue, anntypeuri, annexpect):
        rodir = self.createTestRo(testbase, "data/ro-test-1", "RO test annotation", "ro-testRoAnnotate")
        args = [
            "ro", "annotate", rodir+"/"+"subdir1/subdir1-file.txt", anntype, annvalue,
            "-v",
            ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
        outtxt = self.outstr.getvalue()
        assert status == 0, outtxt
        self.assertEqual(outtxt.count("ro annotate"), 1)
        # Read manifest and check for annotation
        annotations = ro_annotation._getFileAnnotations(rodir, "subdir1/subdir1-file.txt")
        resourceuri = ro_manifest.getComponentUri(rodir, "subdir1/subdir1-file.txt")
        expected_annotations = (
            [ (resourceuri, anntypeuri, rdflib.Literal(annexpect))
            ])
        for i in range(1):
            next = annotations.next()
            #log.debug("Next %s"%(repr(next)))
            if ( next not in expected_annotations):
                self.assertTrue(False, "Not expected (%d) %s"%(i, repr(next)))
        self.assertRaises(StopIteration, annotations.next)
        self.deleteTestRo(rodir)
        return

    # Other annotation types to add (cf. http://wf4ever.github.com/labs/ro-annotator/mockups/1/index.html)

    def testAnnotateType(self):
        self.annotateTest("type", "file type", DCTERMS.type, "file type")
        return

    def testAnnotateKeywords(self):
        self.annotateTest("keywords", "foo,bar", DCTERMS.subject, "foo,bar")  #@@TODO: make multiples
        return

    def testAnnotateDescription(self):
        descr = """
            Multiline
            description
            """
        self.annotateTest("description", descr, DCTERMS.description, descr)
        return

    def testAnnotateCreated(self):
        #@@TODO: use for creation date/time of file
        created = "2011-09-14T12:00:00"
        self.annotateTest("created", created, DCTERMS.created, created)
        return

    def testAnnotateTypeUri(self):
        anntypestr = "http://example.org/annotationtype"
        anntypeuri = rdflib.URIRef(anntypestr)
        annvalue   = "Annotation value"
        self.annotateTest(anntypestr, annvalue, anntypeuri, annvalue)
        return

    def testAnnotateTypeCurie(self):
        anntypestr = "rdfs:comment"
        anntypeuri = RDFS.comment
        annvalue   = "Annotation value"
        self.annotateTest(anntypestr, annvalue, anntypeuri, annvalue)
        return

    # @@TODO: Test use of CURIE as type

    def annotateMultiple(self, rodir, rofile, annotations):
        with SwitchStdout(self.outstr):
            for a in annotations:
                args = ["ro", "annotate", rofile, a["atypename"], a["avalue"]]
                status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
                outtxt = self.outstr.getvalue()
                assert status == 0, outtxt
        # Reset output stream buffer closed
        self.outstr = StringIO.StringIO()
        return

    def testAnnotateMultiple(self):
        rodir  = self.createTestRo(testbase, "data/ro-test-1", "RO test annotation", "ro-testRoAnnotate")
        rofile = rodir+"/"+"subdir1/subdir1-file.txt"
        define_annotations = (
            [ {"atypename": "type",        "avalue":"atype",    "atypeuri":DCTERMS.type,        "aexpect":"atype" }
            , {"atypename": "keywords",    "avalue":"asubj",    "atypeuri":DCTERMS.subject,     "aexpect":"asubj" }
            , {"atypename": "description", "avalue":"adesc",    "atypeuri":DCTERMS.description, "aexpect":"adesc" }
            , {"atypename": "format",      "avalue":"aformat",  "atypeuri":DCTERMS.format,      "aexpect":"aformat" }
            , {"atypename": "title",       "avalue":"atitle",   "atypeuri":DCTERMS.title,       "aexpect":"atitle" }
            , {"atypename": "created",     "avalue":"acreated", "atypeuri":DCTERMS.created,     "aexpect":"acreated" }
            #, {"atypename": ..., "avalue":..., "atypeuri":..., "aexpect":... }
            #, {"atypename": ..., "avalue":..., "atypeuri":..., "aexpect":... }
            ])
        self.annotateMultiple(rodir, rofile, define_annotations)
        # Read manifest and check for annotation
        annotations = ro_annotation._getFileAnnotations(rodir, "subdir1/subdir1-file.txt")
        resourceuri = ro_manifest.getComponentUri(rodir, "subdir1/subdir1-file.txt")
        expected_annotations = (
            [ (resourceuri, a["atypeuri"], rdflib.Literal(a["aexpect"]))
                for a in define_annotations
            ])
        for i in range(6):
            next = annotations.next()
            #log.debug("Next %s"%(repr(next)))
            if ( next not in expected_annotations):
                self.assertTrue(False, "Not expected (%d) %s"%(i, repr(next)))
        self.assertRaises(StopIteration, annotations.next)
        # Clean up
        self.deleteTestRo(rodir)
        return

    def testAnnotateFileWithEscapes(self):
        rodir  = self.createTestRo(testbase, "data/ro-test-1", "RO test annotation", "ro-testRoAnnotate")
        rofile1 = rodir+"/"+"filename with spaces.txt"
        rofile2 = rodir+"/"+"filename#with#hashes.txt"
        with SwitchStdout(self.outstr):
            for rofile in [rofile1,rofile2]:
                args = ["ro", "annotate", rofile, "type", "atype"]
                status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
                outtxt = self.outstr.getvalue()
                assert status == 0, outtxt
        # Reset output stream buffer closed
        self.outstr = StringIO.StringIO()
        # Read manifest and check for annotation
        for rofile in [rofile1,rofile2]:
            resourceuri = ro_manifest.getComponentUri(rodir, rofile)
            annotations = ro_annotation._getFileAnnotations(rodir, rofile)
            next = annotations.next()
            self.assertEqual(next, (resourceuri, DCTERMS.type, rdflib.Literal("atype")))
            self.assertRaises(StopIteration, annotations.next)
        # Clean up
        self.deleteTestRo(rodir)
        return

    # Test annotation display
    def testAnnotationDisplayRo(self):
        # Construct annotated RO
        rodir = self.createTestRo(testbase, "data/ro-test-1", "RO test annotation", "ro-testRoAnnotate")
        rofile = rodir+"/"+"subdir1/subdir1-file.txt"
        # Display annotations
        args = [ "ro", "annotations", rodir+"/"
               , "-v"
               ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
        outtxt = self.outstr.getvalue()
        assert status == 0, "Status %d, outtxt: %s"%(status,outtxt)
        log.debug("status %d, outtxt: %s"%(status, outtxt))
        self.assertEqual(outtxt.count("ro annotations"), 1)
        #self.assertRegexpMatches(outtxt, "((name))")
        self.assertRegexpMatches(outtxt, "title.*RO test annotation")
        self.assertRegexpMatches(outtxt, "created.*\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d")
        self.assertRegexpMatches(outtxt, "description.*RO test annotation")
        self.assertRegexpMatches(outtxt, "rdf:type.*<%s>"%(RO.ResearchObject))
        self.assertRegexpMatches(outtxt, "dcterms:identifier.*ro-testRoAnnotate")
        self.assertRegexpMatches(outtxt, "dcterms:creator.*Test User")
        self.deleteTestRo(rodir)
        return

    def testAnnotationDisplayFile(self):
        # Construct annotated RO
        rodir = self.createTestRo(testbase, "data/ro-test-1", "RO test annotation", "ro-testRoAnnotate")
        rofile = rodir+"/"+"subdir1/subdir1-file.txt"
        annotations = (
            [ {"atypename": "type",        "avalue":"atype",    "atypeuri":DCTERMS.type,        "aexpect":"atype" }
            , {"atypename": "title",       "avalue":"atitle",   "atypeuri":DCTERMS.title,       "aexpect":"atitle" }
            ])
        self.annotateMultiple(rodir, rofile, annotations)
        # Display annotations
        args = [ "ro", "annotations", rofile
               , "-v"
               ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
        outtxt = self.outstr.getvalue()
        assert status == 0, outtxt
        log.debug("outtxt: %s"%(outtxt))
        self.assertEqual(outtxt.count("ro annotations"), 1)
        self.assertRegexpMatches(outtxt, "\n<subdir1/subdir1-file.txt>")
        self.assertRegexpMatches(outtxt, "type.*atype")
        self.assertRegexpMatches(outtxt, "title.*atitle")
        self.deleteTestRo(rodir)
        return

    # Test annotate with graph
    def testAnnotateWithGraph(self):
        rodir  = self.createTestRo(testbase, "data/ro-test-1", "RO test annotation", "ro-testRoAnnotate")
        rofile = rodir+"/"+"subdir1/subdir1-file.txt"
        define_annotations = (
            [ {"atypename": "type",        "avalue":"atype",    "atypeuri":DCTERMS.type,        "aexpect":"atype" }
            , {"atypename": "keywords",    "avalue":"asubj",    "atypeuri":DCTERMS.subject,     "aexpect":"asubj" }
            , {"atypename": "description", "avalue":"adesc",    "atypeuri":DCTERMS.description, "aexpect":"adesc" }
            , {"atypename": "format",      "avalue":"aformat",  "atypeuri":DCTERMS.format,      "aexpect":"aformat" }
            , {"atypename": "title",       "avalue":"atitle",   "atypeuri":DCTERMS.title,       "aexpect":"atitle" }
            , {"atypename": "created",     "avalue":"acreated", "atypeuri":DCTERMS.created,     "aexpect":"acreated" }
            ])
        # Create annotation graph file and apply annotations
        annotation_graph = rdflib.Graph()
        resourceuri = ro_manifest.getComponentUri(rodir, "subdir1/subdir1-file.txt")
        for ann in define_annotations:
            annotation_graph.add( (resourceuri, ann["atypeuri"], rdflib.Literal(ann["aexpect"])) )
        annotation_graph_filename = os.path.join(os.path.abspath(rodir), "annotate-subdir1-file.txt.rdf")
        annotation_graph.serialize(annotation_graph_filename,
            format='xml', base=ro_manifest.getRoUri(rodir), xml_base="")
        args = ["ro", "annotate", rofile, "-g", annotation_graph_filename ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
        outtxt = self.outstr.getvalue()
        assert status == 0, outtxt
        # Read manifest and check for annotation
        annotations = ro_annotation._getFileAnnotations(rodir, "subdir1/subdir1-file.txt")
        expected_annotations = (
            [ (resourceuri, a["atypeuri"], rdflib.Literal(a["aexpect"]))
                for a in define_annotations
            ])
        count = 0
        for next in list(annotations):
            log.debug("- next %s"%(str(next[0])) )
            log.debug("       - (%s, %s)"%(str(next[1]),str(next[2])) )
            if next in expected_annotations:
                count += 1
            else:
                self.assertTrue(False, "Not expected (%d) %s"%(count, repr(next)))
        self.assertEqual(count,6)
        # Clean up
        self.deleteTestRo(rodir)
        return

    # Test annotate with non-existent graph (make nsure it doesn't all fall over)
    def testAnnotateWithNotExistentGraph(self):
        rodir  = self.createTestRo(testbase, "data/ro-test-1", "RO test annotation", "ro-testRoAnnotate")
        rofile = rodir+"/"+"subdir1/subdir1-file.txt"
        # Apply non-exietent graph annotation
        annotation_graph_filename = os.path.join(os.path.abspath(rodir), "annotate-none.rdf")
        rouri = ro_manifest.getRoUri(rodir)
        args = ["ro", "annotate", rodir+"/", "-g", annotation_graph_filename ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
        outtxt = self.outstr.getvalue()
        assert status == 0, outtxt
        # Read manifest and check for annotation
        annotations = ro_annotation.getAllAnnotations(rodir)
        expected_annotations = (
            [ ( rouri, DCTERMS.identifier,  rdflib.Literal('ro-testRoAnnotate')  )
            , ( rouri, DCTERMS.description, rdflib.Literal('RO test annotation') )
            , ( rouri, DCTERMS.title,       rdflib.Literal('RO test annotation') )
            , ( rouri, DCTERMS.creator,     rdflib.Literal('Test User') )
            , ( rouri, RDF.type,            RO.ResearchObject )
            ])
        count = 0
        for next in list(annotations):
            if ( # not isinstance(next[2], rdflib.BNode) and
                 not next[1] in [ORE.aggregates, DCTERMS.created] and
                 not next[1] == DCTERMS.created ):
                log.debug("- next %s"%(str(next[0])) )
                log.debug("       - (%s, %s)"%(str(next[1]),str(next[2])) )
                if next in expected_annotations:
                    count += 1
                else:
                    self.assertTrue(False, "Not expected (%d) %s"%(count, repr(next)))
        self.assertEqual(count,5)
        # Clean up
        self.deleteTestRo(rodir)
        return

    # Test annotation with wildcard pattern
    def testAnnotateWildcardPattern1(self):
        rodir  = self.createTestRo(testbase, "data/ro-test-1", "RO test annotation", "ro-testRoAnnotate")
        self.populateTestRo(testbase, rodir)
        # Apply annotation to filename pattern
        rouri = ro_manifest.getRoUri(rodir)
        args = ["ro", "annotate"
               ,"-d", rodir+"/"
               , "-w", "subdir./.*\\.txt$"
               , "dcterms:description", "pattern annotation" ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
        outtxt = self.outstr.getvalue()
        assert status == 0, outtxt
        # Read manifest and check for annotation
        annotations = ro_annotation.getAllAnnotations(rodir)
        resource1uri = ro_manifest.getComponentUriAbs(rodir, "subdir1/subdir1-file.txt")
        resource2uri = ro_manifest.getComponentUriAbs(rodir, "subdir2/subdir2-file.txt")
        expected_annotations = (
            [ ( rouri, DCTERMS.identifier,  rdflib.Literal('ro-testRoAnnotate')  )
            , ( rouri, DCTERMS.description, rdflib.Literal('RO test annotation') )
            , ( rouri, DCTERMS.title,       rdflib.Literal('RO test annotation') )
            , ( rouri, DCTERMS.creator,     rdflib.Literal('Test User') )
            , ( rouri, RDF.type,            RO.ResearchObject )
            , ( resource1uri, DCTERMS.description, rdflib.Literal('pattern annotation') )
            , ( resource2uri, DCTERMS.description, rdflib.Literal('pattern annotation') )
            ])
        count = 0
        for next in list(annotations):
            if ( not isinstance(next[2], rdflib.BNode) and
                 not next[1] in [ORE.aggregates, DCTERMS.created] ):
                log.debug("- next %s"%(str(next[0])) )
                log.debug("       - (%s, %s)"%(str(next[1]),str(next[2])) )
                if next in expected_annotations:
                    count += 1
                else:
                    self.assertTrue(False, "Not expected (%d) %s"%(count, repr(next)))
        self.assertEqual(count,7)
        # Clean up
        #self.deleteTestRo(rodir)
        return

    # Test annotation with wildcard pattern
    def testAnnotateWildcardPattern2(self):
        """
        Same as previous test, but includes filenames with spaces and hashes
        """
        rodir  = self.createTestRo(testbase, "data/ro-test-1", "RO test annotation", "ro-testRoAnnotate")
        self.populateTestRo(testbase, rodir)
        # Apply annotation to filename pattern
        rouri = ro_manifest.getRoUri(rodir)
        args = ["ro", "annotate"
               ,"-d", rodir+"/"
               , "-w", "\\.txt$"
               , "dcterms:description", "pattern annotation" ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
        outtxt = self.outstr.getvalue()
        assert status == 0, outtxt
        # Read manifest and check for annotation
        annotations = ro_annotation.getAllAnnotations(rodir)
        res_spc_uri = ro_manifest.getComponentUriAbs(rodir, "filename%20with%20spaces.txt")
        res_hsh_uri = ro_manifest.getComponentUriAbs(rodir, "filename%23with%23hashes.txt")
        resource1uri = ro_manifest.getComponentUriAbs(rodir, "subdir1/subdir1-file.txt")
        resource2uri = ro_manifest.getComponentUriAbs(rodir, "subdir2/subdir2-file.txt")
        expected_annotations = (
            [ ( rouri, DCTERMS.identifier,  rdflib.Literal('ro-testRoAnnotate')  )
            , ( rouri, DCTERMS.description, rdflib.Literal('RO test annotation') )
            , ( rouri, DCTERMS.title,       rdflib.Literal('RO test annotation') )
            , ( rouri, DCTERMS.creator,     rdflib.Literal('Test User') )
            , ( rouri, RDF.type,            RO.ResearchObject )
            , ( res_spc_uri,  DCTERMS.description, rdflib.Literal('pattern annotation') )
            , ( res_hsh_uri,  DCTERMS.description, rdflib.Literal('pattern annotation') )
            , ( resource1uri, DCTERMS.description, rdflib.Literal('pattern annotation') )
            , ( resource2uri, DCTERMS.description, rdflib.Literal('pattern annotation') )
            ])
        count = 0
        for next in list(annotations):
            if ( not isinstance(next[2], rdflib.BNode) and
                 not next[1] in [ORE.aggregates, DCTERMS.created] ):
                log.debug("- next %s"%(str(next[0])) )
                log.debug("       - (%s, %s)"%(str(next[1]),str(next[2])) )
                if next in expected_annotations:
                    count += 1
                else:
                    self.assertTrue(False, "Not expected (%d) %s"%(count, repr(next)))
        self.assertEqual(count,9)
        # Clean up
        #self.deleteTestRo(rodir)
        return

    # Test display of annotations for entire RO

    # @@TODO: Test annotations shown in RO listing

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
            , "testAnnotate"
            , "testAnnotateType"
            , "testAnnotateKeywords"
            , "testAnnotateDescription"
            , "testAnnotateCreated"
            , "testAnnotateTypeUri"
            , "testAnnotateTypeCurie"
            , "testAnnotateMultiple"
            , "testAnnotateFileWithEscapes"
            , "testAnnotationDisplayRo"
            , "testAnnotationDisplayFile"
            , "testAnnotateWithGraph"
            , "testAnnotateWithNotExistentGraph"
            , "testAnnotateWildcardPattern1"
            , "testAnnotateWildcardPattern2"
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
    return TestUtils.getTestSuite(TestAnnotations, testdict, select=select)

if __name__ == "__main__":
    TestUtils.runTests("TestAnnotations.log", getTestSuite, sys.argv)

# End.
