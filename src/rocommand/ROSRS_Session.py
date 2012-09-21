"""
RO SRS session client implementation 
"""

import json # Used for service/resource info parsing
import re   # Used for link header parsing
import httplib
import urlparse
import rdflib, rdflib.graph
import logging

from ro_namespaces import RDF, ORE, RO, AO, DCTERMS

# Logging object
log = logging.getLogger(__name__)

# Annotation content types

ANNOTATION_CONTENT_TYPES = (
    { "application/rdf+xml":    "xml"
    , "text/turtle":            "n3"
    , "text/n3":                "n3"
    , "text/nt":                "nt"
    , "application/json":       "jsonld"
    , "application/xhtml":      "rdfa"
    })

ANNOTATION_TEMPLATE = ("""<?xml version="1.0" encoding="UTF-8"?>
    <rdf:RDF
       xmlns:ro="http://purl.org/wf4ever/ro#"
       xmlns:ao="http://purl.org/ao/"
       xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
       xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
       xml:base="%(xmlbase)s"
    >
       <ro:AggregatedAnnotation>
         <ao:annotatesResource rdf:resource="%(resuri)s" />
         <ao:body rdf:resource="%(bodyuri)s" />
       </ro:AggregatedAnnotation>
    </rdf:RDF>
    """)

# Class for ROSRS errors

class ROSRS_Error(Exception):

    def __init__(self, msg="ROSRS_Error", value=None, srsuri=None):
        self._msg    = msg
        self._value  = value
        self._srsuri = srsuri
        return

    def __str__(self):
        txt = self._msg
        if self._srsuri: txt += " for "+str(self._srsuri)
        if self._value:  txt += ": "+repr(self._value)
        return txt

    def __repr__(self):
        return ( "ROSRS_Error(%s, value=%s, srsuri=%s)"%
                 (repr(self._msg), repr(self._value), repr(self._srsuri)))

def splitValues(txt, sep=",", lq='"<', rq='">'):
    """
    Helper function returns list of delimited values in a string,
    where delimiters in quotes are protected.

    sep is string of separator
    lq is string of opening quotes for strings within which separators are not recognized
    rq is string of corresponding closing quotes
    
    @@TODO Is there a better way?  I tried using regexp, but grouping doesn't
    seem to offer a way to handle repeated elements.
    """
    result = []
    cursor = 0
    begseg = cursor
    while cursor < len(txt):
        if txt[cursor] in lq:
            # Skip quoted or bracketed string
            eq = rq[lq.index(txt[cursor])]  # End quote/bracket character
            cursor += 1
            while cursor < len(txt) and txt[cursor] != eq:
                if txt[cursor] == '\\': cursor += 1 # skip '\' quoted-pair
                cursor += 1
            if cursor < len(txt):
                cursor += 1 # Skip closing quote/bracket
        elif txt[cursor] in sep:
            result.append(txt[begseg:cursor])
            cursor += 1
            begseg = cursor
        else:
            cursor += 1
    # append final segment
    result.append(txt[begseg:cursor])
    return result

def testSplitValues():
    assert splitValues("a,b,c") == ['a','b','c']
    assert splitValues('a,"b,c",d') == ['a','"b,c"','d']
    assert splitValues('a, "b, c\\", c1", d') == ['a',' "b, c\\", c1"',' d']
    assert splitValues('a,"b,c",d', ";") == ['a,"b,c",d']
    assert splitValues('a;"b;c";d', ";") == ['a','"b;c"','d']
    assert splitValues('a;<b;c>;d', ";") == ['a','<b;c>','d']
    assert splitValues('"a;b";(c;d);e', ";", lq='"(', rq='")') == ['"a;b"','(c;d)','e']

