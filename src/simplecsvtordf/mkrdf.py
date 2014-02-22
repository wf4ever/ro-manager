# !/usr/bin/env python

"""
mkminim.py - create Minim description from tabular checklist description
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2013, University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import os
import os.path
import re
import argparse
import logging
import csv

log = logging.getLogger(__name__)

# Make sure MiscUtils can be found on path
if __name__ == "__main__":
    sys.path.append(os.path.join(sys.path[0],".."))

import rdflib

from rocommand import ro_utils

from rocommand.ro_namespaces import RDF, makeNamespace

from simplecsvtordf.grid import GridCSV, GridExcel
from simplecsvtordf import gridmatch 
from simplecsvtordf import csvtordf

VERSION = "0.1"

columnnames = (
    [ "colA"
    , "colB"
    , "colC"
    , "colD"
    , "colE"
    , "colF"
    , "colG"
    , "colH"
    , "colI"
    , "colJ"
    , "colK"
    , "colL"
    , "colM"
    , "colN"
    , "colO"
    , "colP"
    , "colQ"
    , "colR"
    , "colS"
    , "colT"
    , "colU"
    , "colV"
    , "colW"
    , "colX"
    , "colY"
    ])

EX = makeNamespace("http://example.org/",
    [ "ColumnHeadingText", "RowData"
    , "colheadings", "row"] + columnnames
    )

def mkminim(grid, baseuri=None):
    """
    Generate RDF graph from supplied grid

    Returns (status,mgr) where mgr is RDF graph containing CSV data,
    or None.
    """
    # Decode the grid
    try:
        (d,(r,c)) = csvtordf.csvtordf.match(grid, 6, 0)
    except Exception, e:
        print "Failed to parse CSV table %s"%(e)
        return (2, None)
    # Create RDF graph and initialize Minim graph creation
    datagr = rdflib.Graph()
    datagr.bind("ex", rdflib.URIRef(EX.baseUri))
    datagr.add( (EX.colheadings, RDF.type, EX.ColumnHeadingText))
    for c in columnnames:
        datagr.add( (EX.colheadings, getattr(EX, c), rdflib.Literal(d[c])) )
    for r in d["datarows"]:
        b = rdflib.BNode()
        datagr.add( (b, RDF.type, EX.RowData) )
        for c in columnnames:
            datagr.add( (b, getattr(EX, c), rdflib.Literal(r[c])) )
    return (0,datagr)

def run(configbase, filebase, options, progname):
    """
    Access input file as grid, and generate Minim
    """
    status = 0
    # open spreadsheet file as grid
    log.debug("%s: open grid %s"%(progname, options.checklist))
    gridfilename = os.path.join(filebase,options.checklist)
    log.debug("CSV file: %s"%gridfilename)
    base = ""
    if gridfilename.endswith(".csv"):
        try:
            with open(gridfilename, "rU") as csvfile:
                grid = GridCSV(csvfile, baseuri="", dialect=csv.excel)
        except IOError, e:
            print "Failed to open grid CSV file %s"%(e)
            return 2
    elif gridfilename.endswith(".xls"):
        try:
            grid = GridExcel(gridfilename, baseuri="")
        except IOError, e:
            print "Failed to open grid XLS file %s"%(e)
            return 2
    else:
        print "Unrecognized grid file type %s; must be CSV or XLS."%(gridfilename)
        return 2
    # Make minim file
    log.debug("mkminim %s"%(repr(options)))
    (status, mgr) = mkminim(grid,  baseuri=grid.resolveUri(""))
    # Serialize graph to output stream
    if status == 0:
        mgr.serialize(sys.stdout, format=options.outformat)
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
    parser = argparse.ArgumentParser(
                description="Generate Minim RDF file from tabular checklist description.",
                epilog="The RDF Graph generated is written to standard output.")
    # parser.add_argument("-a", "--all",
    #                     action="store_true",
    #                     dest="all",
    #                     default=False,
    #                     help="All, list all files, depends on the context")
    parser.add_argument("checklist", help="File containing checklist description in tabular format")
    parser.add_argument('--version', action='version', version='%(prog)s '+VERSION)
    parser.add_argument("-o", "--output",
                        dest="outformat",
                        default="turtle",
                        help="Output format to generate: xml, turtle, n3, etc.  Default: 'turtle'.")
    parser.add_argument("--debug",
                        action="store_true", 
                        dest="debug", 
                        default=False,
                        help="Run with full debug output enabled")
    # parse command line now
    options = parser.parse_args(argv)
    log.debug("Options: %s"%(repr(options)))
    return options

def runCommand(configbase, filebase, argv):
    """
    Run program with supplied configuration base directory, Base directory
    from which to start looking for research objects, and arguments.

    This is called by main function (below), and also by test suite routines.

    Returns exit status.
    """
    options = parseCommandArgs(argv[1:])
    if not options or options.debug:
        logging.basicConfig(level=logging.DEBUG)
    log.debug("runCommand: configbase %s, filebase %s, argv %s"%(configbase, filebase, repr(argv)))
    # else:
    #     logging.basicConfig()
    status = 1
    if options:
        progname = ro_utils.progname(argv)
        status   = run(configbase, filebase, options, progname)
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
