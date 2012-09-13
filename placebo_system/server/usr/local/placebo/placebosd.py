#!/usr/bin/env python

import sys, os, time, atexit, array, string
from signal import SIGTERM 
from socket import *
from threading import Thread
import subprocess, MySQLdb

from placebo_server import *




class Daemon:
	def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
		self.stdin = stdin
		self.stdout = stdout
		self.stderr = stderr
		self.pidfile = pidfile
	
	def daemonize(self):
		"""
		do the UNIX double-fork magic, see Stevens' "Advanced 
		Programming in the UNIX Environment" for details (ISBN 0201563177)
		http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
		"""
		try: 
			pid = os.fork() 
			if pid > 0:
				# exit first parent
				sys.exit(0) 
		except OSError, e: 
			sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
			sys.exit(1)
	
		# decouple from parent environment
		os.chdir("/") 
		os.setsid() 
		os.umask(0) 
	
		# do second fork
		try: 
			pid = os.fork() 
			if pid > 0:
				# exit from second parent
				sys.exit(0) 
		except OSError, e: 
			sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
			sys.exit(1) 
	
		# redirect standard file descriptors
		sys.stdout.flush()
		sys.stderr.flush()
		si = file(self.stdin, 'r')
		so = file(self.stdout, 'a+')
		se = file(self.stderr, 'a+', 0)
		os.dup2(si.fileno(), sys.stdin.fileno())
		os.dup2(so.fileno(), sys.stdout.fileno())
		os.dup2(se.fileno(), sys.stderr.fileno())
	
		# write pidfile
		atexit.register(self.delpid)
		pid = str(os.getpid())
		file(self.pidfile,'w+').write("%s\n" % pid)
	
	def delpid(self):
		os.remove(self.pidfile)

	def start(self):
		"""
		Start the daemon
		"""
		# Check for a pidfile to see if the daemon already runs
		try:
			pf = file(self.pidfile,'r')
			pid = int(pf.read().strip())
			pf.close()
		except IOError:
			pid = None
	
		if pid:
			message = "pidfile %s already exist. Daemon already running?\n"
			sys.stderr.write(message % self.pidfile)
			sys.exit(1)
		
		# Start the daemon
		self.daemonize()
		self.run()

	def stop(self):
		"""
		Stop the daemon
		"""
		# Get the pid from the pidfile
		try:
			pf = file(self.pidfile,'r')
			pid = int(pf.read().strip())
			pf.close()
		except IOError:
			pid = None
	
		if not pid:
			message = "pidfile %s does not exist. Daemon not running?\n"
			sys.stderr.write(message % self.pidfile)
			return # not an error in a restart

		# Try killing the daemon process	
		try:
			while 1:
				os.kill(pid, SIGTERM)
				time.sleep(0.1)
		except OSError, err:
			err = str(err)
			if err.find("No such process") > 0:
				if os.path.exists(self.pidfile):
					os.remove(self.pidfile)
			else:
				print str(err)
				sys.exit(1)

	def restart(self):
		"""
		Restart the daemon
		"""
		self.stop()
		self.start()

	def run(self):
		##### MAIN #####
		port=int(get_config_parameter("srv_port"))
		host=get_config_parameter("srv_addr")
		addr=(host,port)

		serversocket = socket(AF_INET, SOCK_STREAM)
		serversocket.bind(addr)
		serversocket.listen(5)

		print "Placebo Server-Daemon started..."
		while 1: 
			try: 
				connection,address = serversocket.accept()
				hostname = str(get_hostname(address[0]))
				new_thread = proc_client_request(connection,address[0],hostname)
				new_thread.start()
		
			except KeyboardInterrupt:
				print "Dying..."
				serversocket.close()
				sys.exit(0)

		serversocket.close()


#####################################################################################
# Thread for processing Server requests
#####################################################################################
class proc_client_request(Thread, Daemon):
	def __init__ (self, connect, address, hostname):
		Thread.__init__(self)
		self.connect = connect
		self.address = address
		self.hostname = hostname
		#self.connect.settimeout(5)

	def run(self):
		connect = self.connect
		hostname = self.hostname
		address = self.address
		enc_msg = recv_end(connect)
		if enc_msg.split("\n")[0] == "-----BEGIN PGP MESSAGE-----":
			msg = decrypt(enc_msg)
			if msg != None:
				if clean_string(msg[0:8]) == "CLNT_SCN":
					path = msg[8:].split('\n')[1]
					summary=""
					for line in msg[8:].split('\n')[2:]:
						summary=summary+line+"\n"

					add_scan_to_db(hostname, path, summary)
					send_end(connect,encrypt("SRV_0000", hostname))
				elif clean_string(msg[0:8]) == "CLNT_VSU":
					add_signatures_to_db(hostname, str(msg[8:]))
					send_end(connect, encrypt("SRV_0000", hostname))
			else:
				send_end(connect,(encrypt("SRV_0001", hostname)))
		else: #Clean Message
			if clean_string(enc_msg[:8]) == "CLNT_NEW":
				add_server_to_db(hostname, address)
				add_public_key(str(enc_msg[8:]))
				send_end(connect, encrypt("CLNT_NEW"+get_public_key(),hostname))
				#ret = decrypt(recv_end(connect))
				#if ret == "CLNT_0000":
				#	print "OK"
				
			else:
				send_end(connect,"SRV_0001")
		connect.close()

daemon = Daemon("/var/run/placebosd.pid", "/dev/stdin", "/dev/stdout", "/dev/stderr")
daemon.start()


