#!/usr/bin/python -u

import os, random, time, sys, string, re, socket, urllib

from utility import pybrowse, browserpersonality, CtfUtil

def score(ip,flag,cookie): 
	#get old flag  
	if cookie != None:
		try:
			first,last = cookie.split(":")
			contactPage = pybrowse.Browser("http://" + ip + "/contact.html")
			contactPage.open()
			contactPage.parse()
                
			lookupForm = contactPage.forms[0]
			lookupForm.fields['cboname'] = last
                
			resultPage = lookupForm.click(None)
                
			successPtr = resultPage.page.find(first)
			if(successPtr != -1):
				oldFlag = resultPage.page[successPtr+14:][:len(flag)]
				print "FLAG:",oldFlag

		except Exception, e:
			print "ERROR: got exception %s getting flag" % (e)
         
	#set the new flag
	try:
		first = CtfUtil.getRandomString(5)
		last = CtfUtil.getRandomString(random.randint(6,8))
		ext = flag
            
		contactChangeUrl = ip+"/~contact/cgi-bin/contact_change.pl?login=admin&password=retard"+"&first="+first+"&last="+last+"&ext="+ext
		contactChangePage = pybrowse.Browser("http://" + contactChangeUrl)
		contactChangePage.open()
            
		successPtr = contactChangePage.page.find("Update Successful")
		if successPtr == -1:
			print "ERROR: Could not post new flag"
			return
            
		cookie = first+":"+last
		print "COOKIE:",cookie
 
	except Exception, e:
		print "ERROR: got exception %s setting new flag" % (e)
       
if __name__ == '__main__':
	CtfUtil.main(score) 
