# ro_metadata.py

"""
Research Object metadata (manifest and annotations) access class
"""

import sys
import os
import os.path
import re
import urllib
import urlparse
import logging

log = logging.getLogger(__name__)

import MiscLib.ScanDirectories

import rdflib
import rdflib.namespace

import ro_settings
from ro_namespaces import RDF, RO, ORE, AO, DCTERMS
from ro_uriutils import isFileUri, resolveUri, resolveFileAsUri, getFilenameFromUri, isLiveUri, retrieveUri
from ROSRS_Session import ROSRS_Error, ROSRS_Session
import ro_manifest
import ro_annotation
import json
import hashlib


class ro_metadata(object):
    """
    Class for accessing RO metadata
    """

    def __init__(self, roconfig, roref, dummysetupfortest=False):
        """
        Initialize: read manifest from object at given directory into local RDF graph

        roconfig    is the research object manager configuration, supplied as a dictionary
        roref       a URI reference that refers to the Research Object to be accessed, or
                    relative path name (see ro_uriutils.resolveFileAsUri for interpretation)
        dummysetupfortest is an optional parameter that, if True, suppresses some aspects of
                    the setup (does not attempt to read a RO manifest) for isolated testing.
        """
        self.roconfig = roconfig
        self.roref    = roref
        self.dummyfortest  = dummysetupfortest
        self.manifestgraph = None
        self.roannotations = None
        self.registries = None
        uri = resolveFileAsUri(roref)
        if not uri.endswith("/"): uri += "/"
        self.rouri    = rdflib.URIRef(uri)
        if self._isLocal():
            self.rosrs = None
        else:
            self.rosrs = ROSRS_Session(
                self.roconfig["rosrs_uri"], 
                self.roconfig["rosrs_access_token"]
                )
        self._loadManifest()
        # Get RO URI from manifest
        # May be different from computed value if manifest has absolute URI
        self.rouri = self.manifestgraph.value(None, RDF.type, RO.ResearchObject)
        return

    def _isLocal(self):
        return isFileUri(self.rouri)

    def _getManifestUri(self):
        assert self._isLocal()
        return self.getComponentUri(ro_settings.MANIFEST_DIR+"/"+ro_settings.MANIFEST_FILE)

    def _loadManifest(self):
        if self.manifestgraph: return self.manifestgraph
        if self.dummyfortest:
            # Fake minimal manifest graph for testing
            self.manifestgraph = rdflib.Graph()
            self.manifestgraph.add( (self.rouri, RDF.type, RO.ResearchObject) )
        elif self._isLocal():
            # Read manifest graph
            self.manifestgraph = rdflib.Graph()
            self.manifestgraph.parse(self._getManifestUri())
        else:
            (status, reason, _h, _u, manifest) = self.rosrs.getROManifest(self.rouri)
            assert status == 200,  ("ro_metadata: Can't access manifest for %s (%03d %s)"%
                                    (str(self.rouri), status, reason))
            self.manifestgraph = manifest 
        return self.manifestgraph

    def _updateManifest(self):
        """
        Write updated manifest file for research object
        """
        assert self._isLocal()
        self._loadManifest().serialize(
            destination=self.getManifestFilename(), format='xml',
            base=self.rouri, xml_base="..")
        return

    def _iterAnnotations(self, subject=None):
        """
        Return iterator over annotation stubs in the current RO, either for
        the specified subject resource, or for all annotations in the RO
        
        subject is URI of subject whose annotations are returned, or None.
        """
        manifest = self._loadManifest()
        if self._isLocal():
            for (anode, p, subject) in manifest:
                if p in [RO.annotatesAggregatedResource, AO.annotatesResource]:
                    yield anode
        else:
            for anode in self.rosrs.getROAnnotationUris(self.getRoUri(), subject):
                yield anode
        return

    def isAggregatedResource(self, rofile):
        '''
        Returns true if the manifest says that the research object aggregates the
        resource. Resource URI is resolved against the RO URI unless it's absolute.
        '''
        resuri = self.getComponentUriAbs(rofile)
        return (self.rouri, ORE.aggregates, resuri) in self.manifestgraph

    def _loadAnnotations(self):
        if self.roannotations: return self.roannotations
        # Assemble annotation graph
        # NOTE: the manifest itself is included as an annotation by the RO setup
        if self._isLocal():
            manifest = self._loadManifest()
            self.roannotations = rdflib.Graph()
            for anode in self._iterAnnotations():
                auri = manifest.value(subject=anode, predicate=AO.body)
                self._readAnnotationBody(auri, self.roannotations)
        else:
            self.roannotations = self.rosrs.getROAnnotationGraph(self.rouri)
        log.debug("roannotations graph:\n"+self.roannotations.serialize())
        return self.roannotations

    def isInternalResource(self, resuri):
        '''
        Check if the resource is internal, i.e. should the resource content be uploaded
        to the ROSR service. Returns true if the resource URI has the RO URI as a prefix.
        '''
        return resuri.startswith(self.rouri)

    def isExternalResource(self, resuri):
        '''
        Check if the resource is external, i.e. can be aggregated as a URI reference.
        Returns true if the URI has 'http' or 'https' scheme.
        '''
        parseduri = urlparse.urlsplit(resuri)
        return parseduri.scheme in ["http", "https"]
    
    def _createAnnotationBody(self, roresource, attrdict, defaultType="string"):
        """
        Create a new annotation body for a single resource in a research object, based
        on a supplied graph value.

        Existing annotations for the same resource are not touched; if an annotation is being
        added or replaced, it is the calling program'sresponsibility to update the manifest to
        reference the active annotations.  A new name is allocated for the created annotation,
        graph which is returned as the result of this function.

        roresource  is the name of the Research Object component to be annotated,
                    possibly relative to the RO root directory.
        attrdict    is a dictionary of attributes to be saved in the annotation body.
                    Dictionary keys are attribute names that can be resolved via
                    ro_annotation.getAnnotationByName.

        Returns the name of the annotation body created relative to the RO directory.
        """
        assert self._isLocal()
        af = ro_annotation.createAnnotationBody(
            self.roconfig, self.getRoFilename(), roresource, attrdict, defaultType)
        return os.path.join(ro_settings.MANIFEST_DIR+"/", af)

    def _createAnnotationGraphBody(self, roresource, anngraph):
        """
        Create a new annotation body for a single resource in a research object, based
        on a supplied graph value.

        Existing annotations for the same resource are not touched; if an annotation is being
        added or replaced, it is the calling program'sresponsibility to update the manifest to
        reference the active annotations.  A new name is allocated for the created annotation,
        graph which is returned as the result of this function.

        roresource  is the name of the Research Object component to be annotated,
                    possibly relative to the RO root directory.
        anngraph    is an annotation graph that is to be saved.

        Returns the name of the annotation body created relative to the RO
        manifest and metadata directory.
        """
        assert self._isLocal()
        af = ro_annotation.createAnnotationGraphBody(
            self.roconfig, self.getRoFilename(), roresource, anngraph)
        return os.path.join(ro_settings.MANIFEST_DIR+"/", af)

    def _readAnnotationBody(self, annotationref, anngr=None):
        """
        Read annotation body from indicated resource, return RDF Graph of annotation values.

        annotationref   is a URI reference of an annotation, possibly relative to the RO base URI
                        (e.g. as returned by _createAnnotationBody method).
        anngr           if supplied, if an RDF graph to which the annotations are added
        """
        assert self._isLocal()
        log.debug("_readAnnotationBody %s"%(annotationref))
        annotationuri    = self.getComponentUri(annotationref)
        annotationformat = "xml"
        # Look at file extension to figure format
        # (rdflib.Graph.parse says;
        #   "used if format can not be determined from the source")
        if re.search("\.(ttl|n3)$", annotationuri): annotationformat="n3"
        if anngr == None:
            log.debug("_readAnnotationBody: new graph")
            anngr = rdflib.Graph()
        try:
            anngr.parse(annotationuri, format=annotationformat)
            log.debug("_readAnnotationBody parse %s, len %i"%(annotationuri, len(anngr)))
        except IOError, e:
            log.debug("_readAnnotationBody "+annotationref+", "+repr(e))
            anngr = None
        return anngr

    def _addAnnotationToManifest(self, rofile, annfile):
        """
        Add a new annotation body to an RO graph

        rofile      is the research object resource being annotated
        annfile     is the file name of the annotation body to be added,
                    possibly relative to the RO URI, with special characters
                    already URI-escaped.
        """
        assert self._isLocal()
        # <ore:aggregates>
        #   <ro:AggregatedAnnotation>
        #     <ro:annotatesAggregatedResource rdf:resource="data/UserRequirements-astro.ods" />
        #     <ao:body rdf:resource=".ro/(annotation).rdf" />
        #   </ro:AggregatedAnnotation>
        # </ore:aggregates>
        log.debug("_addAnnotationToManifest annfile %s"%(annfile))
        ann     = rdflib.BNode()
        resuri  = self.getComponentUri(rofile)
        bodyuri = self.getComponentUriAbs(annfile)
        self.manifestgraph.add((ann, RDF.type, RO.AggregatedAnnotation))
        self.manifestgraph.add((ann, RO.annotatesAggregatedResource, resuri))
        self.manifestgraph.add((ann, AO.body, bodyuri))
        # Aggregate the annotation
        self.manifestgraph.add((self.getRoUri(), ORE.aggregates, ann))
        # Aggregate annotation body if it is RO metadata.
        # Otherwise aggregation is the caller's responsibility
        if self.isRoMetadataRef(bodyuri):
            self.manifestgraph.add((self.getRoUri(), ORE.aggregates, bodyuri))
        return

    def _removeAnnotationFromManifest(self, ann):
        """
        Remove references to an annotation from an RO graph

        ann         is the the annotation node to be removed
        """
        assert self._isLocal()
        bodyuri = self.manifestgraph.value(subject=ann, predicate=AO.body)
        self.manifestgraph.remove((ann, None, None   ))
        # If annotation body is RO Metadata, and there are no other uses as an annotation,
        # remove it from the RO aggregation.
        if self.isRoMetadataRef(bodyuri):
            if not self.manifestgraph.value(subject=ann, predicate=AO.body):
                self.manifestgraph.remove((None, ORE.aggregates, bodyuri))
        return

    def addAggregatedResources(self, ro_file, recurse=True, includeDirs=False):
        """
        Scan a local directory and add files found to the RO aggregation
        """
        assert self._isLocal()
        def notHidden(f):
            return re.match("\.|.*/\.", f) == None
        log.debug("addAggregatedResources: roref %s, file %s"%(self.roref, ro_file))
        self.getRoFilename()  # Check that we have one
        basedir = os.path.abspath(self.roref)
        if os.path.isdir(ro_file):
            ro_file = os.path.abspath(ro_file)+os.path.sep
            #if ro_file.endswith(os.path.sep):
            #    ro_file = ro_file[0:-1]
            if recurse:
                rofiles = filter(notHidden,
                    MiscLib.ScanDirectories.CollectDirectoryContents(ro_file, 
                          baseDir=basedir,
                          listDirs=includeDirs, 
                          listFiles=True, 
                          recursive=recurse, 
                          appendSep=True
                          )
                    )
            else:
                rofiles = [ro_file.split(basedir+os.path.sep,1)[-1]]
        else:
            rofiles = [self.getComponentUriRel(ro_file)]
        s = self.getRoUri()
        for f in rofiles:
            log.debug("- file %s"%f)
            stmt = (s, ORE.aggregates, self.getComponentUri(f))
            if stmt not in self.manifestgraph: self.manifestgraph.add(stmt)
        self._updateManifest()
        return

    def removeAggregatedResource(self, resuri):
        """
        Remove a specified resource.
        
        resref is the URI of a resource to remove
        """
        assert self._isLocal()
        resuri = rdflib.URIRef(resuri)
        log.debug("removeAggregatedResource: roref %s, resuri %s"%(self.roref, str(resuri)))
        manifest = self._loadManifest()
        for anode in self._iterAnnotations(subject=resuri):
            self._removeAnnotationFromManifest(anode)
        manifest.remove((None, ORE.aggregates, resuri))
        self._updateManifest()
        return

    def getAggregatedResources(self):
        """
        Returns iterator over all resources aggregated by a manifest.

        Each value returned by the iterator is an aggregated resource URI
        """
        log.debug("getAggregatedResources: uri %s"%(self.rouri))
        for r in self._loadManifest().objects(subject=self.rouri, predicate=ORE.aggregates):
            if not isinstance(r, rdflib.BNode):
                yield r
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
        assert self._isLocal()
        ro_graph = self._loadManifest()
        self._addAnnotationToManifest(rofile, graph)
        # ann = rdflib.BNode()
        # ro_graph.add((ann, RDF.type, RO.AggregatedAnnotation))
        # ro_graph.add((ann, RO.annotatesAggregatedResource, self.getComponentUri(rofile)))
        # ro_graph.add((ann, AO.body, self.getComponentUri(graph)))
        # ro_graph.add((self.getRoUri(), ORE.aggregates, ann))
        self._updateManifest()
        return

    def isAnnotationNode(self, respath):
        '''
        Returns true if the manifest says that the research object aggregates the
        annotation and it is an ro:AggregatedAnnotation.
        Resource URI is resolved against the RO URI unless it's absolute.
        '''
        resuri = self.getComponentUriAbs(respath)
        log.debug("isAnnotationNode: ro uri %s res uri %s"%(self.rouri, resuri))
        return (self.rouri, ORE.aggregates, resuri) in self.manifestgraph and \
            (resuri, RDF.type, RO.AggregatedAnnotation) in self.manifestgraph

    def addSimpleAnnotation(self, rofile, attrname, attrvalue, defaultType="string"):
        """
        Add a simple annotation to a file in a research object.

        rofile      names the file or resource to be annotated, possibly relative to the RO.
        attrname    names the attribute in a form recognized by getAnnotationByName
        attrvalue   is a value to be associated with the attribute
        """
        assert self._isLocal()
        ro_dir   = self.getRoFilename()
        annfile  = self._createAnnotationBody(rofile, {attrname: attrvalue}, defaultType)
        self._addAnnotationToManifest(rofile, annfile)
        self._updateManifest()
        return annfile

    def removeSimpleAnnotation(self, rofile, attrname, attrvalue):
        """
        Remove a simple annotation or multiple matching annotations a research object.

        rofile      names the annotated file or resource, possibly relative to the RO.
        attrname    names the attribute in a form recognized by getAnnotationByName
        attrvalue   is the attribute value to be deleted, or Nomne to delete all vaues
        """
        assert self._isLocal()
        ro_dir    = self.getRoFilename()
        ro_graph  = self._loadManifest()
        subject     = self.getComponentUri(rofile)
        (predicate,valtype) = ro_annotation.getAnnotationByName(self.roconfig, attrname)
        val         = attrvalue and ro_annotation.makeAnnotationValue(self.roconfig, attrvalue, valtype)
        add_annotations    = []
        remove_annotations = []
        log.debug("removeSimpleAnnotation subject %s, predicate %s, val %s"%
                  (str(subject), str(predicate), val))
        # Scan for annotation graph resources containing this annotation
        for ann_node in self._iterAnnotations(subject=subject):
            ann_uri   = ro_graph.value(subject=ann_node, predicate=AO.body)
            log.debug("removeSimpleAnnotation ann_uri %s"%(str(ann_uri)))
            if self.isRoMetadataRef(ann_uri):
                ann_graph = self._readAnnotationBody(self.getComponentUriRel(ann_uri))
                log.debug("removeSimpleAnnotation ann_graph %s"%(ann_graph))
                if (subject, predicate, val) in ann_graph:
                    ann_graph.remove((subject, predicate, val))
                    if (subject, None, None) in ann_graph:
                        # Triples remain in annotation body: write new body and update RO graph
                        ann_name = self._createAnnotationGraphBody(rofile, ann_graph)
                        remove_annotations.append(ann_node)
                        add_annotations.append(ann_name)
                    else:
                        # Remove annotation from RO graph
                        remove_annotations.append(ann_node)
        # Update RO manifest graph if needed
        if add_annotations or remove_annotations:
            for a in remove_annotations:
                self._removeAnnotationFromManifest(a)
            for a in add_annotations:
                self._addAnnotationToManifest(rofile, a)
            self._updateManifest()
        return

    def replaceSimpleAnnotation(self, rofile, attrname, attrvalue):
        """
        Replace a simple annotation in a research object.

        rofile      names the file or resource to be annotated, possibly relative to the RO.
        attrname    names the attribute in a form recognized by getAnnotationByName
        attrvalue   is a new value to be associated with the attribute
        """
        assert self._isLocal()
        ro_dir   = self.getRoFilename()
        ro_graph = self._loadManifest()
        subject  = self.getComponentUri(rofile)
        (predicate,valtype) = ro_annotation.getAnnotationByName(self.roconfig, attrname)
        log.debug("Replace annotation: subject %s, predicate %s, value %s"%
                  (repr(subject), repr(predicate), repr(attrvalue)))
        ro_graph.remove((subject, predicate, None))
        ro_graph.add((subject, predicate,
                      ro_annotation.makeAnnotationValue(self.roconfig, attrvalue, valtype)))
        self._updateManifest()
        return

    def iterateAnnotations(self, subject=None, property=None):
        """
        Returns an iterator over annotations of the current RO that match the
        supplied subject and/or property.
        """
        log.debug("iterateAnnotations s:%s, p:%s"%(str(subject),str(property)))
        ann_graph = self._loadAnnotations()
        for (s, p, v) in ann_graph.triples((subject, property, None)):
            if not isinstance(s, rdflib.BNode):
                log.debug("Triple: %s %s %s"%(s,p,v))
                yield (s, p, v)
        return

    def getRoAnnotations(self):
        """
        Returns iterator over annotations applied to the RO as an entity.

        Each value returned by the iterator is a (subject,predicate,object) triple.
        """
        return self.iterateAnnotations(subject=self.getRoUri())

    def getFileAnnotations(self, rofile):
        """
        Returns iterator over annotations applied to a specified component in the RO

        Each value returned by the iterator is a (subject,predicate,object) triple.
        """
        return self.iterateAnnotations(subject=self.getComponentUri(rofile))

    def getAllAnnotations(self):
        """
        Returns iterator over all annotations associated with the RO

        Each value returned by the iterator is a (subject,predicate,object) triple.
        """
        return self.iterateAnnotations()

    def getAllAnnotationNodes(self):
        """
        Returns iterator over all annotations aggregated within the RO

        Each value returned by the iterator is a (annuri, bodyuri, target) triple.
        """
        for (ann_node, ann_target) in self.manifestgraph.subject_objects(predicate=RO.annotatesAggregatedResource):
            ann_body   = self.manifestgraph.value(subject=ann_node, predicate=AO.body)
            yield (ann_node, ann_body, ann_target)
        return

    def getAnnotationValues(self, rofile, attrname):
        """
        Returns iterator over annotation values for given subject and attribute
        """
        (predicate,valtype) = ro_annotation.getAnnotationByName(self.roconfig, attrname)
        resuri = self.getComponentUri(rofile)
        return ( v for (s,p,v) in self.iterateAnnotations(subject=resuri, property=predicate) )

    def queryAnnotations(self, query, initBindings={}):
        """
        Runs a query over the combined annotation graphs (including the manifest)
        and returns True or False (for ASK queries) or a list of doctionaries of
        query results (for SELECT queries).
        """
        ann_gr = self._loadAnnotations()
        resp = ann_gr.query(query,initBindings=initBindings)
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
    
    def replaceUri(self, ann_node, remote_ann_node_uri):
        for (p, o) in self.manifestgraph.predicate_objects(subject = ann_node):
            self.manifestgraph.remove((ann_node, p, o))
            self.manifestgraph.add((remote_ann_node_uri, p, o))
        for (s, p) in self.manifestgraph.subject_predicates(object = ann_node):
            self.manifestgraph.remove((s, p, ann_node))
            self.manifestgraph.add((s, p, remote_ann_node_uri))
        self._updateManifest()
        return

    # Support methods for accessing the manifest graph

    def roManifestContains(self, stmt):
        """
        Returns True if the RO manifest contains a statement matching the supplied triple.
        """
        return stmt in self._loadManifest()

    def getResourceValue(self, resource, predicate):
        """
        Returns value for resource whose URI is supplied assocfiated with indicated predicate
        """
        return self._loadManifest().value(subject=resource, predicate=predicate, object=None)

    def getResourceType(self, resource):
        """
        Returns type of resource whose URI is supplied
        """
        return self.getResourceValue(resource, RDF.type)

    def getRoMetadataDict(self):
        """
        Returns dictionary of metadata about the RO from the manifest graph
        """
        assert self._isLocal()
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
        """
        Return URI for component where relative reference is treated as a file path
        """
        if urlparse.urlsplit(path).scheme == "":
            path = resolveUri("", str(self.getRoUri()), path)
        return rdflib.URIRef(path)

    def getComponentUriAbs(self, path):
        """
        Return absolute URI for component where relative reference is treated as a URI reference
        """
        return rdflib.URIRef(urlparse.urljoin(str(self.getRoUri()), path))

    def getComponentUriRel(self, path):
        """
        Return reference relative to RO for a supplied URI
        """
        file_uri = urlparse.urlunsplit(urlparse.urlsplit(str(self.getComponentUriAbs(path))))
        ro_uri   = urlparse.urlunsplit(urlparse.urlsplit(str(self.getRoUri())))
        if ro_uri is not None and file_uri.startswith(ro_uri):
            file_uri_rel = file_uri.replace(ro_uri, "", 1)
        else:
            file_uri_rel = path
        return rdflib.URIRef(file_uri_rel)

    def isRoMetadataRef(self, uri):
        """
        Test if supplied URI is a reference to the current RO metadata area
        """
        assert self._isLocal()
        urirel = self.getComponentUriRel(uri)
        return str(urirel).startswith(ro_settings.MANIFEST_DIR+"/")

    def isLocalFileRo(self):
        """
        Test current RO URI to see if it is a local file system reference
        """
        return isFileUri(self.getRoUri())

    def getRoFilename(self):
        assert self._isLocal()
        return getFilenameFromUri(self.getRoUri())

    def getManifestFilename(self):
        """
        Return manifest file name: used for local updates
        """
        assert self._isLocal()
        return os.path.join(self.getRoFilename(), ro_settings.MANIFEST_DIR+"/",
                            ro_settings.MANIFEST_FILE)
        
    def getRegistries(self):
        '''
        Load a dictionary of synchronization data from memory or from a JSON file.
        '''
        log.debug("Get registries")
        if self.registries:
            return self.registries
        try:
            rf = open(os.path.join(self.getRoFilename(), ro_settings.REGISTRIES_FILE), 'r')
            self.registries = json.load(rf)
        except IOError:
            self.registries = dict()
        except Exception as e:
            log.exception(e)
            self.registries = dict()
        return self.registries
        
    def saveRegistries(self):
        '''
        Save a dictionary of synchronization data to a JSON file.
        '''
        log.debug("Save registries")
        rf = open(os.path.join(self.getRoFilename(), ro_settings.REGISTRIES_FILE), 'w')
        if self.registries:
            json.dump(self.registries, rf)
        return
    
    def calculateChecksum(self, rofile):
        '''
        Calculate a file checksum.
        '''
        m = hashlib.md5()
        with open(rofile) as f:
            for line in f:
                m.update(line)
            f.close()
        return m.hexdigest()

# End.

