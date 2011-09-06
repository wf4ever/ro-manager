# $Id: Functions.py 1047 2009-01-15 14:48:58Z graham $
#
"""
Miscellaneous functions for use with Python code, 
mostly based on Haskell library elements.
"""

from operator import concat, and_, or_

def concatMap(f,vs):
    """
    Map function over list and concatenate results.
    """
    return reduce( concat, map (f, vs), "")

def fst((a,b)):
    """
    First element of a pair.
    """
    return a

def snd((a,b)):
    """
    Second element of a pair.
    """
    return b

def iterAll(c,sentinel=None):
    """
    Like the built-in 'iter' function, except that when the supplied container 
    has no more objects to return an indefinite sequence of 'sentinel' values is 
    returned. (This is almost the converse of built-in iter(c,sentinel).)
    """
    i = iter(c)
    try:
        while True: yield i.next()
    except StopIteration:
        while True: yield sentinel

def zipAll(*lists):
    """
    A zip-iterator that, unlike the built-in zip function, keeps on returning
    tuples until all elements of the supplied lists have been returned.  When
    the values from any list have been exhausted, None values are returned.
    The iterator stops when all lists have been exhausted.
    """
    iters = map(iterAll,lists)
    while True:
        result = [i.next() for i in iters]
        if allEq(None,result): break
        yield tuple(result)
    return

def isEq(v):
    """
    Return a function that tests for equality with the supplied value.
    (Curried equality function.)
    """
    return (lambda v2: v==v2)

def isNe(v):
    """
    Return a function that tests for inequality with the supplied value.
    (Curried inequality function.)
    """
    return (lambda v2: v!=v2)

def all_orig(f,c):
    """
    Do all members of c satisfy f?
    """
    for i in c: 
        if not f(i): return False
    return True

def all(p, *lsargs):
    """
    Test if all sets of members from supplied lists satisfy predicate p
    """
    return reduce(and_, map(p, *lsargs), True)

def any(p, *lsargs):
    """
    Test if all sets of members from supplied lists satisfy predicate p
    """
    return reduce(or_, map(p, *lsargs), False)

def allEq(v,c):
    """
    Are all members of c equal to v?
    """
    return all(isEq(v),c)

def allNe(v,c):
    """
    Are all members of c not equal to v?
    """
    return all(isNe(v),c)

def filterSplit(p, values):
    """
    Function filters a list into two sub-lists, the first containing entries
    satisfying the supplied predicate p, and the second of entries not satisfying p.
    """
    satp = []
    notp = []
    for v in values:
        if p(v):
            satp.append(v)
        else:
            notp.append(v)
    return (satp,notp)

def cond(cond,v1,v2):
    """
    Conditional expression.
    """
    if cond:
        return v1 
    else:
        return v2

def interleave(l1,l2):
    """
    Interleave lists.
    """
    if not l1: return l2
    if not l2: return l1
    return [l1[0],l2[0]]+interleave(l1[1:],l2[1:])

def endsWith(base,suff):
    """
    Test if list (sequence) ends with given suffix
    """
    return base[-len(suff):] == suff

def formatIntList(ints, sep=",", intfmt=str):
    """
    Format list of integers, using a supplied function to format each value,
    and inserting a supplied separator between each.
    
    Default comma-separated list of decimals.
    """
    return sep.join(map(intfmt, ints))

def formatInt(fmt):
    """
    returns a function to format a single integer value using the supplied
    format string.
    """
    def dofmt(n): return fmt % (n,)
    return dofmt

def formatList(lst,left=0,right=0):
    """
    Format a list over one or more lines, using the supplied margins.
    Left margin padding is *not* added to the first line of output,
    and no final newline is included following the last line of output.
    """
    # Try for format on one line
    out = formatList1(lst,right-left)
    if not out:
        # format over multiple lines
        out = "("
        pre = " "
        pad = "\n"+left*" "
        for i in lst:
            out += pre
            if isinstance(i,list) or isinstance(i,tuple):
                out += formatList(i, left+2, right)
            elif isinstance(i,dict):
                out += formatDict(i, left+2, right, left+2)
            else:
                out += repr(i)
            pre = pad+", "
        out += pad + ")"
    return out

def formatList1(lst,width):
    """
    Attempt to format a list on a single line, within supplied width,
    or return None if the list does not fit.
    """
    out = "("
    pre = ""
    ol  = 2
    for i in lst:
        o   = pre+repr(i)
        ol += len(o)
        if ol > width: return None
        pre  = ", "
        out += o
    return out+")"

