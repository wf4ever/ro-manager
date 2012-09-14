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
from rocommand.ro_namespaces import RDF, DCTERMS, RO, AO, ORE

from TestConfig import ro_test_config
from StdoutContext import SwitchStdout

import TestROSupport

# Base directory for RO tests in this module
testbase = os.path.dirname(os.path.abspath(__file__))

# Local ro_config for testing
ro_config = {
    "annotationTypes": ro_annotation.annotationTypes
    }

def LIT(l): return rdflib.Literal(l)
def REF(u): return rdflib.URIRef(u)

class TestLinks(TestROSupport.TestROSupport):
    """
    Test ro annotation commands
    """
    def setUp(self):
        super(TestLinks, self).setUp()
        return

    def tearDown(self):
        super(TestLinks, self).tearDown()
        return

    # Actual tests follow

    def testNull(self):
        assert True, 'Null test failed'

    def testLink(self):
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

    def linkTest(self, anntype, annvalue, anntypeuri, annexpect):
        rodir = self.createTestRo(testbase, "data/ro-test-1", "RO test annotation", "ro-testRoAnnotate")
        args = [
            "ro", "link", rodir+"/"+"subdir1/subdir1-file.txt", anntype, annvalue,
            "-v",
            ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
        outtxt = self.outstr.getvalue()
        assert status == 0, outtxt
        self.assertEqual(outtxt.count("ro link"), 1)
        # Read manifest and check for annotation
        annotations = ro_annotation._getFileAnnotations(rodir, "subdir1/subdir1-file.txt")
        resourceuri = ro_manifest.getComponentUri(rodir, "subdir1/subdir1-file.txt")
        expected_annotations = (
            [ (resourceuri, anntypeuri, annexpect)
            ])
        count = 0
        for next in list(annotations):
            log.debug("- next %s"%(str(next[0])) )
            log.debug("       - (%s, %s)"%(str(next[1]),str(next[2])) )
            if next in expected_annotations:
                count += 1
            else:
                self.assertTrue(False, "Not expected (%d) %s"%(count, repr(next)))
        self.assertEqual(count,1)
        self.deleteTestRo(rodir)
        return

    # Other annotation types to add (cf. http://wf4ever.github.com/labs/ro-annotator/mockups/1/index.html)

    def testLinkType(self):
        self.linkTest("type", "file type", DCTERMS.type, LIT("file type"))
        return

    def testLinkCreated(self):
        created = "2011-09-14T12:00:00"
        self.linkTest("created", created, DCTERMS.created, LIT(created))
        return

    def testLinkRdfType(self):
        typeref = "http://example.com/type"
        self.linkTest("rdf:type", typeref, RDF.type, REF(typeref))
        return

    def testLinkUnknownUri(self):
        anntypeuri = "http://example.org/unknowntype"
        annvalue   = "http://example.com/link"
        self.linkTest(anntypeuri, annvalue, REF(anntypeuri), REF(annvalue))
        return

    # Test annotate with graph
    def testLinkWithGraph(self):
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
    def testLinkWithNotExistentGraph(self):
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
            , "testLink"
            , "testLinkType"
            , "testLinkCreated"
            , "testLinkRdfType"
            , "testLinkUnknownUri"
            , "testLinkWithGraph"
            , "testLinkWithNotExistentGraph"
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
    return TestUtils.getTestSuite(TestLinks, testdict, select=select)

if __name__ == "__main__":
    TestUtils.runTests("TestLinks.log", getTestSuite, sys.argv)

# End.
