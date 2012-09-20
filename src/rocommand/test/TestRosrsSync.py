'''
Created on 15-09-2011

@author: piotrhol
'''
import sys
import urlparse
if __name__ == "__main__":
    # Add main project directory and ro manager directories at start of python path
    sys.path.insert(0, "../..")
    sys.path.insert(0, "..")

import logging
import os.path
import rdflib
from MiscLib import TestUtils
from rocommand import ro_annotation
from rocommand.test import TestROSupport
from rocommand.test.TestConfig import ro_test_config
from rocommand.ro_metadata import ro_metadata
from rocommand.ro_remote_metadata import ro_remote_metadata, createRO, deleteRO
from rocommand import ro_rosrs_sync
from rocommand.ro_namespaces import ROTERMS
from rocommand.ROSRS_Session import ROSRS_Session

# Local ro_config for testing
ro_config = {
    "annotationTypes":      ro_annotation.annotationTypes,
    "annotationPrefixes":   ro_annotation.annotationPrefixes
    }


# Logging object
log = logging.getLogger(__name__)

# Base directory for RO tests in this module
testbase = os.path.dirname(os.path.abspath(__file__))

class TestRosrsSync(TestROSupport.TestROSupport):
    

    def setUp(self):
        super(TestRosrsSync, self).setUp()
        self.rosrs = ROSRS_Session(ro_test_config.ROSRS_URI,
            accesskey=ro_test_config.ROSRS_ACCESS_TOKEN)
        return

    def tearDown(self):
        super(TestRosrsSync, self).tearDown()
        self.rosrs.close()
        return
    
    # Setup local config for local tests

    def setupConfig(self):
        return self.setupTestBaseConfig(testbase)

    def testNull(self):
        assert True, 'Null test failed'

    def testPush(self):
        rodir = self.createTestRo(testbase, "data/ro-test-1", "RO test push", "ro-testRoPush")
        localRo  = ro_metadata(ro_config, rodir)
        localRo.addAggregatedResources(rodir, recurse=True)
#        localRo.aggregateResourceExt("http://www.example.org")
        roresource = "subdir1/subdir1-file.txt"
        # Add anotations for file
        ann1 = localRo.addSimpleAnnotation(roresource, "type",         "Test file")
        ann2 = localRo.addSimpleAnnotation(roresource, "description",  "File in test research object")
        ann3 = localRo.addSimpleAnnotation(roresource, "rdf:type",     ROTERMS.resource)
        annotationsCnt = 0
        
        deleteRO(self.rosrs, urlparse.urljoin(self.rosrs.baseuri(), "TestPushRO/"))
        (_,_,rouri,_) = createRO(self.rosrs, "TestPushRO")
        remoteRo = ro_remote_metadata(ro_test_config, self.rosrs, rouri)
        remoteRo.aggregateResourceExt("http://www.anotherexample.org")
        
        resourcesInt = (
          [ rdflib.URIRef("README-ro-test-1")
          , rdflib.URIRef("minim.rdf")
          , rdflib.URIRef("subdir1/subdir1-file.txt")
          , rdflib.URIRef("subdir2/subdir2-file.txt")
          , rdflib.URIRef("filename%20with%20spaces.txt")
          , rdflib.URIRef("filename%23with%23hashes.txt")
          , rdflib.URIRef(ann1)
          , rdflib.URIRef(ann2)
          , rdflib.URIRef(ann3)
          ])
        resourcesIntCnt = 0
        
        for (action, resuri) in ro_rosrs_sync.pushResearchObject(localRo, remoteRo):
            log.debug("The following object has been pushed: %s (%s)"%(resuri, action))
            # this assumes that the above is the only external resource
            if action == ro_rosrs_sync.ACTION_AGGREGATE_EXTERNAL:
                self.assertEqual(resuri, rdflib.URIRef("http://www.example.org"), "The external resource is pushed")
                self.assertTrue(localRo.isAggregatedResource(resuri), "Resource that is pushed is aggregated locally")
            elif action == ro_rosrs_sync.ACTION_AGGREGATE_INTERNAL:
                self.assertTrue(localRo.getComponentUriRel(resuri) in resourcesInt, "Resource that is pushed is aggregated locally")
                resourcesIntCnt += 1
            elif action == ro_rosrs_sync.ACTION_DELETE:
                self.assertFalse(localRo.isAggregatedResource(resuri), "Resource that is deaggregated in ROSRS is not aggregated locally")
                self.assertEqual(resuri, rdflib.URIRef("http://www.anotherexample.org"), "The external resource is deaggregated (%s)"%resuri)
            elif action == ro_rosrs_sync.ACTION_AGGREGATE_ANNOTATION:
                self.assertTrue(localRo.isAnnotationNode(resuri), "Annotation that is pushed is aggregated locally (%s)"%(resuri))
                annotationsCnt += 1
            elif action == ro_rosrs_sync.ACTION_DELETE_ANNOTATION:
                self.assertFalse(localRo.isAnnotationNode(resuri), "Annotation that is deaggregated in ROSRS is not aggregated locally")
                pass
            else:
                self.fail("Unexpected action %s"%action)
        self.assertEqual(len(resourcesInt), resourcesIntCnt, "All internal resources were aggregated (should be %d was %d)"%(len(resourcesInt), resourcesIntCnt))
        # 3 annotations + manifest which in RO manager also annotates the RO
        self.assertEqual(4, annotationsCnt, "All annotations were aggregated (should be %d was %d)"%(4, annotationsCnt))
        
        for (action, resuri) in ro_rosrs_sync.pushResearchObject(localRo, remoteRo):
            if action == ro_rosrs_sync.ACTION_UPDATE_ANNOTATION:
                self.assertTrue(localRo.isAnnotationNode(resuri), "Annotations that is updated is aggregated locally (%s)"%(resuri))
            elif action == ro_rosrs_sync.ACTION_UPDATE_OVERWRITE:
                # see https://jira.man.poznan.pl/jira/browse/WFE-671
                self.assertTrue(resuri in [rdflib.URIRef(ann1), rdflib.URIRef(ann2), rdflib.URIRef(ann3)], "Annotation bodies can be uploaded twice")
            elif not action == ro_rosrs_sync.ACTION_SKIP:
                self.fail("Nothing else should be pushed again (%s, %s)"%(action, resuri))

        # Clean up
        remoteRo.delete()
        self.deleteTestRo(rodir)
        return
        
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
            , "testNull"
            ],
        "component":
            [ "testComponents"
            , "testPush"
            ],
        "integration":
            [ "testIntegration"
            ],
        "pending":
            [ "testPending"
            ]
        }
    return TestUtils.getTestSuite(TestRosrsSync, testdict, select=select)

if __name__ == "__main__":
    TestUtils.runTests("TestRosrsSync.log", getTestSuite, sys.argv)
