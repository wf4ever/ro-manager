#!/bin/bash
#
# RO manager script
#

pushd ../robase
ROBASE=`pwd -P`
popd

RONAME="test-simple-wf"
TESTRO="$ROBASE/$RONAME"
RO="../../../ro"

echo "--------"

$RO config -v \
  -b ../robase \
  -r ROSRS_URI \
  -t "ROSRS_ACCESS_TOKEN" \
  -n "Test user" \
  -e "testuser@example.org"

rm -rf $TESTRO
mkdir $TESTRO
cp -rv . $TESTRO

$RO create -v "Simple requirements RO" -d $TESTRO -i $RONAME

$RO add -v -a -d $TESTRO

echo "--------"

$RO status -v -d $TESTRO

echo "--------"

$RO list -v -d $TESTRO

echo "--------"

$RO annotations -d $TESTRO

echo "--------"

$RO annotate -v $TESTRO/simple-wf-wfdesc.rdf rdf:type wfdesc:Workflow

$RO annotate -v $TESTRO/docs/mkjson.sh -g $TESTRO/simple-requirements-wfdesc.rdf

$RO annotations -d $TESTRO

echo "--------"

$RO evaluate checklist -a -d $TESTRO "simple-wf-minim.rdf" "Runnable" "."

# End.
