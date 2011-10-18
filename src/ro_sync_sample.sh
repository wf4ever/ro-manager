#!/bin/bash
#
# RO manager sample script
#

ROBASE="myworkspace"

echo "--------"

./ro config -v \
  -b $ROBASE \
  -r http://sandbox.wf4ever-project.org/rosrs3 \
  -u "OpenID-1318340111490" \
  -p "2ae55d36-de48-444c-a" \
  -n "Test user" \
  -e "testuser@example.org"

echo "--------"

./ro checkout A_sample_pack -v 

echo "--------"

touch $ROBASE/a_sample_pack/file1.txt

echo "touched file1.txt"

echo "`date`: This line is appended" >> $ROBASE/A_sample_pack/file2.txt

echo "appended a line to file2.txt"

echo "--------"

./ro push -v

# End.
