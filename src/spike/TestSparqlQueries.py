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

import rdflib

# Stand-alone test: don't import from ro_prefixes

prefixes = (
    [ ("",          "http://example.org/")
    , ("rdf",       "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    , ("rdfs",      "http://www.w3.org/2000/01/rdf-schema#")
    , ("owl",       "http://www.w3.org/2002/07/owl#")
    , ("xsd",       "http://www.w3.org/2001/XMLSchema#")
    , ("xml",       "http://www.w3.org/XML/1998/namespace")
    ])

turtle_prefixstr = "\n".join([ "@prefix %s: <%s> ."%p for p in prefixes ]) + "\n\n"
sparql_prefixstr = "\n".join([ "PREFIX %s: <%s>"%p for p in prefixes ]) + "\n\n"

class TestSparqlQueries(unittest.TestCase):

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

    def testSimpleSelectQuery(self):
        g = """
            :s1 :p :o1 .
            :s2 :p :o2 .
            """
        q = """
            SELECT * WHERE { :s2 :p ?o }
            """
        r = self.doQuery(g, q)
        self.assertEqual(r.type, "SELECT", "Unexpected query response type: %s"%(r.type))
        self.assertEqual(len(r.bindings), 1, "Unexpected number of query matches %d"%(len(r.bindings)))
        print "----"
        print repr(r.bindings)
        print "----"
        b = r.bindings[0]
        self.assertEqual(len(b), 1)
        self.assertEqual(b['o'], rdflib.URIRef("http://example.org/o2"))
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
        r = self.doSelectQuery(g, q3s, expect=1)
        print "\n----\n%s\n----"%(repr(r))
        self.doAskQuery(g, q3, False)
        return

if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=1)
    tests = unittest.TestSuite()
    tests.addTest(TestSparqlQueries("testSimpleSelectQuery"))
    tests.addTest(TestSparqlQueries("testDatatypeFilter"))
    tests.addTest(TestSparqlQueries("testIntegerStringFilter"))
    runner.run(tests)

# End.
