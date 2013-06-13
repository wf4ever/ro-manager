# ro_minim.py

"""
Research Object minimum information model access functions
"""

import re
import urllib
import urlparse
import logging

log = logging.getLogger(__name__)

import rdflib
import rdflib.namespace
from uritemplate import uritemplate

from rocommand import ro_manifest
from rocommand import ro_namespaces
from rocommand.ro_namespaces import RDF, RDFS

minimnsuri = rdflib.URIRef("http://purl.org/minim/minim#")
MINIM      = ro_namespaces.makeNamespace(minimnsuri,
            [ "Constraint", "Checklist"             # synonyms
            , "hasConstraint", "hasChecklist"       # synonyms
            , "hasPrefix"
            # Model and properties
            , "Model"
            , "hasMustRequirement", "hasShouldRequirement", "hasMayRequirement", "hasRequirement"
            # Requirement and properties
            , "Requirement"
            , "derives", "reports", "isDerivedBy"
            , "show", "showpass", "showfail", "showmiss", "seq"
            # Rules and properties
            , "RequirementRule"
            , "SoftwareEnvironmentRule", "DataRequirementRule", "ContentMatchRequirementRule"
            , "forTarget", "forTargetTemplate", "forPurpose", "toModel"
            , "aggregates"
            , "command", "response"
            , "forall", "orderby", "exists", "aggregatesTemplate", "isLiveTemplate"
            # Refactored rule and properties
            , "QueryTestRule", "graph", "query"
            , "Query"
            , "SparqlQuery", "sparql_query", "result_mod"
            , "QueryResultTest"
            , "CardinalityTest", "min", "max"   ### @@use min, max, all as qualifiers for other tests?
            , "RuleTest", "affirmRule"
            , "RuleNegationTest", "negateRule"  ### @@use max cardinality constraint instead?
            , "AggregationTest", "aggregatesTemplate"
            , "AccessibilityTest", "isLiveTemplate"
            , "ExistsTest", "exists"            ### @@this is structly redundant - drop it?
            # Result properties
            , "minimallySatisfies", "nominallySatisfies", "fullySatisfies"
            , "satisfied", "missingMay", "missingShould", "missingMust"
            , "testedConstraint", "testedPurpose", "testedTarget"
            , "minimUri", "modelUri"
            , "tryRequirement", "tryMessage"
            ])

resultnsuri = rdflib.URIRef("http://www.w3.org/2001/sw/DataAccess/tests/result-set#")
RESULT      = ro_namespaces.makeNamespace(resultnsuri,
            [ "binding", "variable", "value"
            ])

def getElementUri(minimbase, elemname):
    """
    Returns URI of element in Minim file
    
    minimbase   is the URI of the Minim file containing the required element
    elemname    is the relative URI of the element - commonly a fragment identifier
    """
    return rdflib.URIRef(urlparse.urljoin(str(minimbase), elemname))

def readMinimGraph(minimuri):
    """
    Read Minim file, return RDF Graph.
    """
    log.debug("minimuri %s"%(repr(minimuri)))
    minimformat   = "xml"
    if re.search("\.(ttl|n3)$", str(minimuri)): minimformat="n3"
    minimgraph = rdflib.Graph()
    minimgraph.parse(minimuri, format=minimformat)
    return minimgraph

def iter2(iter1, iter2):
    for item in iter1: yield item
    for item in iter2: yield item
    return

def getConstraints(minimgraph):
    constraint_or_checklist = iter2(
        minimgraph.subject_objects(predicate=MINIM.hasConstraint),
        minimgraph.subject_objects(predicate=MINIM.hasChecklist ) )
    for (target, constraint) in constraint_or_checklist:
        c = {'target': target, 'uri': constraint}
        c['target_t']   = minimgraph.value(subject=constraint, predicate=MINIM.forTargetTemplate)
        c['purpose']    = minimgraph.value(subject=constraint, predicate=MINIM.forPurpose)
        c['model']      = minimgraph.value(subject=constraint, predicate=MINIM.toModel)
        yield c
    return

def getConstraint(minimgraph, rouri, target_ref, purpose_regex_string):
    """
    Find constraint matching supplied RO, target and purpose regex
    
    Constraint is returned with:
    targetro_actual  -> URI of resource
    targetres_actual -> URI of target if supplied, else subject of minium:hasConstraint
    """
    def mkstr(u):
        return u and str(u)
    log.debug("getConstraint: rouri %s, target_ref %s"%(rouri, target_ref))
    target       = target_ref and ro_manifest.getComponentUri(rouri, target_ref)
    log.debug("               target_uri %s"%(target))
    purpose      = purpose_regex_string and re.compile(purpose_regex_string)
    templatedict = {'targetro': urllib.unquote(str(rouri))}
    if target:
        # Allow use of {+targetres} in checklist target template:
        templatedict['targetres'] = urllib.unquote(str(target))
    for c in getConstraints(minimgraph):
        log.debug("- test: target %s purpose %s"%(c['target'],c['purpose']))
        log.debug("- purpose %s, c['purpose'] %s"%(purpose_regex_string, c['purpose']))
        if not purpose or purpose.match(c['purpose']):
            c['targetro_actual']   = rouri
            c['targetres_actual']  = target or c['target']
            if not target:
                # No target specified in request, match any (first) constraint
                return c
            if c['target'] == target:
                # Match explicit target specification (subject of minim:hasConstraint)
                return c
            log.debug("- target: %s, c['target_t']: %s"%(target, repr(c['target_t'])))
            if c['target_t'] and c['target_t'].value == "*":
                # Special case: wilcard ("*") template matches any target
                return c
            if target and c['target_t']:
                log.debug("- expand %s"%(uritemplate.expand(c['target_t'], templatedict)))
                if str(target) == uritemplate.expand(c['target_t'], templatedict):
                    # Target matches expanded template from constraint description
                    return c
    return None

