# $Id: TestDomHelpers.py 1058 2009-01-26 10:39:19Z graham $
#
# Unit testing for WebBrick library functions (Functions.py)
# See http://pyunit.sourceforge.net/pyunit.html
#

import sys
import unittest
import logging
from os import *
from os.path import *

sys.path.append("../..")
from MiscLib.DomHelpers import *

class TestDomHelpers(unittest.TestCase):

    def setUp(self):
        self.testdoc = ( """<?xml version="1.0" encoding="iso-8859-1" ?>
<root attr="attrtext">
  <child1>
  some text
  <child11 />
  more text
  <child12>child text</child12>
  final text
  </child1>
</root>""" )
        self.testpath = "resources/"
        self.testfile = self.testpath+"TestDomHelpers.xml"
        self.savefile = self.testpath+"TestDomHelpersSave.xml"
        return

    def tearDown(self):
        return

    def doAssert(self, cond, msg):
        assert cond , msg

    # Actual tests follow

    def testParseXmlString(self):
        assert parseXmlString(self.testdoc), "Parse XML string failed"

    def testParseXmlFile(self):
        assert parseXmlFile(self.testfile), "Parse XML file failed"

    def testSaveXmlToFile(self):
        # ensure clean first
        logging.debug( self.testfile )
        logging.debug( self.savefile )
        try:
            remove( self.savefile )
        except Exception:
            pass
        testDom = parseXmlFile(self.testfile)
        saveXmlToFile(self.savefile, testDom, False)
        
        assert exists(self.savefile), "save XML file failed"
        # could expand test and run compare of data.
