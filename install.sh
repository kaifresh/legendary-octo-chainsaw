#!/usr/bin/env bash

#/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)";
#brew install wget;
#wget

python3 ./setup/get-pip.py;

pip3 install -r ./setup/requirements.txt;

chmod 755 ./run.sh;