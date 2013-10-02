# ro-manager project

**COPYRIGHT (2011-2013) University of Oxford**

**Author: Graham Klyne**

Software licence: MIT (http://opensource.org/licenses/MIT)

Documentation licence: CC-BY (http://creativecommons.org/licenses/by/2.0/uk/deed.en_US)

This project contains a number of command line and web utilities for managing Research Objects (ROs):

* `ro-manager` - a command line to for managing ROs in the local file system.  It also has some capabilities for accessing ROs on the Web,
* `roweb` - a web service that performs checklist evaluation of ROs.
* `roverlay` - a web service that creates "Overlay ROs" based on exsting linked data on the web.  The primary motivation for this has been to support checklist evaluation of linked open data on the web, but other RO-consuming facilities that might become available may also be supported.

More information, including installation instructions can be found in the README file in the project `src` directory ([src/README.md])

[src/README.md]: https://github.com/wf4ever/ro-manager/blob/master/src/README.md "README for RO Manager"


## ro-manager

This is a command-line Research Object management tool, following the specification at [http://www.wf4ever-project.org/wiki/display/docs/RO+management+tool](), which is in turn derived from [http://www.wf4ever-project.org/wiki/display/docs/RO+command+line+tool]().  Details of the command line interface are expected to evolve as the software is developed.

Documentation about using the tool is at [http://wf4ever.github.com/ro-manager/doc/RO-manager.html]() and [http://www.wf4ever-project.org/wiki/display/docs/RO+Manager+FAQ]().

The RO manager tool also includes the main source code and an instantiation of the checklist evaluation service for ROs in the local file system.

## roweb

This is a web server application that performs checklist evaluation of Research Objects accessible onthe Web.

More information, including installation and deployment instructions can be found in the README file in the project `src/roweb` directory ([src/roweb/README.md]).

[src/roweb/README.md]: https://github.com/wf4ever/ro-manager/blob/master/src/roweb/README.md "README for RO Checklist service"

<!-- , built using the [Pyramid](http://www.pylonsproject.org) framework, -->


## roverlay

This is a web server application and associatred command line utilty, providing a fast, lighweight way to create Research Objects from existing linked data on the Web.  General user and developer documentation is at [src/roverlay/roverlay.md].

Summary information, including installation and deployment instructions can be found in the README file in the project `src/roweb` directory ([src/roverlay/README.md]).

[src/roverlay/roverlay.md]: https://github.com/wf4ever/ro-manager/blob/master/src/roverlay/roverlay.md "Documentation for Overlay RO service"

[src/roverlay/README.md]: https://github.com/wf4ever/ro-manager/blob/master/src/roverlay/README.md "README for RO Checklist service"


# Git branch usage

As a first step to using "gitflow" branching structures ([http://nvie.com/posts/a-successful-git-branching-model/]()) a "develop" branch has been created.  The "master" branch should only ever contain production code that has been published to [PyPI](https://pypi.python.org/pypi).

Many developments may take place on a local branch and be pushed straight back to "develop".  Additional feature branches may be created and termined as required for longer-running developments.  The file [git-incantations.md] in the project root dirtectory (same as this README file) summarizes `git` commands that may be used to operate this branching model.

[git-incantations.md]: https://github.com/wf4ever/ro-manager/blob/master/git-incantations.md "Summary of GIT commands for various tasks"

----

<a rel="license" href="http://creativecommons.org/licenses/by/2.0/uk/deed.en_US"><img alt="Creative Commons License" style="border-width:0" src="http://i.creativecommons.org/l/by/2.0/uk/80x15.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/2.0/uk/deed.en_US">Creative Commons Attribution 2.0 UK: England &amp; Wales License</a>.

