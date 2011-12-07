# ro_annotation.py

"""
Research Object annotation read, write, decode functions
"""

import sys
import os
import os.path
import datetime
import rdflib
from rdflib.namespace import RDF
#from rdflib import URIRef, Namespace, BNode
#from rdflib import Literal

import ro_settings
import ro_manifest
from ro_manifest import DCTERMS, ROTERMS

#   Default list of annotation types
annotationTypes = (
    [ { "name": "type", "prefix": "dcterms", "localName": "type", "type": "string"
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

def getAnnotationNameByUri(ro_config, auri):
    """
    Given an attribute URI from the manifest graph, returns an 
    attribute name for displaying an attribute
    """
    for atype in ro_config["annotationTypes"]:
        if atype["fullUri"] == str(auri):
            return atype["name"]
    return str(auri)

def makeAnnotationFilename(rodir, afile):
    return os.path.join(rodir, ro_settings.MANIFEST_DIR+"/", afile)

def readAnnotationBody(rodir, annotationfile):
    """
    Read annotation body from indicated file, return RDF Graph of annotation values.
    """
    annotationfilename = makeAnnotationFilename(rodir, annotationfile)
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
    s = ro_manifest.getComponentUri(ro_dir, rofile)
    for k in attrdict:
        (p,t) = getAnnotationByName(ro_config, k)
        v = rdflib.Literal(attrdict[k])
        #@@TODO may need to take account of type here
        annGraph.add((s, p, v))
    # Create annotation body file
    annGraph.serialize(destination=makeAnnotationFilename(ro_dir, annotation_filename), 
        format='xml', base=ro_manifest.getRoUri(ro_dir), xml_base="..")
    return annotation_filename

# End.
