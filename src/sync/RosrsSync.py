'''
Created on 13-09-2011

@author: piotrhol
'''

from httplib import HTTPConnection, CREATED, NO_CONTENT, OK, responses
import base64
import logging
import urllib2
import urlparse
import tempfile

log = logging.getLogger(__name__)

class RosrsSync:


    URI_WORKSPACES = "/workspaces"
    URI_WORKSPACE_ID = URI_WORKSPACES + "/%s"
    URI_ROS = URI_WORKSPACE_ID + "/ROs"
    URI_RO_ID = URI_ROS + "/%s"
    URI_VERSION_ID = URI_RO_ID + "/%s"
    URI_RESOURCE = URI_VERSION_ID + "/%s"
    
    ADMIN_USERNAME = "wfadmin"
    ADMIN_PASSWORD = "wfadmin!!!"
    
    def __init__(self, rosrs_uri, username, password):
        parsed = urlparse.urlparse(rosrs_uri)
        self.rosrs_path = parsed.path
        self.rosrs_host = parsed.netloc
        self.rosrs_uri = rosrs_uri
        self.username = username
        self.password = password
    
    def postWorkspace(self):
        """
        Create a new workspace in ROSRS. This complies to ROSRS 3, which means that 
        the workspace id will be the same as username.
        
        Parameters: ROSRS URL, username, password
        """
        conn = HTTPConnection(self.rosrs_host)
        url = self.rosrs_path + self.URI_WORKSPACES
        body = (
"""%s
%s""" % (self.username, self.password))
        headers = {"Authorization": "Basic %s" % base64.encodestring('%s:%s' % (self.ADMIN_USERNAME, self.ADMIN_PASSWORD))[:-1],
                   "Content-Type": "text/plain"}
        conn.request("POST", url, body, headers)
        res = conn.getresponse()
        if res.status != CREATED:
            raise Exception("%d %s: %s" % (res.status, res.reason, res.read()))
        log.debug("Workspace %s created: %s" % (self.username, res.msg["location"]))
        return res.msg["location"]
    
    def deleteWorkspace(self):
        """
        Delete a workspace in ROSRS. This complies to ROSRS 3, which means that 
        the workspace id is the same as username.
        
        Parameters: ROSRS URL, username
        """
        conn = HTTPConnection(self.rosrs_host)
        url = self.rosrs_path + urllib2.quote(self.URI_WORKSPACE_ID % self.username)
        headers = {"Authorization": "Basic %s" % base64.encodestring('%s:%s' % (self.ADMIN_USERNAME, self.ADMIN_PASSWORD))[:-1]}
        conn.request("DELETE", url, None, headers)
        res = conn.getresponse()
        if res.status != NO_CONTENT:
            raise Exception("%d %s: %s" % (res.status, res.reason, res.read()))
        log.debug("Workspace %s deleted" % self.username)
        return None
    
    def postRo(self, roId):
        """
        Create a new Research Object in ROSRS.
        
        Parameters: ROSRS URL, username, password, RO id
        """
        conn = HTTPConnection(self.rosrs_host)
        url = self.rosrs_path + urllib2.quote(self.URI_ROS % self.username)
        body = roId
        headers = {"Authorization": "Basic %s" % base64.encodestring('%s:%s' % (self.username, self.password))[:-1],
                   "Content-Type": "text/plain"}
        conn.request("POST", url, body, headers)
        res = conn.getresponse()
        if res.status != CREATED:
            raise Exception("%d %s: %s" % (res.status, res.reason, res.read()))
        log.debug("RO %s created: %s" % (roId, res.msg["location"]))
        return res.msg["location"]
    
    def deleteRo(self, roId):
        """
        Deletes a Research Object from ROSRS.
        
        Parameters: ROSRS URL, username, password, RO id
        """
        conn = HTTPConnection(self.rosrs_host)
        url = self.rosrs_path + urllib2.quote(self.URI_RO_ID % (self.username, roId))
        headers = {"Authorization": "Basic %s" % base64.encodestring('%s:%s' % (self.username, self.password))[:-1]}
        conn.request("DELETE", url, None, headers)
        res = conn.getresponse()
        if res.status != NO_CONTENT:
            raise Exception("%d %s: %s" % (res.status, res.reason, res.read()))
        log.debug("RO %s deleted" % roId)
        return None 
    
    def postVersion(self, roId, versionId):
        """
        Create a new Research Object version in ROSRS.
        
        Parameters: ROSRS URL, username, password, RO id, version id
        """
        conn = HTTPConnection(self.rosrs_host)
        url = self.rosrs_path + urllib2.quote(self.URI_RO_ID % (self.username, roId))
        body = versionId
        headers = {"Authorization": "Basic %s" % base64.encodestring('%s:%s' % (self.username, self.password))[:-1],
                   "Content-Type": "text/plain"}
        conn.request("POST", url, body, headers)
        res = conn.getresponse()
        if res.status != CREATED:
            raise Exception("%d %s: %s" % (res.status, res.reason, res.read()))
        log.debug("Version %s created: %s" % (versionId, res.msg["location"]))
        return res.msg["location"]
    
    def postVersionAsCopy(self, roId, versionId, oldVersionUri):
        """
        Create a new Research Object version in ROSRS as a copy of another version of the same RO.
        
        Parameters: ROSRS URL, username, password, RO id, version id, old version URL
        """
        conn = HTTPConnection(self.rosrs_host)
        url = self.rosrs_path + urllib2.quote(self.URI_RO_ID % (self.username, roId))
        body = """%s
%s""" % (versionId, oldVersionUri)
        versionId
        headers = {"Authorization": "Basic %s" % base64.encodestring('%s:%s' % (self.username, self.password))[:-1],
                   "Content-Type": "text/plain"}
        conn.request("POST", url, body, headers)
        res = conn.getresponse()
        if res.status != CREATED:
            raise Exception("%d %s: %s" % (res.status, res.reason, res.read()))
        log.debug("Version %s created as a copy of %s: %s" % (versionId, oldVersionUri, res.msg["location"]))
        return res.msg["location"]
    
    def deleteVersion(self, roId, versionId):
        """
        Deletes a Research Object version from ROSRS.
        
        Parameters: ROSRS URL, username, password, RO id, version id
        """
        conn = HTTPConnection(self.rosrs_host)
        url = self.rosrs_path + urllib2.quote(self.URI_VERSION_ID % (self.username, roId, versionId))
        headers = {"Authorization": "Basic %s" % base64.encodestring('%s:%s' % (self.username, self.password))[:-1]}
        conn.request("DELETE", url, None, headers)
        res = conn.getresponse()
        if res.status != NO_CONTENT:
            raise Exception("%d %s: %s" % (res.status, res.reason, res.read()))
        log.debug("Version %s deleted" % versionId)
        return None 

    def getVersionAsZip(self, roId, versionId):
        """
        Retrieves a Research Object version from ROSRS as a zip.
        
        Parameters: ROSRS URL, username, password, RO id, version id
        """
        url = self.rosrs_uri + urllib2.quote(self.URI_VERSION_ID % (self.username, roId, versionId)) + "?content=true"
        req = urllib2.Request(url)
        req.add_header("Authorization", "Basic %s" % base64.encodestring('%s:%s' % (self.username, self.password))[:-1])
        res = urllib2.urlopen(req)
        
        tmp = tempfile.TemporaryFile()
        while True:
            packet = res.read()
            if not packet:
                break
            tmp.write(packet)
        res.close()

        log.debug("Version %s retrieved as zip" % versionId)
        return tmp

    def putManifest(self, roId, versionId, manifestFile):
        """
        Updates the manifest of a RO version.
        
        Parameters: ROSRS URL, username, password, RO id, version id, file with the manifest as XML/RDF
        """
        conn = HTTPConnection(self.rosrs_host)
        url = self.rosrs_path + urllib2.quote(self.URI_VERSION_ID % (self.username, roId, versionId))
        body = manifestFile
        headers = {"Authorization": "Basic %s" % base64.encodestring('%s:%s' % (self.username, self.password))[:-1],
                   "Content-Type": "application/rdf+xml"}
