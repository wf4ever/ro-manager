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

import rdflib

from MiscLib import TestUtils

from rocommand import ro, ro_utils, ro_manifest

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

    def getConfigDir(self, testbase):
        return os.path.join(testbase, ro_test_config.CONFIGDIR)

    def getRoBaseDir(self, testbase):
        return os.path.join(testbase, ro_test_config.ROBASEDIR)

    def setupTestBaseConfig(self, testbase):
        """
        Test helper creates RO config for designated test base directory
        and returns configuration and base RO storage directories. 
        """
        # @@refactor to use method from rocommand
        configdir = self.getConfigDir(testbase)
        robasedir = self.getRoBaseDir(testbase)
        ro_utils.resetconfig(configdir)
        args = [
            "ro", "config",
            "-b", robasedir,
            "-r", ro_test_config.ROSRS_URI,
            "-t", ro_test_config.ROSRS_ACCESS_TOKEN,
            "-n", ro_test_config.ROBOXUSERNAME,
            "-e", ro_test_config.ROBOXEMAIL
            ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(configdir, robasedir, args)
            assert status == 0
        self.assertEqual(self.outstr.getvalue().count("ro config"), 0)
        return (configdir, robasedir)

    def createRoFixture(self, testbase, src, robase, roname):
        """
        Create test fixture research object - this is a set of directories
        and files that will be used as a research object, but not actually
        creating the research object specific structures.
        
        Returns name of research object directory
        """
        if testbase != "" and not testbase.endswith("/"): testbase += "/"
        rodir = testbase + robase + "/" + roname
        manifestdir  = rodir+"/"+ro_test_config.ROMANIFESTDIR
        manifestfile = manifestdir+"/"+ro_test_config.ROMANIFESTFILE
        shutil.rmtree(rodir, ignore_errors=True)
        shutil.copytree(testbase+src, rodir)
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

    def checkManifestGraph(self, rodir, rograph):
        """
        Check manifest file contains all statements from supplied graph
        """
        m_graph = ro_manifest.readManifestGraph(rodir)
        for (s,p,o) in rograph:
            if isinstance(s, rdflib.BNode): s = None 
            if isinstance(o, rdflib.BNode): o = None
            self.assertIn((s,p,o), m_graph, "Not found in manifest: "+repr((s, p, o)))
        return

    def checkManifestGraphOmits(self, rodir, rograph):
        """
        Check manifest file contains all statements from supplied graph
        """
        m_graph = ro_manifest.readManifestGraph(rodir)
        for (s,p,o) in rograph:
            if isinstance(s, rdflib.BNode): s = None 
            if isinstance(o, rdflib.BNode): o = None
            self.assertNotIn((s,p,o), m_graph, "Unexpected in manifest: "+repr((s, p, o)))
        return

    def checkTargetGraph(self, targetgraph, expectgraph, msg="Not found in target graph"):
        """
        Check target graph contains all statements from supplied graph
        """
        for (s,p,o) in expectgraph:
            if isinstance(s, rdflib.BNode): s = None 
            if isinstance(o, rdflib.BNode): o = None
            self.assertIn((s,p,o), targetgraph, msg+": "+repr((s, p, o)))
        return

    def deleteRoFixture(self, rodir):
        """
        Delete test fixture research object
        """
        shutil.rmtree(rodir, ignore_errors=True)
        return

    def createTestRo(self, testbase, src, roname, roident):
        """
        Create test research object
        
        Returns name of research object directory
        """
        rodir = self.createRoFixture(testbase, src, ro_test_config.ROBASEDIR, ro_utils.ronametoident(roname))
        args = [
            "ro", "create", roname,
            "-d", rodir,
            "-i", roident,
            ]
        with SwitchStdout(self.outstr):
            configdir = self.getConfigDir(testbase)
            robasedir = self.getRoBaseDir(testbase)
            status = ro.runCommand(configdir, robasedir, args)
        outtxt = self.outstr.getvalue()
        assert status == 0, outtxt
        self.outstr = StringIO.StringIO()
        return rodir

    def populateTestRo(self, testbase, rodir):
        """
        Create test research object
        
        Returns name of research object directory
        """
        args = [
            "ro", "add", "-a",
            "-d", rodir,
            rodir
            ]
        with SwitchStdout(self.outstr):
            configdir = self.getConfigDir(testbase)
            robasedir = self.getRoBaseDir(testbase)
            status = ro.runCommand(configdir, robasedir, args)
        outtxt = self.outstr.getvalue()
        assert status == 0, outtxt
        self.outstr = StringIO.StringIO()
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
