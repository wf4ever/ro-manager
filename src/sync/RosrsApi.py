'''
Created on 13-09-2011

@author: piotrhol
'''

from httplib import HTTPConnection, CREATED, NO_CONTENT, OK, responses
import logging
import urllib2
import urlparse
import tempfile

log = logging.getLogger(__name__)

class RosrsApi:


    URI_ROS = "/ROs/"
    URI_RO_ID = URI_ROS + "%s/"
    URI_RESOURCE = URI_RO_ID + "%s"
    
    def __init__(self, rosrs_uri, accesstoken = None):
        parsed = urlparse.urlparse(rosrs_uri)
        self.rosrs_path = parsed.path
        self.rosrs_host = parsed.netloc
        self.rosrs_uri = rosrs_uri
        self.accesstoken = accesstoken
    
    
    def getRos(self):
        """
        Get a list of RO URIs. If called with an access token, returns 
        only ROs that belong to the user.
        
        Parameters: ROSRS URL, [access token]
        """
        conn = HTTPConnection(self.rosrs_host)
        url = self.rosrs_path + urllib2.quote(self.URI_ROS)
        body = None
        headers = self.__getAuthHeader()
        conn.request("GET", url, body, headers)
        res = conn.getresponse()
        if res.status != OK:
            raise Exception("%d %s: %s" % (res.status, res.reason, res.read()))
        roUris = res.read().splitlines()
        log.debug("RO list retrieved: %d items" % len(roUris))
        return roUris
    
    def postRo(self, roId):
        """
        Create a new Research Object in ROSRS.
        
        Parameters: ROSRS URL, username, password, RO id
        """
        conn = HTTPConnection(self.rosrs_host)
        url = self.rosrs_path + urllib2.quote(self.URI_ROS)
        body = roId
        headers = self.__getAuthHeader()
        headers["Content-Type"] = "text/plain"
        conn.request("POST", url, body, headers)
        res = conn.getresponse()
        if res.status != CREATED:
            raise Exception("%d %s: %s" % (res.status, res.reason, res.read()))
        log.debug("RO %s created: %s" % (roId, res.msg["location"]))
        return res.msg["location"]
    
    def deleteRo(self, roId):
        """
        Deletes a Research Object from ROSRS.
        
        Parameters: ROSRS URL, access token, RO id
        """
        roUrl = self.rosrs_path + urllib2.quote(self.URI_RO_ID % roId)
        return self.deleteRoByUrl(roUrl) 
    
    def deleteRoByUrl(self, roUrl):
        """
        Deletes a Research Object from ROSRS.
        
        Parameters: ROSRS URL, access token, RO URL
        """
        conn = HTTPConnection(self.rosrs_host)
        headers = self.__getAuthHeader()
        conn.request("DELETE", roUrl, None, headers)
        res = conn.getresponse()
        if res.status != NO_CONTENT:
            raise Exception("%d %s: %s" % (res.status, res.reason, res.read()))
        log.debug("RO %s deleted" % roUrl)
        return None 

    def getRoAsZip(self, roId):
        """
        Retrieves a Research Object version from ROSRS as a zip.
        
        Parameters: ROSRS URL, username, password, RO id, version id
        """
        url = self.rosrs_uri + urllib2.quote(self.URI_RO_ID % roId)
        return self.getRoAsZipByUrl(url)

    def getRoAsZipByUrl(self, roUrl):
        """
        Retrieves a Research Object version from ROSRS as a zip.
        
        Parameters: ROSRS URL, username, password, RO id, version id
        """
        req = urllib2.Request(roUrl)
        req.add_header("Accept", "application/zip")
        res = urllib2.urlopen(req)
        
        tmp = tempfile.TemporaryFile()
        while True:
            packet = res.read()
            if not packet:
                break
            tmp.write(packet)
        res.close()

        log.debug("Ro %s retrieved as zip" % roUrl)
        return tmp

    def putFile(self, roId, filePath, contentType, fileObject):
        """
        Creates or updates a file in ROSRS. This includes all metadata.
        
        Parameters: ROSRS URL, access token, RO id, file path (without trailing slash!),
        content type, file object
        """
        conn = HTTPConnection(self.rosrs_host)
        url = self.rosrs_path + urllib2.quote(self.URI_RESOURCE % (roId, filePath))
        body = fileObject
        headers = self.__getAuthHeader()
        headers["Content-Type"] = contentType or "text/plain"
        conn.request("PUT", url, body, headers)
        res = conn.getresponse()
        if res.status not in [OK,CREATED]:
            raise Exception("%d %s: %s" % (res.status, res.reason, res.read()))
        log.debug("File created/updated: %s" % filePath)
        return None
    
    def deleteFile(self, roId, filePath):
        """
        Deletes a file from ROSRS. This includes all metadata.
        
        Parameters: ROSRS URL, access token, RO id, file path
        """
        conn = HTTPConnection(self.rosrs_host)
        url = self.rosrs_path + urllib2.quote(self.URI_RESOURCE % (roId, filePath))
        headers = self.__getAuthHeader()
        conn.request("DELETE", url, None, headers)
        res = conn.getresponse()
        if res.status != NO_CONTENT:
            raise Exception("%d %s: %s" % (res.status, responses[res.status], res.reason))
        log.debug("File %s deleted" % filePath)
        return None
    
    def __getAuthHeader(self):
        if self.accesstoken == None:
            return dict()
        else:
            return {"Authorization": "Bearer %s" % self.accesstoken}
 
    

if __name__ == '__main__':
        pass
