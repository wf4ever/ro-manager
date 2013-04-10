# Minim checklist description

The MINIM description contains 3 levels of description:

* `minim:Checklist` associates a target (e.g. an RO or a resource within an RO) and purpose (e.g. runnable workflow) with a minim:Model to be evaluated.
* `minim:Model` enumerates the requirements (checklist items) to be evaluated, with provision for MUST / SHOULD / MAY requirement levels cater for limited variation in levels of checklist conformance.
* `minim:Requirement` is a single requirement (checklist item), which is associated with a rule for evaluating whether or not it is satisfied or not satisfied.  There are several types of rules for performing different types of evaluation of the supplied data.  Additional evaluation capabilities can be added by adding new rule types to the set of those supported.

These three levels are called out in the sections below.
A definition of the Minim ontology can be found at [https://github.com/wf4ever/ro-manager/tree/develop]()

A minim checklist implementation evaluates a checklist in some context.  A minimum realization for such a context is the presence of some RDF metadata describing the resources associated with it.  In our implementation, the context is a Research Object (@@ref), and the descriptive metadata is a merge of all its aggregated annotations.


## minim:Checklist

The goal of our approach is to determine suitability for some user selected purpose, so there may be several checklists defined, each associated with evaluating suitability of some data for different purposes.  A Checklist may be associated directly with a target resource as the subject of a `minim:hasChecklist` statement, or may be associated indirectly via a URI template that is the object of an associated `minim:forTargetTemplate` statement. The latter form is is more flexible as it allows a given checklist to be more easily used with multiple resources.


A minim:Checklist provides information that can be used to select a minim:Model and a Research Object, or a resource within a resource object, to be evaluated to determine its suitability for some purpose.  This example indicates a minim:Model that might be used for evaluating whether or not a workflow contains a runnable workflow:

    :runnable_workflow a minim:Checklist ;
      minim:forTargetTemplate "{+targetro}" ;
      minim:forPurpose "runnable" ;
      minim:toModel :runnable_workflow_model ;
      rdfs:comment """Select model to evaluate if RO contains a runnable workflow""" .

The `minim:Checklist` structure provides a link between a generic `minim:Model` structure and the application environment in which it is implemented.  In our implementation, the evaluation context is provided by a Research Object and a supplied Minim description resource which may contain several checklist definitions as above.  Also provided by the evaluation context are some Minim environment variables:

* `targetro`: the URI of the research object being evaluated
* `targetres`: the URI of a particular resource that is targeted by the evaluation, which may be specified in the checklist evaluation API.  If no explicit target is specified, this defaults to the RO URI.

These Minim environment variables may be used in subsequent requirement rule descriptions, and in particular may be used as pre-bound query variables in the query part of some requirement rules.


## minim:Model

A minim:Model enumerates of a number of requirements which may be declared at levels of MUST, SHOULD or MAY be satisfied for the model as a whole to be considered satisfied. This follows a structure for minimum information models proposed by Matthew Gamble.  Here is an example of a model that has been used for testing whether a runnable workflow is present:

    :runnable_workflow_model a minim:Model ;
      rdfs:label "Minimum information for RO containing a runnable workflow"
      rdfs:comment
        """
        This model defines information that must be available in a Research Object containing a runnable workfow
        which in turn may need a Python software interpeter to be available.
        """ ;
      minim:hasMustRequirement :has_workflow_instance ;
      minim:hasMustRequirement :live_workflow ;
      minim:hasMustRequirement :has_workflow_inputfiles" ;
      minim:hasMustRequirement :environment_python .


## minim:Requirement

Minim requirements are evaluated using rules.  The current implementation defined two types of rule: a `minim:QueryTestRule` and a `minim:SoftwareEnvRule`, which are described later.  If and when new requirements are encountered that cannot be covered by available rules, new rule types may be introduced to the model and added to its implementation.

The basic structure of a requirement is an association between the identified requirement and its associated evaluation rule; e.g.

    :has_workflow-instance a minim:Requirement ;
      rdfs:label "Workflow instance requirement" ;
      rdfs:comment
        """
        For a Research Object to contain a runnable workflow, a workflow instance must be specified.
        """ ;
      minim:isDerivedBy :has_workflow_instance_rule .


### minim:QueryTestRule

This is a "swiss army knife" of a rule which in its various forms is capable of handling most of the checklist requirements we encounter.  It consists of three parts:

* a SPARQL query, which is evaluated against the RDF metadata that described the evaluation context (i.e., in our implementation, the merged annotations from a Research Object).  The result of evaluating this query is a list of variable bindings, each of which defines values for one or more variable names that appear in the SPARQL query.  Any Minim environment variables are treated as pre-bound variables, which means that the query can generate results that are dependent on the evaluation context.
* (optionally) a resource to be queried.  If not specified, the supplied evaluation context metadata is used.  The resource is specified as a URI template that is expanded using currently defined Minim environment variables, and dereferenced to retrieve an RDF graph value that is queried.
* a query result test, which takes the query result and returns a True (pass) or False (fail) result.  The test may simply examine the supplied query result, or may use that result to perform further interrogation of resources outside the immediate context; e.g. testing if a web resource mentioned in the supplied metadata is actually accessible.

Several different types of query result test are provided, and additional test types may be added to the model (and implementation) if existing tests do not provide the required assurances.  The various test typess currently defined are described in the following sections.


#### `minim:CardinalityTest` (existence test)

This test looks for a minimum and/or maximum number of distinct matches of the query pattern.  To test for the existence of some information matching a query, at least 1 result is expected, as in the following example that tests for the presence of a workflow resource in the queried metadata (assuming use of `wfdesc` terms (@@ref) in the metadata):

    :has_workflow_instance_rule a minim:QueryTestRule ;
      minim:query 
        [ a minim:SparqlQuery ; 
          minim:sparql_query "?wf rdf:type wfdesc:Workflow ." ] ;
      minim:min 1 ;
      minim:showpass "Workflow instance or template found" ;
      minim:showfail "No workflow instance or template found" .

@@need to decide if show/showpass/showfail are part of the requirement or part of the rule.  I think they should be part of the requirement, but this means we need to define that Minim environment variables can be returned by rules.


#### `minim:AccessibilityTest` (liveness test)

For each result returned by the query, tests that a resource is accessible (live).  If there is any result for which the accessibility test fails, then the rule as a whole fails.

Each set of variable bindings returned by the query is used to construct the URI of a resource to be tested through expansion of a URI template, where the query variables are mapped to variables of the same name used in the template.

The following example tests that each workflow definition mentioned in the queried metadata is accessible.  If it is a local file, a file existence check is performed.  If it is a web resource, then a success response to an HTTP HEAD request is expected.

    :live_workflow_rule a minim:QueryTestRule ;
      minim:query 
        [ a minim:SparqlQuery ; 
          minim:sparql_query 
            """
            ?wf rdf:type wfdesc:Workflow ;
              rdfs:label ?wflab ;
              wfdesc:hasWorkflowDefinition ?wfdef .
            """ ] ;
      minim:isLiveTemplate {+wfdef} ;
      minim:showpass "All workflow instance definitions are live (accessible)" ;
      minim:showfail "Workflow instance defininition %(wfdef)s for workflow %(wflab)s is not accessible" .


#### `minim:AggregationTest`

This test is specific to a Research Object context.  It tests to see if a resource defined by each query result is aggregated by the Research Object.

The following example tests that each workflow definition mentioned in the queried metadata is aggregated in the Research Object. The RO URI is accessible through Minim environment variable `targetro`, as described above.

    :aggregated_workflow_rule a minim:QueryTestRule ;
      minim:query 
        [ a minim:SparqlQuery ; 
          minim:sparql_query 
            """
            ?wf rdf:type wfdesc:Workflow ;
              rdfs:label ?wflab ;
              wfdesc:hasWorkflowDefinition ?wfdef .
            """ ] ;
      minim:aggregatesTemplate {+wfdef} ;
      minim:showpass "All workflow instance definitions are aggregated by RO %(targetro)s" ;
      minim:showfail "Workflow instance defininition %(wfdef)s for workflow %(wflab)s is not aggregated by RO %(targetro)s" .

#### `minim:RuleTest`

The variable bindings from each query result are used as additional Minim environment variables in a new rule invocation.  If the new invocation succeeds for every such result, then the current rule succeeds.

The following example uses a cardinality test for each workflow described in the metadata to ensure that each such workflow has at least one defined input resource:

    :has_workflow_inputfiles a minim:QueryTestRule ;
      minim:query 
        [ a minim:SparqlQuery ; 
          minim:sparql_query 
            """
            ?wf rdf:type wfdesc:Workflow ;
              rdfs:label ?wflab .
            """ ] ;
      minim:affirmRule
        [ a minim:QueryTestRule ;
          minim:query
            [ a minim:SparqlQuery ; 
              minim:sparql_query 
                """
                ?wf wfdesc:hasInput [ wfdesc:hasArtifact ?if ] .
                """ ] ;
          mnim:min 1 ;
          minim:showpass "Workflow %(wflab)s has defined input(s)" ;
          minim:showfail "Workflow %(wflab)s has no defined input" ] ;
      minim:showpass "All workflow instance definitions have defined inputs" ;
      minim:showfail "Workflow %(wflab)s has no defined input" .


#### `minim:RuleNegationTest`

@@is this needed?

As previous, but the current rule succeeds if the referenced rule fails (forall/forsome?) query result.


#### `minim:ExistsTest`

@@this test is strictly redundant

If defined, this would be a short cut form for `minim:RuleTest` with `minim:CardinalityTest`; e.g. the previous `minim:RuleTest` example might be presented as:

    :has_workflow_inputfiles a minim:QueryTestRule ;
      minim:query 
        [ a minim:SparqlQuery ; 
          minim:sparql_query 
            """
            ?wf rdf:type wfdesc:Workflow ;
              rdfs:label ?wflab .
            """ ] ;
      minim:exists
        [ a minim:SparqlQuery ; 
          minim:sparql_query 
            """
            ?wf wfdesc:hasInput [ wfdesc:hasArtifact ?if ] .
            """ ] ;
      minim:showpass "All workflow instance definitions have defined inputs" ;
      minim:showfail "Workflow %(wflab)s has no defined input" .


### Software environment testing

A `minim:SoftwareEnvRule` tests to see if a particular piece of software is available in the current execution environment by issuing a command and checking the response against a supplied regular expression. (This test is primarily intended for local use within RO-manager, and may be of limited use on the evaluation service as the command is issued on the host running the evaluation service, not on the host requesting the service.)

The result of running the command (i.e. data written to its standard output stream) is used to define a new Minim environment variable, which can be used for diagnostic purposes.

    :environment_python a minim:SoftwareEnvRule ;
      minim:command "python --version" ;
      minim:response "Python 2.7" ;
      minim:show "Installed python version %(response)s" .


# Notes

* Currently, the OWL ontology does not define the diagnostic message prioperties
* Need to decide how diagnostics should be incorporatedL: as part of requirement or part of rule?
* Negated rule test; need to think if all or some results should result in failure
* Maybe need to think about generalizing `minim:Ruletest` to handle rule composition
* Drop `minim:existstest`, or keep it?
* See: http://www.essepuntato.it/lode/owlapi/https://raw.github.com/wf4ever/ro-manager/develop/Minim/minim-revised.omn

