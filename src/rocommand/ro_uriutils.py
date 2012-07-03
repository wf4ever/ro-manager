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

log = logging.getLogger(__name__)

fileuribase = "file://"

def isFileUri(uri):
    return uri.startswith(fileuribase)

def resolveUri(uriref, base, path=""):
    """
    Resolve a URI reference against a supplied base URI and path.
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
    
    If the supplied string is already a URI, it is returned unchanged (for idepmpotency)
    """
    if urlparse.urlsplit(path).scheme == "":
        path = resolveUri("", fileuribase, os.path.join(os.getcwd(), path))
    return path

def getFilenameFromUri(uri):
    assert isFileUri(uri), "RO %s is not in local file system"%uri
    return uri[len(fileuribase):]

def isLiveUri(uriref):
    #@@TODO
    return False

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
