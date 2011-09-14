# ro_command.py

"""
Basic command functions for ro, research object manager
"""

import sys
import os
import os.path
import readline # enable input editing for raw_input
import re
import datetime
import logging
import rdflib

log = logging.getLogger(__name__)

import MiscLib.ScanDirectories

import ro_settings
import ro_utils
import ro_manifest
from ro_manifest import RDF, DCTERMS

def getoptionvalue(val, prompt):
    if not val:
        if sys.stdin.isatty():
            val = raw_input(prompt)
        else:
            val = sys.stdin.readline()
            if val[-1] == '\n': val = val[:-1]    
    return val

def ro_root_directory(cmdname, ro_config, rodir):
    """
    Find research object root directory

    Returns directory path string, or None if not found, in which
    case an error message is displayed.
    """
    log.debug("ro_root_directory: cmdname %s, rodir %s"%(cmdname, rodir))
    log.debug("                   ro_config %s"%(repr(ro_config)))
    ro_dir = ro_utils.ropath(ro_config, rodir)
    if not ro_dir:
        print ("%s: indicated directory not in configured research object directory tree: %s"%
               (cmdname, rodir))
        return None
    if not os.path.isdir(ro_dir):
        print ("%s: indicated directory does not exist: %s"%
               (cmdname, rodir))
        return None
    manifestdir = None
    ro_dir_next = ro_dir
    ro_dir_prev = ""
    log.debug("ro_dir_next %s, ro_dir_prev %s"%(ro_dir_next, ro_dir_prev))
    while ro_dir_next and ro_dir_next != ro_dir_prev:
        log.debug("ro_dir_next %s, ro_dir_prev %s"%(ro_dir_next, ro_dir_prev))
        manifestdir = os.path.join(ro_dir_next, ro_settings.MANIFEST_DIR)
        if os.path.isdir(manifestdir):
            return ro_dir_next
        ro_dir_prev = ro_dir_next
        ro_dir_next = os.path.dirname(ro_dir_next)    # Up one directory level
    print ("%s: indicated directory is not contained in a research object: %s"%
           (cmdname, ro_dir))
    return None

def help(progname, args):
    """
    Display ro command help.  See also ro --help
    """
    helptext = [
        "Available commands are:",
        "",
        "  %(progname)s help",
        "  %(progname)s config",
        "  %(progname)s create",
        "",
        "See also:",
        "",
        "  %(progname)s --help"
        "",
        ]
    for h in helptext:
        print h%{'progname': progname}
    return 0

