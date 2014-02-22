#!/usr/bin/env python

"""
Module to define matching template for checklist spreadsheet
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2013, University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

from gridmatch import (
    GridMatchReport, GridMatchError, GridMatch,
    text, anyval, regexval, refval, intval, save, value, error, trace
    )

csv_headings = (
    anyval("colA") +
    anyval("colB") +
    anyval("colC") +
    anyval("colD") +
    anyval("colE") +
    anyval("colF") +
    anyval("colG") +
    anyval("colH") +
    anyval("colI") +
    anyval("colJ") +
    anyval("colK") +
    anyval("colL") +
    anyval("colM") +
    anyval("colN") +
    anyval("colO") +
    anyval("colP") +
    anyval("colQ") +
    anyval("colR") +
    anyval("colS") +
    anyval("colT") +
    anyval("colU") +
    anyval("colV") +
    anyval("colW") +
    anyval("colX") +
    anyval("colY")
    )

csv_data = (
    anyval("colA") +
    anyval("colB") +
    anyval("colC") +
    anyval("colD") +
    anyval("colE") +
    anyval("colF") +
    anyval("colG") +
    anyval("colH") +
    anyval("colI") +
    anyval("colJ") +
    anyval("colK") +
    anyval("colL") +
    anyval("colM") +
    anyval("colN") +
    anyval("colO") +
    anyval("colP") +
    anyval("colQ") +
    anyval("colR") +
    anyval("colS") +
    anyval("colT") +
    anyval("colU") +
    anyval("colV") +
    anyval("colW") +
    anyval("colX") +
    anyval("colY")
    )

csvtordf = ( csv_headings
    // csv_data.repeatdown("datarows", max=3000)
    )

# End.
