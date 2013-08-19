## Functionality

### wf4ever-ro-manager/Minim/minim-results.omn:

       21    # by the properties described below that are applied to the evaluated target resource.
       22  
       23:   # @@TODO: rename/synonym to match changes to Minim model?
       24    ObjectProperty: minim:testedConstraint
       25      Annotations:


### wf4ever-ro-manager/src/checklist/gridmatch.py:

      274      Match reference value in current cell, return as result is key given
      275  
      276:     @@TODO: handle CURIE prefix expansion
      277      """
      278      def __init__(self, k=None):


### wf4ever-ro-manager/src/rocommand/ro_remote_metadata.py:

       85      if status == 409:
       86          return (status, reason, None, data)
       87:     #@@TODO: Create annotations for title, creator, date??
       88      raise ROSRS_Error("Error creating RO", "%03d %s"%(status, reason), httpsession.baseuri())
       89  


### wf4ever-ro-manager/src/roverlay/rovweb/rovserver/ContentNegotiationView.py:

       63              </html>
       64              """ % values
       65:         # @@TODO: with Django 1.6, can also set reason string
       66          return HttpResponse(responsebody, status=values['status'])
       67  
       68      # Define values for display with common error cases.
       69:     # @@TODO: This should really be a separate mixin.  Needs fleshing out.
       70      def errorvalues(self, status, reason, message):
       71          return (


### wf4ever-ro-manager/src/roweb/rowebservices.py:

      146      log.info("Evaluate RO %s, minim %s, target %s, purpose %s"%(RO,minim,target,purpose))
      147      # create rometa object
      148:     # @@TODO: use proper configuration and credentials
      149      ROparse   = urlparse.urlparse(RO)
      150      rosrs_uri = (ROparse.scheme or "http") + "://" + (ROparse.netloc or "localhost:8000") + "/"


### wf4ever-ro-manager/src/roweb/TrafficLightReports.py:

       55  #   minim   URI of minim model for which evaluation has been performed
       56  #
       57: # @@TODO:
       58  # Consider refactoring this to follow the report/altreport pattern used for
       59  # generating result label text
   ..
      249  #   modeluri  URI of Minim model defining the evaluated checklist
      250  #
      251: # @@TODO: add sequence to minim model for output ordering of checklist items
      252  #
      253  EvalChecklistJson = (
  ...
      465  #   modeluri  URI of Minim model defining the evaluated checklist
      466  #
      467: # @@TODO: add sequence to minim model for output ordering of checklist items
      468  #
      469  EvalChecklistHtml = (


### wf4ever-ro-manager/src/rocommand/ROSRS_Session.py:

      147          if status == 409:
      148              return (status, reason, None, data)
      149:         #@@TODO: Create annotations for title, creator, date??
      150          raise self.error("Error creating RO", "%03d %s"%(status, reason))
      151  
  ...
      421          returns: (status, reason)
      422          """
      423:         assert False, "@@TODO Not fully implemented - need to GET current annotation and extract annotated resource to resuri"
      424          (status, reason) = self.updateROAnnotation(rouri, annuri, resuri, bodyuri)
      425          return (status, reason)
  ...
      437                  "%03d %s (%s)"%(status, reason, str(rouri)))
      438          for (a,p) in manifest.subject_predicates(object=resuri):
      439:             # @@TODO: in due course, remove RO.annotatesAggregatedResource?
      440              if p in [AO.annotatesResource,RO.annotatesAggregatedResource]:
      441                  yield a
  ...
      457                  "%03d %s (%s)"%(status, reason, str(rouri)))
      458          for (a,p) in manifest.subject_predicates(object=resuri):
      459:             # @@TODO: in due course, remove RO.annotatesAggregatedResource?
      460              if p in [AO.annotatesResource,RO.annotatesAggregatedResource]:
      461                  yield manifest.value(subject=a, predicate=AO.body)
  ...
      521  
      522      def copyRO(self, oldrouri, slug):
      523:         assert False, "@@TODO"
      524          return (status, reason, copyuri)
      525          # copyuri ->  Deferred(oldrouri, rotype, rostatus, newrouri)
      526  
      527      def cancelCopyRO(self, copyuri):
      528:         assert False, "@@TODO"
      529          return (status, reason)
      530  
      531      def updateROStatus(self, rouri, rostatus):
      532:         assert False, "@@TODO"
      533          return (status, reason, updateuri)
      534  


## Documentation


### wf4ever-ro-manager/src/checklist/mkminim.md:

      250  which are replaced by values from matched queries, or other values.  The exact values availabl;e for substitution vary with the rule type, but in the case of <b>ForEach:</b> rules, the query variables from a query match are available to a corresponding <b>Fail:</b> message.
      251  
      252: @@TODO - list other message substitution variables
      253  
      254  


## Refactoring


### wf4ever-ro-manager/src/iaeval/ro_eval_minim.py:

       30  
       31  def doQuery(rometa, queryPattern, queryVerb=None, resultMod="", queryPrefixes=None, initBindings=None):
       32:     # @@TODO - factor out query construction from various places below to use this
       33      querytemplate = (make_sparql_prefixes(queryPrefixes or [])+
       34          """
   ..
      131          log.info("evaluate: %s %s %s"%(r['level'],str(r['uri']),r['seq']))
      132          if 'datarule' in r:
      133:             # @@TODO: factor to separate function?
      134              #         (This is a deprecated form, as it locks the rule to a particular resource)
      135              satisfied = rometa.roManifestContains( (rouri, ORE.aggregates, r['datarule']['aggregates']) )
  ...
      137              log.debug("- %s: %s"%(repr((rouri, ORE.aggregates, r['datarule']['aggregates'])), satisfied))
      138          elif 'softwarerule' in r:
      139:             # @@TODO: factor to separate function
      140              cmnd = r['softwarerule']['command']
      141              resp = r['softwarerule']['response']
  ...
      240          query = querytemplate%queryparams
      241          log.debug(" - forall query: "+query)
      242:         ### @@TODO: Why is this failing?
      243          # resp  = rometa.queryAnnotations(query, initBindings=constraintbinding)
      244          resp  = rometa.queryAnnotations(query)
  ...
      255                      simplebinding[str(k)] = str(binding[k])
      256                      simplebinding['_count'] = len(resp)
      257:                     # @@TODO remove this when rdflib bug resolved 
      258                      if str(k) in ['if', 'of'] and str(binding[k])[:5] not in ["file:","http:"]:
      259                          # Houston, we have a problem...



### wf4ever-ro-manager/src/rocommand/ro.py:

       42          status = ro_command.check_command_args(progname, options, args)
       43      if status != 0: return status
       44:     #@@TODO: refactor to use command/usage table in rocommand for dispatch
       45      if args[1] == "help":
       46          status = ro_command.help(progname, args)
   ..
      186      Returns exit status.
      187      """
      188:     # @@TODO: robase is ignored: remove parameter here and from all calls
      189      (options, args) = parseCommandArgs(argv)
      190      if not options or options.debug:


### wf4ever-ro-manager/src/rocommand/ro_annotation.py:

      302      (predicate,valtype) = getAnnotationByName(ro_config, attrname)
      303      val         = attrvalue and makeAnnotationValue(ro_config, attrvalue, valtype)
      304:     #@@TODO refactor common code with getRoAnnotations, etc.
      305      add_annotations = []
      306      remove_annotations = []
  ...
      354      subject     = ro_manifest.getComponentUri(ro_dir, rofile)
      355      (predicate,valtype) = getAnnotationByName(ro_config, attrname)
      356:     #@@TODO refactor common code with getRoAnnotations, etc.
      357      for ann_node in ro_graph.subjects(predicate=RO.annotatesAggregatedResource, object=subject):
      358          ann_uri   = ro_graph.value(subject=ann_node, predicate=AO.body)
  ...
      391      subject     = ro_manifest.getComponentUri(ro_dir, rofile)
      392      log.debug("getFileAnnotations: %s"%str(subject))
      393:     #@@TODO refactor common code with getRoAnnotations, etc.
      394      for ann_node in ro_graph.subjects(predicate=RO.annotatesAggregatedResource, object=subject):
      395          ann_uri   = ro_graph.value(subject=ann_node, predicate=AO.body)
  ...
      409      log.debug("getAllAnnotations %s"%str(ro_dir))
      410      ro_graph    = ro_manifest.readManifestGraph(ro_dir)
      411:     #@@TODO refactor common code with getRoAnnotations, etc.
      412      for (ann_node, subject) in ro_graph.subject_objects(predicate=RO.annotatesAggregatedResource):
      413          ann_uri   = ro_graph.value(subject=ann_node, predicate=AO.body)
  ...
      428      Returns a graph node for the supplied type and value
      429      """
      430:     #@@TODO: construct appropriately typed RDF literals
      431      if atype == "resource":
      432          return rdflib.URIRef(getResourceNameString(ro_config, aval))
  ...
      443      atype is one of "string", "resurce", ...
      444      """
      445:     #@@TODO: deal with appropriately typed RDF literals
      446      if atype == "resource" or isinstance(aval,rdflib.URIRef):
      447          return '<' + str(aval) + '>'


### wf4ever-ro-manager/src/rocommand/ro_command.py:

      303              raise
      304      # Create manifest file
      305:     # @@TODO: create in-memory graph and serialize that
      306      manifestfilename = os.path.join(manifestdir, ro_settings.MANIFEST_FILE)
      307      log.debug("manifestfilename: " + manifestfilename)
  ...
      371          print "  uri:         %(rouri)s" % rodict
      372      print "  description: %(rodescription)s" % rodict
      373:     # @@TODO: add ROEVO information
      374      return 0
      375  


### wf4ever-ro-manager/src/rocommand/ro_namespaces.py:

       49  RO = makeNamespace(ro, 
       50              [ "ResearchObject", "AggregatedAnnotation"
       51:             , "annotatesAggregatedResource" # @@TODO: deprecated
       52              ])
       53  ROEVO = makeNamespace(roevo, 


### wf4ever-ro-manager/src/rocommand/ro_uriutils.py:

       85          # Pick out elements of response
       86          islive = (status >= 200) and (status <= 299)
       87:     # Original logic @@TODO remove this
       88      if 0:
       89          hc = ROSRS_Session.ROSRS_Session(uriref)


## Tests


### wf4ever-ro-manager/src/iaeval/test/TestEvalChecklist.py:

      380          return
      381  
      382:     # @@TODO Add test cases for software environment rule pass/fail, based on previous
      383      def annotateWfRo(self, testbase, rodir):
      384          """
  ...
      508          return
      509      
      510:     # @@TODO Add test cases for liveness test
      511  
      512      def testEvaluateMissing(self):



### wf4ever-ro-manager/src/iaeval/test/test-simple-wf/docs/UserRequirements-gen.json:

      256                  ], 
      257                  "comment": [
      258:                     "@@TODO: reworded, check"
      259                  ], 
      260                  "require": "to embed (links to?) other\u2019s publications in my working notes", 
  ...
      312                  ], 
      313                  "comment": [
      314:                     "@@TODO: What is meant here by \u201csemantic models\u201d?"
      315                  ], 
      316                  "require": "to annotate experimental results using semantic models", 
  ...
      477                      "", 
      478                      "", 
      479:                     "@@TODO: how does providing content help here?"
      480                  ], 
      481                  "require": "to provide content", 
  ...
      721                  ], 
      722                  "comment": [
      723:                     "@@TODO: or reputation of their creator?"
      724                  ], 
      725                  "require": "to find workflows according to their reputation", 


