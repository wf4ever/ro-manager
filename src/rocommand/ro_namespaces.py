# ro_namespaces.py

"""
Research Object manifest read, write, decode functions
"""

#import sys
#import os
#import os.path
#import re
#import urlparse
#import logging

import rdflib
import rdflib.namespace

class Namespace(object):
    def __init__(self, baseUri):
        self.baseUri = baseUri
        return

def makeNamespace(baseUri, names):
    ns = Namespace(baseUri)
    for name in names:
        setattr(ns, name, rdflib.URIRef(baseUri+name))
    return ns

ao      = rdflib.URIRef("http://purl.org/ao/")
ore     = rdflib.URIRef("http://www.openarchives.org/ore/terms/")
foaf    = rdflib.URIRef("http://xmlns.com/foaf/0.1/")
ro      = rdflib.URIRef("http://purl.org/wf4ever/ro#")
roevo   = rdflib.URIRef("http://purl.org/wf4ever/roevo#")
wfprov  = rdflib.URIRef("http://purl.org/wf4ever/wfprov#")
wfdesc  = rdflib.URIRef("http://purl.org/wf4ever/wfdesc#")
dcterms = rdflib.URIRef("http://purl.org/dc/terms/")
roterms = rdflib.URIRef("http://ro.example.org/ro/terms/")

RDF     = makeNamespace(rdflib.namespace.RDF.uri,
            [ "Seq", "Bag", "Alt", "Statement", "Property", "XMLLiteral", "List", "PlainLiteral"
            , "subject", "predicate", "object", "type", "value", "first", "rest"
            , "nil"
            ])
RDFS    = makeNamespace(rdflib.namespace.RDFS.uri,
            [ "Resource", "Class", "subClassOf", "subPropertyOf", "comment", "label"
            , "domain", "range", "seeAlso", "isDefinedBy", "Literal", "Container"
            , "ContainerMembershipProperty", "member", "Datatype"
            ])
RO = makeNamespace(ro, 
            [ "ResearchObject", "AggregatedAnnotation"
            , "annotatesAggregatedResource" # @@TODO: deprecated
            ])
ROEVO = makeNamespace(roevo, 
            [ "LiveRO"
            ])
ORE = makeNamespace(ore,
            [ "Aggregation", "AggregatedResource", "Proxy"
            , "aggregates", "proxyFor", "proxyIn"
            , "isDescribedBy"
            ])
AO = makeNamespace(ao, 
            [ "Annotation"
            , "body"
            , "annotatesResource"
            ])
DCTERMS = makeNamespace(dcterms, 
            [ "identifier", "description", "title", "creator", "created"
            , "subject", "format", "type"
            ])
ROTERMS = makeNamespace(roterms, 
            [ "note", "resource", "defaultBase"
            ])

# End.
