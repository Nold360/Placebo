#!/bin/bash

export hostname=$(hostname)

cat >plck <<EOF
Key-Type: DSA
Key-Length: 4096
Subkey-Type: ELG-E
Subkey-Length: 1024
Name-Real: $hostname 
Name-Comment: Placebo Daemon
Name-Email: placebo [at] dataport.de
Expire-Date: 0
%commit
EOF

gpg2 --batch --gen-key plck
echo "Generating done..."
#gpg --import --secret-keyring ./placebo.sec --keyring ./placebo.pub

#mv ./placebo.sec /etc/placebo/keypair/


#gpg2 --no-default-keyring --secret-keyring /etc/placebo/keypair/placebo.sec --keyring ./placebo.pub --export -a >> /etc/placebo/keypair/placebo.pub

rm ./placebo.pub ./placebo.sec ./plck

gpg --list-secret-keys
#gpg2 --no-default-keyring --secret-keyring /etc/placebo/keypair/placebo.sec --keyring ./placebo.pub --list-secret-keys
exit 0
