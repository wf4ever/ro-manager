#!/bin/bash

HOST=localhost:8080

# URI template expansion
if 0; then
echo "==== Request URI-template expansion ===="
curl -X POST --data @- http://$HOST/uritemplate <<END
{
  "template": "/evaluate/checklist{?RO,minim,target,purpose}",
  "params":
  {
    "RO": "http://andros.zoo.ox.ac.uk/workspace/wf4ever-ro-catalogue/v0.1/simple-requirements/",
    "minim": "http://andros.zoo.ox.ac.uk/workspace/wf4ever-ro-catalogue/v0.1/simple-requirements/simple-requirements-minim.rdf",
    "purpose": "Runnable"
  }
}
END
fi

# Evaluation results with URI parameters:
echo "==== Request evaluation result with parameters, as RDF/Turtle ===="
curl -H "accept: text/turtle"  "http://$HOST/evaluate/checklist?RO=http%3A%2F%2Fandros.zoo.ox.ac.uk%2Fworkspace%2Fwf4ever-ro-catalogue%2Fv0.1%2Fsimple-requirements%2F&minim=http%3A%2F%2Fandros.zoo.ox.ac.uk%2Fworkspace%2Fwf4ever-ro-catalogue%2Fv0.1%2Fsimple-requirements%2Fsimple-requirements-minim.rdf&purpose=Runnable"
echo "==== Request evaluation result with parameters, as RDF/XML ===="
curl -H "accept: application/rdf+xml"  "http://$HOST/evaluate/checklist?RO=http%3A%2F%2Fandros.zoo.ox.ac.uk%2Fworkspace%2Fwf4ever-ro-catalogue%2Fv0.1%2Fsimple-requirements%2F&minim=http%3A%2F%2Fandros.zoo.ox.ac.uk%2Fworkspace%2Fwf4ever-ro-catalogue%2Fv0.1%2Fsimple-requirements%2Fsimple-requirements-minim.rdf&purpose=Runnable"

