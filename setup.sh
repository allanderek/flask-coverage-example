#! /bin/sh

virtualenv -p python3 venv
source develop.sh
pip install -r requirements.text
npm install phantomjs
