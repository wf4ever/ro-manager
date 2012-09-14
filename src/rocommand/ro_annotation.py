# ro_annotation.py

"""
Research Object annotation read, write, decode functions
"""

import sys
import os
import os.path
import datetime
import logging
import re
import urlparse

log = logging.getLogger(__name__)

import rdflib
#from rdflib.namespace import RDF, RDFS
#from rdflib import URIRef, Namespace, BNode
#from rdflib import Literal

import ro_settings
import ro_manifest
from ro_namespaces import RDF, RDFS, RO, AO, ORE, DCTERMS, ROTERMS
from ro_uriutils   import resolveUri, resolveFileAsUri

#   Default list of annotation types
annotationTypes = (
    [
      { "name": "type", "prefix": "dcterms", "localName": "type", "type": "string"
      , "baseUri": DCTERMS.baseUri, "fullUri": DCTERMS.type
      , "label": "Type"
      , "description": "Word or brief phrase describing type of Research Object component"
      }
    , { "name": "keywords", "prefix": "dcterms", "localName": "subject", "type": "termlist"
      , "baseUri": DCTERMS.baseUri, "fullUri": DCTERMS.subject
      , "label": "Keywords"
      , "description": "List of key words or phrases associated with a Research Object component"
      }
    , { "name": "description", "prefix": "dcterms", "localName": "description", "type": "text"
      , "baseUri": DCTERMS.baseUri, "fullUri": DCTERMS.description
      , "label": "Description"
      , "description": "Extended description of Research Object component"
      }
    , { "name": "format", "prefix": "dcterms", "localName": "format", "type": "string"
      , "baseUri": DCTERMS.baseUri, "fullUri": DCTERMS.format
      , "label": "Data format"
      , "description": "String indicating the data format of a Research Object component"
      }
    , { "name": "note", "prefix": "dcterms", "localName": "note", "type": "text"
      , "baseUri": ROTERMS.baseUri, "fullUri": ROTERMS.note
      , "label": "Note"
      , "description": "String indicating some information about a Research Object component"
      }
    , { "name": "title", "prefix": "dcterms", "localName": "title", "type": "string"
      , "baseUri": DCTERMS.baseUri, "fullUri": DCTERMS.title
      , "label": "Title"
      , "description": "Title of Research Object component"
      }
    , { "name": "created", "prefix": "dcterms", "localName": "created", "type": "datetime"
      , "baseUri": DCTERMS.baseUri, "fullUri": DCTERMS.created
      , "label": "Creation time"
      , "description": "Date and time that Research Object component was created"
      }
    , { "name": "rdf:type", "prefix": "rdf", "localName": "type", "type": "resource"
      , "baseUri": RDF.baseUri, "fullUri": RDF.type
      , "label": "RDF type"
      , "description": "RDF type of the annotated object"
      }
    , { "name": "rdfs:seeAlso", "prefix": "rdfs", "localName": "seeAlso", "type": "resource"
      , "baseUri": RDFS.baseUri, "fullUri": RDFS.seeAlso
      , "label": "See also"
      , "description": "Related resource with further information"
      }
    ])

# Default list of annotation prefixes
annotationPrefixes = (
    { "rdf":       "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    , "rdfs":      "http://www.w3.org/2000/01/rdf-schema#"
    , "owl":       "http://www.w3.org/2002/07/owl#"
    , "xsd":       "http://www.w3.org/2001/XMLSchema#"
    , "rdfg":      "http://www.w3.org/2004/03/trix/trix-1/"
    , "skos":      "http://www.w3.org/2004/02/skos/core#"
    , "foaf":      "http://xmlns.com/foaf/0.1/"
    , "dc":        "http://purl.org/dc/elements/1.1/"
    , "dcterms":   "http://purl.org/dc/terms/"
    , "ore":       "http://www.openarchives.org/ore/terms/"
    , "ao":        "http://purl.org/ao/"
    , "ro":        "http://purl.org/wf4ever/ro#"
    , "roterms":   "http://purl.org/wf4ever/roterms#"
    , "roevo":     "http://purl.org/wf4ever/roevo#"
    , "wfdesc":    "http://purl.org/wf4ever/wfdesc#"
    , "wfprov":    "http://purl.org/wf4ever/wfprov#"
    , "ex":        "http://example.org/ro/annotation#"
    })

