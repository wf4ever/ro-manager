# Minim checklist description

This document describes elements of the Minim checklist model.  Examples are presented using Turtle syntax (@@ref).

HTML and LaTeX versions of this document can be generated using Pandoc; e.g.:

    pandoc --table-of-contents --toc-depth=3 -c pandoc-html.css \
           --from=markdown --to=latex -o minim-revised.tex minim-revised.md

    pandoc --table-of-contents --toc-depth=3 -c pandoc-html.css \
           --from=markdown --to=html -o minim-revised.html minim-revised.md

## Checklist evaluation context

The Minim checklist model describes a set of requirements to be satisfied by some set of linked data for a designated resource to be suitable for some purpose.

Thus, the context required for evaluating a Minim checklist is a target resource, a set of linked data (an RDF graph) containing metadata about the target resource and related resources, and a purpose for which the resource is being evaluated.  The environment or service that invokes a checklist evaluation must supply:

* _metadata_: a set of linked data in the form of an RDF graph,
* _target_: the URI of a resource to be targeted by the evaluation, and
* _purpose_: a string that designates the purpose of the evaluation

For example, when the evaluation is applied to a Research Object (@@ref), the target resource may be the Research Object itself, the set of linked data is the set of annotations aggregated by the Research Object.  But the evaluation may also target an individual resource other than the Research Object while still depending on context that it provides, in which case the Research Object and the target resource must be specified as separate resources.

This information is used in conjunction with a set of `minim:Checklist` descriptions (see below) to select a `minim:Model` as the basis for the evaluation, and to construct an initial Minim _evaluation context_.  The Minim evaluation context consists of a set of variable/value bindings; the initial context contains the following bindings, and maybe others:

<table>
  <tr><td>&nbsp;&nbsp;</td><td><em><code>targetres</code></em></td><td>:</td><td>the URI of the resource that is the target of the current evaluation</td></tr>
</table>

Variables defined in the minim evaluation context, referred to later as _Minim environment variables_, are used in a number of ways:

* In query patterns, query variables that are the same as Minim environment variables are treated as being pre-bound: only those query results for which the returned variable binding would be the same as the existing Minim environment variable binding are returned.
* The results of a query are used as additional variables in constructs that depend on the result of that query.
* URI templates are expanded using Minim environment variables to supply values for template variables.
* Diagnostic messages containing Python-style `%(name)s` constructs have those constructs replaced by the value of the named Minim environment variable. 

The exact ways in which the Minim evaluation context is used depends upon the particular requirement being evaluated.  Most commonly, it is used in conjunction with a `minim:QueryTestRule` (described later).  For example, the following checklist requirement tests for an `rdfs:label` value for the target resource of an evaluation:

    :target_labeled a minim:QueryTestRule ;
      minim:query 
        [ a minim:SparqlQuery ; 
          minim:sparql_query "?targetres rdfs:label ?targetlabel ." ] ;
      minim:min 1 ;
      minim:showpass "Target resource label is %(targetlabel)s" ;
      minim:showfail "No label for target resource %(targetres)s" .

This queries the metadata for an `rdfs:label` applied to the evaluation target resource (whose URI is defined in the initial evaluation context as _`targetres`_, as described above).  If present, the requirement is satisfied and a message containing the label is returned.  Otherwise, the requirement is not satisfied and a message containing the target resource URI is returned.


## Checklist description structure

A Minim checklist contains 3 levels of description:

* `minim:Checklist` associates a target (e.g. an RO or a resource within an RO) and purpose (e.g. runnable workflow) with a minim:Model to be evaluated.
* `minim:Model` enumerates the requirements (checklist items) to be evaluated, with provision for MUST / SHOULD / MAY requirement levels cater for limited variation in levels of checklist conformance.
* `minim:Requirement` is a single requirement (checklist item), which is associated with a rule for evaluating whether or not it is satisfied or not satisfied.  There are several types of rules for performing different types of evaluation of the supplied data.  Additional evaluation capabilities can be added by adding new rule types to the set of those supported.

