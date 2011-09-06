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
        self.assertEqual(filetitle, "subdir1-file title")
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
            , "testAnnotate"
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
