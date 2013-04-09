# Minim checklist description

The MINIM description contains 3 levels of description:

* minim:Constraint associates a target and purpose (e.g. runnable RO) to a minim:Model
to be evaluated.
* minim:Model enumerates the checklist items (a list of requirements) to be evaluated, with provision for MUST / SHOULD / MAY requirement levels cater for limited variation in levels of conformance.
* minim:Requirement is a single requirement (checklist item), which is associated with a rule for evaluating whether or not it is satisfied or not satisfied.  There are several types of rules for performing different types of evaluation of the supplied data.  Additional evaluation capabilities can be added by adding new rule types to the set of those supported.

These three levels are called out in the sections below.
A definition of the Minim ontology can be found at https://github.com/wf4ever/ro-manager/tree/develop


## minim:Constraint

There may be several checklists defined, each associated with evaluating suitability of some data for different purposes.

A minim constraint provides information that can be used to locate a Minim checklist to evaluate a Research Object, or a resource within a resource object, to determine its suitability for some purpose.






These 3 levels are called out in the examples that follow

See:

https://github.com/wf4ever/ro-manager/blob/master/src/iaeval/Minim/minim.rdf
https://github.com/wf4ever/ro-catalogue/blob/master/v0.1/simple-requirements/simple-requirements-minim.rdf
http://www.wf4ever-project.org/wiki/display/docs/RO+Examples
Minim Constraint
The "constraint" provides the basis for mapping from target and purpose values to a particular minim:Model to be used as the basis of an evaluation. Relative URI references are resolved relative to the location of the Minim resource. In this example, the Minim resource is taken from the root directory of an RO, so "." refers to the RO itself.

  <minim:Constraint rdf:about="#runnable_RO">
    <minim:forPurpose>Runnable</minim:forPurpose>
    <minim:onResource rdf:resource="." />
    <minim:toModel rdf:resource="#runnable_RO_model" />
    <rdfs:comment>
      Constraint to be satisfied if the RO is to be runnable
    </rdfs:comment>
  </minim:Constraint>
Minim Model (checklist)
A minim model represents a checklist to be evaluated. It enumerates of a number of requirements which may be declared at levels of MUST, SHOULD or MAY be satisfied for the model as a whole to be considered satisfied. This follows a structure for minimum information models proposed by Matthew Gamble.

  <minim:Model rdf:about="#runnable_RO_model">
    <rdfs:label>Runnable RO</rdfs:label>
    <rdfs:comment>
      This model defines information that must be available for the 
      requirements Research Object to be runnable.
    </rdfs:comment>
    <minim:hasMustRequirement rdf:resource="#environment-software/lpod-show" />
    <minim:hasMustRequirement rdf:resource="#environment-software/python" />
    <minim:hasMustRequirement rdf:resource="#isPresent/workflow-instance" />
    <minim:hasMustRequirement rdf:resource="#isPresent/workflow-inputfiles" />
  </minim:Model>
Minim Requirements
Minim Requirements are evaluated using rules, which in turn invoke checklist evaluation primitives with appropriate parameters. This structure allows a relatively wide range of checklist items to be evaluated based on a relatively small number of primitive tests. The examples show the various primitives.

Requirement for an RO to contain a workflow primitive
The minim:ContentMatchRequirementRule is driven by a SPARQL query probe which is evaluated over a merge of all the RO annotations (including the RO manifest). In this case, it simply tests that the query can be satisfied. The minim:showpass and minim:showfail properties indicate strings that are used for reporting the status of the checklist evaluation.

  <!-- Workflow instance must be present -->
  <minim:Requirement rdf:about="#isPresent/workflow-instance">
    <minim:isDerivedBy>
      <minim:ContentMatchRequirementRule>
        <minim:exists>
          ?wf rdf:type wfdesc:Workflow .
        </minim:exists>
        <minim:showpass>Workflow instance or template found</minim:showpass>
        <minim:showfail>No workflow instance or template found</minim:showfail>
        <minim:derives rdf:resource="#isPresent/workflow-instance" />
      </minim:ContentMatchRequirementRule>
    </minim:isDerivedBy>
  </minim:Requirement>
Requirement for workflow output files to be present
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
