#!/usr/bin/python -u

import os, random, time, traceback, sys, string
from utility import pybrowse, browserpersonality, CtfUtil

retFlag = ""
retCookie = ""
myHost = ""
port = "8080"

def doLogin(user, passwd): 
	mainpg = pybrowse.Browser("http://" + myHost + "/Therapy/login.do")
	mainpg.open()
	mainpg.parse()
	loginForm = mainpg.forms[0]
	loginForm.fields['username'] = user
	loginForm.fields['password'] = passwd
	resultPage = loginForm.click(None)
	resultPage = resultPage.doRedirects()
        
	resultPage.parse()
	rawPage = resultPage.page
	successPtr = rawPage.find("Logout")
        
	if successPtr < 0:
		print "ERROR: Error logging in"
		sys.exit(2)
        
	return resultPage
    
def createAccount(name, passwd, role):
	global myHost
        
	mainpg = pybrowse.Browser("http://" + myHost + "/Therapy/createuser.do?role=" + role)
	mainpg.open()
	mainpg.parse()
        
	userform = mainpg.forms[0]
	userform.fields['firstname'] = CtfUtil.getRandomString(random.randint(4,10))
	userform.fields['lastname'] = CtfUtil.getRandomString(random.randint(5,10))
	userform.fields['email'] = CtfUtil.getRandomEmail()
	userform.fields['username'] = name
	userform.fields['password'] = passwd
	userform.fields['role'] = role
	resultPage = userform.click("submit")
	resultPage = resultPage.doRedirects()
	return resultPage
    
def score(ip,flag, cookie):
	global myHost

	myHost = ip + ":" + port
    
	username = ""
	password = ""
        
	# get old flag
	if cookie != None:
		try:    
			if cookie.find(':') != -1:
				username, password = cookie.split(":")
            
			personality = browserpersonality.getRandomPersonality()
			mainpg = pybrowse.Browser("http://" + myHost + "/Therapy/")
			mainpg.open()
			mainpg.parse()
                
			if mainpg.containsLink("/Therapy/login.do") == None:
				print "ERROR: no login.do link is found on the front page"
				return

			resultPage = doLogin(username, password)

			# view user's private information
			resultPage = resultPage.click(resultPage.links[9])
			resultPage.doRedirects()
			rawPage = resultPage.page
			successPtr = rawPage.find("addinfo")

			if successPtr >= 0:                
				oldFlag = rawPage[successPtr + 21:][:len(flag)]
				print "FLAG:",oldFlag
                
			# logout 
			resultPage.parse()
			resultPage = resultPage.click(resultPage.links[10])
			resultPage.doRedirects()
                
                
		except Exception, e:
			print "ERROR: got exception when getting flag: %s" % e
    	
	try:
		personality = browserpersonality.getRandomPersonality()
		mainpg = pybrowse.Browser("http://" + myHost + "/Therapy/")
		mainpg.open()
		mainpg.parse()
            
		# create a new user account
		username = CtfUtil.getRandomString(random.randint(6,10))
		password = CtfUtil.getRandomString(random.randint(4,10))

		resultPage = createAccount(username, password, "client")
            
		# login using the new account
		resultPage = doLogin(username, password)
		resultPage.parse()
            
		# go to story submission page
		resultPage = resultPage.click(resultPage.links[9])
		resultPage = resultPage.doRedirects()
		resultPage.parse()
            
		#print resultPage.page
		storyform = resultPage.forms[0]
		storyform.fields['story'] = "This is way too sad ..";
		storyform.fields['addinfo'] = flag 
		resultPage = storyform.click("submit")
		resultPage = resultPage.doRedirects( )
            
		rawPage = resultPage.page
		successPtr = rawPage.find("View or edit")
		if successPtr < 0:
			print "ERROR: Failed to retreive flag"
			return
            
		resultPage.parse()
            
		# go and view the submitted info
		resultPage = resultPage.click(resultPage.links[9])
		resultPage = resultPage.doRedirects()
		rawPage = resultPage.page
		successPtr = rawPage.find("addinfo")

		if successPtr < 0:
			print "ERROR: Failed to retreive flag"
			return
            
		resultPage.parse()
            
		# logout 
		if resultPage.containsLink("/Therapy/logout.do"):
			resultPage = resultPage.click("/Therapy/logout.do")
			resultPage = resultPage.doRedirects()
		else:
			print "ERROR: Logout failed."
			return
        
		cookie = username + ":" + password
		print "COOKIE:",cookie
		return 

	except Exception, e:
		print "ERROR: got exception when setting flag: %s" % e
		return

if __name__ == "__main__":
	CtfUtil.main(score)