#        remove( self.savefile )

    def testSaveXmlToFileWithBackup(self):
        # ensure clean first
        try:
            remove( self.savefile )
        except Exception:
            pass
        testDom = parseXmlFile(self.testfile)
        saveXmlToFile(self.savefile, testDom)
        saveXmlToFile(self.savefile, testDom)
        
        assert exists(self.savefile), "save XML file failed"
        assert exists(self.savefile+".bak"), "save XML file failed"

        remove( self.savefile+".bak" )
        remove( self.savefile )

    def testGetNamedElem1(self):
        dom = parseXmlString(self.testdoc)
        elm = getNamedElem(dom, "child1")
        assert elm, "Node not found: child1"

    def testGetNamedElem2(self):
        dom = parseXmlString(self.testdoc)
        elm = getNamedElem(dom, "child12")
        assert elm, "Node not found: child12"

    def testGetNamedElem3(self):
        dom = parseXmlString(self.testdoc)
        elm = getNamedElem(dom, "child99")
        assert not elm, "Unexpected dode found: child99"

    #TODO: deprecate me
    def testGetNamedNode(self):
        dom = parseXmlString(self.testdoc)
        elm = getNamedNode(dom, "child1")
        assert elm, "Node not found: child1"

    def testElemText(self):
        dom = parseXmlString(self.testdoc)
        elm = getNamedElem(dom, "child1")
        txt = getElemText(elm)
        assert txt == "\n  some text\n  \n  more text\n  \n  final text\n  ", \
                      "Wrong element text: "+repr(txt)

    def testAttrText(self):
        dom = parseXmlString(self.testdoc)
        elm = getNamedElem(dom, "root")
        txt = getAttrText(elm,"attr")
        assert txt == "attrtext", "Wrong attribute text: "+txt

    def testNamedNodeAttrText(self):
        dom = parseXmlString(self.testdoc)
        txt = getNamedNodeAttrText(dom, "root", "attr")
        self.assertEqual( txt, "attrtext" )

    def testNodeListText(self):
        dom = parseXmlFile(self.testfile)
        elm = dom.getElementsByTagName("child1")[0]
        txt = getNodeListText(elm.childNodes)
        assert txt == "\n    some text\n    \n    more text\n    \n    final text\n  ", \
                      "Wrong element text: "+repr(txt)

    def testGetNamedNodeText(self):
        dom = parseXmlFile(self.testfile)
        txt = getNamedNodeText(dom, "child1")
        self.assertEqual( txt, "\n    some text\n    \n    more text\n    \n    final text\n  " )

    def testgetElemXml(self):
        dom = parseXmlFile(self.testfile)
        txt = getElemXml( dom.getElementsByTagName("child1")[0] )
        self.assertEqual( txt, "<child1>\n    some text\n    <child11/>\n    more text\n    <child12>child text</child12>\n    final text\n  </child1>" )

    def testgetElemPrettyXml(self):
        dom = parseXmlFile(self.testfile)
        txt = getElemPrettyXml( dom.getElementsByTagName("child1")[0] )
        self.assertEqual( txt, "<child1>\n  \n    some text\n    \n  <child11/>\n  \n    more text\n    \n  <child12>\n    child text\n  </child12>\n  \n    final text\n  \n</child1>\n" )

    def testGetNamedNodeXml(self):
        dom = parseXmlFile(self.testfile)
        txt = getNamedNodeXml( dom, "child1" )
        self.assertEqual( txt, "<child1>\n    some text\n    <child11/>\n    more text\n    <child12>child text</child12>\n    final text\n  </child1>" )

    # --- node type tests ---

    def testIsAttribute(self):
        dom = parseXmlString(self.testdoc)
        elm = getNamedElem(dom, "root")
        atr = elm.getAttributeNode("attr")
        assert isAttribute(atr),"isAttribute test (root/@attr) failed"

    def testIsAttributeElem(self):
        dom = parseXmlString(self.testdoc)
        elm = getNamedElem(dom, "root")
        assert not isAttribute(elm),"isAttribute false test (root) failed"

    def testIsAttributeText(self):
        dom = parseXmlString(self.testdoc)
        elm = getNamedElem(dom, "root")
        txt = elm.childNodes[0]
        assert not isAttribute(elm),"isAttribute false test (root/[0]) failed"

    def testIsElement(self):
        dom = parseXmlString(self.testdoc)
        elm = getNamedElem(dom, "root")
        assert isElement(elm),"isElement test (root/@attr) failed"

    def testIsElementAttr(self):
        dom = parseXmlString(self.testdoc)
        elm = getNamedElem(dom, "root")
        atr = elm.getAttributeNode("attr")
        assert not isElement(atr),"isElement false test (root/@attr) failed"

    def testIsElementText(self):
        dom = parseXmlString(self.testdoc)
        elm = getNamedElem(dom, "root")
        txt = elm.childNodes[0]
        assert not isElement(txt),"isElement false test (root/[0]) failed"

    def testIsText(self):
        dom = parseXmlString(self.testdoc)
        elm = getNamedElem(dom, "root")
        txt = elm.childNodes[0]
        assert isText(txt),"isText test (root/[0]) failed"

    def testIsTextAttr(self):
        dom = parseXmlString(self.testdoc)
        elm = getNamedElem(dom, "root")
        atr = elm.getAttributeNode("attr")
        assert not isText(atr),"isText false test (root/@attr) failed"

    def testIsTextElem(self):
        dom = parseXmlString(self.testdoc)
        elm = getNamedElem(dom, "root")
        assert not isText(elm),"isText false test (root) failed"

    def testRemoveChildren(self):
        dom = parseXmlString(self.testdoc)
        elm = getNamedElem(dom, "root")
        el1 = removeChildren(elm)
        self.assertEqual(getElemXml(elm),"""<root attr="attrtext"/>""")
        self.assertEqual(elm.childNodes, [])

    def testReplaceChildren(self):
        dom = parseXmlString(self.testdoc)
        elm = getNamedElem(dom, "root")
        c1  = getNamedElem(elm, "child11")
        c2  = getNamedElem(elm, "child12")
        replaceChildren(elm,[c1,c2])
        self.assertEqual(getElemXml(elm),
          """<root attr="attrtext">"""+
          """<child11/>"""+
          """<child12>child text</child12>"""+
          """</root>""")

    def testReplaceChildrenText(self):
        dom = parseXmlString(self.testdoc)
        elm = getNamedElem(dom, "root")
        replaceChildrenText(elm,"replacement text")
        self.assertEqual(getElemXml(elm),
          """<root attr="attrtext">"""+
          """replacement text"""+
          """</root>""")

    def testEscapeText(self):
        self.assertEqual(
          escapeText("<tag>Jack & Jill</tag>"),
          "&lt;tag&gt;Jack &amp; Jill&lt;/tag&gt;")

    def testEscapeTextForHtml(self):
        self.assertEqual(
          escapeTextForHtml("<tag>\nJack & Jill\n</tag>\n"),
          "&lt;tag&gt;<br/>Jack &amp; Jill<br/>&lt;/tag&gt;<br/>")

    def testPrintDictionary(self, dic):
        for key in dic:
            if isinstance( dic[key], list ):
                logging.debug( "%s : list " % ( key ) )
                for ntry in dic[key]:
                    # print list
                    if isinstance( ntry, dict ):
                        self.testPrintDictionary(ntry )
                    else:
                        logging.debug( "%s : %s " % ( key, ntry ) )
            elif isinstance( dic[key], dict ):
                logging.debug( "%s : dictionary " % ( key ) )
                self.testPrintDictionary(dic[key] )
            else:
                logging.debug( "%s : %s " % ( key, dic[key] ) )

    def testGetXmlFromDict(self):
        testDict = { 'root': { '': 'string', 
                            'child1': { '': 'string1', 'attr1':'attr1text' },
                            'child2': { '': 'string2', 'attr2':'attr2text',
                                    'child21': { '': 'string21', 'attr21':'attr21text' }, 
                                    },
                            } 
                   }
        testStr = ("""<?xml version="1.0" encoding="utf-8"?>"""+
                   """<root>string<child1 attr1="attr1text">string1</child1>"""+
                   """<child2 attr2="attr2text">string2"""+
                   """<child21 attr21="attr21text">string21</child21>"""+
                   """</child2></root>""")

        dom = getXmlDomFromDict( testDict )

        domTxt = getElemXml( dom )

        logging.debug( repr(testDict) )
        logging.debug( repr(dom) )
        logging.debug( domTxt )
        logging.debug( testStr )

        testDict = getDictFromXml( dom )
        logging.debug( repr(testDict) )

        #add some checks
        #order is not always the same as the dictionary has its own random order
        self.assertEqual( domTxt, testStr )

    def testGetXmlFromDict2(self):
        testDict = { 'root': { 'simpleVal': 'string', 
                            'listVal':[ 'string1', 'string2', 'string3' ],
                            'listVal2':[ { 'key11': 'string11', 'key12': 'string12', 'key13': 'string13'}, 
                                        { 'key21': 'string21', 'key22': 'string22', 'key23': 'string23'},
                                        ] 
                            } 
                   }
        testStr = """<?xml version="1.0" encoding="utf-8"?><root><simpleVal>string</simpleVal><listVal>string1</listVal><listVal>string2</listVal><listVal>string3</listVal><listVal2><key11>string11</key11><key12>string12</key12><key13>string13'</key13><listVal2><listVal2><key21>string21</key21><key22>string22</key22><key23>string23'</key23><listVal2><root>"""

        dom = getXmlDomFromDict( testDict )

        domTxt = getElemXml( dom )

        logging.debug( repr(testDict) )
        logging.debug( repr(dom) )
        logging.debug( domTxt )
        logging.debug( testStr )

        testDict = getDictFromXml( dom )
        logging.debug( repr(testDict) )

        #add some checks
        #order is not always the same as the dictionary has its own random order
        #self.assertEqual( domTxt, testStr )

    def testGetDictFromSimpleXml(self):

        self.testdoc = ( """<?xml version="1.0" encoding="iso-8859-1" ?>
<root attr="attrtext">
  <child1>child1 text</child1>
  <child2 attr2="attr2text">child2 text</child2>
</root>""" )

        logging.debug( self.testdoc )
        dom = parseXmlString(self.testdoc)
        testDict = getDictFromXml( dom )
        logging.debug( repr(testDict) )
        #self.testPrintDictionary(testDict)
        self.assert_( testDict.has_key( "root" ) )

        rootDict = testDict["root"]
        self.assert_( rootDict.has_key( "attr" ) )
        self.assert_( isinstance(rootDict["attr"], basestring) )
        self.assertEqual( rootDict["attr"], "attrtext" )

        self.assert_( rootDict.has_key( "child1" ) )
        self.assert_( isinstance(rootDict["child1"], dict) )
        child1Dict = rootDict["child1"]
        self.assert_( child1Dict.has_key( "" ) )    # text element
        self.assertEqual( child1Dict[""], "child1 text" )

        self.assert_( rootDict.has_key( "child2" ) )
        self.assert_( isinstance(rootDict["child2"], dict) )
        child2Dict = rootDict["child2"]
        self.assert_( child2Dict.has_key( "" ) )    # text element
        self.assertEqual( child2Dict[""], "child2 text" )
        self.assert_( child2Dict.has_key( "attr2" ) )    # text element
        self.assert_( isinstance(child2Dict["attr2"], basestring) )
        self.assertEqual( child2Dict["attr2"], "attr2text" )
                      
    def testGetDictFromXml(self):

        self.testdoc = ( """<?xml version="1.0" encoding="iso-8859-1" ?>
<root attr="attrtext">
  <child1>
  some text
  <child11 />
  more text
  <child12>child text</child12>
  final text
  </child1>
  <repeats>
      <repeat>
        repeat 1
      </repeat>
      <repeat>
        repeat 2
      </repeat>
  </repeats>
  <repeat>
    repeat 1
  </repeat>
  <repeat>
    repeat 2
  </repeat>
</root>""" )

        logging.debug( repr(self.testdoc) )
        dom = parseXmlString(self.testdoc)
        testDict = getDictFromXml( dom )
        logging.debug( repr(testDict) )
        self.assert_( testDict.has_key( "root" ) )
        rootDict = testDict["root"]
        self.assert_( rootDict.has_key( "child1" ) )
        child1Dict = rootDict["child1"]
        self.assertEqual( child1Dict[""],
                    "some text\n  \n  more text\n  \n  final text" )
        self.assertEqual( rootDict["attr"],
                    "attrtext" )
        self.assert_( child1Dict.has_key( "child11" ) )
        self.assert_( child1Dict.has_key( "child12" ) )
        self.assertEqual( child1Dict["child12"][''],
                    "child text" )
        self.assert_( rootDict.has_key( "repeats" ) )
        self.assert_( isinstance( rootDict["repeats"], list ) )
        self.assert_( rootDict.has_key( "repeat" ) )
        self.assert_( isinstance( rootDict["repeat"], list ) )

    def testGetDictFromXml2(self):

        self.testdoc = ( """<?xml version="1.0" encoding="iso-8859-1" ?>
<eventInterfaces>
    <eventInterface module='TestDespatchTask' name='TestEventLogger'>
        <!-- This saves all events -->
        <eventtype type="type1">
            <eventsource source="source1" >
            <event>
                    <!-- interested in all events -->
            </event>
            </eventsource>
        </eventtype>
    </eventInterface>
    <eventInterface module='TestDespatchTask2' name='TestEventLogger2'>
        <!-- This saves all events -->
        <eventtype type="type2">
            <eventsource source="source2" >
            <event>
                    <!-- interested in all events -->
            </event>
            </eventsource>
            <eventsource source="source3" >
            <event>
                    <!-- interested in all events -->
            </event>
            </eventsource>
        </eventtype>
        <eventtype type="type3">
            <eventsource source="source4" >
            <event>
                    <!-- interested in all events -->
                    <params>
                        <second type="list">5,20,35,50</second>
                    </params>
            </event>
            <event>
                    <!-- interested in all events -->
                    <params>
                        <second>5</second>
                    </params>
            </event>
            </eventsource>
        </eventtype>
    </eventInterface>
</eventInterfaces>""" )

        logging.debug( repr(self.testdoc) )
        dom = parseXmlString(self.testdoc)
        testDict = getDictFromXml( dom )
        logging.debug( repr(testDict) )
        self.assert_( testDict.has_key( "eventInterfaces" ) )
        self.testPrintDictionary( testDict )

