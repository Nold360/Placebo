#!/usr/bin/env python

import sys, subprocess, MySQLdb,string

#####################################################################################
#Thanks to John Nielsen
#http://code.activestate.com/recipes/408859-socketrecv-three-ways-to-turn-it-into-recvall/
#####################################################################################
End='EndOFTransmission'
def recv_end(the_socket):
	total_data=[];data=''
	while True:
		data=the_socket.recv(8192)
		if End in data:
			total_data.append(data[:data.find(End)])
			break
		if len(data) > 0:
			total_data.append(data)
		if len(total_data)>1:
			#check if end_of_data was split
			last_pair=total_data[-2]+total_data[-1]
			if End in last_pair:
				total_data[-2]=last_pair[:last_pair.find(End)]
				total_data.pop()
				break
	return ''.join(total_data)

def send_end(the_socket, data):
	the_socket.send(data+End)

#####################################################################################
# Cleans a String from whitespaces
#####################################################################################
def clean_string(oldString):
        newString = []
        for char in oldString:
                if char not in string.whitespace: newString.append(char)
        return ''.join(newString)

#####################################################################################
# Reads Config and returns a fitting parameter or -1
#####################################################################################
def get_config_parameter(parameter):
        conf_file = open("/etc/placebo/server.conf", "r")
        for line in conf_file:
                if line[0] != "#":
                        if line.find(parameter) != -1:
                                conf_file.close()
                                return str(str(line.split("=")).split("\"")[1])
        conf_file.close()
        return ""

#####################################################################################
# Decrypts a message using the Private Keypair
#####################################################################################
def decrypt(enc_msg):
        command = "gpg --no-permission-warning --homedir="+get_config_parameter('gpg_homedir')+" --batch --quiet --always-trust --decrypt << EOF\n"+enc_msg+"\nEOF"
        proc =  subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        return proc.communicate()[0]


#####################################################################################
# Encrypts a message using the "Placebo Server"'s PublicKey
#####################################################################################
def encrypt(msg,hostname):
        command = "gpg --no-permission-warning --homedir="+get_config_parameter('gpg_homedir')+" --batch --quiet --encrypt --always-trust -a -r \""+hostname+"\"<< EOF\n"+msg+"EOF"
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        return proc.communicate()[0]

#####################################################################################
# Adds PublicKey to Keychain 
#####################################################################################
def add_public_key(key):
        command = "gpg --no-permission-warning --homedir="+get_config_parameter('gpg_homedir')+" --batch --quiet -a --import << EOF\n"+key+"EOF"
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        return proc.communicate()[1]

#####################################################################################
# Executes a mysql Statement and returns answer
#####################################################################################
def send_to_db(msg):
        conn = MySQLdb.connect (host = get_config_parameter("mysql_host"),
                                user = get_config_parameter("mysql_user"),
                                passwd = get_config_parameter("mysql_passwd"),
                                db = get_config_parameter("mysql_db"))
        cursor = conn.cursor()
        cursor.execute(msg)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result

#####################################################################################
# Adding Server to DB
#####################################################################################
def add_server_to_db(hostname, ip):
	if 1==1:
        	send_to_db("INSERT INTO `client` (`ID`, `Hostname`, `IP`) VALUES (NULL, '"+str(hostname)+"', '"+str(ip)+"');")
		return True
        else:
		return False

#####################################################################################
# Adding Scan-Summary to DB 
#####################################################################################
def add_scan_to_db(hostname, path, report):
        id = send_to_db("SELECT ID FROM client WHERE Hostname = '"+hostname+"';")
        if id[0][0] != None:
		send_to_db("DELETE FROM `report` WHERE Client_ID = "+str(id[0][0])+" and path = '"+str(path)+"' limit 1;")
                send_to_db("INSERT INTO `report` (`Client_ID`, `Report`, `Path`) VALUES ('"+str(id[0][0])+"', '"+str(report)+"', '"+str(path)+"');")
		add_status_to_db(hostname, "OK")
        else:
                return False
        return True

#####################################################################################
# Adding Signatures+Dates to DB 
#####################################################################################
def add_signatures_to_db(hostname, signatures):
        id = send_to_db("SELECT ID FROM client WHERE Hostname = '"+hostname+"';")
        if id[0][0] != None:
                for signature in signatures.split('\n'):
			if clean_string(signature) != "":
                        	send_to_db("DELETE FROM `signature` WHERE Client_ID = "+str(id[0][0])+" AND Signature = '"+str(clean_string(signature.split(";")[0]))+"';")
                        	send_to_db("INSERT INTO `signature` (`Client_ID`, `Signature`, `Date`) VALUES ('"+str(id[0][0])+"', '"+str(clean_string(signature.split(";")[0]))+"', '"+str(signature.split(";")[1])+"');")
		add_status_to_db(hostname, "OK")
        else:
        	return False
        return True

#####################################################################################
# Adding Client Status to DB 
#####################################################################################
def add_status_to_db(hostname, status):
	if status.find("socket.timeout") >= 0 or status.find("socket.error") >= 0:
		status_level=2
	elif status.find("CLNT_999") >= 0:
		status_level=1
	elif status.find("OK") >= 0:
		status_level=0
	else:
		return False
	
	id = send_to_db("SELECT ID FROM client WHERE Hostname = '"+hostname+"';")
        if id[0][0] != None:
		try:
			exists = send_to_db("SELECT ID FROM status WHERE Client_ID = "+str(id[0][0])+";")[0][0]	
			send_to_db("UPDATE status SET `Status` = '"+str(status_level)+"' WHERE `Client_ID` = "+str(id[0][0])+";")
		except:
			send_to_db("INSERT INTO `status` (`ID`, `Client_ID`, `Status`) VALUES (NULL , '"+str(id[0][0])+"', '"+str(status_level)+"');")
	else:
		return False
	return True

#####################################################################################
# returns hostname using System-DNS 
#####################################################################################
def get_hostname(ip):
        command = "host "+ip+" | cut -f5 -d' '| cut -f1 -d."
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        return clean_string(proc.communicate()[0])

#####################################################################################
# Returns True if host is already added to DB 
#####################################################################################
def host_exists(host):
	try:
		hostname = send_to_db("SELECT Hostname FROM client WHERE Hostname = '"+host+"';")
		if hostname[0][0] != host:
			return False
		else:
			return True
	except:
		return False

#####################################################################################
# Returns the public-key of the server 
#####################################################################################
def get_public_key():
        command = "gpg --no-permission-warning --homedir="+get_config_parameter('gpg_homedir')+" --batch --quiet --export -a \"Placebo Server\""
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        key = proc.communicate()[0]
        return key
