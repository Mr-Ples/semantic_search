#!/bin/bash

# Kill the Python process
pkill -9 -f index.py

# Start the Python server and redirect its output to a file
/usr/bin/python index.py  &

# Wait for the server to start up
sleep 5

# Establish a reverse SSH tunnel
jprq http 8089 -s "semantic-search"