# Annotation support functions
def getResourceNameString(ro_config, rname, base=None):
    """
    Returns a string value corresoponding to a URI indicated by the supplied parameter.
    Relative references are assumed to be paths relative to the supplied base URI or,
    if no rbase is supplied, relative to the current directory.
    """
    rsplit = rname.split(":")
    if len(rsplit) == 2:
        # Try to interpret name as CURIE
        for rpref in ro_config["annotationPrefixes"]:
            if rsplit[0] == rpref:
                rname = ro_config["annotationPrefixes"][rpref]+rsplit[1]
    if urlparse.urlsplit(rname).scheme == "":
        if base:
            rname = resolveUri(rname, base)
        else:
            rname = resolveFileAsUri(rname)
    return rname

def getAnnotationByName(ro_config, aname, defaultType="string"):
    """
    Given an attribute name from the command line, returns
    attribute predicate and type URIs as a URIRef node and attribute value type
    """
    predicate = aname
    valtype   = defaultType
    for atype in ro_config["annotationTypes"]:
        # Try to interpret attribute name as predefined name
        if atype["name"] == aname:
            predicate = atype["fullUri"]
            valtype   = atype["type"]
            break
    else:
        predicate = getResourceNameString(ro_config, aname, base=ROTERMS.defaultBase+"#")
    predicate = rdflib.URIRef(predicate)
    return (predicate, valtype)

def getAnnotationByUri(ro_config, auri, defaultType="string"):
    """
    Given an attribute URI from the manifest graph, returns an
    attribute name and type tuple for displaying an attribute
    """
    # Look for predefined name
    for atype in ro_config["annotationTypes"]:
        if str(atype["fullUri"]) == str(auri):
            return (atype["name"], atype["type"])
    # Look for CURIE match
    for (pref,puri) in ro_config["annotationPrefixes"].iteritems():
        if auri.startswith(puri):
            return (pref+":"+auri[len(puri):], defaultType)
    # return full URI in angle brackets
    return ("<"+str(auri)+">", defaultType)

def getAnnotationNameByUri(ro_config, uri):
    """
    Given an attribute URI from the manifest graph, returns an
    attribute name for displaying an attribute
    """
    return getAnnotationByUri(ro_config, uri)[0]

def makeAnnotationFilename(rodir, afile):
    #log.debug("makeAnnotationFilename: %s, %s"%(rodir, afile))
    return os.path.join(os.path.abspath(rodir), ro_settings.MANIFEST_DIR+"/", afile)

def makeComponentFilename(rodir, rofile):
    log.debug("makeComponentFilename: %s, %s"%(rodir, rofile))
    return os.path.join(rodir, rofile)

def readAnnotationBody(rodir, annotationfile):
    """
    Read annotation body from indicated file, return RDF Graph of annotation values.
    """
    log.debug("readAnnotationBody: %s, %s"%(rodir, annotationfile))
    annotationfilename = makeComponentFilename(rodir, annotationfile)
    if not os.path.exists(annotationfilename): return None
    annotationformat   = "xml"
    # Look at file extension to figure format
    if re.search("\.(ttl|n3)$", annotationfile): annotationformat="n3"
    rdfGraph = rdflib.Graph()
    rdfGraph.parse(annotationfilename, format=annotationformat)
    return rdfGraph

def createAnnotationGraphBody(ro_config, ro_dir, rofile, anngraph):
    """
    Create a new annotation body for a single resource in a research object, based
    on a supplied graph value.

    Existing annotations for the same resource are not touched; if an annotation is being
    added or replaced, it is the calling program'sresponsibility to update the manifest to
    reference the active annotations.  A new name is allocated for the created annotation,
    graph which is returned as the result of this function.

    ro_config   is the research object manager configuration, supplied as a dictionary
    ro_dir      is the research object root directory
    rofile      is the name of the Research Object component to be annotated, possibly
                relative to the RO root directory.
    anngraph    is an annotation graph that is to be saved.

    Returns the name of the annotation body created relative to the RO
    manifest and metadata directory.
    """
    # Determine name for annotation body
    log.debug("createAnnotationGraphBody: %s, %s"%(ro_dir, rofile))
    annotation_filename = None
    name_index = 0
    name_suffix = os.path.basename(rofile)
    if name_suffix in [".",""]:
        name_suffix = os.path.basename(os.path.normpath(ro_dir))
    today = datetime.date.today()
    while annotation_filename == None:
        name_index += 1
        name = ("Ann-%04d%02d%02d-%04d-%s.rdf"%
                (today.year, today.month, today.day, name_index, name_suffix))
        if not os.path.exists(makeAnnotationFilename(ro_dir, name)):
            annotation_filename = name
    # Create annotation body file
    log.debug("createAnnotationGraphBody: %s"%(annotation_filename))
    anngraph.serialize(destination=makeAnnotationFilename(ro_dir, annotation_filename),
        format='xml', base=ro_manifest.getRoUri(ro_dir), xml_base="..")
    return annotation_filename

