#!/bin/bash
#
# RO manager checklist sample script
#

ROURI="<RO>"        # URI of RO to evaluate
RESURI="."          # URI of target resource (relative to RO)

ro evaluate checklist --debug -v -d $ROURI -a simple-requirements-minim.rdf "Runnable" $RESURI

#echo "--------"

# End.
