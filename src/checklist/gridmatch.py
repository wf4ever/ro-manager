# !/usr/bin/env python
#
# Combinator-based pattern matching for grid (e.g. spreadsheet) structures
#
# See: README.md in this directory
#

import os, os.path
import sys
import logging
import csv
import urlparse

log = logging.getLogger(__name__)

# from rocommand import ro_uriutils

class GridMatchError(Exception):
    """
    Class for reporting match failures
    """
    def __init__(self, msg="GridMatchError", value=None):
        self._msg    = msg
        self._value  = value
        return

    def __str__(self):
        txt = self._msg
        if self._value:  txt += ": "+repr(self._value)
        return txt

    def __repr__(self):
        return ( "GridMatchError(%s, value=%s)"%
                 (repr(self._msg), repr(self._value)))

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
            self._baseuri = self.resolveUri(uriref, self._baseuri)
        return self._baseuri
    def resolveUri(self, uriref):
        # return ro_uriutils.resolveUri(uriref, self._baseuri)
        return urlparse.urljoin(self._baseuri, uriref)
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
        return _grid.cell(_row, col)

class GridCSV(Grid):
    """
    Initialize a grid object based on a CSV file

    @param csvfile:     A file-like object that contains CSV data
    @param dialect:     An optional dialect parameter (e.g. 'excel', 'excel-tab').
                        If not specified, the system sniffs the content of the CSV 
                        to guess the CSV dialect used.
    """
    def __init__(self, csvname, csvfile, dialect=None):
        super(GridCSV, self).__init__(csvname)
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

class GridMatch(object):
    """
    Interface for gridmatch combinable parser
    """
    def match(self, grid, row, col):
        """
        Match something in a grid.

        @param grid:    Grid object to use for match
        @param row:     Row at which match starts
        @param col:     Column at which match starts
        @return     (result, (row, col))
            The value returned combines a dictionary of results with a new
            pair of (row, col) which indicates the next row and/or column 
            at which matching may continue.

        If the match fails, a GridMatchError exception is raised.
        """
        assert False, "Unimplemented 'match' method"

    def __add__(self, other):
        return GridMatchNextCol(self, other)

    def __floordiv__(self, other):
        return GridMatchNextRow(self, other)

    def __or__(self, other):
        return GridMatchAlt(self, other)

    def optional(self):
        return GridMatchOpt(self)

    def repeatdown(self, key, min=0, max=None):
        return GridMatchRepeatDown(self, key, min, max)

    def usebaseuri(self, other, key):
        return GridMatchBaseUri(self, other, key)

class GridMatchNextRow(GridMatch):
    """
    Match-next-row combinator
    """
    def __init__(self, t, b):
        self._t = t
        self._b = b
        return
    def match(self, grid, row, col):
        (rt,(rnew,cnew)) = self._t.match(grid, row, col)
        (rb,(rnew,cnew)) = self._b.match(grid, rnew, col)
        rt.update(rb)
        return (rt, (rnew, cnew))

# Combinator classes

class GridMatchNextCol(GridMatch):
    """
    Match-next-column combinator
    """
    def __init__(self, l, r):
        self._l = l
        self._r = r
        return
    def match(self, grid, row, col):
        (rl,(rnew,cnew)) = self._l.match(grid, row, col)
        (rr,(rnew,cnew)) = self._r.match(grid, row, cnew)
        rl.update(rr)
        return (rl, (rnew, cnew))

class GridMatchAlt(GridMatch):
    """
    Match-alternative combinator
    """
    def __init__(self, l, r):
        self._l = l
        self._r = r
        return
    def match(self, grid, row, col):
        try:
            (res,(rnew,cnew)) = self._l.match(grid, row, col)
        except Exception, e:
            (res,(rnew,cnew)) = self._r.match(grid, row, col)
        return (res, (rnew, cnew))

class GridMatchOpt(GridMatch):
    """
    Match-optional combinator
    """
    def __init__(self, m):
        self._m = m
        return
    def match(self, grid, row, col):
        try:
            return self._m.match(grid, row, col)
        except GridMatchError, e:
            pass
        return ({}, (row, col))

class GridMatchRepeatDown(GridMatch):
    """
    Downwards repeat combinator
    """
    def __init__(self, m, key="repeatdown", min=0, max=None):
        self._m   = m
        self._key = key
        self._min = min
        self._max = max if max else sys.maxint
        return
    def match(self, grid, row, col):
        log.debug("GridMatchRepeatDown.match %d, %d"%(row, col))
        resultlist = []
        count      = 0
        rnew       = row
        cmax       = col
        while count < self._max:
            log.debug("- rnew %d, cmax %d"%(rnew, cmax))
            try:
                (res,(rnew,cnew)) = self._m.match(grid, rnew, col)
                resultlist.append(res)
                if cnew > cmax: cmax = cnew
                count += 1
            except GridMatchError, e:
                savedexc = e
                break
        if count < self._min:
            raise Exception("Repeat down < min: %s"%(savedexc))
        return ({self._key: resultlist}, (rnew, cmax))


class GridMatchBaseUri(GridMatch):
    """
    Match second pattern with base URI selected by first.
    """
    def __init__(self, l, r, key):
        self._l   = l
        self._r   = r
        self._key = key
        return
    def match(self, grid, row, col):
        (rl,(rnew,cnew)) = self._l.match(grid, row, col)
        grid.baseUri(res[self._key])
        (rr,(rnew,cnew)) = self._r.match(grid, row, col)
        rl.update(rr)
        return (rl, (rnew, cnew))

# Match primitive classes

class text(GridMatch):
    """
    Match supplied text string
    """
    def __init__(self, t):
        self._t = t
        return
    def match(self, grid, row, col):
        if grid.cell(row, col) != self._t:
            raise GridMatchError("gridmatch.text not matched", (self._t,row,col))
        return ({}, (row+1, col+1))

class anyval(GridMatch):
    """
    Match any value in current cell, return as result is key given
    """
    def __init__(self, k=None):
        self._k = k
        return
    def match(self, grid, row, col):
        d = {self._k: grid.cell(row, col)} if self._k else {}
        return (d, (row+1, col+1))

class refval(GridMatch):
    """
    Match reference value in current cell, return as result is key given

    @@TODO: handle CURIE prefix expansion
    """
    def __init__(self, k=None):
        self._k = k
        return
    def match(self, grid, row, col):
        u = grid.resolveUri(grid.cell(row, col))
        d = {self._k: u} if self._k else {}
        return (d, (row+1, col+1))

class intval(GridMatch):
    """
    Match integer value in current cell, return as result is key given
    """
    def __init__(self, k=None):
        self._k = k
        return
    def match(self, grid, row, col):
        try:
            v = int(grid.cell(row, col))
        except Exception, e:
            raise GridMatchError("gridmatch.intval not matched", (grid.cell(row, col),row,col))
        d = {self._k: v} if self._k else {}
        return (d, (row+1, col+1))

class save(GridMatch):
    """
    Save current cell value, do not advance
    """
    def __init__(self, k):
        self._k = k
        return
    def match(self, grid, row, col):
        return ({self._k: grid.cell(row, col)}, (row, col))

class value(GridMatch):
    """
    Save supplied value, do not advance
    """
    def __init__(self, k, v):
        self._d = {k: v}
        return
    def match(self, grid, row, col):
        return (self._d, (row, col))

class error(GridMatch):
    """
    Do not match; raise error with supplied message and value
    """
    def __init__(self, msg="gridmatch.error", val=None):
        self._e = GridMatchError(msg, val)
        return
    def match(self, grid, row, col):
        raise self._e

# End.

