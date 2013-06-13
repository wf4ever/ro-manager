# ro_eval_minim.py

"""
Research Object evaluation withj respoect to a MINIM description
"""

#import sys
#import os
#import os.path
#import urlparse
import re
import subprocess
import logging
import urllib

log = logging.getLogger(__name__)

import rdflib
#import rdflib.namespace
#from rdflib import URIRef, Namespace, BNode
#from rdflib import Literal
from uritemplate import uritemplate

from rocommand.ro_uriutils   import isLiveUri, resolveUri
from rocommand.ro_namespaces import RDF, RDFS, ORE, DCTERMS
from rocommand.ro_metadata   import ro_metadata
from rocommand.ro_prefixes   import make_sparql_prefixes
import ro_minim
from ro_minim import MINIM, RESULT

def doQuery(rometa, queryPattern, queryVerb=None, resultMod="", queryPrefixes=None, initBindings=None):
    # @@TODO - factor out query construction from various places below to use this
    querytemplate = (make_sparql_prefixes(queryPrefixes or [])+
        """
        BASE <%(querybase)s>

        %(queryverb)s
        {
          %(querypattern)s
        } %(resultmod)s
        """)
    queryparams = (
        { 'querybase':    str(rometa.getRoUri())
        , 'queryverb':    queryVerb or "SELECT * WHERE"
        , 'querypattern': queryPattern
        , 'resultmod':    resultMod or ""
        })
    query = querytemplate%queryparams
    log.debug(" - doQuery: "+query)
    resp  = rometa.queryAnnotations(query, initBindings=initBindings)
    return resp

def getLabel(rometa, target):
    """
    Discover or make up a label for the designated resource
    """
    targetlabel = str(target)
    resp = doQuery(rometa, "<%s> rdfs:label ?label ."%(targetlabel))
    if len(resp) > 0: targetlabel = resp[0]['label']
    log.debug("getLabel %s"%(targetlabel))
    return targetlabel

