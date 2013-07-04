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

    def __init__(self):
        self.minimgr = rdflib.Graph()
        return

    def prefix(self, prefix, nsuri):
        self.minimgr.bind(prefix, rdflib.Namespace(nsuri))
        return

    def checklist(self, purpose=None, model=None, target="{+targetro}"):
        cls = rdflib.URIRef("#ChecklistConstraints")
        cln = rdflib.BNode()
        clt = rdflib.Literal(target)
        clp = rdflib.Literal(purpose)
        clm = rdflib.Literal(model)
        self.minimgr.add( (cls, MINIM.hasChecklist, cln) )
        self.minimgr.add( (cln, RDF.type,                MINIM.Checklist) )
        self.minimgr.add( (cln, MINIM.forTargetTemplate, clt) )
        self.minimgr.add( (cln, MINIM.forPurpose,        clp) )
        self.minimgr.add( (cln, MINIM.toModel,           clm) )
        return cln

    def model(self, modelid, itemlist):
        model = rdflib.URIRef(modelid)
        self.minimgr.add( (model, RDF.type, MINIM.Model) )
        for (level, item) in itemlist:
            self.minimgr.add( (model, level, item) )
        return model

    def item(self, seq=None, level="MUST", reqid=None):
        item = rdflib.URIRef(reqid)
        if seq:
            self.minimgr.add( (item, MINIM.seq, rdflib.Literal(seq)) )
        levelmap = (
            { "MUST":   MINIM.hasMustRequirement
            , "SHOULD": MINIM.hasShouldRequirement
            , "MAY":    MINIM.hasMayRequirement
            })
        return (levelmap[level], item)

    def rule(self,
             reqid, ForEach=None, Exists=None, Min=0, Max=None, 
             Aggregates=None, IsLive=None, 
             Command=None, Response=None,
             Show=None, Pass="None", Fail="None", NoMatch="None"):
        item = rdflib.URIRef(reqid)
        rule = rdflib.BNode()
        self.minimgr.add( (item, RDF.type, MINIM.Requirement) )
        self.minimgr.add( (item, MINIM.isDerivedBy, rule) )
        if ForEach:
            ruletype = MINIM.ContentMatchRequirementRule
            self.minimgr.add( (rule, MINIM.forall, rdflib.Literal(ForEach)) )
            if Exists:
                self.minimgr.add( (rule, MINIM.exists, rdflib.Literal(Exists)) )
            if Min:
                self.minimgr.add( (rule, MINIM.exists, rdflib.Literal(Min)) )
            if Max:
                self.minimgr.add( (rule, MINIM.exists, rdflib.Literal(Max)) )
            if Aggregates:
                self.minimgr.add( (rule, MINIM.aggregatesTemplate, rdflib.Literal(Aggregates)) )
            if IsLive:
                self.minimgr.add( (rule, MINIM.isLiveTemplate, rdflib.Literal(IsLive)) )
        elif Exists:
            ruletype = MINIM.ContentMatchRequirementRule
            self.minimgr.add( (rule, MINIM.exists, rdflib.Literal(Exists)) )
        elif Command:
            ruletype = MINIM.SoftwareEnvironmentRule
            self.minimgr.add( (rule, MINIM.command, rdflib.Literal(Command)) )
            self.minimgr.add( (rule, MINIM.response, rdflib.Literal(Response)) )
        else:
            raise ValueError("Unrecognized requirement rule pattern")
        self.minimgr.add( (rule, RDF.type, ruletype) )
        if Show:
            self.minimgr.add( (rule, MINIM.show,     rdflib.Literal(Show)) )
        if Pass:
            self.minimgr.add( (rule, MINIM.showpass, rdflib.Literal(Pass)) )
        if Fail:
            self.minimgr.add( (rule, MINIM.showfail, rdflib.Literal(Fail)) )
        if NoMatch:
            self.minimgr.add( (rule, MINIM.showmiss, rdflib.Literal(NoMatch)) )
        self.minimgr.add( (rule, MINIM.derives, item) )
        return rule

    def serialize(self, outstr, format="turtle"):
        self.minimgr.serialize(destination=outstr, format=format)
        return

    def graph(self):
        return self.minimgr

# End.
