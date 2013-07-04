# !/usr/bin/env python
#
# mkminim.py - create Minim description from tabular checklist description
#

import sys
import os
import os.path
import re
import argparse
import logging
import csv
import rdflib

log = logging.getLogger(__name__)

# Make sure MiscLib can be found on path
if __name__ == "__main__":
    sys.path.append(os.path.join(sys.path[0],".."))

from rocommand import ro_utils

from checklist import gridmatch 
from checklist import checklist_template 

VERSION = "0.1"

def mkminim(grid, outstr, options):
    """
    Generate minim file from supplied grid
    """
    # Decode the grid
    try:
        (d,(r,c)) = checklist_template.checklist.match(grid, 0, 0)
    except Exception, e:
        print "Failed to parse minim table %s"%(e)
        return 2
    # Create RDF graph and initialize Minim graph creation
    mgr = Minim_graph()
    # Add prefixes to graph
    for pre in d["prefixes"]:
        mgr.prefix(pre, d["prefixes"][pre])
    # Add checklists to graph
    for cl in d["checklists"]:
        mgr.checklist(purpose=cl["purpose"], model=cl["model"], target=cl["target_urit"])
    # Add models to graph
    for cm in d["models"]:
        mgr.model(cm["modelid"],
            [ mgr.item(seq=mi["seq"], level=mi["level"], reqid=["reqid"])
                for mi in cm["items"]
            ])
    # Add requirement rules to graph
    for rq in d["requirements"]:
        if rq.haskey("foreach"):
            # ForEach ...
            mgr.rule(rq["reqid"], 
                ForEach=rq["foreach"], 
                Exists=rq.get("exists"),
                Min=rq.get("min"),
                Max=rq.get("max"), 
                IsAggregated=rq.get("aggregates"), 
                IsLive=rq.get("islive"), 
                Show=rq.get("show")
                Pass=rq.get("pass"), 
                Fail=rq.get("fail"), 
                NoMatch=rq.get("miss"))
        elif rq.haskey("exists"):
            # Simple exists
            mgr.rule(rq["reqid"], 
                Exists=rq["exists"], 
                Show=rq.get("show")
                Pass=rq.get("pass"), 
                Fail=rq.get("fail"), 
                NoMatch=rq.get("miss"))
        elif rq.haskey("command"):
            mgr.rule(rq["reqid"], 
                Command=rq["command"],
                Response=rq["response"], 
                Show=rq.get("show")
                Pass=rq.get("pass"), 
                Fail=rq.get("fail"), 
                NoMatch=rq.get("miss"))
    # Serialize graph to output stream
    mgr.serialize(sys.stdout)
    return

def run(configbase, filebase, options, args):
    """
    Access input file as grid, and generate Minim
    """
    status = 0
    progname = ro_utils.progname(args)
    # open spreadsheet file as grid
    log.debug("Open grid %s"%(args[1]))
    csvname = os.path.join(filebase,args[1])
    log.debug("CSV file: %s"%csvname)
    base = ""
    try:
        with open(csvname, "rU") as csvfile:
            grid = gridmatch.GridCSV("", csvfile, dialect=csv.excel)
    except IOError, e:
        print "Failed to open table file %s"%(e)
        return 2
    # Make minim file
    log.debug("mkminim %s"%(repr(options)))
    status = mkminim(grid, sys.stdout, options)
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
                usage="\n  %prog [options] minim-table-input"+
                      "\n  %prog --help"+
                      "\n"+
                      "\nminim-table-input is file conmtaining minim-defining table in CSV format",
                version="%prog "+VERSION)
    # parser.add_option("-a", "--all",
    #                   action="store_true",
    #                   dest="all",
    #                   default=False,
    #                   help="All, list all files, depends on the context")
    parser.add_option("-o", "--output",
                      dest="outformat",
                      help="Output format to generate: ...")
    parser.add_option("--debug",
                      action="store_true", 
                      dest="debug", 
                      default=False,
                      help="run with full debug output enabled")
    # parse command line now
    (options, args) = parser.parse_args(argv)
    if len(args) < 2: parser.error("No checklist file specified")
    return (options, args)

def runCommand(configbase, filebase, argv):
    """
    Run program with supplied configuration base directory, Base directory
    from which to start looking for research objects, and arguments.

    This is called by main function (below), and also by test suite routines.

    Returns exit status.
    """
    (options, args) = parseCommandArgs(argv)
    if not options or options.debug:
        logging.basicConfig(level=logging.DEBUG)
    # else:
    #     logging.basicConfig()
    log.debug("runCommand: configbase %s, filebase %s, argv %s"%(configbase, filebase, repr(argv)))
    status = 1
    if options:
        status  = run(configbase, filebase, options, args)
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
