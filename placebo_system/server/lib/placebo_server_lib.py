# -*- coding: utf-8 -*-

import subprocess, MySQLdb
from placebolib import Ticket
from re import escape


#####################################################################################
# returns hostname using System-DNS 
#####################################################################################
#FIXME
def get_hostname(ip):
        command = "host "+ip+" | cut -f5 -d' '| cut -f1 -d."
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        return clean_string(proc.communicate()[0])


class Database():
	def __init__(self, hostname, username, password, database):
		self.conn = MySQLdb.connect (host = hostname,
                                        user = username,
                                        passwd = password,
                                        db = database)

	#####################################################################################
	# Executes a mysql Statement and returns answer
	#####################################################################################
	def send_to_db(self,msg):
	        cursor = self.conn.cursor()
	        cursor.execute(msg)
	        result = cursor.fetchall()
	        cursor.close()
	        return result

	#####################################################################################
	# Adding Server to DB
	#####################################################################################
	def add_server_to_db(self, hostname, ip):
		if 1==1:
	        	self.send_to_db("INSERT INTO `client` (`ID`, `Hostname`, `IP`) VALUES (NULL, '"+str(hostname)+"', '"+str(ip)+"');")
			return True
	        else:
			return False

	#####################################################################################
	# Adding Scan-Summary to DB 
	#####################################################################################
	def add_scan_to_db(self, hostname, path, report):
	        id = self.send_to_db("SELECT ID FROM client WHERE Hostname = '"+hostname+"';")
	        if id[0][0] != None:
			self.send_to_db("DELETE FROM `report` WHERE Client_ID = "+str(id[0][0])+" and path = '"+str(path)+"' limit 1;")
	                self.send_to_db("INSERT INTO `report` (`Client_ID`, `Report`, `Path`) VALUES ('"+str(id[0][0])+"', '"+str(report)+"', '"+str(path)+"');")
			self.add_status_to_db(hostname, "OK")
	        else:
	                return False
	        return True

	#####################################################################################
	# Adding Signatures+Dates to DB 
	#####################################################################################
	def add_signatures_to_db(self, hostname, signatures):
	        id = self.send_to_db("SELECT ID FROM client WHERE Hostname = '"+hostname+"';")
	        if id[0][0] != None:
	                for signature in signatures.split('\n'):
				if clean_string(signature) != "":
	                        	self.send_to_db("DELETE FROM `signature` WHERE Client_ID = "+str(id[0][0])+" AND Signature = '"+str(clean_string(signature.split(";")[0]))+"';")
	                        	self.send_to_db("INSERT INTO `signature` (`Client_ID`, `Signature`, `Date`) VALUES ('"+str(id[0][0])+"', '"+str(clean_string(signature.split(";")[0]))+"', '"+str(signature.split(";")[1])+"');")
			self.add_status_to_db(hostname, "OK")
	        else:
	        	return False
	        return True

	#####################################################################################
	# Adding Client Status to DB 
	#####################################################################################
	def add_status_to_db(self, hostname, status):
		if status.find("socket.timeout") >= 0 or status.find("socket.error") >= 0:
			status_level=2
		elif status.find("CLNT_999") >= 0:
			status_level=1
		elif status.find("OK") >= 0:
			status_level=0
		else:
			return False
	
		id = self.send_to_db("SELECT ID FROM client WHERE Hostname = '"+hostname+"';")
	        if id[0][0] != None:
			try:
				exists = self.send_to_db("SELECT ID FROM status WHERE Client_ID = "+str(id[0][0])+";")[0][0]	
				self.send_to_db("UPDATE status SET `Status` = '"+str(status_level)+"' WHERE `Client_ID` = "+str(id[0][0])+";")
			except:
				self.send_to_db("INSERT INTO `status` (`ID`, `Client_ID`, `Status`) VALUES (NULL , '"+str(id[0][0])+"', '"+str(status_level)+"');")
		else:
			return False
		return True

	def add_ticket_to_db(self, hostname, ticket):
		id = self.send_to_db("SELECT ID FROM client WHERE Hostname = '"+hostname+"';")
		if id[0][0] != None:
			self.send_to_db("INSERT INTO `ticket` (`ID`, `Type_ID`, `Client_ID`, `Content`) VALUES ('"+str(ticket.get_ticket_id())+"', '"+str(ticket.get_type())+"', '"+str(id[0][0])+"', '"+str(ticket.get_content())+"');")
		return True


	#####################################################################################
	# Returns True if host is already added to DB 
	#####################################################################################
	def host_exists(self, host):
		try:
			hostname = self.send_to_db("SELECT Hostname FROM client WHERE Hostname = '"+host+"';")
			if not host in hostname[0][0]:
				return False
			else:
				return True
		except:
			return False


	def ticket_exists(self, id):
		try:
			#Makes checking for host-id any sense?
			ticket = self.send_to_db("SELECT * FROM `ticket` WHERE `ID` LIKE '"+str(id)+"' LIMIT 1;")
			if ticket[0][0]:
				return True
			else:
				return False
		except:
			return False

	def ticket_remove(self, id):
		#try:
		if 1:
			ret = self.send_to_db("DELETE FROM `ticket` WHERE `ticket`.`ID` = '"+str(id)+"'")
			return True
		#except:
		#	return False

	def ticket_move(self, id, content):
		#try
		if 1:
			ticket = self.send_to_db("SELECT Client_ID, Content, Type_ID FROM `ticket` WHERE `ID` LIKE '"+str(id)+"' LIMIT 1;")
			client_id = str(ticket[0][0])
			path = escape(ticket[0][1])
			type = int(ticket[0][2])
			if type != None:
				if type == Ticket.TYPE_SCAN:
					self.send_to_db("DELETE FROM `report` WHERE `Client_ID` = "+client_id+" AND `Path` LIKE '"+path+"';")
					self.send_to_db("INSERT INTO `report` (`ID`, `Client_ID`, `Path`, `Report`, `Date`) VALUES (NULL, '"+client_id+"', '"+path+"', '"+content+"', CURRENT_TIMESTAMP);")
				elif type == Ticket.TYPE_UPDATE:
					self.send_to_db("DELETE FROM `signature` WHERE `Client_ID` = "+client_id+";")
					for line in content.split("\n"):
						if line and line != "":
							line = escape(line)
							self.send_to_db("INSERT INTO `signature` (`ID`, `Client_ID`, `Signature`, `Date`) VALUES (NULL, \""+client_id+"\", \""+line+"\", CURRENT_TIMESTAMP);")
				else:
					return False

				return True
			else:
				return False





