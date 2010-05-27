#!/usr/bin/python -u
import os, random, time, sys, string, re, socket, urllib

from utility import pybrowse, browserpersonality, CtfUtil


def score(ip,flag,cookie):
	#get old flag  
	if cookie != None:
		try:
			name = cookie
			personality = browserpersonality.getRandomPersonality()
			resultPage = pybrowse.Browser("http://" + ip + ":8081/notes?username="+name, personality)
			resultPage.open();

			successPtr = resultPage.page.find("["+name+":")

			if successPtr != -1:
				oldFlag = resultPage.page[successPtr+len(name)+2:][:len(flag)]
				print "FLAG:",oldFlag

		except Exception, e:
			print "ERROR: got exception %s getting flag" % (e)

	#set the new flag
	try:
		personality = browserpersonality.getRandomPersonality()
		login = pybrowse.Browser("http://" + ip + ":8081/login", personality)
		login.open()
		login.parse()

		loginForm = login.forms[0]

		name = CtfUtil.getRandomString(random.randint(6,8))
		password = CtfUtil.getRandomAlphaNum(6)

		loginForm.fields['username'] = name
		loginForm.fields['password'] = password

		resultPage = loginForm.click(None)
		resultPage.parse()


		successPtr = resultPage.page.find("Login succeeded")
		if successPtr == -1:
			print "ERROR: Could not set new flag"
			return

		notes = resultPage.click(resultPage.links[0])
		notes.parse()

		noteForm = notes.forms[0]

		noteForm.fields['note'] = flag
		noteForm.fields['line'] = str(random.randint(1,100))
		noteForm.fields['character'] = str(random.randint(1,20))

		resultPage = noteForm.click(None)

		successPtr = resultPage.page.find("Note accepted")
		if successPtr == -1:
			print "ERROR: Could not set new flag"
			return

		cookie = name
		print "COOKIE:",cookie

	except Exception, e:
		print "ERROR: got exception %s setting new flag" % (e)

if __name__ == '__main__':
	CtfUtil.main(score)
