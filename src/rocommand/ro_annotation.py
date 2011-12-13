# ro_annotation.py

"""
Research Object annotation read, write, decode functions
"""

import sys
import os
import os.path
import datetime
import logging

log = logging.getLogger(__name__)

import rdflib
from rdflib.namespace import RDF
#from rdflib import URIRef, Namespace, BNode
#from rdflib import Literal

import ro_settings
import ro_manifest
from ro_manifest import RDF, DCTERMS, ROTERMS, RO, AO, ORE

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
    , { "name": "note", "prefix": "dcterms", "localName": "format", "type": "text"
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
    ])

def getAnnotationByName(ro_config, aname):
    """
    Given an attribute name from the command line, returns 
    attribute predicate and type URIs as a URIRef node and attribute value type
    """
    #@@TODO: deal properly with annotation types: return URIRef for type instead of name string
    for atype in ro_config["annotationTypes"]:
        if atype["name"] == aname:
            predicate = atype["fullUri"]
            valtype   = atype["type"]
            break
    else:
        predicate = aname
        valtype   = "string"
    predicate = rdflib.URIRef(predicate)
    return (predicate, valtype)

def getAnnotationByUri(ro_config, auri):
    """
    Given an attribute URI from the manifest graph, returns an 
    attribute name and type tuple for displaying an attribute
    """
    for atype in ro_config["annotationTypes"]:
        if str(atype["fullUri"]) == str(auri):
            return (atype["name"], atype["type"])
    return ("<"+str(auri)+">", "string")

def getAnnotationNameByUri(ro_config, uri):
    """
    Given an attribute URI from the manifest graph, returns an 
    attribute name for displaying an attribute
    """
    return getAnnotationByUri(ro_config, uri)[0]

def makeAnnotationFilename(rodir, afile):
    log.debug("makeAnnotationFilename: %s, %s"%(rodir, afile))
    return os.path.join(os.path.abspath(rodir), ro_settings.MANIFEST_DIR+"/", afile)

def makeComponentFilename(rodir, rofile):
    log.debug("makeComponentFilename: %s, %s"%(rodir, rofile))
    return os.path.join(rodir, rofile)

def readAnnotationBody(rodir, annotationfile):
    """
    Read annotation body from indicated file, return RDF Graph of annotation values.
    """
    annotationfilename = makeComponentFilename(rodir, annotationfile)
    rdfGraph = rdflib.Graph()
    rdfGraph.parse(annotationfilename)
    return rdfGraph

