#!/usr/bin/python -u

import os, random, time, sys, string, re, socket, urllib

from utility import pybrowse, browserpersonality, CtfUtil

def createComment(ip,first,last,private,comment):
	mainpage = pybrowse.Browser("http://" + ip + "/feedback.html")
	mainpage.open()
	mainpage.parse()
            
	guestbookForm = mainpage.forms[0]
                    
	guestbookForm.fields['first'] = first
	guestbookForm.fields['last'] = last
	guestbookForm.fields['private'] = private
	guestbookForm.fields['comment'] = comment

	return guestbookForm.click(None)
        
def score(ip,flag,cookie):
	#get old flag          
	if cookie != None:
		try:
			first,last = cookie.split(":")
                
			guestPage = pybrowse.Browser("http://" + ip + "/~guestbook/cgi-bin/guestbook.pl?user="+first)
			guestPage.open()
			guestPage.parse()
                                                
			successPtr = guestPage.page.find(first+" "+last)
			if(successPtr != -1):
				oldFlag = guestPage.page[successPtr+len(first)+len(last)+31:][:len(flag)]
				print "FLAG:",oldFlag
                         
		except Exception, e:
			print "ERROR: got exception %s getting flag" % (e)

	#set the new flag
	try:
		first = CtfUtil.getRandomString(random.randint(6,8))  
		last = CtfUtil.getRandomString(random.randint(6,8))
            
		resultPage = createComment(ip,first, last, "yes", flag)
		successPtr = resultPage.page.find("has been received")
		if(successPtr == -1):
			print "ERROR: Could not post new flag"
			return
               
		cookie = first+":"+last
		print "COOKIE:",cookie

	except Exception, e:
		print "ERROR: got exception %s setting new flag" % (e)

if __name__ == '__main__':
	CtfUtil.main(score) 
