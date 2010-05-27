#!/usr/bin/env python
import random
import httplib
import urllib2
import urllib
import sys

users = [
	("Bob", "pass0"),
	("Sam", "pass1"),
	("Foo", "pass2"),
	("Bar", "pass3"),
]

def score(ip,flag,cookie):
	url = "http://%s:%d" % (ip,40404)
	try:
		page = urllib2.urlopen(url).read()
	except:
		print "ERROR: Could not connect"

	user,passwd = random.choice(users)

	params = urllib.urlencode({
		'user': user, 
		'pass': passwd, 
		'data' : flag, 
		'debug' : 'false'})
	try:
		conn = urllib2.urlopen(url,params)
		result = conn.read()
		index = result.find("old data was")
		if(index != -1):
			old_flag = result[index+12:].strip()
			print "FLAG:",old_flag
	except:
		print "ERROR: Could not post new flag"
	
def main():
	ip = sys.argv[1]
	flag = sys.argv[2]
	cookie = None

	if(len(sys.argv) == 4):
		cookie = sys.argv[3]

	score(ip,flag,cookie)

if __name__ == '__main__':
	main()
