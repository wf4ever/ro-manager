#!/bin/bash
#
# RO manager sample script
#

ROBASE="myworkspace"

echo "--------"

./ro config -v \
  -b $ROBASE \
  -r http://sandbox.wf4ever-project.org/rosrs5 \
  -t "47d5423c-b507-4e1c-8" 

echo "--------"

./ro checkout -v 219 

echo "--------"

touch $ROBASE/219/file1.txt

echo "touched file1.txt"

echo "`date`: This line is appended" >> $ROBASE/219/file2.txt

echo "appended a line to file2.txt"

echo "--------"

./ro push -v

# End.
