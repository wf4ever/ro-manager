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
import ro_manifest

from TestConfig import ro_test_config

class TestBasicCommands(unittest.TestCase):
    """
    Test basic ro commands
    """
    def setUp(self):
        super(TestBasicCommands, self).setUp()
        self.save_cwd = os.getcwd()
        return

    def tearDown(self):
        super(TestBasicCommands, self).tearDown()
        os.chdir(self.save_cwd)
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

    def testConfigVerbose(self):
        """
        $ ro config -v \
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
            "ro", "config", "-v",
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

    def createRoFixture(self, src, robase, roname):
        """
        Create test fixture research object
        
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
        self.assertEqual(manifest['rodescription'], roname,  "RO name")
        self.assertEqual(manifest['roname'],        roname,  "RO name")
        self.assertEqual(manifest['rocreator'],     ro_test_config.ROBOXUSERNAME, "RO creator")
        # See: http://stackoverflow.com/questions/969285/
        #      how-do-i-translate-a-iso-8601-datetime-string-into-a-python-datetime-object
        rocreated = datetime.datetime.strptime(manifest['rocreated'], "%Y-%m-%dT%H:%M:%S")
        timenow   = datetime.datetime.now().replace(microsecond=0)
        rodelta   = timenow-rocreated
        self.assertTrue(rodelta.total_seconds()<=1.0, 
            "Unexpected created datetime: %s, expected about %s"%
                (manifest['rocreated'],timenow.isoformat()))
        return

    def deleteRoFixture(self, rodir):
        """
        Delete test fixture research object
        """
        shutil.rmtree(rodir, ignore_errors=True)
        return

    def testCreate(self):
        """
        Create a new Research Object.

        ro create RO-name [ -d dir ] [ -i RO-ident ]
        """
        rodir = self.createRoFixture("data/ro-test-1", ro_test_config.ROBASEDIR, "ro-testCreate")
        args = [
            "ro", "create", "Test Create RO",
            "-v", 
            "-d", rodir,
            "-i", "RO-id-testCreate",
            ]
        status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
        assert status == 0
        self.checkRoFixtureManifest(rodir)
        self.checkManifestContent(rodir, "Test Create RO", "RO-id-testCreate")
        self.deleteRoFixture(rodir)
        return

    def testCreateDefaults(self):
        """
        Create a new Research Object with default options

        ro create RO-name [ -d dir ] [ -i RO-ident ]
        """
        rodir = self.createRoFixture("data/ro-test-1", ro_test_config.ROBASEDIR, "ro-testCreateDefaults")
        args = [
            "ro", "create", "Test Create RO_+_defaults",
            "-v"
            ]
        save_cwd = os.getcwd()
        configbase = os.path.abspath(ro_test_config.CONFIGDIR)
        os.chdir(rodir)
        status = ro.runCommand(configbase, ro_test_config.ROBASEDIR, args)
        os.chdir(save_cwd)
        assert status == 0
        self.checkRoFixtureManifest(rodir)
        self.deleteRoFixture(rodir)
        return

    def testCreateBadDir(self):
        """
        Create a new Research Object with directory not in configured area

        ro create RO-name [ -d dir ] [ -i RO-ident ]
        """
        rodir = self.createRoFixture("data/ro-test-1", ro_test_config.NOBASEDIR, "ro-testCreateBadDir")
        args = [
            "ro", "create", "Test Create RO bad directory",
            "-d", rodir,
            "-v"
            ]
        status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
        self.assertTrue(status == 1, "Expected failure due to bad RO directory");
        manifestdir = rodir+"/"+ro_test_config.ROMANIFESTDIR
        self.assertFalse(os.path.exists(manifestdir), msg="checking created RO manifest dir")
        self.deleteRoFixture(rodir)
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
            , "testConfigVerbose"
            , "testCreate"
            , "testCreateDefaults"
            , "testCreateBadDir",
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
