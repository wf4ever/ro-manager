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
import ro_settings
import ro_command

def run(configbase, options, args):
    status = 0
    progname = os.path.split(args[0])[1]
    if args[1] == "help":
        status = ro_command.help(progname, args)
    elif args[1] == "config":
        status = ro_command.config(progname, configbase, options, args)
    elif args[1] == "create":
        status = ro_command.create(progname, configbase, options, args)
    elif args[1] == "status":
        status = ro_command.status(progname, configbase, options, args)
    else:
        print "%s: unrecognized command: %s"%(progname,args[1])
        status = 2
    return status

def parseCommandArgs(prog, argv):
    """
    Parse command line arguments
    
    prog -- program name from command line
    argv -- argument list from command line
    
    Returns a pair consisting of options specified as returned by
    OptionParser, and any remaining unparsed arguments.
    """
    # create a parser for the command line options
    parser = optparse.OptionParser(
                usage="%prog [options] command [args...]\n\n",
                version="%prog "+ro_settings.VERSION)
    # version option
    parser.add_option("-d", "--ro-directory",
                      dest="rodir", 
                      help="Directory of Research Object to process (defaults to current directory)")
    parser.add_option("-i", "--ro-identifier",
                      dest="roident", 
                      help="Identifier of Research Object (defaults to value based on name)")
    parser.add_option("-r", "--robox-uri",
                      dest="roboxuri", 
                      help="URI of ROBOX service")
    parser.add_option("-p", "--robox-password",
                      dest="roboxpassword", 
                      help="Local directory monitored by ROBOX")
    parser.add_option("-b", "--robox-base",
                      dest="roboxdir", 
                      help="Base of local directory tree monitored by ROBOX")
    parser.add_option("-n", "--user-name",
                      dest="username", 
                      help="Full name of research objects owner")
    parser.add_option("-e", "--user-email",
                      dest="useremail", 
                      help="Email address of research objects owner")
    parser.add_option("-v", "--verbose",
                      action="store_true", 
                      dest="verbose", 
                      default=False,
                      help="display verbose output")
    # parse command line now
    (options, args) = parser.parse_args(argv)
    if len(args) < 2: parser.error("No command present")
    if len(args) > 4: parser.error("Too many arguments present: "+repr(args))
    return (options, args)

def runCommand(configbase, robase, argv):
    """
    Run program with supplied configuration base directory, RO base directory 
    and arguments.
    
    This is called by main function (below), and also by test suite routines.
    
    Returns exit status.
    """
    (options, args) = parseCommandArgs("ro", argv)
    status = 1
    if options:
        status  = run(configbase, options, args)
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
