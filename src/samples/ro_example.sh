#!/usr/bin/env bash
#
# Create and list Research Object structure
# Script for example at http://www.wf4ever-project.org/wiki/display/docs/RO+Manager+FAQ

echo "---- Create and list Research Object structure"

ro create "Sample RO" -d ROSample -i RO-id-sample
ro list -d ROSample
ro list -a -d ROSample
ro status -d ROsample/

ro add -a -d ROsample/ ROsample/
ro list -d ROsample/
ro list -s -a -d ROsample/

echo "---- Create and display an annotation on specific file"

ro annotate ROsample/file1.txt title "Title for file1.txt"
ro annotations ROsample/file1.txt 

echo "---- Display all annotations for a Research Object"

ro annotations -d ROsample/

echo "---- Create link from file to notes"

ro link ROsample/file1.txt ex:hasNote ROsample/notes/note1.txt 
ro annotations ROsample/file1.txt 

echo "---- Aggregate an internal directory"

ro add -d ROsample/ ROsample/notes/
ro list -d ROsample/

echo "---- Add link relation between internal directory and RO"

ro link -d ROsample ROsample/notes ex:notesFor ROsample/
ro annotations ROsample/notes/

echo "---- Aggregate an external resource"

ro add -d ROsample/ http://example.org/external
ro list -d ROsample/

echo "---- Annotate an external resource"

ro annotate -d ROsample/ http://example.org/external type "external resource"
ro annotate -d ROsample/ http://example.org/external keywords "foo,bar"
ro annotate -d ROsample/ http://example.org/external title "External resource in ROSample"
ro annotate -d ROsample/ http://example.org/external rdfs:seeAlso http://example.org/another/resource
ro annotations -d ROsample/ http://example.org/external

echo "---- Research Object content summary"

ro status -d ROsample/
ro list -a -s -d ROsample/
ro annotations -d ROsample/

# End.
