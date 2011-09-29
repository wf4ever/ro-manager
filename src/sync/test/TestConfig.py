#!/usr/bin/python

"""
Configuration module for RO manager tests
"""

import base64
import uuid

class ro_test_config:
#    ROSRS_HOST     = "sandbox.wf4ever-project.org"
    ROSRS_HOST     = "calatola.man.poznan.pl"
    ROSRS_USERNAME = "test-" + base64.encodestring(str(uuid.uuid1()))[0:22]
    ROSRS_PASSWORD = "pass"
    RO_DIR         = "ro-test-1"
    RO_ID          = "ro1-identifier"
    VER_ID         = "v1"
    RO_ID_2        = "ro-test-2"

# End.
