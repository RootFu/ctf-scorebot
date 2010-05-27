#!/usr/bin/python -u

"""
http://<server>/~copyright/cgi-bin/account.php

COOKIE is <email>:<password>
(POST)

first=<flag>&email=<email>&password=<password>

This stores a new flag under ID <email>

http://<server>/~copyright/cgi-bin/login.php
(POST)
email=<email>&password=<password>

This logs in and creates the cookie

http://<server>/~copyright/cgi-bin/upload.php
This stores a new file (functionality check only)

http://<server>/~copyright/cgi-bin/star.php
This returns the flag as the first name in the Hello line

"""


import os, random, time, sys, string, re, socket, urllib
import httplib

from utility import pybrowse, browserpersonality, CtfUtil

def execution_path(filename):
	return os.path.join(os.path.dirname(sys._getframe(1).f_code.co_filename), filename)

def post_multipart(host, selector, fields, files, cookie):
	content_type, body = encode_multipart_formdata(fields, files)
	h = httplib.HTTPConnection(host)  
	headers = {
		'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686;) Firefox/2.0.0.6',
		'Cookie': cookie,
		'Content-Type': content_type
           }
	h.request('POST', selector, body, headers)
	res = h.getresponse()
	return res.status, res.reason, res.read()    
    
    
def encode_multipart_formdata(fields, files):
	"""
	fields is a sequence of (name, value) elements for regular form fields.
	files is a sequence of (name, filename, value) elements for data to be uploaded as files
	Return (content_type, body) ready for httplib.HTTP instance
	"""

	BOUNDARY = '----------8506126151759583858729434387'
	CRLF = '\r\n'
	L = []
	for (key, value) in fields:
		L.append('--' + BOUNDARY)
		L.append('Content-Disposition: form-data; name="%s"' % key)
		L.append('')
		L.append(value)

	for (key, filename, value) in files:
		L.append('--' + BOUNDARY)
		L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
		L.append('Content-Type: %s' % get_content_type(filename))
		L.append('')
		L.append(value)
	L.append('--' + BOUNDARY + '--')
	L.append('')
	body = CRLF.join(L)
	content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
	return content_type, body
    
def get_content_type(filename):
	#return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
	return 'application/octet-stream'
     
def getRandomSentence(len):
	ret = ""
	for i in range(len):
		ret += CtfUtil.getRandomString(random.randint(1,8)) + " "
	return ret
     
def score(ip,flag,cookie):
	# get old flag
	oldFlag = ""
	if cookie != None:
		(myemail, mypassword) = cookie.split(':');
		try:
			personality = browserpersonality.getRandomPersonality()
			mainpg = pybrowse.Browser("http://" + ip + "/Site/Sound_of_music.html")
			mainpg.open()

			# Logs in
			mainpg = pybrowse.Browser("http://" + ip + "/Site/Sound_of_music_files/widget2_markup.html")
			mainpg.open()
			mainpg.parse()
    
			qForm = mainpg.forms[0]
			qForm.fields["email"] = myemail 
			qForm.fields["password"] = mypassword
                
			resultingPage = qForm.click( None )
			resultingPage = resultingPage.doRedirects( )
    
			successPtr = resultingPage.page.find("successfully authenticated")
			if successPtr == -1:
				oldFlag = ""
			else:
				mainpg = pybrowse.Browser("http://" + ip + "/Site/Sound_of_music.html")
				mainpg.open()
				mainpg.parse()
				resultingPage = pybrowse.Browser("http://" + ip + "/~copyright/cgi-bin/star.php", resultingPage.personality, resultingPage.referer, resultingPage.cookies)

				resultingPage.open()
				resultingPage.parse()
				successPtr = resultingPage.page.find("Hello ")
				if successPtr != -1:
					oldFlag = resultingPage.page[successPtr+6:][:len(flag)]
				else:
					oldFlag = ""
                    
			print "FLAG:",oldFlag

		except Exception, e:
			print "ERROR: got exception [%s] getting flag" % (e)
			sys.exit(1)
                
        
	# set the new flag
	try:
		personality = browserpersonality.getRandomPersonality()
		mainpg = pybrowse.Browser("http://" + ip + "/Site/Sound_of_music.html")
		mainpg.open()
		mainpg = pybrowse.Browser("http://" + ip + "/Site/Sound_of_music_files/widget1_markup.html")
		mainpg.open()
		mainpg.parse()

		qForm = mainpg.forms[0]
		myfirst =flag 
		mylast = CtfUtil.getRandomString(random.randint(3,10))
		myemail = CtfUtil.getRandomEmail()
		mypassword = CtfUtil.getRandomString(random.randint(3,10))
            
		qForm.fields["first"] = myfirst
		qForm.fields["last"] = mylast
		qForm.fields["email"] = myemail
		qForm.fields["password"] = mypassword
            
		cookie = qForm.fields["email"] + ":" + qForm.fields["password"]
		resultingPage = qForm.click(None)
		resultingPage = resultingPage.doRedirects()
		successPtr = resultingPage.page.find("successfully created")

		if successPtr == -1:
			print "ERROR: Error setting new flag"
			return

		print "COOKIE:",cookie

	except Exception, e:
		print "ERROR: got exception %s setting flag" % (e)
		return

if __name__ == "__main__":
	CtfUtil.main(score)
