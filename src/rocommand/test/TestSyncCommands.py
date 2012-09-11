#!/usr/bin/python

"""
Module to test ROSRS synchronization RO manager commands

See: http://www.wf4ever-project.org/wiki/display/docs/RO+management+tool
"""

import sys
import os.path
import filecmp
import logging
import random
import string
try:
    # Running Python 2.5 with simplejson?
    import simplejson as json
except ImportError:
    import json
    
from os import remove, path

log = logging.getLogger(__name__)

if __name__ == "__main__":
    # Add main project directory and ro manager directories at start of python path
    sys.path.insert(0, "../..")
    sys.path.insert(0, "..")

from MiscLib import TestUtils
from sync.RosrsApi import RosrsApi
from sync.ResourceSync import ResourceSync

from rocommand import ro, ro_command
from TestConfig import ro_test_config
from StdoutContext import SwitchStdout

import TestROSupport

# Base directory for RO tests in this module
testbase = os.path.dirname(os.path.abspath(__file__))

class TestSyncCommands(TestROSupport.TestROSupport):
    """
    Test sync ro commands
    """
    
    def setUp(self):
        super(TestSyncCommands, self).setUp()
        return

    def tearDown(self):
        super(TestSyncCommands, self).tearDown()
        return

    # Actual tests follow

    def testNull(self):
        assert True, 'Null test failed'

    def testPush(self):
        """
        Push a Research Object to ROSRS.

        ro push [ -d <dir> ] [ -f ] [ -r <rosrs_uri> ] [ -t <access_token> ]
        """
        rodir = self.createTestRo(testbase, "data/ro-test-1", "RO test ro push", "ro-testRoPush")
        args = [
            "ro", "push",
            "-d", rodir,
            "-r", "http://sandbox.wf4ever-project.org/rodl/ROs/",
            "-t", "7d5423c-b507-4e1c-8",
            "-v"
            ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
        assert status == 0
        self.assertEqual(self.outstr.getvalue().count("Updated:"), 1)
        self.assertEqual(self.outstr.getvalue().count("Deleted:"), 0)
        # Clean up
        self.deleteTestRo(rodir)
        return

    def testCheckout(self):
        """
        Checkout a Research Object from ROSRS.

        ro checkout [ <RO-identifier> ] [ -d <dir> ] [ -r <rosrs_uri> ] [ -t <access_token> ]
        """
        # push an RO
        args = [
            "ro", "push",
            "-d", self.rodir,
            "-r", "http://sandbox.wf4ever-project.org/rodl/ROs/",
            "-t", "7d5423c-b507-4e1c-8"
            ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
        assert status == 0
        
        # check it out as a copy
        rodir2 = os.path.join(ro_test_config.ROBASEDIR, "RO_test_checkout_copy")
        os.rename(self.rodir, rodir2)
        args = [
            "ro", "checkout", self.ident1,
            "-d", ro_test_config.ROBASEDIR,
            "-v"
            ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
        assert status == 0
        self.assertEqual(self.outstr.getvalue().count("ro checkout"), 1)
        for f in self.files:
            self.assertEqual(self.outstr.getvalue().count(f), 1)
        self.assertEqual(self.outstr.getvalue().count("%d files checked out" % len(self.files)), 1)
        
        # compare they're identical, with the exception of registries.pickle
        cmpres = filecmp.dircmp(rodir2, self.rodir)
        self.assertEquals(cmpres.left_only, [ResourceSync.REGISTRIES_FILE])
        self.assertEquals(cmpres.right_only, [])
        self.assertListEqual(cmpres.diff_files, [], "Files should be the same (manifest is ignored)")

        # delete the checked out copy
        self.deleteTestRo(rodir2)
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
            ],
        "component":
            [ "testComponents"
            , "testPush"
            , "testCheckout"
            ],
        "integration":
            [ "testIntegration"
            ],
        "pending":
            [ "testPending"
            ]
        }
    return TestUtils.getTestSuite(TestSyncCommands, testdict, select=select)

if __name__ == "__main__":
    TestUtils.runTests("TestSyncCommands.log", getTestSuite, sys.argv)

# End.
