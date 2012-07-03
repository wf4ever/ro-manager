#!/usr/bin/env python

"""
Module to test RO SRS APIfunctions
"""

import os, os.path
import sys
import unittest
import logging
import json
import StringIO
import httplib
#import urllib
import urlparse
import rdflib

from MiscLib import TestUtils

# Logging object
log = logging.getLogger(__name__)

# Class for HTTP session errors

class HTTPSessionError(Exception):

    def __init__(self, msg="HTTPSessionError", value=None, uri=None):
        self._msg    = msg
        self._value  = value
        self._uri = uri
        return

    def __str__(self):
        str = self._msg
        if self._uri:   str += " for "+self._uri
        if self._value: str += ": "+repr(value)
        return str

    def __repr__(self):
        return ( "HTTPSessionError(%s, value=%s, uri=%s)"%
                 (repr(self._msg), repr(self._value), repr(self._uri)))

# Class for handling HTTP access

class HTTP_Session(object):

    def __init__(self, uri, accesskey=None):
        self._uri     = uri
        self._key     = accesskey
        parseduri     = urlparse.urlsplit(uri)
        self._scheme  = parseduri.scheme
        self._host    = parseduri.netloc
        self._path    = parseduri.path
        self._httpcon = httplib.HTTPConnection(self._host)
        return

    def close(self):
        self._key = None
        self._httpcon.close()
        return

    def baseuri(self):
        return self._uri

    def error(self, msg, value):
        return HTTPSessionError(msg=msg, value=value, uri=self._uri)

    def parseLinks(headers):
        """
        Parse link header(s), return dictionary of links keyed by link relation type
        """
        linkvallist = [ v for (h,v) in headers["_headerlist"] if h == "link" ]
        links = {}
        for linkval in linkvallist:
            linkmatch = re.match(r'''\s*<([^>]*)>\s*;\s*rel\s*=\s*"([^"]*)"''', linkval)
            if linkmatch:
                links[linkmatch.group(2)] = rdflib.URIRef(linkmatch.group(1))
        return links

    def doRequest(self, uripath, method="GET", body=None, ctype=None, accept=None, reqheaders=None):
        """
        Perform HTTP request
        Return status, reason(text), response headers, response body
        """
        # Sort out path to use in HTTP request: request may be path or full URI or rdflib.URIRef
        uripath  = str(uripath)        # get URI string from rdflib.URIRef
        uriparts = urlparse.urlsplit(urlparse.urljoin(self._path,uripath))
        if uriparts.scheme:
            if self._scheme != uriparts.scheme:
                raise HTTPSessionError(
                    "HTTP session URI scheme mismatch",
                    value=uriparts.scheme,
                    uri=self._uri)
        if uriparts.netloc:
            if self._host != uriparts.netloc:
                raise HTTPSessionError(
                    "HTTP session URI host:port mismatch",
                    value=uriparts.netloc,
                    uri=self._uri)
        path = uriparts.path
        if uriparts.query: path += "?"+uriparts.query
        # Assemble request headers
        if not reqheaders:
            reqheaders = {}
        if self._key:
            reqheaders["authorization"] = "Bearer "+self._key
        if ctype:
            reqheaders["content-type"] = ctype
        if accept:
            reqheaders["accept"] = accept
        # Execute request
        self._httpcon.request(method, path, body, reqheaders)
        # Pick out elements of response
        response = self._httpcon.getresponse()
        status   = response.status
        reason   = response.reason
        headerlist = [ (h.lower(),v) for (h,v) in response.getheaders() ]
        headers  = dict(headerlist)   # dict(...) keeps last result of multiple keys
        headers["_headerlist"] = headerlist
        data = response.read()
        return (status, reason, headers, data)

    def doRequestRDF(self, uripath, method="GET", body=None, ctype=None, headers=None):
        """
        Perform HTTP request with RDF response.
        If requests succeeds, return response as RDF graph,
        or return fake 9xx status if RDF cannot be parsed
        otherwise return responbse and content per request.
        Thus, only 2xx responses include RDF data.
        """
        (status, reason, headers, data) = self.doRequest(uripath,
            method=method, body=body,
            ctype=ctype, accept="application/rdf+xml", headers=headers)
        if status >= 200 and status < 300:
            if headers["content-type"].lower() == "application/rdf+xml":
                rdfgraph = rdflib.Graph()
                try:
                    rdfgraph.parse(data=data, format="xml")
                    data = rdfgraph
                except Exception, e:
                    status   = 902
                    reason   = "RDF parse failure"
            else:
                status   = 901
                reason   = "Non-RDF content-type returned"
        return (status, reason, headers, data)

# End.
