# !/usr/bin/env python
#
# generate-ro.py - create synthetic RO with specified number and size of annotations
#

import sys
import os
import os.path
import re
import argparse
import logging
import datetime

log = logging.getLogger(__name__)

import rdflib
from rdflib.namespace import XSD

# Make sure rocommand, etc., can be found on the path, overriding installed copy
if __name__ == "__main__":
    sys.path.insert(0, os.path.join(sys.path[0],"../.."))

from rocommand import ro_settings, ro_utils

from rocommand.ro_namespaces import RDF, DCTERMS, RO, AO, ORE

VERSION = "0.1"

PREFIXES = (
    [ ("rdf",     "http://www.w3.org/1999/02/22-rdf-syntax-ns#" )
    , ("ro",      "http://purl.org/wf4ever/ro#" )
    , ("ore",     "http://www.openarchives.org/ore/terms/" )
    , ("ao",      "http://purl.org/ao/" )
    , ("dcterms", "http://purl.org/dc/terms/" )
    , ("foaf",    "http://xmlns.com/foaf/0.1/" )
    ])

RESNAMETEMPLATE = "res%d"
RESREFTEMPLATE  = "subject/res%d.txt"
RESDIR          = "subject"
ANNGROUPTEMPLATE   = """
    @prefix ex: <http://example.org/> .

    <%(base)ssubject/%(key)s.txt>
        ex:key1 "simple literal" ;
        ex:key2 <http://example.org/object/%(key)s/%(subkey)s> ;
        ex:key3 [ a ex:blanknode ;
            ex:key31 "another literal" ;
            ex:key32 <http://example.org/object32/%(key)s/%(subkey)s> ;
            ex:key33 33 ;
            ex:key34 [ a ex:blanknode ;
                ex:key341 "and yet another literal" ;
                ex:key342 <http://example.org/object342/%(key)s/%(subkey)s> ;
                ex:key343 333 ;
                ]
            ]
        .
    """


def mkannotation(base, key, size, baseuri=None):
    """
    Generate annotation graph.

    key     is unique string to ensure uniqueness of statements generated
    size    is number triple-groups to generate

    Returns RDF annotation graph
    """
    # Create RDF graph and initialize Minim graph creation
    anngr = rdflib.Graph()
    for i in range(size):
        d = { "base": base, "key": key, "subkey": "obj"+str(i) }
        anngr.parse(data=(ANNGROUPTEMPLATE%d), format="text/turtle")
    return anngr


