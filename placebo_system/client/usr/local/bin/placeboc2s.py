#!/usr/bin/env python

import string, os, sys, socket, subprocess
from placebo_client import *

def help():
        print "Usage: "+sys.argv[0]+" <scan|add|update>"

if len(sys.argv) < 2:
	help()
	sys.exit(0)

if "scan" == sys.argv[1][:4]:
	command = "CLNT_SCN"
	try: 
		path = str(sys.argv[1]).split(":")[1] 
	except:
		path = "/"	

	print "Scanning: "+path

elif "update" == sys.argv[1]:
	print "Updateing..."
	command = "CLNT_VSU"
elif "add" == sys.argv[1]:
	print "Adding..."
	command = "CLNT_NEW"

host =  get_config_parameter("adm_server")
port = int(get_config_parameter("adm_port")) 

if host == None:
	print "ERROR: No adm_server in /etc/placebo/client.conf"
	sys.exit(1)
elif port == None:
	print "ERROR: No adm_port in /etc/placebo/client.conf"
	sys.exit(1)


print host+":"+str(port)+" "+command
if command == "CLNT_SCN" and len(process_exists("clamscan -i -r "+path)) > 0:
	print "Already scanning \""+path+"\" - Exit"
	sys.exit(1)

try:
	ret = None
	if command == "CLNT_SCN":
		msg = scan_file(path)
		ret = encrypt("CLNT_SCN\n"+path+"\n"+msg)
	elif command == "CLNT_VSU":
		ret = encrypt("CLNT_VSU"+update_virus_signatures())
	
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((str(host), int(port)))
	print "Connected..."
	
	if ret != None:
		send_end(s,ret)
	elif command == "CLNT_NEW":
		send_end(s,"CLNT_NEW"+get_public_key())
		ret = decrypt(recv_end(s))
		if ret[:8] == "CLNT_NEW":
			add_public_key(ret[8:])
			send_end(s, "CLNT_000")
		else:
			print "ERROR: "+ret[:-4]
	else:
		print "ERROR"
		s.close()
		sys.exit(1)
		
	s.close()
except:
	print "ERROR: Can't connect to Host!"
	sys.exit(1)
	
sys.exit(0)
