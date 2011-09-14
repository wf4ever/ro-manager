'''
Created on 14-09-2011

@author: piotrhol
'''
import unittest
import sys
from sync.RosrsSync import RosrsSync
from sync.test.TestConfig import ro_test_config


if __name__ == "__main__":
    # Add main project directory and ro manager directories to python path
    sys.path.append("../..")
    sys.path.append("..")

class Test(unittest.TestCase):

    def testROCreation(self):
        RosrsSync().post_workspace(ro_test_config.ROSRS_HOST, ro_test_config.ROSRS_USERNAME, ro_test_config.ROSRS_PASSWORD)
        RosrsSync().delete_workspace(ro_test_config.ROSRS_HOST, ro_test_config.ROSRS_USERNAME)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testROCreation']
    unittest.main()