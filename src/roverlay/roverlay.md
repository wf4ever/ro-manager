<!-- # roverlay.md -->

# roverlay: Service to create RO overlays on generic linked data

## roverlay command line client and related utilities

Implemented

    # Create an RO
    roverlay -s http://roverlay.example.org/ uri1 uri2 ... uriN
    http://roverlay.example.org/ROs/id1234/

    # List agregated content of RO
    ro list http://roverlay.example.org/RO/id1234/
    uri1
    uri2
     :
    uriN

    # List available overlay RO URIs at this service:
    roverlay -s http://roverlay.example.org/ -l
     :
    http://roverlay.example.org/ROs/id1234/
     :

    # Remove Overlay RO
    roverlay -d http://roverlay.example.org/ROs/id1234/
    RO http://roverlay.example.org/ROs/id1234/ deleted.


To be implemented:

    # Get URI for collected annotations
    roverlay -r http://roverlay.example.org/ROs/id1234/ -g
    http://roverlay.example.org/RO_Annotations/id1234/    

    # Get URI for SPARQL endpoint over annotations
    roverlay -r http://roverlay.example.org/ROs/id1234/ -q
    http://roverlay.example.org/RO_Query/id1234/

    # Query SPARQL endpoint
    asq -e http://roverlay.example.org/RO_Query/id1234/ \
        "SELECT * WHERE {http://roverlay.example.org/RO/id1234/ ?p ?o}"
    ...


## Installation

The installation assumes that a suitable Python virtual environment is being used for the RO Manager installation.  The same environment should be used for running the Overlay RO server and the command line utilities when both are run on a single machine.  See section below for more information.

