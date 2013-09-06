#!/bin/bash
PLACEBO_TICKET_DIR="/var/placebo/tickets"
PLACEBO_HOME_DIR="/var/placebo"
PYTHON_LIB_DIR="/usr/lib/python2.7"

if [ "$PLACEBO_TICKET_DIR" == "" -a "$PLACEBO_HOME_DIR" == "" -a "$PYTHON_LIB_DIR" == "" ] ; then
	echo "Please edit this script to your needs"
	exit 1
fi

if [ $UID -ne 0 ] ; then
	echo "need to be root"
	exit 1
fi

if [ $# -lt 1 -o "$1" == "-h" ] ; then
	echo "Usage: $0 < -h | -i | -c > [SERVER]"
	echo "Description:"
	echo "             -h  | Show this help"
	echo "             -i  | Prepare Placebo enviroment"
	echo "             -c  | Check dependencies"
	echo "         SERVER  | If you want to install a Placebo Server"
	exit 1 
fi

if [ "$1" == "-i" ] ; then
	echo "Adding placebo-Group and User..."
	grep -q placebo /etc/group || groupadd placebo
	grep -q placebo /etc/passwd || useradd -s /bin/false -c"Placebo User" -d"$PLACEBO_HOME_DIR"-m -g placebo placebo

	echo "Creating $PLACEBO_TICKET_DIR"
	[ -d "$PLACEBO_TICKET_DIR" ] || mkdir -p "$PLACEBO_TICKET_DIR" 
	chown placebo:placebo "$PLACEBO_TICKET_DIR"

	echo "Copy files..."
	cp ./any/placebolib.py "$PYTHON_LIB_DIR"/
	
	mkdir -p /usr/share/placebo
	mkdir -p /etc/placebo
	if [ "$2" == "SERVER" ] ; then
		cp -v ./server/lib/* "$PYTHON_LIB_DIR"
		cp -v ./server/placebos2c.py /usr/local/bin/
		cp -v ./server/placebosd.py /usr/share/placebo/
		cp -v ./server/etc/placebo/server.conf /etc/placebo/
		chown placebo:placebo /etc/placebo/server.conf
	else	
		cp -v ./client/placeboc2s.py /usr/local/bin/
		cp -v ./client/placebocd.py /usr/share/placebo/
		cp -v ./client/etc/placebo/client.conf /etc/placebo/
		chown placebo:placebo /etc/placebo/client.conf
	fi

	echo "Generating GPG-Keypair.. This could take a while..."
	export hostname=$(hostname)
	if [ "$2" == "SERVER" ] ; then
		export GPG_NAME="Placebo Server"
	else
		export GPG_NAME="Placebo Client"
	fi

	gpg --list-secret-keys | grep -q $GPG_NAME
	if [ $? -ne 0 ] ; then
cat >plck <<EOF
Key-Type: DSA
Key-Length: 4096
Subkey-Type: ELG-E
Subkey-Length: 1024
Name-Real: $GPG_NAME
Name-Comment: $hostname
Name-Email: placebo [at] $hostname
Expire-Date: 0
%commit
EOF

		gpg --homedir $PLACEBO_HOME_DIR/.gnupg --batch --gen-key plck && rm ./plck
		echo "Generating done..."
	else
		echo "WARNING: Key already exists!"
	fi
fi

if [ "$1" == "-c" ] ; then
	grep -q placebo /etc/passwd || echo "placebo user dosn't exist"
	grep -q placebo /etc/group || echo "palcebo group dosn't exist"
	if [ "$2" == "SERVER" ] ; then
		 [ -d /etc/placebo -a -f /etc/placebo/client.conf ] || echo "/etc/placebo/* dosn't exist"
	else
		 [ -d /etc/placebo -a -f /etc/placebo/server.conf ] || echo "/etc/placebo/* dosn't exist"
	fi
	[ -d "$PLACEBO_TICKET_DIR" ] || echo "$PLACEBO_TICKET_DIR dosn't exist"
fi	

echo "Checking for python-libs..."
if [ "$2" == "SERVER" ] ; then
	python -c "import pyclamd, gnupg, placebolib,placebo_server_lib"
else
	python -c "import pyclamd, gnupg, placebolib"
fi
