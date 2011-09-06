# $Id: TestSuperGlobal.py 1047 2009-01-15 14:48:58Z graham $
#
# Unit testing for SuperGlobal module
# See http://pyunit.sourceforge.net/pyunit.html
#

import sys
import unittest

sys.path.append("../..")
from MiscLib.SuperGlobal import *

class TestSuperGlobal(unittest.TestCase):

    def setUp(self):
        return

    def tearDown(self):
        return

    # Test cases

    def testCreateSuperGlobal(self):
        sg = SuperGlobal()
        sg.i1 = 1
        sg.s1 = "s1"
        self.assertEqual(sg.i1, 1)
        self.assertEqual(sg.s1, "s1")

    def testRetrieveSuperGlobal(self):
        self.testCreateSuperGlobal()
        sg = SuperGlobal()
        self.assertEqual(sg.i1, 1)
        self.assertEqual(sg.s1, "s1")

    def testUpdateSuperGlobal(self):
        self.testCreateSuperGlobal()
        sg = SuperGlobal()
        sg.i2 = 2
        sg.s2 = "s2"
        self.assertEqual(sg.i1, 1)
        self.assertEqual(sg.s1, "s1")
        self.assertEqual(sg.i2, 2)
        self.assertEqual(sg.s2, "s2")
        sg2 = SuperGlobal()
        sg2.i1 = 11
        sg2.s1 = "s11"
        self.assertEqual(sg.i1, 11)
        self.assertEqual(sg.s1, "s11")
        self.assertEqual(sg.i2, 2)
        self.assertEqual(sg.s2, "s2")

# Code to run unit tests directly from command line.
def getTestSuite():
    suite = unittest.TestSuite()
    suite.addTest(TestSuperGlobal("testCreateSuperGlobal"))
    suite.addTest(TestSuperGlobal("testRetrieveSuperGlobal"))
    suite.addTest(TestSuperGlobal("testUpdateSuperGlobal"))
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(getTestSuite())

# End.
