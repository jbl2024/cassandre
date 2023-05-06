#!/bin/bash

# Start script 1
make docker &
pid1=$!
sleep 5
# Start script 2
make runserver_dev &
pid2=$!

make run_celery &
pid3=$!

# Start script 3
make runtailwind_dev &
pid4=$!

# Wait for all scripts to finish
wait $pid1 $pid2 $pid3 $pid4