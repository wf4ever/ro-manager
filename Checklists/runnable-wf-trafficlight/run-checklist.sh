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

#ro evaluate checklist --debug -v -d $ROURI -a $MINIMURI "Runnable" $RESURI
echo "ro evaluate checklist -d $ROURI -a  $MINIMURI "Runnable" $RESURI"
ro evaluate checklist -d $ROURI -a  $MINIMURI "Runnable" $RESURI

echo "--------"

# URI of RO to evaluate
ROURI="http://sandbox.wf4ever-project.org/rodl/ROs/wf74ph/"

# URI of target resource (relative to RO)
RESURI="."

#ro evaluate checklist --debug -v -d $ROURI -a $MINIMURI "Runnable" $RESURI
echo "ro evaluate checklist -d $ROURI -a  $MINIMURI "Runnable" $RESURI"
ro evaluate checklist -d $ROURI -a  $MINIMURI "Runnable" $RESURI

echo "--------"

# URI of RO to evaluate
ROURI="http://sandbox.wf4ever-project.org/rodl/ROs/wf74-repeat-fail1/"

# URI of target resource (relative to RO)
RESURI="."

#ro evaluate checklist --debug -v -d $ROURI -a $MINIMURI "Runnable" $RESURI
echo "ro evaluate checklist -d $ROURI -a  $MINIMURI "Runnable" $RESURI"
ro evaluate checklist -d $ROURI -a  $MINIMURI "Runnable" $RESURI

echo "--------"

# URI of RO to evaluate
ROURI="http://sandbox.wf4ever-project.org/rodl/ROs/wf74-repeat-fail2/"

# URI of target resource (relative to RO)
RESURI="."

#ro evaluate checklist --debug -v -d $ROURI -a $MINIMURI "Runnable" $RESURI
echo "ro evaluate checklist -d $ROURI -a  $MINIMURI "Runnable" $RESURI"
ro evaluate checklist -d $ROURI -a  $MINIMURI "Runnable" $RESURI

echo "--------"

# End.