def evaluate(rometa, minim, target, purpose):
    """
    Evaluate a RO against a minimum information model for a particular
    purpose with respect to a particular target resource.

    rometa      is an ro_metadata object used to access the RO being evaluated
    minim       is a URI-reference (relative to the RO, or absolute) of the
                minim description to be used.
    target      is a URI-reference (relative to the RO, or absolute) of a 
                target resource with respect to which the evaluation is
                performed.
    purpose     is a string that identifies a purpose w.r.t. the target for
                which completeness will be evaluated.
                
    'target' and 'purpose' are ued together to select a particular minim Model
    that will be used for the evaluation.  For example, to evaluate whether an 
    RO is sufficiently complete to support creation (a purpose) of a specified
    output file (a target).
    
    There are two main steps to the evaluation process:
    1. locate the minim model constraint for the target resource and purpose
    2. evaluate the RO against the selected model.
    
    The function returns a pair of values (minimgraph, evalresult)
    
    minimgraph is a copy of the minim graph on which the evaluation was based.
    
    The evalresult indicates a summary and details of the analysis; e.g.
      { 'summary':        [MINIM.fullySatisfies, MINIM.nominallySatisfies, MINIM.minimallySatisfies]
      , 'missingMust':    []
      , 'missingShould':  []
      , 'missingMay':     []
      , 'rouri':          rouri
      , 'roid':           roid
      , 'description':    rodesc
      , 'minimuri':       minim
      , 'target':         target
      , 'targetlabel':    targetlabel
      , 'purpose':        purpose
      , 'constrainturi':  constraint['uri']
      , 'modeluri':       model['uri']
      }
    """
    # Locate the constraint model requirements
    rouri        = rometa.getRoUri()
    roid         = rometa.getResourceValue(rouri, DCTERMS.identifier)
    if roid == None:
        roid = str(rouri)
        if roid.endswith('/'): roid = roid[0:-1]
        roid = roid.rpartition('/')[2]
    rotitle      = ( rometa.getAnnotationValue(rouri, DCTERMS.title) or 
                     rometa.getAnnotationValue(rouri, RDFS.label) or
                     roid
                   )
    rodesc       = rometa.getAnnotationValue(rouri, DCTERMS.description) or rotitle
    minimuri     = rometa.getComponentUri(minim)
    minimgraph   = ro_minim.readMinimGraph(minimuri)
    constraint   = ro_minim.getConstraint(minimgraph, rouri, target, purpose)
    assert constraint != None, "Missing minim:Constraint for target %s, purpose %s"%(target, purpose)
    cbindings    = { 'targetro':   constraint['targetro_actual']
                   , 'targetres':  constraint['targetres_actual']
                   }
    model        = ro_minim.getModel(minimgraph, constraint['model'])
    assert model != None, "Missing minim:Model for target %s, purpose %s"%(target, purpose)
    requirements = ro_minim.getRequirements(minimgraph, model['uri'])
    # Evaluate the individual model requirements
    reqeval = []
    for r in requirements:
        log.info("evaluate: %s %s %s"%(r['level'],str(r['uri']),r['seq']))
        if 'datarule' in r:
            # @@TODO: factor to separate function?
            #         (This is a deprecated form, as it locks the rule to a particular resource)
            satisfied = rometa.roManifestContains( (rouri, ORE.aggregates, r['datarule']['aggregates']) )
            reqeval.append((r,satisfied,{}))
            log.debug("- %s: %s"%(repr((rouri, ORE.aggregates, r['datarule']['aggregates'])), satisfied))
        elif 'softwarerule' in r:
            # @@TODO: factor to separate function
            cmnd = r['softwarerule']['command']
            resp = r['softwarerule']['response']
            log.debug("softwarerule: %s -> %s"%(cmnd,resp))
            out = unicode(subprocess.check_output(cmnd.split(), stderr=subprocess.STDOUT))
            exp = re.compile(resp)
            satisfied = exp.match(out)
            reqeval.append((r,satisfied,{}))
            log.debug("- Software %s: response %s,  satisfied %s"%
                      (cmnd, resp, "OK" if satisfied else "Fail"))
        elif 'contentmatchrule' in r:
            (satisfied, bindings) = evalContentMatch(rometa, r['contentmatchrule'], cbindings)
            reqeval.append((r,satisfied,bindings))
            log.debug("- ContentMatch: rule %s, bindings %s, satisfied %s"%
                      (repr(r['contentmatchrule']), repr(bindings), "OK" if satisfied else "Fail"))
        elif 'querytestrule' in r:
            (satisfied, bindings, msg) = evalQueryTest(rometa, r['querytestrule'], cbindings)
            reqeval.append((r,satisfied,bindings))
            log.debug("- QueryTest: rule %s, bindings %s, satisfied %s"%
                      (repr(r['querytestrule']), repr(bindings), "OK" if satisfied else "Fail"))
        else:
            raise ValueError("Unrecognized requirement rule: %s"%repr(r.keys()))
    # Evaluate overall satisfaction of model
    targetlabel = getLabel(rometa, target)
    eval_result = (
        { 'summary':        []
        , 'missingMust':    []
        , 'missingShould':  []
        , 'missingMay':     []
        , 'satisfied':      []
        , 'rouri':          rouri
        , 'roid':           roid
        , 'title':          rotitle
        , 'description':    rodesc
        , 'minimuri':       minimuri
        , 'target':         target
        , 'targetlabel':    targetlabel
        , 'purpose':        purpose
        , 'constrainturi':  constraint['uri']
        , 'modeluri':       model['uri']
        })
    # sat_levels initially assume all requirements pass, then reset levels achieved as
    # individual requirements are examined.
    sat_levels = (
        { 'MUST':   MINIM.minimallySatisfies
        , 'SHOULD': MINIM.nominallySatisfies
        , 'MAY':    MINIM.fullySatisfies
        })
    for (r, satisfied, binding) in reqeval:
        if satisfied:
            eval_result['satisfied'].append((r, binding))
        else:
            if r['level'] == "MUST":
                eval_result['missingMust'].append((r, binding))
                sat_levels['MUST']   = None
                sat_levels['SHOULD'] = None
                sat_levels['MAY']    = None
            elif r['level'] == "SHOULD":
                eval_result['missingShould'].append((r, binding))
                sat_levels['SHOULD'] = None
                sat_levels['MAY']    = None
            elif r['level'] == "MAY":
                eval_result['missingMay'].append((r, binding))
                sat_levels['MAY'] = None
    eval_result['summary'] = [ sat_levels[k] for k in sat_levels if sat_levels[k] ]
    return (minimgraph, eval_result)

