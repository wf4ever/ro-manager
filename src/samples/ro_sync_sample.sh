#!/bin/bash
#
# RO manager sample script for RODL interactions
#

ROBASE="robase"

mkdir -p $ROBASE

echo "--------"

ro config -v \
  -b $ROBASE \
  -r http://sandbox.wf4ever-project.org/rosrs5 \
  -t "47d5423c-b507-4e1c-8" \
  -n "Test User" \
  -e "user@example.com"

echo "--------"

ro checkout -v -d $ROBASE 219 

echo "--------"

touch $ROBASE/219/file1.txt

echo "touched file1.txt"

echo "--------"

ro push -v -d $ROBASE/219

# End.
