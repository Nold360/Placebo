#!/usr/bin/env python

import string, os, sys, socket, subprocess
from placebo_client import *

def help():
        print "Usage: "+sys.argv[0]+" <scan|add|update|get-key>"

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
elif "get-key" == sys.argv[1]:
	print "Getting public-Key..."
	command = "CLNT_GSK"

host =  get_config_parameter("adm_server")
port = int(get_config_parameter("adm_port")) 

if host == None:
	print "ERROR: No adm_server in /etc/placebo/client.conf"
	sys.exit(1)
elif port == None:
	print "ERROR: No adm_port in /etc/placebo/client.conf"
	sys.exit(1)


print host+":"+str(port)+" "+command
if command == "CLNT_SCN":
	if len(process_exists("clamscan -i -r "+path)) > 0:
		print "Already scanning \""+path+"\" - Exit"
		sys.exit(1)

try:
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((str(host), int(port)))
	print "Connected..."

	if command == "CLNT_SCN":
		msg = scan_file(path)
		ret = encrypt("CLNT_SCN\n"+path+"\n"+msg)
		s.send(ret)
	elif command == "CLNT_VSU":
		s.send(encrypt("CLNT_VSU"+update_virus_signatures()))
	elif command == "CLNT_NEW":
		s.send(new_host_request())
	elif command == "CLNT_GSK":
		s.send(command)

	ret = s.recv(65565)
	if ret[0] == "-": #Encrypted message
		ret = decrypt(ret)
		if ret[:-4] != clean_string("SRV_0000"):
			print "ERROR_CODE: "+ret[:-4]
			sys.exit(1)
		else:
			print "OK"
	else:
		if ret[:8] == "SRV_PUBK":
			add_public_key(ret[8:])
			print "OK"
	s.close()
except:
	print "ERROR: Can't connect to Host!"
	sys.exit(1)
	
sys.exit(0)
