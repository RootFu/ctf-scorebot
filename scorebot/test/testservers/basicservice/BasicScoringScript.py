#!/usr/bin/env python

import httplib
import urllib2
import urllib
import sys

def score(ip,flag):
	url = "http://%s:%d" % (ip,60001)
	try:
		page = urllib2.urlopen(url).read()
	except:
		print "ERROR: Could not connect"

	flagPtr = page.index("<body>")
	if flagPtr != -1:
		oldFlag = page[flagPtr+6:][:len(flag)]
       	print "FLAG:",oldFlag
 
	params = urllib.urlencode({'flag': flag})
	try:
		conn = urllib2.urlopen(url,params)
	except:
		print "ERROR: Could not post new flag"

def main():
	ip = sys.argv[1]
	flag = sys.argv[2]
	stored = None

	if(len(sys.argv) == 4):
		stored = sys.argv[3]

	score(ip,flag)
		

if __name__ == '__main__':
	main()
