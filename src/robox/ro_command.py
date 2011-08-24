# ro_command.py

"""
Basic command functions for ro, research object manager
"""

import sys
import os.path
import readline # enable input editing for raw_input

import ro_utils

def getoptionvalue(val, prompt):
    if not val:
        if sys.stdin.isatty():
            val = raw_input(prompt)
        else:
            val = sys.stdin.readline()
            if val[-1] == '\n': val = val[:-1]    
    return val

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
        }
    ro_config["robase"] = os.path.abspath(ro_config["robase"])
    if options.verbose: 
        print "ro config -b %(robase)s"%ro_config
        print "          -r %(roboxuri)s"%ro_config
        print "          -p %(roboxpass)s"%ro_config
        print "          -u %(username)s -e %(useremail)s"%ro_config
    ro_utils.writeconfig(configbase, ro_config)
    if options.verbose:
        print "Confif written to %s"%(configbase)
    return 0

def create(progname, configbase, options, args):
    """
    Create a new Research Object.

    ro create RO-name [ -d dir ] [ -i RO-ident ]
    """
    #    create(progname, configbase, options, args):
    return 0
