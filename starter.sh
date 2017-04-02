#!/bin/bash
WORKSPACE_DIR=$HOME/boxer
PROJ_DIR=$HOME/boxer
CLIENT_DIR=$PROJ_DIR/client
SERVER_DIR=$PROJ_DIR/server
ENV_DIR=$PROJ_DIR/.env
PROJECT=boxer

sudo apt-get install build-essential virtualenv

virtualenv -p python3 $ENV_DIR
source $ENV_DIR/bin/activate
bower install
pip install -r requirements.txt