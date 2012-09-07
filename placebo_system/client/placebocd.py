#!/usr/bin/env python

import commands, os, array, string, sys
from socket import *
from threading import Thread
import subprocess

sys.path.append("/usr/local/lib/placebo")
from placebo_client import *

#####################################################################################
# Thread for processing Server requests
#####################################################################################
class proc_server_request(Thread):
	def __init__ (self, connect):
        	Thread.__init__(self)
        	self.connect = connect

	def run(self):
		connect = self.connect
		enc_msg = connect.recv(65565)
		if enc_msg.split("\n")[0] == "-----BEGIN PGP MESSAGE-----":
			msg = decrypt(enc_msg)
		elif clean_string(enc_msg) == "CLNT_NEW":
			print "new..."
			connect.send(new_host_request())
			return 0
		else:
			print "Error"
			sys.exit(1)	

		if clean_string(msg[0:8]) == "CLNT_SCN":
			print "scan.."
			enc_msg = encrypt("CLNT_000"+scan_file(clean_string(msg[8:-4])))
			connect.send(enc_msg)
		elif clean_string(msg[0:8]) == "CLNT_VSU":
			print "vsu..."
			ret = update_virus_signatures()		
			connect.send(encrypt("CLNT_000"+ret))
		else:
			connect.send(encrypt("CLNT_001"))
		connect.close()


##### MAIN #####
port=int(get_config_parameter("cln_port"))
host=get_config_parameter("cln_addr")
addr=(host,port)

serversocket = socket(AF_INET, SOCK_STREAM)
serversocket.bind(addr)
serversocket.listen(5)

while 1: 
    try: 
        connection,address = serversocket.accept()
	if str(address[0]) == get_config_parameter("adm_server"):
        	new_thread = proc_server_request(connection)
        	new_thread.start()
	else:
		connection.close()
		
    except KeyboardInterrupt:
        print "Exit"
	serversocket.close()
	sys.exit(0)
       
serversocket.close()

