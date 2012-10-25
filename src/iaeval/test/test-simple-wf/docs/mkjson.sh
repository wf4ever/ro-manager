#!/bin/bash
#
# Make JSON from local CSV
#

which lpod-show.py >/dev/null
if [[ "$?" != "0" ]]; then
    echo "$0: This script needs lpod installed - see http://lpod-project.org/"
    echo "    lpod can be installed using apt-get on on Ubuntu Linux as lpod-python"
    exit 1
fi

for f in UserRequirements-astro UserRequirements-bio UserRequirements-gen ; do
    lpod-show.py ../data/$f.ods >$f.csv 
    echo "python ../python/ReadCSV.py $f"
    python ../python/ReadCSV.py $f
done

exit 0

# End.
