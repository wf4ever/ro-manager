#!/usr/bin/python

"""
Module to test RO manager RDF report creation function
"""

import os, os.path
import sys
import re
import shutil
import logging
import datetime
import StringIO
import json
import unittest

log = logging.getLogger(__name__)

if __name__ == "__main__":
    # Add main project directory and ro manager directories at start of python path
    sys.path.insert(0, "../..")
    sys.path.insert(0, "..")
    # sys.path.insert(0, "/usr/workspace/github-rdfextras")
    # sys.path.insert(0, "/usr/workspace/github-rdflib")

import rdflib

from MiscUtils import TestUtils

from rocommand.ro_namespaces import RDF, DCTERMS, RO, AO, ORE

import RdfReport
import TrafficLightReports

# Base directory for RO tests in this module
testbase = os.path.dirname(os.path.abspath(__file__))
simple_test_data = testbase+"/data/simple-test-data.rdf"
trafficlight_test_data = testbase+"/data/trafficlight-test-data.rdf"

def LIT(l): return rdflib.Literal(l)
def REF(u): return rdflib.URIRef(u)

prefixes = """
    PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl:     <http://www.w3.org/2002/07/owl#>
    PREFIX xsd:     <http://www.w3.org/2001/XMLSchema#>
    PREFIX xml:     <http://www.w3.org/XML/1998/namespace>
    PREFIX rdfg:    <http://www.w3.org/2004/03/trix/rdfg-1/>
    PREFIX ore:     <http://www.openarchives.org/ore/terms/>
    PREFIX ao:      <http://purl.org/ao/>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX foaf:    <http://xmlns.com/foaf/0.1/>
    PREFIX ro:      <http://purl.org/wf4ever/ro#>
    PREFIX wfprov:  <http://purl.org/wf4ever/wfprov#>
    PREFIX wfdesc:  <http://purl.org/wf4ever/wfdesc#>
    PREFIX wf4ever: <http://purl.org/wf4ever/wf4ever#>
    PREFIX minim:   <http://purl.org/minim/minim#>
    PREFIX result:  <http://www.w3.org/2001/sw/DataAccess/tests/result-set#>
    PREFIX ex:      <http://example.org/terms/>
    """

