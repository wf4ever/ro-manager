#!/usr/bin/python

"""
RO manager parameter settings
"""

import __init__
VERSION_NUM   = __init__.__version__

RO_VERSION      = "v"+VERSION_NUM
VERSION         = RO_VERSION+" (RODL)"
MANIFEST_DIR    = ".ro"
MANIFEST_FILE   = "manifest.rdf"
MANIFEST_FORMAT = "application/rdf+xml"
MANIFEST_REF    = MANIFEST_DIR + "/" + MANIFEST_FILE
REGISTRIES_FILE = ".registries.json"

# End.
