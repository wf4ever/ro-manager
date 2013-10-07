#!/bin/bash
HOST=http://localhost:8080    # Service endpoint URI

# $1 = RO to evaluate
# $2 = Minim to use (default runnable)
ROURI="${1:-http://sandbox.wf4ever-project.org/rodl/ROs/simple-requirements/}"
MINIM="${2:-http://sandbox.wf4ever-project.org/rodl/ROs/simple-requirements/checklist-runnable.rdf}"

echo "==== ROURI: $ROURI"
echo "==== MINIM: $MINIM"

# Retrieve service description and extract template

echo "==== Retrieve URI template for evaluate checklist ===="
TEMPLATE=`curl -H "accept: text/turtle" $HOST/ | sed -n 's/^.*roe:checklist[ ]*"\([^"]*\)".*$/\1/p'`
echo "==== Template: <$TEMPLATE>"

# URI template expansion

echo "==== Request URI-template expansion ===="
cat >sample-params.txt <<END
{
  "template": "$TEMPLATE",
  "params":
  {
    "RO": "$ROURI",
    "minim": "$MINIM",
    "purpose": "Runnable"
  }
}
END

EVALURI=$HOST`curl -X POST --data @sample-params.txt $HOST/uritemplate`

echo "==== URI: $EVALURI"

# Evaluation results with URI parameters:

echo "==== Request evaluation result with parameters, as RDF/Turtle ===="
curl -H "accept: text/turtle" $EVALURI

# echo "==== Request evaluation result with parameters, as RDF/XML ===="
# curl -H "accept: application/rdf+xml" $EVALURI

# End.
