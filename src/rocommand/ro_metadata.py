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

import MiscLib.ScanDirectories

import rdflib
import rdflib.namespace
#from rdflib import Namespace, URIRef, BNode, Literal
# Set up to use SPARQL
rdflib.plugin.register(
    'sparql', rdflib.query.Processor,
    'rdfextras.sparql.processor', 'Processor')
rdflib.plugin.register(
    'sparql', rdflib.query.Result,
    'rdfextras.sparql.query', 'SPARQLQueryResult')

import ro_settings
from ro_namespaces import RDF, RO, ORE, AO, DCTERMS
import ro_manifest
import ro_annotation

fileuribase = "file://"

class ro_metadata(object):
    """
    Class for accessing RO metadata
    """

    def __init__(self, roconfig, roref, dummysetupfortest=False):
        """
        Initialize: read manifest from object at given directory into local RDF graph

        roconfig    is the research object manager configuration, supplied as a dictionary
        roref       a URI reference that refers to the Research Object to be accessed
        """
        self.roconfig = roconfig
        self.roref    = roref
        base = fileuribase+os.path.abspath(os.getcwd())+"/"
        uri  = urlparse.urljoin(base, roref)
        if not uri.endswith("/"): uri += "/" 
        self.rouri    = rdflib.URIRef(uri)
        self.manifesturi  = self.getManifestUri()
        self.dummyfortest = dummysetupfortest
        self._loadManifest()
        # Get RO URI from manifest
        # May be different from computed value if manifest has absolute URI
        self.rouri = self.manifestgraph.value(None, RDF.type, RO.ResearchObject)
        return

    def _loadManifest(self):
        self.manifestgraph    = rdflib.Graph()
        if self.dummyfortest:
            # Fake minimal manifest graph for testing
            self.manifestgraph.add( (self.rouri, RDF.type, RO.ResearchObject) )
        else:
            # Read manifest graph
            self.manifestgraph.parse(self.manifesturi)
        return

    def updateManifest(self):
        """
        Write updated manifest file for research object
        """
        self.manifestgraph.serialize(
            destination=self.getManifestFilename(), format='xml',
            base=self.rouri, xml_base="..")
        return

    def addAggregatedResources(self, ro_file, recurse=True):
        """
        Scan a local directory and add files found to the RO aggregation
        """
        def notHidden(f):
            return re.match("\.|.*/\.", f) == None
        log.debug("addAggregatedResources: ref %s, file %s"%(self.roref, ro_file))
        self.getRoFilename()  # Check that we have one
        if ro_file.endswith(os.path.sep):
            ro_file = ro_file[0:-1]
        rofiles = [ro_file]
        if os.path.isdir(ro_file):
            rofiles = filter( notHidden,
                                MiscLib.ScanDirectories.CollectDirectoryContents(
                                    os.path.abspath(ro_file), baseDir=os.path.abspath(self.roref), 
                                    listDirs=False, listFiles=True, recursive=recurse, appendSep=False)
                            )
        #s = self.getComponentUri(".")
        s = self.getRoUri()
        for f in rofiles:
            log.debug("- file %s"%f)
            stmt = (s, ORE.aggregates, self.getComponentUri(f))
            if stmt not in self.manifestgraph: self.manifestgraph.add(stmt)
        self.updateManifest()
        return

    def getAggregatedResources(self):
        """
        Returns iterator over all resources aggregated by a manifest.
    
        Each value returned by the iterator is an aggregated resource URI
        """
        log.debug("getAggregatedResources: uri %s"%(self.rouri))
        for r in self.manifestgraph.objects(subject=self.rouri, predicate=ORE.aggregates):
            yield r
        return

    def createAnnotationBody(self, roresource, attrdict):
        """
        Create a new annotation body for a single resource in a research object, based
        on a supplied graph value.

        Existing annotations for the same resource are not touched; if an annotation is being 
        added or replaced, it is the calling program'sresponsibility to update the manifest to
        reference the active annotations.  A new name is allocated for the created annotation,
        graph which is returned as the result of this function.
    
        roresource  is the name of the Research Object component to be annotated, possibly
                    relative to the RO root directory.
        attrdict    is a dictionary of attributes to be saved in the annotation body.
                    Dictionary keys are attribute names that can be resolved via 
                    ro_annotation.getAnnotationByName.
    
        Returns the name of the annotation body created relative to the RO directory.
        """
        af = ro_annotation.createAnnotationBody(self.roconfig, self.getRoFilename(), roresource, attrdict)
        return os.path.join(ro_settings.MANIFEST_DIR+"/", af)

    def readAnnotationBody(self, annotationref, anngr=None):
        """
        Read annotation body from indicated resource, return RDF Graph of annotation values.
        
        annotationref   is a URI reference of an annotation, possibly relative to the RO base URI
                        (e.g. as returned by createAnnotationBody method).
        """
        log.debug("readAnnotationBody %s"%(annotationref))
        annotationuri    = self.getComponentUri(annotationref)
        annotationformat = "xml"
        # Look at file extension to figure format
        # (rdflib.Graph.parse says; 
        #   "used if format can not be determined from the source")
        if re.search("\.(ttl|n3)$", annotationuri): annotationformat="n3"
        if anngr == None:
            log.debug("readAnnotationBody: new graph")
            anngr = rdflib.Graph()
        try:
            anngr.parse(annotationuri, format=annotationformat)
            log.debug("readAnnotationBody parse %s, len %i"%(annotationuri, len(anngr)))
        except Exception(e):  # @@TODO Make this more explicit
            print str(e)
            anngr = None
        return anngr

    def addSimpleAnnotation(self, rofile, attrname, attrvalue):
        """
        Add a simple annotation to a file in a research object.
    
        rofile      names the file or resource to be annotated, possibly relative to the RO.
        attrname    names the attribute in a form recognized by getAnnotationByName
        attrvalue   is a value to be associated with the attribute
        """
        # @@TODO bring inline and update manifest graph
        ro_annotation.addSimpleAnnotation(self.roconfig, self.getRoFilename(), rofile, attrname, attrvalue)
        return

    def removeSimpleAnnotation(self, rofile, attrname, attrvalue):
        """
        Remove a simple annotation or multiple matching annotations a research object.

        rofile      names the annotated file or resource, possibly relative to the RO.
        attrname    names the attribute in a form recognized by getAnnotationByName
        attrvalue   is the attribute value to be deleted, or Nomne to delete all vaues
        """
        # @@TODO bring inline and update manifest graph
        ro_annotation.removeSimpleAnnotation(self.roconfig, self.getRoFilename(), rofile, attrname, attrvalue)
        return

    def replaceSimpleAnnotation(self, rofile, attrname, attrvalue):
        """
        Replace a simple annotation in a research object.
    
        rofile      names the file or resource to be annotated, possibly relative to the RO.
        attrname    names the attribute in a form recognized by getAnnotationByName
        attrvalue   is a new value to be associated with the attribute
        """
        # @@TODO bring inline and update manifest graph
        ro_annotation.replaceSimpleAnnotation(self.roconfig, self.getRoFilename(), rofile, attrname, attrvalue)
        return

    def addGraphAnnotation(self, rofile, graph):
        """
        Add an annotation graph for a named resource.  Unlike addSimpleAnnotation, this
        method adds an annotation to the manifest using an existing RDF graph (which is
        presumably itself in the RO structure).
        
        rofile      names the file or resource to be annotated, possibly relative to the RO.
                    Note that no checks are performed to ensure that the graph itself actually
                    refers to this resource - that's up the the creator of the graph.  This
                    identifies the resourfce with which the annotation body is associated in
                    the RO manifest.
        graph       names the file or resource containing the annotation body.
        """
        # @@TODO manifest read/write inline
        rodir = self.getRoFilename()
        ro_graph = ro_manifest.readManifestGraph(rodir)
        ann = rdflib.BNode()
        ro_graph.add((ann, RDF.type, RO.AggregatedAnnotation))
        ro_graph.add((ann, RO.annotatesAggregatedResource, self.getComponentUri(rofile)))
        ro_graph.add((ann, AO.body, self.getComponentUri(graph)))
        ro_graph.add((self.getRoUri(), ORE.aggregates, ann))
        ro_manifest.writeManifestGraph(rodir, ro_graph)
        return

    def getRoAnnotations(self):
        """
        Returns iterator over annotations applied to the RO as an entity.

        Each value returned by the iterator is a (subject,predicate,object) triple.
        """
        # @@TODO annotation read inline      
        return ro_annotation.getRoAnnotations(self.getRoFilename())

    def getFileAnnotations(self, rofile):
        """
        Returns iterator over annotations applied to a specified component in the RO
    
        Each value returned by the iterator is a (subject,predicate,object) triple.
        """
        # @@TODO annotation read inline      
        return ro_annotation.getFileAnnotations(self.getRoFilename(), rofile)

    def getAllAnnotations(self):
        """
        Returns iterator over all annotations associated with the RO
    
        Each value returned by the iterator is a (subject,predicate,object) triple.
        """
        # @@TODO annotation read inline      
        return ro_annotation.getAllAnnotations(self.getRoFilename())

    def getAnnotationValues(self, rofile, attrname):
        """
        Returns iterator over annotation values for given subject and attribute
        """
        # @@TODO annotation read inline      
        return ro_annotation.getAnnotationValues(self.roconfig, self.getRoFilename(), rofile, attrname)

    def queryAnnotations(self, query):
        """
        Runs a query over the combined annotation graphs (including the manifest)
        and returns True or False (for ASK queries) or a list of doctionaries of 
        query results (for SELECT queries).
        """
        # @@TODO: cache annotation graph; invalidate when annotations updated.
        # Assemble annotation graph
        # NOTE: the manifest itself is included as an annotation by the RO setup
        self._loadManifest()
        self.roannotations = rdflib.Graph()
        for (ann_node, subject) in self.manifestgraph.subject_objects(predicate=RO.annotatesAggregatedResource):
            ann_uri   = self.manifestgraph.value(subject=ann_node, predicate=AO.body)
            self.readAnnotationBody(ann_uri, self.roannotations)
        # Run query against assembled annotation graph
        resp = self.roannotations.query(query)
        if resp.type == 'ASK':
            return resp.askAnswer
        elif resp.type == 'SELECT':
            return resp.bindings
        else:
            assert False, "Unexpected query response type %s"%resp.type
        return None

    def showAnnotations(self, annotations, outstr):
        ro_annotation.showAnnotations(self.roconfig, self.getRoFilename(), annotations, outstr)
        return 

    # Support methods for accessing the manifest graph

    def _getRoManifestGraph(self):
        """
        Returns RDF graph containing RO manifest
        """
        return self.manifestgraph

    def roManifestContains(self, stmt):
        """
        Returns True if the RO manifest contains a statement matching the supplied triple.
        """
        return stmt in self.manifestgraph

    def getResourceValue(self, resource, predicate):
        """
        Returns value for resource whose URI is supplied assocfiated with indicated predicate
        """
        return self.manifestgraph.value(subject=resource, predicate=predicate, object=None)

    def getResourceType(self, resource):
        """
        Returns type of resource whose URI is supplied
        """
        return self.getResourceValue(resource, RDF.type)

    def getRoMetadataDict(self):
        """
        Returns dictionary of metadata about the RO from the manifest graph
        """
        strsubject = ""
        if isinstance(self.rouri, rdflib.URIRef): strsubject = str(self.rouri)
        manifestDict = {
            'ropath':         self.getRoFilename(),
            'rouri':          strsubject,
            'roident':        self.getResourceValue(self.rouri, DCTERMS.identifier  ),
            'rotitle':        self.getResourceValue(self.rouri, DCTERMS.title       ),
            'rocreator':      self.getResourceValue(self.rouri, DCTERMS.creator     ),
            'rocreated':      self.getResourceValue(self.rouri, DCTERMS.created     ),
            'rodescription':  self.getResourceValue(self.rouri, DCTERMS.description ),
            }
        return manifestDict

    # Support methods for accessing RO and component URIs

    def getRoRef(self):
        """
        Returns RO URI reference supplied (which may be a local file directory string)
        """
        return self.roref

    def getRoUri(self):
        return self.rouri

    def getComponentUri(self, path):
        return rdflib.URIRef(urlparse.urljoin(str(self.getRoUri()), path))

    def getComponentUriRel(self, path):
        file_uri = urlparse.urlunsplit(urlparse.urlsplit(str(self.getComponentUri(path))))
        ro_uri   = urlparse.urlunsplit(urlparse.urlsplit(str(self.getRoUri())))
        if ro_uri is not None and file_uri.startswith(ro_uri):
            file_uri_rel = file_uri.replace(ro_uri, "", 1)
        else:
            file_uri_rel = path
        return rdflib.URIRef(file_uri_rel)

    def getManifestUri(self):
        return self.getComponentUri(ro_settings.MANIFEST_DIR+"/"+ro_settings.MANIFEST_FILE)

    def getFileUri(self, path):
        """
        Like getComponentUri, except that path may be relative to the current directory,
        and returned URI string includes file:// scheme
        """
        if not path.startswith(fileuribase):
            path = fileuribase+os.path.join(os.getcwd(), path)
        return rdflib.URIRef(path)

    def isLocalFileRo(self):
        """
        Test current RO URI to see if it is a local file system reference
        """
        return self.getRoUri().startswith("file://")

    def getRoFilename(self):
        assert self.isLocalFileRo(), "RO %s is not in local file system"%self.getRoUri()
        return self.rouri[len("file://"):]

    def getManifestFilename(self):
        """
        Return manifesrt file name: used for local updates
        """
        return os.path.join(self.getRoFilename(), ro_settings.MANIFEST_DIR+"/", ro_settings.MANIFEST_FILE)

# End.

