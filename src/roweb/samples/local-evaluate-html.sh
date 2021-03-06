#!/bin/bash
HOST=http://localhost:8080    # Service endpoint URI

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
    "RO": "http://sandbox.wf4ever-project.org/rodl/ROs/simple-requirements/",
    "minim": "simple-requirements-minim.rdf",
    "purpose": "Runnable"
  }
}
END

EVALURI=$HOST`curl -X POST --data @sample-params.txt $HOST/uritemplate`

echo "==== GET $EVALURI"

# Evaluation results with URI parameters:

echo "==== Trafficlight result as HTML ===="
curl $EVALURI

# End.
