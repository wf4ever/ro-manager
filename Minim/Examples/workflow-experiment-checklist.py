# Checklist definition experiment as Python-embedded DSL
# To create a Minimn RDF file, use the following command:
#
#   python workflow-experiment-checklist.py
#
# Assumes RO-Manager is installed in the current Python environment.

import Minim_begin, Minim_end, Prefix, Checklist, Model, Item, Rule from iaeval.checklist

Minim_begin()

Prefix("rdf",       "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
Prefix("rdfs",      "http://www.w3.org/2000/01/rdf-schema#")
Prefix("owl",       "http://www.w3.org/2002/07/owl#")
Prefix("xsd",       "http://www.w3.org/2001/XMLSchema#")
Prefix("xml",       "http://www.w3.org/XML/1998/namespace")
Prefix("rdfg",      "http://www.w3.org/2004/03/trix/rdfg-1/")
Prefix("ore",       "http://www.openarchives.org/ore/terms/")
Prefix("ao",        "http://purl.org/ao/")
Prefix("dcterms",   "http://purl.org/dc/terms/")
Prefix("foaf",      "http://xmlns.com/foaf/0.1/")
Prefix("ro",        "http://purl.org/wf4ever/ro#")
Prefix("wfprov",    "http://purl.org/wf4ever/wfprov#")
Prefix("wfdesc",    "http://purl.org/wf4ever/wfdesc#")
Prefix("wf4ever",   "http://purl.org/wf4ever/wf4ever#")
Prefix("minim",     "http://purl.org/minim/minim#")

Checklist(purpose="ready-to-release", model="experiment_complete_model", target="{+targetro}")
Checklist(purpose="wf-accessible",    model="wf_accessible_model",       target="{+targetro}")

Model("experiment_complete_model",
    Item(seq="010", SHOULD_Requirement="RO_has_hypothesys"),
    Item(seq="020", SHOULD_Requirement="RO_has_sketch"),
    Item(seq="030", MUST_Requirement="WF_accessible"),
    Item(seq="040", MUST_Requirement="WF_services_accessible"),
    Item(seq="050", MUST_Requirement="RO_has_inputdata"),
    Item(seq="060", SHOULD_Requirement="RO_has_conclusion"),
    )

Model("experiment_complete_model",
    Item(seq="030", MUST_Requirement="WF_accessible"),
    )

# Define rules to test individual requirements                    

Rule("RO_has_hypothesys",
     Exists="?hypothesis rdf:type roterms:Hypothesis"
     Pass="Experiment hypothesis is present",
     Fail="Experiment hypothesis is not present",
    )

Rule("RO_has_sketch",
     Exists="?sketch rdf:type roterms:Sketch"
     Pass="Workflow design sketch is present",
     Fail="Workflow design sketch is not present",
    )

Rule("WF_accessible",
     ForEach="?wf rdf:type wfdesc:Workflow ; rdfs:label ?wflab ; wfdesc:hasWorkflowDefinition ?wfdef"
     IsLive="{+wfdef},"
     NoMatch="No workflow definitions are present",
     Pass="All workflow definitions are accessible",
     Fail="The definition for workflow <i>%(wflab)s</i> is not accessible",
    )

Rule("WF_services_accessible",
     ForEach="""?pr rdf:type wfdesc:Process ; rdfs:label ?prlab . 
                  { ?pr wf4ever:serviceURI ?pruri }
                UNION 
                  { ?pr wf4ever:wsdlURI ?pruri }
             """,
     IsLive="{+pruri},"
     NoMatch="No web services are referenced by any workflow",
     Pass="All web services used by workflows are accessible",
     Fail="One or more web services used by a workflow are inaccessible, including <a href="%(pruri)s"><i>%(prlab)s</i></a>",
    )

Rule("RO_has_inputdata",
     Exists="?wfbundle roterms:inputSelected ?inputdata",
     Pass="Input data is present",
     Fail="Input data is not present",
    )

Rule("RO_has_conclusion",
     Exists="?conclusion rdf:type roterms:Conclusions",
     Pass="Experiment conclusions are present",
     Fail="Experiment conclusions are not present",
    )

Minim_end()
