Research Object manager command line tool

Research Objects are semantically rich aggregations of resources [1] that bring together data, methods and people in scientific investigations.  For further information, see:
* What is an RO? - http://www.wf4ever-project.org/wiki/pages/viewpage.action?pageId=2065079 
* Wf4Ever Research Object Model -  http://wf4ever.github.com/ro/

Research Object Manager (RO Manager) is a simple command line tool for creating and manipulating Research Objects in a local file system, and for exchanging them with a Research Object Digital Library (RODL):
* http://www.wf4ever-project.org/wiki/display/docs/RO+management+tool
* http://www.wf4ever-project.org/wiki/display/docs/RO+Manager+FAQ

Dependencies:
- Python 2.7.
- Linux/Unix type system.  This software has not been tested under Windows, but may work.
- The sample scripts are written to run under BASH

Installation summary (see below for more details):

  pip install ro-manager
  ro-manager-test

OR

  cd (some working directory)
  git clone https://github.com/wf4ever/ro-manager.git ro-manager
  cd ro-manager
  python setyp.by build
  python setup.py install
  ro-manager-test


== To install from GitHub ==

1. Pull a copy of this repository to a local directory. Let's call this $RO_MANAGER.
   It's recommended to do this using git.
   In the first instance, will be a "git clone ...".
   For subsequent updates, go into the ro-manager directory tree and use "git pull".

     cd (some working directory)
     git clone https://github.com/wf4ever/ro-manager.git ro-manager
     cd ro-manager

   The current working directory is now the $RO_MANAGER directory.

2. (Optional) Use Python virtualenv to create and activate an environment for installing
   RO manager.  There are two advantages to doing this: (a) not needing root privileges to 
   install ro-manager, and (b) using a Python environment version different from the
   system default.  The main disadvantage of using a new Python virtual environment is
   that it must be activated every time before RO Manager can be run.

     cd $RO_Manager
     virtualenv roenv
     source roenv/bin/activate

3. Go to directory $RO_MANAGER/src

4. Build the installation package:

     python setup.py build

5. Install the package and its dependencies.  If installing into new Python virtual environment:

     python setup.py install
   
   If *not* installing into new Python virtual environment, this command must be run as root:
   
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

7. To run RO manager to display a sumnmary of commands and options:

     ro help


== To install from PyPI ==

RO-manager can also be installed from PyPI using 'pip' or 'easy_install'.

1. If required, create a new Python virtual environment as described above

2. Install:

     pip install ro-manager

   If not installing to a virtual environment, the command needs to be run with 
   root privileges:
   
     sudo pip install ro-manager


3. Test:

     ro-manager-test
     ro help


== Using RO Manager ==

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