def parseLinks(headerlist):
    """
    Helper function to parse 'link:' headers,
    returning a dictionary of links keyed by link relation type
    
    headerlist is a list of header (name,value) pairs
    """
    linkheaders = [ v for (h,v) in headerlist if h.lower() == "link" ]
    log.debug("parseLinks linkheaders %s"%(repr(linkheaders)))
    links = {}
    for linkheader in linkheaders:
        for linkval in splitValues(linkheader, ","):
            linkparts = splitValues(linkval, ";")
            linkmatch = re.match(r'''\s*<([^>]*)>\s*''', linkparts[0])
            if linkmatch:
                linkuri   = linkmatch.group(1)
                for linkparam in linkparts[1:]:
                    linkmatch = re.match(r'''\s*rel\s*=\s*"?(.*?)"?\s*$''', linkparam)  # .*? is non-greedy
                    if linkmatch:
                        linkrel = linkmatch.group(1)
                        log.debug("parseLinks links[%s] = %s"%(linkrel, linkuri))
                        links[linkrel] = rdflib.URIRef(linkuri)
    return links

def testParseLinks():
    links = (
        ('Link', '<http://example.org/foo>; rel=foo'),
        ('Link', ' <http://example.org/bar> ; rel = bar '),
        ('Link', '<http://example.org/bas>; rel=bas; par = zzz , <http://example.org/bat>; rel = bat'),
        ('Link', ' <http://example.org/fie> ; par = fie '),
        ('Link', ' <http://example.org/fum> ; rel = "http://example.org/rel/fum" '),
        ('Link', ' <http://example.org/fas;far> ; rel = "http://example.org/rel/fas" '),
        )
    assert str(parseLinks(links)['foo']) == 'http://example.org/foo'
    assert str(parseLinks(links)['bar']) == 'http://example.org/bar'
    assert str(parseLinks(links)['bas']) == 'http://example.org/bas'
    assert str(parseLinks(links)['bat']) == 'http://example.org/bat'
    assert str(parseLinks(links)['http://example.org/rel/fum']) == 'http://example.org/fum'
    assert str(parseLinks(links)['http://example.org/rel/fas']) == 'http://example.org/fas;far'

# Class for handling ROSRS access

