import cPickle
import struct
import time
from scorebot.common.thirdparty import xtea

class MsgSequenceError(Exception):
	
	def __init__(self,seq,expected_seq):
		self.seq = seq
		self.expected_seq = expected_seq

	def __str__(self):
		return "Message sequence did not match! (%d != %d)" % (self.seq,self.expected_seq)

class BotMessage():
	REQ = 1
	RESP = 2
	NAN = 3

	def __init__(self,type,data,req_type=NAN,req_id=-1):
		self.type = type
		self.data = data
		self.req_type = req_type
		self.req_id = req_id

def toTxt(key,iv,seq,msg):
	assert(len(key) == 16)
	assert(len(iv) == 8)

	seq_txt = struct.pack('I',seq)
	pkl = cPickle.dumps(msg,cPickle.HIGHEST_PROTOCOL)
	txt = seq_txt + pkl.encode('zip')
	enc = xtea.crypt(key,txt,iv)
	result = enc.encode('base64').strip()
	return result

def fromTxt(key,iv,expected_seq,txt):
	seq_size = struct.calcsize('I')
	dec = xtea.crypt(key,txt.decode('base64'),iv)
	seq = struct.unpack('I',dec[:seq_size])[0]

	if(seq != expected_seq):
		raise MsgSequenceError(seq,expected_seq)

	pkl = dec[seq_size:].decode('zip')
	msg = cPickle.loads(pkl)
	return msg
