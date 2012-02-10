# ro_metadata.py

"""
Research Object metadata (manifest and annotations) access class
"""

import sys
import os
import os.path
import re
import urlparse
import logging

log = logging.getLogger(__name__)

#import MiscLib.ScanDirectories

import rdflib
import rdflib.namespace
#from rdflib import URIRef, Namespace, BNode
#from rdflib import Literal

import ro_settings
import ro_manifest
import ro_annotation

class ro_metadata(object):
    """
    Class for accessing RO metadata
    """
    
    def __init__(self, roconfig, rodir):
        """
        Initialize: read manifest from object at given directory into local RDF graph
        """
        self.roconfig = roconfig
        self.rodir    = rodir
        self.rouri    = ro_manifest.getRoUri(rodir)
        self.manifestfilename = ro_manifest.makeManifestFilename(rodir)
        self.manifestgraph    = rdflib.Graph()
        self.manifestgraph.parse(self.manifestfilename)
        # RO URI from manifest
        # May be different from computed value if manifest has absolute URI
        self.rouri = ro_manifest.getGraphRoUri(rodir, self.manifestgraph)
        return

    def updateManifest(self):
        """
        Write updated manifest file for research object
        """
        self.manifestgraph.serialize(
            destination=self.manifestfilename, format='xml',
            base=self.rouri, xml_base="..")
        return

    def createAnnotationBody(self, roresource, anngraph):
        """
        Create a new annotation body for a single resource in a research object, based
        on a supplied graph value.

        Existing annotations for the same resource are not touched; if an annotation is being 
        added or replaced, it is the calling program'sresponsibility to update the manifest to
        reference the active annotations.  A new name is allocated for the created annotation,
        graph which is returned as the result of this function.
    
        roresource  is the name of the Research Object component to be annotated, possibly
                    relative to the RO root directory.
        attrdict    is a dictionary of attributes to be saved inthe annotation body.
                    Dictionary keys are attribute names that can be resolved via 
                    ro_annotation.getAnnotationByName.
    
        Returns the name of the annotation body created relative to the RO directory.
        """
        af = ro_annotation.createAnnotationBody(self.roconfig, self.rodir, roresource, anngraph)
        return os.path.join(ro_settings.MANIFEST_DIR+"/", af)

    def readAnnotationBody(self, annotationfile):
        """
        Read annotation body from indicated file, return RDF Graph of annotation values.
        
        annotationfile  is name of annotation file, possibly relative to the RO base directory
                        (e.g. as returned by createAnnotationBody method).
        """
        ag = ro_annotation.readAnnotationBody(self.rodir, annotationfile)
        return ag

    def addSimpleAnnotation(self, rofile, attrname, attrvalue):
        """
        Add a simple annotation to a file in a research object.
    
        rofile      names the file or resource to be annotated, possibly relative to the RO.
        attrname    names the attribute in a form recognized by getAnnotationByName
        attrvalue   is a value to be associated with the attribute
        """
        ro_annotation.addSimpleAnnotation(self.roconfig, self.rodir, rofile, attrname, attrvalue)
        return

    def removeSimpleAnnotation(self, rofile, attrname, attrvalue):
        """
        Remove a simple annotation or multiple matching annotations a research object.

        rofile      names the annotated file or resource, possibly relative to the RO.
        attrname    names the attribute in a form recognized by getAnnotationByName
        attrvalue   is the attribute value to be deleted, or Nomne to delete all vaues
        """
        ro_annotation.removeSimpleAnnotation(self.roconfig, self.rodir, rofile, attrname, attrvalue)
        return

    def replaceSimpleAnnotation(self, rofile, attrname, attrvalue):
        """
        Replace a simple annotation in a research object.
    
        rofile      names the file or resource to be annotated, possibly relative to the RO.
        attrname    names the attribute in a form recognized by getAnnotationByName
        attrvalue   is a new value to be associated with the attribute
        """
        ro_annotation.replaceSimpleAnnotation(self.roconfig, self.rodir, rofile, attrname, attrvalue)
        return

    def getRoAnnotations(self):
        """
        Returns iterator over annotations applied to the RO as an entity.

        Each value returned by the iterator is a (subject,predicate,object) triple.
        """
        return ro_annotation.getRoAnnotations(self.rodir)

    def getFileAnnotations(self, rofile):
        """
        Returns iterator over annotations applied to a specified component in the RO
    
        Each value returned by the iterator is a (subject,predicate,object) triple.
        """
        return ro_annotation.getFileAnnotations(self.rodir, rofile)

    def getAllAnnotations(self):
        """
        Returns iterator over all annotations associated with the RO
    
        Each value returned by the iterator is a (subject,predicate,object) triple.
        """
        return ro_annotation.getAllAnnotations(self.rodir)

    def getAnnotationValues(self, rofile, attrname):
        """
        Returns iterator over annotation values for given subject and attribute
        """
        return ro_annotation.getAnnotationValues(self.roconfig, self.rodir, rofile, attrname)

    def _makeAnnotationValue(self, aval, atype):
        """
        atype is one of "string", "resurce", ...
    
        Returns a graph node for the supplied type and value
        """
        #@@TODO: construct appropriately typed RDF literals
        if atype == "string":
            return rdflib.Literal(aval)
        if atype == "text":
            return rdflib.Literal(aval)
        if atype == "datetime":
            return rdflib.Literal(aval)
        if atype == "resource":
            return rdflib.URIRef(aval)
        return rdflib.Literal(aval)

    def _formatAnnotationValue(self, aval, atype):
        """
        atype is one of "string", "resurce", ...
        """
        #@@TODO: deal with appropriately typed RDF literals
        if atype == "string":
            return '"' + str(aval).replace('"', '\\"') + '"'
        if atype == "text":
            # multiline
            return '"""' + str(aval) + '"""'
        if atype == "datetime":
            return '"' + str(aval) + '"'
        if atype == "resource":
            return '<' + str(aval) + '>'
        return str(aval)

    def showAnnotations(self, annotations, outstr):
        ro_annotation.showAnnotations(self.roconfig, self.rodir, annotations, outstr)
        return 

# End.

