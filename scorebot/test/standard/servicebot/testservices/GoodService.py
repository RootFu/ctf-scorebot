#!/usr/bin/env python
import pickle
import sys
import os

#Useful function for using relative paths
def modulePath():
    return os.path.dirname(os.path.realpath( __file__ ))

#argv[1] == ip
#argv[2] == flag
#argv[3] == stored
assert(len(sys.argv) == 3 or len(sys.argv) == 4)

print sys.argv[1]
print sys.argv[2]

try:
	file = open(modulePath()+"/GoodService.flag")
	flag = pickle.load(file)
	print "FLAG:",flag
except:
	pass

file = open(modulePath()+"/GoodService.flag","w")
pickle.dump(sys.argv[2],file)