class TestRdfReport(unittest.TestCase):
    """
    Test RDF report generator

    Report definition structure:

    report-defn     = { 'report': template-item }   // May add more later

    template-item   = sequence | query-template     // Bindings to date are fed down into template-item processing

    sequence        = [ template-item, ... ]

    query-template  = { 'query':    sparql-query [None],
                        'max':      integer [1],
                        'output':   python-format-string [None],
                        'report':   template-item [None],
                        'alt':      python-format-string [None],
                      }
    """
    def setUp(self):
        super(TestRdfReport, self).setUp()
        return

    def tearDown(self):
        super(TestRdfReport, self).tearDown()
        return

    # Actual tests follow

    def testNull(self):
        assert True, 'Null test failed'

    def testEscapeJSON(self):
        s = []
        for i in range(0,128):
            s.append(unichr(i))
        s = "".join(s)
        s_esc = RdfReport.escape_json(s)
        e_esc = ( u'\\u0000\\u0001\\u0002\\u0003\\u0004\\u0005\\u0006\\u0007'+
                  u'\\b\\t\\n\\u000b\\f\\r\\u000e\\u000f'+
                  u'\\u0010\\u0011\\u0012\\u0013\\u0014\\u0015\\u0016\\u0017'+
                  u'\\u0018\\u0019\\u001a\\u001b\\u001c\\u001d\\u001e\\u001f'+
                  u' !\\"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\\\]^_`'+
                  u'abcdefghijklmnopqrstuvwxyz{|}~\\u007f')
        # print "----"
        # print repr(s_esc)
        # print repr(e_esc)
        self.assertEqual(s_esc, e_esc)
        s_loads = json.loads('"'+s_esc+'"')
        self.assertEqual(s_loads, s)
        return

    def testHelloWorld(self):
        """
        Test just about the simplest possible report
        """
        report = (
            { 'report':
              { 'output': "Hello world" }
            })
        outstr   = StringIO.StringIO()
        rdfgraph = rdflib.Graph()
        rdfgraph.parse(simple_test_data)
        RdfReport.generate_report(report, rdfgraph, {}, outstr)
        self.assertEqual("Hello world", outstr.getvalue())
        return

    def testSimpleQuery(self):
        """
        Test a simple query report
        """
        report = (
            { 'report':
              { 'query':  prefixes+"SELECT * WHERE { ?s dcterms:creator ?creator }"
              , 'output': "Hello %(creator)s" }
            })
        outstr   = StringIO.StringIO()
        rdfgraph = rdflib.Graph()
        rdfgraph.parse(simple_test_data)
        RdfReport.generate_report(report, rdfgraph, {}, outstr)
        self.assertEqual("Hello Graham", outstr.getvalue())
        return

    def testSimpleQuotedJson(self):
        """
        Test JSON quoting in simple report
        """
        report = (
            { 'report':
              { 'query':  prefixes+"SELECT * WHERE { ?s ex:quoteme ?quoteme }"
              , 'output': "Hello %(quoteme_esc)s" }
            })
        outstr   = StringIO.StringIO()
        rdfgraph = rdflib.Graph()
        rdfgraph.parse(simple_test_data)
        RdfReport.generate_report(report, rdfgraph, {}, outstr, RdfReport.escape_json)
        self.assertEqual("""Hello <\\\"Graham\\">""", outstr.getvalue())
        return

    def testSimpleQuotedHtml(self):
        """
        Test HTML quoting in simple report
        """
        report = (
            { 'report':
              { 'query':  prefixes+"SELECT * WHERE { ?s ex:quoteme ?quoteme }"
              , 'output': "Hello %(quoteme_esc)s" }
            })
        outstr   = StringIO.StringIO()
        rdfgraph = rdflib.Graph()
        rdfgraph.parse(simple_test_data)
        RdfReport.generate_report(report, rdfgraph, {}, outstr, RdfReport.escape_html)
        self.assertEqual("""Hello &lt;"Graham"&gt;""", outstr.getvalue())
        return

    def testQueryResultMerge(self):
        """
        Test a simple query merged with existing results
        """
        report = (
            { 'report':
              { 'query':  prefixes+"SELECT * WHERE { ?s dcterms:creator ?creator }"
              , 'output': "Hello %(creator)s and %(name)s"
              }
            })
        outstr   = StringIO.StringIO()
        rdfgraph = rdflib.Graph()
        rdfgraph.parse(simple_test_data)
        RdfReport.generate_report(report, rdfgraph, {'name': 'anyone'}, outstr)
        self.assertEqual("Hello Graham and anyone", outstr.getvalue())
        return

    def testQueryResultPreBinding(self):
        """
        Test a simple query with pre-bound result value
        """
        report = (
            { 'report':
              { 'query':  prefixes+"SELECT * WHERE { ?s dcterms:creator ?creator; rdfs:label ?label }"
              , 'output': "Hello %(creator)s"
              }
            })
        outstr   = StringIO.StringIO()
        rdfgraph = rdflib.Graph()
        rdfgraph.parse(simple_test_data)
        RdfReport.generate_report(report, rdfgraph, {}, outstr)
        self.assertEqual("Hello Graham", outstr.getvalue())
        outstr   = StringIO.StringIO()
        RdfReport.generate_report(report, rdfgraph, {'label': rdflib.Literal('simple-test-data')}, outstr)
        self.assertEqual("Hello Graham", outstr.getvalue())
        return

    def testSequence(self):
        """
        Test a sequence report
        """
        report = (
            { 'report':
              [ { 'output': "Foreword: " }
              , { 'query':  prefixes+"SELECT * WHERE { ?s dcterms:creator ?creator }"
                , 'output': "Hello %(creator)s; "
                }
              , { 'output': "afterword." }
              ]
            })
        outstr   = StringIO.StringIO()
        rdfgraph = rdflib.Graph()
        rdfgraph.parse(simple_test_data)
        RdfReport.generate_report(report, rdfgraph, {}, outstr)
        self.assertEqual("Foreword: Hello Graham; afterword.", outstr.getvalue())
        return

    def testAlternative(self):
        """
        Test an alterantive (query not matched) report
        """
        report = (
            { 'report':
              [ { 'output': "Foreword: " }
              , { 'query':  prefixes+"SELECT * WHERE { ?s ex:notfound ?creator }"
                , 'output': "Hello %(creator)s; " 
                , 'alt':    "Is %(name)s there? "
                }
              , { 'output': "afterword." }
              ]
            })
        outstr   = StringIO.StringIO()
        rdfgraph = rdflib.Graph()
        rdfgraph.parse(simple_test_data)
        RdfReport.generate_report(report, rdfgraph, {'name': "anyone"}, outstr)
        self.assertEqual("Foreword: Is anyone there? afterword.", outstr.getvalue())
        return

    def testAlternativeMissing(self):
        """
        Test an alterantive (query not matched) report with no alternative given
        """
        report = (
            { 'report':
              [ { 'output': "Foreword: " }
              , { 'query':  prefixes+"SELECT * WHERE { ?s ex:notfound ?creator }"
                , 'output': "Hello %(creator)s; " 
                }
              , { 'output': "afterword." }
              ]
            })
        outstr   = StringIO.StringIO()
        rdfgraph = rdflib.Graph()
        rdfgraph.parse(simple_test_data)
        RdfReport.generate_report(report, rdfgraph, {'name': "anyone"}, outstr)
        self.assertEqual("Foreword: afterword.", outstr.getvalue())
        return

    def testRepetition(self):
        """
        Test a report with a repeated match
        """
        report = (
            { 'report':
              [ { 'output': "Tags: " }
              , { 'query':  prefixes+"SELECT * WHERE { ?s dcterms:creator ?creator; ex:tag ?tag } ORDER BY ?tag"
                , 'output': "%(tag)s"
                , 'sep':    ", "
                }
              , { 'output': "." }
              ]
            })
        outstr   = StringIO.StringIO()
        rdfgraph = rdflib.Graph()
        rdfgraph.parse(simple_test_data)
        RdfReport.generate_report(report, rdfgraph, {}, outstr)
        self.assertEqual("Tags: tag1, tag2, tag3, tag4.", outstr.getvalue())
        return

    def testRepetitionMax(self):
        """
        Test a report with a repeated match
        """
        report = (
            { 'report':
              [ { 'output': "Tags: " }
              , { 'query':  prefixes+"SELECT * WHERE { ?s dcterms:creator ?creator; ex:tag ?tag } ORDER BY ?tag"
                , 'output': "%(tag)s"
                , 'sep':    ", "
                , 'max':    2
                }
              , { 'output': "." }
              ]
            })
        outstr   = StringIO.StringIO()
        rdfgraph = rdflib.Graph()
        rdfgraph.parse(simple_test_data)
        RdfReport.generate_report(report, rdfgraph, {}, outstr)
        self.assertEqual("Tags: tag1, tag2.", outstr.getvalue())
        return

    def testRepetitionAlt(self):
        """
        Test a report with a repeated match
        """
        report = (
            { 'report':
              [ { 'output': "Tags: " }
              , { 'query':  prefixes+"SELECT * WHERE { ?s ex:notag ?tag } ORDER BY ?tag"
                , 'output': "%(tag)s"
                , 'sep':    ", "
                , 'alt':    "none"
                }
              , { 'output': "." }
              ]
            })
        outstr   = StringIO.StringIO()
        rdfgraph = rdflib.Graph()
        rdfgraph.parse(simple_test_data)
        RdfReport.generate_report(report, rdfgraph, {}, outstr)
        self.assertEqual("Tags: none.", outstr.getvalue())
        return

    def testNesting(self):
        """
        Test a report with a nested sub-report
        """
        report = (
            { 'report':
              [ { 'query':  prefixes+
                            "SELECT ?s ?title ?label WHERE { ?s dcterms:title ?title; rdfs:label ?label } "+
                            "ORDER BY DESC(?label)"
                , 'output': "\nFound %(title)s:"
                , 'report':
                  [ {'output': "\nTags for %(label)s: " }
                  , { 'query':  prefixes+"SELECT * WHERE { ?s ex:tag ?tag } ORDER BY ?tag"
                    , 'output': "%(tag)s"
                    , 'sep':    ", "
                    , 'alt':    "none"
                    }
                  , { 'output': "." }
                  , { 'output': "\nFinished %(title)s." }
                  ]
                }
              , { 'output': "\nFinished all." }
              ]
            })
        outstr   = StringIO.StringIO()
        rdfgraph = rdflib.Graph()
        rdfgraph.parse(simple_test_data)
        RdfReport.generate_report(report, rdfgraph, {}, outstr)
        expected = ("\n"+
            "Found Simple test data:\n"+
            "Tags for simple-test-data: tag1, tag2, tag3, tag4.\n"+
            "Finished Simple test data.\n"+
            "Found More test data:\n"+
            "Tags for more-test-data: more1, more2.\n"+
            "Finished More test data.\n"+
            "Finished all."+
            "")
        result = outstr.getvalue()
        # print "\n-----"
        # print result
        # print "-----"
        self.assertEqual(expected, result)
        return

    def testQueryForNesting(self):
        testdata = """<?xml version="1.0" encoding="UTF-8"?>
            <rdf:RDF
               xmlns:xml="http://www.w3.org/XML/1998/namespace"
               xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
               xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
               xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
               xmlns:dct="http://purl.org/dc/terms/"
               xmlns:ex="http://example.org/terms/"
            >
              <rdf:Description rdf:about="simple-test-data.rdf">
                <rdfs:label>Label</rdfs:label>
                <dct:title>Title</dct:title>
              </rdf:Description>
            </rdf:RDF>
            """
        teststream = StringIO.StringIO(testdata)
        rdfgraph = rdflib.Graph()
        rdfgraph.parse(teststream)
        query = """
            PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX dct:     <http://purl.org/dc/terms/>

            SELECT * WHERE { ?s dct:title ?title; rdfs:label ?label } ORDER BY DESC(?label)
            """
        resp = rdfgraph.query(query, initBindings={ 'title': "foo" })
        self.assertEqual(resp.type, 'SELECT')
        bindings = resp.bindings
        count = 0
        for b in bindings:
            count += 1
            print "\nResult bindings %d:"%count
            for k in b:
                print "%s: %s"%(str(k), str(b[k]))
            self.assertEquals(b['title'], "foo")
            self.assertEquals(b['label'], "Label")
        return

    def testReportEvalResultUri(self):
        """
        Test report that selects one of the following test result status URIs from:
            http://purl.org/minim/minim#fullySatifies
            http://purl.org/minim/minim#nominallySatifies
            http://purl.org/minim/minim#minimallySatifies
            http://purl.org/minim/minim#potentiallySatisfies
        """
        rouristr  = "file:///usr/workspace/wf4ever-ro-catalogue/v0.1/simple-requirements/"
        checklist = "file:///usr/workspace/wf4ever-ro-manager/Checklists/runnable-wf-trafficlight/checklist.rdf"
        initvars  = (
            { 'target': rdflib.URIRef(rouristr)
            , 'minim':  rdflib.URIRef(checklist+"#Runnable_model") 
            })
        outstr   = StringIO.StringIO()
        rdfgraph = rdflib.Graph()
        rdfgraph.parse(trafficlight_test_data)
        RdfReport.generate_report(TrafficLightReports.EvalTargetResultUri, rdfgraph, initvars, outstr)
        expected = "http://purl.org/minim/minim#minimallySatisfies"
        result = outstr.getvalue()
        # print "\n-----"
        # print result
        # print "-----"
        self.assertEqual(expected, result)
        return

    def testReportEvalResultLabel(self):
        """
        Test report that selects a result label string
        """
        rouristr  = "file:///usr/workspace/wf4ever-ro-catalogue/v0.1/simple-requirements/"
        checklist = "file:///usr/workspace/wf4ever-ro-manager/Checklists/runnable-wf-trafficlight/checklist.rdf"
        initvars  = (
            { 'target': rdflib.URIRef(rouristr)
            , 'minim':  rdflib.URIRef(checklist+"#Runnable_model") 
            })
        outstr   = StringIO.StringIO()
        rdfgraph = rdflib.Graph()
        rdfgraph.parse(trafficlight_test_data)
        RdfReport.generate_report(TrafficLightReports.EvalTargetResultLabel, rdfgraph, initvars, outstr)
        expected = "minimally satisfies"
        result = outstr.getvalue()
        # print "\n-----"
        # print result
        # print "-----"
        self.assertEqual(expected, result)
        return

    def testReportEvalResultClass(self):
        """
        Test report of a textual status summary of a checklist match
        """
        rouristr  = "file:///usr/workspace/wf4ever-ro-catalogue/v0.1/simple-requirements/"
        checklist = "file:///usr/workspace/wf4ever-ro-manager/Checklists/runnable-wf-trafficlight/checklist.rdf"
        initvars  = (
            { 'target': rdflib.URIRef(rouristr)
            , 'minim':  rdflib.URIRef(checklist+"#Runnable_model") 
            })
        outstr   = StringIO.StringIO()
        rdfgraph = rdflib.Graph()
        rdfgraph.parse(trafficlight_test_data)
        RdfReport.generate_report(TrafficLightReports.EvalTargetResultClass, rdfgraph, initvars, outstr)
        expected = '"fail", "should"'
        result = outstr.getvalue()
        # print "\n-----"
        # print result
        # print "-----"
        self.assertEqual(expected, result)
        return

    def testReportEvalItemJSON(self):
        """
        Test report of a textual status summary of a checklist match
        """
        rouristr  = "file:///usr/workspace/wf4ever-ro-catalogue/v0.1/simple-requirements/"
        checklist = "file:///usr/workspace/wf4ever-ro-manager/Checklists/runnable-wf-trafficlight/checklist.rdf"
        initvars  = (
            { 'rouri':      rdflib.URIRef(rouristr)
            , 'modeluri':   rdflib.URIRef(checklist+"#Runnable_model") 
            , 'itemuri':    rdflib.URIRef(checklist+"#workflow_inputs_accessible")
            , 'itemlevel':  rdflib.URIRef("http://purl.org/minim/minim#missingShould")
            })
        outstr   = StringIO.StringIO()
        rdfgraph = rdflib.Graph()
        rdfgraph.parse(trafficlight_test_data)
        RdfReport.generate_report(TrafficLightReports.EvalItemJson, rdfgraph, initvars, outstr)
        expected = (
            [ ''
            , '''{ "itemuri":        "%s#workflow_inputs_accessible"'''%(checklist)
            , ''', "itemlabel":      '''+
              '''"Workflow %sdocs/mkjson.sh input %sdata/UserRequirements-astro.ods is not accessible"'''%
              (rouristr, rouristr)
            , ''', "itemlevel":      "http://purl.org/minim/minim#missingShould"'''
            , ''', "itemsatisfied":  false'''
            , ''', "itemclass":      ["fail", "should"]'''
            ])
        result = outstr.getvalue()
        # print "\n-----"
        # print result
        # print "-----"
        resultlines = result.split('\n')
        for i in range(len(expected)):
            self.assertEqual(expected[i], resultlines[i].strip())
        return

    def testTrafficlightJSON(self):
        """
        Test report generating traffic-light JSON (per data/mockup.json)
        """
        outstr   = StringIO.StringIO()
        rdfgraph = rdflib.Graph()
        rdfgraph.parse(trafficlight_test_data)
        RdfReport.generate_report(TrafficLightReports.EvalChecklistJson, rdfgraph, {}, outstr)
        # Test the non-item output only.  The previous test checks itemized output.
        expected = (
          [ ''''''
          , '''{ "rouri":                  "file:///usr/workspace/wf4ever-ro-catalogue/v0.1/simple-requirements/"'''
          , ''', "roid":                   "simple-requirements"'''
          , ''', "title":                  "A simple test RO"'''
          , ''', "description":            "A simple RO used for testing traffic light display."'''
          , ''', "checklisturi":           "file:///usr/workspace/wf4ever-ro-manager/Checklists/runnable-wf-trafficlight/checklist.rdf#Runnable_model"'''
          , ''', "checklistpurpose":       "Runnable"'''
          , ''', "checklisttarget":        "file:///usr/workspace/wf4ever-ro-catalogue/v0.1/simple-requirements/"'''
          , ''', "checklisttargetid":      "simple-requirements"'''
          , ''', "checklisttargetlabel":   "simple-requirements"'''
          , ''', "evalresult":             "http://purl.org/minim/minim#minimallySatisfies"'''
          , ''', "evalresultlabel":        "minimally satisfies"'''
          , ''', "evalresultclass":        ["fail", "should"]'''
          ])
        result = outstr.getvalue()
        log.debug("---- JSON result\n%s\n----"%(result))
        resultlines = result.split('\n')
        for i in range(len(expected)):
            self.assertEqual(expected[i], resultlines[i].strip())
        # Check that output is valid JSON
        resultdict = json.loads(result)
        self.assertEqual(resultdict['rouri'],
            "file:///usr/workspace/wf4ever-ro-catalogue/v0.1/simple-requirements/")
        return

    def testReportEvalItemHTML(self):
        """
        Test report of a textual status summary of a checklist match
        """
        rouristr  = "file:///usr/workspace/wf4ever-ro-catalogue/v0.1/simple-requirements/"
        checklist = "file:///usr/workspace/wf4ever-ro-manager/Checklists/runnable-wf-trafficlight/checklist.rdf"
        initvars  = (
            { 'rouri':      rdflib.URIRef(rouristr)
            , 'modeluri':   rdflib.URIRef(checklist+"#Runnable_model") 
            , 'itemuri':    rdflib.URIRef(checklist+"#workflow_inputs_accessible")
            , 'itemlevel':  rdflib.URIRef("http://purl.org/minim/minim#missingShould")
            })
        outstr   = StringIO.StringIO()
        rdfgraph = rdflib.Graph()
        rdfgraph.parse(trafficlight_test_data)
        RdfReport.generate_report(TrafficLightReports.EvalItemHtml, rdfgraph, initvars, outstr)
        expected = (
            [ ''
            , '''<tr class="sub_result">'''
            , '''<td></td>'''
            , '''<td class="trafficlight small fail should"><div/></td>'''
            , '''<td>Workflow %sdocs/mkjson.sh input %sdata/UserRequirements-astro.ods is not accessible</td>'''%
              (rouristr, rouristr)
            , '''</tr>'''
            ])
        result = outstr.getvalue()
        #print "\n-----"
        #print result
        #print "-----"
        resultlines = result.split('\n')
        for i in range(len(expected)):
            self.assertEqual(expected[i], resultlines[i].strip())
        return

    def testTrafficlightHTML(self):
        """
        Test report generating traffic-light HTML (per data/mockup.html)
        """
        rouristr  = "file:///usr/workspace/wf4ever-ro-catalogue/v0.1/simple-requirements/"
        outstr   = StringIO.StringIO()
        rdfgraph = rdflib.Graph()
        rdfgraph.parse(trafficlight_test_data)
        RdfReport.generate_report(TrafficLightReports.EvalChecklistHtml, rdfgraph, {}, outstr)
        # Test the non-item output only.  The previous test checks itemized output.
        expected = (
          [ '''<title>Research Object Runnable evaluation - simple-requirements</title>'''
          , '''</head>'''
          , '''<body>'''
          , '''<div class="Container">'''
          , '''<div class="header">'''
          , '''A simple test RO'''
          , '''</div>'''
          , '''<div class="content">'''
          , '''<div class="sub_header">A simple RO used for testing traffic light display.</div>'''
          , '''<div class="body">'''
          , '''<table>'''
          , '''<thead>'''
          , '''<tr class="main_result">'''
          , '''<th class="trafficlight large fail should"><div/></th>'''
          , '''<th colspan="2">Target <span class="target">'''
          , '''<a href="%s">simple-requirements</a></span>'''%(rouristr)
          , '''<span class="testresult">minimally satisfies</span> checklist for'''
          , '''<span class="testpurpose">Runnable</span>.'''
          # , '''<p>This Research Object @@TODO.</p>'''
          , '''</th>'''
          , '''</tr>'''
          ])
        result = outstr.getvalue()
        #print "\n-----"
        #print result
        #print "-----"
        resultlines = result.split('\n')
        for i in range(len(expected)):
            # Skip 1st 8 lines of generated HTML:
            self.assertEqual(expected[i], resultlines[i+8].strip())
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
            , "testEscapeJSON"
            , "testHelloWorld"
            , "testSimpleQuery"
            , "testSimpleQuotedJson"
            , "testSimpleQuotedHtml"
            , "testQueryResultMerge"
            , "testQueryResultPreBinding"
            , "testSequence"
            , "testAlternative"
            , "testAlternativeMissing"
            , "testRepetition"
            , "testRepetitionMax"
            , "testRepetitionAlt"
            , "testQueryForNesting"
            , "testNesting"
            , "testReportEvalResultUri"
            , "testReportEvalResultLabel"
            , "testReportEvalResultClass"
            , "testReportEvalItemJSON"
            , "testTrafficlightJSON"
            , "testReportEvalItemHTML"
            , "testTrafficlightHTML"
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
    return TestUtils.getTestSuite(TestRdfReport, testdict, select=select)

if __name__ == "__main__":
    TestUtils.runTests("TestRdfReport.log", getTestSuite, sys.argv)

# End.
