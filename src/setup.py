#!/usr/bin/env python
#
# Setup.py based on https://github.com/paltman/python-setup-template/blob/master/setup.py,
# following http://www.ibm.com/developerworks/opensource/library/os-pythonpackaging/index.html

import codecs
import os
import sys

from distutils.util import convert_path
from fnmatch import fnmatchcase
from setuptools import setup, find_packages

def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()

# (Leftover from previous setup?)
standard_exclude = ["*.py", "*.pyc", "*$py.class", "*~", ".*", "*.bak"]
standard_exclude_directories = [
    ".*", "CVS", "_darcs", "./build", "./dist", "EGG-INFO", "*.egg-info"
]

PACKAGE = "rocommand"
NAME = "ro-manager"
DESCRIPTION = "Research Object manager (command line tool)"
AUTHOR = "Graham Klyne"
AUTHOR_EMAIL = "gk-pypi@ninebynine.org"
URL = "https://github.com/wf4ever/ro-manager"
VERSION = __import__(PACKAGE).__version__

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=read("README.md"),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="MIT",
    url=URL,
    packages = ['rocommand','rocommand.test'
               ,'iaeval','iaeval.test'
               ,'checklist','checklist.test'
               ,'roweb','roweb.test'
               ,'roverlay.rovweb','roverlay.rovcmd'
               ,'roverlay','roverlay.rovweb.rovweb','roverlay.rovweb.rovserver'
               ,'MiscUtils'
               ,'samples'
               ],
    package_data = {
        'rocommand':    [ 'test/config/*','test/robase/README','test/nobase/README'
                        , 'test/data/ro-test-1/subdir1/*','test/data/ro-test-1/subdir2/*'
                        , 'test/data/ro-test-1/*.rdf','test/data/ro-test-1/README*','test/data/ro-test-1/file*'
                        ],
        'iaeval':       [ 'test/config/*','test/robase/README'
                        , 'test/test-data-1/*.rdf', 'test/test-data-1/data/*', 'test/test-data-1/docs/*'
                        , 'test/test-data-2/*.rdf', 'test/test-data-2/data/*'
                        , 'test/test-simple-wf/TODO'
                        , 'test/test-simple-wf/*.rdf', 'test/test-simple-wf/*.sh'
                        , 'test/test-simple-wf/data/*', 'test/test-simple-wf/docs/*'
                        , 'test/test-chembox/*'
                        ],
        'roweb':        [ 'test/data/*.rdf','test/data/*.json','test/data/*.html','test/data/*.sh'
                        , 'test/data/css/*.css','test/data/css/images/*'
                        , 'test/data/images/*' 
                        ],
        'checklist':    [ 'test/config/*','test/robase/README','test/testro/*'
                        , 'test/TestGridMatch.xls', 'test/TestGridMatch.csv'
                        ],
        'roverlay':     [ '*.txt', '*.png', '*.md'
                        , 'rovweb/db/*.txt'
                        , 'rovweb/rovserver/templates/*.html'
                        , 'rovweb/rovserver/testdata/ro-test-1/subdir1/*'
                        , 'rovweb/rovserver/testdata/ro-test-1/subdir2/*'
                        , 'rovweb/rovserver/testdata/ro-test-1/*.txt'
                        , 'rovweb/rovserver/testdata/ro-test-1/*.rdf'
                        ],
        'samples':      [ '*.sh', '*.py', 'prefixes.*', 'README' ],
        },
    exclude_package_data = {
        '': ['spike/*'] 
        },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        ],
    zip_safe=False,
    install_requires=["rdflib == 4.0.1", "rdflib-sparql == 0.2", "httplib2", "uritemplate", "xlrd"],
    entry_points = {
        'console_scripts': [
            'ro = rocommand.ro:runMain',
            'mkminim = checklist.mkminim:runMain',
            'roverlay = roverlay.rovcmd.roverlay:runMain',
            'ro-manager-test = rocommand.test.RunRoManagerTests:runTestSuite'
            ],
        },
    )
