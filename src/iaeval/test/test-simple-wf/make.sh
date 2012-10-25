#!/bin/bash
#
# RO manager script
#

RONAME="test-wf-requirements"
TESTRO="../robase/$RONAME"

echo "--------"

$RO config -v \
  -b $ROPATH \
  -r ROSRS_URI \
  -t "ROSRS_ACCESS_TOKEN" \
  -n "Test user" \
  -e "testuser@example.org"

rm .ro/*

$RO create -v "Simple requirements RO" -d $TESTRO -i $RONAME

$RO add -v -a -d $TESTRO

echo "--------"

$RO status -v -d $TESTRO

echo "--------"

$RO list -v -d $TESTRO

echo "--------"

$RO annotations

echo "--------"

$RO annotate -v $TESTRO/simple-wf-wfdesc.rdf type "workflow-description"
$RO annotate -v $TESTRO/simple-wf-minim.rdf type "minim"

$RO annotate -v docs/mkjson.sh -g $TESTRO/simple-requirements-wfdesc.rdf

$RO annotations

echo "--------"

# End.
