#!/usr/bin/python

"""
Context manager for running function with modified current working directory
"""

import sys, os

class SwitchWorkingDirectory:
    """
    Context handler class that swiches current working directory to
    a supplied value.
    """
    
    def __init__(self, targetgdir):
        self.targetgdir = targetgdir
        return
    
    def __enter__(self):
        self.savedcwd = os.getcwd()
        os.chdir(self.targetgdir)
        return 

    def __exit__(self, exctype, excval, exctraceback):
        os.chdir(self.savedcwd)
        return False

if __name__ == "__main__":
    cwd = os.getcwd()
    print cwd
    with SwitchWorkingDirectory("/tmp"):
        tmp = os.getcwd();
        print tmp
    assert os.getcwd() == cwd
    assert tmp != cwd

# End.
