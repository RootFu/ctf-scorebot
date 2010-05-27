#!/usr/bin/python -u

import ftplib, os

from utility import pybrowse, browserpersonality, CtfUtil

def flagCallback(line):
	print "FLAG:",line
        
def score(ip,flag,cookie):
	try:
		#Login to ftp
		ftp = ftplib.FTP(ip)
		ftp.login() 
		ftp.cwd("/home/ftp/incoming")
        
		if cookie != None:
			ftp.retrlines("RETR "+cookie,flagCallback)
            
		#set new flag
		filename = CtfUtil.getRandomString(9)
            
		file = open(filename,'w')
		file.write(flag)
		file.close();
            
		file = open(filename,'r')
		ftp.storlines("stor "+filename,file)
		file.close()
		os.remove(filename)

		cookie = filename
		print "COOKIE:",cookie
                
	except Exception, e:
		print "ERROR: Failed to set new flag!"

if __name__ == "__main__":
	CtfUtil.main(score)
