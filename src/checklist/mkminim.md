# mkminim: Minim checklist file creator

This note describes a utility that may be used to create Minim checklist description
files from a checklist description presented in spreadsheet tabular form.

## Using mkminim

`mkminim` is installed as part of the [ro-manager package](https://pypi.python.org/pypi/ro-manager/),
version 0.2.13 or later.

To use `mkminim`, perform the following steps

1. Create a checklist descriptrion in a spreadsheet program
   (this procedure has been tested using Excel, but other spreadsheet programmes should be usable).  
   The spreadsheet layout and structure for a checklist description is described below.  
   Also, there is a simple example checklist in GitHub at 
   [mkminim-documentation-example](https://github.com/wf4ever/ro-catalogue/tree/master/v0.1/mkminim-documentation-example).
2. Export the spreadsheet data in CSV format.
   The exported data should look like the CSV example in GitHub at 
   [mkminim-documentation-example](https://github.com/wf4ever/ro-catalogue/tree/master/v0.1/mkminim-documentation-example).
3. Use the `mkminim` command thus:

       	mkminim (filename).csv > (filename).ttl

   or

       	mkminim -o xml (filename).csv > (filename).rdf

   where `(filename).csv` is the name of the CSV file that is the saved spreadsheet.
   If no errors are reported, the result of executing either of these commands is an RDF file
   that contains a Minim description corresponding to the supplied spreadsheet, which can be 
   supplied to the checklist evaluation service.

## Checklist evaluation context

When the checklist service is invoked, a Research Object (RO), Minim file, _purpose_ and _target resource_ are input parameters (with the target resource defaulting to the RO).  The _purpose_ and _target_ values are matched against the available checklists described in the Minim file to select a Minim Model for evaluation.

The Research Object provides a context for the checklist evaluation, consisting of:

* a set of aggregated resources: these are just resources that are considered to be "part of" por "aggregated by" the research object, identified by URIs.  Thne resources may be accessible web resources, or arbitrary named entities such as people or physical objects.
* a set of RDF annotations relating to the Research Object and/or its aggregated resources.  For the purpose of checklist evaluation, the RDF annotations are merged into a single RDF graph, which is probed using SPARQL query patterns.  See the rule type descriptions below for more details.  Some checklist requirements may be evaluated without specific reference to the Research Object (such as the software environment test described below).


## Spreadsheet format for describing checklists

There is an example spreadsheet with checklist descriptions in GitHub at 
[mkminim-documentation-example](https://github.com/wf4ever/ro-catalogue/tree/master/v0.1/mkminim-documentation-example).
We recommend downloading the [Excel spreadsheet](https://github.com/wf4ever/ro-catalogue/blob/master/v0.1/mkminim-documentation-example/TestMkMinim.xls) and viewing it in some suitable spreadsheet software.

The checklist description is in several parts:

* URI prefix definitions.
* One or more Checklist definitions.
* One or more Minim Model definitions.
* One or more rules, each of which is used to test a requirement.
* End of Minim definition

Each part is initiated by a keyword that MUST appear in the first column of the spreadsheet, and MUST appear exactly as shown in the examples below.  I.e. <b>Prefixes:</b>, <b>Checklists:</b>, <b>Model:</b>, <b>Items:</b> and <b>Model:</b>.


## URI prefix definitions

These allow short [CURIE](http://www.w3.org/TR/curie/) forms of URIs to be used in SPARQL queries that are used by many checklist requirement rules.

A prefix section typically looks like this.  Prefixes may be added or dropped as required.

| <b>Prefixes:</b> | <b>Prefix</b> |                  <b>URI</b>                 |
|------------------|---------------|---------------------------------------------|
|                  | rdf           | http://www.w3.org/1999/02/22-rdf-syntax-ns# |
|                  | rdfs          | http://www.w3.org/2000/01/rdf-schema#       |
|                  | owl           | http://www.w3.org/2002/07/owl#              |
|                  | xsd           | http://www.w3.org/2001/XMLSchema#           |
|                  | xml           | http://www.w3.org/XML/1998/namespace        |
|                  | rdfg          | http://www.w3.org/2004/03/trix/rdfg-1/      |
|                  | ore           | http://www.openarchives.org/ore/terms/      |
|                  | ao            | http://purl.org/ao/                         |
|                  | dcterms       | http://purl.org/dc/terms/                   |
|                  | ro            | http://purl.org/wf4ever/ro#                 |
|                  | minim         | http://purl.org/minim/minim#                |
|                  | ex            | http://example.org/                         |

> @@NOTE: currently, these prefixes are not used, but a hard-coded list is built into the checklist evaluator.  It is intended to change this aspect of the implementation.  However, these prefixes are currently used when generating the RDF for the Minim description, which probably should be based on a fixed list.


## Checklist definition

This associates a Minim Model with a target resource URI-template and a purpose.

When the checklist service is invoked, the RO, purpose and target resource are input parameters (with the target resource defaulting to the RO), and these values are matched against the available checklists to select a Minim Model for evaluation.

If no match is found for the supplied paerameters in the Minim definition file, no Minim Model is selected and the evaluation process returns an error.

| <b>Checklists:</b> | <b>Target</b> | <b>Purpose</b>        | <b>Model</b>               |
|--------------------|---------------|-----------------------|----------------------------|
|                    | {+targetro}   | <i>purpose-string</i> | <i>Model URI-reference</i> |
|                    | {+targetro}   | <i>purpose-string</i> | <i>Model URI-reference</i> |

The value in the <b>Target</b> column is a [URI template](http://tools.ietf.org/html/rfc6570), which is expended with variables `targetro` beingthe URI of the RO being evalutated, and `targetres` being the URI of the target resource specified in the evaluation request.  Thius specifying `{+targetro}` indicates that the corresponding Minim Model may be used when the target resource being evaluated is the research object itself.  (In some cases, it may be useful to associate specific resources with specific Minim Mopdels, but this may make the Minim description less generically applicable.)


## Minim Model definition

A Minim Model is an identified list of requirements to be satisfied, 
each with an associated requirement level ("MUST", "SHOULD" or "MAY"), and 
a sequence number that is used to order the individual requirement test results for presentation.

|  <b>Model:</b>  | <i>Model URI-reference</i> |               |
|-----------------|----------------------------|---------------|
| <b>Items:</b>   | <b>Level</b>               | <b>Rule</b>   |
| <i>sequence</i> | <i>req-level</i>           | <i>req-id</i> |
| :               | :                          | :             |
| <i>sequence</i> | <i>req-level</i>           | <i>req-id</i> |

The <i>Model URI-reference</i> identifies the defined Minim Model,
and is used to associate a checklist definition (see above) with this entry.

The <i>sequence</i> values are sortable alphanumeric keys, and may be used to order the results in a display of the checklist evaluation.  Note that pure numeric values may not sort as expected, as the ordering is generally determined by string rather than numeric comparison.

The <i>req-level</i> values are `MUST`, `SHOULD` or `MAY`, indicating the level of importance attached to the corresponding requirement.

The <i>req-id</i> values are URI references that identify the rules (see below) that are used to evaluate the corresponding requirement.

## Requirement evaluation rule

A rule is used to test an identified requirement.  Each rule starts with:

| <b>Rule:</b> |   <i>req_id</i>    |                             |
|--------------|--------------------|-----------------------------|

Where the <i>req-id</i> values is a URI references that indicates the requirements (see above) that they are used for testing.  The format of the remainder of the rule varies with the type of rule defined.

There are several types of rule, the formats for which are enumerated in the sections below:

* Exists data rule
* ForEach match Exists data
* ForEach match Aggregates resource
* ForEach match Accessible resource
* Match cardinality rule
* Software environment test

Diagnostic message elements are common to all rule types:
* Pass message
* Fail message
* No-match message

### Exists data rule

This rule uses a SPARQL query pattern to test for the existence of some data in the Research Object annotations.  If the query is matched, the test succeeds, otherwise it fails.

| <b>Rule:</b> |   <i>req_id</i>    |                             |
|--------------|--------------------|-----------------------------|
|              | <b>Exists:</b>     | <i>SPARQL query pattern</i> |
|              | <b>Pass:</b>       | <i>pass message</i>         |
|              | <b>Fail:</b>       | <i>fail message</i>         |

### ForEach match Exists data

This rule probes the RO annotation data with a SPARQL query pattern, and for each match found it tests to see if some related information is also present.  Query variables bound by each match of the initial <b>ForEach:</b> query are used in a corresponding <b>Exists:</b> query.

| <b>Rule:</b> |  <i>req_id</i>  |                                  |
|--------------|-----------------|----------------------------------|
|              | <b>ForEach:</b> | <i>SPARQL query pattern</i>      |
|              | <b>Exists:</b>  | <i>SPARQL query pattern</i>      |
|              | <b>Pass:</b>    | <i>pass message</i>              |
|              | <b>Fail:</b>    | <i>fail message</i>              |
|              | <b>None:</b>    | <i>Optional no-match message</i> |

### ForEach match Aggregates resource

This rule probes the RO annotation data with a SPARQL query pattern, and for each match found it tests to see if some related resource is aggregated by the RO.  The resource is identified by a [URI template](http://tools.ietf.org/html/rfc6570), where query variables from each match of the <b>ForEach:</b> query are provided as inputs when the URI template is expanded to construct a resource URI to be tested.

| <b>Rule:</b> |   <i>req_id</i>    |                                  |
|--------------|--------------------|----------------------------------|
|              | <b>ForEach:</b>    | <i>SPARQL query pattern</i>      |
|              | <b>Aggregates:</b> | <i>URI template</i>              |
|              | <b>Pass:</b>       | <i>pass message</i>              |
|              | <b>Fail:</b>       | <i>fail message</i>              |
|              | <b>None:</b>       | <i>Optional no-match message</i> |


### ForEach match Accessible resource

This rule probes the RO annotation data with a SPARQL query pattern, and for each match found it tests to see if some related resource is accessible on the Web.  The resource is identified by a [URI template](http://tools.ietf.org/html/rfc6570), where query variables from each match of the <b>ForEach:</b> query are provided as inputs when the URI template is expanded to construct a resource URI to be tested.

| <b>Rule:</b> |  <i>req_id</i>  |                                  |
|--------------|-----------------|----------------------------------|
|              | <b>ForEach:</b> | <i>SPARQL query pattern</i>      |
|              | <b>IsLive:</b>  | <i>URI template</i>              |
|              | <b>Pass:</b>    | <i>pass message</i>              |
|              | <b>Fail:</b>    | <i>fail message</i>              |
|              | <b>None:</b>    | <i>Optional no-match message</i> |


### Match cardinality rule

This rule probes the RO annotation data with a SPARQL query pattern, and counts the number of distinct matches found.
The resultinbg count is tested against supplied minimum and/or maximum values: if less than the specified minimuym, or greater thamn the specified maximum, the test fails.

| <b>Rule:</b> |  <i>req_id</i>  |                             |
|--------------|-----------------|-----------------------------|
|              | <b>ForEach:</b> | <i>SPARQL query pattern</i> |
|              | <b>Min:</b>     | <i>min cardinality</i>      |
|              | <b>Pass:</b>    | <i>pass message</i>         |
|              | <b>Fail:</b>    | <i>fail message</i>         |

or

| <b>Rule:</b> |  <i>req_id</i>  |                             |
|--------------|-----------------|-----------------------------|
|              | <b>ForEach:</b> | <i>SPARQL query pattern</i> |
|              | <b>Max:</b>     | <i>max cardinality</i>      |
|              | <b>Pass:</b>    | <i>pass message</i>         |
|              | <b>Fail:</b>    | <i>fail message</i>         |

or

| <b>Rule:</b> |  <i>req_id</i>  |                             |
|--------------|-----------------|-----------------------------|
|              | <b>ForEach:</b> | <i>SPARQL query pattern</i> |
|              | <b>Min:</b>     | <i>exact cardinality</i>    |
|              | <b>Max:</b>     | <i>exact cardinality</i>    |
|              | <b>Pass:</b>    | <i>pass message</i>         |
|              | <b>Fail:</b>    | <i>fail message</i>         |


### Software environment test

This test probes the execution environment of the host running the checklist service, by issuing a specified shell command and testing the generated output (i.e. output send to the standard output stream) agains a supplied [Python regular expression](http://docs.python.org/2/library/re.html#regular-expression-syntax).  If it matches, the test succeeds, otherwise the test fails.

| <b>Rule:</b> |  <i>req_id</i>   |                        |
|--------------|------------------|------------------------|
|              | <b>Command:</b>  | <i>command</i>         |
|              | <b>Response:</b> | <i>response regexp</i> |
|              | <b>Pass:</b>     | <i>pass message</i>    |
|              | <b>Fail:</b>     | <i>fail message</i>    |


### Diagnostic message elements

These elements can be used with any rule:

| <b>Rule:</b> |     ...      |                                                                       |
|--------------|--------------|-----------------------------------------------------------------------|
|              |     ...      | ...                                                                   |
|              | <b>Pass:</b> | <i>Message for checklist item display when rule is satisfied     </i> |
|              | <b>Fail:</b> | <i>Message for checklist item display when rule is not satisfied </i> |
|              | <b>None:</b> | <i>Optional message when ForEach element of rule is not matched  </i> |

The message strings are Python format strings, and may contain emebedded codes of the form `%(name)s`, 
which are replaced by values from matched queries, or other values.  The exact values availabl;e for substitution vary with the rule type, but in the case of <b>ForEach:</b> rules, the query variables from a query match are available to a corresponding <b>Fail:</b> message.

@@TODO - list other message substitution variables


## End of Minim definition

The Minim description is terminated by a cell on column 1 of the spreadsheet data containing just "End:".



