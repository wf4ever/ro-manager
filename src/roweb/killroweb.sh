#!/bin/bash

ps 

echo kill `ps | grep "python rowebservices.py" | grep -v "grep" | awk '{print $1}'`
kill `ps | grep "python rowebservices.py" | grep -v "grep" | awk '{print $1}'`

