#!/usr/bin/env python

import string, os, sys, socket, subprocess
from client import *

def help():
	print "Bla"



if len(sys.argv) < 3:
	help()
	sys.exit(0)

if "scan" == sys.argv[1][:4]:
	command = "CLNT_SCN"
	try: 
		path = str(sys.argv[1]).split(":")[1] 
	except:
		path = "/"	

	print "Scanning Server..."
	print "Path: "+path

elif "update" == sys.argv[1]:
	print "Updateing Server..."
	command = "CLNT_VSU"
elif "add" == sys.argv[1]:
	print "Adding Server..."
	command = "CLNT_NEW"

host = sys.argv[2]
if len(sys.argv) > 3:
	port = sys.argv[3]
else:
	port = 21337

print host+":"+port+" "+command

#try:
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((str(host), int(port)))
print "Connected..."

if command == "CLNT_SCN":
	ret = encrypt("CLNT_SCN\n"+path+"\n"+scan_file(path))
	s.send(ret)
elif command == "CLNT_VSU":
	s.send(encrypt("CLNT_VSU"+update_virus_signatures()))
elif command == "CLNT_NEW":
	s.send(new_host_request())

ret = decrypt(s.recv(65565))
if ret[:-4] != clean_string("SRV_0000"):
	print "ERROR_CODE: "+ret[:-4]
	sys.exit(1)
else:
	print "OK"
	sys.exit(0)
#except:
#	print "ERROR: Can't connect to Host!"
#	sys.exit(1)
	
sys.exit(0)
