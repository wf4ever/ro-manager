<!-- # roverlay.md -->

# roverlay: Service to create RO overlays on generic linked data

## roverlay command line client and related utilities

    # Create an RO
    roverlay -s http://roverlay.example.org/ uri1 uri2 ... uriN
    http://roverlay.example.org/ROs/id1234/

    # List agregated contebnt of RO
    ro list http://roverlay.example.org/RO/id1234/
    uri1
    uri2
     :
    uriN

    # Get URI for collected annotations
    roverlay -r http://roverlay.example.org/ROs/id1234/ -g
    http://roverlay.example.org/RO_Annotations/id1234/    

    # Get URI for SPARQL endpoint over annotations
    roverlay -r http://roverlay.example.org/ROs/id1234/ -q
    http://roverlay.example.org/RO_Query/id1234/

    # Query SPARQL endpoint
    asq -e http://roverlay.example.org/RO_Query/id1234/ \
        "SELECT * WHERE {http://roverlay.example.org/RO/id1234/ ?p ?o}"
    ...

## roverlay service interactions

![roverlay service interactions](roverlay-sequence-diagram.png "roverlay service interactions diagram")

## roverlay software framework

roverlay web service:
* Base on Django web framework
* Have asked about SPARQL protocol server implementation in Django
* POST to create RO
* DELETE to delete RO
* GET, HEAD to access RO using read-only elements of RO API

roverlay command line tool:
* use mkminim as initial template; command options as illustrated above.  Interacts with web service.

> The examples above show graph and SPARQL endpoint options.  These are in anticipation of performance improvements for (say) chembox, and will not be part of theinitial implementation.

## roverlay deployment plans

Initial deployment on Andros.

Subsequent deployment on Wf4Ever sandbox?  May need to arrange an alternate port number (or migrate checklist service to Django platform).

