#!/usr/bin/env python

"""
Module to define matching template for checklist spreadsheet
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2013, University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

from gridmatch import (
    GridMatchReport, GridMatchError, GridMatch,
    text, anyval, regexval, refval, intval, save, value, error, trace
    )

checklist_start = value("matchtemplate", "checklist")

prefix = text("") + regexval(r"\w+", "prefix") + refval("uri")

prefixes = (text("Prefixes:").skipdownto()
    // text("Prefixes:")
    // prefix.repeatdown("prefixes", min=1, dkey="prefix", dval="uri")
    )

checklist = text("") + regexval(r".+", "target_urit") + anyval("purpose") + refval("model")

checklists = (text("Checklists:").skipdownto() 
    // text("Checklists:") 
    // checklist.repeatdown("checklists", min=1)
    )

itemlevel = save("level") + (text("MUST") | text("SHOULD") | text("MAY"))

checkitem = anyval("seq") + itemlevel + refval("reqid")

model = ( text("Model:").skipdownto() 
    // (text("Model:") + refval("modelid"))
    // text("Items:")
    // checkitem.repeatdown("items")
    )

models = model.repeatdown("models", min=1)

matchforeach = ( (text("ForEach:") + regexval(".+", "foreach"))
    // (text("ResultMod:")  + regexval(".+", "result_mod")).optional()
    // (text("Exists:")     + regexval(".+", "exists")).optional()
    // (text("Aggregates:") + regexval(".+", "aggregates")).optional()
    // (text("IsLive:")     + regexval(".+", "islive")).optional()
    // (text("Min:")        + intval("min")).optional()
    // (text("Max:")        + intval("max")).optional()
    )

matchexists = text("Exists:") + regexval(".+", "exists")

matchsoftware = ( (text("Command:") + anyval("command"))
    // (text("Response:") + anyval("response"))
    )

rulebody = ( matchforeach
    | matchexists 
    | matchsoftware 
    | error("No rule body found")
    )

collectvarlist = ( ( regexval("\?\w+", "collectvar") + text("as:") + regexval("\?\w+", "collectlist") )
                 | trace("collectvarlist not matched")
                 )

collectall = ( text("Collect:") + collectvarlist )

collectpass = ( text("CollectPass:") + collectvarlist )

collectfail = ( text("CollectFail:") + collectvarlist )

collectvars = ( collectall.repeatdown("collectall")
    // collectpass.repeatdown("collectpass")
    // collectfail.repeatdown("collectfail")
    )

rulediag = ( (text("Pass:") + anyval("pass"))
    // (text("Fail:") + anyval("fail"))
    // (text("None:") + anyval("miss")).optional()
    )

requirement = ( text("Rule:").skipdownto() 
    // (text("Rule:") + refval("reqid"))
    // (text("") + (rulebody // collectvars // rulediag))
    )

requirements = requirement.repeatdown("requirements", min=1)

checklist_end = text("End:").skipdownto() // text("End:")

checklist = ( checklist_start
    // prefixes
    // checklists
    // models
    // requirements
    // checklist_end
    )


# Example data matched by the above:
#
# Prefixes:,Prefix,URI,,,@@NOTE: there is a shortcoming in the present Minim model and implementation that means there is no way to add new prefixes to those predefined in the minim evaluation code.  Noted as technical debt fix.,
# ,rdf,http://www.w3.org/1999/02/22-rdf-syntax-ns#,,,,
# ,rdfs,http://www.w3.org/2000/01/rdf-schema#,,,,
# ,owl,http://www.w3.org/2002/07/owl#,,,,
# ,xsd,http://www.w3.org/2001/XMLSchema#,,,,
# ,xml,http://www.w3.org/XML/1998/namespace,,,,
# ,rdfg,http://www.w3.org/2004/03/trix/rdfg-1/,,,,
# ,ore,http://www.openarchives.org/ore/terms/,,,,
# ,ao,http://purl.org/ao/,,,,
# ,dcterms,http://purl.org/dc/terms/,,,,
# ,foaf,http://xmlns.com/foaf/0.1/,,,,
# ,ro,http://purl.org/wf4ever/ro#,,,,
# ,wfprov,http://purl.org/wf4ever/wfprov#,,,,
# ,wfdesc,http://purl.org/wf4ever/wfdesc#,,,,
# ,wf4ever,http://purl.org/wf4ever/wf4ever#,,,,
# ,minim,http://purl.org/minim/minim#,,,,

# Checklists:,Target,Purpose,Model,,Description,
# ,{+targetro},ready-to-release,#experiment_complete_model,,Checklist to be satisfied if the target RO is to be considered a complete and fully-described workflow experiment.,
# ,{+targetro},wf-accessible,#wf_accessible_model,,Checklist to test workflow accessible item in isolation,
# ,,,,,,
# Model:,#experiment_complete_model,,,,This model defines information that must be satisfied by the target RO for the target RO to be considered a complete and fully-described workflow experiment.,
# Items:,Level,Rule,,,,
# 010,SHOULD,#RO_has_hypothesys,,,RO should contain a resource describing the hypothesis the experiment is intended to test,
# 020,SHOULD,#RO_has_sketch,,,RO should contain a resource that is a high level sketch of the workflow that is used to test the hypothesys,
# 030,MUST,#WF_accessible,,,The RO must contain an accessible workflow definition,
# 040,MUST,#WF_services_accessible,,,All services used by the workflow must be live,
# 050,MUST,#RO_has_inputdata,,,The RO must specify input data that is used by the workflow,
# 060,SHOULD,#RO_has_conclusion,,,The RO should contain a resource that describes outcomes and conclusions obtained by running the workflow. ,

# Model:,#wf_accessible_model,,,,Model to test workflow accessible item in isolation,
# Items:,Level,Rule,,,,
# 030,MUST,#WF_accessible,,,The RO must contain an accessible workflow definition

# Define rules to test individual requirements,,,,,

# Rule:,#RO_has_hypothesys,,,,
# ,Exists:,?hypothesis rdf:type roterms:Hypothesis,,,
# ,Pass:,Experiment hypothesis is present,,,
# ,Fail:,Experiment hypothesis is not present,,,

# Rule:,#RO_has_sketch,,,,
# ,Exists:,?sketch rdf:type roterms:Sketch,,,
# ,Pass:,Workflow design sketch is present,,,
# ,Fail:,Workflow design sketch is not present,,,

# Rule:,#WF_accessible,,,,
# ,ForEach:,"?wf rdf:type wfdesc:Workflow ;
#   rdfs:label ?wflab ;
#   wfdesc:hasWorkflowDefinition ?wfdef",,,
# ,IsLive:,{+wfdef},,,
# ,Pass:,All workflow definitions are accessible,,,
# ,Fail:,The definition for workflow <i>%(wflab)s</i> is not accessible,,,
# ,None:,No workflow definitions are present,,,

# Rule:,#WF_services_accessible,,,,
# ,ForEach:,"?pr rdf:type wfdesc:Process ;
#   rdfs:label ?prlab .
#     { ?pr wf4ever:serviceURI ?pruri }
#   UNION
#     { ?pr wf4ever:wsdlURI ?pruri }",,,
# ,IsLive:,{+pruri},,,
# ,Pass:,All web services used by workflows are accessible,,,
# ,Fail:,"One or more web services used by a workflow are inaccessible, including <a href=""%(pruri)s""><i>%(prlab)s</i></a>",,,
# ,None:,No web services are referenced by any workflow,,,

# Rule:,#RO_has_inputdata,,,,
# ,Exists:,?wfbundle roterms:inputSelected ?inputdata,,,
# ,Pass:,Input data is present,,,
# ,Fail:,Input data is not present,,,

# Rule:,#RO_has_conclusion,,,,
# ,Exists:,?conclusion rdf:type roterms:Conclusions,,,
# ,Pass:,Experiment conclusions are present,,,
# ,Fail:,Experiment conclusions are not present,,,

# End:,,,,,

# End.