def getModels(minimgraph, modeluri=None):
    for (model, p, o) in minimgraph.triples( (modeluri, RDF.type, MINIM.Model) ):
        m = {'uri': model}
        m['label']   = minimgraph.value(subject=model, predicate=RDFS.label)
        m['comment'] = minimgraph.value(subject=model, predicate=RDFS.comment)
        yield m
    return

def getModel(minimgraph, modeluri):
    for m in getModels(minimgraph, modeluri=modeluri):
        return m
    return None

def getPrefixes(minimgraph):
    for (uri, p, prefix) in minimgraph.triples((None, MINIM.hasPrefix, None)):
        yield (str(prefix), str(uri))

def litval(l):
    return l.value if l else None

def getRequirements(minimgraph, modeluri):
    def matchRequirement((s, p, o), reqp, reqval):
        req = None
        if p == reqp:
            req = (
                { 'uri':    o
                , 'model':  s
                , 'level':  reqval
                , 'label':  minimgraph.value(subject=o, predicate=RDFS.label)
                })
            ruleuri = minimgraph.value(subject=o, predicate=MINIM.isDerivedBy)
            assert ruleuri, "Requirement %s has no minim:isDerivedBy rule"%(str(o))
            rule = (
                { 'derives':    minimgraph.value(subject=ruleuri, predicate=MINIM.derives) 
                , 'show':       minimgraph.value(subject=ruleuri, predicate=MINIM.show) 
                , 'showpass':   minimgraph.value(subject=ruleuri, predicate=MINIM.showpass)
                , 'showfail':   minimgraph.value(subject=ruleuri, predicate=MINIM.showfail)
                , 'showmiss':   minimgraph.value(subject=ruleuri, predicate=MINIM.showmiss)
                })
            # Create field used for sorting checklist items
            req['seq'] = str( minimgraph.value(subject=s, predicate=MINIM.seq) or
                              rule['show'] or
                              rule['showpass'] )
            ruletype = minimgraph.value(subject=ruleuri, predicate=RDF.type)
            if ruletype == MINIM.DataRequirementRule:
                rule['aggregates']  = minimgraph.value(subject=ruleuri, predicate=MINIM.aggregates)
                req['datarule'] = rule
            elif ruletype == MINIM.SoftwareEnvironmentRule:
                rule['command']  = minimgraph.value(subject=ruleuri, predicate=MINIM.command)
                rule['response'] = minimgraph.value(subject=ruleuri, predicate=MINIM.response)
                req['softwarerule'] = rule
            elif ruletype == MINIM.ContentMatchRequirementRule:
                rule['forall']   = minimgraph.value(subject=ruleuri, predicate=MINIM.forall)
                rule['orderby']  = minimgraph.value(subject=ruleuri, predicate=MINIM.orderby)
                rule['exists']   = minimgraph.value(subject=ruleuri, predicate=MINIM.exists)
                rule['template'] = minimgraph.value(subject=ruleuri, predicate=MINIM.aggregatesTemplate)
                rule['islive']   = minimgraph.value(subject=ruleuri, predicate=MINIM.isLiveTemplate)
                req['contentmatchrule'] = rule
            elif ruletype == MINIM.QueryTestRule:
                query = minimgraph.value(subject=ruleuri, predicate=MINIM.query)
                assert query, "QueryTestRule for requirement %s has no query"%(o)
                rule['prefixes']     = list(getPrefixes(minimgraph))
                rule['query']        = minimgraph.value(subject=query, predicate=MINIM.sparql_query)
                rule['resultmod']    = minimgraph.value(subject=query, predicate=MINIM.result_mod)
                rule['min']          = litval(minimgraph.value(subject=ruleuri, predicate=MINIM.min))
                rule['max']          = litval(minimgraph.value(subject=ruleuri, predicate=MINIM.max))
                rule['aggregates_t'] = minimgraph.value(subject=ruleuri, predicate=MINIM.aggregatesTemplate)
                rule['islive_t']     = minimgraph.value(subject=ruleuri, predicate=MINIM.isLiveTemplate)
                exists = minimgraph.value(subject=ruleuri, predicate=MINIM.exists)
                if exists:
                    rule['exists']        = minimgraph.value(subject=exists, predicate=MINIM.sparql_query)
                else:
                    rule['exists'] = None
                req['querytestrule'] = rule
            else:
                assert False, "Unrecognized rule type %s for requirement %s"%(str(ruletype), str(o))
        return req
    for stmt in minimgraph.triples( (modeluri, None, None) ):
        pred_level_list = (
            [ (MINIM.hasMustRequirement, "MUST")
            , (MINIM.hasShouldRequirement, "SHOULD")
            , (MINIM.hasMayRequirement, "MAY")
            ])
        for (pred, level) in pred_level_list:
            r = matchRequirement(stmt, pred, level)
            if r:
                yield r
                break
    return

# End.
