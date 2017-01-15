#!/bin/bash
WORKSPACE_DIR=$HOME/boxer
PROJ_DIR=$HOME/boxer
CLIENT_DIR=$PROJ_DIR/client
SERVER_DIR=$PROJ_DIR/server
ENV_DIR=$PROJ_DIR/.env
PROJECT=boxer

tmux new-session -d -s $PROJECT
tmux attach-session $PROJECT

# Tmux config
tmux set -g mode-mouse on
tmux set -g mouse-select-pane on
tmux set -g mouse-resize-pane on
tmux set -g mouse-select-window on

# CopyPaste hotkeys for linux
tmux bind-key -n -t emacs-copy M-w copy-pipe "xclip -i -sel p -f | xclip -i -sel c "
tmux bind-key -n C-y run "xclip -o | tmux load-buffer - ; tmux paste-buffer"

tmux split-window -d -t 0 -v
tmux split-window -d -t 1 -h
tmux split-window -d -t 0 -h

fuser -k 5560/tcp
fuser -k 8080/tcp
fuser -k 9999/tcp

find . -name "*.pyc" -exec rm -rf {} \;

# zmq pair
tmux send-keys -t 1 'export ' PYTHONPATH=$WORKSPACE_DIR enter
tmux send-keys -t 1 $ENV_DIR'/bin/python '$SERVER_DIR'/queue_server.py' enter

# client
tmux send-keys -t 0 'export ' PYTHONPATH=$WORKSPACE_DIR enter
tmux send-keys -t 0 $ENV_DIR'/bin/python '$CLIENT_DIR'/run.py' enter

# websocket
tmux send-keys -t 3 'export ' PYTHONPATH=$WORKSPACE_DIR enter
tmux send-keys -t 3 $ENV_DIR'/bin/python '$SERVER_DIR'/websocket.py' enter

tmux select-pane -t 0

tmux attach
