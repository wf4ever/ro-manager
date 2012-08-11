#!/usr/bin/env python

import sys, os, os.path

from MiscLib import TestUtils

def runTestSuite():
    """
    Transfer function for setup.py script ro-manager-test
    """
    base = os.path.dirname(__file__)
    os.chdir(base)
    #print "Run test suite assuming base path "+base
    sys.path.insert(0, os.path.normpath(base+"/..") )
    sys.path.insert(0, os.path.normpath(base+"/../..") )
    sys.path.insert(0, os.path.normpath(base+"/../../iaeval/test") )
    sys.path.insert(0, os.path.normpath(base+"/../../sync/test") )
    #print "Path: "+repr(sys.path)
    import TestAll
    TestUtils.runTests("TestAll", TestAll.getTestSuite, sys.argv)
    return 0
