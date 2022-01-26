#!/bin/bash
#All commands for setting up a new Droplet 

# Manually:
adduser cyrill
usermod -aG sudo cyrill


# before re-logging with my username, have to: 
sudo nano /etc/ssh/sshd_config
PasswordAuthentication yes
sudo service sshd restart

# Now you can log in from the new user. We're almost done.
mkdir ~/.ssh
nano ~/.ssh/authorized_keys # Paste your ssh public key here
sudo service sshd restart
sudo nano /etc/ssh/sshd_config  # Now disable password authentification again:
PasswordAuthentication no

# Automatically
sudo apt-get update
sudo apt install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
sudo apt update
apt-cache policy docker-ce
sudo apt install docker-ce
sudo systemctl status docker
sudo usermod -aG docker ${USER}
su - ${USER}


