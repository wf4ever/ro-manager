#!/bin/bash
#
# RO manager sample script
#

ROBASE="/usr/workspace/"
RO="/usr/workspace/wf4ever-ro-manager/src/ro"

echo "--------"

$RO config -v \
  -b $ROBASE \
  -r http://sandbox.wf4ever-project.org/rosrs3 \
  -u "OpenID-1318340111490" \
  -p "2ae55d36-de48-444c-a" \
  -n "Test user" \
  -e "testuser@example.org"

$RO create -v "Wf4Ever requirements" -d $ROBASE/wf4ever-requirements/ -i wf4ever-requirements

for F in \
    data/UserRequirements-astro.ods \
    data/UserRequirements-bio.ods   \
    data/UserRequirements-gen.ods   \
    data/TechRequirements-all.ods   \
    data/TechnicalFacets.ods
do
    $RO add -v -d $ROBASE/wf4ever-requirements/ $ROBASE/wf4ever-requirements/$F
done

$RO status -v -d $ROBASE/wf4ever-requirements

# $RO list -v -d $ROBASE/wf4ever-requirements


#echo "--------"

#./ro annotate -v $ROBASE/test-create-RO/subdir1/subdir1-file.txt title "subdir1-file.txt title"

#./ro annotations -v $ROBASE/test-create-RO/subdir1/subdir1-file.txt

#echo "--------"

#./ro annotate -v $ROBASE/test-create-RO/subdir2/subdir2-file.txt type        "subdir2-file.txt type"
#./ro annotate -v $ROBASE/test-create-RO/subdir2/subdir2-file.txt keywords    "subdir2-file.txt foo,bar"
#./ro annotate -v $ROBASE/test-create-RO/subdir2/subdir2-file.txt description "subdir2-file.txt description\nline 2"
#./ro annotate -v $ROBASE/test-create-RO/subdir2/subdir2-file.txt format      "subdir2-file.txt format"
#./ro annotate -v $ROBASE/test-create-RO/subdir2/subdir2-file.txt title       "subdir2-file.txt title"
#./ro annotate -v $ROBASE/test-create-RO/subdir2/subdir2-file.txt created     "20110914T12:00:00"

#./ro annotations -v $ROBASE/test-create-RO/subdir2/subdir2-file.txt

#echo "--------"

# End.