def evalContentMatch(rometa, rule, constraintbinding):
    """
    rometa      ro_metadata for RO to test
    rule        requirement rule to evaluate
    constraintbinding
                value bindings generated by constraint matching:
                'targetro' and 'targetres'
    """
    log.debug("evalContentMatch: rule: \n  %s, \nconstraintbinding:\n  %s"%(repr(rule), repr(constraintbinding)))
    querytemplate = (make_sparql_prefixes()+
        """
        %(queryverb)s
        {
          %(querypattern)s
        } %(queryorder)s
        """)
    satisfied     = True
    simplebinding = constraintbinding.copy()
    if rule['forall']:
        exists   = rule['exists']
        template = rule['template']
        islive   = rule['islive']
        assert (exists or template or islive), (
            "minim:forall construct requires "+
            "minim:aggregatesTemplate, minim:isLiveTemplate and/or minim:exists value")
        if template:  template = str(template).strip()
        if islive:    islive   = str(islive).strip()
        queryparams = (
            { 'queryverb':    "SELECT * WHERE"
            , 'querypattern': rule['forall']
            , 'queryorder':   rule['orderby'] or ""
            })
        query = querytemplate%queryparams
        log.debug(" - forall query: "+query)
        ### @@TODO: Why is this failing?
        # resp  = rometa.queryAnnotations(query, initBindings=constraintbinding)
        resp  = rometa.queryAnnotations(query)
        log.debug(" - forall resp: "+repr(resp))
        simplebinding['_count'] = len(resp)
        if len(resp) == 0 and rule['showmiss']:
            satisfied = False
        for binding in resp:
            satisfied = False
            # Extract keys and values from query result to return with result
            simplebinding = constraintbinding.copy()
            for k in binding:
                if not isinstance(k,rdflib.BNode):
                    simplebinding[str(k)] = str(binding[k])
                    simplebinding['_count'] = len(resp)
                    # @@TODO remove this when rdflib bug resolved 
                    if str(k) in ['if', 'of'] and str(binding[k])[:5] not in ["file:","http:"]:
                        # Houston, we have a problem...
                        agraph = rometa.roannotations
                        log.warning( "--------------------" )
                        log.debug( "Graph: "+agraph.serialize(format="xml") )
                        log.warning( "Query: "+query )
                        log.warning( "Response bindings: "+repr(resp) )
                        log.warning( "--------------------" )
                        ### assert False, "Aborted"
            if exists:
                # existence query against forall results
                existsparams = (
                    { 'queryverb': "ASK"
                    , 'querypattern': exists
                    , 'queryorder':   ""
                    })
                query = querytemplate%existsparams
                log.debug("evalContentMatch RO test exists: \nquery: %s \nbinding: %s"%
                          (query, repr(binding)))
                satisfied = rometa.queryAnnotations(query,initBindings=binding)
            if template:
                # Construct URI for file from template
                # Uses code copied from http://code.google.com/p/uri-templates
                fileref = uritemplate.expand(template, simplebinding)
                fileuri = rometa.getComponentUri(fileref)
                # Test if URI is aggregated
                log.debug("evalContentMatch RO aggregates %s (%s)"%(fileref, str(fileuri)))
                satisfied = rometa.roManifestContains( (rometa.getRoUri(), ORE.aggregates, fileuri) )
            if islive:
                # Construct URI for file from template
                # Uses code copied from http://code.google.com/p/uri-templates
                fileref = uritemplate.expand(islive, simplebinding)
                fileuri = rometa.getComponentUri(fileref)
                # Test if URI is live (accessible)
                log.debug("evalContentMatch RO islive %s (%s)"%(fileref, str(fileuri)))
                satisfied = isLiveUri(fileuri)
            log.debug("evalContentMatch (forall) RO satisfied %s"%(satisfied))
            if not satisfied: break
    elif rule['exists']:
        queryparams = (
            { 'queryverb': "ASK"
            , 'querypattern': rule['exists']
            , 'queryorder':   ""
            })
        query = querytemplate%queryparams
        log.debug("- query %s"%(query))
        satisfied = rometa.queryAnnotations(query)
        log.debug("- satisfied %s"%(satisfied))
    else:
        raise ValueError("Unrecognized content match rule: %s"%repr(rule))
    return (satisfied,simplebinding)