def mkro(filebase, options):
    # Sort out RO directory, etc
    roname  = options.roname or "benchmark_ro"
    robase  = os.path.realpath(filebase)
    rodir   = os.path.abspath(os.path.join(robase, roname))
    baseuri = "file://" + rodir + "/"
    log.debug("rodir:        " + rodir)
    manifestdir = os.path.join(rodir, ro_settings.MANIFEST_DIR)
    log.debug("manifestdir:  " + manifestdir)
    manifestfile = os.path.join(manifestdir, ro_settings.MANIFEST_FILE)
    log.debug("manifestfile: " + manifestfile)
    subjectdir = os.path.join(rodir, RESDIR)

    # Create directory for manifest, etc.
    try:
        os.makedirs(manifestdir)
    except OSError:
        if os.path.isdir(manifestdir):
            # Someone else created it...
            # See http://stackoverflow.com/questions/273192/
            #          python-best-way-to-create-directory-if-it-doesnt-exist-for-file-write
            pass
        else:
            # There was an error on creation, so make sure we know about it
            raise

    # Create directory for subject resources
    try:
        os.makedirs(subjectdir)
    except OSError:
        if os.path.isdir(subjectdir):
            # Someone else created it...
            pass
        else:
            # There was an error on creation, so make sure we know about it
            raise

    # Create manifest graph
    mangr       = rdflib.Graph()
    rouri       = rdflib.URIRef(baseuri)
    manifesturi = rdflib.URIRef(baseuri+ro_settings.MANIFEST_REF)
    timenowlit  = rdflib.Literal(datetime.datetime.now().isoformat(), datatype=XSD.date)
    for (pre, uri) in PREFIXES:
        mangr.bind(pre, uri)
    mangr.add( (rouri, RDF.type,            RO.ResearchObject)             )
    mangr.add( (rouri, DCTERMS.identifier,  rdflib.Literal("Identifier"))  )
    mangr.add( (rouri, DCTERMS.title,       rdflib.Literal("Title"))       )
    mangr.add( (rouri, DCTERMS.description, rdflib.Literal("Description")) )
    mangr.add( (rouri, DCTERMS.creator,     rdflib.Literal("creator"))     )
    mangr.add( (rouri, DCTERMS.created,     timenowlit)                    )
    n = rdflib.BNode()
    mangr.add( (rouri, ORE.aggregates,      n)                             )
    mangr.add( (n,     RDF.type,            RO.AggregatedAnnotation)       )
    mangr.add( (n,     RO.annotatesAggregatedResource, rouri)              )
    mangr.add( (n,     AO.body,             manifesturi)                   )

    # Create aggregated resources to annotate
    annresref = [ RESREFTEMPLATE%(anum) for anum in range(options.num_annotations)]
    for resref in annresref:
        resstr  = open("%s/%s"%(roname,resref), "w")
        resstr.write("Annotated resource %s\n"%(resref))
        resstr.close()
        mangr.add( (rouri, ORE.aggregates, rdflib.URIRef(rouri+resref)) )

    # Create annotations
    if options.outformat in ["turtle", "text/turtle"]:
        outext = ".ttl"
    elif options.outformat in ["n3", "text/n3"]:
        outext = ".n3"
    elif options.outformat in ["xml", "rdfxml", "application/rdf+xml"]:
        outext = ".rdf"
    for anum in range(options.num_annotations):
        key = RESNAMETEMPLATE%anum
        anngr = mkannotation(baseuri, key, options.size_annotations, baseuri=rouri)
        annfile = os.path.join(manifestdir, key+outext)
        annuri  = rdflib.URIRef("file://"+annfile)
        annstr  = open(annfile, "w")
        anngr.serialize(annstr, format=options.outformat)
        annstr.close()
        # Add annotation to manifest
        n = rdflib.BNode()
        mangr.add( (rouri, ORE.aggregates,      n)                       )
        mangr.add( (n,     RDF.type,            RO.AggregatedAnnotation) )
        mangr.add( (n,     RO.annotatesAggregatedResource, rouri)        )
        mangr.add( (n,     AO.body,             annuri)                  )

    # Serialize manifest graph
    manstr  = open(manifestfile, "w")
    mangr.serialize(manstr, format=ro_settings.MANIFEST_FORMAT)
    manstr.close()
    return 0

def run(configbase, filebase, options, progname):
    """
    Access input file as grid, and generate Minim
    """
    status = mkro(filebase, options)
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
                description="Generate synthetic RO with annotations for benchmark testing.",
                epilog="The RDF Graph generated is written to standard output.")
    # parser.add_argument("-a", "--all",
    #                     action="store_true",
    #                     dest="all",
    #                     default=False,
    #                     help="All, list all files, depends on the context")
    parser.add_argument('roname', help="Name of research object to create")
    parser.add_argument('--version', action='version', version='%(prog)s '+VERSION)
    parser.add_argument("-o", "--output",
                        dest="outformat",
                        default="turtle",
                        help="Output format to generate: xml, turtle, n3, etc.  Default: 'turtle'.")
    parser.add_argument("-n", "--num-annotations",
                        dest="num_annotations",
                        type=int,
                        default=1,
                        help="Number of distinct annotation bodies.")
    parser.add_argument("-s", "--size-annotations",
                        dest="size_annotations",
                        type=int,
                        default=1,
                        help="Size of each annotation body (triples *11)")
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
    Run program with supplied configuration base directory, directory
    in which to create research object, and arguments.

    This is called by main function (below), and also by test suite routines.

    Returns exit status.
    """
    options = parseCommandArgs(argv[1:])
    if not options or options.debug:
        logging.basicConfig(level=logging.DEBUG)
    log.debug("runCommand: configbase %s, filebase %s, argv %s"%(configbase, filebase, repr(argv)))
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

