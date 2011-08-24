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
try:
    # Running Python 2.5 with simplejson?
    import simplejson as json
except ImportError:
    import json

# Add main project directory and ro manager directories to python path
sys.path.append("../..")
sys.path.append("..")

from MiscLib import TestUtils

import ro
import ro_utils

from TestConfig import ro_test_config

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
        status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, ["ro", "--version"])
        self.assertEqual(status, 0)
        return

    def testHelpOptions(self):
        status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, ["ro", "--help"])
        self.assertEqual(status, 0)
        return

    def testHelpCommands(self):
        status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, ["ro", "help"])
        self.assertEqual(status, 0)
        return

    def testInvalidCommand(self):
        status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, ["ro", "nosuchcommand"])
        self.assertEqual(status, 2)
        return

    def testConfig(self):
        """
        $ ro config \
          -r http://calatola.man.poznan.pl/robox/dropbox_accounts/1/ro_containers/2 \
          -p d41d8cd98f00b204e9800998ecf8427e \
          -b /usr/workspace/Dropbox/myROs \
          -n "Graham Klyne" \
          -e gk@example.org
        """
        ro_utils.resetconfig(ro_test_config.CONFIGDIR)
        config = ro_utils.readconfig(ro_test_config.CONFIGDIR)
        self.assertEqual(config["robase"],    None)
        self.assertEqual(config["roboxuri"],  None)
        self.assertEqual(config["roboxpass"], None)
        self.assertEqual(config["username"],  None)
        self.assertEqual(config["useremail"], None)
        args = [
            "ro", "config",
            "-b", ro_test_config.ROBASEDIR,
            "-r", ro_test_config.ROBOXURI,
            "-n", ro_test_config.ROBOXUSERNAME,
            "-p", ro_test_config.ROBOXPASSWORD,
            "-e", ro_test_config.ROBOXEMAIL
            ]
        status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
        assert status == 0
        config = ro_utils.readconfig(ro_test_config.CONFIGDIR)
        self.assertEqual(config["robase"],    os.path.abspath(ro_test_config.ROBASEDIR))
        self.assertEqual(config["roboxuri"],  ro_test_config.ROBOXURI)
        self.assertEqual(config["roboxpass"], ro_test_config.ROBOXPASSWORD)
        self.assertEqual(config["username"],  ro_test_config.ROBOXUSERNAME)
        self.assertEqual(config["useremail"], ro_test_config.ROBOXEMAIL)
        return

    def testCreate(self):
        """
        Create a new Research Object.

        ro create RO-name [ -d dir ] [ -i RO-ident ]
        """
        # Create directory tree for test
        rodir = ro_test_config.ROBASEDIR+"/ro-testCreate"
        manifestdir  = rodir+"/"+ro_test_config.ROMANIFESTDIR
        manifestfile = manifestdir+"/"+ro_test_config.ROMANIFESTFILE
        shutil.rmtree(rodir, ignore_errors=True)
        shutil.copytree("data/ro-test-1", rodir)
        # Confirm non-existence of manifest
        self.assertTrue(os.path.exists(rodir), msg="checking copied RO directory")
        self.assertFalse(os.path.exists(manifestdir), msg="checking copied RO manifest dir")
        # Run command
        args = [
            "ro", "create", "Test Create RO"
            "-d", rodir,
            "-i", "RO-id-testCreate",
            ]
        status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
        assert status == 0
        # Confirm existence of manifest directory and file
        self.assertTrue(os.path.exists(manifestdir), msg="checking created RO manifest dir")
        self.assertTrue(os.path.exists(manifestfile), msg="checking created RO manifest file")
        # Remove test RO directory
        shutil.rmtree(rodir, ignore_errors=True)
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
            , "testConfig"
            , "testCreate"
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
