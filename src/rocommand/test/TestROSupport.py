#!/usr/bin/python

"""
Research Object manager tests support module:  provides common functions used by multiple test suites.
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

if __name__ == "__main__":
    # Add main project directory and ro manager directories to python path
    sys.path.append("../..")
    sys.path.append("..")

from MiscLib import TestUtils

import ro
import ro_utils
import ro_manifest

from TestConfig import ro_test_config
from StdoutContext import SwitchStdout

class TestROSupport(unittest.TestCase):
    """
    Test basic ro commands
    """
    def setUp(self):
        super(TestROSupport, self).setUp()
        self.save_cwd = os.getcwd()
        self.outstr = StringIO.StringIO()
        return

    def tearDown(self):
        self.outstr.close()
        super(TestROSupport, self).tearDown()
        os.chdir(self.save_cwd)
        return

    def createRoFixture(self, src, robase, roname):
        """
        Create test fixture research object - this is a set of directries
        and files that will be used as a research object, but not actually
        creating the reesearch object specific structures.
        
        Returns name of research object directory
        """
        rodir = robase+"/"+ roname
        manifestdir  = rodir+"/"+ro_test_config.ROMANIFESTDIR
        manifestfile = manifestdir+"/"+ro_test_config.ROMANIFESTFILE
        shutil.rmtree(rodir, ignore_errors=True)
        shutil.copytree(src, rodir)
        # Confirm non-existence of manifest directory
        self.assertTrue(os.path.exists(rodir), msg="checking copied RO directory")
        self.assertFalse(os.path.exists(manifestdir), msg="checking copied RO manifest dir")
        return rodir

    def checkRoFixtureManifest(self, rodir):
        """
        Test for existence of manifest in RO fixture.
        """
        manifestdir  = rodir+"/"+ro_test_config.ROMANIFESTDIR
        manifestfile = manifestdir+"/"+ro_test_config.ROMANIFESTFILE
        self.assertTrue(os.path.exists(manifestdir), msg="checking created RO manifest dir")
        self.assertTrue(os.path.exists(manifestfile), msg="checking created RO manifest file")
        return

    def checkManifestContent(self, rodir, roname, roident):
        manifest = ro_manifest.readManifest(rodir)
        self.assertEqual(manifest['roident'],       roident, "RO identifier")
        self.assertEqual(manifest['rotitle'],       roname,  "RO title")
        self.assertEqual(manifest['rocreator'],     ro_test_config.ROBOXUSERNAME, "RO creator")
        # See: http://stackoverflow.com/questions/969285/
        #      how-do-i-translate-a-iso-8601-datetime-string-into-a-python-datetime-object
        rocreated = datetime.datetime.strptime(manifest['rocreated'], "%Y-%m-%dT%H:%M:%S")
        timenow   = datetime.datetime.now().replace(microsecond=0)
        rodelta   = timenow-rocreated
        self.assertTrue(rodelta.seconds<=1, 
            "Unexpected created datetime: %s, expected about %s"%
                (manifest['rocreated'],timenow.isoformat()))
        self.assertEqual(manifest['rodescription'], roname,  "RO name")
        return

    def deleteRoFixture(self, rodir):
        """
        Delete test fixture research object
        """
        shutil.rmtree(rodir, ignore_errors=True)
        return

    def createTestRo(self, src, roname, roident):
        """
        Create test research object
        
        Returns name of research object directory
        """
        rodir = self.createRoFixture(src, ro_test_config.ROBASEDIR, ro_utils.ronametoident(roname))
        args = [
            "ro", "create", roname,
            "-v", 
            "-d", rodir,
            "-i", roident,
            ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
        assert status == 0
        return rodir

    def deleteTestRo(self, rodir):
        """
        Delete test research object
        """
        self.deleteRoFixture(rodir)
        return

    # UnitTest support from Python 2.7

    def assertRegexpMatches(self, text, expected_regexp, msg=None):
        """Fail the test unless the text matches the regular expression."""
        if isinstance(expected_regexp, basestring):
            expected_regexp = re.compile(expected_regexp)
        if not expected_regexp.search(text):
            msg = msg or "Regexp didn't match"
            msg = '%s: %r not found in %r' % (msg, expected_regexp.pattern, text)
            raise self.failureException(msg)

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
    return TestUtils.getTestSuite(TestROSupport, testdict, select=select)

if __name__ == "__main__":
    TestUtils.runTests("TestROSupport.log", getTestSuite, sys.argv)

# End.
