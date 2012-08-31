#! /bin/bash
echo "Sending service output to roweb.log"

nohup python rowebservices.py >roweb.log &

# End.
