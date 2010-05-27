#!/usr/bin/python -u

import re
import random
import xmlrpclib
from utility import CtfUtil

hex = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A','B','C','D','E','F']

def genUser():
        
	fn = ["john", "joe", "jake", "horst", "franz", "detlef", "dietmar", "ingeborg", "angela", "george", "otto", "kalle", "jenna","bob","frank"];
	ln = ["doe", "mueller", "meier", "schmidt", "bush", "kerry", "merkel", "smith", "heinze", "schroedinger"]
	dom = ["sex", "drugs", "school", "rock", "computer", "unix", "service", "online", "live", "download", "old", "buy", "shop", "beer", "bong", "root","leet"]
	tld = ["gov","net","edu","com","org","de","us","uk","su"]
	delim = [".", "", "-"]
        
	name = ""
        
	name += random.choice(fn)
	name += random.choice(delim)
	name += random.choice(ln)
	name += "@"

	d = random.choice(delim)
	y = random.randint(2,4)

	for i in xrange(y):
		name += random.choice(dom)
		if(i < y-1):
			name += d

	name += "."+random.choice(tld)
	return name
    
def score(ip,flag,cookie):
	serverUrl = "http://"+ip+"/~spamdb/cgi-bin/server.php"
	server = xmlrpclib.Server(serverUrl)
        
	#Get old flag
	if cookie != None:
		try:
			user,password = cookie.split(":")
			oldFlag = server.spamdb.veryfy_data(user,password)
			print "FLAG:",oldFlag
		except Exception, e:
			print "ERROR: got exception '%s' when getting flag" % (e)
                
	#Set new flag
	try:
		user = genUser()
		password = server.spamdb.create_account(user)
		result = server.spamdb.upload_data(user, password, flag)
            
		cookie = user + ":" + password
		print "COOKIE:",cookie
    
		if(result != "OK"):
			print "ERROR: Did not receive OK from spamdb server!"
 
	except Exception, e:
		print "ERROR: got exception '%s' when setting flag" % (e)

if __name__ == "__main__":
	CtfUtil.main(score)
