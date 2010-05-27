#!/usr/bin/python -u
import os, random, time, sys, string, re, socket, urllib

from utility import pybrowse, browserpersonality, CtfUtil

def score(ip,flag,cookie):
	#get old flag  
	if cookie != None:
		try:
			name,password = cookie.split(":")

			personality = browserpersonality.getRandomPersonality()
			mainpg = pybrowse.Browser("http://" + ip + "/~diebald/cgi-bin/admin", personality)
			mainpg.open()
			mainpg.parse()

			getTaskForm = mainpg.forms[2]
			getTaskForm.fields['username'] = name
			getTaskForm.fields['password'] = password                
			resultPage = getTaskForm.click(None)

			successPtr = resultPage.page.find("pre")
			if successPtr != -1:
				oldFlag = resultPage.page[successPtr+5:][:len(flag)]
				print "FLAG:",oldFlag

		except Exception, e:
			print "ERROR: got exception %s getting flag" % (e)

	#set the new flag
	try:
		personality = browserpersonality.getRandomPersonality()
		mainpg = pybrowse.Browser("http://" + ip + "/~diebald/cgi-bin/admin", personality)
		mainpg.open()
		mainpg.parse()

		name = CtfUtil.getRandomString(random.randint(6,8))
		password = CtfUtil.getRandomAlphaNum(6)

		createUserForm = mainpg.forms[0]
		createUserForm.fields['username'] = name
		createUserForm.fields['password'] = password
		resultPage = createUserForm.click(None)

		successPtr = resultPage.page.find("Account successfully created")
		if successPtr == -1:
			print "ERROR: Could not post new flag."
			return

		addTaskForm = mainpg.forms[1]
		addTaskForm.fields['username'] = name
		addTaskForm.fields['password'] = password
		addTaskForm.fields['task'] = flag
		resultPage = addTaskForm.click(None)

		successPtr = resultPage.page.find("was assigned to user")
		if successPtr == -1:
			print "ERROR: Could not post new flag."
			return

		cookie = name+":"+password
		print "COOKIE:",cookie

	except Exception, e:
		print "ERROR: got exception %s setting new flag" % ( e )

if __name__ == '__main__':
	CtfUtil.main(score)
