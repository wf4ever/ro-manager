# ro_utils.py

"""
Research Object management supporting utility functions
"""

import os.path
try:
    # Running Python 2.5 with simplejson?
    import simplejson as json
except ImportError:
    import json
import re
import logging

log = logging.getLogger(__name__)

CONFIGFILE = ".ro_config"

def ronametoident(name):
    """
    Turn resource object name into an identifier containing only letters, digits and underscore characters
    """
    name = re.sub(r"\s", '_', name)         # spaces, etc. -> underscores
    name = re.sub(r"\W", "", name)          # Non-identifier characters -> remove
    return name

def progname(args):
    return os.path.basename(args[0])

def ropath(ro_config, dir):
    rodir  = os.path.abspath(dir)
    robase = os.path.realpath(ro_config['robase'])
    log.debug("ropath: rodir  %s"%(rodir))
    log.debug("ropath: robase %s"%(robase))
    if os.path.isdir(rodir) and os.path.commonprefix([robase, os.path.realpath(rodir)]) == robase:
       return rodir
    return None

def configfilename(configbase):
    return os.path.abspath(configbase+"/"+CONFIGFILE)

def writeconfig(configbase, config):
    """
    Write supplied configuration dictionary to indicated directory
    """
    configfile = open(configfilename(configbase), 'w')
    json.dump(config, configfile, indent=4)
    configfile.write("\n")
    configfile.close()
    return

def resetconfig(configbase):
    """
    Reset configuration in indicated directory
    """
    ro_config = {
        "robase":               None,
        "rosrs_uri":            None,
        "rosrs_access_token":   None,
        "username":             None,
        "useremail":            None,
        "annotationTypes":      None,
        "annotationPrefixes":   None,
        }
    writeconfig(configbase, ro_config)
    return

def readconfig(configbase):
    """
    Read configuration in indicated directory and return as a dictionary
    """
    ro_config = {
        "robase":               None,
        "rosrs_uri":            None,
        "rosrs_access_token":   None,
        "username":             None,
        "useremail":            None,
        "annotationTypes":      None,
        "annotationPrefixes":   None,
        }
    configfile = None
    try:
        configfile = open(configfilename(configbase), 'r')
        ro_config  = json.load(configfile)
    finally:
        if configfile: configfile.close()
    return ro_config

# End.
