# ro_command.py

"""
Basic command functions for ro, research object manager
"""

def help(progname, args):
    """
    Display ro command help.  See also ro --help
    """
    helptext = [
        "Available commands are:",
        "",
        "  %(progname)s help",
        "",
        "See also:",
        "",
        "  %(progname)s --help"
        "",
        ]
    for h in helptext:
        print h%{'progname': progname}
    return 0
