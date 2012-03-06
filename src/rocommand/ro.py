#!/usr/bin/env python

"""
RO manager command parser and dispatcher
"""

import sys
import os
import os.path
import re
import codecs
import optparse
import logging

log = logging.getLogger(__name__)

# Make sure MiscLib can be found on path
if __name__ == "__main__":
    sys.path.append(os.path.join(sys.path[0],".."))

import ro_settings
import ro_command
import ro_utils

def run(configbase, options, args):
    status = 0
    progname = ro_utils.progname(args)
    if args[1] == "help":
        status = ro_command.help(progname, args)
    elif args[1] == "config":
        status = ro_command.config(progname, configbase, options, args)
    elif args[1] == "create":
        status = ro_command.create(progname, configbase, options, args)
    elif args[1] == "add":
        status = ro_command.add(progname, configbase, options, args)
    elif args[1] == "status":
        status = ro_command.status(progname, configbase, options, args)
    elif args[1] == "list" or args[1] == "ls":
        status = ro_command.list(progname, configbase, options, args)
    elif args[1] == "annotate":
        status = ro_command.annotate(progname, configbase, options, args)
    elif args[1] == "annotations":
        status = ro_command.annotations(progname, configbase, options, args)
    elif args[1] == "evaluate" or args[1] == "eval":
        status = ro_command.evaluate(progname, configbase, options, args)
    elif args[1] == "push":
        status = ro_command.push(progname, configbase, options, args)
    elif args[1] == "checkout":
        status = ro_command.checkout(progname, configbase, options, args)
    else:
        print "%s: unrecognized command: %s"%(progname,args[1])
        status = 2
    return status

def parseCommandArgs(argv):
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
    parser.add_option("-r", "--rosrs-uri",
                      dest="rosrs_uri", 
                      help="URI of ROSRS service")
    parser.add_option("-u", "--rosrs-username",
                      dest="rosrs_username", 
                      help="ROSRS username")
    parser.add_option("-p", "--rosrs-password",
                      dest="rosrs_password", 
                      help="ROSRS password")
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
    parser.add_option("-f", "--force",
                      action="store_true",
                      dest="force", 
                      default=False,
                      help="Force, depends on the context")
    parser.add_option("-a", "--all",
                      action="store_true",
                      dest="all", 
                      default=False,
                      help="All, list all files, depends on the context")
    # parse command line now
    (options, args) = parser.parse_args(argv)
    if len(args) < 2: parser.error("No command present")
    if len(args) > 6: parser.error("Too many arguments present: "+repr(args))
    return (options, args)

def runCommand(configbase, robase, argv):
    """
    Run program with supplied configuration base directory, Base directory 
    from which to start looking for research objects, and arguments.
    
    This is called by main function (below), and also by test suite routines.
    
    Returns exit status.
    """
    log.debug("runCommand: configbase %s, robase %s, argv %s"%(configbase, robase, repr(argv)))
    (options, args) = parseCommandArgs(argv)
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
