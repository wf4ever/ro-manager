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

from ro_prefixes import prefixes, turtle_prefixstr, sparql_prefixstr

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

    def testIntegerStringFilter(self):
        g = """
            :s1 :p1 "111" .
            :s2 :p2 222 .
            :s3 :p3 "notaninteger" .
            """
        # Note:
        # "FILTERs eliminate any solutions that, when substituted into the expression, 
        # either result in an effective boolean value of false or produce an error" 
        # -- http://www.w3.org/TR/rdf-sparql-query/#tests.
        #
        # Further, the str() of any valid integer is a non-blank string, which in SPARQL
        # yields an equivalent boolean value (EBV) of True.
        # Thus, only valid integer literals should be accepted.
        #
        q1 = """
            ASK { :s1 :p1 ?value . FILTER ( str(xsd:integer(?value)) ) }
            """ ;
        q2 = """
            ASK { :s2 :p2 ?value . FILTER ( str(xsd:integer(?value)) ) }
            """ ;
        q3 = """
            ASK { :s3 :p3 ?value . FILTER ( str(xsd:integer(?value)) ) }
            """ ;
        q3s = """
            SELECT * WHERE { :s3 :p3 ?value . FILTER ( str(xsd:integer(?value)) ) }
            """ ;
        self.doAskQuery(g, q1, True)
        self.doAskQuery(g, q2, True)
        r = self.doSelectQuery(g, q3s, expect=0)
        # print "\n----\n%s\n----"%(repr(r))
        self.doAskQuery(g, q3, False)
        return

    def testRegexFilter(self):
        g = """
            :s1 :p1 "111" .
            :s2 :p2 222 .
            :s3 :p3 "notaninteger" .
            """
        q1 = """
            ASK { :s1 :p1 ?value . FILTER(regex(?value, "^\\\\d+$")) }
            """ ;
        q2 = """
            ASK { :s2 :p2 ?value . FILTER(regex(?value, "^\\\\d+$")) }
            """ ;
        q3 = """
            ASK { :s3 :p3 ?value . FILTER(regex(?value, "^\\\\d+$")) }
            """ ;
        self.doAskQuery(g, q1, True)
        self.doAskQuery(g, q2, False)    # Is this correct?
        self.doAskQuery(g, q3, False)
        return

    # @unittest.skip("Currently 'OPTIONAL { filter(!bound(?label)) BIND(str(?s) as ?label) }' does not work")
    def testDefaultQuery(self):
        g1 = """
            :s1 a :test ; rdfs:label "s1" .
            """
        g2 = """
            :s2 a :test .
            """
        q1 = """
            SELECT * WHERE
            {
              ?s a :test .
              OPTIONAL { ?s rdfs:label ?label }{
              OPTIONAL { filter(!bound(?label)) BIND(str(?s) as ?label) }
            }
            """
        q2 = """
            SELECT ?s (COALESCE(?reallabel, ?genlabel) AS ?label) WHERE 
            { 
              ?s a :test . 
              BIND(str(?s) as ?genlabel) 
              OPTIONAL { ?s rdfs:label ?reallabel } 
            }
            """
        r1 = self.doSelectQuery(g1, q2, expect=1)
        # print "\n----\n%s\n----"%(repr(r1))
        self.assertEqual(r1[0]['s'],     rdflib.URIRef("http://example.org/s1"))
        self.assertEqual(r1[0]['label'], rdflib.Literal("s1"))
        r2 = self.doSelectQuery(g2, q2, expect=1)
        # print "\n----\n%s\n----"%(repr(r2))
        self.assertEqual(r2[0]['s'],     rdflib.URIRef("http://example.org/s2"))
        self.assertEqual(r2[0]['label'], rdflib.Literal("http://example.org/s2"))
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
        self.assertEqual(rdflib.Literal("def").value, "def")
        lit111 = rdflib.Literal("111", datatype=rdflib.URIRef("http://www.w3.org/2001/XMLSchema#integer"))
        self.assertEqual(lit111.value, 111)
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
            , "testIntegerStringFilter"
            , "testRegexFilter"
            , "testDefaultQuery"
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
