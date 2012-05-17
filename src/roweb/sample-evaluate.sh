#!/bin/bash
HOST=andros.zoo.ox.ac.uk:8080

# URI template expansion
echo "==== Request URI-template expansion ===="
cat >sample-params.txt <<END
{
  "template": "/evaluate/checklist{?RO,minim,target,purpose}",
  "params":
  {
    "RO": "http://andros.zoo.ox.ac.uk/workspace/wf4ever-ro-catalogue/v0.1/simple-requirements/",
    "minim": "simple-requirements-minim.rdf",
    "purpose": "Runnable"
  }
}
END

EVALURI=http://$HOST`curl -X POST --data @sample-params.txt http://$HOST/uritemplate`
echo "==== URI: $EVALURI"

# Evaluation results with URI parameters:
echo "==== Request evaluation result with parameters, as RDF/Turtle ===="
curl -H "accept: text/turtle" $EVALURI
echo "==== Request evaluation result with parameters, as RDF/XML ===="
curl -H "accept: application/rdf+xml" $EVALURI

# End.
