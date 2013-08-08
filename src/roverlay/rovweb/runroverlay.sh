#! /bin/bash
echo "Sending service output to rovweb.log"

nohup python manage.py runserver >rovweb.log &

# End.