def createAnnotationBody(ro_config, ro_dir, rofile, attrdict, defaultType="string"):
    """
    Create a new annotation body for a single resource in a research object.

    Existing annotations for the same resource are not touched; if an annotation is being
    added or replaced, it is the calling program'sresponsibility to update the manifest to
    reference the active annotations.  A new name is allocated for the created annotation,
    which is returned as the result of this function.

    ro_config   is the research object manager configuration, supplied as a dictionary
    ro_dir      is the research object root directory
    rofile      is the name of the Research Object component to be annotated, possibly
                relative to the RO root directory.
    attrdict    is a dictionary of attributes to be saved inthe annotation body.
                Dictionary keys are attribute names that can be resolved via getAnnotationByName.

    Returns the name of the annotation body created relative to the RO
    manifest and metadata directory.
    """
    # Assemble data for annotation
    anngraph = rdflib.Graph()
    s = ro_manifest.getComponentUri(ro_dir, rofile)
    for k in attrdict:
        (p,t) = getAnnotationByName(ro_config, k, defaultType)
        anngraph.add((s, p, makeAnnotationValue(ro_config, attrdict[k],t)))
    # Write graph and return filename
    return createAnnotationGraphBody(ro_config, ro_dir, rofile, anngraph)

def _addAnnotationBodyToRoGraph(ro_graph, ro_dir, rofile, annfile):
    """
    Add a new annotation body to an RO graph

    ro_graph    graph to which annotation is added
    ro_dir      is the research object directory
    rofile      is the research object file being annotated
    annfile     is the base file name of the annotation body to be added
    """
    # <ore:aggregates>
    #   <ro:AggregatedAnnotation>
    #     <ro:annotatesAggregatedResource rdf:resource="data/UserRequirements-astro.ods" />
    #     <ao:body rdf:resource=".ro/(annotation).rdf" />
    #   </ro:AggregatedAnnotation>
    # </ore:aggregates>
    ann = rdflib.BNode()
    ro_graph.add((ann, RDF.type, RO.AggregatedAnnotation))
    ro_graph.add((ann, RO.annotatesAggregatedResource, ro_manifest.getComponentUri(ro_dir, rofile)))
    ro_graph.add((ann, AO.body, ro_manifest.getComponentUri(ro_dir, ro_settings.MANIFEST_DIR+"/"+annfile)))
    ro_graph.add((ro_manifest.getComponentUri(ro_dir, "."), ORE.aggregates, ann))
    return

def _removeAnnotationBodyFromRoGraph(ro_graph, annbody):
    """
    Remove references to an annotation body from an RO graph

    ro_graph    graph from which annotation is removed
    annbody     is the the annotation body node to be removed
    """
    ro_graph.remove((annbody, None,           None   ))
    ro_graph.remove((None,    ORE.aggregates, annbody))
    return

def _addSimpleAnnotation(ro_config, ro_dir, rofile, attrname, attrvalue):
    """
    Add a simple annotation to a file in a research object.

    ro_config   is the research object manager configuration, supplied as a dictionary
    ro_dir      is the research object root directory
    rofile      names the file or resource to be annotated, possibly relative to the RO.
    attrname    names the attribute in a form recognized by getAnnotationByName
    attrvalue   is a value to be associated with the attribute
    """
    annfile = createAnnotationBody(ro_config, ro_dir, rofile, { attrname: attrvalue} )
    ro_graph = ro_manifest.readManifestGraph(ro_dir)
    _addAnnotationBodyToRoGraph(ro_graph, ro_dir, rofile, annfile)
    ro_manifest.writeManifestGraph(ro_dir, ro_graph)
    return