def formatDict(dic,left=0,right=0,pos=0):
    """
    Format a dictionary over one or more lines, using the supplied margins.
    Left margin padding is *not* added to the first line of output,
    and no final newline is included following the last line of output.
    """
    # Try for format on one line
    out = formatDict1(dic,right-pos)
    if not out:
        # format over multiple lines
        out = "{"
        pre = " "
        pad = "\n"+left*" "
        for k in dic.keys():
            out += pre
            v    = dic[k]
            ks   = repr(k)+': '
            p    = pos+2+len(ks)
            if isinstance(v,dict):
                o = formatDict1(v, right-p)
                if not o:
                    o = pad + "  " + formatDict(v, left+2, right, left+2)
                out += ks + o
            elif isinstance(v,list) or isinstance(v,tuple):
                o = formatList1(v, right-p)
                if not o:
                    o = pad + "  " + formatList(v, left+2, right)
                out += ks + o
            else:
                out += ks + repr(v)
            pre  = pad+", "
            pos  = left+2
        out += pad + "}"
    return out

def formatDict1(dic,width):
    """
    Attempt to format a dictionary on a single line, within the supplied width,
    or return None if it does not fit.
    """
    out = "{"
    pre = ""
    ol  = 2
    for k in dic.keys():
        v  = dic[k]
        o  = pre + repr(k)+': '
        if isinstance(v,dict):
            vs = formatDict1(v,width)
            if not vs: return None
            o += vs
        elif isinstance(v,list) or isinstance(v,tuple):
            vs = formatList1(v,width)
            if not vs: return None
            o += vs
        else:
            o += repr(v)
        ol += len(o)
        if ol > width: return None
        pre  = ", "
        out += o
    return out+"}"

def compareLists(c1,c2):
    """
    Compare a pair of lists, returning None if the lists are identical, 
    or a pair of lists containing:
    (1) elements of first list not in second, and
    (2) elements of second list not in first list.
    """
    c1 = c1 or []
    c2 = c2 or []
    c1d = []
    c2d = []
    for c in c1: 
        if not (c in c2): c1d.append(c)
    for c in c2: 
        if not (c in c1): c2d.append(c)
    if c1d or c2d: return (c1d,c2d)
    return None

def compareDicts(d1,d2):
    """
    Return None if dictionaries are identical, or pair of lists containing
    entries in d1 not in d2, and entries in d2 not in d1.
    """
    dif1 = diffDicts(d1,d2)
    dif2 = diffDicts(d2,d1)
    if dif1 or dif2:
        return (dif1,dif2)
    else:
        return None

def diffDicts(d1,d2):
    """
    Return dictionary of entries in d1 that are not in d2.
    """
    difs = {}
    for (k,v1) in d1.iteritems():
        if v1:
            if k not in d2:
                difs[k] = v1
            else:
                d = diffPair(v1,d2[k])
                if nonEmpty(d):
                    difs[k] = d
    return difs

def diffLists(t1,t2):
    """
    Compares pairwise elements of 2 lists, and returns a list of elements
    in the first that are not in the second.
    Where the elements are dictionaries or tuples, the element difference is
    determined recursively, otherwise the value is treated atomically.
    """
    ps = zipAll(t1,t2)
    ds = filter(nonEmpty, [diffPair(a,b) for (a,b) in ps])
    return ds

def diffTuples(t1,t2):
    """
    Compares pairwise elements of 2 tuples, and returns a list of elements
    in the first that are not in the second.
    Where the elements are dictionaries or tuples, the element difference is
    determined recursively, otherwise the value is treated atomically.
    """
    return tuple(diffLists(t1,t2))
    
def diffPair(v1,v2):
    """
    Return the part of v1 that is not present in v2.
    Returns None if v11 and v2 are equal, or if every element of v1 is
    also present in v2.
    """   
    if isinstance(v1,tuple) and isinstance(v2,tuple):
        return diffTuples(v1,v2)
    if isinstance(v1,list) and isinstance(v2,list):
        return diffLists(v1,v2)
    if isinstance(v1,dict) and isinstance(v2,dict):
        return diffDicts(v1,v2)
    if v1!=v2:
        return v1
    return None

def nonEmpty(v):
    """
    If v is a container (tuple, list or dictionary), return None if it is empty,
    otherwise return v itself.
    """
    if isinstance(v,(tuple,list,dict)):
        if len(v) == 0: return None
    return v

# End.
