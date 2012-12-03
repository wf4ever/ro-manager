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

from MiscLib import TestUtils

from rocommand.ro_namespaces import RDF, DCTERMS, RO, AO, ORE

import rdfreport

# Base directory for RO tests in this module
testbase = os.path.dirname(os.path.abspath(__file__))

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
    PREFIX dct:     <http://purl.org/dc/terms/>
    PREFIX foaf:    <http://xmlns.com/foaf/0.1/>
    PREFIX ro:      <http://purl.org/wf4ever/ro#>
    PREFIX wfprov:  <http://purl.org/wf4ever/wfprov#>
    PREFIX wfdesc:  <http://purl.org/wf4ever/wfdesc#>
    PREFIX minim:   <http://purl.org/minim/minim#>
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
        rdfgraph.parse("data/simple-test-data.rdf")
        rdfreport.generate_report(report, rdfgraph, {}, outstr)
        self.assertEqual("Hello world", outstr.getvalue())
        return

    def testSimpleQuery(self):
        """
        Test a simple query report
        """
        report = (
            { 'report':
              { 'query':  prefixes+"SELECT * WHERE { ?s dct:creator ?creator }"
              , 'output': "Hello %(creator)s" }
            })
        outstr   = StringIO.StringIO()
        rdfgraph = rdflib.Graph()
        rdfgraph.parse("data/simple-test-data.rdf")
        rdfreport.generate_report(report, rdfgraph, {}, outstr)
        self.assertEqual("Hello Graham", outstr.getvalue())
        return

    def testQueryResultMerge(self):
        """
        Test a simple query merged with existing results
        """
        report = (
            { 'report':
              { 'query':  prefixes+"SELECT * WHERE { ?s dct:creator ?creator }"
              , 'output': "Hello %(creator)s and %(name)s"
              }
            })
        outstr   = StringIO.StringIO()
        rdfgraph = rdflib.Graph()
        rdfgraph.parse("data/simple-test-data.rdf")
        rdfreport.generate_report(report, rdfgraph, {'name': 'anyone'}, outstr)
        self.assertEqual("Hello Graham and anyone", outstr.getvalue())
        return

    def testQueryResultPreBinding(self):
        """
        Test a simple query with pre-bound result value
        """
        report = (
            { 'report':
              { 'query':  prefixes+"SELECT ?s ?creator ?label WHERE { ?s dct:creator ?creator; rdfs:label ?label }"
              , 'output': "Hello %(creator)s"
              }
            })
        outstr   = StringIO.StringIO()
        rdfgraph = rdflib.Graph()
        rdfgraph.parse("data/simple-test-data.rdf")
        rdfreport.generate_report(report, rdfgraph, {}, outstr)
        self.assertEqual("Hello Graham", outstr.getvalue())
        outstr   = StringIO.StringIO()
        rdfreport.generate_report(report, rdfgraph, {'label': 'simple-test-data'}, outstr)
        self.assertEqual("Hello Graham", outstr.getvalue())
        return

    def testSequence(self):
        """
        Test a sequence report
        """
        report = (
            { 'report':
              [ { 'output': "Foreword: " }
              , { 'query':  prefixes+"SELECT * WHERE { ?s dct:creator ?creator }"
                , 'output': "Hello %(creator)s; "
                }
              , { 'output': "afterword." }
              ]
            })
        outstr   = StringIO.StringIO()
        rdfgraph = rdflib.Graph()
        rdfgraph.parse("data/simple-test-data.rdf")
        rdfreport.generate_report(report, rdfgraph, {}, outstr)
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
        rdfgraph.parse("data/simple-test-data.rdf")
        rdfreport.generate_report(report, rdfgraph, {'name': "anyone"}, outstr)
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
        rdfgraph.parse("data/simple-test-data.rdf")
        rdfreport.generate_report(report, rdfgraph, {'name': "anyone"}, outstr)
        self.assertEqual("Foreword: afterword.", outstr.getvalue())
        return

    def testRepetition(self):
        """
        Test a report with a repeated match
        """
        report = (
            { 'report':
              [ { 'output': "Tags: " }
              , { 'query':  prefixes+"SELECT * WHERE { ?s dct:creator ?creator; ex:tag ?tag } ORDER BY ?tag"
                , 'output': "%(tag)s"
                , 'sep':    ", "
                }
              , { 'output': "." }
              ]
            })
        outstr   = StringIO.StringIO()
        rdfgraph = rdflib.Graph()
        rdfgraph.parse("data/simple-test-data.rdf")
        rdfreport.generate_report(report, rdfgraph, {}, outstr)
        self.assertEqual("Tags: tag1, tag2, tag3, tag4.", outstr.getvalue())
        return

    def testRepetitionMax(self):
        """
        Test a report with a repeated match
        """
        report = (
            { 'report':
              [ { 'output': "Tags: " }
              , { 'query':  prefixes+"SELECT * WHERE { ?s dct:creator ?creator; ex:tag ?tag } ORDER BY ?tag"
                , 'output': "%(tag)s"
                , 'sep':    ", "
                , 'max':    2
                }
              , { 'output': "." }
              ]
            })
        outstr   = StringIO.StringIO()
        rdfgraph = rdflib.Graph()
        rdfgraph.parse("data/simple-test-data.rdf")
        rdfreport.generate_report(report, rdfgraph, {}, outstr)
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
        rdfgraph.parse("data/simple-test-data.rdf")
        rdfreport.generate_report(report, rdfgraph, {}, outstr)
        self.assertEqual("Tags: none.", outstr.getvalue())
        return

    def testNesting(self):
        """
        Test a report with a nested sub-report
        """
        report = (
            { 'report':
              [ { 'query':  prefixes+
                            "SELECT ?s ?title ?label WHERE { ?s dct:title ?title; rdfs:label ?label } "+
                            "ORDER BY DESC(?label)"
                , 'output': "\nFound %(title)s:"
                , 'report':
                  [ {'output': "\nTags for %(label)s: " }
                  , { 'query':  prefixes+"SELECT ?tag WHERE { ?s ex:tag ?tag } ORDER BY ?tag"
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
        rdfgraph.parse("data/simple-test-data.rdf")
        rdfreport.generate_report(report, rdfgraph, {}, outstr)
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
        print "\n-----"
        print result
        print "-----"
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

            SELECT ?s ?label ?title WHERE { ?s dct:title ?title; rdfs:label ?label } ORDER DESC BY ?label
            """
        # query = """
        #     PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        #     PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
        #     PREFIX dct:     <http://purl.org/dc/terms/>
        # 
        #     SELECT ?s ?label ?title WHERE { ?s rdfs:label ?label . }
        #     """
        #     SELECT * WHERE { ?s rdfs:label ?label . }
        #     SELECT ?s ?title ?label WHERE { ?s rdfs:label ?label . }
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
            , "testHelloWorld"
            , "testSimpleQuery"
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
            #, "testTrafficlight"
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
