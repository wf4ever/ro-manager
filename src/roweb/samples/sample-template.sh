#!/bin/bash

HOST=${1:-"localhost:8080"}

#echo $HOST

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
