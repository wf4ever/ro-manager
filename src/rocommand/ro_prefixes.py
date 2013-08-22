# ro_prefixes.py

"""
Central list of prefixes commonly used with ROs
"""

prefixes = (
    [ ("rdf",       "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    , ("rdfs",      "http://www.w3.org/2000/01/rdf-schema#")
    , ("owl",       "http://www.w3.org/2002/07/owl#")
    , ("xml",       "http://www.w3.org/XML/1998/namespace")
    , ("xsd",       "http://www.w3.org/2001/XMLSchema#")
    , ("rdfg",      "http://www.w3.org/2004/03/trix/rdfg-1/")
    , ("ro",        "http://purl.org/wf4ever/ro#")
    , ("roevo",     "http://purl.org/wf4ever/roevo#")
    , ("roterms",   "http://purl.org/wf4ever/roterms#")
    , ("wfprov",    "http://purl.org/wf4ever/wfprov#")
    , ("wfdesc",    "http://purl.org/wf4ever/wfdesc#")
    , ("wf4ever",   "http://purl.org/wf4ever/wf4ever#")
    , ("ore",       "http://www.openarchives.org/ore/terms/")
    , ("ao",        "http://purl.org/ao/")
    , ("dcterms",   "http://purl.org/dc/terms/")
    , ("dc",        "http://purl.org/dc/elements/1.1/")
    , ("foaf",      "http://xmlns.com/foaf/0.1/")
    , ("minim",     "http://purl.org/minim/minim#")
    , ("result",    "http://www.w3.org/2001/sw/DataAccess/tests/result-set#")
    ])

extra_prefixes =  (
    [ ("",          "http://example.org/")
    ])

def make_turtle_prefixes(extra_prefixes=[]):
    return"\n".join([ "@prefix %s: <%s> ."%p for p in prefixes+extra_prefixes ]) + "\n\n"

def make_sparql_prefixes(extra_prefixes=[]):
    return"\n".join([ "PREFIX %s: <%s>"%p for p in prefixes+extra_prefixes ]) + "\n\n"

turtle_prefixstr = make_turtle_prefixes(extra_prefixes)
sparql_prefixstr = make_sparql_prefixes(extra_prefixes)

prefix_dict = dict(prefixes)

# from rocommand.ro_prefixes import prefixes, prefix_dict, make_turtle_prefixes, make_sparql_prefixes, sparql_prefixstr

