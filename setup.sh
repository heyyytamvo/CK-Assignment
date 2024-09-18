#!/bin/bash
sudo apt update -y
sudo apt install -y python3-pip
sudo apt install -y python3.10-venv
sudo apt install -y awscli

sudo apt install -y npm

sudo apt install -y curl
sudo curl https://raw.githubusercontent.com/creationix/nvm/master/install.sh | bash
source ~/.bashrc
nvm install 20.11.0

sudo npm install -g aws-cdk