#!/bin/bash
#All commands for setting up a new Droplet 

# Manually:
adduser your_username
usermod -aG sudo your_username


# before re-logging with my username, have to: 
sudo nano /etc/ssh/sshd_config
PasswordAuthentication yes
sudo service sshd restart
# SSH has to be configured. 
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

# Then there was the issue with HTTPS (Which I resolved by installing the ufw:
# https://www.digitalocean.com/community/tutorials/how-to-set-up-a-firewall-with-ufw-on-ubuntu-18-04
# All issued commands
sudo nano /etc/default/ufw
IPV6=yes
sudo ufw default deny incoming
sudo ufw default allow outgoing
# You can check which profiles are currently registered:
sudo ufw app list
sudo ufw allow OpenSSH
sudo ufw enable #IMPORTANT
sudo ufw allow 80
sudo ufw allow 443
sudo ufw status verbose

# Output
# Available applications:
  # OpenSSH



# Useful curl commands
curl -I -L https://yourdomain.com

