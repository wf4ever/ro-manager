#!/usr/bin/python

"""
Module to test RO manager minim access functions

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

from rocommand import ro_manifest
from rocommand.ro_metadata import ro_metadata
from rocommand.ro_annotation import annotationTypes, annotationPrefixes
from rocommand.ro_prefixes   import make_sparql_prefixes

from rocommand.test import TestROSupport
from rocommand.test import TestConfig

from iaeval import ro_minim
from iaeval.ro_minim import MINIM

from iaeval import ro_eval_minim

# Base directory for RO tests in this module
testbase = os.path.dirname(os.path.realpath(__file__))

# Local ro_config for testing
ro_config = {
    "annotationTypes":      annotationTypes,
    "annotationPrefixes":   annotationPrefixes
    }

# Test suite
class TestEvalQueryMatch(TestROSupport.TestROSupport):
    """
    Test ro annotation commands
    """
    def setUp(self):
        super(TestEvalQueryMatch, self).setUp()
        return

    def tearDown(self):
        super(TestEvalQueryMatch, self).tearDown()
        return

    # Setup local config for Minim tests

    def setupConfig(self):
        return self.setupTestBaseConfig(testbase)

    # Actual tests follow

    def testNull(self):
        assert True, 'Null test failed'

    def testEvalQueryTestModelMin(self):
        """
        Evaluate RO against minimal Minim description using just QueryTestRules
        """
        self.setupConfig()
        rodir = self.createTestRo(testbase, "test-data-2", "RO test minim", "ro-testMinim")
        rouri = ro_manifest.getRoUri(rodir)
        self.populateTestRo(testbase, rodir)
        rometa = ro_metadata(ro_config, rodir)
        (g, evalresult) = ro_eval_minim.evaluate(rometa,
            "Minim-UserRequirements2-min.rdf",    # Minim file
            "data/UserRequirements-astro.ods",    # Target resource
            "create")                             # Purpose
        log.debug("ro_eval_minim.evaluate result:\n----\n%s"%(repr(evalresult)))
        self.assertIn(MINIM.fullySatisfies,     evalresult['summary'])
        self.assertIn(MINIM.nominallySatisfies, evalresult['summary'])
        self.assertIn(MINIM.minimallySatisfies, evalresult['summary'])
        self.assertEquals(evalresult['missingMust'],    [])
        self.assertEquals(evalresult['missingShould'],  [])
        self.assertEquals(evalresult['missingMay'],     [])
        self.assertEquals(evalresult['rouri'],          rometa.getRoUri())
        self.assertEquals(evalresult['minimuri'],       rometa.getComponentUri("Minim-UserRequirements2-min.rdf"))
        self.assertEquals(evalresult['target'],         "data/UserRequirements-astro.ods")
        self.assertEquals(evalresult['purpose'],        "create")
        self.assertEquals(evalresult['constrainturi'],
            rometa.getComponentUriAbs("Minim-UserRequirements2-min.rdf#create/data/UserRequirements-astro.ods"))
        self.assertEquals(evalresult['modeluri'],
            rometa.getComponentUriAbs("Minim-UserRequirements2-min.rdf#runnableRO"))
        self.deleteTestRo(rodir)
        return

    def testEvalQueryTestModelExists(self):
        """
        Evaluate RO against minimal Minim description using just QueryTestRules
        """
        self.setupConfig()
        rodir = self.createTestRo(testbase, "test-data-2", "RO test minim", "ro-testMinim")
        rouri = ro_manifest.getRoUri(rodir)
        self.populateTestRo(testbase, rodir)
        rometa = ro_metadata(ro_config, rodir)
        resuri = rometa.getComponentUriAbs("data/UserRequirements-astro.ods")
        rometa.addSimpleAnnotation(resuri, "rdfs:label", "Test label")
        # Now run evaluation against test RO
        (g, evalresult) = ro_eval_minim.evaluate(rometa,
            "Minim-UserRequirements2-exists.rdf", # Minim file
            "data/UserRequirements-astro.ods",    # Target resource
            "create")                             # Purpose
        log.debug("ro_eval_minim.evaluate result:\n----\n%s"%(repr(evalresult)))
        self.assertIn(MINIM.fullySatisfies,     evalresult['summary'])
        self.assertIn(MINIM.nominallySatisfies, evalresult['summary'])
        self.assertIn(MINIM.minimallySatisfies, evalresult['summary'])
        self.assertEquals(evalresult['missingMust'],    [])
        self.assertEquals(evalresult['missingShould'],  [])
        self.assertEquals(evalresult['missingMay'],     [])
        self.assertEquals(evalresult['rouri'],          rometa.getRoUri())
        self.assertEquals(evalresult['minimuri'],       rometa.getComponentUri("Minim-UserRequirements2-exists.rdf"))
        self.assertEquals(evalresult['target'],         "data/UserRequirements-astro.ods")
        self.assertEquals(evalresult['purpose'],        "create")
        self.assertEquals(evalresult['constrainturi'],
            rometa.getComponentUriAbs("Minim-UserRequirements2-exists.rdf#create/data/UserRequirements-astro.ods"))
        self.assertEquals(evalresult['modeluri'],
            rometa.getComponentUriAbs("Minim-UserRequirements2-exists.rdf#runnableRO"))
        self.deleteTestRo(rodir)
        return

    def testEvalQueryTestModel(self):
        """
        Evaluate RO against Minim description using just QueryTestRules
        """
        self.setupConfig()
        rodir = self.createTestRo(testbase, "test-data-2", "RO test minim", "ro-testMinim")
        rouri = ro_manifest.getRoUri(rodir)
        self.populateTestRo(testbase, rodir)
        rometa = ro_metadata(ro_config, rodir)
        resuri = rometa.getComponentUriAbs("data/UserRequirements-astro.ods")
        rometa.addSimpleAnnotation(resuri, "rdfs:label", "Test label")
        # Now run evaluation against test RO
        (g, evalresult) = ro_eval_minim.evaluate(rometa,
            "Minim-UserRequirements2.rdf",        # Minim file
            "data/UserRequirements-astro.ods",    # Target resource
            "create")                             # Purpose
        log.debug("ro_eval_minim.evaluate result:\n----\n%s"%(repr(evalresult)))
        self.assertIn(MINIM.fullySatisfies,     evalresult['summary'])
        self.assertIn(MINIM.nominallySatisfies, evalresult['summary'])
        self.assertIn(MINIM.minimallySatisfies, evalresult['summary'])
        self.assertEquals(evalresult['missingMust'],    [])
        self.assertEquals(evalresult['missingShould'],  [])
        self.assertEquals(evalresult['missingMay'],     [])
        self.assertEquals(evalresult['rouri'],          rometa.getRoUri())
        self.assertEquals(evalresult['minimuri'],       rometa.getComponentUri("Minim-UserRequirements2.rdf"))
        self.assertEquals(evalresult['target'],         "data/UserRequirements-astro.ods")
        self.assertEquals(evalresult['purpose'],        "create")
        self.assertEquals(evalresult['constrainturi'],
            rometa.getComponentUriAbs("Minim-UserRequirements2.rdf#create/data/UserRequirements-astro.ods"))
        self.assertEquals(evalresult['modeluri'],
            rometa.getComponentUriAbs("Minim-UserRequirements2.rdf#runnableRO"))
        self.deleteTestRo(rodir)
        return

    def testEvalQueryTestChembox(self):
        """
        Evaluate Chembox data against Minim description using QueryTestRules
        """
        self.setupConfig()
        rodir = self.createTestRo(testbase, "test-chembox", "RO test minim", "ro-testMinim")
        rouri = ro_manifest.getRoUri(rodir)
        self.populateTestRo(testbase, rodir)
        rometa = ro_metadata(ro_config, rodir)
        resuri = rometa.getComponentUriAbs("http://purl.org/net/chembox/Ethane")
        rometa.addGraphAnnotation(resuri, "Ethane.ttl")
        # Now run evaluation against test RO
        (g, evalresult) = ro_eval_minim.evaluate(rometa,
            "Minim-chembox.ttl",                  # Minim file
            resuri,                               # Target resource
            "complete")                           # Purpose
        log.debug("ro_eval_minim.evaluate result:\n%s\n----"%(repr(evalresult)))
        self.assertNotIn(MINIM.fullySatisfies,     evalresult['summary'])
        self.assertIn(MINIM.nominallySatisfies, evalresult['summary'])
        self.assertIn(MINIM.minimallySatisfies, evalresult['summary'])
        self.assertEquals(evalresult['missingMust'],    [])
        self.assertEquals(evalresult['missingShould'],  [])
        self.assertEquals(len(evalresult['missingMay']), 1)
        self.assertEquals(evalresult['missingMay'][0][0]['seq'], 'Synonym is present')
        self.assertEquals(evalresult['rouri'],          rometa.getRoUri())
        self.assertEquals(evalresult['minimuri'],       rometa.getComponentUri("Minim-chembox.ttl"))
        self.assertEquals(evalresult['target'],         resuri)
        self.assertEquals(evalresult['purpose'],        "complete")
        self.deleteTestRo(rodir)
        return

    def testEvalQueryTestChemboxFail(self):
        """
        Test for failing chembox requirement
        """
        self.setupConfig()
        rodir = self.createTestRo(testbase, "test-chembox", "RO test minim", "ro-testMinim")
        rouri = ro_manifest.getRoUri(rodir)
        self.populateTestRo(testbase, rodir)
        rometa = ro_metadata(ro_config, rodir)
        resuri = rometa.getComponentUriAbs("http://purl.org/net/chembox/Ethane")
        rometa.addGraphAnnotation(resuri, "Ethane.ttl")
        # Now run evaluation against test RO
        (g, evalresult) = ro_eval_minim.evaluate(rometa,
            "Minim-chembox.ttl",              # Minim file
            resuri,                           # Target resource
            "fail")                           # Purpose
        log.debug("ro_eval_minim.evaluate result:\n----\n%s"%(repr(evalresult)))
        self.assertNotIn(MINIM.fullySatisfies,     evalresult['summary'])
        self.assertNotIn(MINIM.nominallySatisfies, evalresult['summary'])
        self.assertNotIn(MINIM.minimallySatisfies, evalresult['summary'])
        self.assertEquals(len(evalresult['missingMust']), 1)
        self.assertEquals(evalresult['missingMust'][0][0]['seq'], 'This test should fail')
        self.assertEquals(evalresult['missingShould'],  [])
        self.assertEquals(evalresult['missingMay'],     [])
        self.assertEquals(evalresult['rouri'],          rometa.getRoUri())
        self.assertEquals(evalresult['minimuri'],       rometa.getComponentUri("Minim-chembox.ttl"))
        self.assertEquals(evalresult['target'],         resuri)
        self.assertEquals(evalresult['purpose'],        "fail")
        self.deleteTestRo(rodir)
        return

    def setupEvalFormat(self):
        self.setupConfig()
        rodir     = self.createTestRo(testbase, "test-chembox", "RO test minim", "ro-testMinim")
        rometa    = ro_metadata(ro_config, rodir)
        minimbase = rometa.getComponentUri("Minim-chembox.ttl")
        modeluri  = rdflib.URIRef('http://example.com/chembox-samples/minim_model')
        resuri    = rometa.getComponentUriAbs("http://purl.org/net/chembox/Ethane")
        self.satisfied_result_1 = (
            { 'seq':    'ChemSpider identifier is present'
            , 'level': 'SHOULD'
            , 'uri':    rdflib.URIRef('http://example.com/chembox-samples/ChemSpider')
            , 'label':  None
            , 'model':  modeluri
            , 'querytestrule': 
                { 'prefixes':
                    [ ('chembox', 'http://dbpedia.org/resource/Template:Chembox:')
                    , ('default', 'http://example.com/chembox-samples/')
                    ]
                , 'query':        rdflib.Literal('?targetres chembox:ChemSpiderID ?value . FILTER ( str(xsd:integer(?value)) )')
                , 'resultmod':    None
                , 'max':          None
                , 'min':          1
                , 'aggregates_t': None
                , 'islive_t':     None
                , 'exists':       None
                , 'show':         None
                , 'showpass':     rdflib.Literal('ChemSpider identifier is present')
                , 'showfail':     rdflib.Literal('No ChemSpider identifier is present')
                , 'showmiss':     None
                , 'derives':      None
                }
            })
        self.satisfied_binding_1 = (
            { '_count': 1
            , 'targetro':  rometa.getRoUri()
            , 'targetres': resuri
            })
        self.satisfied_result_2 = (
            { 'seq':    'InChI identifier is present'
            , 'level':  'MUST'
            , 'uri':    rdflib.URIRef('http://example.com/chembox-samples/InChI')
            , 'label':  None
            , 'model':  modeluri
            , 'querytestrule': 
                { 'prefixes':
                    [ ('chembox', 'http://dbpedia.org/resource/Template:Chembox:')
                    , ('default', 'http://example.com/chembox-samples/')
                    ]
                , 'query':        rdflib.Literal('?targetres chembox:StdInChI ?value . FILTER ( datatype(?value) = xsd:string )')
                , 'resultmod':    None
                , 'min':          1
                , 'max':          1
                , 'aggregates_t': None
                , 'islive_t':     None
                , 'exists':       None
                , 'show':         None
                , 'showpass':     rdflib.Literal('InChI identifier is present')
                , 'showfail':     rdflib.Literal('No InChI identifier is present')
                , 'showmiss':     None
                , 'derives':      None
                }
            })
        self.satisfied_binding_2 = (
            { '_count': 1
            , 'targetro':  rometa.getRoUri()
            , 'targetres': resuri
            })
        self.missing_may_result = (
            { 'seq':    'Synonym is present'
            , 'level':  'MAY'
            , 'uri':    rdflib.URIRef('http://example.com/chembox-samples/Synonym')
            , 'label':  None
            , 'model':  modeluri
            , 'querytestrule': 
                { 'prefixes':
                    [ ('chembox', 'http://dbpedia.org/resource/Template:Chembox:')
                    , ('default', 'http://example.com/chembox-samples/')
                    ]
                , 'query':        rdflib.Literal('\n            ?targetres chembox:OtherNames ?value .\n            ')
                , 'resultmod':    None
                , 'min':          1
                , 'max':          None
                , 'aggregates_t': None
                , 'islive_t':     None
                , 'exists':       None
                , 'show':         None
                , 'showpass':     rdflib.Literal('Synonym is present')
                , 'showfail':     rdflib.Literal('No synonym is present')
                , 'showmiss':     None
                , 'derives':      None
                }
            })
        self.missing_may_binding = (
            { '_count': 1
            , 'targetro':  rometa.getRoUri()
            , 'targetres': resuri
            })
        self.eval_result = (
            { 'summary':        [MINIM.nominallySatisfies, MINIM.minimallySatisfies]
            , 'missingMust':    []
            , 'missingShould':  []
            , 'missingMay':     [(self.missing_may_result, self.missing_may_binding)]
            , 'satisfied':      [ (self.satisfied_result_1, self.satisfied_binding_1)
                                , (self.satisfied_result_2, self.satisfied_binding_2)
                                ]
            , 'rouri':          rometa.getRoUri()
            , 'roid':           rdflib.Literal('ro-testMinim')
            , 'title':          rdflib.Literal('RO test minim')
            , 'description':    rdflib.Literal('RO test minim')
            , 'target':         resuri
            , 'purpose':        'complete'
            , 'minimuri':       rometa.getComponentUri("Minim-chembox.ttl")
            , 'constrainturi':  rdflib.URIRef('http://example.com/chembox-samples/minim_pass_constraint')
            , 'modeluri':       modeluri
            })
        self.deleteTestRo(rodir)
        return rodir

    def testEvalFormatSummary(self):
        rodir   = self.setupEvalFormat()
        options = { 'detail': "summary" }
        stream  = StringIO.StringIO()
        ro_eval_minim.format(self.eval_result, options, stream)
        outtxt = stream.getvalue()
        log.debug("---- Result:\n%s\n----"%(outtxt))
        expect = (
            "Research Object file://%s/:\n"%rodir +
            "Nominally complete for %(purpose)s of resource %(target)s\n"%(self.eval_result)
            )
        self.assertEquals(outtxt, expect)
        return

# Research Object file:///usr/workspace/wf4ever-ro-manager/src/iaeval/test/robase/RO_test_minim/:
# Nominally complete for complete of resource http://purl.org/net/chembox/Ethane
# Unsatisfied MAY requirements:
#   No synonym is present
# Satisfied requirements:
#   ChemSpider identifier is present
#   InChI identifier is present
# Research object URI:     file:///usr/workspace/wf4ever-ro-manager/src/iaeval/test/robase/RO_test_minim/
# Minimum information URI: file:///usr/workspace/wf4ever-ro-manager/src/iaeval/test/robase/RO_test_minim/Minim-chembox.ttl


    def testEvalFormatDetail(self):
        rodir   = self.setupEvalFormat()
        options = { 'detail': "full" }
        stream  = StringIO.StringIO()
        ro_eval_minim.format(self.eval_result, options, stream)
        outtxt = stream.getvalue()
        log.debug("---- Result:\n%s\n----"%(outtxt))
        expect = (
            [ "Research Object file://%s/:"%rodir
            , "Nominally complete for %(purpose)s of resource %(target)s"%(self.eval_result)
            # , "Unsatisfied MUST requirements:"
            # , "Unsatisfied SHOULD requirements:"
            , "Unsatisfied MAY requirements:"
            , "  No synonym is present"%(self.eval_result['missingMay'][0][0]['querytestrule'])
            , "Satisfied requirements:"
            , "  ChemSpider identifier is present"
            , "  InChI identifier is present"
            , "Research object URI:     %(rouri)s"%(self.eval_result)
            , "Minimum information URI: %(minimuri)s"%(self.eval_result)
            ])
        stream.seek(0)
        for expect_line in expect:
            line = stream.readline()
            self.assertEquals(line, expect_line+"\n")
        return
    
    def testEvaluateRDF(self):
        self.setupConfig()
        rodir = self.createTestRo(testbase, "test-chembox", "RO test minim", "ro-testMinim")
        rouri = ro_manifest.getRoUri(rodir)
        self.populateTestRo(testbase, rodir)
        rometa = ro_metadata(ro_config, rodir)
        resuri = rometa.getComponentUriAbs("http://purl.org/net/chembox/Ethane")
        rometa.addGraphAnnotation(resuri, "Ethane.ttl")
        # Now run evaluation against test RO
        (minimgr, evalresult) = ro_eval_minim.evaluate(rometa,
            "Minim-chembox.ttl",                  # Minim file
            resuri,                               # Target resource
            "complete")                           # Purpose
        resultgr = ro_eval_minim.evalResultGraph(minimgr, evalresult)
        log.debug("------ resultgr:\n%s\n----"%(resultgr.serialize(format='turtle'))) # pretty-xml
        # Check response returned
        modeluri = rdflib.URIRef('http://example.com/chembox-samples/minim_model')
        prefixes = make_sparql_prefixes()
        probequeries = (
            [ '''ASK { <%s> minim:minimUri <%s> }'''%
              (rouri, rometa.getComponentUri("Minim-chembox.ttl"))
            , '''ASK { <%s> minim:modelUri <%s> }'''%
              (rouri, modeluri)
            , '''ASK { <%s> minim:satisfied [ minim:tryMessage "%s" ] }'''%
              (rouri, "InChI identifier is present")
            , '''ASK { <%s> minim:satisfied [ minim:tryMessage "%s" ] }'''%
              (rouri, "ChemSpider identifier is present")
            , '''ASK { <%s> minim:missingMay [ minim:tryMessage "%s" ] }'''%
              (rouri, "No synomym is present")
            , '''ASK { <%s> minim:nominallySatisfies <%s> }'''%
              (resuri, modeluri)
            , '''ASK { <%s> minim:minimallySatisfies <%s> }'''%
              (resuri, modeluri)
            , '''ASK { <%s> rdfs:label "%s" }'''%
              (resuri, str(resuri))
            # , '''ASK { <%s> minim:more <%s> }'''%
            #   (resuri, rdflib.Literal(str(resuri)))
            ])
        for q in probequeries:
            r = resultgr.query(prefixes+q)
            self.assertEqual(r.type, 'ASK', "Result type %s for: %s"%(r.type, q))
            self.assertTrue(r.askAnswer, "Failed query: %s"%(q))
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
            , "testEvalQueryTestModelMin"
            , "testEvalQueryTestModelExists"
            , "testEvalQueryTestModel"
            , "testEvalQueryTestChembox"
            , "testEvalQueryTestChemboxFail"
            , "testEvalFormatSummary"
            , "testEvalFormatDetail"
            , "testEvaluateRDF"
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
    return TestUtils.getTestSuite(TestEvalQueryMatch, testdict, select=select)

if __name__ == "__main__":
    TestUtils.runTests("TestEvalQueryMatch.log", getTestSuite, sys.argv)

# End.