### wf4ever-ro-manager/src/rocommand/test/TestAnnotations.py:

      128  
      129      def testAnnotateKeywords(self):
      130:         self.annotateTest("keywords", "foo,bar", DCTERMS.subject, "foo,bar")  #@@TODO: make multiples
      131          return
      132  
  ...
      140  
      141      def testAnnotateCreated(self):
      142:         #@@TODO: use for creation date/time of file
      143          created = "2011-09-14T12:00:00"
      144          self.annotateTest("created", created, DCTERMS.created, created)
  ...
      159          return
      160  
      161:     # @@TODO: Test use of CURIE as type
      162  
      163      def annotateMultiple(self, rodir, rofile, annotations):
  ...
      478      # Test display of annotations for entire RO
      479  
      480:     # @@TODO: Test annotations shown in RO listing
      481  
      482      # Sentinel/placeholder tests


### wf4ever-ro-manager/src/rocommand/test/TestAnnotationUtils.py:

      263          attrdict = {
      264              "type":         rdflib.Literal("Research Object"),
      265:             # @@TODO: handle lists "keywords":     ["test", "research", "object"],
      266              "description":  rdflib.Literal("Test research object"),
      267              "format":       rdflib.Literal("application/vnd.wf4ever.ro"),
  ...
      280          attrpropdict = {
      281              "type":         DCTERMS.type,
      282:             # @@TODO "keywords":     DCTERMS.subject,
      283              "description":  DCTERMS.description,
      284              "format":       DCTERMS.format,


### wf4ever-ro-manager/src/rocommand/test/TestROMetadata.py:

      101          attrdict = {
      102              "type":         rdflib.Literal("Research Object"),
      103:             # @@TODO: handle lists "keywords":     ["test", "research", "object"],
      104              "description":  rdflib.Literal("Test research object"),
      105              "format":       rdflib.Literal("application/vnd.wf4ever.ro"),
  ...
      116          attrpropdict = {
      117              "type":         DCTERMS.type,
      118:             # @@TODO "keywords":     DCTERMS.subject,
      119              "description":  DCTERMS.description,
      120              "format":       DCTERMS.format,


### wf4ever-ro-manager/src/rocommand/test/TestROSRS_Session.py:

      148          self.assertEqual(reason, "OK")
      149          self.assertEqual(headers["content-type"], "application/zip")
      150:         # @@TODO test content of zip (data)?
      151          return
      152  
  ...
      492          self.assertIn(bodyuri1, buris1)
      493          # Update annotation using external body reference
      494:         # @@TODO - this doesn't check that old annotation is removed.
      495:         # @@TODO - currently, update is not fully implemented (2013-05).
      496          bodyuri2 = rdflib.URIRef("http://example.org/ext/ann2.rdf")
      497          (status, reason, annuri) = self.rosrs.createROAnnotationExt(rouri, resuri, bodyuri2)


### wf4ever-ro-manager/src/roweb/test/TestRdfReport.py:

      624            , '''<span class="testresult">minimally satisfies</span> checklist for'''
      625            , '''<span class="testpurpose">Runnable</span>.'''
      626:           # , '''<p>This Research Object @@TODO.</p>'''
      627            , '''</th>'''
      628            , '''</tr>'''

