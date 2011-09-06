# $Id: DomHelpers.py 1058 2009-01-26 10:39:19Z graham $
#
# Copyright (c) 2008 WebBrick Systems Limited
# Released under the MIT licence
# See LICENCE.TXT included with these files,
# or http://www.opensource.org/licenses/mit-license.php
#

import types
from os.path import exists
from os import rename, remove, linesep

###OLD CODE:
###from xml.dom.ext.reader import Sax2
###from xml.dom.ext import Print, PrettyPrint
###END

from xml.dom import minidom

from StringIO  import StringIO
from string import strip

from Functions import concatMap

"""
Miscellaneous DOM helper functions.
"""

def parseXmlString(config):
    """
    Parse XML from a supplied string into a DOM structure
    """
    if type(config) == types.UnicodeType:
        s = StringIO(config.encode("utf-8") )
    else:
        s = StringIO(config)
    return parseXmlStream(s)

def parseXmlFile(name):
    """
    Read and parse XML from a file into a DOM structure
    """
    f = open(name,"r")
    dom = parseXmlStream(f)
    f.close()
    return dom

def saveXmlToFile(name, xmlDom, doBackup=True):
    """
    write the Xml DOM to a disk file.
    """
    if doBackup:
        if exists(name):
            if exists(name+'.bak'):
                remove(name+'.bak')
            rename( name, name+'.bak')
    f = open(name,"w")
    xmlDom.writexml(f)
    ###OLD CODE:
    ###Print(xmlDom, f)
    ###END
    f.close()

def saveXmlToFilePretty(name, xmlDom, doBackup=True):
    """
    write bthe Xml DOM to a disk file.
    """
    if doBackup:
        if exists(name):
            if exists(name+'.bak'):
                remove(name+'.bak')
            rename( name, name+'.bak')
    f = open(name,"w")
    xmlDom.writexml(f, addindent="  ", newl="\n" )
#    xmlDom.writexml(f, addindent="  ", newl=linesep )
    ###OLD CODE:
    ###Print(xmlDom, f)
    ###END
    f.close()

def parseXmlStream(inpstr):
    """
    Parse XML from a supplied stream into a DOM structure.
    Closes the stream when done.
    """
    dom = minidom.parse(inpstr)
    inpstr.close()
    ###OLD CODE:
    #### See: http://pyxml.sourceforge.net/topics/howto/node18.html
    ###reader = Sax2.Reader()
    ###dom    = reader.fromStream(configstr)
    ###configstr.close()
    ###END
    return dom

def getElemXml(node):
    """
    Return text value of xml element (include all its children in the Xml string)
    """
    return node.toxml(encoding="utf-8")
    ###OLD CODE:
    ###s = StringIO()
    ###Print(node, s)
    ###result = s.getvalue()
    ###s.close()
    ###return result
    ###END

def getElemPrettyXml(node):
    """
    Return prettyfied text value of xml element 
    (include all its children in the Xml string)
    """
    return node.toprettyxml(indent="  ", encoding="utf-8")
    ###OLD CODE:
    #s = StringIO()
    ## See: http://infohost.nmt.edu/tcc/help/pubs/pyxml/printing.html
    #PrettyPrint( node, stream=s, encoding='UTF-8', indent='  ', preserveElements=None )
    #result = s.getvalue()
    #s.close()
    #return result
    ###END

def getAttrText(elem,attr):
    """
    Return text value from a named attribute of the supplied element node.
    """
    return elem.getAttribute(attr)

def getElemText(elem):
    """
    Return text value from a single element node.
    This is a concatenation of text nodes contained within the element.
    """
    return getNodeListText(elem.childNodes)

def getNodeListText(nodelist):
    """
    Return concatenation of text values from a supplied list of nodes
    """
    rc = u""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc

def getFirstTextNodeValue(elem):
    """
    Return text value from the first named subnode of the supplied node.
    This is only the text at that node and 
    """
    return getElemText(elem)

#    for node in elem.childNodes:
#        if ( node.nodeType == node.TEXT_NODE ):
#            return node.nodeValue
#    return ""

def getNamedElem(parent, nodename):
    """
    Return first subnode of given parent with given tag name, or None
    if there is no such subnode.
    """
    nodes = parent.getElementsByTagName(nodename)
    if nodes:
        return nodes[0]
    return None

#TODO: deprecate me
def getNamedNode(node, nodename):
    """
    Return first named subnode of the supplied node
    """
    subnodes = node.getElementsByTagName(nodename)
    if len(subnodes) > 0:
        return subnodes[0]
    return None

def getNamedNodeXml(parent, nodename):
    """
    Return Xml string of the first named subnode 
    (include all its children in the Xml string),
    or None.
    """
    subnode = getNamedElem(parent, nodename)
    if subnode:
        return getElemXml(subnode)
    return None
   
def getNamedNodeText(parent, nodename):
    """
    Return text value from the first named subnode of the supplied node
    This is a concatenation of text nodes contained within the first named element.
    """
    subnode = getNamedElem(parent, nodename)
    return subnode and getElemText(subnode)

def getNamedNodeAttrText(node, nodename, attr):
    """
    Return text value from a named attribute of the first named subnode of the supplied node
    """
    elem = getNamedElem(node, nodename)
    return elem and elem.getAttribute(attr)

# Node content replacement

def removeChildren(elm):
    while elm.hasChildNodes():
        elm.removeChild(elm.firstChild)
    return elm

def replaceChildren(elm,newchildren):
    removeChildren(elm)
    for n in newchildren:
        elm.appendChild(n)
    return elm