def config(progname, configbase, options, args):
    """
    Update RO repository access configuration
    """
    ro_config = {
        "robase":     getoptionvalue(options.roboxdir,      "ROBOX service base directory:  "),
        "roboxuri":   getoptionvalue(options.roboxuri,      "URI for ROBOX service:         "),
        "roboxpass":  getoptionvalue(options.roboxpassword, "Password for ROBOX service:    "),
        "username":   getoptionvalue(options.username,      "Name of research object owner: "),
        "useremail":  getoptionvalue(options.useremail,     "Email address of owner:        "),
        # Built-in annotation types
        "annotationTypes": [
            { "name": "type", "prefix": "dcterms", "localName": "type", "type": "string", 
              "baseUri": DCTERMS.baseUri, "fullUri": DCTERMS.type,
              "label": "Type",
              "description": "Word or brief phrase describing type of Research Object component" },
            { "name": "keywords", "prefix": "dcterms", "localName": "subject", "type": "termlist", 
              "baseUri": DCTERMS.baseUri, "fullUri": DCTERMS.subject,
              "label": "Keywords",
              "description": "List of key words or phrases associated with a Research Object component" },
            { "name": "description", "prefix": "dcterms", "localName": "description", "type": "text", 
              "baseUri": DCTERMS.baseUri, "fullUri": DCTERMS.description,
              "label": "Description",
              "description": "Extended description of Research Object component" },
            { "name": "format", "prefix": "dcterms", "localName": "format", "type": "string", 
              "baseUri": DCTERMS.baseUri, "fullUri": DCTERMS.format,
              "label": "Data format",
              "description": "String indicating the data format of a Research Object component" },
            { "name": "format", "prefix": "dcterms", "localName": "format", "type": "string", 
              "baseUri": DCTERMS.baseUri, "fullUri": DCTERMS.format,
              "label": "Data format",
              "description": "String indicating the data format of a Research Object component" },
            { "name": "title", "prefix": "dcterms", "localName": "title", "type": "string",
              "baseUri": DCTERMS.baseUri, "fullUri": DCTERMS.title,
              "label": "Title",
              "description": "Title of Research Object component" },
            { "name": "created", "prefix": "dcterms", "localName": "created", "type": "datetime",
              "baseUri": DCTERMS.baseUri, "fullUri": DCTERMS.created,
              "label": "Creation time",
              "description": "Data and time that Research Object component was created" }
            ],
        }
    ro_config["robase"] = os.path.abspath(ro_config["robase"])
    if options.verbose: 
        print "ro config -b %(robase)s"%ro_config
        print "          -r %(roboxuri)s"%ro_config
        print "          -p %(roboxpass)s"%ro_config
        print "          -u %(username)s -e %(useremail)s"%ro_config
    ro_utils.writeconfig(configbase, ro_config)
    if options.verbose:
        print "ro configuration written to %s"%(os.path.abspath(configbase))
    return 0

def create(progname, configbase, options, args):
    """
    Create a new Research Object.

    ro create RO-name [ -d dir ] [ -i RO-ident ]
    """
    ro_options = {
        "roname":  getoptionvalue(args[2],  "Name of new research object: "),
        "rodir":   options.rodir or "",
        "roident": options.roident or ""
        }
    log.debug("cwd: "+os.getcwd())
    log.debug("ro_options: "+repr(ro_options))
    ro_options['roident'] = ro_options['roident'] or ro_utils.ronametoident(ro_options['roname'])
    # Read local ro configuration and extract creator
    ro_config = ro_utils.readconfig(configbase)
    timestamp = datetime.datetime.now().replace(microsecond=0)
    ro_options['rocreator'] = ro_config['username']
    ro_options['rocreated'] = timestamp.isoformat()
    ro_dir = ro_utils.ropath(ro_config, ro_options['rodir'])
    if not ro_dir:
        print ("%s: research object not in configured research object directory tree: %s"%
               (ro_utils.progname(args), ro_options['rodir']))
        return 1
    # Create directory for manifest
    if options.verbose: 
        print "ro create \"%(roname)s\" -d \"%(rodir)s\" -i \"%(roident)s\""%ro_options
    manifestdir = os.path.join(ro_dir, ro_settings.MANIFEST_DIR)
    log.debug("manifestdir: "+manifestdir)
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
    # Create manifest file
    # @@TODO: create in-memory graph and serialize that
    manifestfilename = os.path.join(manifestdir, ro_settings.MANIFEST_FILE)
    log.debug("manifestfilename: "+manifestfilename)
    manifest = (
        """<?xml version="1.0" encoding="utf-8"?>
        <rdf:RDF
          xml:base=".."
          xmlns:dcterms="http://purl.org/dc/terms/"
          xmlns:oxds="http://vocab.ox.ac.uk/dataset/schema#"
          xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        >
          <oxds:Grouping rdf:about="#">
            <dcterms:identifier>%(roident)s</dcterms:identifier>
            <dcterms:title>%(roname)s</dcterms:title>
            <dcterms:description>%(roname)s</dcterms:description>
            <dcterms:creator>%(rocreator)s</dcterms:creator>
            <dcterms:created>%(rocreated)s</dcterms:created>
          </oxds:Grouping>
        </rdf:RDF>
        """%ro_options)
    log.debug("manifest: "+manifest)
    manifestfile = open(manifestfilename, 'w')
    manifestfile.write(manifest)
    manifestfile.close()
    return 0

