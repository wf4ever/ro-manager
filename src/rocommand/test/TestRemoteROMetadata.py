#!/usr/bin/python

"""
Module to test remote RO metadata handling class
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
import uuid

from MiscLib import TestUtils

from rocommand import ro_settings
from rocommand import ro_metadata
from rocommand import ro_remote_metadata
from rocommand.HTTPSession import HTTP_Session
from rocommand.ro_namespaces import RDF, RO, ORE, DCTERMS, ROTERMS
from rocommand.ro_annotation import annotationTypes

from TestConfig import ro_test_config
from StdoutContext import SwitchStdout

import TestROSupport

# Base directory for RO tests in this module
testbase = os.path.dirname(__file__)

# Local ro_config for testing
ro_config = {
    "annotationTypes": annotationTypes
    }

cwd        = os.getcwd()
robase     = ro_test_config.ROBASEDIR
robase_abs = os.path.abspath(ro_test_config.ROBASEDIR)

class TestRemoteROMetadata(TestROSupport.TestROSupport):
    """
    Test ro metadata handling
    """
    def setUp(self):
        super(TestRemoteROMetadata, self).setUp()
        self.remoteRo = None
        return

    def tearDown(self):
        super(TestRemoteROMetadata, self).tearDown()
        if self.remoteRo:
            self.remoteRo.delete()
        return

    # Actual tests follow

    def testNull(self):
        assert True, 'Null test failed'
        
    def testCreateRo(self):
        httpsession = HTTP_Session(ro_test_config.ROSRS_URI, ro_test_config.ROSRS_ACCESS_TOKEN)
        roid = "romanagertest-" + str(uuid.uuid4())      
        self.remoteRo = ro_remote_metadata.ro_remote_metadata(ro_config, httpsession, roid = roid)
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
            , "testCreateRo"
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
    return TestUtils.getTestSuite(TestRemoteROMetadata, testdict, select=select)

if __name__ == "__main__":
    TestUtils.runTests("TestROMetadata.log", getTestSuite, sys.argv)

# End.