def evalQueryTest(rometa, rule, constraintbinding):
    """
    rometa      ro_metadata for RO to test
    rule        requirement rule to evaluate
    constraintbinding
                value bindings generated by constraint matching:
                'targetro' and 'targetres', and maybe others

    Returns ....
    """
    log.debug("evalQueryTest: rule: \n----\n  %s, \n----\nconstraintbinding:\n  %s\n----"%(repr(rule), repr(constraintbinding)))
    querytemplate = (make_sparql_prefixes(rule['prefixes'])+
        """
        BASE <%(querybase)s>

        %(queryverb)s
        {
          %(querypattern)s
        } %(resultmod)s
        """)
    satisfied     = True
    simplebinding = constraintbinding.copy()
    if rule['query']:
        count_min  = rule['min']
        count_max  = rule['max']
        aggregates = rule['aggregates_t']
        islive     = rule['islive_t']
        exists     = rule['exists']
        assert (count_min or count_max or aggregates or islive or exists), (
            "minim:QueryTestRule requires "+
            "minim:min, minim:max, minim:aggregatesTemplate, minim:isLiveTemplate and/or minim:exists value")
        if aggregates:  aggregates = str(aggregates).strip()
        if islive:      islive   = str(islive).strip()
        queryparams = (
            { 'querybase':    str(rometa.getRoUri())
            , 'queryverb':    "SELECT * WHERE"
            , 'querypattern': rule['query']
            , 'resultmod':    rule['resultmod'] or ""
            })
        query = querytemplate%queryparams
        log.debug(" - QueryTest: "+query)
        resp  = rometa.queryAnnotations(query, initBindings=constraintbinding)
        log.debug(" - QueryTest resp: "+repr(resp))
        simplebinding['_count'] = len(resp)
        satisfied_count  = 0
        total_count      = len(resp)
        result_list      = []
        failure_message_template = rule['showfail'] or rule['show']
        for binding in resp:
            satisfied = True
            failmsg   = failure_message_template
            simplebinding = constraintbinding.copy()
            for k in binding:
                if not isinstance(k,rdflib.BNode):
                    simplebinding[str(k)]   = unicode(binding[k])
                    simplebinding['_count'] = len(resp)
            # Do the required test
            if aggregates:
                fileref   = uritemplate.expand(aggregates, simplebinding)
                fileuri   = rometa.getComponentUri(fileref)
                simplebinding.update({'_fileref': fileref, '_fileuri': fileuri})
                log.debug("evalQueryTest RO aggregates %s (%s)"%(fileref, str(fileuri)))
                satisfied = rometa.roManifestContains( (rometa.getRoUri(), ORE.aggregates, fileuri) )
                failmsg   = failmsg or "Aggregates %(_fileref)s"
            if islive:
                fileref   = uritemplate.expand(islive, simplebinding)
                fileuri   = rometa.getComponentUri(fileref)
                simplebinding.update({'_fileref': fileref, '_fileuri': fileuri})
                log.debug("evalQueryTest RO isLive %s (%s)"%(fileref, str(fileuri)))
                satisfied = isLiveUri(fileuri)
                failmsg   = failmsg or "Accessible %(_fileref)s"
            if exists:
                existsparams = (
                    { 'querybase':    str(rometa.getRoUri())
                    , 'queryverb':    "ASK"
                    , 'querypattern': exists
                    , 'resultmod':    ""
                    })
                query = querytemplate%existsparams
                simplebinding.update({'_pattern': exists, '_query': query})
                log.debug("evalContentMatch RO test exists: \nquery: %s \nbinding: %s"%
                          (query, repr(binding)))
                satisfied = rometa.queryAnnotations(query,initBindings=binding)
                failmsg   = failmsg or "Exists %(_fileref)s"
            # Test done, defines: satisfied, failmsg, simplebinding 
            log.debug("Satisfied: %s"%(repr(satisfied)))
            if satisfied:
                satisfied_count += 1
            result_list.append((satisfied, failmsg, simplebinding))
        # All responses tested
    else:
        raise ValueError("Query test rule has no query: %s"%repr(rule))
    # Sort out final response
    log.debug("evalQueryTest RO satisfied_count %d"%(satisfied_count))
    if count_min or count_max:
        satisfied = ( (not count_min or (satisfied_count >= count_min)) and
                      (not count_max or (satisfied_count <= count_max)) )
        binding = constraintbinding.copy()
        binding['_count'] = satisfied_count
        msg = (rule['showpass'] if satisfied else rule['showfail'])
        msh = msg or rule['show'] or "Cardinality requirement failed"
    elif total_count == 0:
        binding   = simplebinding
        satisfied = False if rule['showmiss'] else True
        msg       = rule['showmiss'] or rule['showpass'] or rule['show'] or "No matches"
    elif (satisfied_count < total_count):
        satisfied = False
        # Pick out first failure (for now):
        (msg, binding) = ((failmsg,binding) for (satisfied, failmsg, binding) in result_list if not satisfied).next()
    else:
        satisfied = True
        binding   = simplebinding     # last result tested
        msg       = rule['showpass']
    return (satisfied, binding, msg)

