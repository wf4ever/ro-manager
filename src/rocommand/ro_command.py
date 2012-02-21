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
import shutil

log = logging.getLogger(__name__)

import MiscLib.ScanDirectories

import ro_settings
import ro_utils
import ro_manifest   # @@TODO: remove this
import ro_annotation # @@TODO: remove this
from ro_annotation import annotationTypes
from ro_metadata   import ro_metadata

from iaeval import ro_eval_completeness

from sync.RosrsSync import RosrsSync
from sync.BackgroundSync import BackgroundResourceSync

from zipfile import ZipFile

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
    #log.debug("ro_root_directory: cmdname %s, rodir %s"%(cmdname, rodir))
    #log.debug("                   ro_config %s"%(repr(ro_config)))
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
    #log.debug("ro_dir_next %s, ro_dir_prev %s"%(ro_dir_next, ro_dir_prev))
    while ro_dir_next and ro_dir_next != ro_dir_prev:
        #log.debug("ro_dir_next %s, ro_dir_prev %s"%(ro_dir_next, ro_dir_prev))
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
    helptext = (
        [ "Available commands are:"
        , ""
        , "  %(progname)s help"
        , "  %(progname)s config -b <robase> -r <roboxuri> -p <roboxpass> -u <username> -e <useremail>"
        , "  %(progname)s create <RO-name> [ -d <dir> ] [ -i <RO-ident> ]"
        , "  %(progname)s add [ -d <dir> ] [ -a ] [ file | directory ]"
        , "  %(progname)s status [ -d <dir> ]"
        , "  %(progname)s list [ -d <dir> ]"
        , "  %(progname)s annotate <file> <attribute-name> [ <attribute-value> ]"
        , "  %(progname)s annotations [ <file> | -d <dir> ]"
        , "  %(progname)s push [ -d <dir> ] [ -f ] [ -r <rosrs_uri> ] [ -u <username> ] [ -p <password> ]"
        , "  %(progname)s checkout [ <RO-identifier> [ -d <dir>] ] [ -r <rosrs_uri> ] [ -u <username> ] [ -p <password> ]"
        , "  %(progname)s evaluate completeness [ -d <dir> ] [ -a ] [ <minim> ] [ <purpose> ] [ <target> ]"
        , ""
        , "Supported annotation type names are: "
        , "\n".join([ "  %(name)s - %(description)s"%atype for atype in annotationTypes ])
        , ""
        , "See also:"
        , ""
        , "  %(progname)s --help"
        ""
        ])
    for h in helptext:
        print h%{'progname': progname}
    return 0

