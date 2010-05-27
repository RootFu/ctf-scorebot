#!/usr/bin/python -u

import os, random, time, sys, string, re, socket, urllib

from utility import pybrowse, browserpersonality, CtfUtil

def createUser(mainpage,flag):
	try:
		userPage = mainpage.click("cgi-bin/createuser.php")
		userPage.parse()
            
		userForm = userPage.forms[0];
            
		userName = CtfUtil.getRandomString(random.randint(6,8))
		firstName = CtfUtil.getRandomString(random.randint(6,8))
		lastName = CtfUtil.getRandomString(random.randint(6,8))
		password = CtfUtil.getRandomAlphaNum(8)
		email = flag
            
		userForm.fields['username'] = userName
		userForm.fields['lastname'] = lastName
		userForm.fields['firstname']= firstName
		userForm.fields['password'] = password
		userForm.fields['email'] = email
            
		resultPage = userForm.click(None)
		successPtr = resultPage.page.find("User successfully created!")

		if successPtr != -1:
			return userName,password
		else:
			sys.exit(-1)
                
	except Exception, e:
		print "ERROR: got exception %s creating user" % (e)
		sys.exit(-1)
            
def login(mainpage, userName, password):
	try:
		loginPage = mainpage.click("cgi-bin/login.php")
		loginPage.parse()
            
		loginForm = loginPage.forms[0]
		loginForm.fields['username'] = userName
		loginForm.fields['password'] = password
		resultPage = loginForm.click(None)
            
		successPtr = resultPage.page.find("successfully authenticated")
		if successPtr != -1:
			resultPage.parse()
			return resultPage.click("/~estore/index.html")
		else:
			sys.exit(-1)
                
	except Exception, e:
		print "ERROR: got exception %s logging in" % (e)
    
def logout(mainpage):
	try:
		logoutPage = mainpage.click("cgi-bin/logout.php")
		logoutPage.parse()
           
		for form in logoutPage.forms:
			if(form.buttons['decision'] == "Cancel Purchase and Logout"):
				resultPage = form.click('decision')
				successPtr = resultPage.page.find("successfully logged out")
				if successPtr != -1:
					return
				else:
					break
            
	except Exception, e:
		print "ERROR: got exception %s logging out" % (e)
            
def score(ip,flag,cookie):
	#get old flag  
	if cookie != None:
		try:
			userName,password = cookie.split(":")
                
			mainpage = pybrowse.Browser("http://" + ip + "/~estore/index.html")
			mainpage.open()
			mainpage.parse()
			loginMainPage = login(mainpage, userName, password)
			updatePage = loginMainPage.click("cgi-bin/update.php")
			updatePage.parse()
			updateForm = updatePage.forms[0]
			updateForm.fields['username'] = userName
			updateForm.fields['password'] = password
			updateForm.fields['email'] = CtfUtil.getRandomEmail() 
                
			resultPage = updateForm.click(None)
			successPtr = resultPage.page.find("address was:")

			if(successPtr != -1):
				oldFlag = resultPage.page[successPtr+13:][:len(flag)]
				print "FLAG:",oldFlag
 
			logout(loginMainPage)
                
		except Exception, e:
			print "ERROR: got exception %s getting flag" % (e)


	#set the new flag
	try:
		mainpage = pybrowse.Browser("http://" + ip + "/~estore/index.html")
		mainpage.open()
		mainpage.parse()
            
		userName,password = createUser(mainpage,flag)
		loginMainPage = login(mainpage, userName, password)
		logout(loginMainPage)
               
		cookie = userName+":"+password
		print "COOKIE:",cookie
 
	except Exception, e:
		print "ERROR: got exception %s setting new flag" % (e)

if __name__ == '__main__':
	CtfUtil.main(score)
