#!/usr/bin/python

"""
Test some SPARQL queries
"""

import os, os.path
import sys
import re
import shutil
import unittest
import logging
import datetime
import StringIO

if __name__ == "__main__":
    # Add main project directory and ro manager directories to python path
    sys.path.append("../..")
    sys.path.append("..")

import rdflib

from MiscLib import TestUtils
from TestConfig import ro_test_config
from StdoutContext import SwitchStdout

prefixes = (
    [ ("",          "http://example.org/")
    , ("rdf",       "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    , ("rdfs",      "http://www.w3.org/2000/01/rdf-schema#")
    , ("owl",       "http://www.w3.org/2002/07/owl#")
    , ("xsd",       "http://www.w3.org/2001/XMLSchema#")
    , ("xml",       "http://www.w3.org/XML/1998/namespace")
    , ("ro",        "http://purl.org/wf4ever/ro#")
    , ("wfprov",    "http://purl.org/wf4ever/wfprov#")
    , ("wfdesc",    "http://purl.org/wf4ever/wfdesc#")
    , ("wf4ever",   "http://purl.org/wf4ever/wf4ever#")
    , ("rdfg",      "http://www.w3.org/2004/03/trix/rdfg-1/")
    , ("ore",       "http://www.openarchives.org/ore/terms/")
    , ("ao",        "http://purl.org/ao/")
    , ("dcterms",   "http://purl.org/dc/terms/")
    , ("foaf",      "http://xmlns.com/foaf/0.1/")
    , ("minim",     "http://purl.org/minim/minim#")
    ])

turtle_prefixstr = "\n".join([ "@prefix %s: <%s> ."%p for p in prefixes ]) + "\n\n"
sparql_prefixstr = "\n".join([ "PREFIX %s: <%s>"%p for p in prefixes ]) + "\n\n"

class TestSparqlQueries(unittest.TestCase):
    """
    Test sparql queries
    """
    def setUp(self):
        super(TestSparqlQueries, self).setUp()
        return

    def tearDown(self):
        super(TestSparqlQueries, self).tearDown()
        return

    # Query test helpers

    def doQuery(self, graph, query, format="n3", initBindings=None):
        g = rdflib.Graph()
        s = StringIO.StringIO(turtle_prefixstr+graph)
        g.parse(s, format=format)
        # print "----"
        # print sparql_prefixstr+query
        # print "----"
        return g.query(sparql_prefixstr+query, initBindings=initBindings)

    def doAskQuery(self, graph, query, expect=True, format="n3", initBindings=None):
        r = self.doQuery(graph, query, format, initBindings)
        self.assertEqual(r.type, "ASK", "Unexpected query response type: %s"%(r.type))
        self.assertEqual(r.askAnswer, expect, "Unexpected query response %s"%(r.askAnswer))
        return r.askAnswer

    def doSelectQuery(self, graph, query, expect=None, format="n3", initBindings=None):
        r = self.doQuery(graph, query, format, initBindings)
        self.assertEqual(r.type, "SELECT", "Unexpected query response type: %s"%(r.type))
        self.assertEqual(len(r.bindings), expect, "Unexpected number of query matches %d"%(len(r.bindings)))
        return r.bindings

    # Query tests

    def testSimpleAskQuery(self):
        g = """
            :s :p :o .
            """
        q1 = """
            ASK { :s :p :o }
            """
        q2 = """
            ASK { :s :p ?o }
            """
        q3 = """
            ASK { :s1 :p ?o }
            """
        q4 = """
            ASK { :s :p1 ?o }
            """
        self.doAskQuery(g, q1, True)
        self.doAskQuery(g, q2, True)
        self.doAskQuery(g, q3, False)
        self.doAskQuery(g, q4, False)
        return

    def testSimpleSelectQuery(self):
        g = """
            :s1 :p :o1 .
            :s2 :p :o2 .
            """
        q1 = """
            SELECT * WHERE { :s1 :p :o1 }
            """
        q2 = """
            SELECT * WHERE { :s2 :p ?o }
            """
        q3 = """
            SELECT * WHERE { ?s :p ?o } ORDER BY ?s
            """
        q4 = """
            SELECT * WHERE { :s1 :p1 :o2 }
            """
        r = self.doSelectQuery(g, q1, expect=1)
        self.assertEqual(len(r[0]), 0)
        r = self.doSelectQuery(g, q2, expect=1)
        # print "----"
        # print repr(r)
        # print "----"
        self.assertEqual(len(r[0]), 1)
        self.assertEqual(r[0]['o'], rdflib.URIRef("http://example.org/o2"))
        r = self.doSelectQuery(g, q3, expect=2)
        self.assertEqual(len(r[0]), 2)
        self.assertEqual(r[0]['s'], rdflib.URIRef("http://example.org/s1"))
        self.assertEqual(r[0]['o'], rdflib.URIRef("http://example.org/o1"))
        self.assertEqual(len(r[1]), 2)
        self.assertEqual(r[1]['s'], rdflib.URIRef("http://example.org/s2"))
        self.assertEqual(r[1]['o'], rdflib.URIRef("http://example.org/o2"))
        r = self.doSelectQuery(g, q4, expect=0)
        return

    def testDatatypeFilter(self):
        g = """
            :s1 :p1 "text" .
            :s2 :p2 2 .
            """
        q1 = """
            ASK { :s1 :p1 ?o }
            """
        q2 = """
            ASK { :s1 :p1 ?o FILTER (datatype(?o) = xsd:string) }
            """
        q3 = """
            ASK { :s1 :p1 ?o FILTER (datatype(?o) = xsd:integer) }
            """
        q4 = """
            ASK { :s2 :p2 ?o }
            """
        q5 = """
            ASK { :s2 :p2 ?o FILTER (datatype(?o) = xsd:string) }
            """
        q6 = """
            ASK { :s2 :p2 ?o FILTER (datatype(?o) = xsd:integer) }
            """
        self.doAskQuery(g, q1, True)
        self.doAskQuery(g, q2, True)
        self.doAskQuery(g, q3, False)
        self.doAskQuery(g, q4, True)
        self.doAskQuery(g, q5, False)
        self.doAskQuery(g, q6, True)
        return

    def testGraphReadTerms(self):
        gturtle = """
            :s1 :p :o1 .
            :s2 :p "text" .
            """
        g = rdflib.Graph()
        s = StringIO.StringIO(turtle_prefixstr+gturtle)
        g.parse(s, format='n3')
        o = g.value(rdflib.URIRef("http://example.org/s1"), rdflib.URIRef("http://example.org/p"),  None)
        self.assertEqual(o, rdflib.URIRef("http://example.org/o1"))
        o = g.value(rdflib.URIRef("http://example.org/s2"), rdflib.URIRef("http://example.org/p"),  None)
        self.assertEqual(o, rdflib.Literal("text"))
        self.assertEqual(o.value, "text")
        return

    def testLiteralCompare(self):
        self.assertEqual(rdflib.Literal("abc").value, unicode("abc"))
        self.assertEqual(rdflib.Literal("abc").value, "abc")
        self.assertEqual("def", rdflib.Literal("def").value)
        return

    # Placeholder tests
        
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
            , "testSimpleAskQuery"
            , "testSimpleSelectQuery"
            , "testDatatypeFilter"
            , "testGraphReadTerms"
            , "testLiteralCompare"
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
    return TestUtils.getTestSuite(TestSparqlQueries, testdict, select=select)

if __name__ == "__main__":
    TestUtils.runTests("TestSparqlQueries.log", getTestSuite, sys.argv)

# End.
