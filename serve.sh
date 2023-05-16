#!/bin/bash

# Kill the Python process
pkill -9 -f index.py
pkill -9 -f jprq

# Start the Python server and redirect its output to a file
nohup /usr/bin/python3 index.py  &

# Wait for the server to start up
sleep 5

# Establish a reverse SSH tunnel
jprq http 8089 -s "semantic-search" &

tail -f nohup.out
