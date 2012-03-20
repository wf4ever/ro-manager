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

class ro_metadata(object):
    """
    Class for accessing RO metadata
    """

    def __init__(self, roconfig, rodir, dummysetupfortest=False):
        """
        Initialize: read manifest from object at given directory into local RDF graph
        """
        self.roconfig = roconfig
        self.rodir    = rodir
        self.rouri    = self.getRoUri()
        self.manifestfilename = self.getManifestFilename()
        self.dummyfortest     = dummysetupfortest
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
            self.manifestgraph.parse(self.manifestfilename)
        return

    def updateManifest(self):
        """
        Write updated manifest file for research object
        """
        self.manifestgraph.serialize(
            destination=self.manifestfilename, format='xml',
            base=self.rouri, xml_base="..")
        return

    def addAggregatedResources(self, ro_file, recurse=True):
        def notHidden(f):
            return re.match("\.|.*/\.", f) == None
        log.debug("addAggregatedResources: dir %s, file %s"%(self.rodir, ro_file))
        if ro_file.endswith(os.path.sep):
            ro_file = ro_file[0:-1]
        rofiles = [ro_file]
        if os.path.isdir(ro_file):
            rofiles = filter( notHidden,
                                MiscLib.ScanDirectories.CollectDirectoryContents(
                                    os.path.abspath(ro_file), baseDir=os.path.abspath(self.rodir), 
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
        log.debug("getAggregatedResources: dir %s"%(self.rodir))
        for r in self.manifestgraph.objects(subject=self.rouri, predicate=ORE.aggregates):
            yield r
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
        attrdict    is a dictionary of attributes to be saved in the annotation body.
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
        # @@TODO bring inline and update manifest graph
        ro_annotation.addSimpleAnnotation(self.roconfig, self.rodir, rofile, attrname, attrvalue)
        return

    def removeSimpleAnnotation(self, rofile, attrname, attrvalue):
        """
        Remove a simple annotation or multiple matching annotations a research object.

        rofile      names the annotated file or resource, possibly relative to the RO.
        attrname    names the attribute in a form recognized by getAnnotationByName
        attrvalue   is the attribute value to be deleted, or Nomne to delete all vaues
        """
        # @@TODO bring inline and update manifest graph
        ro_annotation.removeSimpleAnnotation(self.roconfig, self.rodir, rofile, attrname, attrvalue)
        return

    def replaceSimpleAnnotation(self, rofile, attrname, attrvalue):
        """
        Replace a simple annotation in a research object.
    
        rofile      names the file or resource to be annotated, possibly relative to the RO.
        attrname    names the attribute in a form recognized by getAnnotationByName
        attrvalue   is a new value to be associated with the attribute
        """
        # @@TODO bring inline and update manifest graph
        ro_annotation.replaceSimpleAnnotation(self.roconfig, self.rodir, rofile, attrname, attrvalue)
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
        ro_graph = ro_manifest.readManifestGraph(self.rodir)
        ann = rdflib.BNode()
        ro_graph.add((ann, RDF.type, RO.AggregatedAnnotation))
        ro_graph.add((ann, RO.annotatesAggregatedResource, ro_manifest.getComponentUri(self.rodir, rofile)))
        ro_graph.add((ann, AO.body, ro_manifest.getComponentUri(self.rodir, graph)))
        ro_graph.add((ro_manifest.getComponentUri(self.rodir, "."), ORE.aggregates, ann))
        ro_manifest.writeManifestGraph(self.rodir, ro_graph)
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

    def queryAnnotations(self, query):
        """
        Runs a query over the combined annotation graphs (including the manifest)
        and returns True or False (for ASK queries) or a list of doctionaries of 
        query results (for SELECT queries).
        """
        # @@TODO: cache annotation graph; invalidate when annotations updated.
        # Assemble annotation graph
        self._loadManifest()
        self.roannotations = rdflib.Graph()
        for (ann_node, subject) in self.manifestgraph.subject_objects(predicate=RO.annotatesAggregatedResource):
            ###print "\nann_node %s, body %s"%(repr(ann_node), repr(subject))
            ann_uri   = self.manifestgraph.value(subject=ann_node, predicate=AO.body)
            ann_file  = os.path.join(self.rodir, ro_manifest.getComponentUriRel(self.rodir, ann_uri))
            if os.path.exists(ann_file):
                ###print "Parse file; "+ann_file
                self.roannotations.parse(ann_file)
        ###print self.roannotations.serialize(
        ###    format='xml', base=ro_manifest.getRoUri(self.rodir))

        # Run query against assembled annotation graph
        print "query: "+query
        resp = self.roannotations.query(query)
        print "response:       "+repr(resp)
        print "resp.type:      "+repr(resp.type)
        print "resp.vars:      "+repr(resp.vars)
        print "resp.bindings:  "+repr(resp.bindings)
        print "resp.askAnswer: "+repr(resp.askAnswer)
        print "resp.graph:     "+repr(resp.graph)
        if resp.type == 'ASK':
            return resp.askAnswer
        elif resp.type == 'SELECT':
            return resp.bindings
        else:
            assert(False, "Unexpected query response type %s"%resp.type)









        #################################


        return None

    def showAnnotations(self, annotations, outstr):
        ro_annotation.showAnnotations(self.roconfig, self.rodir, annotations, outstr)
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
            'ropath':         self.rodir,
            'rouri':          strsubject,
            'roident':        self.getResourceValue(self.rouri, DCTERMS.identifier  ),
            'rotitle':        self.getResourceValue(self.rouri, DCTERMS.title       ),
            'rocreator':      self.getResourceValue(self.rouri, DCTERMS.creator     ),
            'rocreated':      self.getResourceValue(self.rouri, DCTERMS.created     ),
            'rodescription':  self.getResourceValue(self.rouri, DCTERMS.description ),
            }
        return manifestDict

    # Support methods for accessing RO and component URIs

    def getRoDir(self):
        """
        Returns RO directory string
        """
        return self.rodir

    def getManifestFilename(self):
        return os.path.join(self.rodir, ro_settings.MANIFEST_DIR+"/", ro_settings.MANIFEST_FILE)

    def getFileUri(self, path):
        """
        Like getComponentUri, except that path may be relative to the current directory,
        and returned URI string includes file:// scheme
        """
        filebase = "file://"
        if not path.startswith(filebase):
            path = filebase+os.path.join(os.getcwd(), path)
        return rdflib.URIRef(path)

    def getRoUri(self):
        return self.getFileUri(os.path.abspath(self.rodir)+"/")

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

# End.