def replaceChildrenText(elm,newtext):
    replaceChildren(elm, [elm.ownerDocument.createTextNode(newtext)])
    return elm

# Node test functions

def isElement(node):
    """
    Returns True if the supplied node is an element
    """
    return node.nodeType == node.ELEMENT_NODE

def isAttribute(node):
    """
    Returns True if the supplied node is an attribute
    """
    return node.nodeType == node.ATTRIBUTE_NODE

def isText(node):
    """
    Returns True if the supplied node is free text.
    """
    return node.nodeType == node.TEXT_NODE

# Content manipulation helpers
def escapeChar(c,d={}):
    if c == '<': return "&lt;"
    if c == '>': return "&gt;"
    if c == '&': return "&amp;"
    return d.get(c,c)

def escapeCharForHtml(c):
    return escapeChar(c,d={'\n': "<br/>"})

def escapeText(s):
    return concatMap(escapeChar, s)

def escapeTextForHtml(s):
    return concatMap(escapeCharForHtml, s)

def getDictFromXml(elm):
    """
    Turn an Xml DOM into a python dictionary, this only allows for a simple XML structure that consists only of 
    attributes, the element text and nested elements.  The attributes are stored in the dictionary by name.

    Nested elements are stored as dictionaries keyed by element tag.  The element text body is stored in the dictionary with a
    blank name, i.e. an empty string. Only text nodes, element nodes and element attributes are understood.

    Also this code will create a list of dictionaries where an element contains elements whose name is the singular
    form of its own name, i.e. the parent element is the child element name plus an 's'. Note in this case all
    other child elements are ignored.

    This code is an interim measure as we shift to using python data structures for configuration, instead of XML.

    TODO should this code use from xml.sax.saxutils import escape, unescape
    """
    nodes = None
    if elm.nodeName.endswith( 's' ):
        nodes = elm.getElementsByTagName(elm.nodeName[0:-1])

    if nodes:
        result = list()
        for node in nodes:
            result.append( getDictFromXml(node) )
    else:
        result = dict()
        # for text body of elm. Only if contains some non white space
        txt = strip(getElemText(elm))
        if txt:
            # attempt convert to numeric
#            try:
#                result[""] = int(txt)
#            except ValueError:
            result[""] = txt

        # for each attribute in elm
        if elm.attributes:
            for idx in range(elm.attributes.length):
                attr = elm.attributes.item(idx)
                # attempt convert to numeric
#                try:
#                    result[attr.name] = int(attr.value)
#                except ValueError:
                result[attr.name] = attr.value

        # for each child element in elm
        for node in elm.childNodes:
            if isElement(node):
                newVal = getDictFromXml(node)
                if result.has_key(node.nodeName):
                    # turn into list, for now skip.
                    if not isinstance( result[node.nodeName], list ):
                        ntry = result[node.nodeName]
                        result[node.nodeName] = list()
                        result[node.nodeName].append( ntry )
                    result[node.nodeName].append( newVal )
                else:
                    result[node.nodeName] = newVal
        # LPK CHANGE. An element always creates a dictionary. If there is
        # only a text entry then the dictionary has a single key of '' (the empty string)
        # flatten elements that only have content
#        if len(result) == 1 and result.has_key(''):
#            result = result['']

    return result

def getDictFromXmlString( str ):
    return getDictFromXml( parseXmlString( str ) )

def getDictFromXmlFile( fileName ):
    try :
        return getDictFromXml( parseXmlFile( fileName ) )
    except IOError, ex:  # file does not exist
        return None

def getXmlElemFromObject( doc, addTo, obj ):
    """
    Create correct element type for obj
    """
    if isinstance( obj, dict ):
        # Add multiple elements.
        for k in obj:
            # create element and recurse
            if k == '': 
                # empty string key, TEXT node.
                elm = doc.createTextNode( unicode(obj[k]) )
                addTo.appendChild( elm )

            elif isinstance( obj[k], list ):
                # Add multiple elements. Each value should be a dictionary.
                for val in obj[k]:
                    elm = doc.createElement( k )
                    addTo.appendChild( elm )
                    getXmlElemFromObject( doc, elm, val )

            elif isinstance( obj[k], dict ):
                # element
                elm = doc.createElement( k )
                addTo.appendChild( elm )
                getXmlElemFromObject( doc, elm, obj[k] )

            elif isinstance( obj[k], basestring ):
                # attribute
                atr = doc.createAttribute( k )
                addTo.setAttribute( k, unicode(obj[k]) )

            else:
                # should not get here as Dictionary form has strings, lists and dictionaries in it.
                elm = doc.createElement( k )
                addTo.appendChild( elm )
                getXmlElemFromObject( doc, elm, obj[k] )

    else:
        # add single text element.
        # Should not get here as obj should be dictionary
        # adding attributes and elements.
        elm = doc.createTextNode( unicode(obj) )
        addTo.appendChild( elm )

def getXmlDomFromDict( dct, rootElem = None ):
    """
    rootElem is the name for the root element, if None then the dct must have a 
    single root level element.
    """
    from xml.dom.minidom import getDOMImplementation
    impl = getDOMImplementation()

    if rootElem:
        newdoc = impl.createDocument(None, rootElem, None)
        getXmlElemFromObject( newdoc, newdoc.documentElement, dct )
    else:
        k1 = dct.keys()[0]
        newdoc = impl.createDocument(None, k1, None)
        getXmlElemFromObject( newdoc, newdoc.documentElement, dct[k1] )

    return newdoc

# End.
