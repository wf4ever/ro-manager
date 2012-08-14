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
    long_description=read("README.txt"),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="MIT",
    url=URL,
    packages = ['rocommand','rocommand.test'
               ,'iaeval','iaeval.test'
               ,'sync','sync.test'
               ,'MiscLib'
               ,'samples'
               ,'uritemplate'], #@@TODO: uritemplate already in PyPI?
    package_data = {
        'rocommand':    ['test/config/*','test/robase/*','test/nobase/*'
                        ,'test/data/ro-test-1/subdir1/*','test/data/ro-test-1/subdir2/*'
                        ,'test/data/ro-test-1/*.rdf','test/data/ro-test-1/README*'
                        ],
        'iaeval':       ['test/config/*','test/robase/*'
                        ,'test/data/data/*','test/data/docs/*'
                        ,'test/data/*.rdf'
                        ],
        'sync':         ['test/config/*','test/robase/*'],
        'samples':      ['*.sh', '*.py', 'prefixes.*', 'README'],
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
    install_requires=["rdflib >= 3.2.1", "rdfextras >=0.2"],
    entry_points = {
        'console_scripts': [
            'ro = rocommand.ro:runMain',
            'ro-manager-test = rocommand.test.RunRoManagerTests:runTestSuite'
            ],
        },
    )
