#!/usr/bin/python

"""
Module defining report templates for Traffic light reports of checklist evaluation.

This module primarily defines data that are used by other modules to create traffic light reports

Report definition structure:

    report-defn     = { 'report': template-item }   // May add more later

    template-item   = sequence | query-template     // Bindings to date are fed down into template-item processing

    sequence        = [ template-item, ... ]

    query-template  = { 'query':      sparql-query [None],            # Probe query for input RDF data
                        'max':        integer [1],                    # Max numberof query matches to use
                        'output':     python-format-string [None],    # Output format string for query results
                        'report':     template-item [None],           # Sub-report used with query results
                        'alt':        python-format-string [None],    # Alternate string if querry not matched
                        'altreport':  template-item [None],           # Alternate sub-report for query not matched
                        'sep':        python-format-string [None],    # Separator between query result outputs
                      }

"""

import os, os.path
import sys
import logging
import json

import rdflib

from rocommand.ro_namespaces import RDF, DCTERMS, RO, AO, ORE
from rocommand.ro_prefixes   import make_sparql_prefixes

sparql_prefixes = make_sparql_prefixes()

log = logging.getLogger(__name__)

def LIT(l): return rdflib.Literal(l)
def REF(u): return rdflib.URIRef(u)

# Report structure used to get evaluation result URI from result graph
# Query idiom adapted from http://lists.w3.org/Archives/Public/public-sparql-dev/2006JulSep/0000.html
#
# Report a inserts one of the following status URIs:
#   http://purl.org/minim/minim#fullySatifies
#   http://purl.org/minim/minim#nominallySatifies
#   http://purl.org/minim/minim#minimallySatifies
#   http://purl.org/minim/minim#potentiallySatisfies  (actually: did not satisfy)
#
# Assumed incoming bindings:
#   target  URI of target resource of evaluation
#   minim   URI of minim model for which evaluation has been performed
#
# @@TODO:
# Consider refactoring this to follow the report/altreport pattern used for
# generating result label text
#
EvalTargetResultUri = (
    { 'report':
      { 'output': "%(satisfaction)s"
      , 'alt':    "http://purl.org/minim/minim#potentiallySatisfies"
      , 'query':
        """
        SELECT ?target ?satisfaction ?minim WHERE
        {
          {
            ?target ?satisfaction ?minim .
            FILTER ( ?satisfaction = <http://purl.org/minim/minim#fullySatisfies> )
          }
          UNION
          {
            ?target ?satisfaction ?minim .
            FILTER ( ?satisfaction = <http://purl.org/minim/minim#nominallySatisfies> )
            OPTIONAL
            {
              ?target ?altsat ?minim .
              FILTER ( ?altsat = <http://purl.org/minim/minim#fullySatisfies> )
            }
            FILTER ( ! bound(?altsat) )
          }
          UNION
          {
            ?target ?satisfaction ?minim .
            FILTER ( ?satisfaction = <http://purl.org/minim/minim#minimallySatisfies> )
            OPTIONAL
            {
              ?target ?altsat ?minim .
              FILTER ( ?altsat = <http://purl.org/minim/minim#nominallySatisfies> )
            }
            FILTER ( ! bound(?altsat) )
          }
        }
        """
      }
    })

# Report structure used to get evaluation result label from result graph
#
# Report a inserts one of the following strings:
#   "fully satisfies"       (no item failures)
#   "nominally satisfies"   (failed MAY items only)
#   "minimally satisfies"   (failed SHOULD items)
#   "does not satisfy"      (failed MUST items)
#
# Assumed incoming bindings:
#   target  URI of target resource of evaluation
#   minim   URI of minim model for which evaluation has been performed
#
EvalTargetResultLabel = (
    { 'report':
      { 'output': "fully satisfies"
      , 'query':  """ASK { ?target <http://purl.org/minim/minim#fullySatisfies> ?minim }"""
      , 'altreport':
        { 'output': "nominally satisfies"
        , 'query':  """ASK { ?target <http://purl.org/minim/minim#nominallySatisfies> ?minim }"""
        , 'altreport':
          { 'output': "minimally satisfies"
          , 'query':  """ASK { ?target <http://purl.org/minim/minim#minimallySatisfies> ?minim }"""
          , 'alt': "does not satisfy"
          }
        }
      }
    })