# Code to run unit tests directly from command line.
# Constructing the suite manually allows control over the order of tests.
def getTestSuite():
    suite = unittest.TestSuite()
    suite.addTest(TestDomHelpers("testParseXmlString"))
    suite.addTest(TestDomHelpers("testParseXmlFile"))
    suite.addTest(TestDomHelpers("testSaveXmlToFile"))
    suite.addTest(TestDomHelpers("testSaveXmlToFileWithBackup"))
    suite.addTest(TestDomHelpers("testGetNamedElem1"))
    suite.addTest(TestDomHelpers("testGetNamedElem2"))
    suite.addTest(TestDomHelpers("testGetNamedElem3"))

    suite.addTest(TestDomHelpers("testElemText"))
    suite.addTest(TestDomHelpers("testAttrText"))
    suite.addTest(TestDomHelpers("testNodeListText"))
    suite.addTest(TestDomHelpers("testIsAttribute"))
    suite.addTest(TestDomHelpers("testIsAttributeElem"))
    suite.addTest(TestDomHelpers("testIsAttributeText"))
    suite.addTest(TestDomHelpers("testIsElement"))
    suite.addTest(TestDomHelpers("testIsElementAttr"))
    suite.addTest(TestDomHelpers("testIsElementText"))
    suite.addTest(TestDomHelpers("testIsText"))
    suite.addTest(TestDomHelpers("testIsTextAttr"))
    suite.addTest(TestDomHelpers("testIsTextElem"))

    suite.addTest(TestDomHelpers("testGetNamedNodeXml"))
    suite.addTest(TestDomHelpers("testgetElemXml"))
    suite.addTest(TestDomHelpers("testgetElemPrettyXml"))
    suite.addTest(TestDomHelpers("testGetNamedNodeText"))
    suite.addTest(TestDomHelpers("testNamedNodeAttrText"))

    suite.addTest(TestDomHelpers("testRemoveChildren"))
    suite.addTest(TestDomHelpers("testReplaceChildren"))
    suite.addTest(TestDomHelpers("testReplaceChildrenText"))

    suite.addTest(TestDomHelpers("testEscapeText"))
    suite.addTest(TestDomHelpers("testEscapeTextForHtml"))
    
    return suite

if __name__ == "__main__":
    # unittest.main()

    if len(sys.argv) > 1:
        logging.basicConfig(level=logging.DEBUG)
        tests = TestDomHelpers( sys.argv[1] )
    else:
        tests = getTestSuite()

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(tests)
