#!/bin/bash
source common.sh

sudo apt-get install build-essential virtualenv

virtualenv $ENV_DIR
source $ENV_DIR/bin/activate
pip install -r requirements.txt