# Report structure used to get evaluation result class list from result graph
# The intent is that these class labels can be used in conjunction with CSS-directed
# styling when generating a web page display of a checklist evaluation result.
#
# Report a inserts one of the following strings:
#   ["pass"]                (no item failures)
#   ["fail" "may"]          (failed MAY items only)
#   ["fail", "should"]      (failed SHOULD items)
#   ["fail", "must"]        (failed MUST items)
#
# Assumed incoming bindings:
#   target  URI of target resource of evaluation
#   minim   URI of minim model for which evaluation has been performed
#
EvalTargetResultClass = (
    { 'report':
      { 'output': '"pass"'
      , 'query':  """ASK { ?target <http://purl.org/minim/minim#fullySatisfies> ?minim }"""
      , 'altreport':
        { 'output': '"fail", "may"'
        , 'query':  """ASK { ?target <http://purl.org/minim/minim#nominallySatisfies> ?minim }"""
        , 'altreport':
          { 'output': '"fail", "should"'
          , 'query':  """ASK { ?target <http://purl.org/minim/minim#minimallySatisfies> ?minim }"""
          , 'alt': '"fail", "must"'
          }
        }
      }
    })

# Report inserts result of checklist item evaluation item as JSON
#
# Example of output:
#
#     { "itemuri":        "URI of checklist item"
#     , "itemlabel":      "Result label text generated from checklist item"
#     , "itemlevel":      "http://purl.org/minim/minim#hasShouldRequirement" 
#     , "itemsatisfied":  false
#     , "itemclass":      ["fail", "should"]
#     }
#
# Assumed incoming bindings:
#   rouri     URI of RO being evaluated
#   modeluri  URI of Minim model defining the evaluated checklist
#   itemuri   URI or Minim model checklist item whose result is reported
#   itemlevel URI of satisfaction level asspociated with this item:
#             minim:hasMustRequirement, minim:hasShouldRequirement or minim:hasMayRequirement
#
EvalItemJson = (
    { 'report':
      [
        { 'output':
            '''\n    { "itemuri":        "%(itemuri)s"'''+
            '''\n    , "itemlabel":      "%(itemlabel_esc)s"'''+
            '''\n    , "itemlevel":      "%(itemlevel)s" '''
        , 'alt':  '''\n    *** no match for message/label ***'''
        , 'query': sparql_prefixes+
            """
            SELECT * WHERE
            {
            ?s minim:tryRequirement ?itemuri ;
               minim:tryMessage ?itemlabel .
            }"""
        },
        { 'output':
            '''\n    , "itemsatisfied":  true'''
        , 'alt':
            '''\n    , "itemsatisfied":  false'''
        , 'query': sparql_prefixes+
            """
            SELECT * WHERE
            {
              ?target minim:satisfied [ minim:tryRequirement ?itemuri ]
            }
            """
        },
        { 'query':  sparql_prefixes+"""ASK { ?target minim:satisfied [ minim:tryRequirement ?itemuri ] }"""
        , 'output':     '''\n    , "itemclass":      ["pass"]'''
        , 'altreport':
          { 'query':  sparql_prefixes+"""ASK { ?target minim:missingMay [ minim:tryRequirement ?itemuri ] }"""
          , 'output':   '''\n    , "itemclass":      ["fail", "may"]'''
          , 'altreport':
            { 'query':  sparql_prefixes+"""ASK { ?target minim:missingShould [ minim:tryRequirement ?itemuri ] }"""
            , 'output': '''\n    , "itemclass":      ["fail", "should"]'''
            , 'alt':    '''\n    , "itemclass":      ["fail", "must"]'''
            }
          }
        },
        { 'output':
            '''\n    }'''
        },
      ]
    })

