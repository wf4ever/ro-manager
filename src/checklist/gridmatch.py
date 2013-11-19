# !/usr/bin/env python

"""
Combinator-based pattern matching for grid (e.g. spreadsheet) structures

See: README.md in this directory
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2013, University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os, os.path
import sys
import re
import logging
import csv
import urlparse

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# from rocommand import ro_uriutils

class GridMatchReport(Exception):
    """
    Class for reporting match failures
    """
    def __init__(self, msg="GridMatchReport", row=0, col=0, value=None):
        self._msg    = msg
        self._row    = row
        self._col    = col
        self._value  = value
        return

    def __str__(self):
        txt = "%s @[%d,%d]"%(self._msg, self._row, self._col)
        if self._value:  txt += ": "+repr(self._value)
        return txt

    def __repr__(self):
        return ( "GridMatchReport(%s (%d,%d), value=%s)"%
                 (repr(self._msg), self._row, self._col, repr(self._value)))

class GridMatchError(GridMatchReport):
    """
    Class for signalling recoverable match failures
    """
    def __init__(self, msg="GridMatchError", row=0, col=0, value=None):
        super(GridMatchError, self).__init__(msg=msg, row=row, col=col, value=value)        
        return

    def __repr__(self):
        return ( "GridMatchError(%s (%d,%d), value=%s)"%
                 (repr(self._msg), self._row, self._col, repr(self._value)))

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

    def repeatdown(self, key, min=0, max=None, dkey=None, dval=None):
        return GridMatchRepeatDown(self, key, min, max, dkey, dval)

    def skipdownto(self):
        return GridMatchSkipDown(self)

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

    @param min:     minimum number of repeats (default: 0)
    @param max:     maximum number of repeats (defaul: no limit)
    @param dkey:    field for resulting dictionary key
    @param dval:    field for resulting dictionary value

    If 'dkey' and 'dval' are defined, they are keys that are used to select values
    from the list of results, and construct a dictionary from the list.
    """
    def __init__(self, m, key="repeatdown", min=0, max=None, dkey=None, dval=None):
        self._m   = m
        self._key = key
        self._min = min
        self._max = max if max else sys.maxint
        self._dk  = dkey
        self._dv  = dval
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
            raise GridMatchError("Repeat down < min", rnew, col, str(savedexc))
        if self._dk and self._dv:
            res = dict( [ (r[self._dk], r[self._dv]) for r in resultlist ] )
        else:
            res = resultlist
        return ({self._key: res}, (rnew, cmax))

class GridMatchSkipDown(GridMatch):
    """
    Skip down over non matching rows until a match is found.
    Downwards matching continues with the matched item; mno m,atych result is returned.
    """
    def __init__(self, m):
        self._m   = m
        return
    def match(self, grid, row, col):
        log.debug("GridMatchSkipDown.match %d, %d"%(row, col))
        while True:
            log.debug("- row %d, col %d"%(row, col))
            try:
                self._m.match(grid, row, col)
                break
            except GridMatchError, e:
                savedexc = e
                row += 1
                continue
            except IndexError, e:
                raise GridMatchError("GridMatchSkipDown: target not found", row, col, str(savedexc))
        return ({}, (row, col))

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

class start(GridMatch):
    """
    Mark start of pattern - mainly to set GridMatch comntext for operators.
    """
    def __init__(self):
        return
    def match(self, grid, row, col):
        return ({}, (row, col))

class text(GridMatch):
    """
    Match supplied text string
    """
    def __init__(self, t):
        self._t = t
        return
    def match(self, grid, row, col):
        if grid.cell(row, col) != self._t:
            raise GridMatchError("gridmatch.text not matched", row, col, self._t)
        return ({}, (row+1, col+1))

class anyval(GridMatch):
    """
    Match any value in current cell, return as result if key given
    """
    def __init__(self, k=None):
        self._k = k
        return
    def match(self, grid, row, col):
        d = {self._k: grid.cell(row, col)} if self._k else {}
        return (d, (row+1, col+1))

class regexval(GridMatch):
    """
    Match any value that matches the supplied regexp, return as result if key given
    """
    def __init__(self, rex, k=None):
        self._r = rex
        self._k = k
        return
    def match(self, grid, row, col):
        v =  grid.cell(row, col)
        if not re.match(self._r, v):
            raise GridMatchError("gridmatch.regexval not matched", row, col, self._r)
        d = {self._k: v} if self._k else {}
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
        t = grid.cell(row, col)
        try:
            v = int(t)
        except Exception, e:
            raise GridMatchError("gridmatch.intval not matched", row, col, t)
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
        self._msg = msg
        self._val = val
        return
    def match(self, grid, row, col):
        raise GridMatchError(self._msg, row, col, self._val)

class trace(GridMatch):
    """
    Do not match; raise error with supplied message and value
    """
    def __init__(self, msg="gridmatch.trace", val=None):
        self._msg = msg
        self._val = val
        return
    def match(self, grid, row, col):
        raise GridMatchReport(self._msg, row, col, self._val)

# End.

