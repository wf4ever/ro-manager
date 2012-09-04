#!/usr/bin/python

"""
Configuration module for RO manager tests
"""

from rocommand import ro_settings

class ro_test_config:
    CONFIGDIR      = "config"
    ROBASEDIR      = "robase"
    NOBASEDIR      = "nobase"
    ROBOXURI       = "http://calatola.man.poznan.pl/robox/dropbox_accounts/1/ro_containers/2"
    ROBOXUSERNAME  = "Test User"
    ROBOXPASSWORD  = "d41d8cd98f00b204e9800998ecf8427e"
    ROBOXEMAIL     = "testuser@example.org"
    ROMANIFESTDIR  = ro_settings.MANIFEST_DIR
    ROMANIFESTFILE = ro_settings.MANIFEST_FILE
    ROMANIFESTPATH = ro_settings.MANIFEST_DIR+"/"+ro_settings.MANIFEST_FILE
    ROSRS_URI           = "http://sandbox.wf4ever-project.org/rodl/ROs/"
    ROSRS_ACCESS_TOKEN  = "32801fc0-1df1-4e34-b"
# End.
