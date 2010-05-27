#!/usr/bin/python -u
import os, random, time, sys, string, re, socket, urllib

from utility import pybrowse, browserpersonality, CtfUtil

months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

def score(ip,flag,cookie):

	#get old flag
	if cookie != None:
		try:
			password, wwid = cookie.split(':')

			personality = browserpersonality.getRandomPersonality()
			mainpg = pybrowse.Browser("http://" + ip + "/~register/register.html", personality)
			mainpg.open()
			mainpg.parse()

			reviewForm = mainpg.forms[1]
			reviewForm.fields["password"] = password 
			reviewForm.fields["wwid"]  = wwid

			resultingPage = reviewForm.click(None)
			resultingPage = resultingPage.doRedirects()

			successPtr = resultingPage.page.find("name=\"wwid\"")

			if successPtr != -1:
				oldFlag = resultingPage.page[successPtr+19:][:len(flag)]
				print "FLAG:",oldFlag

		except Exception, e:
			print "ERROR: got exception %s getting flag" % (e)

	#set the new flag
	try:
		personality = browserpersonality.getRandomPersonality()
		mainpg = pybrowse.Browser("http://" + ip + "/~register/register.html", personality)
		mainpg.open()
		mainpg.parse()

		registrationForm = mainpg.forms[0]

		password = CtfUtil.getRandomAlphaNum(8)
		wwid = flag

		registrationForm.fields['first'] = CtfUtil.getRandomString(random.randint(5,7))
		registrationForm.fields['last'] = CtfUtil.getRandomString(random.randint(6,9))
		registrationForm.fields['dob'] = str(random.choice(months))+" "+str(random.randint(1,29))+", "+str(random.randint(1900,2000))
		registrationForm.fields['email'] = CtfUtil.getRandomEmail()
		registrationForm.fields['password'] = password
		registrationForm.fields['wwid'] = wwid

		resultingPage = registrationForm.click(None)

		successPtr = resultingPage.page.find("Registration successful!")

		if successPtr == -1:
			print "ERROR: Could not set new flag"
			return

		cookie = password+":"+wwid
		print "COOKIE:",cookie

	except Exception, e:
		print "ERROR: got exception %s setting new flag" % (e)

if __name__ == '__main__':
	CtfUtil.main(score)
