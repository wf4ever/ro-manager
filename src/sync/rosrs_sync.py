'''
Created on 13-09-2011

@author: piotrhol
'''

from robox import ro_command
from httplib import HTTPConnection, CREATED, NO_CONTENT, responses
import base64

URI_WORKSPACES = "/rosrs3/workspaces"
URI_WORKSPACE_ID = URI_WORKSPACES + "/%s"
URI_ROS = URI_WORKSPACE_ID + "/ROs"
URI_RO_ID = URI_ROS + "/%s"
URI_VERSION_ID = URI_RO_ID + "/%s"
URI_RESOURCE = URI_VERSION_ID + "/%s"

ADMIN_USERNAME = "wfadmin"
ADMIN_PASSWORD = "wfadmin!!!"

def post_workspace(progname, configbase, options, args):
    """
    Create a new workspace in ROSRS. This complies to ROSRS 3, which means that 
    the workspace id will be the same as username.
    
    Parameters: ROSRS URL, username, password
    """
    ro_options = {
        "rosrs_url":  ro_command.getoptionvalue(options.rosrs_url, "ROSRS URL: "),
        "username":  ro_command.getoptionvalue(options.username, "Username: "),
        "rosrs_password":  ro_command.getoptionvalue(options.rosrs_password, "ROSRS password: "),
        }
    conn = HTTPConnection(ro_options["rosrs_url"])
    url = URI_WORKSPACES
    body = (
"""%(username)
%(rosrs_password)""" % ro_options)
    headers = {"Authorization": "Basic %s" % base64.encodestring('%s:%s' % (ADMIN_USERNAME, ADMIN_PASSWORD))[:-1],
               "Content-Type": "text/plain"}
    conn.request("POST", url, body, headers)
    res = conn.getresponse()
    if res.status != CREATED:
        raise Exception("%d %s: %s" % (res.status, responses[res.status], res.reason))
    return None 

def delete_workspace(progname, configbase, options, args):
    """
    Delete a workspace in ROSRS. This complies to ROSRS 3, which means that 
    the workspace id is the same as username.
    
    Parameters: ROSRS URL, username
    """
    ro_options = {
        "rosrs_url":  ro_command.getoptionvalue(options.rosrs_url, "ROSRS URL: "),
        "username":  ro_command.getoptionvalue(options.username, "Username: "),
        }
    conn = HTTPConnection(ro_options["rosrs_url"])
    url = URI_WORKSPACE_ID % ro_options["username"]
    headers = {"Authorization": "Basic %s" % base64.encodestring('%s:%s' % (ADMIN_USERNAME, ADMIN_PASSWORD))[:-1]}
    conn.request("DELETE", url, None, headers)
    res = conn.getresponse()
    if res.status != NO_CONTENT:
        raise Exception("%d %s: %s" % (res.status, responses[res.status], res.reason))
    return None 

def post_ro(progname, configbase, options, args):
    return None 

def post_version(progname, configbase, options, args):
    return None 

def put_manifest(progname, configbase, options, args):
    return None 

def put_file(progname, configbase, options, args):
    return None 

if __name__ == '__main__':
    pass
