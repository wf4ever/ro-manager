'''
Created on 13-09-2011

@author: piotrhol
'''

from robox.ro_command import getoptionvalue
from httplib import HTTPConnection, CREATED, NO_CONTENT, responses
import base64

class RosrsSync:

    URI_WORKSPACES = "/rosrs3/workspaces"
    URI_WORKSPACE_ID = URI_WORKSPACES + "/%s"
    URI_ROS = URI_WORKSPACE_ID + "/ROs"
    URI_RO_ID = URI_ROS + "/%s"
    URI_VERSION_ID = URI_RO_ID + "/%s"
    URI_RESOURCE = URI_VERSION_ID + "/%s"
    
    ADMIN_USERNAME = "wfadmin"
    ADMIN_PASSWORD = "wfadmin!!!"
    
    def post_workspace(self, rosrs_host, username, password):
        """
        Create a new workspace in ROSRS. This complies to ROSRS 3, which means that 
        the workspace id will be the same as username.
        
        Parameters: ROSRS URL, username, password
        """
        ro_options = {
            "rosrs_host":  getoptionvalue(rosrs_host, "ROSRS host: "),
            "username":  getoptionvalue(username, "Username: "),
            "rosrs_password":  getoptionvalue(password, "ROSRS password: "),
            }
        conn = HTTPConnection(ro_options["rosrs_host"])
        url = self.URI_WORKSPACES
        body = (
    """%(username)s
    %(rosrs_password)s""" % ro_options)
        headers = {"Authorization": "Basic %s" % base64.encodestring('%s:%s' % (self.ADMIN_USERNAME, self.ADMIN_PASSWORD))[:-1],
                   "Content-Type": "text/plain"}
        conn.request("POST", url, body, headers)
        res = conn.getresponse()
        if res.status != CREATED:
            raise Exception("%d %s: %s" % (res.status, responses[res.status], res.reason))
        print "Workspace %s created" % username
        return None 
    
    def delete_workspace(self, rosrs_url, username):
        """
        Delete a workspace in ROSRS. This complies to ROSRS 3, which means that 
        the workspace id is the same as username.
        
        Parameters: ROSRS URL, username
        """
        ro_options = {
            "rosrs_host":  getoptionvalue(rosrs_url, "ROSRS host: "),
            "username":  getoptionvalue(username, "Username: "),
            }
        conn = HTTPConnection(ro_options["rosrs_host"])
        url = self.URI_WORKSPACE_ID % ro_options["username"]
        headers = {"Authorization": "Basic %s" % base64.encodestring('%s:%s' % (self.ADMIN_USERNAME, self.ADMIN_PASSWORD))[:-1]}
        conn.request("DELETE", url, None, headers)
        res = conn.getresponse()
        if res.status != NO_CONTENT:
            raise Exception("%d %s: %s" % (res.status, responses[res.status], res.reason))
        print "Workspace %s deleted" % username
        return None 
    
    def post_ro(self):
        return None 
    
    def post_version(self):
        return None 
    
    def put_manifest(self):
        return None 
    
    def put_file(self):
        return None 
    
    if __name__ == '__main__':
        pass
