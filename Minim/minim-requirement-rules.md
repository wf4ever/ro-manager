## 1. Exists(query)

The simplest kind of requirement simply looks for information in the RO metadata matching a supplied SPARQL query.

Example: does the RO contain a hypothesis?

Rule:

    Exists("?hyp rdf:type roterms:Hypothesis")

In order to formulate the query, knowledge of the vocabulary used in the RO metadata is required (as well as knowledge of SPARQL query patterns).


## 2. ForEach(query), Exists(query)

This is a slightly extended form of the exists query that collects results from one query, and for each result obtained tests to see if there is a corresponding match to a second query.

Example: does each workflow defined by an RO have a title specified?

Rule:

    ForEach("?wf rdf:type wfdesc:Workflow")
    Exists("?wf dcterms:description ?wfdescr")

The query patterns here assume use of the `wfdesc` and `dcterms` vocabularies respectively.

Here, for each result obtained by the first query, the resulting value for `?wf` is passed into the second query pattern.  The rule terminates with failure on the first result for which there is no match of the `Exists` query.


## 3. ForEach(query), IsAggregated(template)

This form of requirement is used to make sure that resources referenced by an RO are explicitly aggregated as part of the RO.  This might be used as part of a test to ensure that all key resources for an experiment are actually specified to be part of the RO.

Example:  are all inputs for all workflows defined by an RO also aggregated in the RO?

Rule:

    ForEach("?wf rdf:type wfdesc:Workflow ; wfdesc:hasInput [ wfdesc:hasArtifact ?if ]")
    IsAggregated("{+if}")

The initial query locates all the specific input resources that are mentioned by any described workflow.  The second part uses each result of that query to expand a URI template, thus constructing a URI, and then test to see if the resources thus named is aggregated by the RO.  This is a form of test that cannot be handled by queries alone.


## 4. ForEach(query), IsLive(template)

This form of requirement is used to make sure that resources referenced by an RO are accessible though the web.  This might be used as part of a test to ensure that all key resources for a workflow run are actually accessible.

Example:  are all inputs for all workflows defined by an RO accessible?

Rule:

    ForEach("?wf rdf:type wfdesc:Workflow ; wfdesc:hasInput [ wfdesc:hasArtifact ?if ]")
    IsLive("{+if}")

This follows a very similar pattern to the previous example: the initial query locates all the specific input resources that are mentioned by any described workflow.  The second part uses each result of that query to test that the resource is accessible, by performing an HTTP HEAD request to the URI obtained by expanding the template.  This is another form of test that cannot be handled by queries alone.


## 5. Cardinality test

This form of query is a generalisation of the ForEach-Exists test, and can be used to constrain the number results obtained for a query.

Example: has the RO been reviewed by at least 2 collaborators of its creator?

Rule:

    ForEach("?targetro dcterms:creator ?researcher ;  roterms:reviewedBy ?reviewer")
    Exists("?reviewer semcerif:Collaborator ?researcher")
    Min(2)

The `Min(2)` qualifier here requires that there are at least two results of the original `ForEach` query that are satisfied by the corresponding `Exists` query.  (This is a slightly weak example, as the test could be done using a single query.)


## 6. Software environment test

This is a completely different kind of test, which does not involve querying an RO.  It allows the software environment in which the RO is being evaluated to be tested, and might be used to advise a user if the current environment contains tools needed to repeat the results reported in an RO.

Example: does the software environment support Python version 2.7?

Rule:

    Command("python --version")
    Response("Python 2\.7(\.\d+)?")

This rule works by issuing the given command, and testing the response that is written to its standard output stream.  The `Response` value is a regular expression that is matched against the standard output from the command: if it matches, the test passes, otherwise it fails.  This is a generic mechanism that can be used to probe the host software environment in a variety of ways.

