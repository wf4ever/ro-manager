#!/bin/bash

killall python
python setup.py build
python setup.py install
cd roweb
source runroweb.sh
sleep 2
cat roweb.log
cd ..

