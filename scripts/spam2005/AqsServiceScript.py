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
			getFlagUrl = ip+"/~aqs/cgi-bin/guestbook.py?name="+cookie+"&command=lookup"
			getFlagPage = pybrowse.Browser("http://" + getFlagUrl)
			getFlagPage.open()
            
			rawPage = getFlagPage.page
                
			successPattern = cookie
			successPtr = rawPage.find(successPattern)

			if successPtr >= 0:
				successPtr += len(cookie)
				oldFlag = rawPage[successPtr+8:][:len(flag)]
				print "FLAG:",oldFlag
 
		except Exception, e:
			print "ERROR: got exception '%s' when getting flag" % (e)
			return
        
	#set new flag
	try:
		randomName = CtfUtil.getRandomString(random.randint(6,8))
            
		setFlagUrl = ip+"/~aqs/cgi-bin/guestbook.py?name="+randomName+"&comment="+flag+"&priv=on&command=sign"
        
		mainpg = pybrowse.Browser("http://" + setFlagUrl)
		mainpg.open()
		resultPage = mainpg.page
            
		successPattern = "Thanks for signing"
		successPtr = resultPage.find(successPattern)

		if successPtr < 0:
			print "ERROR: Failed to set flag"
			return
            
		cookie = randomName
		print "COOKIE:",cookie
            
	except Exception, e:
		print "ERROR: got exception '%s' when setting flag" % (e)
		return

if __name__ == "__main__":
	CtfUtil.main(score)