def config(progname, configbase, options, args):
    """
    Update RO repository access configuration
    """
    ro_config = {
        "robase":         getoptionvalue(options.roboxdir,       "ROBOX service base directory:  "),
        "rosrs_uri":      getoptionvalue(options.rosrs_uri,      "URI for ROSRS service:         "),
        "rosrs_username": getoptionvalue(options.rosrs_username, "Username for ROSRS service:    "),
        "rosrs_password": getoptionvalue(options.rosrs_password, "Password for ROSRS service:    "),
        "username":       getoptionvalue(options.username,       "Name of research object owner: "),
        "useremail":      getoptionvalue(options.useremail,      "Email address of owner:        "),
        # Built-in annotation types
        "annotationTypes": annotationTypes
        }
    ro_config["robase"] = os.path.abspath(ro_config["robase"])
    if options.verbose: 
        print "ro config -b %(robase)s"%ro_config
        print "          -r %(rosrs_uri)s"%ro_config
        print "          -u %(rosrs_username)s"%ro_config
        print "          -p %(rosrs_password)s"%ro_config
        print "          -n %(username)s -e %(useremail)s"%ro_config
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
          xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
          xmlns:ro="http://purl.org/wf4ever/ro#"
          xmlns:ore="http://www.openarchives.org/ore/terms/"
          xmlns:ao="http://purl.org/ao/"
          xmlns:dcterms="http://purl.org/dc/terms/"
          xmlns:foaf="http://xmlns.com/foaf/0.1/"
        >
          <ro:ResearchObject rdf:about="">
            <dcterms:identifier>%(roident)s</dcterms:identifier>
            <dcterms:title>%(roname)s</dcterms:title>
            <dcterms:description>%(roname)s</dcterms:description>
            <dcterms:creator>%(rocreator)s</dcterms:creator>
            <dcterms:created>%(rocreated)s</dcterms:created>
            <!-- self-reference to include above details as annotation -->
            <ore:aggregates>
              <ro:AggregatedAnnotation>
                <ro:annotatesAggregatedResource rdf:resource="" />
                <ao:body rdf:resource=".ro/manifest.rdf" />
              </ro:AggregatedAnnotation>
            </ore:aggregates>
          </ro:ResearchObject>
        </rdf:RDF>
        """%ro_options)
    log.debug("manifest: "+manifest)
    manifestfile = open(manifestfilename, 'w')
    manifestfile.write(manifest)
    manifestfile.close()
    return 0

def add(progname, configbase, options, args):
    """
    Add files to a research object manifest
    
    ro add [ -d dir ] file
    ro add [ -d dir ] [-a] [directory]

    Use -a/--all to add subdirectories recursively

    If no file or directory specified, defaults to current directory.
    """
    # Check command arguments
    if len(args) not in [2, 3]:
        print ("%s add: wrong number of arguments provided"%
               (progname))
        print ("Usage: %s add [ -a ] [ file | directory ]"%
               (progname))
        return 1
    ro_config = ro_utils.readconfig(configbase)
    ro_options = {
        "rodir":        options.rodir or "",
        "rofile":       args[2] if len(args) == 3 else ".",
        "recurse":      options.all,
        "recurseopt":   "-a" if options.all else ""
        }
    log.debug("ro_options: "+repr(ro_options))
    # Find RO root directory
    ro_dir = ro_root_directory(progname+" add", ro_config, ro_options['rodir'])
    if not ro_dir: return 1
    # Read and update manifest
    if options.verbose:
        print "ro add -d %(rodir)s %(recurseopt)s %(rofile)s"%ro_options
    ro_manifest.addAggregatedResources(ro_dir, ro_options['rofile'], ro_options['recurse'])
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

    ro list [ -a ] [ -d dir ]
    ro ls [ -a ] [ -d dir ]
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
                ro_dir, baseDir=os.path.abspath(ro_dir), 
                listDirs=False, listFiles=True, recursive=True, appendSep=False)
    if not options.all:
        def notHidden(f):
            return re.match("\.|.*/\.", f) == None
        rofiles = filter(notHidden, rofiles)
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
    # Read and update manifest and annotations
    if options.verbose:
        print "ro annotate %(rofile)s %(roattribute)s \"%(rovalue)s\""%ro_options
    rometa = ro_metadata(ro_config, ro_dir)
    rofile = rometa.getFileUri(ro_options['rofile'])     # Relative to CWD
    rometa.addSimpleAnnotation(rofile, ro_options['roattribute'],  ro_options['rovalue'])
    return 0

def annotations(progname, configbase, options, args):
    """
    Display annotations
    
    ro annotations [ file | -d dir ]
    """
    log.debug("annotations: progname %s, configbase %s, args %s"%
              (progname, configbase, repr(args)))
    # Check command arguments
    if len(args) not in [2,3]:
        print ("%s annotations: wrong number of arguments provided"%
               (progname))
        print ("Usage: %s annotations [ file | -d dir ]"%
               (progname))
        return 1
    ro_config  = ro_utils.readconfig(configbase)
    ro_file    = (args[2] if len(args) >= 3 else "")
    ro_options = {
        "rofile":       ro_file,
        "rodir":        options.rodir or os.path.dirname(ro_file)
        }
    log.debug("ro_options: "+repr(ro_options))
    if options.verbose:
        print "ro annotations -d \"%(rodir)s\" %(rofile)s "%ro_options
    ro_dir = ro_root_directory(progname+" annotations", ro_config, ro_options['rodir'])
    if not ro_dir: return 1
    # Enumerate and display annotations
    if ro_options['rofile']:
        ro_file = ro_manifest.getFileUri(ro_options['rofile'])   # Relative to CWD
        log.debug("Annotations for %s"%str(ro_file))
        annotations = ro_annotation.getFileAnnotations(ro_dir, ro_file)
    else:
        annotations = ro_annotation.getAllAnnotations(ro_dir)
    ro_annotation.showAnnotations(ro_config, ro_dir, annotations, sys.stdout)

    sname_prev = None
    for (asubj,apred,aval) in annotations:
        #log.debug("Annotations: asubj %s, apred %s, aval %s"%
        #          (repr(asubj), repr(apred), repr(aval)))
        aname = ro_annotation.getAnnotationNameByUri(ro_config, apred)
        sname = ro_manifest.getComponentUriRel(ro_dir, str(asubj))
        log.debug("Annotations: sname %s, aname %s"%(sname, aname))
        if sname == "":
            sname = ro_manifest.getRoUri(ro_dir)
        if sname != sname_prev:
            print sname
            sname_prev = sname
        print "  %s %s"%(aname,str(aval))
    return 0

def push(progname, configbase, options, args):
    """
    Push all or selected ROs and their resources to ROSRS
    
    ro push [ -d <dir> ] [ -f ] [ -r <rosrs_uri> ] [ -u <username> ] [ -p <password> ]
    """
    # Check command arguments
    if len(args) not in [2, 3, 4, 5, 6, 7]:
        print ("%s push: wrong number of arguments provided"%
               (progname))
        print ("Usage: %s push [ -d <dir> ] [ -f ] [ -r <rosrs_uri> ] [ -u <username> ] [ -p <password> ]"%
               (progname))
        return 1
    ro_config = ro_utils.readconfig(configbase)
    ro_options = {
        "rodir":          options.rodir or None,
        "rosrs_uri":      options.rosrs_uri or getoptionvalue(ro_config['rosrs_uri'],           "URI for ROSRS service:         "),
        "rosrs_username": options.rosrs_username or getoptionvalue(ro_config['rosrs_username'], "Username for ROSRS service:    "),
        "rosrs_password": options.rosrs_password or getoptionvalue(ro_config['rosrs_password'], "Password for ROSRS service:    "),
        "force":          options.force
        }
    log.debug("ro_options: "+repr(ro_options))
    if options.verbose:
        print "ro push %(rodir)s %(rosrs_uri)s %(rosrs_username)s %(rosrs_password)s"%ro_options
    sync = RosrsSync(ro_options['rosrs_uri'], ro_options['rosrs_username'], ro_options['rosrs_password'])
    back = BackgroundResourceSync(sync, ro_options['force'])
    if not ro_options['rodir']:
        (sent, deleted) = back.pushAllResourcesInWorkspace(ro_config['robase'], True)
    else:
        roDir = ro_utils.ropath(ro_config, ro_options['rodir'])
        (sent, deleted) = back.pushAllResources(roDir, True)
    if not options.verbose:
        print "%d files updated, %d files deleted" % (len(sent), len(deleted))
    else:
        for s in sent:
            print "Updated: %s" % s
        for d in deleted:
            print "Deleted: %s" % d
    return 0

def checkout(progname, configbase, options, args):
    """
    Checkout a RO from ROSRS
    
    ro checkout [ <RO-identifier> [ -d <dir>] ] [ -r <rosrs_uri> ] [ -u <username> ] [ -p <password> ]
    """
    # Check command arguments
    if len(args) not in [2, 3, 4, 5, 6, 7]:
        print ("%s push: wrong number of arguments provided"%
               (progname))
        print ("Usage: %s checkout [ <RO-identifier> [ -d <dir>] ] [ -r <rosrs_uri> ] [ -u <username> ] [ -p <password> ]"%
               (progname))
        return 1
    ro_config = ro_utils.readconfig(configbase)
    ro_options = {
        "roident":        args[2] if len(args) > 2 else None,
        "rodir":          options.rodir or (args[2] if len(args) > 2 else None),
        "rosrs_uri":      options.rosrs_uri or getoptionvalue(ro_config['rosrs_uri'],           "URI for ROSRS service:         "),
        "rosrs_username": options.rosrs_username or getoptionvalue(ro_config['rosrs_username'], "Username for ROSRS service:    "),
        "rosrs_password": options.rosrs_password or getoptionvalue(ro_config['rosrs_password'], "Password for ROSRS service:    "),
        "force":          options.force
        }
    log.debug("ro_options: "+repr(ro_options))
    if options.verbose:
        print "ro checkout %(roident)s %(rodir)s %(rosrs_uri)s %(rosrs_username)s %(rosrs_password)s"%ro_options
    sync = RosrsSync(ro_options['rosrs_uri'], ro_options['rosrs_username'], ro_options['rosrs_password'])
    if (ro_options["roident"]):
        ros = set([ro_options['roident']])
        rodirs = ro_options['rodir']
    else:
        ros = sync.getRos()
        rodirs = None
    
    for ro in ros:
        print "Checking out %s" % ro
        rodir = os.path.join(ro_config["robase"], rodirs if rodirs else ro)
        verzip = sync.getVersionAsZip(ro, ro_settings.RO_VERSION)
        zipfile = ZipFile(verzip)
        
        if options.verbose:
            # HACK for moving the manifest
            #        zipfile.printdir()
            for l in zipfile.namelist():
                if l == ro_settings.MANIFEST_FILE:
                    print ro_settings.MANIFEST_DIR + "/" + l
                else:
                    print l
                    
        if not os.path.exists(rodir) or not os.path.isdir(rodir):
            os.mkdir(rodir)
        zipfile.extractall(rodir)
            
        # HACK for moving the manifest
        if not os.path.exists(rodir + "/" + ro_settings.MANIFEST_DIR):
            os.mkdir(rodir + "/" + ro_settings.MANIFEST_DIR)
        shutil.move(rodir + "/" + ro_settings.MANIFEST_FILE, rodir + "/" + ro_settings.MANIFEST_DIR + "/" + ro_settings.MANIFEST_FILE)
        
        print "%d files checked out" % len(zipfile.namelist())
    return 0

def evaluate(progname, configbase, options, args):
    """
    Evaluate RO
    
    ro evaluate completeness [ -d <dir> ] [ <purpose> ] [ <target> ]"
    """
    log.debug("evaluate: progname %s, configbase %s, args %s"%
              (progname, configbase, repr(args)))
    # Check command arguments
    if len(args) < 3:
        print ("%s evaluate: wrong number of arguments provided"%(progname))
        print ("Usage: %s evaluate <function> [ -d <dir> ] ..."%(progname))
        return 1
    ro_config  = ro_utils.readconfig(configbase)
    ro_options = (
        { "rodir":        options.rodir or ""
        , "function":     args[2]
        })
    log.debug("ro_options: "+repr(ro_options))
    ro_dir = ro_root_directory(progname+" annotations", ro_config, ro_options['rodir'])
    if not ro_dir: return 1
    # Evaluate...
    if ro_options["function"] == "completeness":
        if len(args) not in [3,4,5,6]:
            print ("%s evaluate completeness: wrong number of arguments provided"%(progname))
            print ("Usage: %s evaluate completeness [ -d <dir> ] [ -a ] [ <minim> ] [ <purpose> ] [ <target> ]"%(progname))
            return 1
        ro_options["minim"]   = ((len(args) > 3) and args[3]) or "minim.rdf"
        ro_options["purpose"] = ((len(args) > 4) and args[4]) or "create"
        ro_options["target"]  = ((len(args) > 5) and args[5]) or "."
        if options.verbose:
            print "ro evaluate %(function)s -d \"%(rodir)s\" %(minim)s %(purpose)s %(target)s"%ro_options
        evalresult = ro_eval_completeness.evaluate(ro_dir, 
            ro_options["minim"], ro_options["target"], ro_options["purpose"])
        ro_eval_completeness.format(evalresult, 
            { "detail" : "full" if options.all else "summary" }, 
            sys.stdout)
    # elif ... other functions here
    else:
        print ("%s evaluate: unrecognized function provided"%(progname))
        print ("Usage:")
        print ("  %s evaluate completeness [ -d <dir> ] [ -a ] [ <minim> ] [ <purpose> ] [ <target> ]"%(progname))
        return 1
    return 0

# End.