def _removeSimpleAnnotation(ro_config, ro_dir, rofile, attrname, attrvalue):
    """
    Remove a simple annotation or multiple matching annotations a research object.

    ro_config   is the research object manager configuration, supplied as a dictionary
    ro_dir      is the research object root directory
    rofile      names the annotated file or resource, possibly relative to the RO.
    attrname    names the attribute in a form recognized by getAnnotationByName
    attrvalue   is the attribute value to be deleted, or Nomne to delete all vaues
    """
    log.debug("removeSimpleAnnotation: ro_dir %s, rofile %s, attrname %s, attrvalue %s"%
              (ro_dir, rofile, attrname, attrvalue))
    # Enumerate annotations
    # For each:
    #     if annotation is only one in graph then:
    #         remove aggregated annotation
    #     else:
    #         create new annotation graph witj annotation removed
    #         update aggregated annotation
    ro_graph    = ro_manifest.readManifestGraph(ro_dir)
    subject     = ro_manifest.getComponentUri(ro_dir, rofile)
    (predicate,valtype) = getAnnotationByName(ro_config, attrname)
    val         = attrvalue and makeAnnotationValue(ro_config, attrvalue, valtype)
    #@@TODO refactor common code with getRoAnnotations, etc.
    add_annotations = []
    remove_annotations = []
    for ann_node in ro_graph.subjects(predicate=RO.annotatesAggregatedResource, object=subject):
        ann_uri   = ro_graph.value(subject=ann_node, predicate=AO.body)
        ann_graph = readAnnotationBody(ro_dir, ro_manifest.getComponentUriRel(ro_dir, ann_uri))
        if (subject, predicate, val) in ann_graph:
            ann_graph.remove((subject, predicate, val))
            if (subject, None, None) in ann_graph:
                # Triples remain in annotation body: write new body and update RO graph
                ann_name = createAnnotationGraphBody(ro_config, ro_dir, rofile, ann_graph)
                remove_annotations.append(ann_node)
                add_annotations.append(ann_name)
            else:
                # Remove annotation from RO graph
                remove_annotations.append(ann_node)
    # Update RO graph if needed
    if add_annotations or remove_annotations:
        for a in remove_annotations:
            _removeAnnotationBodyFromRoGraph(ro_graph, a)
        for a in add_annotations:
            _addAnnotationBodyToRoGraph(ro_graph, ro_dir, rofile, a)
        ro_manifest.writeManifestGraph(ro_dir, ro_graph)
    return

def _replaceSimpleAnnotation(ro_config, ro_dir, rofile, attrname, attrvalue):
    """
    Replace a simple annotation in a research object.

    ro_config   is the research object manager configuration, supplied as a dictionary
    ro_dir      is the research object root directory
    rofile      names the file or resource to be annotated, possibly relative to the RO.
    attrname    names the attribute in a form recognized by getAnnotationByName
    attrvalue   is a new value to be associated with the attribute
    """
    ro_graph = ro_manifest.readManifestGraph(ro_dir)
    subject  = ro_manifest.getComponentUri(ro_dir, rofile)
    (predicate,valtype) = getAnnotationByName(ro_config, attrname)
    log.debug("Replace annotation: subject %s, predicate %s, value %s"%(repr(subject), repr(predicate), repr(attrvalue)))
    ro_graph.remove((subject, predicate, None))
    ro_graph.add((subject, predicate, makeAnnotationValue(ro_config, attrvalue, valtype)))
    ro_manifest.writeManifestGraph(ro_dir, ro_graph)
    return

def _getAnnotationValues(ro_config, ro_dir, rofile, attrname):
    """
    Returns iterator over annotation values for given subject and attribute
    """
    log.debug("getAnnotationValues: ro_dir %s, rofile %s, attrname %s"%(ro_dir, rofile, attrname))
    ro_graph    = ro_manifest.readManifestGraph(ro_dir)
    subject     = ro_manifest.getComponentUri(ro_dir, rofile)
    (predicate,valtype) = getAnnotationByName(ro_config, attrname)
    #@@TODO refactor common code with getRoAnnotations, etc.
    for ann_node in ro_graph.subjects(predicate=RO.annotatesAggregatedResource, object=subject):
        ann_uri   = ro_graph.value(subject=ann_node, predicate=AO.body)
        ann_graph = readAnnotationBody(ro_dir, ro_manifest.getComponentUriRel(ro_dir, ann_uri))
        for v in ann_graph.objects(subject=subject, predicate=predicate):
            #log.debug("Triple: %s %s %s"%(subject,p,v))
            yield v
    return

def _getRoAnnotations(ro_dir):
    """
    Returns iterator over annotations applied to the RO as an entity.

    Each value returned by the iterator is a (subject,predicate,object) triple.
    """
    ro_graph = ro_manifest.readManifestGraph(ro_dir)
    subject  = ro_manifest.getRoUri(ro_dir)
    log.debug("getRoAnnotations %s"%str(subject))
    for ann_node in ro_graph.subjects(predicate=RO.annotatesAggregatedResource, object=subject):
        ann_uri   = ro_graph.value(subject=ann_node, predicate=AO.body)
        ann_graph = readAnnotationBody(ro_dir, ro_manifest.getComponentUriRel(ro_dir, ann_uri))
        if ann_graph:
            for (p, v) in ann_graph.predicate_objects(subject=subject):
                #log.debug("Triple: %s %s %s"%(subject,p,v))
                yield (subject, p, v)
    return

