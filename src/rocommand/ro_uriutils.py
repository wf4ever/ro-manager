# ro_metadata.py

"""
Helper functions for manipulasting and testing URIs and URI-related file paths,
and for accessing or testing data at a URI reference.
"""

import sys
import os
import os.path
import re
import urllib
import urlparse
import logging

import ROSRS_Session

log = logging.getLogger(__name__)

fileuribase = "file://"

def isFileUri(uri):
    return uri.startswith(fileuribase)

def resolveUri(uriref, base, path=""):
    """
    Resolve a URI reference against a supplied base URI and path (supplied as strings).
    (The path is a local file system path, and may need converting to use URI conventions)
    """
    upath = urllib.pathname2url(path)
    if os.path.isdir(path) and not upath.endswith('/'):
        upath = upath + '/'
    return urlparse.urljoin(urlparse.urljoin(base, upath), uriref)

def resolveFileAsUri(path):
    """
    Resolve a filename reference against the current working directory, and return the
    corresponding file:// URI.
    
    If the supplied string is already a URI, it is returned unchanged
    (for idempotency and non-file URIs)
    """
    if urlparse.urlsplit(path).scheme == "":
        path = resolveUri("", fileuribase, os.path.join(os.getcwd(), path))
    return path

def getFilenameFromUri(uri):
    """
    Convert a file:// URI into a local file system reference
    """
    uriparts = urlparse.urlsplit(uri)
    assert uriparts.scheme == "file", "RO %s is not in local file system"%uri
    uriparts = urlparse.SplitResult("","",uriparts.path,uriparts.query,uriparts.fragment)
    return urllib.url2pathname(urlparse.urlunsplit(uriparts))

def isLiveUri(uriref):
    """
    Test URI reference to see if it refers to an accessible resource
    
    Relative URI references are assumed to be local file system references,
    relartive to the current working directory.
    """
    islive  = False
    fileuri = resolveFileAsUri(uriref)
    if isFileUri(fileuri):
        islive = os.path.exists(getFilenameFromUri(fileuri))
    else:
        hs = ROSRS_Session(uriref)
        (status, reason, headers, body) = hs.doRequest(uriref, method="HEAD")
        islive = (status == 200)
    return islive

def retrieveUri(uriref):
    uri = resolveUri(uriref, fileuribase, os.getcwd())
    request  = urllib2.Request(uri)
    try:
        response = urllib2.urlopen(request)
        result   = response.read()
    except:
        result = None
    return result

# End.