def format(eval_result, options, ostr):
    """
    Formats a completeness evaluation report, and writes it to the supplied stream.
    
    eval_result is the result of evaluation from ro_eval_completeness.evaluate
    options     a dictionary that provides options to control the formatting (see below)
    ostr        is a stream to which the formatted result is written

    options currently has just one field:
    options['detail'] = "summary", "must", "should", "may" or "full"
    """
    s_any     = ["full", "may", "should", "must", "summary"]
    s_must    = ["full", "may", "should", "must"]
    s_should  = ["full", "may", "should"]
    s_may     = ["full", "may"]
    s_full    = ["full"]
    def put(detail, line):
        if options['detail'] in detail:
            ostr.write(line)
            ostr.write("\n")
        return
    put(s_any, "Research Object %(rouri)s:"%eval_result)
    summary_text= ( "Fully complete"     if MINIM.fullySatisfies     in eval_result['summary'] else
                    "Nominally complete" if MINIM.nominallySatisfies in eval_result['summary'] else
                    "Minimally complete" if MINIM.minimallySatisfies in eval_result['summary'] else
                    "Incomplete")
    put(s_any, summary_text+" for %(purpose)s of resource %(target)s"%(eval_result))
    if eval_result['missingMust']:
        put(s_must, "Unsatisfied MUST requirements:")
        for m in eval_result['missingMust']:
            put(s_must, "  "+formatRule(False, *m))
    if eval_result['missingShould']:
        put(s_should, "Unsatisfied SHOULD requirements:")
        for m in eval_result['missingShould']:
            put(s_should, "  "+formatRule(False, *m))
    if eval_result['missingMay']:
        put(s_may, "Unsatisfied MAY requirements:")
        for m in eval_result['missingMay']:
            put(s_may, "  "+formatRule(False, *m))
    if eval_result['satisfied']:
        put(s_full, "Satisfied requirements:")
        for m in eval_result['satisfied']:
            put(s_full, "  "+formatRule(True, *m))
    put(s_full, "Research object URI:     %(rouri)s"%(eval_result))
    put(s_full, "Minimum information URI: %(minimuri)s"%(eval_result))
    return

def formatRule(satisfied, rule, bindings):
    """
    Format a rule for a missing/satisfied report
    """
    templateoverride = None
    # Pick up details from rule used
    if 'datarule' in rule:
        ruledict = rule['datarule']
        templatedefault = "Aggregates resource %(aggregates)s"
    elif 'softwarerule' in rule:
        ruledict = rule['softwarerule']
        templatedefault = "Environment '%(command)s' matches '%(response)s'"
    elif 'contentmatchrule' in rule:
        ruledict = rule['contentmatchrule']
        if ruledict['forall']:
            if bindings['_count'] == 0 and ruledict["showmiss"]:
                templateoverride = ruledict["showmiss"]
            if ruledict['exists']:
                templatedefault = "Match %(exists)s for each matching %(forall)s"
            elif ruledict['template']:
                templatedefault = "Aggregate %(template)s for each matching %(forall)s"
            elif ruledict['islive']:
                templatedefault = "Liveness of %(template)s for each matching %(forall)s"
            else:
                templatedefault = "Unknown test for each matching %(forall)s"
        elif ruledict['exists']:
            templatedefault = "Match for %(exists)s"
        else:
            templatedefault = "Unknown content match rule (no forall or exists)"
    elif 'querytestrule' in rule:
        ruledict = rule['querytestrule']
        templatedefault = "Query test rule %(query)s"
    else:
        ruledict = { 'rule': repr(rule), 'show': None, 'templateindex': None }
        templatedefault = "Unrecognized rule: %(rule)s"
    # Select and apply formatting template
    if satisfied:
        template = ruledict.get("showpass", None)
    else:
        template = ruledict.get("showfail", None)
    template = templateoverride or template or ruledict.get("show", None) or templatedefault
    bindings.update(ruledict)
    return template%bindings

