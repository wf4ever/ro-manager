#!/bin/env python

import sys
import re

p = "{ "
for l in sys.stdin.readlines():
    m = re.match(r"PREFIX\s*(\w*):\s*<([^>]*)>",l)
    if m:
        print '''%s"%s":%s"%s"'''%(p, m.group(1), (" "*(10-len(m.group(1)))), m.group(2))
        p = ", "
print "}"