# Report generates JSON for traffic-light display
#
# The resulting JSON may be used by some other software (e.g. Javascript) to genrate an
# HTML display of a checklist evaluation result.
# 
# Outer query is per evaluated RO, extracting evaluation parameters and overall result
# Inner query is repeated for each checklist item and results (for each RO)
#
# Example output:
#
#   { "rouri":                  "file:///usr/workspace/wf4ever-ro-catalogue/v0.1/simple-requirements/"
#   , "roid":                   "simple-requirements"
#   , "checklisturi":           "file:///runnable-wf-trafficlight/checklist.rdf#Runnable_model"
#   , "checklisttarget":        "file:///usr/workspace/wf4ever-ro-catalogue/v0.1/simple-requirements/"
#   , "checklisttargetid":      "simple-requirements"
#   , "checklisttargetlabel":   "simple-requirements"
#   , "checklistpurpose":       "Runnable"
#   , "evalresult":             "http://purl.org/minim/minim#minimallySatisfies"
#   , "evalresultlabel":        "minimally satisfies"
#   , "evalresultclass":        ["fail", "should"]
#   , "checklistitems":
#     [
#       ... (EvalItemJson output, repeated)
#     ]
#   }
#
# Optional incoming bindings:
#   rouri     URI of RO evaluated
#   modeluri  URI of Minim model defining the evaluated checklist
#
EvalChecklistJson = (
    { 'report':
      [ { 'output':
            '''\n{ "rouri":                  "%(rouri)s"'''+
            '''\n, "roid":                   "%(roid)s"'''+
            '''\n, "title":                  "%(title_esc)s"'''+
            '''\n, "description":            "%(description_esc)s"'''+
            '''\n, "checklisturi":           "%(modeluri)s"'''+
            '''\n, "checklistpurpose":       "%(purpose)s"'''+
            '''\n, "checklisttarget":        "%(target)s"'''+
            # '''\n, "checklisttargetid":      "%(targetid)s"'''+
            # '''\n, "checklisttargetlabel":   "%(targetlabel_esc)s"'''+
            ''''''
        , 'query':
            sparql_prefixes+
            """
            SELECT ?rouri ?roid ?title ?description ?modeluri ?target ?targetlabel ?purpose WHERE
            {
              ?rouri
                dcterms:identifier ?roid ;
                dcterms:title ?title ;
                dcterms:description ?description ;
                minim:modelUri ?modeluri ;
                minim:testedTarget ?target ;
                minim:testedPurpose ?purpose .
            }
            LIMIT 1
            """
              # OPTIONAL { ?target rdfs:label ?targetlabel }
              # OPTIONAL { FILTER( !bound(?targetlabel) ) BIND(str(?target) as ?targetlabel) }

              # { 
              #   ?target rdfs:label ?targetlabel
              # }
              # UNION
              # {
              #   OPTIONAL { ?target rdfs:label ?targethaslabel }
              #   FILTER(!bound(?targethaslabel))
              #   BIND(str(?target) as ?targetlabel)
              # }
        , 'report':
          [ { 'output':
                '''\n, "checklisttargetid":      "%(targetid)s"'''
            , 'query':
              sparql_prefixes+
              """
              SELECT ?targetid WHERE
              {
                ?target 
                  dcterms:identifier ?targetid
              }
              """
            }
          , { 'output':
                '''\n, "checklisttargetlabel":   "%(targetlabel_esc)s"'''
            , 'query':
              sparql_prefixes+
              """
              SELECT ?targetlabel WHERE
              {
                ?target 
                  rdfs:label ?targetlabel
              }
              """
            }
          , { 'output':
                '''\n, "evalresult":             "'''
            }
          , { 'report': EvalTargetResultUri
            }
          , { 'output':
                '''"'''
            }
          , { 'output':
                '''\n, "evalresultlabel":        "'''
            }
          , { 'report': EvalTargetResultLabel
            }
          , { 'output':
                '''"'''
            }
          , { 'output':
                '''\n, "evalresultclass":        ['''
            }
          , { 'report': EvalTargetResultClass
            }
          , { 'output':
                ''']'''
            }
          , { 'output':
                '''\n, "checklistitems":\n  ['''
            }
          , { 'report': EvalItemJson
            , 'sep':    ","
            , 'query': sparql_prefixes+
              """
              SELECT ?itemuri ?itemlevel ?modeluri WHERE
              { ?modeluri ?itemlevel ?itemuri .
                ?itemuri a minim:Requirement ;
                         minim:seq ?itemseq .
              }
              ORDER BY ?itemseq
              """
            }
          , { 'output':
                '''\n  ]\n}'''
            }
          ]
        }
      ]
    })

