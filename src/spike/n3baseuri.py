# Testing N3/Turtle parsing with no @base in source.

import rdflib

testdata = """
# @base <http://example.org/> .
@prefix : <> .
:hello :turtle :world .
"""

gr = rdflib.Graph()
gr.parse(data=testdata, publicID="http://example.org/", format="n3")
print gr.serialize(format="n3")

# Did that work?
