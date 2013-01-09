#!/bin/bash
#HOST=http://andros.zoo.ox.ac.uk:8080    # Service endpoint URI
HOST=http://sandbox.wf4ever-project.org/roevaluate   # Service endpoint URI

# Retrieve service description and extract template

echo "==== Retrieve URI template for evaluate checklist ===="
TEMPLATE=`curl -H "accept: text/turtle" $HOST/ | sed -n 's/^.*roe:trafficlight_html[ ]*"\([^"]*\)".*$/\1/p'`
echo "==== Template: <$TEMPLATE>"

# URI template expansion

echo "==== Request URI-template expansion ===="
cat >sample-params.txt <<END
{
  "template": "$TEMPLATE",
  "params":
  {
    "RO": "$1",
    "minim": "http://raw.github.com/wf4ever/ro-catalogue/master/v0.1/simple-requirements/checklist-runnable.rdf",
    "purpose": "Runnable"
  }
}
END

EVALURI=$HOST`curl -X POST --data @sample-params.txt $HOST/uritemplate`

echo "==== URI: $EVALURI"

# Evaluation results with URI parameters:

# echo "==== Request evaluation result with parameters, as RDF/Turtle ===="
# curl -H "accept: text/turtle" $EVALURI

echo "==== Request evaluation result with parameters, as RDF/XML ===="
#curl -H "accept: application/rdf+xml" $EVALURI

# End.