# Report inserts result of checklist item evaluation item as HTML
#
# Example of output:
#
#           <tr>
#             <td></td>
#             <td class="trafficlight small pass must"><div/></td>
#             <td>Workflow is present</td>
#           </tr>
#
# Assumed incoming bindings:
#   target    URI of target resource being evaluated
#   modeluri  URI of Minim model defining the evaluated checklist
#   itemuri   URI or Minim model checklist item whose result is reported
#   itemlevel URI of satisfaction level asspociated with this item:
#             minim:hasMustRequirement, minim:hasShouldRequirement or minim:hasMayRequirement
#
EvalItemHtml = (
    { 'report':
      [
        { 'output':
            '''\n          <tr class="sub_result">'''+
            '''\n            <td></td>'''+
            ''''''
        }
      , { 'query':  sparql_prefixes+"""ASK { ?target minim:satisfied [ minim:tryRequirement ?itemuri ] }"""
        , 'output':     '''\n            <td class="trafficlight small pass"><div/></td>'''
        , 'altreport':
          { 'query':  sparql_prefixes+"""ASK { ?target minim:missingMay [ minim:tryRequirement ?itemuri ] }"""
          , 'output':   '''\n            <td class="trafficlight small fail may"><div/></td>'''
          , 'altreport':
            { 'query':  sparql_prefixes+"""ASK { ?target minim:missingShould [ minim:tryRequirement ?itemuri ] }"""
            , 'output': '''\n            <td class="trafficlight small fail should"><div/></td>'''
            , 'alt':    '''\n            <td class="trafficlight small fail must"><div/></td>'''
            }
          }
        }
      , { 'output':
            '''\n            <td>%(itemlabel)s</td>'''
        , 'alt':  
            '''\n            <td>*** no match for message/label ***</td>'''
        , 'query': sparql_prefixes+
            """
            SELECT * WHERE
            {
              ?s minim:tryRequirement ?itemuri ;
                 minim:tryMessage ?itemlabel .
            }"""
        }
      , { 'output':
            '''\n          </tr>'''+
            ''''''
        }
      ]
    })