#        conn.request("PUT", url, body, headers)
#        res = conn.getresponse()
#        if res.status != OK:
#            raise Exception("%d %s: %s" % (res.status, res.reason, res.read()))
#        log.debug("Manifest updated: %s" % res.msg["location"])
#        return res.msg["location"]
        return None
        
    def putFile(self, roId, versionId, filePath, contentType, fileObject):
        """
        Creates or updates a file in ROSRS
        
        Parameters: ROSRS URL, username, password, RO id, version id, file path (without trailing slash!),
        content type, file object
        """
        conn = HTTPConnection(self.rosrs_host)
        url = self.rosrs_path + urllib2.quote(self.URI_RESOURCE % (self.username, roId, versionId, filePath))
        body = fileObject
        headers = {"Authorization": "Basic %s" % base64.encodestring('%s:%s' % (self.username, self.password))[:-1],
                   "Content-Type": contentType or "text/plain"}
        conn.request("PUT", url, body, headers)
        res = conn.getresponse()
        if res.status != OK:
            raise Exception("%d %s: %s" % (res.status, res.reason, res.read()))
        log.debug("File created/updated: %s" % filePath)
        return None
    
    def deleteFile(self, roId, versionId, filePath):
        """
        Deletes a file from ROSRS.
        
        Parameters: ROSRS URL, username, password, RO id, version id, file path
        """
        conn = HTTPConnection(self.rosrs_host)
        url = self.rosrs_path + urllib2.quote(self.URI_RESOURCE % (self.username, roId, versionId, filePath))
        headers = {"Authorization": "Basic %s" % base64.encodestring('%s:%s' % (self.username, self.password))[:-1]}
        conn.request("DELETE", url, None, headers)
        res = conn.getresponse()
        if res.status != NO_CONTENT:
            raise Exception("%d %s: %s" % (res.status, responses[res.status], res.reason))
        log.debug("File %s deleted" % filePath)
        return None
    

if __name__ == '__main__':
        pass
