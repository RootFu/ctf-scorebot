#!/usr/bin/python

import random
import string

class BrowserPersonality:
   def __init__(self, name, headers):
      self.name = name
      self.headers = headers

   def getHeaders(self, host, referer = None, clength = 0):
      ret = []
      for h in self.headers:
         (key,val) = h
         l = string.lower(key)
         if l == "host":
            ret.append((key, host))
         elif l == "referer":
            if referer:
               ret.append((key,referer))
         elif l == "content-type":
            if clength > 0:
               ret.append(h)
         elif l == "content-length":
            if clength > 0:
               ret.append((key,str(clength)))
         else:
            ret.append(h)

      return  ret



all_browsers = [ BrowserPersonality("Konquerror/ Linux",[
                                    ("Connection", "Keep-Alive"),
                                    ("User-Agent", "Mozilla/5.0 (compatible; Konqueror/3.3; Linux) (KHTML, like Gecko)"),
                                    ("Referer", "http://192.168.5.2:8000/"),
                                    ("Pragma", "no-cache"),
                                    ("Cache-control", "no-cache"),
                                    ("Accept", "text/html, image/jpeg, image/png, text/*, image/*, */*"),
                                    ("Accept-Encoding", "x-gzip, x-deflate, gzip, deflate"),
                                    ("Accept-Charset", "iso-8859-1, utf-8;q=0.5, *;q=0.5"),
                                    ("Accept-Language", "en"),
                                    ("Host", "192.168.5.2:8000"),
                                    ("Content-Type", "application/x-www-form-urlencoded"),
                                    ("Content-Length", "36") ]),

                 BrowserPersonality("Mozilla/ Linux",[
                                    ("Host", "192.168.5.2:8000"),
                                    ("User-Agent", "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.7.3) Gecko/20041008"),
                                    ("Accept", "text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5"),
                                    ("Accept-Language", "en-us,en;q=0.5"),
                                    ("Accept-Encoding", "gzip,deflate"),
                                    ("Accept-Charset", "ISO-8859-1,utf-8;q=0.7,*;q=0.7"),
                                    ("Keep-Alive", "300"),
                                    ("Connection", "keep-alive"),
                                    ("Referer", "http://192.168.5.2:8000/"),
                                    ("Content-Type", "application/x-www-form-urlencoded"),
                                    ("Content-Length", "36") ]),


                 BrowserPersonality("Firefox/ Linux",[           
                                    ("Host", "192.168.5.2:8000"),
                                    ("User-Agent", "Mozilla/5.0 (X11; U; Linux i686; rv:1.7.3) Gecko/20041001 Firefox/0.10.1"),
                                    ("Accept", "text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5"),
                                    ("Accept-Language", "en-us,en;q=0.5"),
                                    ("Accept-Encoding", "gzip,deflate"),
                                    ("Accept-Charset", "ISO-8859-1,utf-8;q=0.7,*;q=0.7"),
                                    ("Keep-Alive", "300"),
                                    ("Connection", "keep-alive"),
                                    ("Referer", "http://192.168.5.2:8000/"),
                                    ("Content-Type", "application/x-www-form-urlencoded"),
                                    ("Content-Length", "36") ]),


                 BrowserPersonality("Safari/ OSX",[
                                    ("Host", "192.168.5.2:8000"),
                                    ("Connection", "close"),
                                    ("Referer", "http://192.168.5.2:8000/"),
                                    ("User-Agent", "Mozilla/5.0 (Macintosh; U; PPC Mac OS X; en) AppleWebKit/125.5.5 (KHTML, like Gecko) Safari/125.11"),
                                    ("Accept", "*/*"),
                                    ("Accept-Encoding", "gzip, deflate;q=1.0, identity;q=0.5, *;q=0"),
                                    ("Accept-Language", "en, ja;q=0.92, ja-jp;q=0.96, fr;q=0.88, de-de;q=0.85, de;q=0.81, es;q=0.77, it-it;q=0.73, it;q=0.69, nl-nl;q=0.65, nl;q=0.62, sv-se;q=0.58, sv;q=0.54, no-no;q=0.50, no;q=0.46, da-dk;q=0.42, da;q=0.38, fi-fi;q=0.35, fi;q=0.31"),
                                    ("Content-Type", "application/x-www-form-urlencoded"),
                                    ("Content-Length", "36") ]),


                 BrowserPersonality("Explorer/ OSX",[
                                    ("Host", "192.168.5.2:8000"),
                                    ("Accept", "*/*"),
                                    ("Accept-Language", "en"),
                                    ("Pragma", "no-cache"),
                                    ("Connection", "Keep-Alive"),
                                    ("Referer", "http://192.168.5.2:8000/"),
                                    ("User-Agent", "Mozilla/4.0 (compatible; MSIE 5.23; Mac_PowerPC)"),
                                    ("UA-OS", "MacOS"),
                                    ("UA-CPU", "PPC"),
                                    ("Content-type", "application/x-www-form-urlencoded"),
                                    ("Extension", "Security/Remote-Passphrase"),
                                    ("Content-length", "36") ])
               ]

def getRandomPersonality():
   return random.choice(all_browsers)

### Main

#b = getRandomPersonality()
#print b.name + " " + str(b.getHeaders("localhost"))
                 
