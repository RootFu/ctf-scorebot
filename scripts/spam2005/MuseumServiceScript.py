#!/usr/bin/python -u

import httplib
import urllib
import random
import re

from utility import pybrowse, browserpersonality, CtfUtil

def score(ip,flag,cookie): 
        
	personality = browserpersonality.getRandomPersonality()
        
	if cookie != None:
		try:
			first,last = cookie.split(":")

			getFlagUrl = ip+"/~museum/cgi-bin/museum_admin.pl?first="+first+"&last="+last+"&password=unbreakable"
			getFlagPage = pybrowse.Browser("http://" + getFlagUrl)
			getFlagPage.open()
            
			rawPage = getFlagPage.page
                
			oldFlag = rawPage[253:][:len(flag)]
			print "FLAG:",oldFlag
 
		except Exception, e:
			print "ERROR: got exception '%s' when getting flag" % (e)
			return
        
	#set new flag
	try:
		first = CtfUtil.getRandomString(random.randint(6,8))
		last = CtfUtil.getRandomString(random.randint(6,8))
            
		idea = urllib.quote(flag)
		setFlagUrl = ip+"/~museum/cgi-bin/museum_upload.pl?first="+first+"&last="+last+"&dob=&ssn=&mmn=&email=&idea="+idea
        
		mainpg = pybrowse.Browser("http://" + setFlagUrl)
		mainpg.open()
		resultPage = mainpg.page

		successPattern = "Your idea has been received!!"
		successPtr = resultPage.find(successPattern)

		if successPtr >= 0:
			cookie = first+":"+last
			print "COOKIE:",cookie

	except Exception, e:
		print "ERROR: got exception '%s' when setting flag" % (e)

if __name__ == "__main__":
	CtfUtil.main(score)
