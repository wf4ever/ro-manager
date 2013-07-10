# Minim_graph.py

"""
Module to create RDF Minim graph throughn simple set of API calls
"""

import rdflib

from rocommand.ro_namespaces import RDF

from iaeval.ro_minim import MINIM

class Minim_graph(object):
    """
    Class to create abstraction for constructing a Minim graph.

    The actual format of the resulting graph is implementation-dependent.
    This implementation builds an RDG graph, and serializes it in one of 
    a number of formats.  The default format is Turtle/N3.
    """

    def __init__(self, base=None):
        self._base    = base
        self._minimgr = rdflib.Graph()
        return

    def prefix(self, prefix, nsuri):
        self._minimgr.bind(prefix, rdflib.Namespace(nsuri))
        return

    def checklist(self, purpose=None, model=None, target="{+targetro}"):
        cls = rdflib.URIRef("#ChecklistConstraints", base=self._base)
        cln = rdflib.BNode()
        clt = rdflib.Literal(target)
        clp = rdflib.Literal(purpose)
        clm = rdflib.URIRef(model, base=self._base)
        self._minimgr.add( (cls, MINIM.hasChecklist, cln) )
        self._minimgr.add( (cln, RDF.type,                MINIM.Checklist) )
        self._minimgr.add( (cln, MINIM.forTargetTemplate, clt) )
        self._minimgr.add( (cln, MINIM.forPurpose,        clp) )
        self._minimgr.add( (cln, MINIM.toModel,           clm) )
        return cln

    def model(self, modelid, itemlist):
        model = rdflib.URIRef(modelid, base=self._base)
        self._minimgr.add( (model, RDF.type, MINIM.Model) )
        for (level, item) in itemlist:
            self._minimgr.add( (model, level, item) )
        return model

    def item(self, seq=None, level="MUST", ruleid=None):
        item = rdflib.BNode()
        rule = rdflib.URIRef(ruleid, base=self._base)
        self._minimgr.add( (item, RDF.type, MINIM.Requirement) )
        self._minimgr.add( (item, MINIM.isDerivedBy, rule) )
        if seq:
            self._minimgr.add( (item, MINIM.seq, rdflib.Literal(seq)) )
        levelmap = (
            { "MUST":   MINIM.hasMustRequirement
            , "SHOULD": MINIM.hasShouldRequirement
            , "MAY":    MINIM.hasMayRequirement
            })
        return (levelmap[level], item)

    def rule(self,
             ruleid, ForEach=None, ResultMod=None, Exists=None, Min=0, Max=None, 
             Aggregates=None, IsLive=None, 
             Command=None, Response=None,
             Show=None, Pass="None", Fail="None", NoMatch="None"):
        rule = rdflib.URIRef(ruleid, base=self._base)
        if ForEach:
            ruletype  = MINIM.QueryTestRule
            querynode = rdflib.BNode()
            self._minimgr.add( (rule, MINIM.query, querynode) )
            self._minimgr.add( (querynode, MINIM.sparql_query, rdflib.Literal(ForEach)) )
            if ResultMod:
                self._minimgr.add( (querynode, MINIM.result_mod, rdflib.Literal(ResultMod)) )
            if Exists:
                existsnode = rdflib.BNode()
                self._minimgr.add( (rule, MINIM.exists, existsnode) )
                self._minimgr.add( (existsnode, MINIM.sparql_query, rdflib.Literal(Exists)) )
            if Min:
                self._minimgr.add( (rule, MINIM.min, rdflib.Literal(Min)) )
            if Max:
                self._minimgr.add( (rule, MINIM.max, rdflib.Literal(Max)) )
            if Aggregates:
                self._minimgr.add( (rule, MINIM.aggregatesTemplate, rdflib.Literal(Aggregates)) )
            if IsLive:
                self._minimgr.add( (rule, MINIM.isLiveTemplate, rdflib.Literal(IsLive)) )
        elif Exists:
            ruletype = MINIM.QueryTestRule
            existsnode = rdflib.BNode()
            self._minimgr.add( (rule, MINIM.exists, existsnode) )
            self._minimgr.add( (existsnode, MINIM.sparql_query, rdflib.Literal(Exists)) )
        elif Command:
            ruletype = MINIM.SoftwareEnvironmentRule
            self._minimgr.add( (rule, MINIM.command, rdflib.Literal(Command)) )
            self._minimgr.add( (rule, MINIM.response, rdflib.Literal(Response)) )
        else:
            raise ValueError("Unrecognized requirement rule pattern")
        self._minimgr.add( (rule, RDF.type, ruletype) )
        if Show:
            self._minimgr.add( (rule, MINIM.show,     rdflib.Literal(Show)) )
        if Pass:
            self._minimgr.add( (rule, MINIM.showpass, rdflib.Literal(Pass)) )
        if Fail:
            self._minimgr.add( (rule, MINIM.showfail, rdflib.Literal(Fail)) )
        if NoMatch:
            self._minimgr.add( (rule, MINIM.showmiss, rdflib.Literal(NoMatch)) )
        return rule

    def serialize(self, outstr, format="turtle"):
        self._minimgr.serialize(destination=outstr, format=format)
        return

    def graph(self):
        return self._minimgr

# End.
