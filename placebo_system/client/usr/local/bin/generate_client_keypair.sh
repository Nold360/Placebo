#!/bin/bash

export hostname=$(hostname)

gpg --list-secret-keys | grep -q $(hostname)
if [ $? -eq 1 ] ; then

cat >plck <<EOF
Key-Type: DSA
Key-Length: 4096
Subkey-Type: ELG-E
Subkey-Length: 1024
Name-Real: $hostname 
Name-Comment: Placebo Daemon
Name-Email: placebo [at] localhost
Expire-Date: 0
%commit
EOF

	gpg2 --batch --gen-key plck
	rm  ./plck
	echo "Generating done..."
else
	echo -e "WARNING: Key already exists!\n"
fi

gpg --list-secret-keys
exit 0
