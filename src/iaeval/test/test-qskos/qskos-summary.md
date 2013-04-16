# qSKOS checking

From http://arxiv.org/pdf/1206.1339v1.pdf, section 3.

In the following analysis, I assume the SKOS thesaurus is presented as an annotation or annotations to the checklist evaluation process.

It appears that about half of the criteria (7-8) can be tested with existing Minim structures. The others will need some combination of extensions.

Three new features may help to cover the qSKOS requirements:

* compare result sets (@@consistency?)
* query external service or resource
* filter forall results on on namespace (of more generally on some; maybe this can be done in SPARQL?)

A reporting variation based on a forall:not-exists test is likely to be helpful.

Some form of Minim query chaining might make it easier to express some of the requirements (e.g. combining local queries with external resource tests).

Need to check liveness test handles redirections.


## Labeling and Documentation Issues

### Omitted or Invalid Language Tags

> SKOS defines a set of properties that link resources with RDF Literals, which are plain text natural language strings with an optional language tag. This includes the labeling properties rdfs:label, skos:prefLabel, skos:altLabel, skos:hiddenLabel and also SKOS documentation properties, such as skos:note and subproperties thereof. Literals should be tagged consistently [23], because omitting language tags or using nonstandardized, private language tags in a SKOS vocabulary could unintentionally limit the result set of language-dependent queries. A SKOS vocabulary can be checked for omitted and invalid language tags by iterating over all resources in IR and finding those that have labeling or documentation property relations to plain literals in LV with missing or invalid language tags, i.e., tags that are not defined in RFC3066 [Tags for the Identification of Languages](http://www.ietf.org/rfc/rfc3066.txt)

This will need a reference copy of RFC3066 language tags to be available.  If they are provided in an appropriate RDF format, and made accessible as an RO annotation, it is possible that the current Minim structure will be able to handle this check.


### Incomplete Language Coverage

> The set of language tags used by the literal values linked with a concept should be the same for all concepts. If this is not the case, appropriate actions like, e.g., splitting concepts or introducing scope notes should be taken by the creators. This is particularly important for applications that rely on internationalization and translation use cases. Affected concepts can be identified by first extracting the global set of language tags used in a vocabulary from all literal values in LV , which are attached to a concept in C. In a second iteration over all concepts, those having a set of language tags that is not equal to the global language tag set are returned.

This will need a way to compare the result-sets from different queries, which is beyond the current capability of Minim checklists.  I think it is also beyond the capability of MIM to express.


### Undocumented Concepts

> Svenonius [20] advocates the “inclusion of as much definition material as possible” and the SKOS Reference [13] defines a set of “documentation properties” intended to hold this kind of information. To identify all undocumented concepts, we iterate over all concepts in C and collect those that do not use any of these documentation properties.

This should be do-able using Minim checklists (a forall:exists query-based test).


### Label Conflicts

> The SKOS Primer [11] recommends that “no two concepts have the same preferred lexical label in a given language when they belong to the same concept scheme”. This issue could affect application scenarios such as auto-completion, which proposes labels based on user input. Although these extra cases are acceptable for some thesauri, we generalize the above recommendation and search for all concept pairs with their respective skos:prefLabel, skos:altLabel or skos:hiddenLabel property values meeting a certain similarity threshold defined by a function sim : LV × LV → [0, 1]. The default, built-in similarity function checks for case-insensitive string equality with a threshold equal to 1. Label conflicts can be found by iterating over all (authoritative) concept pairs AC × AC, applying sim to every possible label combination, and collecting those pairs with at least one label combination meeting or exceeding a specified similarity threshold. We handle this issue under the Closed World Assumption, because data on concept scheme membership may lack and concepts may be linked to concepts with similar labels in other vocabularies.

This is borderline possible using advanced SPARQL 1.1 queries.  More detailed exploration needed, assuming I can get SPARQL 1.1 support in the RO Manager checklist code.


## Structural Issues

### Orphan Concepts

> Orphan Concepts are motivated by the notion of “orphan terms” in the literature [8], i.e., terms without any associative or hierarchical relationships. Checking for such terms is common in thesaurus development and also suggested by [15]. Since SKOS is concept-centric, we understand an orphan concept as being a concept that has no semantic relation sr ∈ SR with any other concept. Although it might have attached lexical labels, it lacks valuable context information, which can be essential for retrieval tasks such as search query expansion. Orphan concepts in a SKOS vocabulary can be found by iterating over all elements in C and selecting those without any semantic relation to another concept in C.

This should be do-able with Minim (a forall:exists query-based test).


### Weakly Connected Components

> A vocabulary can be split into separate “clusters” because of incomplete data acquisition, deprecated terms, accidental deletion of relations, etc. This can affect operations that rely on navigating a connected vocabulary structure, such as query expansion or suggestion of related terms. Weakly connected components are identified by first creating an undirected graph that includes all non-orphan concepts (as defined above) as nodes and all semantic relations SR as edges. “Tarjan’s algorithm” [10] can then be applied to find all connected components, i.e., all sets of concepts that are connected together by (chains of) semantic relations.

This looks like something that would be difficult to accommodate within present Minim structiures.  I would look to using a specialist web service to do the “Tarjan’s algorithm” analysis, and then test the result of that in a Minim construct.


### Cyclic Hierarchical Relations

> Cyclic Hierarchical Relations is motivated by Soergel et al. [18] who suggest a “check for hierarchy cycles” since they “throw the program for a loop in the generation of a complete hierarchical structure”. Also Hedden [8], Harpring [6] and Aitchison et al. [2] argue that there exist common forms like, e.g., “generics-pecific”, “instance-of” or “whole-part” where cycles would be considered a logical contradiction. Cyclic relations can be found by constructing a graph with the set of nodes being C and the set of edges being all skos:broader relations.

This looks like difficult to accommodate within present Minim structures.  I would consider a specialist web service to do the cycle detection, and then test the result from that in a Minim construct.


### Valueless Associative Relations

> The ISO/DIS 25964-1 standard [1] suggests that terms that share a common broader term should not be related associatively if this relation is only justified by the fact that they are siblings. This is advocated by Hedden [8] and Aitchison et al. [2] who point out “the risk that thesaurus compilers may overload the thesaurus with valueless relationships”, having a negative effect on precision. This issue can be checked by identifying concept pairs C × C that share the same broader or narrower concept while also being associatively related by the property skos:related.

I think this is detectable using a forall:exists test, but may be easier to generate appropriate diagnostics if the reporting structures are revised (e.g. formulated as a not-exists test).


### Solely Transitively Related Concepts

> Two concepts that are explicitly related by skos:broaderTransitive and/or skos:narrowerTransitive can be regarded a quality issue because, according to [13], these properties are “not used to make assertions”. Transitive hierarchical relations in SKOS are meant to be inferred by the vocabulary consumer, which is reflected in the SKOS ontology by, for instance, skos:broader being a subproperty of skos:broaderTransitive. This issue can be detected by finding all concept pairs C × C that are directly related by skos:broaderTransitive and/or skos:narrowerTransitive properties but not by (chains of) skos:broader and skos:narrower subproperties.

This should be do-able with Minim (an exists query-based test), but may be easier to generate appropriate diagnostics if the reporting structures are revised (e.g. formulated as a not-exists test).


### Omitted Top Concepts

> The SKOS model provides concept schemes, which are a facility for grouping related concepts. This helps to provide “efficient access” [11] and simplifies orientation in the vocabulary. In order to provide entry points to such a group of concepts, one or more concepts can be marked as top concepts. Omitted top concepts can be detected by iterating over all concept schemes in CS and collecting those that do not occur in relations established by the properties skos:hasTopConcept or skos:topConceptOf.

This should be do-able with Minim (a forall:exists query-based test).


### Top Concept Having Broader Concepts

> Allemang et al. [3] propose to “not indicate any concepts internal to the tree as top concepts”, which means that top concepts should not have broader concepts. Affected resources are found by collecting all top concepts that are related to a resource via a skos:broader statement and not via skos:broadMatch—mappings are not part of a vocabulary’s “intrinsic” definition and a top concept in one vocabulary may perfectly have a broader concept in another vocabulary.

This should be do-able with Minim (a forall:exists query-based test), but may be easier to generate appropriate diagnostics if the reporting structures are revised (e.g. formulated as a not-exists test).


## Linked Data Specific Issues

### Missing In-Links

> When vocabularies are published on the Web, SKOS concepts become linkable resources. Estimating the number of in-links and identifying the concepts without any in-links, can indicate the importance of a concept. We estimate the number of in-links by iterating over all elements in AC and querying the [Sindice](http://sindice.com/) SPARQL endpoint for triples containing the concept’s URI in the object part. Empty query results are indicators for missing in-links.

>http://sindice.com/ indexes the Web of Data, which is composed of pages with semantic markup in RDF, RDFa, Microformats, or Microdata. Currently [June 2012?] it covers approximately 230M documents with over 11 billion triples.

This would require making namespaces visible (@@really?) to Minim checklist items, _and_ providing a mechanism to use queries against external SPARQL services.


### Missing Out-Links

> SKOS concepts should also be linked with other related concepts on the Web, “enabling seamless connections between data sets”[7]. Similar to Missing In-Links, this issue identifies the set of all authoritative concepts that have no out-links. It can be computed by iterating over all elements in AC and returning those that are not linked with any non-authoritative resource.

Need to clarify what is meant by "non-authoritative resource".


### Broken Links

> As we discussed in detail in our earlier work [17], this issue is caused by vocabulary resources that return HTTP error responses or no response when being dereferenced. An erroneous HTTP response in that case can be defined as a response code other than 200 after possible redirections. Just as in the “document” Web, these “broken links” hinder navigability also in the Linked Data Web and and should therefore be avoided. Broken links are detected by iterating over all resources in IR, dereferencing their HTTP URIs, following possible redirects, and including unavailable resources in the result set.

This looks like a Minim forall:liveness test.

I may need to check that Minim liveness test handles redirections.  Currently I'm not sure, but if it doesn't that's probably a bug in any case.


### Undefined SKOS Resources 

> The SKOS model is defined within the namespace http://www.w3.org/2004/02/skos/core#. However, some vocabularies use resources from within this namespace, which are unresolvable for two main reasons: vocabulary creators “invented” new terms within the SKOS namespace instead of introducing them in a separate namespace, or they use “deprecated” SKOS elements like skos:subject. Undefined SKOS resources can be identified by iterating over all resources in IR and returning those (i) that are contained in the list of deprecated resources or (ii) are identified by a URI in the SKOS namespace but are not defined in the current version of the SKOS ontology.

This would require making namespaces visible to Minim checklist items, _and_ providing a mechanism to use queries against external resources.  It also looks as if access to a list a deprecated SKOS names may be required (similar to language tags requirement),   With that, it might be possible to formulate this test as a forall:exists test, but may need some more selective structure (e.g. forall:filter-namespace:not-exists or forall:filter-namespace:not-exists:not-exists tests)


# References (from qSKOS paper)

1. ISO 25964-1: Information and documentation – Thesauri and interoperability with other vocabularies – Part 1: Thesauri for information retrieval. Norm, International Organization for Standardization (2011)
2. Aitchison, J., Gilchrist, A., Bawden, D.: Thesaurus construction and use: a prac- tical manual. Aslib IMI (2000)
3. Allemang, D., Hendler, J.: Semantic Web for the Working Ontologist: Effective Modeling in RDFS and OWL. Morgan Kaufmann (2011)
4. Batini, C., Cappiello, C., Francalanci, C., Maurino, A.: Methodologies for data quality assessment and improvement. ACM Computing Surveys 41(3), 16 (2009)
5. de Coronado, S., Wright, L.W., Fragoso, G., Haber, M.W., Hahn-Dantona, E.A.,
Hartel, F.W., Quan, S.L., Safran, T., Thomas, N., Whiteman, L.: The NCI The-
saurus quality assurance life cycle. J. Biomed. Inform. 42(3), 530–539 (2009)
6. Harpring, P.: Introduction to Controlled Vocabularies: Terminology for Art, Ar-
chitecture, and Other Cultural Works. Getty Publications, Los Angeles (2010)
7. Heath, T., Bizer, C.: Linked Data: Evolving the Web into a Global Data Space.
Morgan & Claypool (2011), http://linkeddatabook.com/
8. Hedden, H.: The accidental taxonomist. Information Today (2010)
9. Hogan, A., Harth, A., Passant, A., Decker, S., Polleres, A.: Weaving the pedantic
web. In: Proc. WWW2010 Workshop on Linked Data on the Web (LDOW) (2010)
10. Hopcroft, J.E., Tarjan, R.E.: Algorithm 447: efficient algorithms for graph manip-
ulation. Commun. ACM 16(6), 372–378 (1973)
11. Isaac, A., Summers, E.: SKOS Simple Knowledge Organization System Primer.
Working Group Note, W3C (2009), http://www.w3.org/TR/skos-primer/
12. Kless, D., Milton, S.: Towards quality measures for evaluating thesauri. Metadata
and Semantic Research pp. 312–319 (2010)
13. Miles, A., Bechhofer, S.: SKOS Simple Knowledge Organization System Reference.
Recommendation, W3C (2009), http://www.w3.org/TR/skos-reference/
14. Nagy, H., Pellegrini, T., Mader, C.: Exploring structural differences in thesauri for
SKOS-based applications. pp. 187–190. I-Semantics ’11, ACM (2011)
15. NISO: ANSI/NISO Z39.19 - Guidelines for the Construction, Format, and Man-
agement of Monolingual Controlled Vocabularies (2005)
16. Pipino, L., Lee, Y., Wang, R.: Data quality assessment. Commun. ACM 45(4),
211–218 (2002)
17. Popitsch, N.P., Haslhofer, B.: DSNotify: handling broken links in the web of data.
In: Proc. 19th Int. Conf. World Wide Web (WWW). pp. 761–770 (2010)
18. Soergel, D.: Thesauri and ontologies in digital libraries: tutorial. In: Proc. 2nd
Joint Conf. on Digital libraries (JCDL) (2002)
19. Spero, S.: LCSH is to Thesaurus as Doorbell is to Mammal: Visualizing Structural
Problems in the Library of Congress Subject Headings. In: Proc. Int. Conf. on
Dublin Core and Metadata Applications (DC) (2008)
20. Svenonius, E.: Definitional approaches in the design of classification and thesauri
and their implications for retrieval and for automatic classification. In: Proc. Int.
Study Conference on Classification Research. pp. 12–16 (1997)
21. Svenonius, E.: Design of controlled vocabularies. Encyclopedia of Library and In-
formation Science 45, 822–838 (2003)
22. Van Assem, M., Malais ́e, V., Miles, A., Schreiber, G.: A method to convert thesauri
to SKOS. In: Proc. 3rd European Semantic Web Conf. (ESWC). pp. 95–109 (2006)
23. Vrandecic, D.: Ontology Evaluation. Ph.D. thesis, KIT, Fakult ̈at fu ̈r
Wirtschaftswissenschaften, Karlsruhe (2010)
