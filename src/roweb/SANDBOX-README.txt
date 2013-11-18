SANDBOX-README.TXT


Notes for installing and running ro-manager / checklist evaluation service on sandbox.

== Quick start for checklist service on wf4ever sandbox ==

This guide assumes that RO-Manager and supporting software has been installed.

1.  Log in to checklist account on the sandbox

2.  Switch to bash shell:

        bash

3.  Activate the Python virtual environment:

        source ~/py27/bin/activate

4.  Run the bstartup script:

        cd ~/git/wf4ever/ro-manager/src/roweb/
        ./runroweb.sh

5.  Wait a few seconds and checvk the service log file:

        cat roweb.log

    The log file should be empty at this stage.  
    If there any problems starying the service, they should be recorded here.

If the service is already running, an error will be generated when trying to restart it.
To stop the service, use the command:

    ps x

to locate the current running service (look for `python rowebservices.py`), then issue:

    kill nnnnn

where `nnnnn` is the PID value associated with the current running service.


== Prerequisites ==

Standard compile/link tools (cc, etc.)

Python 2.7

sudo pip install VirtualEnv # (installed from PyPi, *not* Ubuntu 10.04 repository)
sudo apt-get  install libxml2-dev
sudo apt-get  install libxslt-dev


== Install and test ==

       cd /home/checklist
   36  virtualenv -p python2.7 py27
   37  source py27/bin/activate
   39  pip install lxml
   40  pip install rdfextras
   41  cd git
   42  git clone git://gitorious.org/lpod-project/lpod-python.git
   45  cd lpod-python/
   46  python setup.py install
   47  cd ..

   49  cd wf4ever/ro-manager/src/rocommand/test/
   50  python TestAll.py 

   53  cd /home/checklist/git/wf4ever/ro-manager/src/roweb/
   56  pip install pyramid

   55  python rowebservices.py &
   62  ./sandbox-evaluate.sh 

...

(py27)checklist@calatola:~/git/wf4ever/ro-manager/src/roweb$ cat runroweb.sh 
#! /bin/bash
nohup python rowebservices.py >roweb.log &

# End.

...

(py27)checklist@calatola:~/git/wf4ever/ro-manager/src/roweb$ cat sandbox-evaluate.sh 
#!/bin/bash
HOST=http://sandbox.wf4ever-project.org:8080    # Service endpoint URI

# Retrieve service description and extract template

echo "==== Retrieve URI template for evaluate checklist ===="
TEMPLATE=`curl -H "accept: text/turtle" $HOST/ | sed -n 's/^.*roe:checklist[ ]*"\([^"]*\)".*$/\1/p'`
echo "==== Template: <$TEMPLATE>"

# URI template expansion

echo "==== Request URI-template expansion ===="
cat >sample-params.txt <<END
{
  "template": "$TEMPLATE",
  "params":
  {
    "RO": "http://andros.zoo.ox.ac.uk/workspace/wf4ever-ro-catalogue/v0.1/simple-requirements/",
    "minim": "simple-requirements-minim.rdf",
    "purpose": "Runnable"
  }
}
END

EVALURI=$HOST`curl -X POST --data @sample-params.txt $HOST/uritemplate`

echo "==== URI: $EVALURI"

# Evaluation results with URI parameters:

echo "==== Request evaluation result with parameters, as RDF/Turtle ===="
curl -H "accept: text/turtle" $EVALURI

echo "==== Request evaluation result with parameters, as RDF/XML ===="
curl -H "accept: application/rdf+xml" $EVALURI

# End.