1. Install RO-manager as described in [https://github.com/wf4ever/ro-manager/blob/master/src/README.md](https://github.com/wf4ever/ro-manager/blob/master/src/README.md).
This installs all the command line utilities (`ro`, `mkminim` and `roverlay`) and their dependencies,
but does not install the web frameworks needed to run any servioces.

2. Install Django, thus:

        $ pip install django

3. To activate an instance of the Overlay RO service, go to the directory `src/roverlay/roweb` within the installed Python environment.  In the following example, `(pyenv)` is the directory which hosts the Python virtual enviropnement where RO Manager has been installed; other elements of the path will vary with the particular version of python used:

        $ which python
        (pyenv)/bin/python
        $ cd (pyenv)/lib/python2.7/site-packages/ro_manager-0.2.15-py2.7.egg/roverlay/rovweb

4. On the very first occasion of running the service, create an instance of the `roverlay` local database: 

        $ python manage.py syncdb

   If asked about creating a superuser account, respond "No".

   If this operation fails with the message "OperationalError: unable to open database file", issue the following command and try again:

        $ mkdir db
        $ python manage.py syncdb

5. Now start the Overlay RO service:

        $ python manage.py runserver 0.0.0.0:8000

6. To confirm the service is running, point a browser to [http://localhost:8000/rovserver/]()

At this point, switch to a new terminal session, activate the Python virtual environment into which RO Manager was installed, and you should be able to run the command:

    roverlay --help

A summary of usage options is displayed.

At this point, the commands listed above are available.  If accessing a service running on the local machine, the `-s ` option can be omitted.  Example:

    $ roverlay res1 res2 res3
    http://localhost:8000/rovserver/ROs/127544b3/
    $ roverlay -l
    http://localhost:8000/rovserver/ROs/127544b3/
    $ ro list http://localhost:8000/rovserver/ROs/127544b3/
    file:///usr/workspace/wf4ever-ro-manager/src/roverlay/res1
    file:///usr/workspace/wf4ever-ro-manager/src/roverlay/res2
    file:///usr/workspace/wf4ever-ro-manager/src/roverlay/res3
    $ roverlay -d http://localhost:8000/rovserver/ROs/127544b3/
    RO http://localhost:8000/rovserver/ROs/127544b3/ deleted.
    $ ro list http://localhost:8000/rovserver/ROs/127544b3/
    Can't access RO manifest (404 NOT FOUND) for srsuri http://localhost:8000/rovserver/ROs/127544b3/
    $ roverlay -l

These commands can be issued with the `-s` option to explicitly specify thje Overlay RO service:

    $ roverlay -s http://localhost:8000/rovserver/ res1 res2 res3
    http://localhost:8000/rovserver/ROs/127544b4/
    $ roverlay -s http://localhost:8000/rovserver/ -l
    http://localhost:8000/rovserver/ROs/127544b4/

etc.  This `-s` option can be used to access an Overlay RO service running on another host.


## Persistence of created Research Objects

Research Objects created by the roverlay service are saved in a local on-disk database.  This means that they persist when the service is shut down and restarted.

The database can be re-initialized using the `manage.py` utility used when installing the software to initialize the database and run the server:

        $ python manage.py sqlclear rovserver
        $ python manage.py syncdb
        $ python manage.py runserver


## Python virtual environments

I recommend using a Python "virtual environment" for installing RO Manager and related software.
It allows the software to be installed without root privileges, or to create a temporary
or local copy of the RO Manager installation.
A disadvantage of this approach is that the Python virtual environment must always be activated
in order to run RO Manager or any related services.

The following assumes that Python "virtualenv" is installed (http://pypi.python.org/pypi/virtualenv).

You will need to choose a working directory where the Python virtual 
environment will be created.  We'll call this `$RO_MANAGER`.

Prerequisites are python 2.7 (http://python.org/download/releases/2.7/),
virtualenv (http://pypi.python.org/pypi/virtualenv) and 
pip (http://pypi.python.org/pypi/pip, http://www.pip-installer.org/).

1. Create and activate a Python virtual environment:

        cd $RO_MANAGER
        virtualenv roenv
        source roenv/bin/activate

2. To subsequently revert to the system default Python environment:
   
        deactivate

3. To reactivate the Python virtual environment, or to activate it in a new terminal session:

        source $RO_MANAGER/roenv/bin/activate

    or

        . $RO_MANAGER/roenv/bin/activate

4. To remove a temporary Python virtual environment, including any software that has been installed there:

        deactivate
        rm -rf $RO_MANAGER/roenv


## roverlay service interactions

![roverlay service interactions](roverlay-sequence-diagram.png "roverlay service interactions diagram")


## roverlay software framework

roverlay web service:
* Base on Django web framework
* Have asked about SPARQL protocol server implementation in Django
* POST to create RO
* DELETE to delete RO
* GET, HEAD to access RO using read-only elements of RO API

roverlay command line tool:  a simple Python command line program that interacts with the roveray web service.  It uses mostly standard Python library facilities in its operation.

> The examples above show graph and SPARQL endpoint options.  These are in anticipation of performance improvements for (say) chembox, and will not be part of the initial implementation.

> Subsequent experience with roverlay has shown alternative, very effective ways to overcome the performance issues enountered previously.  At this stage, it is not clear that the additional features will be justified.  The graph facility can be partially provided using the `ro dump` command, and the additional value of a SPARQL endpoint is currently not clear.


## roverlay deployment plans

The service has been tempoirarily deployed at andros.zoo.ox.ac.uk for testing, but this is not a production service and may be taken down at any time.

Deployment on the Wf4Ever sandbox has been attempted, but a fulkly functional service does not exist here because the service does not work through a reverse proxy (see below).

### Note about reverse proxy deployment

The roverlay service returns URIs in headers and response bodies that are needed to access the ROs created.  Because of this, the service cannot be run behind a reverse proxy gateway.  For this reason, we have not been able to deploy it in the Wf4Ever sandbox.

For the service to function behind a reverse proxy, the following would need to be handled by the reverse proxy service:

1. Proxy redirects to a public address, not the localhost interface (is this true if the rewrites are all performed as needed?)
2. Location: headers in responses re-written (in principle, Apache's reverse proxy should do this, but in tests we undertook this was not happening)
3. URIs in text/uri-list response bodies rewritten

    and possibly, for the future:

4. (Link: header URIs re-written - not currently needed, but may be for future developments)
5. (URIs in RDF responses (all syntaxes) re-written - this might not be needed if the roiverlay server always returns relative URIs.
5. (URIs in HTML responses re-written - see http://apache.webthing.com/mod_proxy_html/)
