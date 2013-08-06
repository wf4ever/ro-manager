# ro-manager project

This project contains a number of command line and web utilities for managing ROs:

* ro-manager - command line to for managing ROs in the local file system.  It also has some capabilities for accessing ROs on the Web,
* roweb - a web service that performs Rchecklist evaluation of ROs.
* roverlay - a web service that creates "Overlay ROs" based on exsting linked data on the web.  The primary motivation for this has been to support checklist evaluation of linked open data on the web, but other RO-using facilities may also be supported.

Installation instructions can be found in the README file in the "src" directory (https://github.com/wf4ever/ro-manager/blob/master/src/README.md).


# ro-manager

This is a command-line Research Object management tool, following the specification at http://www.wf4ever-project.org/wiki/display/docs/RO+management+tool, which is in turn derived from http://www.wf4ever-project.org/wiki/display/docs/RO+command+line+tool.  Details of the command line interface are expected to evolve as the software is developed.

Documentation about using the tool is at http://wf4ever.github.com/ro-manager/doc/RO-manager.html and http://www.wf4ever-project.org/wiki/display/docs/RO+Manager+FAQ.  (As of October 2012, the FAQ documentation is more up to date.)


## Git branch usage

As a first step to using "gitflow" branching structures (http://nvie.com/posts/a-successful-git-branching-model/) a "develop" branch has been created.  In due course, the "master" branch should only ever contain production code that has been published to PyPI.

I have not yet created branches for releases or feature development
I'm taking a view that these can be created as required.

Many developments may take place on a local branch and be pushed straight back to "develop".

