#!/bin/bash
#
# RO manager sample script
#

ROBASE="rocommand/test/robase"
TESTRO="rocommand/test/data"

echo "--------"

./ro config -v \
  -b $ROBASE \
  -r http://calatola.man.poznan.pl/robox/dropbox_accounts/1/ro_containers/2 \
  -n "Test user" \
  -p "d41d8cd98f00b204e9800998ecf8427e" \
  -e "testuser@example.org"

echo "--------"

mkdir $ROBASE/test-create-RO
cp -r $TESTRO/ro-test-1/* $ROBASE/test-create-RO

./ro create -v "Test Create RO" -d $ROBASE/test-create-RO -i RO-id-testCreate

./ro status -v -d $ROBASE/test-create-RO

./ro list -v -d $ROBASE/test-create-RO

echo "--------"

./ro annotate -v $ROBASE/test-create-RO/subdir1/subdir1-file.txt title "subdir1-file.txt title"

./ro annotations -v $ROBASE/test-create-RO/subdir1/subdir1-file.txt

echo "--------"

./ro annotate -v $ROBASE/test-create-RO/subdir2/subdir2-file.txt type        "subdir2-file.txt type"
./ro annotate -v $ROBASE/test-create-RO/subdir2/subdir2-file.txt keywords    "subdir2-file.txt foo,bar"
./ro annotate -v $ROBASE/test-create-RO/subdir2/subdir2-file.txt description "subdir2-file.txt description\nline 2"
./ro annotate -v $ROBASE/test-create-RO/subdir2/subdir2-file.txt format      "subdir2-file.txt format"
./ro annotate -v $ROBASE/test-create-RO/subdir2/subdir2-file.txt title       "subdir2-file.txt title"
./ro annotate -v $ROBASE/test-create-RO/subdir2/subdir2-file.txt created     "20110914T12:00:00"

./ro annotations -v $ROBASE/test-create-RO/subdir2/subdir2-file.txt

echo "--------"

# End.