These three levels are called out in the sections below.
A definition of the Minim ontology can be found at [https://github.com/wf4ever/ro-manager/tree/develop]()

A minim checklist implementation evaluates a checklist in some context.  A minimum realization for such a context is the presence of some RDF metadata describing the resources associated with it.  In our implementation, the context is a Research Object (@@ref), and the descriptive metadata is a merge of all its aggregated annotations.


## minim:Checklist

The goal of our approach is to determine suitability for some user selected purpose, so there may be several checklists defined, each associated with evaluating suitability of some data for a different purpose.  

The role of a `minim:Checklist` resource is associate a target resource with a `minim:Model` that describes requirements for the resource to be suitable for an indicated purpose.  A `minim:Model` may be associated directly with a target resource that is the subject of a `minim:hasChecklist` statement, or may be associated indirectly via a URI template that is the object of an associated `minim:forTargetTemplate` statement. The latter form is is more flexible as it allows a given `minim:Modfel` to be more easily used with multiple resources.  This example indicates a `minim:Model` that might be used for evaluating whether or not a workflow contains a runnable workflow:

    :runnable_workflow a minim:Checklist ;
      minim:forTargetTemplate "{+targetro}" ;
      minim:forPurpose "runnable" ;
      minim:toModel :runnable_workflow_model ;
      rdfs:comment """Select model to evaluate if RO contains a runnable workflow""" .

The `minim:Checklist` structure provides a link between a `minim:Model` structure and the context in which it is evaluated.  In our implementation, the evaluation context is provided by a Research Object and a supplied Minim description resource, which may contain several checklist definitions as above.  Also provided by the Minim checklist evaluation context are some Minim environment variables:

<table>
  <tr><td>&nbsp;&nbsp;</td><td><em><code>targetres</code></em></td><td>:</td><td>the URI of the resource that is the target resource to be evaluated.  By default, this is the URI of provided Research Object.</td></tr>
  <tr><td>&nbsp;&nbsp;</td><td><em><code>targetro</code></em></td><td>:</td><td>the URI of the research object that provides contextual information (metadata) about the target resource.</td></tr>
</table>

See above for more information about the Minim checklist evaluation context.


## minim:Model

A minim:Model enumerates of a number of requirements which may be declared at levels of MUST, SHOULD or MAY be satisfied for the model as a whole to be considered satisfied. This follows an outline structure for minimum information models proposed by Matthew Gamble (@@ref).  Here is an example of a model that has been used for testing whether a runnable workflow is present:

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

Each requirement takes the form of a function that returns `true` (indicating that the requirement is satisfied), or `false` (indicating that the requirement is not satisfied).  It may also return a diagnostic string that may be used when reporting the outcome of the checklist evaluation.  This `true` or `false` values are sometimes referred to as _pass_ or _fail_.


### minim:QueryTestRule

This is a "swiss army knife" of a rule which in its various forms is capable of handling most of the checklist requirements we encounter.  It consists of three parts:

* a query pattern, which is evaluated against the RDF metadata that described the evaluation context (i.e., in our implementation, the merged annotations from a Research Object).  The result of evaluating this query is a list of variable bindings, each of which defines values for one or more variable names that appear in the query pattern.  Any supplied Minim environment variables are treated as pre-bound variables, which allows a query to generate results that are dependent on the evaluation context.
* (optionally) an external resource to be queried.  This value is used to probe data that is external to the evaluation context, rather that supplied metadata about the target resource.  If not specified, the supplied evaluation context metadata is used.  The external resource is specified as a URI template that is expanded using currently defined Minim environment variables, and dereferenced to retrieve an RDF graph value.
* a test, which analyzes values from the query result and returns a True (pass) or False (fail) result.  The test may simply examine the supplied query result, or may use that result to perform further interrogation of resources outside the immediate context; e.g. testing if a web resource mentioned in the supplied metadata is actually accessible.

The interaction of a `minim:QueryTestRule` with the evaluation context environment variables is particularly important to the way that it can be used.  If the query pattern mentions any variables that are already defined in the evaluation context, those variables are considered to be pre-bound in the query.  That is, only those query results in which the query variable matches a value equal to the environment variable value are returned.  Further, other query variables whose values are returned are used as additional environment variables in the tests that use the query result, and may be used in URI templates, diagnostic strings or as pre-bound variables in any further queries that are used.

Examples of query results used in URI tenmplates and diagnostic strings can be seen in the `minim:AccessibilityTest` section below.  An example of query results used in a further query can be seen in the section on `minim:RuleTest`.

Several different types of query result test are provided, and additional test types may be added to the model (and implementation) if existing tests do not provide the required assurances.  The various test types currently defined are described in the following sections.


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