def evalResultGraph(graph, evalresult):
    """
    This function combines the results from the evaluate function (above) to return
    a single RDF result graph that is the result of the checklist evaluation service, 
    and also is returned when RDF output is requested by 'ro evaluate checklist'.
    
    graph       is the minim graph used for the evaluation.
                The supplied graph is updated and returned by this function.
    evalresult  is the evaluation result returned by the evaluate function
    """
    graph.bind("rdf",     RDF.baseUri)
    graph.bind("rdfs",    RDFS.baseUri)
    graph.bind("dcterms", DCTERMS.baseUri)
    graph.bind("result",  RESULT.baseUri)
    graph.bind("minim",   MINIM.baseUri)
    rouri     = rdflib.URIRef(evalresult['rouri'])
    targeturi = rdflib.URIRef(resolveUri(evalresult['target'], evalresult['rouri']))
    graph.add( (rouri, DCTERMS.identifier,     rdflib.Literal(evalresult['roid']))         )
    graph.add( (rouri, RDFS.label,             rdflib.Literal(evalresult['title']))        )
    graph.add( (rouri, DCTERMS.title,          rdflib.Literal(evalresult['title']))        )
    graph.add( (rouri, DCTERMS.description,    rdflib.Literal(evalresult['description']))  )
    graph.add( (rouri, MINIM.testedConstraint, rdflib.URIRef(evalresult['constrainturi'])) )
    graph.add( (rouri, MINIM.testedPurpose,    rdflib.Literal(evalresult['purpose']))      )
    graph.add( (rouri, MINIM.testedTarget,     targeturi)                                  )
    graph.add( (rouri, MINIM.minimUri,         rdflib.URIRef(evalresult['minimuri']))      )
    graph.add( (rouri, MINIM.modelUri,         rdflib.URIRef(evalresult['modeluri']))      )
    graph.add( (targeturi, RDFS.label,         rdflib.Literal(evalresult['targetlabel'])) )
    for level in evalresult['summary']:
        log.info("RO %s, level %s, model %s"%(rouri,level,evalresult['modeluri']))
        graph.add( (targeturi, level, rdflib.URIRef(evalresult['modeluri'])) )
    # Add details for all items tested...
    def addRequirementsDetail(satisfied, results, satlevel):
        for (req, binding) in results:
            b = rdflib.BNode()
            msg = formatRule(satisfied, req, binding)
            graph.add( (rouri, satlevel, b) )
            graph.add( (b, MINIM.tryRequirement, req['uri']) )
            graph.add( (b, MINIM.tryMessage, rdflib.Literal(msg)) )
            for k in binding:
                b2 = rdflib.BNode()
                graph.add( (b,  RESULT.binding,  b2) )
                graph.add( (b2, RESULT.variable, rdflib.Literal(k)) )
                graph.add( (b2, RESULT.value,    rdflib.Literal(binding[k])) )
            if not graph.value(subject=req['uri'], predicate=MINIM.seq):
                graph.add( (req['uri'], MINIM.seq, rdflib.Literal(req['seq'])) )
    addRequirementsDetail(True,  evalresult['satisfied'], MINIM.satisfied)
    addRequirementsDetail(False, evalresult['missingMay'], MINIM.missingMay)
    addRequirementsDetail(False, evalresult['missingShould'], MINIM.missingShould)
    addRequirementsDetail(False, evalresult['missingMust'], MINIM.missingMust)
    return graph

# End.