def _getFileAnnotations(ro_dir, rofile):
    """
    Returns iterator over annotations applied to a specified component in the RO

    Each value returned by the iterator is a (subject,predicate,object) triple.
    """
    log.debug("getFileAnnotations: ro_dir %s, rofile %s"%(ro_dir, rofile))
    ro_graph    = ro_manifest.readManifestGraph(ro_dir)
    subject     = ro_manifest.getComponentUri(ro_dir, rofile)
    log.debug("getFileAnnotations: %s"%str(subject))
    #@@TODO refactor common code with getRoAnnotations, etc.
    for ann_node in ro_graph.subjects(predicate=RO.annotatesAggregatedResource, object=subject):
        ann_uri   = ro_graph.value(subject=ann_node, predicate=AO.body)
        ann_graph = readAnnotationBody(ro_dir, ro_manifest.getComponentUriRel(ro_dir, ann_uri))
        if ann_graph:
            for (p, v) in ann_graph.predicate_objects(subject=subject):
                #log.debug("Triple: %s %s %s"%(subject,p,v))
                yield (subject, p, v)
    return

def getAllAnnotations(ro_dir):
    """
    Returns iterator over all annotations associated with the RO

    Each value returned by the iterator is a (subject,predicate,object) triple.
    """
    log.debug("getAllAnnotations %s"%str(ro_dir))
    ro_graph    = ro_manifest.readManifestGraph(ro_dir)
    #@@TODO refactor common code with getRoAnnotations, etc.
    for (ann_node, subject) in ro_graph.subject_objects(predicate=RO.annotatesAggregatedResource):
        ann_uri   = ro_graph.value(subject=ann_node, predicate=AO.body)
        log.debug("- ann_uri %s"%(str(ann_uri)))
        ann_graph = readAnnotationBody(ro_dir, ro_manifest.getComponentUriRel(ro_dir, ann_uri))
        if ann_graph == None:
            log.debug("No annotation graph: ann_uri: "+str(ann_uri))
        else:
            for (p, v) in ann_graph.predicate_objects(subject=subject):
                #log.debug("Triple: %s %s %s"%(subject,p,v))
                yield (subject, p, v)
    return

def makeAnnotationValue(ro_config, aval, atype):
    """
    atype is one of "string", "resurce", ...

    Returns a graph node for the supplied type and value
    """
    #@@TODO: construct appropriately typed RDF literals
    if atype == "resource":
        return rdflib.URIRef(getResourceNameString(ro_config, aval))
    if atype == "string":
        return rdflib.Literal(aval)
    if atype == "text":
        return rdflib.Literal(aval)
    if atype == "datetime":
        return rdflib.Literal(aval)
    return rdflib.Literal(aval)

def formatAnnotationValue(aval, atype):
    """
    atype is one of "string", "resurce", ...
    """
    #@@TODO: deal with appropriately typed RDF literals
    if atype == "resource" or isinstance(aval,rdflib.URIRef):
        return '<' + str(aval) + '>'
    if atype == "string":
        return '"' + str(aval).replace('"', '\\"') + '"'
    if atype == "text":
        # multiline
        return '"""' + str(aval) + '"""'
    if atype == "datetime":
        return '"' + str(aval) + '"'
    return str(aval)

def showAnnotations(ro_config, ro_dir, annotations, outstr):
    sname_prev = None
    for (asubj,apred,aval) in annotations:
        #log.debug("Annotations: asubj %s, apred %s, aval %s"%
        #          (repr(asubj), repr(apred), repr(aval)))
        if apred != ORE.aggregates:
            (aname, atype) = getAnnotationByUri(ro_config, apred)
            sname = ro_manifest.getComponentUriRel(ro_dir, str(asubj))
            log.debug("Annotations: sname %s, aname %s"%(sname, aname))
            if sname == "":
                sname = ro_manifest.getRoUri(ro_dir)
            if sname != sname_prev:
                print "\n<"+sname+">"
                sname_prev = sname
            outstr.write("  %s %s\n"%(aname, formatAnnotationValue(aval, atype)))
    return

# End.
