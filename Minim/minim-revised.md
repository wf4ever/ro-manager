# Minim checklist description

The MINIM description contains 3 levels of description:

* `minim:Checklist` associates a target (e.g. an RO or a resource within an RO) and purpose (e.g. runnable workflow) with a minim:Model to be evaluated.
* `minim:Model` enumerates the requirements (checklist items) to be evaluated, with provision for MUST / SHOULD / MAY requirement levels cater for limited variation in levels of checklist conformance.
* `minim:Requirement` is a single requirement (checklist item), which is associated with a rule for evaluating whether or not it is satisfied or not satisfied.  There are several types of rules for performing different types of evaluation of the supplied data.  Additional evaluation capabilities can be added by adding new rule types to the set of those supported.

These three levels are called out in the sections below.
A definition of the Minim ontology can be found at [https://github.com/wf4ever/ro-manager/tree/develop]()

A minim checklist implementation evaluates a checklist in some context.  A minimum realization for such a context is the presence of some RDF metadata describing the resources associated with it.  In our implementation, the context is a Research Object (@@ref), and the descriptive metadata is a merge of all its aggregated annotations.


## minim:Checklist

The goal of our approach is to determine suitability for some user selected purpose, so there may be several checklists defined, each associated with evaluating suitability of some data for different purposes.

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
    minim:hasMustRequirement :has_workflow_instance" ;
    minim:hasMustRequirement :has_workflow_inputfiles" ;
    minim:hasMustRequirement :environment_python .


## minim:Requirement

Minim requirements are evaluated using rules.  The current implementation defined two types of rule: a `minim:QueryTestRule` and a `minim:SoftwareEnvRule`, which are described later.  If and when new requirements are encountered that cannot be covered by available rules, new rule types may be introduced to the model and added to its implementation.

The basic structure of a requirement is an association between the identified requirement and its associated evaluation rule; e.g.

    :has_workflow-instance a minim:Requirement
      rdfs:label "Workflow instance requirement"
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


#### `minim:CardinalityTest`

This test looks for a minimum and/or maximum number of distinct matches of the query pattern.  To test for the existence of some information matching a query, at least 1 result is expected, as in the following example that tests for the presence of a workflow resource in the queried metadata (assuming use of `wfdesc` terms (@@ref) in the metadata):

    :has_workflow_instance_rule a minim:QueryTestRule ;
      minim:query 
        [ a minim:SparqlQuery ; 
          minim:sparql_query "?wf rdf:type wfdesc:Workflow" ] ;
      minim:min 1 ;
      minim:showpass "Workflow instance or template found" ;
      minim:showfail "No workflow instance or template found" .

@@need to decide if show/showpass/showfail are part of the requirement or part of the rule.  I think they should be part of the requirement, but this means we need to define that Minim environment variables can be returned by rules.


#### `minim:AccessibilityTest`

#### `minim:AggregationTest`

@@specific to RO context

#### `minim:RuleTest`

#### `minim:RuleNegationTest`

@@is this needed?

#### `minim:Existstest`

@@strictly redundant




Liveness testing
To test for liveness of a resource, the evaluator will need to attempt to access the resource. If it is a local file, a file existence check should suffice. If it is a web resource, then a success response to an HTTP HEAD request is expected.

  <!-- Workflow descriptions must be accessible (live) -->
  <minim:Requirement rdf:about="#workflows_accessible">
    <minim:isDerivedBy>
      <minim:ContentMatchRequirementRule>
        <minim:forall>
          ?wf rdf:type wfdesc:Workflow .
        </minim:forall>
        <minim:isLiveTemplate>
          {+wf}
        </minim:isLiveTemplate>
        <minim:showpass>All declared workflow descriptions are accessible</minim:showpass>
        <minim:showfail>Workflow description %(wf)s is not accessible</minim:showfail>
        <minim:derives rdf:resource="#workflows_accessible" />
      </minim:ContentMatchRequirementRule>
    </minim:isDerivedBy>
  </minim:Requirement>
This varies from the simple aggregation test in that the minim::aggregatesTemplate property is replaced by a minim:isLiveTemplate property.



#### Requirement for workflow input files to be defined

This use of a minim:ContentMatchRequirementRule uses the SPARQL query as a probe to find all workflow output files mentioned according to the wfdesc description vocabulary, and for each of these tests that the indicated resource is indeed aggregated by the RO (a weak notion of being "present" in the RO). The URI of the required aggregated resource is constructed using a URI template (http://tools.ietf.org/html/rfc6570) with query result values. The diagnostic messages can interpolate query result values, as in the case of minim:showfail in this example.

  <!-- Workflow output files must be present -->
  <minim:Requirement rdf:about="#isPresent/workflow-outputfiles">
    <minim:isDerivedBy>
      <minim:ContentMatchRequirementRule>
        <minim:forall>
          ?wf rdf:type wfdesc:Workflow ;
              wfdesc:hasOutput [ wfdesc:hasArtifact ?of ] .
        </minim:forall>
        <minim:aggregatesTemplate>{+of}</minim:aggregatesTemplate>
        <minim:showpass>All workflow outputs referenced or present</minim:showpass>
        <minim:showfail>Workflow %(wf)s output %(of)s not found</minim:showfail>
        <minim:derives rdf:resource="#isPresent/workflow-outputfiles" />
      </minim:ContentMatchRequirementRule>
    </minim:isDerivedBy>
  </minim:Requirement>

Software environment testing
A minim:SoftwareEnvironmentRule tests to see if a particular piece of software is available by issuing a command and checking the response against a supplied regular expression. (This test is primarily intended for local use within RO-manager, and may be of limited use on the evaluation service as the command is issued on the host running the evaluation service, not on the host requesting the service.)

  <!-- Environment needs python -->
  <minim:Requirement rdf:about="#environment-software/python">
    <minim:isDerivedBy>
      <minim:SoftwareEnvironmentRule>
        <minim:command>python --version</minim:command>
        <minim:response>Python 2.7</minim:response>
        <minim:show>Installed python version %(response)s</minim:show>
        <minim:derives rdf:resource="#environment-software/python" />
      </minim:SoftwareEnvironmentRule>
    </minim:isDerivedBy>
  </minim:Requirement>
