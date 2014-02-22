# !/usr/bin/env python

""""
Grid class and implementations for CSV and Excel spreadsheet files

See: README.md in this directory
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2013, University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import urlparse
import csv
import xlrd
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

class Grid(object):
    """
    Interface for grid or spreadsheet object.
    """

    def __init__(self, baseuri=None):
        ### self._baseuri = ro_uriutils.resolveFileAsUri(baseuri or "")
        self._baseuri = (baseuri or "")
        return

    def baseUri(self, uriref=None):
        if uriref:
            self._baseuri = self.resolveUri(uriref)
        return self._baseuri

    def resolveUri(self, uriref):
        # return ro_uriutils.resolveUri(uriref, self._baseuri)
        endswithhash = uriref.endswith("#")
        resolveduri  = urlparse.urljoin(self._baseuri, uriref)
        if endswithhash and not resolveduri.endswith("#"):
            resolveduri = resolveduri + "#"
        return resolveduri

    def cell(self, row, col):
        assert False, "Unimplemented 'cell' method"

    def __getitem__(self, row):
        return GridRow(self, row)


class GridRow(object):
    """
    Interface for auxiliary grid or spreadsheet row.
    """

    def __init__(self, grid, row):
        self._grid = grid
        self._row  = row
        return

    def __getitem__(self, col):
        return self._grid.cell(self._row, col)


class GridCSV(Grid):
    """
    Initialize a grid object based on a CSV file

    @param csvfile:     A file-like object that contains CSV data
    @param baseuri:     A string used as the base URI for references in the grid.
    @param dialect:     An optional dialect parameter (e.g. 'excel', 'excel-tab').
                        If not specified, the system sniffs the content of the CSV 
                        to guess the CSV dialect used.
    """

    def __init__(self, csvfile, baseuri=None, dialect=None):
        super(GridCSV, self).__init__(baseuri=baseuri)
        if not dialect:
            dialect = csv.Sniffer().sniff(csvfile.read(1024))
            csvfile.seek(0)
        log.debug("GridCSV: %s, %s"%(csvfile, dialect))
        reader = csv.reader(csvfile, dialect)
        self._rows   = []
        self._maxcol = 0
        for row in reader:
            # log.debug("- row: %s"%(repr(row)))
            self._rows.append(row)
            if len(row) > self._maxcol: self._maxcol = len(row)
        return

    def cell(self, row, col):
        return self._rows[row][col] if col < len(self._rows[row]) else ""


class GridExcel(Grid):
    """
    Initialize a grid object based on an excel file

    @param xlsfile:     Filename of an Excel spreadsheet file
    @param baseuri:     A string used as the base URI for references in the grid.
    """

    def __init__(self, xlsfilename, baseuri=None):
        super(GridExcel, self).__init__(baseuri=baseuri)
        log.debug("GridExcel: %s"%(xlsfilename))
        self._workbook = xlrd.open_workbook(filename=xlsfilename)
        # Assume first and only worksheet
        self._sheet = self._workbook.sheet_by_index(0)
        log.debug("GridExcel sheet size: %d, %d"%(self._sheet.nrows, self._sheet.ncols))
        return

    def cell(self, row, col):
        log.debug("GridExcel.cell [%d,%d]"%(row, col))
        if row in range(self._sheet.nrows) and col in range(self._sheet.ncols):
            cell = self._sheet.cell(row, col)
            log.debug("Cell type: %d"%(cell.ctype))
            if cell.ctype == 0:
                return ""
            elif cell.ctype == 1:
                return cell.value
            else:
                raise ValueError("Cell type must be empty or string (got %d)"%(cell.ctype))
        raise IndexError("Index outside bound of spreadsheet: %d,%d"%(row, col))