def status(progname, configbase, options, args):
    """
    Display status of a designated research object

    ro status [ -d dir ]
    """
    # Check command arguments
    ro_config = ro_utils.readconfig(configbase)
    ro_options = {
        "rodir":   options.rodir or "",
        }
    log.debug("ro_options: "+repr(ro_options))
    # Find RO root directory
    ro_dir = ro_root_directory(progname+" status", ro_config, ro_options['rodir'])
    if not ro_dir: return 1
    # Read manifest and display status
    if options.verbose: 
        print "ro status -d \"%(rodir)s\""%ro_options
    ro_dict = ro_manifest.readManifest(ro_dir)
    print "Research Object status"
    print "  identifier:  %(roident)s, title: %(rotitle)s"%ro_dict
    print "  creator:     %(rocreator)s, created: %(rocreated)s"%ro_dict
    print "  path:        %(ropath)s"%ro_dict
    if ro_dict['rouri']:
        print "  uri:         %(rouri)s"%ro_dict
    print "  description: %(rodescription)s"%ro_dict
    return 0

def list(progname, configbase, options, args):
    """
    List contents of a designated research object

    ro list [ -d dir ]
    ro ls [ -d dir ]
    """
    # Check command arguments
    ro_config = ro_utils.readconfig(configbase)
    ro_options = {
        "rodir":   options.rodir or "",
        }
    log.debug("ro_options: "+repr(ro_options))
    # Find RO root directory
    ro_dir = ro_root_directory(progname+" list", ro_config, ro_options['rodir'])
    if not ro_dir: return 1
    # Scan directory tree and display files
    if options.verbose:
        print "ro list -d \"%(rodir)s\""%ro_options
    rofiles = MiscLib.ScanDirectories.CollectDirectoryContents(
                ro_dir, baseDir=ro_config['robase'], 
                listDirs=False, listFiles=True, recursive=True, appendSep=False)
    print "\n".join(rofiles)
    return 0

def annotate(progname, configbase, options, args):
    """
    Annotate a specified research object component
    
    ro annotate file attribute-name [ attribute-value ]
    """
    # Check command arguments
    if len(args) not in [4,5]:
        print ("%s annotate: wrong number of arguments provided"%
               (progname))
        print ("Usage: %s annotate file attribute-name [ attribute-value ]"%
               (progname))
        return 1
    ro_config = ro_utils.readconfig(configbase)
    ro_options = {
        "rofile":       args[2],
        "rodir":        os.path.dirname(args[2]),
        "roattribute":  args[3],
        "rovalue":      args[4] or None
        }
    log.debug("ro_options: "+repr(ro_options))
    # Find RO root directory
    ro_dir = ro_root_directory(progname+" attribute", ro_config, ro_options['rodir'])
    if not ro_dir: return 1
    # Read and update manifest
    if options.verbose:
        print "ro annotate %(rofile)s %(roattribute)s \"%(rovalue)s\""%ro_options
    ro_graph = ro_manifest.readManifestGraph(ro_dir)
    predicate = ro_options['roattribute']
    #@@TODO: deal with annotation types
    for atype in ro_config["annotationTypes"]:
        if atype["name"] == predicate:
            predicate = atype["fullUri"]
            break
    predicate = rdflib.URIRef(predicate)
    log.debug("Adding annotation predicate: %s, value %s"%(repr(predicate),repr(ro_options['rovalue'])))
    ro_graph.add(
        ( ro_manifest.getComponentUri(ro_dir, os.path.abspath(ro_options['rofile'])),
          predicate,
          rdflib.Literal(ro_options['rovalue']) 
        ) )
    ro_manifest.writeManifestGraph(ro_dir, ro_graph)
    return 0

# End.
