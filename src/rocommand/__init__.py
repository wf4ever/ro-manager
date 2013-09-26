# __init__.py
#__version__ = "0.2.1"       # Initial version with installation package
#__version__ = "0.2.2"       # Updated README documentation for PyPI page
#__version__ = "0.2.3"       # Experimenting with distribution options
#__version__ = "0.2.4"       # Added MANIFEST.in so that data files are part of sdist
#__version__ = "0.2.5"       # Drop references to lpod-show from test suite
#__version__ = "0.2.6"       # Enhacements to handling of directories and external references
#__version__ = "0.2.7"       # Decouple MINIM constraints from target RO
                             # ROSRS (v6) support, support evaluation of RODL/ROSRS objects
                             # new annotation and linking options, 
                             # annotations with CURIE (QName) properties
                             # add ro remove command, fix URI escaping problems
#__version__ = "0.2.8"       # Optimize annotation access in ROSRS_Session
                             # Add web services for rendering traffic light displays
#__version__ = "0.2.9"       # Fix up experiment-workflow checklist
#__version__ = "0.2.10"      # Fix problem evaluating RO with space in URI
                             # RDFReport add escaping support; escape quotes in JSON strings
                             # Fix problem with URI liveness test
                             # New RO must have ore:Aggregation class
                             # Allow reporting of missing <forall> entries
                             # Add ro dump command
                             # Ordering of checklist display
                             # Various display formatting enhancements
#__version__ = "0.2.11"      # Add RO evolution commands; ro snapshow, ro archive, ro freeze
#__version__ = "0.2.12"      # Fix queries to work with rdflib 4.0.1 and rdflib-sparql
                             # Fix some bugs in RODL synchronization and evolution
                             # Refactor Minim model and add some new capabilities
#__version__ = "0.2.13"      # Implement Minim file creator from spreadsheet description
                             # Renamed library that was clashing with other installations
                             # Fixed bugs in processing of refactored Minim model
                             # Removed all references to minim:derives
                             # Improve escaping of string values in JSON output
                             # Updated REST checklisrt service landing page
                             # Various bug fixes
#__version__ = "0.2.14"      # ro list supports URI argument as alternative to directory
                             # Added initial "Overlay RO" service
                             # Added checklist spreadsheet -> Minim model converter
                             # Refactored HTTP session handling
                             # Code and test enhancements, including HTTP resource mocking
                             # Documentation updates
#__version__ = "0.2.15"      # Tuned "Overtlay RO" service and added command line utility
                             # Fixed some bugs in ROSRS URI handling, and cleaned URI handling code
                             # Updated documentation for Overlay RO installation
                             # Fixed ro-manager-test
                             # Improved user diagnostics when accessing unavailable RO
                             # Refactored spreadsheet grid access code
                             # Added direct-from-Excel support to mkminim
                             # Added context handler to HTTP_Session class
#__version__ = "0.2.16"      # Fixed bug in traffic light display when target resource is not the RO
                             # Add HTTP-redirect cache to roverlay server, to reduce use of redirectors
                             # Modify HTTP doRequestr methiods top return URI as string, not rdflib.URIRef
                             # Add retry logic to make Overlay ROs behave more consistently
                             # Minor documentation and script tweaks
__version__ = "0.2.17"      # Updates to RODL inbterface synchronization.  Includes option to push ZIP file bundle
                             # Provide label for checklist target resource as well as the RO
                             # Overlay RO service documentation updated
                             # Refactoring of HTTP access to ROs (HTTP_Session), and logic to catch and log HTTP connection errors
                             # Fix bug in RO metadata access when nested ROs are used
                             # Rename minim:testedConstraint to minim:testedChecklist in checklist results vocabulary
                             # Fix bug in handling of checklist "miss" option. 
                             # Improve diagnostics/logging in several areas, especially the checklist service
                             # Fix listening port error in Overlay RO service
                             # Improve handling of errors when parsing RO annotations
