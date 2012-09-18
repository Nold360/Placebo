#!/usr/bin/env python

import string, sys, subprocess

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

#####################################################################################
# Sends data to socket and adds the "End" String for recv_end
#####################################################################################
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
        conf_file = open("/etc/placebo/client.conf", "r")
        for line in conf_file:
                if line[0] != "#":
                        if line.find(parameter) != -1:
                                conf_file.close()
                                return str(str(line.split("=")).split("\"")[1])
        conf_file.close()
        return -1


#####################################################################################
# Decrypts a message using the Private Keypair
#####################################################################################
def decrypt(enc_msg):
        command = "gpg --batch --quiet --decrypt << EOF\n"+enc_msg+"EOF"
        proc =  subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        return proc.communicate()[0]


#####################################################################################
# Encrypts a message using the "Placebo Server"'s PublicKey
#####################################################################################
def encrypt(msg):
        command = "gpg --batch --quiet --always-trust --encrypt -a -r \"Placebo Server\"<< EOF\n"+str(msg)+"EOF"
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        return proc.communicate()[0]


#####################################################################################
# Executes a clamscan on <path>
#####################################################################################
def scan_file(path):
        command = "clamscan -i -r "+path
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        return proc.communicate()[0]

#####################################################################################
# Calls the Signature Update
#####################################################################################
def update_virus_signatures():
        if get_config_parameter("vsig_server") != None and get_config_parameter("vsig_server") != "INTERNET":
                command = "/usr/local/bin/update_clam_signatures.sh"
        else:
                command = "/usr/local/bin/update_clam_signatures.sh INTERNET"
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        return proc.communicate()[0]


#####################################################################################
# Returns the public-key of the client
#####################################################################################
def get_public_key():
        command = "gpg --batch --quiet --export -a $(hostname)"
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        key = proc.communicate()[0]
        return key

#####################################################################################
# add's a public key to keychain
#####################################################################################
def add_public_key(key):
	command = "gpg  --no-verbose --quiet --batch -a --import << EOF\n"+str(key)+"EOF"
	proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
	return proc.communicate()[0]	

#####################################################################################
# Checkes Processes for running scans, updates,...
#####################################################################################
def process_exists(string):
	command = "ps -ef | grep '"+string+"' | grep -v grep"
	proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
	return proc.communicate()[0]

