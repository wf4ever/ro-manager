#!/bin/bash
#
# RO manager checklist sample script
#

source ../../ro.sh

RONAME="simple-requirements"
TESTRO="$ROPATH/$RONAME"

echo "--------"

$RO evaluate checklist --debug -v -d $TESTRO -a simple-requirements-minim.rdf "Runnable" $TESTRO/

echo "--------"

#$RO evaluate checklist -v -d $TESTRO -a simple-requirements-minim.rdf "Reviewable" $TESTRO/

echo "--------"

#$RO evaluate checklist -v -d $TESTRO -a simple-requirements-minim.rdf "Repeatable" $TESTRO/

echo "--------"

#./ro annotations -v $ROBASE/test-create-RO/subdir1/subdir1-file.txt

#echo "--------"

#echo "--------"

# End.
