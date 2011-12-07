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

from rocommand import ro
from rocommand import ro_utils
from rocommand import ro_manifest
from rocommand import ro_annotation
from rocommand.ro_manifest import DCTERMS, ROTERMS

from TestConfig import ro_test_config
from StdoutContext import SwitchStdout

import TestROSupport

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

    def testCreateSimpleAnnotationBody(self):
        """
        Test function to create simple annotation body
        """
        roconfig = {
            "annotationTypes": ro_annotation.annotationTypes
            }   # @@TODO: add needed fields
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
            roconfig, rodir, roresource, attrdict)
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
            , "testCreateSimpleAnnotationBody"
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
