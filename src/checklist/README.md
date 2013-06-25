# Tooling to create Minim checklist definition.

See also: [../../Minim/spreadsheet-minim-conversion-requirements.md]()


# Outline design

To meet the requirements outlined, the converter will use a number of template "queries".  Each template would be a pattern that matches a rectangular portion of a spreadsheet, and the resulting RDF would be generated using an associated CONSTRUCT-like pattern for each match.  This would allow values to be picked out from arbitrary regions of a spreadsheet.  The intent is to make extensive use of explicit labels in the spreadsheet content to drive the matching of these templates.

In general, a template could match anywhere in a spreadsheet, but might be constrained in where it can be matched.  A common case envisaged to to restrict matches to the first column, which could thereby be reserved as a kind of keyword field and thus avoid unwanted matches.

An additional wrinkle is introduced by the requirement for repeated values.  

Implementation of the templkate matching is handled by a Parsec/pyParsing style combinator library, which would allow the initial implementation to be focused on immediate needs, and functionality to be added in as needed.  This design is developed fiurther below.


# Combinator-based grid matching

The basic type signature for a grid matching construct is:

    gridmatch :: (Sheet, Int, Int) -> Either ((Data.Map String Value), (Sheet, Int, Int)) Error

`(Sheet, Int, Int)` indicates a spreadsheet and a position at which to start matrching.

That is, if matched, a mapping dictionary is returned, along with a new position from
which to continue matching.

If not matched, diagnostic information is returned (gemnerally, an error message).

`Sheet` is an interface that abstracts access to a spreadsheet grid, which could be supplied in a number of different formats.  The interface is very simple:

    sheet.cell(row, col)

returns the content of the indicated cell.  The value returned may be a string or a number.

Grid matching functions may be combined in various ways to make more complex pattern matchers:

*   Horizontal continuation:

        gm1 + gm2

    Matches `gm1` then `gm2` immediately to its right on the same row.  
    The resulting dictinary contains values retyurned by both `gm1` and `gm2`.

*   Next row continuation:

        gm1 // gm2

    Matches `gm1` then `gm2` starting immediately below the start of `gm1`.
    The resulting dictinary contains values retyurned by both `gm1` and `gm2`.

*   Alternative matches:

        gm1 | gm2

    The resulting dictinary contains values retyurned by the matched alternative.

*   Optional match:

        gm1.optional()

    Matches `gm1` or nothing at all.  If nothing matched then an empty dictionary is returned.

*   Repeated match:

        gm1.repeatdown([min], [max])

    Matches `gm1` repeating down the grid, at least `min` times (default 0) and 
    at most `max` times (default unlimited).
    The value returned is a single element dictionary whose value is a list of dictionaries.

# Grid matching primitives

These primitives match (or fail to match) a single cell, and return a value accordingly.
If the match is successful, the return row, column values are updated to refelect the next 
row and columnb respectively, with the exception of `return` which does not update the
row and column values (i.e. returns the values supplied).

*   Match fixed text:

        text("<text>")

    Matches a single cell containing the literal `<text>` indicated.

*   Match and save arbitrary cell value:

        any(["key"])

    matches any cell, and returns a dictionary in which its value accessed using the suplied key.
    If no key is provided, returns an empty diuctionary.

*   Match and save URI reference:

        ref("key")

    matches a URI reference, and returns a dictionary in which its resolved value accessed using 
    the suplied key.  The containing document URI, with '#' appended, is used as a base URI for 
    resolving relative references.

*   Match and save integer value:

        int("key")

    matches an integer value, and returns a dictionary in which it is accessed using the suplied key.

*   Match nothing, but return a dictionary with the supplied key referencing the curremnt cell value:

        save("key", value)

*   Match nothing, but return a dictionary with the supplied key+value:

        return("key", value)

*   Always fails to match, and returns a supplied error message:

        error(message)
