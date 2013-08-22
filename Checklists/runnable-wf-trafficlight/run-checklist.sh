#!/bin/bash
#
# RO manager checklist sample script
#

# URI if minim file (needs to be absolute URI)
MINIMURI="file://`pwd -P`/checklist.rdf"

# URI of RO to evaluate
ROURI="http://sandbox.wf4ever-project.org/rodl/ROs/simple-requirements/"

# URI of target resource (relative to RO)
RESURI="."

echo "--------"

ROURIS="http://sandbox.wf4ever-project.org/rodl/ROs/simple-requirements/ \
       http://sandbox.wf4ever-project.org/rodl/ROs/wf74ph/               \
       http://sandbox.wf4ever-project.org/rodl/ROs/wf74-repeat-fail1/    \
       http://sandbox.wf4ever-project.org/rodl/ROs/wf74-repeat-fail2/"

ROURIS="http://sandbox.wf4ever-project.org/rodl/ROs/simple-requirements/"

for ROURI in $ROURIS; do

    #ro evaluate checklist --debug -v -d $ROURI -a $MINIMURI "Runnable" $RESURI
    echo "ro evaluate checklist -d $ROURI -a  $MINIMURI "Runnable" $RESURI"
    ro evaluate checklist -a -o RDFXML -d $ROURI $MINIMURI "Runnable" $RESURI | less

    echo "--------"

done


# End.
