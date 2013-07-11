#!/usr/bin/python

"""
This module contains codes to extract information from a checklist evaluation to create a "traffic light" display

At its core is a SPARQL-driven templating engine, which will be used initially to create a JSON representation
of RDF information from the checklist evaluation, which can be used to easily construct an HTML rendering of
the required "traffic light"

Report definition structure:

    report-defn     = { 'report': template-item }

    template-item   = sequence | query-template

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

import sys
import collections
import re
import logging
import rdflib
import json

log = logging.getLogger(__file__)

def escape_json(val):
    """
    Applies appropriate escaping to the supplied value to allow it to be included in a JSON string result.
    """
    vnew = []
    #print "val: "+repr(val)
    for c in val:
        if   c == u'"':  c = u'\\"'
        elif c == u'\\': c = u'\\\\'
        elif c == u'\b': c = u'\\b'
        elif c == u'\f': c = u'\\f'
        elif c == u'\n': c = u'\\n'
        elif c == u'\r': c = u'\\r'
        elif c == u'\t': c = u'\\t'
        elif ord(c) in range(0,32)+[127]:
            c = '\\u'+"%04x"%(ord(c))
        vnew.append(c)
    return "".join(vnew)

def escape_html(val):
    """
    Applies appropriate escaping to the supplied value to allow it to be included in HTML element text.
    """
    # Also consider: 
    #   http://stackoverflow.com/questions/1061697/whats-the-easiest-way-to-escape-html-in-python
    return val.replace('<','&lt;').replace('>','&gt;')

def escape_none(val):
    """
    Applies no escaping to the supplied value.
    """
    return val

def generate_report(repdefn, rdfgraph, initvars, outstr, escape=escape_none):
    """
    Generates a report defined to the supplied output stream.
    
    repdefn     is a structure that defines the report to be generated,
                whose structure is as outlined above.
    rdfgraph    is an RDF graph containing data that will be used to 
                populate the report
    initvars    an initial set of variable bindings that are fed into the
                report generation query process
    outstr      a stream to which the report is written
    escape      a function that escapes characters in strings used to fill
                the template
    """
    item = repdefn['report']
    process_item(repdefn['report'], rdfgraph, initvars, outstr, escape)
    return

def process_item(repitem, rdfgraph, initvars, outstr, escape):
    """
    Processes a report template item to the supplied output stream.
    
    repitem     is the report template item to be processed
    rdfgraph    is an RDF graph containing data that will be used to 
                populate the report
    initvars    an initial set of variable bindings that are fed into the
                report generation query process
    outstr      a stream to which the report is written
    escape      a function that escapes characters in strings used to fill
                the template
    """
    log.debug("process_item: repitem:  "+repr(repitem))
    log.debug("              initvars: "+repr(initvars))
    if isinstance(repitem, dict):
        # Single query template
        process_query(repitem, rdfgraph, initvars, outstr, escape)
    elif isinstance(repitem, collections.Iterable):
        # Iterable list of items - apply each
        for q in repitem:
            process_query(q, rdfgraph, initvars, outstr, escape)
    else:
        raise "Unexpected value for report template item %s"%(repr(repitem))
    return

def takefirst(n, iter):
    count = 0;
    for i in iter:
        count += 1
        if count > n: break
        yield i
    return

def process_query(qitem, rdfgraph, initvars, outstr, escape):
    """
    Process a single query+template structure
    """
    # do query
    log.debug("process_query:")
    log.debug(" - initvars: "+repr(initvars))
    query       = qitem.get('query', None)
    newbindings = [initvars]
    if query:
        for ql in query.split('\n'):
            if not re.match("\s*(PREFIX|$)", ql):
                log.debug(" - query: "+ql);
        resp = rdfgraph.query(qitem['query'],initBindings=initvars)
        if resp.type == 'ASK':
            if not resp.askAnswer: newbindings = []
        elif resp.type == 'SELECT':
            newbindings = resp.bindings
        else:
            raise "Unexpected query response type %s"%resp.type
    log.debug(" - newbindings: "+repr(newbindings))
    # Apply limit to result set
    maxrepeat   = qitem.get('max', sys.maxsize)
    newbindings = takefirst(maxrepeat, newbindings)
    # Process each binding in rsult set
    output  = qitem.get('output', None)
    report  = qitem.get('report', None)
    alt     = qitem.get('alt', None)
    altrep  = qitem.get('altreport', None)
    sep     = qitem.get('sep', None)
    usealt  = altrep or alt
    nextsep = None
    for b in newbindings:
        newbinding = initvars.copy()
        for k in b:
            if not isinstance(k,rdflib.BNode):
                newbinding[str(k)]        = b[k]
                newbinding[str(k)+"_esc"] = escape(b[k])
        if nextsep:
            outstr.write(nextsep%newbinding)
        if output:
            outstr.write(output%newbinding)
        if report:
            process_item(report, rdfgraph, newbinding, outstr, escape)
        usealt  = False
        nextsep = sep
    if usealt:
        if altrep:
            process_item(altrep, rdfgraph, initvars, outstr, escape)
        if alt:
            outstr.write(alt%initvars)
    return

# End.
