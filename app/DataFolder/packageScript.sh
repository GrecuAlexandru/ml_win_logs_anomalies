#!/bin/bash

# Ubuntu package installation   

# Install the downloaded .deb packages
dpkg -i /usr/src/app/DataFolder/ubuntu_packages/*.deb

# Test that curl is successfully installed
if command -v curl &> /dev/null; then
    echo "curl is successfully installed."
else
    echo "curl installation failed."
    exit 1
fi

# Test that tshark is successfully installed
if command -v tshark &> /dev/null; then
    echo "tshark is successfully installed."
else
    echo "tshark installation failed."
    exit 1
fi

# Python package installation

# Activate the virtual environment
source /usr/src/app/venv/bin/activate

# Install pandas and its dependencies from the local directory
pip install --no-index --find-links=/usr/src/app/DataFolder/pandas_offline pandas

pip install --no-index --find-links=/usr/src/app/DataFolder/scapy_offline scapy

pip install --no-index --find-links=/usr/src/app/DataFolder/xgboost_offline xgboost

pip install --no-index --find-links=/usr/src/app/DataFolder/lightgbm_offline lightgbm

pip install --no-index --find-links=/usr/src/app/DataFolder/catboost_offline catboost

pip install --no-index --find-links=/usr/src/app/DataFolder/nltk_offline nltk

# Deactivate the virtual environment
deactivate