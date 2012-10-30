#!/usr/bin/python

"""
Module to test RO manager manifest and aggregation commands

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
    # Add main project directory at start of python path
    sys.path.insert(0, "../..")

import rdflib

from MiscLib import TestUtils

from rocommand import ro
from rocommand import ro_utils
from rocommand.ro_namespaces import RDF, DCTERMS, RO, AO, ORE
from rocommand.ro_annotation import annotationTypes
from rocommand.ro_metadata   import ro_metadata

from rocommand.test import TestROSupport
from rocommand.test import TestConfig
from rocommand.test import StdoutContext

#from TestConfig import ro_test_config
#from StdoutContext import SwitchStdout

from iaeval import ro_minim
from iaeval.ro_minim import MINIM

from iaeval import ro_eval_minim

# Local ro_config for testing
ro_config = {
    "annotationTypes": annotationTypes
    }

# Base directory for RO tests in this module
testbase = os.path.dirname(os.path.realpath(__file__))

class TestEvalChecklist(TestROSupport.TestROSupport):
    """
    Test ro checklist evaluation

    Some tests here require that the python package lpod-python is installed
      apt-get  install libxml2-dev
      apt-get  install libxslt-dev
      easy_install lxml
      pip install lpod-python
    """
    def setUp(self):
        super(TestEvalChecklist, self).setUp()
        return

    def tearDown(self):
        super(TestEvalChecklist, self).tearDown()
        return

    # Setup local config for Minim tests

    def setupConfig(self):
        return self.setupTestBaseConfig(testbase)

    # Actual tests follow

    def testNull(self):
        assert True, 'Null test failed'

    def testSetupConfig(self):
        (configdir, robasedir) = self.setupConfig()
        config = ro_utils.readconfig(configdir)
        self.assertEqual(config["robase"],          os.path.abspath(robasedir))
        self.assertEqual(config["rosrs_uri"],       TestConfig.ro_test_config.ROSRS_URI)
        self.assertEqual(config["rosrs_access_token"],  TestConfig.ro_test_config.ROSRS_ACCESS_TOKEN)
        self.assertEqual(config["username"],        TestConfig.ro_test_config.ROBOXUSERNAME)
        self.assertEqual(config["useremail"],       TestConfig.ro_test_config.ROBOXEMAIL)
        return

    def testEvalAllPresent(self):
        """
        Evaluate complete RO against Minim description 
        """
        self.setupConfig()
        rodir      = self.createTestRo(testbase, "test-data-1", "RO test minim", "ro-testMinim")
        self.populateTestRo(testbase, rodir)
        rometa = ro_metadata(ro_config, rodir)
        (g,evalresult) = ro_eval_minim.evaluate(rometa,
            "Minim-UserRequirements.rdf",               # Minim file
            "docs/UserRequirements-astro.csv",          # Target resource
            "create")                                   # Purpose
        self.assertIn(MINIM.fullySatisfies,     evalresult['summary'])
        self.assertIn(MINIM.nominallySatisfies, evalresult['summary'])
        self.assertIn(MINIM.minimallySatisfies, evalresult['summary'])
        self.assertEquals(evalresult['missingMust'],    [])
        self.assertEquals(evalresult['missingShould'],  [])
        self.assertEquals(evalresult['missingMay'],     [])
        self.assertEquals(evalresult['rouri'],          rometa.getRoUri())
        self.assertEquals(evalresult['minimuri'],       rometa.getComponentUri("Minim-UserRequirements.rdf"))
        self.assertEquals(evalresult['target'],         "docs/UserRequirements-astro.csv")
        self.assertEquals(evalresult['purpose'],        "create")
        self.assertEquals(evalresult['constrainturi'],
            rometa.getComponentUriAbs("Minim-UserRequirements.rdf#create/docs/UserRequirements-astro.csv"))
        self.assertEquals(evalresult['modeluri'],
            rometa.getComponentUriAbs("Minim-UserRequirements.rdf#runnableRequirementRO"))
        self.deleteTestRo(rodir)
        return

    def testEvalMustMissing(self):
        """
        Evaluate complete RO against Minim description 
        """
        self.setupConfig()
        rodir      = self.createTestRo(testbase, "test-data-1", "RO test minim", "ro-testMinim")
        self.populateTestRo(testbase, rodir)
        rometa = ro_metadata(ro_config, rodir)
        minimbase  = rometa.getComponentUri("Minim-UserRequirements.rdf")
        modeluri   = ro_minim.getElementUri(minimbase, "#missingMustRequirement")
        (g,evalresult) = ro_eval_minim.evaluate(rometa,
            "Minim-UserRequirements.rdf",               # Minim file
            "docs/UserRequirements-bio.csv",            # Target resource
            "create")                                   # Purpose
        missing_must = (
            { 'level': "MUST"
            , 'model': modeluri 
            , 'label': rdflib.Literal("aggregates data/UserRequirements-bio.ods")
            , 'datarule':
              { 'aggregates': rometa.getComponentUri("data/UserRequirements-bio.ods")
              , 'show':       None
              , 'showpass':   None
              , 'showfail':   None
              , 'derives':    ro_minim.getElementUri(minimbase, "#isPresent/data/UserRequirements-bio.ods")
              }
            , 'uri': ro_minim.getElementUri(minimbase, "#isPresent/data/UserRequirements-bio.ods") 
            })
        self.maxDiff=None
        self.assertEquals(evalresult['summary'],       [] )
        self.assertEquals(evalresult['missingMust'],   [(missing_must,{})] )
        self.assertEquals(evalresult['missingShould'], [] )
        self.assertEquals(evalresult['missingMay'],    [] )
        self.deleteTestRo(rodir)
        return

    def testEvalShouldMissing(self):
        """
        Evaluate complete RO against Minim description 
        """
        self.setupConfig()
        rodir      = self.createTestRo(testbase, "test-data-1", "RO test minim", "ro-testMinim")
        self.populateTestRo(testbase, rodir)
        rometa = ro_metadata(ro_config, rodir)
        minimbase  = rometa.getComponentUri("Minim-UserRequirements.rdf")
        modeluri   = ro_minim.getElementUri(minimbase, "#missingShouldRequirement")
        (g,evalresult) = ro_eval_minim.evaluate(rometa,
            "Minim-UserRequirements.rdf",               # Minim file
            "docs/UserRequirements-bio.html",           # Target resource
            "create")                                   # Purpose
        missing_should = (
            { 'level': "SHOULD"
            , 'model': modeluri 
            , 'label': rdflib.Literal("aggregates docs/missing.css")
            , 'datarule':
              { 'aggregates': rometa.getComponentUri("docs/missing.css")
              , 'show':       None
              , 'showpass':   None
              , 'showfail':   None
              , 'derives':    ro_minim.getElementUri(minimbase, "#isPresent/docs/missing.css")
              }
            , 'uri': ro_minim.getElementUri(minimbase, "#isPresent/docs/missing.css") 
            })
        self.maxDiff=None
        self.assertEquals(evalresult['summary'],       [MINIM.minimallySatisfies])
        self.assertEquals(evalresult['missingMust'],   [] )
        self.assertEquals(evalresult['missingShould'], [(missing_should,{})] )
        self.assertEquals(evalresult['missingMay'],    [] )
        self.deleteTestRo(rodir)
        return

    def testEvalMayMissing(self):
        """
        Evaluate complete RO against Minim description 
        """
        self.setupConfig()
        rodir      = self.createTestRo(testbase, "test-data-1", "RO test minim", "ro-testMinim")
        self.populateTestRo(testbase, rodir)
        rometa = ro_metadata(ro_config, rodir)
        minimbase  = rometa.getComponentUri("Minim-UserRequirements.rdf")
        modeluri   = ro_minim.getElementUri(minimbase, "#missingMayRequirement")
        (g,evalresult) = ro_eval_minim.evaluate(rometa,
            "Minim-UserRequirements.rdf",               # Minim file
            "docs/UserRequirements-bio.pdf",            # Target resource
            "create")                                   # Purpose
        missing_may = (
            { 'level': "MAY"
            , 'model': modeluri 
            , 'label': rdflib.Literal("aggregates docs/missing.css")
            , 'datarule':
              { 'aggregates': rometa.getComponentUri("docs/missing.css")
              , 'show':       None
              , 'showpass':   None
              , 'showfail':   None
              , 'derives':    ro_minim.getElementUri(minimbase, "#isPresent/docs/missing.css")
              }
            , 'uri': ro_minim.getElementUri(minimbase, "#isPresent/docs/missing.css") 
            })
        self.maxDiff=None
        self.assertEquals(evalresult['summary'],        [MINIM.nominallySatisfies, MINIM.minimallySatisfies])
        self.assertEquals(evalresult['missingMust'],    [] )
        self.assertEquals(evalresult['missingShould'],  [] )
        self.assertEquals(evalresult['missingMay'],     [(missing_may,{})] )
        self.assertEquals(evalresult['rouri'],          rometa.getRoUri())
        self.assertEquals(evalresult['minimuri'],       rometa.getComponentUri("Minim-UserRequirements.rdf"))
        self.assertEquals(evalresult['target'],         "docs/UserRequirements-bio.pdf")
        self.assertEquals(evalresult['purpose'],        "create")
        self.assertEquals(evalresult['constrainturi'],  
            rometa.getComponentUriAbs("Minim-UserRequirements.rdf#create/docs/UserRequirements-bio.pdf"))
        self.assertEquals(evalresult['modeluri'],
            rometa.getComponentUriAbs("Minim-UserRequirements.rdf#missingMayRequirement"))
        self.deleteTestRo(rodir)
        self.deleteTestRo(rodir)
        return

    def setupEvalFormat(self):
        self.setupConfig()
        rodir       = self.createTestRo(testbase, "test-data-1", "RO test minim", "ro-testMinim")
        rometa = ro_metadata(ro_config, rodir)
        minimbase  = rometa.getComponentUri("Minim-UserRequirements.rdf")
        modeluri    = ro_minim.getElementUri(minimbase, "#test-formatting-constraint")
        self.missing_must = (
            { 'level': "MUST"
            , 'model': modeluri 
            , 'label': rdflib.Literal("aggregates data/UserRequirements-bio.ods")
            , 'datarule':
              { 'aggregates': rometa.getComponentUri("data/UserRequirements-bio.ods")
              , 'show':       None
              , 'showpass':   None
              , 'showfail':   None
              , 'derives':    ro_minim.getElementUri(minimbase, "#isPresent/data/UserRequirements-bio.ods")
              }
            , 'uri': ro_minim.getElementUri(minimbase, "#isPresent/data/UserRequirements-bio.ods") 
            })
        self.missing_should = (
            { 'level': "SHOULD"
            , 'model': modeluri 
            , 'label': rdflib.Literal("aggregates docs/missing.css")
            , 'datarule':
              { 'aggregates': rometa.getComponentUri("docs/missing.css")
              , 'show':       None
              , 'showpass':   None
              , 'showfail':   None
              , 'derives':    ro_minim.getElementUri(minimbase, "#isPresent/docs/missing.css")
              }
            , 'uri': ro_minim.getElementUri(minimbase, "#isPresent/docs/missing.css") 
            })
        self.missing_may = (
            { 'level': "MAY"
            , 'model': modeluri 
            , 'label': rdflib.Literal("aggregates docs/missing.css")
            , 'datarule':
              { 'aggregates': rometa.getComponentUri("docs/missing.css")
              , 'show':       None
              , 'showpass':   None
              , 'showfail':   None
              , 'derives':    ro_minim.getElementUri(minimbase, "#isPresent/docs/missing.css")
              }
            , 'uri': ro_minim.getElementUri(minimbase, "#isPresent/docs/missing.css") 
            })
        self.eval_result = (
            { 'summary':        [MINIM.nominallySatisfies, MINIM.minimallySatisfies]
            , 'missingMust':    [(self.missing_must,   {})]
            , 'missingShould':  [(self.missing_should, {})]
            , 'missingMay':     [(self.missing_may,    {})]
            , 'satisfied':      []
            , 'rodir':          rodir
            , 'rouri':          rometa.getRoUri()
            , 'minimuri':       minimbase
            , 'target':         "test-formatting-target"
            , 'purpose':        "test formatting"
            , 'constrainturi':  rometa.getComponentUri("Minim-UserRequirements.rdf#test-formatting-constraint")
            , 'modeluri':       rometa.getComponentUri("Minim-UserRequirements.rdf#test-formatting-constraint")
            })
        self.deleteTestRo(rodir)
        return rodir

    def testEvalFormatSummary(self):
        rodir   = self.setupEvalFormat()
        options = { 'detail': "summary" }
        stream  = StringIO.StringIO()
        ro_eval_minim.format(self.eval_result, options, stream)
        outtxt = stream.getvalue()
        expect = (
            "Research Object file://%s/:\n"%rodir +
            "Nominally complete for %(purpose)s of resource %(target)s\n"%(self.eval_result)
            )
        self.assertEquals(outtxt, expect)
        return

    def testEvalFormatDetail(self):
        rodir   = self.setupEvalFormat()
        options = { 'detail': "full" }
        stream  = StringIO.StringIO()
        ro_eval_minim.format(self.eval_result, options, stream)
        expect = (
            [ "Research Object file://%s/:"%rodir
            , "Nominally complete for %(purpose)s of resource %(target)s"%(self.eval_result)
            , "Unsatisfied MUST requirements:"
            , "  Aggregates resource %s"%(self.eval_result['missingMust'][0][0]['datarule']['aggregates'])
            , "Unsatisfied SHOULD requirements:"
            , "  Aggregates resource %s"%(self.eval_result['missingShould'][0][0]['datarule']['aggregates'])
            , "Unsatisfied MAY requirements:"
            , "  Aggregates resource %s"%(self.eval_result['missingMay'][0][0]['datarule']['aggregates'])
            , "Research object URI:     %(rouri)s"%(self.eval_result)
            , "Minimum information URI: %(minimuri)s"%(self.eval_result)
            ])
        stream.seek(0)
        for expect_line in expect:
            line = stream.readline()
            self.assertEquals(line, expect_line+"\n")
        return

    def testEvaluateChecklistCommand(self):
        self.setupConfig()
        rodir = self.createTestRo(testbase, "test-data-1", "RO test minim", "ro-testMinim")
        self.populateTestRo(testbase, rodir)
        rometa   = ro_metadata(ro_config, rodir)
        minimuri = rometa.getComponentUri("Minim-UserRequirements.rdf")
        # Evaluate annotations
        args = [ "ro", "evaluate", "checklist"
               , "-a"
               , "-d", rodir+"/"
               , "Minim-UserRequirements.rdf"
               , "create"
               , "docs/UserRequirements-bio.html"
               ]
        self.outstr.seek(0)
        with StdoutContext.SwitchStdout(self.outstr):
            status = ro.runCommand(
                os.path.join(testbase, TestConfig.ro_test_config.CONFIGDIR),
                os.path.join(testbase, TestConfig.ro_test_config.ROBASEDIR),
                args)
        outtxt = self.outstr.getvalue()
        assert status == 0, "Status %d, outtxt: %s"%(status,outtxt)
        log.debug("status %d, outtxt: %s"%(status, outtxt))
        # Check response returned
        expect = (
            [ "Research Object file://%s/:"%(rodir)
            , "Minimally complete for create of resource docs/UserRequirements-bio.html"
            , "Unsatisfied SHOULD requirements:"
            , "  Aggregates resource %s"%(rometa.getComponentUri("docs/missing.css"))
            , "Satisfied requirements:"
            , "  Aggregates resource %s"%(rometa.getComponentUri("data/UserRequirements-astro.ods")) 
            , "  Environment 'python -V' matches 'Python 2.7'"
            , "Research object URI:     %s"%(rometa.getRoUri())
            , "Minimum information URI: %s"%(minimuri)
            ])
        self.outstr.seek(0)
        for line in self.outstr:
            self.assertIn(str(line)[:-1], expect)
        self.deleteTestRo(rodir)
        return

    # @@TODO Add test cases for software environment rule pass/fail, based on previous
    def annotateWfRo(self, testbase, rodir):
        """
        Annotate test workflow research object
        Returns name of research object directory
        """
        # $RO annotate -v $TESTRO/simple-wf-wfdesc.rdf rdf:type wfdesc:Workflow
        args1 = [
            "ro", "annotate", rodir+"/simple-wf-wfdesc.rdf", "rdf:type", "wfdesc:Workflow"
            ]
        # $RO annotate -v $TESTRO/docs/mkjson.sh -g $TESTRO/simple-requirements-wfdesc.rdf
        args2 = [
            "ro", "annotate", rodir+"/docs/mkjson.sh", "-g", rodir+"/simple-requirements-wfdesc.rdf"
            ]
        with StdoutContext.SwitchStdout(self.outstr):
            configdir = self.getConfigDir(testbase)
            robasedir = self.getRoBaseDir(testbase)
            #print "testbase %s, configdir %s, robasedir %s"%(testbase, configdir, robasedir)
            status = ro.runCommand(configdir, robasedir, args1)
            if status == 0:
                status = ro.runCommand(configdir, robasedir, args2)
        outtxt = self.outstr.getvalue()
        assert status == 0, outtxt
        self.outstr = StringIO.StringIO()
        return rodir

    def testEvaluateWfInputs(self):
        # Test cases usiung content match rule
        # Also tests constraint that is not directly linked to RO,
        # and use of designated target resource in probe query
        self.setupConfig()
        rodir = self.createTestRo(testbase, "test-simple-wf", "RO test minim", "ro-testMinim")
        self.populateTestRo(testbase, rodir)
        self.annotateWfRo(testbase, rodir)
        rometa   = ro_metadata(ro_config, rodir)
        minimuri = rometa.getComponentUri("simple-wf-minim.rdf")
        # Evaluate
        args = [ "ro", "evaluate", "checklist"
               , "-a"
               , "-d", rodir+"/"
               , "simple-wf-minim.rdf"
               , "Runnable"
               , "."
               ]
        self.outstr.seek(0)
        with StdoutContext.SwitchStdout(self.outstr):
            status = ro.runCommand(
                os.path.join(testbase, TestConfig.ro_test_config.CONFIGDIR),
                os.path.join(testbase, TestConfig.ro_test_config.ROBASEDIR),
                args)
        outtxt = self.outstr.getvalue()
        assert status == 0, "Status %d, outtxt: %s"%(status,outtxt)
        log.debug("status %d, outtxt: %s"%(status, outtxt))
        # Check response returned
        expect = (
            [ "Research Object file://%s/:"%(rodir)
            , "Fully complete for Runnable of resource ."
            , "Satisfied requirements:"
            , "  Workflow instance or template found" 
            , "  All workflow inputs referenced or present"
            , "Research object URI:     %s"%(rometa.getRoUri())
            , "Minimum information URI: %s"%(minimuri)
            ])
        self.outstr.seek(0)
        for line in self.outstr:
            self.assertIn(str(line)[:-1], expect)
        self.deleteTestRo(rodir)
        return
    
    # @@TODO Add test cases for liveness test

    # Test evaluation of remote resource

    def testEvaluateChecklistRemote(self):
        # Config remote testing
        remotehost   = "http://andros.zoo.ox.ac.uk"
        remoterobase = "/workspace/wf4ever-ro-catalogue/v0.1/"
        remoteroname = "simple-requirements/"
        remoteminim  = "simple-requirements-minim.rdf"
        #self.setupConfig()
        rouri    = remotehost+remoterobase+remoteroname
        rometa   = ro_metadata(ro_config, rouri)
        minimuri = rometa.getComponentUri(remoteminim)
        # create rometa object
        rometa = ro_metadata(ro_config, rouri)
        # invoke evaluation service
        #   ro_eval_minim.evaluate(rometa, minim, target, purpose)
        evalresult = ro_eval_minim.evaluate(rometa, minimuri, rouri, "Runnable")
        self.assertEqual(evalresult['rouri'],         rdflib.URIRef(rouri))
        self.assertEqual(evalresult['minimuri'],      rdflib.URIRef(minimuri))
        self.assertEqual(evalresult['target'],        rouri)
        self.assertEqual(evalresult['purpose'],       "Runnable")
        self.assertEqual(evalresult['constrainturi'], rometa.getComponentUri("simple-requirements-minim.rdf#runnable_RO"))
        self.assertEqual(evalresult['modeluri'],      rometa.getComponentUri("simple-requirements-minim.rdf#runnable_RO_model"))
        self.assertIn(MINIM.fullySatisfies,    evalresult['summary'])
        self.assertIn(MINIM.nominallySatisfies, evalresult['summary'])
        self.assertIn(MINIM.minimallySatisfies, evalresult['summary'])
        self.assertEqual(len(evalresult['missingMust']),   0)
        self.assertEqual(len(evalresult['missingShould']), 0)
        self.assertEqual(len(evalresult['missingMay']),    0)
        self.assertEqual(len(evalresult['satisfied']),     4)
        return

    def testEvaluateChecklistRemoteFail(self):
        # Config remote testing
        remotehost   = "http://andros.zoo.ox.ac.uk"
        remoterobase = "/aleix/ro-catalogue/v0.1/"
        remoteroname = "wf74-repeat-fail/"
        remoteminim  = "simple-requirements-minim.rdf"
        #self.setupConfig()
        rouri    = remotehost+remoterobase+remoteroname
        rometa   = ro_metadata(ro_config, rouri)
        minimuri = rometa.getComponentUri(remoteminim)
        # create rometa object
        rometa = ro_metadata(ro_config, rouri)
        # invoke evaluation service
        #   ro_eval_minim.evaluate(rometa, minim, target, purpose)
        evalresult = ro_eval_minim.evaluate(rometa, minimuri, rouri, "Repeatable")
        self.assertEqual(evalresult['rouri'],         rdflib.URIRef(rouri))
        self.assertEqual(evalresult['minimuri'],      rdflib.URIRef(minimuri))
        self.assertEqual(evalresult['target'],        rouri)
        self.assertEqual(evalresult['purpose'],       "Repeatable")
        self.assertEqual(evalresult['constrainturi'], rometa.getComponentUri("simple-requirements-minim.rdf#repeatable_RO"))
        self.assertEqual(evalresult['modeluri'],      rometa.getComponentUri("simple-requirements-minim.rdf#repeatable_RO_model"))
        self.assertNotIn(MINIM.fullySatisfies,     evalresult['summary'])
        self.assertNotIn(MINIM.nominallySatisfies, evalresult['summary'])
        self.assertNotIn(MINIM.minimallySatisfies, evalresult['summary'])
        self.assertEqual(len(evalresult['missingMust']),   1)
        self.assertEqual(len(evalresult['missingShould']), 0)
        self.assertEqual(len(evalresult['missingMay']),    0)
        self.assertEqual(len(evalresult['satisfied']),     4)
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
            , "testSetupConfig"
            , "testEvalAllPresent"
            , "testEvalMustMissing"
            , "testEvalShouldMissing"
            , "testEvalMayMissing"
            , "testEvalFormatSummary"
            , "testEvalFormatDetail"
            , "testEvaluateChecklistCommand"
            , "testEvaluateWfInputs"
            ],
        "component":
            [ "testComponents"
            ],
        "integration":
            [ "testIntegration"
            ],
        "pending":
            [ "testPending"
            , "testEvaluateChecklistRemote"
            ]
        }
    return TestUtils.getTestSuite(TestEvalChecklist, testdict, select=select)

if __name__ == "__main__":
    TestUtils.runTests("TestEvalChecklist.log", getTestSuite, sys.argv)

# End.
