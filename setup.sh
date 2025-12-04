#!/bin/bash

echo "Installing Python packages..."
python3 -m pip install --upgrade pip
pip3 install -r requirements.txt

echo "Installing system tools..."
sudo apt update
sudo apt install -y speedtest-cli
