# Overlay Research Object service

**Author: Graham Klyne (graham.klyne@zoo.ox.ac.uk)**

The Overlay Research Object service is a web server that provides an easy, lightweight way to create Research Objects, primarily so that RO-based services can be used with arbitrary linked data.

The software consists of two components:

1. A Django-based web apoplication that provides a simple HTTP API for creating, deleting and accessing Overlay Research Objects.

2. A simple command-line tool, `roverlay` to provide access to the web service from a command shell, or from a shell script.

See [https://github.com/wf4ever/ro-manager/blob/master/src/roverlay/roverlay.md]() for more details.


# Installation and deployment

## Dependencies

* Python 2.7.x
* Linux/Unix type system.
  This software has not been tested under Windows, but may work.
* Python `pip` utility
* `git` command line tool (depending on the installation option used).
* Commands are tested to run in a `bash` shell environment.
* The Overlay RO web service uses the Django web development framework, installation of which is covered below.  The software has been developed and tested with Django version 1.5.1, but will hopefully also work with later releases.
* Various other Python packages that are located and installed by the `pip` and `setup.py` utilities.


## Installation overview

Installation instructions assume a terminal interface and a `bash` command shell.

The first step for installing the checklist service is to install RO Manager.  Then some additional supporting code needs to be installed, and the web service deployed and activated.

In the instructions that follow:
* _software_ is the name of a directory where the Python virtual enviroment will be installed.
* _pyenv_ is the name of python virtual environmewnt used.  This is also used to name a subdirectory of _software_ that holds the virtual environment files.
* _workspace_ is the name of a workspace directory where the RO Manager software is copied.


### RO Mananger

This is just a summary of the RO Manager installation.  More detailed explanations can be found in [https://github.com/wf4ever/ro-manager/blob/master/src/README.md]().  Installing RO Manager is sufficient to install the `roverlay` command line client.

The installation method suggested here uses `git` to pull the software from Github rather than installation from PyPI using `pip`.  Either can be used, but with the suggested approach, it is easier to locate the Django utilities used to start the web service, the service log file, etc.

If not already existing, create the new virtual environment:

    cd _software_
    pip install virtualenv
    virtualenv _pyenv_

Once created, activate this environment (using name of enviroment used in the original `virtualenv` command):

    source _pyenv_/bin/activate

Install the RO Manager software package from github:

    cd _workspace_
    git clone https://github.com/wf4ever/ro-manager.git ro-manager
    cd ro-manager/src
    python setup.py build
    python setup.py install
    ro-manager-test


### Overlay RO web service instalation and deploymemt

These are quick-start instructions, assuming that the RO Manager source package has been extracted into directory `_workspace_`.  More details about the installation process are in [https://github.com/wf4ever/ro-manager/blob/master/src/README.md]().

First, ensure that the appropriate Python virtual environment is active; e.g.

    source _pyenv_/bin/activate

The checklist evaluation service uses the Pyramid web application development framework ([http://www.pylonsproject.org]()), which is installed thus:

    pip install django

To activate the checklist web service, go to the RO Manager source directory and issue the command shown:

    cd _workspace_/ro-manager/src/roverlay/rovweb
    mkdir db
    python manage.py syncdb
    python manage.py runserver 0.0.0.0:8000

At this point, the Overlay RO service should to ready to receive HTTP requests on port 8000.  Try starting a browser on the local machine, and displaying the page at `http://localhost:8000` to confirm this.

## Testing the deployed service

Switch to a new terminal session and activate the Python virtual environment into which RO Manager was installed.  Should be able to run the command:

    roverlay --help

A summary of usage options is displayed.  Twy the following:

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
    $

Again, more details are at [https://github.com/wf4ever/ro-manager/blob/master/src/README.md]().


# Related Publications

* Jun Zhao, Graham Klyne, Piotr Holubowicz, Raúl Palma, Stian Soiland-Reyes, Kristina Hettne, José Enrique Ruiz, Marco Roos, Kevin Page, José Manuel Gómez-Pérez, David De Roure, Carole Goble. _RO-Manager: A Tool for Creating and Manipulating Research Objects to Support Reproducibility and Reuse in Sciences_. The Second Linked Science Workshop at ISWC Boston, USA November, 2012
* Kevin Page, Raúl Palma, Piotr Holubowicz, Graham Klyne, Stian Soiland-Reyes, Don Cruickshank, Rafael González Cabero, Esteban García, David De Roure Cuesta, Jun Zhao, José Manuel Gómez-Pérez. _From workflows to Research Objects: an architecture for preserving the semantics of science_. The Second Linked Science Workshop at ISWC Boston, USA November, 2012


# Acknowledgement

![Wf4Ever project](http://sandbox.wf4ever-project.org/portal/images/wf4ever_logo.png)

This software has been developed by University of Oxford as part of the [Wf4Ever project](http://www.wf4ever-project.org).

----

<a rel="license" href="http://creativecommons.org/licenses/by/2.0/uk/deed.en_US"><img alt="Creative Commons License" style="border-width:0" src="http://i.creativecommons.org/l/by/2.0/uk/80x15.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/2.0/uk/deed.en_US">Creative Commons Attribution 2.0 UK: England &amp; Wales License</a>.

