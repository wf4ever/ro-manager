#!/bin/bash

HOST=${1:-"localhost:8080"}

#echo $HOST

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
