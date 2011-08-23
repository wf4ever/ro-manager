#!/usr/bin/python

"""
RO manager command parser and dispatcher
"""

import os
import os.path
import re
import codecs
import sys
import optparse
import logging
import ro_command

VERSION = "0.1 (ROBOX)"

def run(options, args):
    status = 0
    progname = os.path.split(args[0])[1]
    if args[1] == "help":
        status = ro_command.help(progname, args)
    else:
        print "%s: unrecognized command: %s"%(progname,args[1])
        status = 2
    return status

def parseCommandArgs(prog, argv):
    # create a parser for the command line options
    parser = optparse.OptionParser(
                usage="%prog [options] command [args...]\n\n",
                version="%prog "+VERSION)
    # version option
    parser.add_option("-v", "--verbose",
                      action="store_true", 
                      dest="verbose", 
                      default=False,
                      help="display verbose output")
    # parse command line now
    (options, args) = parser.parse_args(argv)
    if len(args) < 2: parser.error("No command present")
    if len(args) > 4: parser.error("Too many arguments present")
    return (options, args)


def runCommand(configbase, robase, argv):
    """
    Run program with supplied configuration base directory, RO base directory and
    arguments.
    
    This is called by main function (below), and also by test suite routines.
    
    Returns exit status.
    """
    (options, args) = parseCommandArgs("ro", argv)
    status = 1
    if options:
        status  = run(options, args)
    return status

if __name__ == "__main__":
    """
    Program invoked from the command line.
    """
    configbase = os.path.expanduser("~")
    robase = os.getcwd()
    status = runCommand(configbase, robase, sys.argv)
    sys.exit(status)

#--------+---------+---------+---------+---------+---------+---------+---------+
