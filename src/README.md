# Research Object manager command line tool

**Author: Graham Klyne (graham.klyne@zoo.ox.ac.uk)**

Research Objects are semantically rich aggregations of resources that bring
together data, methods and people in scientific investigations.  For further
information, see:
* What is an RO?
  - http://www.wf4ever-project.org/wiki/pages/viewpage.action?pageId=2065079 
* Wf4Ever Research Object Model
  - http://wf4ever.github.com/ro/

Research Object Manager (RO Manager) is a simple command line tool for creating and
manipulating Research Objects in a local file system, and for exchanging them with a
Research Object Digital Library (RODL):
* http://www.wf4ever-project.org/wiki/display/docs/RO+management+tool
* http://www.wf4ever-project.org/wiki/display/docs/RO+Manager+FAQ

Additional installation and deployment information:
* Checklist evaluaton service: [https://github.com/wf4ever/ro-manager/blob/master/src/roweb/README.md]()
* Overlay Research Object creation service: [https://github.com/wf4ever/ro-manager/blob/master/src/roverlay/README.md]()


## Dependencies

* Python 2.7.
* Linux/Unix type system.
  This software has not been tested under Windows, but may work.
* The sample scripts are written to run under BASH
* Python pip utility, or git, depending on the installation option used.


## Installation overview

This is just a summary of the installation options.
More detailed explanations can be found below.

There are two main options for installation: the first is from the Python 
Package Index (PyPI) which requires that the Python pip utility is installed:

    pip install ro-manager
    ro-manager-test

The other option is to take a copy of the source code from GitHub, and install
from that, which requires that the git source code management tool is
installed:

    cd (some working directory)
    git clone https://github.com/wf4ever/ro-manager.git ro-manager
    cd ro-manager/src
    python setup.py build
    python setup.py install
    ro-manager-test

For further information on installing git on various systems, see:
* http://git-scm.com/download
* http://git-scm.com/book/en/Getting-Started-Installing-Git
* http://www.devdaily.com/mac-os-x/how-install-git-mac-os-x-osx
* https://help.ubuntu.com/community/Git

For further information on installing pip on various systems, see:
* http://stackoverflow.com/questions/4986896/
* http://www.saltycrane.com/blog/2010/02/how-install-pip-ubuntu/
* http://stackoverflow.com/questions/4750806/how-to-install-pip-on-windows

Once pip is installed, it can be used to install virtualenv, if needed.


## System-wide install from PyPI

RO-manager can be installed from the Python Package Index (PyPI) using 'pip'.

This is the simplest option for installing RO Manager, and does not require
a copy of the RO Manager code be obtained from GitHub, but generally does
require that you have root access on the computer where it is installed:

Prerequisites are python 2.7 (http://python.org/download/releases/2.7/) and 
pip (http://pypi.python.org/pypi/pip, http://www.pip-installer.org/).

1. Install:

        sudo pip install ro-manager

    (You may be asked for a password to confirm root access privilege.)

2. Test:

        ro help


## "Virtual environment" install from PyPI

If you don't have root privileges, or if you want to create a temporary
or local copy of the RO Manager installation, this can be done using the
Python "virtual environment" facility.  The following assumes that Python
"virtualenv" is installed (http://pypi.python.org/pypi/virtualenv),  This
method does not require that a copy of RO Manager software be obtained
from GitHub.  A disadvantage of this method is that the Python virtual
environment must always be activated in order to run RO Manager.

You will need to choose a working directory where the Python virtual 
environment will be created.  We'll call this $RO_MANAGER.

Prerequisites are python 2.7 (http://python.org/download/releases/2.7/),
virtualenv (http://pypi.python.org/pypi/virtualenv) and 
pip (http://pypi.python.org/pypi/pip, http://www.pip-installer.org/).

1. Create and activate virtual environment:

        cd $RO_Manager
        virtualenv roenv
        source roenv/bin/activate

    To subsequently revert to the system default Python environment:
   
        deactivate

    To remove a temporary virtual environment, including any software
    that has been installed there:

        deactivate
        rm -rf $RO_MANAGER/roenv

2. Install RO Manager:

        pip install ro-manager

3. Test:

        ro help


## To install from GitHub

RO Manager can also be installed using a copy of the software obtained
from GitHub.  This may be advantageous if you need to access the most
recent version of the software.  (The copy uploaded to PyPI may lag the
development copy in GitHub.)

Prerequisites are python 2.7 (http://python.org/download/releases/2.7/) and git (http://git-scm.com/).

1. Obtain a copy of software from GitHub:

    In the first instance, the command used will be a "git clone ...":

    Choose a working directory where the RO Manager software will be
    stored:

        cd (working directory)
        git clone https://github.com/wf4ever/ro-manager.git ro-manager
        cd ro-manager

    The current working directory is now the $RO_MANAGER directory.

    To obtain subsequent updates, go into the ro-manager directory
    tree and use "git pull":
   
        cd $RO_MANAGER
        git pull

2. (Optional) Use Python virtualenv to create and activate an environment
   for installing RO manager.  There are two advantages to doing this:
   (a) not needing root privileges to install ro-manager, and 
   (b) using a Python environment version different from the system default.
   The main disadvantage of using a new Python virtual environment is
   that it must be activated every time before RO Manager can be run.

        cd $RO_Manager
        virtualenv roenv
        source roenv/bin/activate

3. Go to directory $RO_MANAGER/src

        cd $RO_MANAGER/src

4. Build the installation package:

        python setup.py build

5. Install the package and its dependencies

    If installing into a Python virtual environment:

        python setup.py install
   
    If *not* installing into a Python virtual environment, 
    this command must be run as root:
   
        sudo python setup.py install

6. Test the installation

        ro-manager-test

    The following should be displayed:

        $ ro-manager-test 
        .......................................................................................................
        ----------------------------------------------------------------------
        Ran 103 tests in 13.406s
    
        OK
        $ 

    Note that (on some systems, including MacOS), if RO Manager is installed under
    the system Python environment (i.e. not using virtualenv) then a small number of
    test cases that access test data files may fail.  If the majority of tests pass,
    and the ro command appears to work, the installation is probably fine.

7. To run RO manager to display a summary of commands and options:

        ro help


## Using RO Manager

See also the documentation at http://www.wf4ever-project.org/wiki/display/docs/RO+management+tool

Directory $RO_MANAGER/src/samples contains some bash shell scripts that are 
examples for creating, annotating and displaying simple Research Objects.

Note that the ro config command needs to be run to set up a 
configuration for your environment, though it can be re-run to update 
the details.  Most ro config values are currently ignored.  The important 
value is -b <robase>, which indicates a disk area where Research Objects
are managed.

Look inside the file $RO_MANAGER/src/samples/ro_sample.sh to see what the 
individual commands used look like.

For example, to create and manipulate a simple example Research Object:

    cd $RO_MANAGER/src/samples
    ./ro_sample.sh

The output should look something like this:

    $ ./ro_sample.sh 
    --------
    ro config -b /usr/workspace/wf4ever-ro-manager/src/rocommand/test/robase
              -r http://calatola.man.poznan.pl/robox/dropbox_accounts/1/ro_containers/2
              -p d41d8cd98f00b204e9800998ecf8427e
              -u Test user -e testuser@example.org
    ro configuration written to /Users/graham
    --------
    mkdir: rocommand/test/robase/test-create-RO: File exists
    cp: /ro-test-1/*: No such file or directory
    ro create "Test Create RO" -d "rocommand/test/robase/test-create-RO" -i "RO-id-testCreate"
    ro status -d "rocommand/test/robase/test-create-RO"
    Research Object status
      identifier:  RO-id-testCreate, title: Test Create RO
      creator:     Test user, created: 2011-09-15T15:12:17
      path:        /usr/workspace/wf4ever-ro-manager/src/rocommand/test/robase/test-create-RO
      uri:         file:///usr/workspace/wf4ever-ro-manager/src/rocommand/test/robase/test-create-RO/#
      description: Test Create RO
    ro list -d "rocommand/test/robase/test-create-RO"
    test-create-RO/.ro/manifest.rdf
    test-create-RO/README-ro-test-1
    test-create-RO/subdir1/subdir1-file.txt
    test-create-RO/subdir2/subdir2-file.txt
    --------
    ro annotate rocommand/test/robase/test-create-RO/subdir1/subdir1-file.txt title "subdir1-file.txt title"
    ro annotations -d "rocommand/test/robase/test-create-RO/subdir1" rocommand/test/robase/test-create-RO/subdir1/subdir1-file.txt 
    file:///usr/workspace/wf4ever-ro-manager/src/rocommand/test/robase/test-create-RO/subdir1/subdir1-file.txt
      title: subdir1-file.txt title
    --------
    ro annotate rocommand/test/robase/test-create-RO/subdir2/subdir2-file.txt type "subdir2-file.txt type"
    ro annotate rocommand/test/robase/test-create-RO/subdir2/subdir2-file.txt keywords "subdir2-file.txt foo,bar"
    ro annotate rocommand/test/robase/test-create-RO/subdir2/subdir2-file.txt description "subdir2-file.txt description\nline 2"
    ro annotate rocommand/test/robase/test-create-RO/subdir2/subdir2-file.txt format "subdir2-file.txt format"
    ro annotate rocommand/test/robase/test-create-RO/subdir2/subdir2-file.txt title "subdir2-file.txt title"
    ro annotate rocommand/test/robase/test-create-RO/subdir2/subdir2-file.txt created "20110914T12:00:00"
    ro annotations -d "rocommand/test/robase/test-create-RO/subdir2" rocommand/test/robase/test-create-RO/subdir2/subdir2-file.txt 
    file:///usr/workspace/wf4ever-ro-manager/src/rocommand/test/robase/test-create-RO/subdir2/subdir2-file.txt
      type: subdir2-file.txt type
      title: subdir2-file.txt title
      format: subdir2-file.txt format
      keywords: subdir2-file.txt foo,bar
      created: 20110914T12:00:00
      description: subdir2-file.txt description\nline 2
    --------

## Revision history

### Changes for 0.2.20

* More documentation improvements (including LISC 2013 material added)
* Metadata query diagnostic improvements (log query in event of failure)
* Enhance Minim model to allow values to be collected from probe query
* Update Minim results model to create independent description for each evaluation

### Changes for 0.2.19

* Documentation updates (not released)

### Changes for 0.2.18

* Create benchmarking scrpts and result data
* Add utility to create RO for benchmarking
* Adjust iaeval package to work with PyPI copy of uritemplate
* Revise RO access logic to allow 'ro' to display details of RO at arbitrary location
* Add project copyright and licencing information.
* Add README for Overlay RO service, and update other documentation files.

### Changes for 0.2.17

* Updates to RODL synchronization.  Includes option to push ZIP file bundle
* Provide label for checklist target resource as well as the RO
* Overlay RO service documentation updated
* Refactoring of HTTP access to ROs (HTTP_Session), and logic to catch and log HTTP connection errors
* Fix bug in RO metadata access when nested ROs are used
* Rename minim:testedConstraint to minim:testedChecklist in checklist results vocabulary
* Fix bug in handling of checklist "miss" option. 
* Improve diagnostics/logging in several areas, especially the checklist service
* Fix listening port error in Overlay RO service
* Improve handling of errors when parsing RO annotations

### Changes for 0.2.16

* Fixed bug in traffic light display when target resource is not the RO
* Add HTTP-redirect cache to roverlay server, to reduce use of redirectors
* Modify HTTP doRequestr methiods top return URI as string, not rdflib.URIRef
* Add retry logic to make Overlay ROs behave more consistently
* Minor documentation and script tweaks


### Changes for V0.2.15

* Tuned "Overlay RO" service and added `roverlay` command line utility
* Fixed some bugs in ROSRS URI handling, and tidied URI handling code
* Updated documentation for Overlay RO installation
* Fixed `ro-manager-test`
* Improved user diagnostics when accessing an unavailable RO
* Refactored spreadsheet grid access code
* Added direct-from-Excel support to mkminim
* Added context handler to `HTTP_Session` class


### Changes for V0.2.14

* `ro list` supports URI argument as alternative to directory
* Added initial "Overlay RO" service
* Added checklist spreadsheet -> Minim model converter
* Refactored HTTP session handling
* Code and test enhancements, including HTTP resource mocking
* Documentation updates


### Changes for V0.2.13

* Implement Minim file creator from spreadsheet description (mkminim command)
* Renamed library that was clashing with other installations
* Fixed bugs in processing of refactored Minim model
* Removed all references to minim:derives
* Improve escaping of string values in JSON output
* Updated REST checklisrt service landing page
* Various bug fixes


### Changes for V0.2.12

* Refactor Minim model and extend checklist evaluation capabilities
* Fix queries to work with rdflib 4.0.1 and rdflib-sparql
* Fix some bugs in RODL synchronization and evolution
* Fix rowebservices handling of URIs containing escaped characters and special characters
* Fix problems with extended (non-ASCII) characters in checklist query results



### Changes for V0.2.11

* Add RO evolution commands; ro snapshot, ro archive, ro freeze


### Changes for V0.2.10

* Fix problem evaluating RO with space in URI
* RDFReport add escaping support; escape quotes in JSON strings
* Fix problem with URI liveness test
* New RO must have ore:Aggregation class
* Allow reporting of missing <forall> entries
* Add ro dump command
* Ordering of checklist display
* Various display formatting enhancements


### Changes for V0.2.9

* Fix up experiment-workflow checklist


### Changes for V0.2.8

* Web services to return checklist result as HTML or JSON for rendering by Javascript
* RDF output option from checklist evaluation function
* Command line evaluation can run against RO accessed using ROSRS API
* Various small bug fixes, refactoring and optimizations
* Updated sample files and scripts


### Changes for V0.2.7

* Add `ro remove` command, fix URI escaping problems that were occurring when an RO was created from files containing space or '#' characters
* Add `ro link` command; this works just like `ro annotate`, except that the default treatment of the target value (i.e. for unrecognized annotation types) is as a URI, this providing a mechanism to create arbitrary links between RO resources, or between an RO resource and an external resource.
* Allow annotation and links  with CURIE (QName) properties.  A predefined set of recognized URI prefixes are defined (see `~/.ro-config`) which can be used to create annotations with CURIES; e.g. `ro link foo rdfs:seeAlso bar`.
* Create multiple annotations and links with wildcard resource matching; e.g. `ro link -w "/workflow/.*t2flow$" rdf:type wfdesc:Workflow" will create an rdf:type wfdesc:Workflow link for all aggregated resources in a directory named "/Workflow" and with file extension ".t2flow".
* ROSRS (v6) support
* Support for checklist evaluation of ROs stored in RODL or some other ROSRS service (used primarily by the `roweb` service component)
* Decouple MINIM constraints from target RO.  Allow creation of MINIM descriptions that can be applied to arbitrary ROs:  this paves the way for creating and using checklists that encode community norms for RO quality.


----

<a rel="license" href="http://creativecommons.org/licenses/by/2.0/uk/deed.en_US"><img alt="Creative Commons License" style="border-width:0" src="http://i.creativecommons.org/l/by/2.0/uk/80x15.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/2.0/uk/deed.en_US">Creative Commons Attribution 2.0 UK: England &amp; Wales License</a>.

