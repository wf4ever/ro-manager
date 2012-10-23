#!/bin/bash
#
# RO manager sample script for RODL interactions
#

ROBASE="robase"
TESTRO="../rocommand/test/data"

echo "--------"
echo "1. create $ROBASE"

mkdir -p $ROBASE

echo "--------"
echo "2. configure RO manager"

ro config -v \
  -b $ROBASE \
  -r http://sandbox.wf4ever-project.org/rodl/ROs/ \
  -t "b1b286f1-24cf-4a86-97b1-208513d403ee" \
  -n "Test User" \
  -e "user@example.com"

echo "--------"
echo "3. create a test RO"

mkdir  $ROBASE/test-create-RO
rm -rf $ROBASE/test-create-RO/.ro
cp -r  $TESTRO/ro-test-1/* $ROBASE/test-create-RO

ro create -v "Test Create RO" -d $ROBASE/test-create-RO -i RO-id-testCreate
ro add -v -a -d $ROBASE/test-create-RO $ROBASE/test-create-RO
ro annotate -v $ROBASE/test-create-RO/subdir1/subdir1-file.txt title "subdir1-file.txt title"
ro annotations -v $ROBASE/test-create-RO/subdir1/subdir1-file.txt

echo "--------"
echo "4. push RO to RODL"

ro push -v -d $ROBASE/test-create-RO

echo "--------"
echo "5. remove RO from $ROBASE"

rm -rf $ROBASE/test-create-RO

echo "--------"
echo "6. download RO from RODL"

ro checkout -v -d $ROBASE test-create-RO 

# End.
