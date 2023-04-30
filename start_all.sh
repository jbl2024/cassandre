#!/bin/bash

# Start script 1
docker-compose up &
pid1=$!
sleep 5
# Start script 2
./run_local.sh &
pid2=$!

# Start script 3
make runtailwind_dev &
pid3=$!

# Wait for all scripts to finish
wait $pid1 $pid2 $pid3