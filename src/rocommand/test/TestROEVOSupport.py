import os, os.path, sys
from rocommand.test.TestConfig import ro_test_config
from urlparse import urljoin
from ROSRS_Session import ROSRS_Session
from ro_evo import get_location
from ro_utils import parse_job
import TestROSupport
try:
    # Running Python 2.5 with simplejson?
    import simplejson as json
except ImportError:
    import json


if __name__ == "__main__":
    # Add main project directory and ro manager directories to python path
    sys.path.append("../..")
    sys.path.append("..")

import rdflib
from MiscLib import TestUtils
from rocommand import ro, ro_utils, ro_manifest


class TestROEVOSupport(TestROSupport.TestROSupport):
    
    def createSnapshot(self, live_name,sp_name,freeze = True):
        service_uri = urljoin(ro_test_config.ROSRS_URI, "../evo/copy/")
        body = {
                'copyfrom': urljoin(ro_test_config.ROSRS_URI,live_name),
                'target': sp_name,
                'type': "SNAPSHOT",
                'finalize': ( "%s" % freeze).lower()
            }
        
        body = json.dumps(body)
        reqheaders = {
            'token': ro_test_config.ROSRS_ACCESS_TOKEN,
            'Slug' : sp_name,
        }       
        rosrs = ROSRS_Session(ro_test_config.ROSRS_URI, ro_test_config.ROSRS_ACCESS_TOKEN)
        (status, reason, headers, data) = rosrs.doRequest(uripath=service_uri, method="POST", body=body, ctype="application/json", reqheaders=reqheaders)
        job_location = get_location(headers)
        status = "RUNNING"
        while status == "RUNNING":
            (status, id) = parse_job(rosrs, job_location)
        assert  status == "DONE"
        return (status,id)
    
    def createArchive(self, live_name,sp_name,freeze = True):
        service_uri = urljoin(ro_test_config.ROSRS_URI, "../evo/copy/")
        body = {
                'copyfrom': urljoin(ro_test_config.ROSRS_URI,live_name),
                'target': sp_name,
                'type': "ARCHIVE",
                'finalize': ( "%s" % freeze).lower()
            }
        
        body = json.dumps(body)
        reqheaders = {
            'token': ro_test_config.ROSRS_ACCESS_TOKEN,
            'Slug' : sp_name,
        }       
        rosrs = ROSRS_Session(ro_test_config.ROSRS_URI, ro_test_config.ROSRS_ACCESS_TOKEN)
        (status, reason, headers, data) = rosrs.doRequest(uripath=service_uri, method="POST", body=body, ctype="application/json", reqheaders=reqheaders)
        job_location = get_location(headers)
        status = "RUNNING"
        while status == "RUNNING":
            (status, id) = parse_job(rosrs, job_location)
        return (status, id)
    
    # Sentinel/placeholder tests
    def freeze(self, ro_uri):
        rosrs = ROSRS_Session(ro_test_config.ROSRS_URI, ro_test_config.ROSRS_ACCESS_TOKEN)
        service_uri = urljoin(ro_test_config.ROSRS_URI, "../evo/finalize/")
        body = {
                'target': ro_uri,
        }
        body = json.dumps(body)
        reqheaders = {}
        (status, reason, headers, data) = rosrs.doRequest(uripath=service_uri, method="POST", body=body, ctype="application/json", reqheaders=reqheaders)
        job_location = get_location(headers)
        status = "RUNNING"
        while status == "RUNNING":
            (status, id) = parse_job(rosrs, job_location)
        return status
    
    def remote_status(self, ro_uri):
        rosrs = ROSRS_Session(ro_test_config.ROSRS_URI, ro_test_config.ROSRS_ACCESS_TOKEN)
        service_uri = ro_uri
        (status, reason, headers, data) = rosrs.doRequest(uripath=service_uri, method="POST", body="", ctype="application/json", reqheaders={})
        return status, reason, headers, data
    
    def testUnits(self):
        assert (True)

    def testComponents(self):
        assert (True)

    def testIntegration(self):
        assert (True)

    def testPending(self):
        assert (False), "Pending tests follow"

# Assemble test suite

def getTestSuite(select="unit"):
    """
    Get test suite

    select  is one of the following:
            "unit"      return suite of unit tests only
            "component" return suite of unit and component tests
            "all"       return suite of unit, component and integration tests
            "pending"   return suite of pending tests
            name        a single named test to be run
    """
    testdict = {
        "unit":
            [ "testUnits"
            ],
        "component":
            [ "testComponents"
            ],
        "integration":
            [ "testIntegration"
            ],
        "pending":
            [ "testPending"
            ]
        }
    return TestUtils.getTestSuite(TestROSupport, testdict, select=select)

if __name__ == "__main__":
    TestUtils.runTests("TestROSupport.log", getTestSuite, sys.argv)
    