# Report generates HTML for traffic-light display
#
# Example output:
#
# <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" 
#     "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
# <html xmlns="http://www.w3.org/1999/xhtml">
# 
# <html>
# 
#   <head>
#     <link rel="stylesheet" type="text/css" href="css/checklist.css" />
#     <meta http-equiv="content-type" content="text/html; charset=utf-8" />
#     <title>Research Object runnable evaluation - simple-requirements</title>
#   </head>
# 
#   <body>
#     <div class="Container">
# 
#       <div class="header">
#         Research object <a href="(Research-object-URI)">simple-requirements</a>
#       </div>
# 
#       <div class="body">
#         <table>
#           <tr>
#             <th class="trafficlight large fail should"><div/></th>
#             <th colspan="2">Target 
#               <span class="target">
#                 <a href="(Research-object-URI)">simple-requirements</a>
#               </span>
#               <span class="testresult">minimally satisfies</span> checklist for 
#               <span class="testpurpose">Runnability</span>.
#               <p>This Research Object might not be runnable.</p>
#             </th>
#           </tr>
#            :
#           (checklist items here)
#            :
#         </table>
#       </div>
# 
#       <div class="footer">
#         <hr/>
#         <div><b><a href="http://www.wf4ever-project.org">Wf4Ever project</a></b></div>
#       </div>
# 
#     </div>
#   </body>
# 
# </html>
#
# Incoming bindings:
#   @@TBD css js?
#
# Optional incoming bindings:
#   rouri     URI of RO evaluated
#   modeluri  URI of Minim model defining the evaluated checklist
#
EvalChecklistHtml = (
    { 'report':
      [ { 'output':
            '''\n<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" '''+
            '''\n    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'''+
            '''\n<html xmlns="http://www.w3.org/1999/xhtml">'''+
            '''\n<html>'''+
            '''\n  <head>'''+
            '''\n    <link rel="stylesheet" type="text/css" href="css/checklist.css" />'''+
            '''\n    <meta http-equiv="content-type" content="text/html; charset=utf-8" />'''+
            '''\n    <title>Research Object %(purpose)s evaluation - %(roid)s</title>'''+
            '''\n  </head>'''+
            ''''''
        , 'query':
            sparql_prefixes+
            """
            SELECT ?rouri ?roid ?title ?description ?modeluri ?target ?targetlabel ?purpose WHERE
            {
              ?rouri
                dcterms:identifier ?roid ;
                dcterms:title ?title ;
                dcterms:description ?description ;
                minim:modelUri ?modeluri ;
                minim:testedTarget ?target ;
                minim:testedPurpose ?purpose .
              OPTIONAL { ?target rdfs:label ?targetlabel . }
            }
            LIMIT 1
            """
        , 'report':
          [ { 'output':
                '''\n  <body>'''+
                '''\n    <div class="Container">'''+
                '''\n      <div class="header">'''+
                '''\n        %(title_esc)s'''+
                #'''\n        Research object <a href="%(rouri)s">%(roid)s</a>'''+
                '''\n      </div>'''+
                '''\n      <div class="content">'''+
                '''\n        <div class="sub_header">%(description_esc)s</div>'''+
                '''\n        <div class="body">'''+
                '''\n          <table>'''+
                '''\n            <thead>'''+
                '''\n              <tr class="main_result">'''
            }
          , { 'report':
              { 'output':
                  '''\n                <th class="trafficlight large pass"><div/></th>'''
              , 'query':  """ASK { ?target <http://purl.org/minim/minim#fullySatisfies> ?minim }"""
              , 'altreport':
                { 'output':
                    '''\n                <th class="trafficlight large fail may"><div/></th>'''
              , 'query':  """ASK { ?target <http://purl.org/minim/minim#nominallySatisfies> ?minim }"""
                , 'altreport':
                  { 'query':  """ASK { ?target <http://purl.org/minim/minim#minimallySatisfies> ?minim }"""
                  , 'output':
                      '''\n                <th class="trafficlight large fail should"><div/></th>'''
                  , 'alt':
                      '''\n                <th class="trafficlight large fail must"><div/></th>'''
                  }
                }
              }
            }
          , { 'output':
                '''\n                <th colspan="2">Target <span class="target">'''+
                '''\n                  <a href="%(target)s">%(targetlabel_esc)s</a></span> '''+
                ''''''
            }
          , { 'output':
                '''\n                  <span class="testresult">'''
            }
          , { 'report': EvalTargetResultLabel
            }
          , { 'output':
                '''</span> checklist for '''+
                '''\n                  <span class="testpurpose">%(purpose)s</span>.'''+
                '''\n                </th>'''+
                ''''''
            }
          , { 'output':
                '''\n              </tr>'''+
                '''\n            </thead>'''+
                ''''''
            }
          , { 'output':
                '''\n            <tbody class="result_detail">'''+
                ''''''
            }
          , { 'report': EvalItemHtml
            , 'query': sparql_prefixes+
              """
              SELECT ?itemuri ?itemseq ?itemlevel ?modeluri WHERE
              { ?modeluri ?itemlevel ?itemuri .
                ?itemuri a minim:Requirement ;
                         minim:seq ?itemseq .
              }
              ORDER BY ?itemseq
              """
            }
          , { 'output':
                '''\n            </tbody>'''+
                ''''''
            }
          , { 'output':
                '''\n          </table>'''+
                '''\n        </div>'''+
                '''\n        <div class="footer">'''+
                '''\n          <div><b><a href="http://www.wf4ever-project.org">Wf4Ever project</a></b></div>'''+
                '''\n        </div>'''+
                '''\n      </div>'''+
                '''\n    </div>'''+
                '''\n  </body>'''+
                '''\n</html>'''+
                ''''''
            }
          ]
        }
      ]
    })

# End.
