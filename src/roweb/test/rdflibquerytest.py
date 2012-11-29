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

log = logging.getLogger(__name__)

import rdflib

class TestRdfQuery(unittest.TestCase):
    def setUp(self):
        return

    def tearDown(self):
        return

    def testQuery(self):
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

            SELECT * WHERE { ?s dct:title ?title; rdfs:label ?label } ORDER DESC BY ?label
            """
        query = """
            PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX dct:     <http://purl.org/dc/terms/>

            SELECT * WHERE { ?s rdfs:label ?label . }
            """
        resp = rdfgraph.query(query, initBindings={ 'title': "foo" })
        self.assertEqual(resp.type, 'SELECT')
        bindings = resp.bindings
        count = 0
        print "\n-----"
        for b in bindings:
            count += 1
            print "Result bindings %d:"%count
            for k in b:
                print "%s: %s"%(str(k), str(b[k]))
            self.assertEquals(b['title'], "Title")
            self.assertEquals(b['label'], "Label")
        return

if __name__ == "__main__":
    tests = unittest.TestSuite()
    tests.addTest(TestRdfQuery('testQuery'))
    runner = unittest.TextTestRunner(verbosity=2)
    if tests: runner.run(tests)

# End.
