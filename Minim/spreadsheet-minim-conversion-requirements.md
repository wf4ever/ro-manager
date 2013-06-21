# Requirements on spreadsheet-to-checklist conversion tool

## 1. Generate templated RDF from the content of a group of cells.

Example 1:

     "{+targetro}", "ready-to-release", "experiment_complete_model"

to generate:

    _:checklists minim:hasChecklist
        [ a minim:Checklist ;
          minim:forTargetTemplate "{+targetro}" ;
          minim:forPurpose "ready-to-release" ;
          minim:toModel <#experiment_complete_model>
        ] .


## 2. Generate RDF with repeated references to a previous value

Example 2 (note label fields can be ignored if the cells themselves are suitably marked up):

    "Model:", "experiment_complete_model"
    "Items:", "Rule"
    "010",    "RO_has_hypothesys"
    "020",    "RO_has_sketch"
    (etc. - row structure repeated an arbitrary number of times)

to generate:

    <#experiment_complete_model> minim:hasMustRequirement  <#RO_has_hypothesys> .
    <#WF_accessible> minim:seq "010" .
    <#experiment_complete_model> minim:hasMustRequirement  <#RO_has_sketch> .
    <#WF_accessible> minim:seq "020" .
    (etc.)


## 3. Generate RDF with sub-property selection from ontology

Example 3:

    "Model:", "experiment_complete_model"
    "Items:", "Level",  "Rule"
    "010",    "MUST",   "RO_has_hypothesis"
    "020",    "SHOULD", "RO_has_sketch"
    (etc.)

to generate:

    <#experiment_complete_model> minim:hasMustRequirement  <#RO_has_hypothesis> .
    <#RO_has_hypothesis> minim:seq "010" .
    <#experiment_complete_model> minim:hasShouldRequirement  <#RO_has_sketch> .
    <#RO_has_sketch> minim:seq "020" .
    (etc.)

where minim:hasMustRequirement and minim:hasShouldRequirement are both sub properties of minim:hasRequirement.


## 4. Generation of different RDF from different cell structures

Example 4a:

    "Rule:", "RO_has_hypothesis"
           , "Exists:",   "?hypothesis rdf:type roterms:Hypothesis"
           , "Pass:",     "Experiment hypothesis is present"
           , "Fail:",     "Experiment hypothesis is not present"

to generate:

    <#RO_has_hypothesis> a minim:Requirement ;
      minim:isDerivedBy
        [ a minim:ContentMatchRequirementRule ;
          minim:exists   "?hypothesis rdf:type roterms:Hypothesis" ;
          minim:showpass "Experiment hypothesis is present" ;
          minim:showfail "Experiment hypothesis is not present" ;
        ] .

and

Example 4b:

    "Rule:", "WF_accessible"
           , "ForEach:",  "?wf rdf:type wfdesc:Workflow ; rdfs:label ?wflab ; wfdesc:hasWorkflowDefinition ?wfdef"
           , "IsLive:",   "{+wfdef}"
           , "Pass:",     "All workflow definitions are accessible"
           , "Fail:",     "The definition for workflow <i>%(wflab)s</i> is not accessible"
           , "None:",     "No workflow definitions are present"

to generate:

    <#WF_accessible> a minim:Requirement ;
      minim:isDerivedBy
        [ a minim:ContentMatchRequirementRule ;
          minim:forall "?wf rdf:type wfdesc:Workflow ; rdfs:label ?wflab ; wfdesc:hasWorkflowDefinition ?wfdef" ;
          minim:isLiveTemplate "{+wfdef}" ;
          minim:showpass "All workflow definitions are accessible" ;
          minim:showfail "The definition for workflow &lt;i&gt;%(wflab)s &lt;/i&gt; is not accessible" ;
          minim:showmiss "No workflow definitions are present" ;
        ] .


## 5. Handle optional values in a structure

(Really, just a special case of 4?)


## 6. XML escaping of characters in string values

(See example 4b)


