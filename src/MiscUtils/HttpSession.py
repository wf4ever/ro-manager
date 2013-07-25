# HTTP session class and supporting utilites.

import re   # Used for link header parsing
import httplib
import urlparse
import rdflib
import logging

# Logger for this module
log = logging.getLogger(__name__)


def splitValues(txt, sep=",", lq='"<', rq='">'):
    """
    Helper function returns list of delimited values in a string,
    where delimiters in quotes are protected.

    sep is string of separator
    lq is string of opening quotes for strings within which separators are not recognized
    rq is string of corresponding closing quotes
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



# Class for exceptions raised by HTTP session

class HTTP_Error(Exception):

    def __init__(self, msg="HTTP_Error", value=None, uri=None):
        self._msg   = msg
        self._value = value
        self._uri   = uri
        return

    def __str__(self):
        txt = self._msg
        if self._uri:   txt += " for "+str(self._uri)
        if self._value: txt += ": "+repr(self._value)
        return txt

    def __repr__(self):
        return ( "HTTP_Error(%s, value=%s, uri=%s)"%
                 (repr(self._msg), repr(self._value), repr(self._uri)))



# Class for handling Access in an HTTP session

class HTTP_Session(object):
    
    """
    Client access class for HTTP session.

    Creates a session to access a single HTTP endpoint,
    and provides methods to issue requests on this session
    """

    def __init__(self, baseuri, accesskey = None):
        log.debug("HTTP_Session.__init__: baseuri "+baseuri)
        self._baseuri = baseuri
        self._key     = accesskey
        parseduri     = urlparse.urlsplit(baseuri)
        self._scheme  = parseduri.scheme
        self._host    = parseduri.netloc
        self._path    = parseduri.path
        self._httpcon = httplib.HTTPConnection(self._host)
        return

    def close(self):
        self._key     = None
        self._httpcon.close()
        return

    def baseuri(self):
        return self._baseuri

    def error(self, msg, value=None):
        return HTTP_Error(msg=msg, value=value, uri=self._baseuri)

    def parseLinks(self, headers):
        """
        Parse link header(s), return dictionary of links keyed by link relation type
        """
        return parseLinks(headers["_headerlist"])

    def doRequest(
        self, uripath, method="GET", body=None, ctype=None, accept=None, reqheaders=None):
        """
        Perform HTTP request

        Return status, reason(text), response headers, response body
        """
        # Sort out path to use in HTTP request: request may be path or full URI or rdflib.URIRef
        uripath  = str(uripath)        # get URI string from rdflib.URIRef
        uriparts = urlparse.urlsplit(urlparse.urljoin(self._path,uripath))
        if uriparts.scheme:
            if self._scheme != uriparts.scheme:
                raise HTTP_Error(
                    "URI scheme mismatch",
                    value=uriparts.scheme,
                    baseuri=self._baseuri)
        if uriparts.netloc:
            if self._host != uriparts.netloc:
                raise HTTP_Error(
                    "URI host:port mismatch",
                    value=uriparts.netloc,
                    baseuri=self._baseuri)
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
        log.debug("HTTP_Session.doRequest method:     "+method)
        log.debug("HTTP_Session.doRequest path:       "+path)
        log.debug("HTTP_Session.doRequest reqheaders: "+repr(reqheaders))
        log.debug("HTTP_Session.doRequest body:       "+repr(body))
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
        log.debug("HTTP_Session.doRequest response: "+str(status)+" "+reason)
        log.debug("HTTP_Session.doRequest headers:  "+repr(headers))
        ###log.debug("HTTP_Session.doRequest data:     "+repr(data))
        return (status, reason, headers, data)

    def doRequestFollowRedirect(
        self, uripath, method="GET", body=None, ctype=None, accept=None, reqheaders=None):
        """
        Perform HTTP request, following any redirect returned

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

# End.