def createSimpleAnnotationBody(ro_config, ro_dir, rofile, attrdict):
    """
    Create a new annotation body for a single resource in a research object.
    A new metadata file is created for the annotation body.

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
    # Determine name for annotation body
    annotation_filename = None
    name_index = 0
    name_suffix = os.path.basename(rofile)
    if name_suffix == ".":
        name_suffix = os.path.basename(ro_dir)
    today = datetime.date.today()
    while annotation_filename == None:
        name_index += 1
        name = ("Ann-%04d%02d%02d-%04d-%s.rdf"%
                (today.year, today.month, today.day, name_index, name_suffix))
        if not os.path.exists(makeAnnotationFilename(ro_dir, name)):
            annotation_filename = name
    # Assemble data for annotation
    annGraph = rdflib.Graph()
    s = ro_manifest.getComponentUriRel(ro_dir, rofile)
    for k in attrdict:
        (p,t) = getAnnotationByName(ro_config, k)
        annGraph.add((s, p, makeAnnotationValue(attrdict[k],t)))
    # Create annotation body file
    annGraph.serialize(destination=makeAnnotationFilename(ro_dir, annotation_filename), 
        format='xml', base=ro_manifest.getRoUri(ro_dir), xml_base="..")
    return annotation_filename

def addSimpleAnnotation(ro_config, ro_dir, rofile, attrname, attrvalue):
    """
    Add a simple annotation to a file in a research object.
    
    ro_config   is the research object manager configuration, supplied as a dictionary
    ro_dir      is the research object root directory
    rofile      names the file or resource to be annotated, possibly relative to the RO.
    attrname    names the attribute in a form recognized by getAnnotationByName
    attrvalue   is a value to be associated with the attribute
    """
    #---Old logic---
    #ro_graph = ro_manifest.readManifestGraph(ro_dir)
    #subject  = ro_manifest.getComponentUriRel(ro_dir, rofile)
    #log.debug("addSimpleAnnotation: ro_dir %s, rofile %s, subject %s"%(ro_dir, rofile, repr(subject)))
    #(predicate,valtype) = getAnnotationByName(ro_config, attrname)
    #log.debug("Add annotation: subject %s"%(repr(subject)))
    #log.debug("                predicate %s, value %s"%(repr(predicate), repr(attrvalue)))
    #ro_graph.add((subject, predicate, makeAnnotationValue(attrvalue, valtype)))
    #---
    annfile = createSimpleAnnotationBody(ro_config, ro_dir, rofile, { attrname: attrvalue} )
    #<ore:aggregates>
    #  <ro:AggregatedAnnotation>
    #    <ro:annotatesAggregatedResource rdf:resource="data/UserRequirements-astro.ods" />
    #    <ao:body rdf:resource=".ro/(annotation).rdf" />
    #  </ro:AggregatedAnnotation>
    #</ore:aggregates>
    ro_graph = ro_manifest.readManifestGraph(ro_dir)
    ann = rdflib.BNode()
    ro_graph.add((ann, RDF.type, RO.AggregatedAnnotation))
    ro_graph.add((ann, RO.annotatesAggregatedResource, ro_manifest.getComponentUriRel(ro_dir, rofile)))
    ro_graph.add((ann, AO.body, ro_manifest.getComponentUriRel(ro_dir, ro_settings.MANIFEST_DIR+"/"+annfile)))
    ro_graph.add((ro_manifest.getComponentUriRel(ro_dir, "."), ORE.aggregates, ann))
    ro_manifest.writeManifestGraph(ro_dir, ro_graph)
    return

def removeSimpleAnnotation(ro_config, ro_dir, rofile, attrname, attrvalue):
    """
    Remove a simple annotation or multiple matching annotations a research object.
    
    ro_config   is the research object manager configuration, supplied as a dictionary
    ro_dir      is the research object root directory
    rofile      names the annotated file or resource, possibly relative to the RO.
    attrname    names the attribute in a form recognized by getAnnotationByName
    attrvalue   is the attribute value to be deleted, or Nomne to delete all vaues
    """
    ro_graph = ro_manifest.readManifestGraph(ro_dir)
    subject  = ro_manifest.getComponentUri(ro_dir, rofile)
    (predicate,valtype) = getAnnotationByName(ro_config, attrname)
    val = attrvalue and makeAnnotationValue(attrvalue, valtype)
    log.debug("Remove annotation: subject %s, predicate %s, value %s"%(repr(subject), repr(predicate), repr(val)))
    ro_graph.remove((subject, predicate, val))
    ro_manifest.writeManifestGraph(ro_dir, ro_graph)
    return

def replaceSimpleAnnotation(ro_config, ro_dir, rofile, attrname, attrvalue):
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
    ro_graph.add((subject, predicate, makeAnnotationValue(attrvalue, valtype)))
    ro_manifest.writeManifestGraph(ro_dir, ro_graph)
    return

def getRoAnnotations(ro_dir):
    """
    Returns iterator over annotations applied tothe RO as an entity
    """
    ro_graph = ro_manifest.readManifestGraph(ro_dir)
    subject  = ro_manifest.getRoUri(ro_dir)
    log.debug("getRoAnnotations %s"%str(subject))
    for ann_node in ro_graph.subjects(predicate=RO.annotatesAggregatedResource, object=subject):
        ann_uri   = ro_graph.value(subject=ann_node, predicate=AO.body)
        ann_graph = readAnnotationBody(ro_dir, ro_manifest.getComponentUriRel(ro_dir, ann_uri))
        for (p, v) in ann_graph.predicate_objects(subject=subject):
            log.debug("Triple: %s %s %s"%(subject,p,v))
            yield (subject, p, v)
    return

def getFileAnnotations(ro_dir, rofile):
    """
    Returns iterator over annotations applied to a specified component in the RO
    """
    log.debug("getFileAnnotations: ro_dir %s, rofile %s"%(ro_dir, rofile))
    ro_graph    = ro_manifest.readManifestGraph(ro_dir)
    subject     = ro_manifest.getComponentUri(ro_dir, rofile)
    log.debug("getFileAnnotations: %s"%str(subject))
    #@@TODO refactor common code with getRoAnnotations
    for ann_node in ro_graph.subjects(predicate=RO.annotatesAggregatedResource, object=subject):
        ann_uri   = ro_graph.value(subject=ann_node, predicate=AO.body)
        ann_graph = readAnnotationBody(ro_dir, ro_manifest.getComponentUriRel(ro_dir, ann_uri))
        for (p, v) in ann_graph.predicate_objects(subject=subject):
            log.debug("Triple: %s %s %s"%(subject,p,v))
            yield (subject, p, v)
            for (p, v) in ro_graph.predicate_objects(subject=subject):
                yield (subject, p, v)
    return

def getAllAnnotations(ro_dir):
    """
    Returns iterator over all annotations associated with the RO
    """
    ro_graph    = ro_manifest.readManifestGraph(ro_dir)
    log.debug("getAllAnnotations %s"%str(ro_dir))
    for (ann_node, subject) in ro_graph.subject_objects(predicate=RO.annotatesAggregatedResource):
        ann_uri   = ro_graph.value(subject=ann_node, predicate=AO.body)
        ann_graph = readAnnotationBody(ro_dir, ro_manifest.getComponentUriRel(ro_dir, ann_uri))
        for (p, v) in ann_graph.predicate_objects(subject=subject):
            log.debug("Triple: %s %s %s"%(subject,p,v))
            yield (subject, p, v)
    return

def makeAnnotationValue(aval, atype):
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

def formatAnnotationValue(aval, atype):
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

def showAnnotations(ro_config, ro_dir, annotations, outstr):
    sname_prev = None
    for (asubj,apred,aval) in annotations:
        #log.debug("Annotations: asubj %s, apred %s, aval %s"%
        #          (repr(asubj), repr(apred), repr(aval)))
        (aname, atype) = getAnnotationByUri(ro_config, apred)
        sname = ro_manifest.getComponentUriRel(ro_dir, str(asubj))
        log.debug("Annotations: sname %s, aname %s"%(sname, aname))
        if sname == "":
            sname = ro_manifest.getRoUri(ro_dir)
        if sname != sname_prev:
            print sname
            sname_prev = sname
        outstr.write("  %s %s\n"%(aname, formatAnnotationValue(aval, atype)))
    return

# End.
