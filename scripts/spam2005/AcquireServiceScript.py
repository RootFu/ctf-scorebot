#!/usr/bin/python -u

import httplib
import urllib
import re
import random
import sys

from utility import pybrowse, browserpersonality, CtfUtil

hex = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A','B','C','D','E','F']

def score(ip,flag,cookie):
	personality = browserpersonality.getRandomPersonality()
	if cookie != None:
		try:
			getFlagUrl = ip+"/~acquire/cgi-bin/get.php?ip="+cookie
			getFlagPage = pybrowse.Browser("http://" + getFlagUrl)
			getFlagPage.open()
            
			rawPage = getFlagPage.page
            
			successPattern = "entry was "
			successPtr = rawPage.find(successPattern)

			if successPtr < 0:
				print "ERROR: Failed to retrieve a flag!"

			else:
				oldFlag = rawPage[successPtr+48:][:len(flag)]
				print "FLAG:",oldFlag
                
		except Exception, e:
			print "ERROR: got exception '%s' when getting flag" % (e)
            
	#set new flag
	try:
		ipv6 = ""
        
		for i in range(32):
			ipv6 += random.choice(hex)
            
		setFlagUrl = ip+"/~acquire/cgi-bin/set.php?ip="+ipv6+"&net=ucsb&de="+urllib.quote(flag)
        
		mainpg = pybrowse.Browser("http://" + setFlagUrl)
		mainpg.open()
		resultPage = mainpg.page
            
		successPattern = "new spam relay"
		successPtr = resultPage.find(successPattern)

		if successPtr < 0:
			print "ERROR: Failed to post new flag!"
			return
            
		print "COOKIE:",ipv6
            
	except Exception, e:
		print "ERROR: got exception '%s' when setting flag" % e
		return

if __name__ == "__main__":
	CtfUtil.main(score)
