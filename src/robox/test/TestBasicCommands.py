#!/usr/bin/python

"""
Module to test basic RO manager commands
"""

import os, os.path
import sys
import re
import unittest
import logging
try:
    # Running Python 2.5 with simplejson?
    import simplejson as json
except ImportError:
    import json

# Add main project directory to python path
sys.path.append("../..")
sys.path.append("..")

from MiscLib import TestUtils

import ro

class TestBasicCommands(unittest.TestCase):
    """
    Test basic ro commands
    """
    def setUp(self):
        super(TestBasicCommands, self).setUp()
        return

    def tearDown(self):
        super(TestBasicCommands, self).tearDown()
        return

    # Actual tests follow

    def testNull(self):
        assert True, 'Null test failed'

    def testHelpVersion(self):
        status = ro.runCommand("config", "robase", ["ro", "--version"])
        assert status == 0
        return

    def testHelpOptions(self):
        status = ro.runCommand("config", "robase", ["ro", "--help"])
        assert status == 0
        return

    def testHelpCommands(self):
        status = ro.runCommand("config", "robase", ["ro", "help"])
        assert status == 0
        return

    def testInvalidCommand(self):
        status = ro.runCommand("config", "robase", ["ro", "nosuchcommand"])
        assert status == 2
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
            #, "testHelpVersion"
            #, "testHelpOptions"
            , "testHelpCommands"
            , "testInvalidCommand"
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
    return TestUtils.getTestSuite(TestBasicCommands, testdict, select=select)

if __name__ == "__main__":
    TestUtils.runTests("TestBasicCommands.log", getTestSuite, sys.argv)

# End.
