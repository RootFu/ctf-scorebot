from __future__ import with_statement
import sqlite3
import threading
import time
import datetime
import socket

from scorebot.attackengine.flagsubmissionbot.SubmitClient import SubmitClient

DB = None
dbLock = threading.Lock()

class FlagSubmitter:
	def __init__(self,db_path,logger,client):
		global DB

		DB = db_path
		self.logger = logger		
		self.db = Db()
		SubmitThread(logger,client)

	def submit(self,flag,exploit,team=None):
		result = self.db.insertFlag(flag,exploit,team)
		if result != None:
			self.logger.info("New flag %s from exploit %s, team %s"%(flag,exploit,team))

	def getFlagStats(self):
		return self.db.getFlagStats()	

class SubmitThread(threading.Thread):
	def __init__(self,logger,client):
		threading.Thread.__init__(self)
		self.logger = logger
		self.client = client
		self.setDaemon(True)
		self.start()

	def run(self):
		db = Db()
		
		while True:
			try:
				time.sleep(20)
				self.client.connect()

				for i in range(50):
					flag = db.getNewFlag()
					if flag != None:
						response = self.client.submit(flag)

						if(response == SubmitClient.VALID):	
							db.update(flag,Db.STATUS_SUCCESS,response)
							self.logger.info("Valid Flag! (%s)"  % flag)
						elif(response == SubmitClient.INVALID):		
							db.update(flag,Db.STATUS_ERROR,response)
							self.logger.info("Invalid Flag! (%s)"  % flag)
						"""
						if response.find("you captured a flag") >= 0:
							db.update(flag,Db.STATUS_SUCCESS,response)		
						elif len(response) > 0:
							db.update(flag,Db.STATUS_ERROR,response)
						"""

				self.client.quit()
			except Exception,e :
				self.logger.error("exception " + str(e))
				pass			
	

class Db:
	STATUS_NEW = "n"
	STATUS_ERROR = "e"
	STATUS_SUCCESS = "s"

	def __init__(self):
		self.conn = sqlite3.connect(DB)
		self.conn.text_factory = str

		with dbLock:
			c = self.conn.cursor()
			c.execute("CREATE TABLE IF NOT EXISTS flag(flag text, exploit text, status text, response text, made text, submitted text, team text)")
			self.conn.commit()
			c.close()

	def insertFlag(self,flag,exploit,team=None):
		with dbLock:
			c = self.conn.cursor()
				
			c.execute("SELECT flag FROM flag WHERE flag=?",(flag,))
			if c.fetchone() != None:
				c.close()
				return None

			c.execute("INSERT INTO flag(flag,exploit,status,made,team) VALUES(?,?,?,?,?)",(flag,exploit,"n",datetime.datetime.now(),team))
			self.conn.commit()
			c.close()

			return flag

	def update(self, flag, status, response=None):
		with dbLock:
			c = self.conn.cursor()
			c.execute("UPDATE flag SET status=?, submitted=?, response=? WHERE flag=?",(status,datetime.datetime.now(),response,flag))
			self.conn.commit()
			c.close()

	def getNewFlag(self):
		with dbLock:
			c = self.conn.cursor()
			c.execute("SELECT flag FROM flag WHERE status=? ORDER BY made DESC LIMIT 1",(Db.STATUS_NEW))
			row = c.fetchone()
			c.close()

			if row == None:
				return None

			return row[0]

	def getFlagStats(self):
		with dbLock:
			c = self.conn.cursor()
			c.execute("SELECT exploit,team,status,count(*) FROM flag GROUP BY exploit,team,status");
			stats = {}

			row = c.fetchone()
			while row != None:
				s = {}
				if (row[0], row[1]) in stats:
					s = stats[(row[0], row[1])]
				else:
					s = {'n':0, 'e':0, 's':0}

				s[row[2]] = row[3]
				stats[(row[0], row[1])] = s
				
				row = c.fetchone()

			self.conn.commit()
			c.close()

		l = []
		for (key, value) in stats.items():
			l.append((key[0], int(key[1]), value['n'], value['e'], value['s']))

		return l
