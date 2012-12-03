#!/usr/bin/python

import os, os.path
import sys
import re
import shutil
import logging
import datetime
import StringIO
import json
import unittest


if __name__ == '__main__':
    sys.path.insert(0, "/usr/workspace/github-rdfextras")
    sys.path.insert(0, "/usr/workspace/github-rdflib")
    logging.basicConfig()

log  = logging.getLogger(__file__)
here = os.path.dirname(os.path.abspath(__file__))

log = logging.getLogger(__name__)

import rdflib

testdata1 = """<?xml version="1.0" encoding="UTF-8"?>
    <rdf:RDF
       xmlns:xml="http://www.w3.org/XML/1998/namespace"
       xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
       xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
       xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
       xmlns:dct="http://purl.org/dc/terms/"
       xmlns:ex="http://example.org/terms/"
    >
      <rdf:Description rdf:about="test1.rdf">
        <rdfs:label>Label</rdfs:label>
        <dct:title>Title</dct:title>
      </rdf:Description>
    </rdf:RDF>
    """

testdata2 = """<?xml version="1.0" encoding="UTF-8"?>
    <rdf:RDF
       xmlns:xml="http://www.w3.org/XML/1998/namespace"
       xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
       xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
       xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
       xmlns:dct="http://purl.org/dc/terms/"
       xmlns:ex="http://example.org/terms/"
    >
      <rdf:Description rdf:about="test1.rdf">
        <rdfs:label>Label</rdfs:label>
        <dct:title>Title</dct:title>
      </rdf:Description>
      <rdf:Description rdf:about="test2.rdf">
        <rdfs:label>Label2</rdfs:label>
        <dct:title>Title2</dct:title>
      </rdf:Description>
      <rdf:Description rdf:about="test3.rdf">
        <rdfs:label>Label3</rdfs:label>
        <dct:title>Title3</dct:title>
      </rdf:Description>
    </rdf:RDF>
    """

class TestRdfQuery(unittest.TestCase):
    def setUp(self):
        return

    def tearDown(self):
        return

    def testQuery1(self):
        teststream = StringIO.StringIO(testdata)
        rdfgraph = rdflib.Graph()
        rdfgraph.parse(teststream)
        if True:
            print "\n-----"
            for s, p, o in rdfgraph:
                print str(s)
                print str(p)
                print str(o)
                print "---"
        query1 = """
            PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX dct:     <http://purl.org/dc/terms/>

            SELECT * WHERE { ?s dct:title ?title; rdfs:label ?label } 
            ORDER DESC BY ?s
            """
        query2 = """
            PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX dct:     <http://purl.org/dc/terms/>

            SELECT * WHERE { ?s rdfs:label ?label . }
            """
        resp = rdfgraph.query(query1)
        #resp = rdfgraph.query(query2, initBindings={ 'title': "foo" })
        self.assertEqual(resp.type, 'SELECT')
        bindings = resp.bindings
        count = 0
        print "\n-----"
        for b in bindings:
            count += 1
            print "Result bindings %d:"%count
            print repr(b)
            for k in b:
                print "%s: %s"%(str(k), str(b[k]))
        for b in bindings:
            self.assertEquals(b['title'], "Title")
            self.assertEquals(b['label'], "Label")
        return

    def testQuery1(self):
        teststream = StringIO.StringIO(testdata1)
        rdfgraph = rdflib.Graph()
        rdfgraph.parse(teststream)
        if False:
            print "\n-----"
            for s, p, o in rdfgraph:
                print str(s)
                print str(p)
                print str(o)
                print "---"
        query1 = """
            PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX dct:     <http://purl.org/dc/terms/>

            SELECT * WHERE { ?s dct:title ?title; rdfs:label ?label } 
            ORDER DESC BY ?s
            """
        resp = rdfgraph.query(query1)
        self.assertEqual(resp.type, 'SELECT')
        bindings = resp.bindings
        count = 0
        print "\n-----"
        for b in bindings:
            count += 1
            print "Result bindings %d:"%count
            print repr(b)
            for k in b:
                print "%s: %s"%(str(k), str(b[k]))
        for b in bindings:
            self.assertEquals(b['title'], "Title")
            self.assertEquals(b['label'], "Label")
        return

    def testQuery2(self):
        teststream = StringIO.StringIO(testdata1)
        rdfgraph = rdflib.Graph()
        rdfgraph.parse(teststream)
        if False:
            print "\n-----"
            for s, p, o in rdfgraph:
                print str(s)
                print str(p)
                print str(o)
                print "---"
        query2 = """
            PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX dct:     <http://purl.org/dc/terms/>

            SELECT * WHERE { ?s rdfs:label ?label . }
            """
        resp = rdfgraph.query(query2, initBindings={ 'title': "foo" })
        self.assertEqual(resp.type, 'SELECT')
        bindings = resp.bindings
        count = 0
        print "\n-----"
        for b in bindings:
            count += 1
            print "Result bindings %d:"%count
            print repr(b)
            for k in b:
                print "%s: %s"%(str(k), str(b[k]))
        for b in bindings:
            self.assertEquals(b['title'], "foo")
            self.assertEquals(b['label'], "Label")
        return

if __name__ == "__main__":
    tests = unittest.TestSuite()
    tests.addTest(TestRdfQuery('testQuery1'))
    tests.addTest(TestRdfQuery('testQuery2'))
    runner = unittest.TextTestRunner(verbosity=2)
    if tests: runner.run(tests)

# End.
