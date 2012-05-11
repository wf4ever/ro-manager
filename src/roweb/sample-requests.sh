#!/bin/bash

HOST=${1:-"localhost:8080"}

# Service document
echo "==== Request service description with default content type ===="
curl http://$HOST/
echo "==== Request service description as HTML ===="
curl -H "accept: text/html" http://$HOST/
echo "==== Request service description as RDF/Turtle ===="
curl -H "accept: text/turtle" http://$HOST/
echo "==== Request service description as RDF/XML ===="
curl -H "accept: application/rdf+xml" http://$HOST/

# Evaluation results
# (will need changing to include parameters)
curl http://$HOST/evaluate/checklist
echo "==== Request evaluation result as RDF/Turtle ===="
curl -H "accept: text/turtle" http://$HOST/evaluate/checklist
echo "==== Request evaluation result as RDF/XML ===="
curl -H "accept: application/rdf+xml" http://$HOST/evaluate/checklist

# URI template expansion
echo "==== Request URI-template expansion ===="
curl -X POST --data @- http://$HOST/uritemplate <<END
{
  "template": "/evaluate/checklist{?RO,minim,target,purpose}",
  "params":
  {
    "RO": "http://sandbox.example.org/ROs/myro",
    "minim": "http://another.example.com/minim/repeatable.rdf",
    "purpose": "Runnable"
  }
}
END

echo "===="

