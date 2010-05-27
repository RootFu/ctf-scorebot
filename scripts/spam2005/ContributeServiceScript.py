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
			getFlagUrl = ip+"/~contribute/cgi-bin/history.py?name="+cookie
			getFlagPage = pybrowse.Browser("http://" + getFlagUrl)
			getFlagPage.open()
            
			rawPage = getFlagPage.page
        
			successPattern = "address"
			successPtr = rawPage.find(successPattern)

			if successPtr >= 0:
				oldFlag = rawPage[successPtr+8:][:len(flag)]
				print "FLAG:",oldFlag
                
		except Exception, e:
			print "ERROR: got exception '%s' when getting flag" % (e)
			return
        
	#set new flag	
	try:
		randomName = CtfUtil.getRandomString(random.randint(6,8))
		
		url = ip+"/~contribute/contribute.html"
        
		mainpg = pybrowse.Browser("http://" + url)
		mainpg.open()
		mainpg = mainpg.doRedirects()
		mainpg.parse()
            
		form = mainpg.forms[0]
            
		form.fields['name'] = randomName
		form.fields['address'] = flag
		form.fields['cc'] = str(random.randint(10000000,99999999))
		form.fields['contribution'] = str(random.randint(1,9999))
            
		resultPage = form.click(None).page
            
		successPattern = "Your contribution id"
		successPtr = resultPage.find(successPattern)

		if successPtr < 0:
			print "ERROR: Failed to set new flag!"
			return
            
		cookie = randomName
		print "COOKIE:",cookie
            
	except Exception, e:
		print "ERROR: got exception '%s' when setting flag" % (e)
   
if __name__ == "__main__":
	CtfUtil.main(score) 
