import struct
import hmac
import base64
import hashlib

from scorebot.common.thirdparty import xtea

class FlagParseException(Exception):
	
	def __init__(self,txt):
		self.flag_text = txt

	def __str__(self):
		return "Invalid Flag Text: "+self.flag_text

class Flag:

	def __init__(self,teamId,serviceId,round,timestamp):
		self.teamId = teamId
		self.serviceId = serviceId
		self.round = round
		self.timestamp = timestamp

class FlagManager:
	
	def __init__(self,key,iv,keyphrase):
		self.key = key
		self.phrase = keyphrase
		self.iv = iv

	def toTxt(self,flag):
		packed = struct.pack("<IIId",flag.teamId,flag.serviceId,flag.round,flag.timestamp)
		sig = hmac.new(self.phrase,packed,hashlib.md5).digest()
		enc = xtea.crypt(self.key,packed+sig,self.iv)
		return "FLG"+base64.urlsafe_b64encode(enc)
	
	def toFlag(self,txt):
		txt = txt.strip()
		size = struct.calcsize("<IIId")

		if(len(txt) <= 3+size):
			raise FlagParseException(txt)
		
		if(txt.startswith("FLG") == False):	
			raise FlagParseException(txt)

		try:
			enc = base64.urlsafe_b64decode(txt[3:])
			dec = xtea.crypt(self.key,enc,self.iv)
			packed = dec[:size]
			sig = dec[size:]
		except Exception as e:
			raise FlagParseException(str(e))

		if(sig != hmac.new(self.phrase,packed,hashlib.md5).digest()):
			raise FlagParseException(txt)

		teamId,serviceId,round,timestamp = struct.unpack("<IIId",packed)
		
		return Flag(teamId,serviceId,round,timestamp)		
