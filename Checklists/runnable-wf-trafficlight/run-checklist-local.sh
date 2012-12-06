#!/bin/bash
#
# RO manager checklist sample script, using local copies of ROs
#

RO=ro
RO=/usr/workspace/wf4ever-ro-manager/romenv/bin/ro
RO=/usr/workspace/wf4ever-ro-manager/src/ro

# URI if minim file (needs to be absolute URI)
MINIMURI="file://`pwd -P`/checklist.rdf"

# RO Base URI
ROBASE="/usr/workspace/wf4ever-ro-catalogue/v0.1"

# URI of RO to evaluate
ROREF="simple-requirements"

# URI of target resource (relative to RO)
RESURI="."

echo "--------"

# ROURIS="http://sandbox.wf4ever-project.org/rodl/ROs/simple-requirements/ \
#        http://sandbox.wf4ever-project.org/rodl/ROs/wf74ph/               \
#        http://sandbox.wf4ever-project.org/rodl/ROs/wf74-repeat-fail1/    \
#        http://sandbox.wf4ever-project.org/rodl/ROs/wf74-repeat-fail2/"

ROURIS="$ROBASE/$ROREF/"

for ROURI in $ROURIS; do

    #ro evaluate checklist --debug -v -d $ROURI -a $MINIMURI "Runnable" $RESURI
    echo "ro evaluate checklist -d $ROURI -a  $MINIMURI "Runnable" $RESURI"
    $RO evaluate checklist -a -d $ROURI $MINIMURI "Runnable" $RESURI
    $RO evaluate checklist -a -o RDFXML -d $ROURI $MINIMURI "Runnable" $RESURI >evalchecklistresult.rdf

    echo "--------"

done


# End.
