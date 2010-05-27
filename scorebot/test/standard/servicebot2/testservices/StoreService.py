#!/usr/bin/env python
import sys

#argv[1] == ip
#argv[2] == flag
#argv[3] == stored
assert(len(sys.argv) == 3 or len(sys.argv) == 4)

if(len(sys.argv) == 3):
	print "COOKIE: Store Text"
else:
	assert(sys.argv[3] == "Store Text")
	print "COOKIE: Worked"
