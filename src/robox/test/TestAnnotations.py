#!/usr/bin/python

"""
Module to test basic RO manager commands

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
import rdflib

log = logging.getLogger(__name__)

if __name__ == "__main__":
    # Add main project directory and ro manager directories to python path
    sys.path.append("../..")
    sys.path.append("..")

from MiscLib import TestUtils

import ro
import ro_utils
import ro_manifest
from ro_manifest import DCTERMS

from TestConfig import ro_test_config
from StdoutContext import SwitchStdout

import TestROSupport

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
        rodir = self.createTestRo("data/ro-test-1", "RO test annotation", "ro-testRoAnnotate")
        args = [
            "ro", "annotate", rodir+"/"+"subdir1/subdir1-file.txt", "title", "subdir1-file title",
            "-v",
            ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
        outtxt = self.outstr.getvalue()
        assert status == 0, outtxt
        self.assertEqual(outtxt.count("ro annotate"), 1)
        #self.assertRegexpMatches(outtxt, "annotation.*dc:title")
        # Read manifest and check for annotation
        manifestgraph = ro_manifest.readManifestGraph(rodir)
        filesubj  = ro_manifest.getComponentUri(rodir, "subdir1/subdir1-file.txt")
        log.debug("filesubj %s"%filesubj)
        filetitle = manifestgraph.value(filesubj, DCTERMS.title, None),
        self.assertEqual(len(filetitle), 1, "Singleton result expected")
        self.assertEqual(filetitle[0], "subdir1-file title")
        self.deleteTestRo(rodir)
        return

    def annotationTest(self, anntype, annvalue, anntypeuri, annexpect):
        rodir = self.createTestRo("data/ro-test-1", "RO test annotation", "ro-testRoAnnotate")
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
        manifestgraph = ro_manifest.readManifestGraph(rodir)
        filesubj  = ro_manifest.getComponentUri(rodir, "subdir1/subdir1-file.txt")
        fileann   = manifestgraph.value(filesubj, anntypeuri, None),
        #@@TODO: deal with case that expected result is a list
        self.assertEqual(len(fileann), 1, "Singleton result expected")
        self.assertEqual(fileann[0], annexpect)
        self.deleteTestRo(rodir)
        return

    # Other annotation types to add (cf. http://wf4ever.github.com/labs/ro-annotator/mockups/1/index.html)

    def testAnnotateType(self):
        self.annotationTest("type", "file type", DCTERMS.type, "file type")
        return

    def testAnnotateKeywords(self):
        self.annotationTest("keywords", "foo,bar", DCTERMS.subject, "foo,bar")  #@@TODO: make multiples
        return

    def testAnnotateDescription(self):
        descr = """
            Multiline
            description
            """
        self.annotationTest("description", descr, DCTERMS.description, descr)
        return

    def testAnnotateCreated(self):
        #@@TODO: use for creation date/time of file
        created = "2011-09-14T12:00:00"
        self.annotationTest("created", created, DCTERMS.created, created)
        return

    def testAnnotateTypeUri(self):
        anntypeuri = rdflib.URIRef("http://example.org/annotationtype")
        annvalue   = "Annotation value"
        self.annotationTest(anntypeuri, annvalue, anntypeuri, annvalue)
        return

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
        rodir  = self.createTestRo("data/ro-test-1", "RO test annotation", "ro-testRoAnnotate")
        rofile = rodir+"/"+"subdir1/subdir1-file.txt"
        annotations = (
            [ {"atypename": "type",        "avalue":"atype",    "atypeuri":DCTERMS.type,        "aexpect":"atype" }
            , {"atypename": "keywords",    "avalue":"asubj",    "atypeuri":DCTERMS.subject,     "aexpect":"asubj" }
            , {"atypename": "description", "avalue":"adesc",    "atypeuri":DCTERMS.description, "aexpect":"adesc" }
            , {"atypename": "format",      "avalue":"aformat",  "atypeuri":DCTERMS.format,      "aexpect":"aformat" }
            , {"atypename": "title",       "avalue":"atitle",   "atypeuri":DCTERMS.title,       "aexpect":"atitle" }
            , {"atypename": "created",     "avalue":"acreated", "atypeuri":DCTERMS.created,     "aexpect":"acreated" }
            #, {"atypename": ..., "avalue":..., "atypeuri":..., "aexpect":... }
            #, {"atypename": ..., "avalue":..., "atypeuri":..., "aexpect":... }
            ])
        self.annotateMultiple(rodir, rofile, annotations)
        # Read manifest and check for annotation
        manifestgraph = ro_manifest.readManifestGraph(rodir)
        filesubj  = ro_manifest.getComponentUri(rodir, "subdir1/subdir1-file.txt")
        for a in annotations:
            fileann   = manifestgraph.value(filesubj, a["atypeuri"], None),
            self.assertEqual(len(fileann), 1, "Singleton result expected")
            self.assertEqual(fileann[0], a["aexpect"])
        self.deleteTestRo(rodir)
        return

    # Test annotation display
    def testAnnotationDisplay(self):
        # Construct annotated RO
        rodir = self.createTestRo("data/ro-test-1", "RO test annotation", "ro-testRoAnnotate")
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
        self.assertEqual(outtxt.count("ro annotations"), 1)
        self.assertRegexpMatches(outtxt, "subdir1/subdir1-file.txt")
        self.assertRegexpMatches(outtxt, "type:.*atype")
        self.assertRegexpMatches(outtxt, "title:.*atitle")
        self.deleteTestRo(rodir)
        return

    # Test display of annotations for entire RO

    
    # @@TODO: Test annotations shown in RO listing

    # @@TODO: Test interactive/multiline update (how?)
    
    # @@TODO: Test use of CURIE as type
    
    # @@TODO: Test use of URI as type

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
            , "testAnnotateMultiple"
            , "testAnnotationDisplay"
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
