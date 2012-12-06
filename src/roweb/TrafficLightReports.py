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

log = logging.getLogger(__name__)

def LIT(l): return rdflib.Literal(l)
def REF(u): return rdflib.URIRef(u)

sparql_prefixes = """
    PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd:     <http://www.w3.org/2001/XMLSchema#>
    PREFIX xml:     <http://www.w3.org/XML/1998/namespace>
    PREFIX ao:      <http://purl.org/ao/>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX foaf:    <http://xmlns.com/foaf/0.1/>
    PREFIX ro:      <http://purl.org/wf4ever/ro#>
    PREFIX wfprov:  <http://purl.org/wf4ever/wfprov#>
    PREFIX wfdesc:  <http://purl.org/wf4ever/wfdesc#>
    PREFIX minim:   <http://purl.org/minim/minim#>
    PREFIX result:  <http://www.w3.org/2001/sw/DataAccess/tests/result-set#>
    """

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

# Report inserts result of checklist evaluation item as JSON
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
            '''\n    , "itemlabel":      "%(itemlabel)s"'''+
            '''\n    , "itemlevel":      "%(itemlevel)s" '''
        , 'alt':  '''\n    *** no match fort message/label ***'''
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
              ?rouri minim:satisfied [ minim:tryRequirement ?itemuri ]
            }
            """
        },
        { 'query':  sparql_prefixes+"""ASK { ?rouri minim:satisfied [ minim:tryRequirement ?itemuri ] }"""
        , 'output':     '''\n    , "itemclass":      ["pass"]'''
        , 'altreport':
          { 'query':  sparql_prefixes+"""ASK { ?rouri minim:missingMay [ minim:tryRequirement ?itemuri ] }"""
          , 'output':   '''\n    , "itemclass":      ["fail", "may"]'''
          , 'altreport':
            { 'query':  sparql_prefixes+"""ASK { ?rouri minim:missingShould [ minim:tryRequirement ?itemuri ] }"""
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
# @@TODO: add sequence to minim model for output ordering of checklist items
#
EvalChecklistJson = (
    { 'report':
      [ { 'output':
            '''\n{ "rouri":                  "%(rouri)s"'''+
            '''\n, "roid":                   "%(roid)s"'''+
            '''\n, "checklisturi":           "%(modeluri)s"'''+
            '''\n, "checklisttarget":        "%(target)s"'''+
            '''\n, "checklisttargetlabel":   "%(targetlabel)s"'''+
            '''\n, "checklistpurpose":       "%(purpose)s"'''
        , 'query':
            sparql_prefixes+
            """
            SELECT ?rouri ?roid ?modeluri ?target ?targetlabel ?purpose WHERE
            {
              ?rouri
                dcterms:identifier ?roid ;
                minim:modelUri ?modeluri ;
                minim:testedTarget ?target ;
                minim:testedPurpose ?purpose .
              ?target rdfs:label ?targetlabel .
            }
            LIMIT 1
            """
        , 'report':
          [ { 'output':
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
                ?itemuri a minim:Requirement .
              }
              """
            }
          , { 'output':
                '''\n  ]\n}'''
            }
          ]
        }
      ]
    })

# End.
