# !/usr/bin/env python
#
# mkminim.py - create Minim description from tabular checklist description
#

import sys
import os
import os.path
import re
import optparse
import logging
logging.basicConfig()

log = logging.getLogger(__name__)

# Make sure MiscLib can be found on path
if __name__ == "__main__":
    sys.path.append(os.path.join(sys.path[0],".."))

import ro_utils

VERSION = "0.1"

def mkminim(grid, outstr, options):
    """
    Generate minim file from supplied grid
    """
    # Decode the grid
    try:
        pass
    except Exception, e:
        return 2
    # Create RDF graph
    # Add prefixes to graph
    # Add checklists to graph
    # Add models to graph
    # Add rules to graph
    # Serialize graph to output stream
    return

def run(configbase, options, args):
    """
    Access input file as grid, and generate Minim
    """
    status = 0
    progname = ro_utils.progname(args)
    # open spreadsheet file as grid
    grid = ...
    # Make minim file
    status = mkminim(grid)
    # Exit
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
                version="%prog "+VERSION)
    # parser.add_option("-a", "--all",
    #                   action="store_true",
    #                   dest="all",
    #                   default=False,
    #                   help="All, list all files, depends on the context")
    parser.add_option("-o", "--output",
                      dest="outformat",
                      help="Output format to generate: TEXT, RDFXML, TURTLE, etc.")
    # parse command line now
    (options, args) = parser.parse_args(argv)
    if len(args) < 2: parser.error("No checklist file specified")
    return (options, args)

def runCommand(userhome, filebase, argv):
    """
    Run program with supplied configuration base directory, Base directory
    from which to start looking for research objects, and arguments.

    This is called by main function (below), and also by test suite routines.

    Returns exit status.
    """
    (options, args) = parseCommandArgs(argv)
    if not options or options.debug:
        logging.basicConfig(level=logging.DEBUG)
    log.debug("runCommand: configbase %s, robase %s, argv %s"%(configbase, robase, repr(argv)))
    status = 1
    if options:
        status  = run(userthome, filebase, options, args)
    return status

def runMain():
    """
    Main program transfer function for setup.py console script
    """
    userhome = os.path.expanduser("~")
    filebase = os.getcwd()
    return runCommand(userhome, filebase, sys.argv)

if __name__ == "__main__":
    """
    Program invoked from the command line.
    """
    status = runMain()
    sys.exit(status)
