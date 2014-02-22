# Simple tooling to create RDF from CSV

This has been quickly hacked from the `mkminim` utility (see "checklist" directory)

See also: [../../Minim/spreadsheet-minim-conversion-requirements.md]()

When the converted data is loaded to Fuseki, True this SP{ARQL query:

    prefix ex: <http://example.org/>

    select ?a ?av ?b ?bv ?e ?ev ?w ?wv ?x ?xv where 
    { 
      ?s a ex:ColumnHeadingText 
        ; ex:colA ?a
        ; ex:colB ?b 
        ; ex:colE ?e
        ; ex:colW ?w 
        ; ex:colX ?x
        .
      ?r a ex:RowData 
        ; ex:colA ?av 
        ; ex:colB ?bv 
        ; ex:colE ?ev 
        ; ex:colW ?wv 
        ; ex:colX ?xv 
        .
    }
