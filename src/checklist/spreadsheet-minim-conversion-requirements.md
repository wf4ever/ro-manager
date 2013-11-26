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


# Evaluations

See also: [http://answers.semanticweb.com/questions/2476/popular-tools-to-migrate-data-from-excel-ss-to-rdf]()

## Rightfield

[http://www.sysmo-db.org/rightfield]()

At first appearance, Rightfield seems to be limited to associating single cells with Ontology subclasses or individuals of a specified class, and contraining the cell contents accordingly.  There's also some mention of generating an RDF statement for sucvh a cell using a specified property, but I haven't been able to find out how that works.  As such, I don't see it handling any of the requirements listed here.  A query to the Rightfield support group confirms that what I'm trying to do is not within Rightfield's design remit.

## Ontomaton

[http://isatools.wordpress.com/2012/07/13/introducing-ontomaton-ontology-search-tagging-for-google-spreadsheets/]()

As far as I can tell, this tool is lmited to locating and resticting free text cells to contain terms from an ontology.  I don't see anything about generating RDF from the resulting spreadsheet.

I see nothing to indicate that this tool will begin to address the requirements of spreadsheet-to-checklist conversion.

## XLWrap

[http://xlwrap.sourceforge.net]()

This tool seems to have the kind iof transfiormation capabilities needed, but they seem to be based on specified cell tranghes.
I see no way to apply trasformations based on matches found in the content of the spreadsheet 
(e.g. cells containing "Model:", "Rule:", etc. in the above examples).

## OwlPopulous

[http://code.google.com/p/owlpopulous/]()

[http://e-lico.eu/populous.html]()

This tool appears to have some of the required mapping caoabiulities, 
but seems to be intebnded for generaiting OWL ontologies rather than generic RDF.
Documentation is provided only as a video of the tool in use, which isn't very helpful.

## RDF123

[http://rdf123.umbc.edu]()

[http://ebiquity.umbc.edu/_file_directory_/papers/370.pdf]()

This tool comes close to what is needed to map the checklist description foprmat to RDF, but is very row-oriented.  As such, it does not appear to be able to match multi-row structures (as exemplified for requirements 2 and 4 above) and generate RDF accordingly.

## Anzo for Excel

[http://www.cambridgesemantics.com/products/anzo-express]()

Commercial software - not evaluated.  (They don't even publish pricing, so it's bound to be sky-high)

## csv2rdf

[https://github.com/timrdf/csv2rdf4lod-automation/wiki]()

Can't figure out what it does.

## Tarql

[https://github.com/cygri/tarql]()

This is promising as it makes the full expressive power of SPARQL available for converting tabular data.  But the CSV input is treated as a table of bindings, so we're stuck with the view of spreadsheet data as independent rows.

## OpenRefine

[http://openrefine.org]()

A veritable swiss-army-knife of a tool, that seems to be aimed primarily at cleaning of tabular data.  It does seem to support some flexible pattern-match-driven data transformation capabilities.  As with other tools for processing tabular data, it is very focused on the row/column structure, and I could find no facility for matching patterns that extend over multiple rows.  It's possible that such features could be added, but that would involve a significant learning curve for understanding how to extend the system.

## TabLinker

https://github.com/Data2Semantics/TabLinker

(Added 2013-10-22. Evaluation TBD)

## Others

I glanced briefly at a number of other spreadsheet/tabular data conversion tools, and as far as I could tell they were (maybe unsurporisingly) all very much focused on treating each row as an independent record to be converted.  The designed format for checklist-in-spreadsheets captures a structure that is somewhat deeper than tabular data, and as such uses multiple rows to encode a information about a common entity, such as a rule.

See also:

* [http://www.python-excel.org]()


# Tentative design for a converter

(@@rough notes only)

To meet the requirements outlined above, my tenative design for a converter would use a number of template "queries".  Each template would be a pattern that matches a rectangular portion of a spreadsheet, and the resulting RDF would be generated using an associated CONSTRUCT-like pattern for each match.  This would allow values to be picked out from arbitrary regions of a spreadsheet.  The intent is to make extensive use of explicit labels in the spreadsheet content to drive the matching of these templates.

In general, a template could match anywhere in a spreadsheet, but might be constrained in where it can be matched.  A common case envisaged to to restrict matches to the first column, which could thereby be reserved as a kind of keyword field and thus avoid unwanted matches.

An additional wrinkle is introduced by requirement 2: repeated values.  Two approaches might be considered for this:  (1) an explicit repeart construct in a template, and/or (2) a variable "skip" construct that allows a template to match multiple regions separated by designated content - the repatition woukld then be handled by repeated matching of the template with differently sized skips.

Implementation of the templkate matching could be handled by a Parsec/pyParsing style combinator library, which would allow the initial implementation to be focused on immediate needs, and functionality to be added in as needed.

See also:
* [checklist/README.md](../src/checklist/README.md)