class ROSRS_Session(object):
    
    """
    Client access class for RO SRS - creates a session to access a single ROSRS endpoint,
    and provides methods to access ROs and RO resources via the RO SRS API.
    
    See:
    * http://www.wf4ever-project.org/wiki/display/docs/RO+SRS+interface+6
    * http://www.wf4ever-project.org/wiki/display/docs/RO+evolution+API
    
    Related:
    * http://www.wf4ever-project.org/wiki/display/docs/User+Management+2
    """

    def __init__(self, srsuri, accesskey = None):
        log.debug("ROSRS_Session.__init__: srsuri "+srsuri)
        self._srsuri    = srsuri
        self._key       = accesskey
        parseduri       = urlparse.urlsplit(srsuri)
        self._srsscheme = parseduri.scheme
        self._srshost   = parseduri.netloc
        self._srspath   = parseduri.path
        self._httpcon   = httplib.HTTPConnection(self._srshost)
        return

    def close(self):
        self._key = None
        self._httpcon.close()
        return

    def baseuri(self):
        return self._srsuri

    def error(self, msg, value=None):
        return ROSRS_Error(msg=msg, value=value, srsuri=self._srsuri)

    def parseLinks(self, headers):
        """
        Parse link header(s), return dictionary of links keyed by link relation type
        """
        return parseLinks(headers["_headerlist"])

    def doRequest(
        self, uripath, method="GET", body=None, ctype=None, accept=None, reqheaders=None):
        """
        Perform HTTP request to ROSRS
        Return status, reason(text), response headers, response body
        """
        # Sort out path to use in HTTP request: request may be path or full URI or rdflib.URIRef
        uripath = str(uripath)        # get URI string from rdflib.URIRef
        uriparts = urlparse.urlsplit(urlparse.urljoin(self._srspath,uripath))
        if uriparts.scheme:
            if self._srsscheme != uriparts.scheme:
                raise ROSRS_Error(
                    "ROSRS URI scheme mismatch",
                    value=uriparts.scheme,
                    srsuri=self._srsuri)
        if uriparts.netloc:
            if self._srshost != uriparts.netloc:
                raise ROSRS_Error(
                    "ROSRS URI host:port mismatch",
                    value=uriparts.netloc,
                    srsuri=self._srsuri)
        path = uriparts.path
        if uriparts.query: path += "?"+uriparts.query
        # Assemble request headers
        if not reqheaders:
            reqheaders = {}
        reqheaders["authorization"] = "Bearer "+self._key
        if ctype:
            reqheaders["content-type"] = ctype
        if accept:
            reqheaders["accept"] = accept
        # Execute request
        log.debug("ROSRS_Session.doRequest method:     "+method)
        log.debug("ROSRS_Session.doRequest path:       "+path)
        log.debug("ROSRS_Session.doRequest reqheaders: "+repr(reqheaders))
        log.debug("ROSRS_Session.doRequest body:       "+repr(body))
        self._httpcon.request(method, path, body, reqheaders)
        # Pick out elements of response
        response = self._httpcon.getresponse()
        status   = response.status
        reason   = response.reason
        headerlist = [ (h.lower(),v) for (h,v) in response.getheaders() ]
        headers  = dict(headerlist)   # dict(...) keeps last result of multiple keys
        headers["_headerlist"] = headerlist
        data = response.read()
        if status < 200 or status >= 300: data = None
        log.debug("ROSRS_Session.doRequest response: "+str(status)+" "+reason)
        log.debug("ROSRS_Session.doRequest headers:  "+repr(headers))
        log.debug("ROSRS_Session.doRequest data:     "+repr(data))
        return (status, reason, headers, data)

    def doRequestFollowRedirect(
        self, uripath, method="GET", body=None, ctype=None, accept=None, reqheaders=None):
        """
        Perform HTTP request to ROSRS, following any redirect returned
        Return status, reason(text), response headers, final uri, response body
        """
        (status, reason, headers, data) = self.doRequest(uripath,
            method=method, accept=accept,
            body=body, ctype=ctype, reqheaders=reqheaders)
        if status in [302,303,307]:
            uripath = headers["location"]
            (status, reason, headers, data) = self.doRequest(uripath,
                method=method, accept=accept,
                body=body, ctype=ctype, reqheaders=reqheaders)
        if status in [302,307]:
            # Allow second temporary redirect
            uripath = headers["location"]
            (status, reason, headers, data) = self.doRequest(uripath,
                method=method,
                body=body, ctype=ctype, reqheaders=reqheaders)
        return (status, reason, headers, rdflib.URIRef(uripath), data)

    def doRequestRDF(self, uripath, method="GET", body=None, ctype=None, reqheaders=None):
        """
        Perform HTTP request with RDF response.
        If requests succeeds, return response as RDF graph,
        or return fake 9xx status if RDF cannot be parsed
        otherwise return response and content per request.
        Thus, only 2xx responses include RDF data.
        """
        (status, reason, headers, data) = self.doRequest(uripath,
            method=method, body=body,
            ctype=ctype, accept="application/rdf+xml", reqheaders=reqheaders)
        if status >= 200 and status < 300:
            if headers["content-type"].lower() == "application/rdf+xml":
                rdfgraph = rdflib.graph.Graph()
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

    def doRequestRDFFollowRedirect(self, uripath, method="GET", body=None, ctype=None, reqheaders=None):
        """
        Perform HTTP request to ROSRS, following any redirect returned
        Return status, reason(text), response headers, final uri, response body
        """
        (status, reason, headers, data) = self.doRequestRDF(uripath,
            method=method,
            body=body, ctype=ctype, reqheaders=reqheaders)
        if status in [302,303,307]:
            uripath = headers["location"]
            (status, reason, headers, data) = self.doRequestRDF(uripath,
                method=method,
                body=body, ctype=ctype, reqheaders=reqheaders)
        return (status, reason, headers, rdflib.URIRef(uripath), data)

    def listROs(self):
        """
        List ROs in service

        Result is list of dictionaries, where dict["uri"] is the URI of an RO.
        """
        (status, reason, headers, data) = self.doRequest("")
        if status < 200 or status >= 300:
            raise self.error("Error listing ROs", "%03d %s"%(status, reason))
        log.debug("ROSRS_session.listROs: %s"%(repr(data)))
        urilist = data.splitlines()
        return [ { "uri" : u } for u in urilist ]

    def createRO(self, id, title, creator, date):
        """
        Create a new RO, return (status, reason, uri, manifest):
        status+reason: 201 Created or 409 Exists
        uri+manifest: URI and copy of manifest as RDF graph if 201 status,
                      otherwise None and response data as diagnostic
        """
        reqheaders   = {
            "slug":     id
            }
        roinfo = {
            "id":       id,
            "title":    title,
            "creator":  creator,
            "date":     date
            }
        roinfotext = json.dumps(roinfo)
        (status, reason, headers, data) = self.doRequestRDF("",
            method="POST", body=roinfotext, reqheaders=reqheaders)
        log.debug("ROSRS_session.createRO: %03d %s: %s"%(status, reason, repr(data)))
        if status == 201:
            return (status, reason, rdflib.URIRef(headers["location"]), data)
        if status == 409:
            return (status, reason, None, data)
        #@@TODO: Create annotations for title, creator, date??
        raise self.error("Error creating RO", "%03d %s"%(status, reason))

    def deleteRO(self, rouri):
        """
        Delete an RO
        Return (status, reason), where status is 204 or 404
        """
        (status, reason, headers, data) = self.doRequest(rouri,
            method="DELETE",
            accept="application/rdf+xml")
        if status in [204, 404]:
            return (status, reason)
        raise self.error("Error deleting RO", "%03d %s"%(status, reason))

    def getROResource(self, resuriref, rouri=None, accept=None, reqheaders=None):
        """
        Retrieve resource from RO
        Return (status, reason, headers, data), where status is 200 or 404 or redirect code
        """
        resuri = str(resuriref)
        if rouri:
            resuri = urlparse.urljoin(str(rouri), resuri)
        (status, reason, headers, uri, data) = self.doRequestFollowRedirect(resuri,
            method="GET", accept=accept, reqheaders=reqheaders)
        if status in [200, 404]:
            return (status, reason, headers, uri, data)
        raise self.error("Error retrieving RO resource", "%03d %s (%s)"%(status, reason, resuriref))

    def getROResourceRDF(self, resuriref, rouri=None, reqheaders=None):
        """
        Retrieve RDF resource from RO
        Return (status, reason, headers, data), where status is 200 or 404
        """
        resuri = str(resuriref)
        if rouri:
            resuri = urlparse.urljoin(str(rouri), resuri)
        (status, reason, headers, uri, data) = self.doRequestRDFFollowRedirect(resuri,
            method="GET", reqheaders=reqheaders)
        if status in [200, 404]:
            return (status, reason, headers, uri, data)
        raise self.error("Error retrieving RO RDF resource", "%03d %s (%s)"%(status, reason, resuriref))

    def getROResourceProxy(self, resuriref, rouri):
        """
        Retrieve proxy description for resource.
        Return (proxyuri, manifest)
        """
        (status, reason, headers, manifesturi, manifest) = self.getROManifest(rouri)
        if status not in [200,404]:
            raise self.error("Error retrieving RO manifest", "%03d %s"%
                             (status, reason))
        proxyuri = None
        if status == 200:
            resuri = rdflib.URIRef(urlparse.urljoin(str(rouri), str(resuriref)))
            proxyterms = list(manifest.subjects(predicate=ORE.proxyFor, object=resuri))
            log.debug("getROResourceProxy proxyterms: %s"%(repr(proxyterms)))
            if len(proxyterms) == 1:
                proxyuri = proxyterms[0]
        return (proxyuri, manifest)

    def getROManifest(self, rouri):
        """
        Retrieve an RO manifest
        Return (status, reason, headers, uri, data), where status is 200 or 404
        """
        (status, reason, headers, uri, data) = self.doRequestRDFFollowRedirect(rouri,
            method="GET")
        if status in [200, 404]:
            return (status, reason, headers, uri, data)
        raise self.error("Error retrieving RO manifest",
            "%03d %s"%(status, reason))

    def getROLandingPage(self, rouri):
        """
        Retrieve an RO landing page
        Return (status, reason, headers, uri, data), where status is 200 or 404
        """
        (status, reason, headers, uri, data) = self.doRequestFollowRedirect(rouri,
            method="GET", accept="text/html")
        if status in [200, 404]:
            return (status, reason, headers, uri, data)
        raise self.error("Error retrieving RO landing page",
            "%03d %s"%(status, reason))

    def getROZip(self, rouri):
        """
        Retrieve an RO as ZIP file
        Return (status, reason, headers, data), where status is 200 or 404
        """
        (status, reason, headers, uri, data) = self.doRequestFollowRedirect(rouri,
            method="GET", accept="application/zip")
        if status in [200, 404]:
            return (status, reason, headers, uri, data)
        raise self.error("Error retrieving RO as ZIP file",
            "%03d %s"%(status, reason))

    def aggregateResourceInt(self,
        rouri, respath=None, ctype="application/octet-stream", body=None):
        """
        Aggegate internal resource
        Return (status, reason, proxyuri, resuri), where status is 200 or 201
        """
        # POST (empty) proxy value to RO ...
        reqheaders = respath and { "slug": respath }
        proxydata = ("""
            <rdf:RDF
              xmlns:ore="http://www.openarchives.org/ore/terms/"
              xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" >
              <ore:Proxy>
              </ore:Proxy>
            </rdf:RDF>
            """)
        (status, reason, headers, data) = self.doRequest(rouri,
            method="POST", ctype="application/vnd.wf4ever.proxy",
            reqheaders=reqheaders, body=proxydata)
        if status != 201:
            raise self.error("Error creating aggregation proxy",
                            "%03d %s (%s)"%(status, reason, respath))
        proxyuri = rdflib.URIRef(headers["location"])
        links    = self.parseLinks(headers)
        log.debug("- links: "+repr(links))
        log.debug("- ORE.proxyFor: "+str(ORE.proxyFor))
        if str(ORE.proxyFor) not in links:
            raise self.error("No ore:proxyFor link in create proxy response",
                            "Proxy URI %s"%str(proxyuri))
        resuri   = rdflib.URIRef(links[str(ORE.proxyFor)])
        # PUT resource content to indicated URI
        (status, reason, headers, data) = self.doRequest(resuri,
            method="PUT", ctype=ctype, body=body)
        if status not in [200,201]:
            raise self.error("Error creating aggregated resource content",
                "%03d %s (%s)"%(status, reason, respath))
        return (status, reason, proxyuri, resuri)

    def aggregateResourceExt(self, rouri, resuri):
        """
        Aggegate external resource
        Return (status, reason, proxyuri, resuri), where status is 200 or 201
        """
        # Aggegate external resource: POST proxy ...
        proxydata = ("""
            <rdf:RDF
              xmlns:ore="http://www.openarchives.org/ore/terms/"
              xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" >
              <ore:Proxy>
                <ore:proxyFor rdf:resource="%s" />
              </ore:Proxy>
            </rdf:RDF>
            """)%str(resuri)
        (status, reason, headers, data) = self.doRequest(rouri,
            method="POST", ctype="application/vnd.wf4ever.proxy",
            body=proxydata)
        if status != 201:
            raise self.error("Error creating aggregation proxy",
                "%03d %s (%s)"%(status, reason, str(resuri)))
        proxyuri = rdflib.URIRef(headers["location"])
        links    = self.parseLinks(headers)
        return (status, reason, proxyuri, rdflib.URIRef(resuri))

    def removeResource(self, rouri, resuri):
        """
        Remove resource from aggregation (internal or external)
        return (status, reason), where status is 204 No content or 404 Not found
        """
        # Find proxy for resource
        (proxyuri, manifest) = self.getROResourceProxy(resuri, rouri)
        if proxyuri == None:
            return (404, "Resource proxy not found in manifest")
        assert isinstance(proxyuri, rdflib.URIRef)
        # Delete proxy
        (status, reason, headers, uri, data) = self.doRequestFollowRedirect(proxyuri,
            method="DELETE")
        return (status, reason)

    def createROAnnotationBody(self, rouri, anngr):
        """
        Create an annotation body from a supplied annnotation graph.
        
        Returns: (status, reason, bodyuri)
        """
        # Create annotation body
        (status, reason, bodyproxyuri, bodyuri) = self.aggregateResourceInt(rouri,
            ctype="application/rdf+xml",
            body=anngr.serialize(format="xml"))
        if status != 201:
            raise self.error("Error creating annotation body resource",
                "%03d %s (%s)"%(status, reason, str(resuri)))
        return (status, reason, bodyuri)

    def createAnnotationRDF(self, rouri, resuri, bodyuri):
        """
        Create entity body for annotation
        """
        annotation = (ANNOTATION_TEMPLATE%
            { "xmlbase": str(rouri)
            , "resuri": str(resuri)
            , "bodyuri": str(bodyuri)
            })
        return annotation

    def createROAnnotation(self, rouri, resuri, bodyuri):
        """
        Create an annotation stub for supplied resource using indicated body
        
        Returns: (status, reason, annuri)
        """
        annotation = self.createAnnotationRDF(rouri, resuri, bodyuri)
        (status, reason, headers, data) = self.doRequest(rouri,
            method="POST",
            ctype="application/vnd.wf4ever.annotation",
            body=annotation)
        if status != 201:
            raise self.error("Error creating annotation",
                "%03d %s (%s)"%(status, reason, str(resuri)))
        annuri   = rdflib.URIRef(headers["location"])
        return (status, reason, annuri)

    def createROAnnotationInt(self, rouri, resuri, anngr):
        """
        Create internal annotation
        
        Return (status, reason, annuri, bodyuri)
        """
        (status, reason, bodyuri) = self.createROAnnotationBody(rouri, anngr)
        if status == 201:
            (status, reason, annuri) = self.createROAnnotation(rouri, resuri, bodyuri)
        return (status, reason, annuri, bodyuri)

    def createROAnnotationExt(self, rouri, resuri, bodyuri):
        """
        Creeate a resource annotation using an existing (possibly external) annotation body
        
        Returns: (status, reason, annuri)
        """
        (status, reason, annuri) = self.createROAnnotation(rouri, resuri, bodyuri)
        return (status, reason, annuri)

    def updateROAnnotation(self, rouri, annuri, resuri, bodyuri):
        """
        Update an indicated annotation for supplied resource using indiocated body
        
        Returns: (status, reason)
        """
        annotation = self.createAnnotationRDF(rouri, resuri, bodyuri)
        (status, reason, headers, data) = self.doRequest(annuri,
            method="PUT",
            ctype="application/vnd.wf4ever.annotation",
            body=annotation)
        if status != 200:
            raise self.error("Error updating annotation",
                "%03d %s (%s)"%(status, reason, str(resuri)))
        return (status, reason)

    def updateROAnnotationInt(self, rouri, annuri, resuri, anngr):
        """
        Update an annotation with a new internal annotation body

        returns: (status, reason, bodyuri)
        """
        (status, reason, bodyuri) = self.createROAnnotationBody(rouri, anngr)
        assert status == 201
        (status, reason) = self.updateROAnnotation(rouri, annuri, resuri, bodyuri)
        return (status, reason, bodyuri)

    def updateROAnnotationExt(self, rouri, annuri, bodyuri):
        """
        Update an annotation with an existing (possibly external) annotation body

        returns: (status, reason)
        """
        (status, reason) = self.updateROAnnotation(rouri, annuri, resuri, bodyuri)
        return (status, reason)

    def getROAnnotationUris(self, rouri, resuri=None):
        """
        Enumerate annnotation URIs associated with a resource
        (or all annotations for an RO) 
        
        Returns an iterator over annotation URIs
        """
        (status, reason, headers, manifesturi, manifest) = self.getROManifest(rouri)
        if status != 200:
            raise self.error("No manifest",
                "%03d %s (%s)"%(status, reason, str(rouri)))
        for (a,p) in manifest.subject_predicates(object=resuri):
            # @@TODO: in due course, remove RO.annotatesAggregatedResource?
            if p in [AO.annotatesResource,RO.annotatesAggregatedResource]:
                yield a
        return

    def getROAnnotationBodyUris(self, rouri, resuri=None):
        """
        Enumerate annnotation body URIs associated with a resource
        (or all annotations for an RO) 
        
        Returns an iterator over annotation URIs
        """
        for annuri in self.getROAnnotationUris(rouri, resuri):
            yield self.getROAnnotationBodyUri(annuri)
        return

    def getROAnnotationBodyUri(self, annuri):
        """
        # Retrieve annotation for given annotation URI
        """
        #(status, reason, headers, uri, anngr) = self.getROResourceRDF(annuri)
        #bodyuri = anngr.value(subject=annuri, predicate=AO.body)
        #return bodyuri
        (status, reason, headers, anngr) = self.doRequestRDF(annuri)
        if status != 303:
            raise self.error("No redirect from annnotation URI",
                "%03d %s (%s)"%(status, reason, str(annuri)))
        return rdflib.URIRef(headers['location'])

    def getROAnnotationGraph(self, rouri, resuri=None):
        """
        Build RDF graph of annnotations associated with a resource
        (or all annotations for an RO) 
        
        Returns graph of merged annotations
        """
        agraph = rdflib.graph.Graph()
        for auri in self.getROAnnotationUris(rouri, resuri):
            (status, reason, headers, buri, bodytext) = self.doRequestFollowRedirect(auri)
            if status == 200:
                content_type = headers['content-type'].split(";", 1)[0]
                content_type = content_type.strip().lower()
                if content_type in ANNOTATION_CONTENT_TYPES:
                    bodyformat = ANNOTATION_CONTENT_TYPES[content_type]
                    agraph.parse(data=bodytext, format=bodyformat)
                else:
                    log.warn("getROResourceAnnotationGraph: %s has unrecognized content-type: %s"%
                             (str(buri),content_type))
            else:
                log.warn("getROResourceAnnotationGraph: %s read failure: %03d %s"%
                         (str(buri), status, reason))
        return agraph

    def getROAnnotation(self, annuri):
        """
        Retrieve annotation for given annotation URI
        
        Returns: (status, reason, bodyuri, anngr)
        """
        (status, reason, headers, uri, anngr) = self.getROResourceRDF(annuri)
        return (status, reason, uri, anngr)

    def removeROAnnotation(self, rouri, annuri):
        """
        Remove annotation at given annotation URI
        
        Returns: (status, reason)
        """
        (status, reason, headers, data) = self.doRequest(annuri,
            method="DELETE")
        return (status, reason)

    # ---------------------------------------------
    # RO Evolution
    # ---------------------------------------------
    # See: http://www.wf4ever-project.org/wiki/display/docs/RO+evolution+API

    # Need to fugure out how deferred values can work, associated with copyuri
    # e.g. poll, notification subscribe, sync options

    def copyRO(self, oldrouri, slug):
        assert False, "@@TODO"
        return (status, reason, copyuri)
        # copyuri ->  Deferred(oldrouri, rotype, rostatus, newrouri)

    def cancelCopyRO(self, copyuri):
        assert False, "@@TODO"
        return (status, reason)

    def updateROStatus(self, rouri, rostatus):
        assert False, "@@TODO"
        return (status, reason, updateuri)

    def getROEvolution(self, rouri):
        assert False, "@@TODO"
        return (status, reason, evogr)

# End.
