#!/bin/bash

# Redis server connection details
REDIS_HOST="localhost"
REDIS_PORT="6380"
REDIS_DB="0"

# Send TIME command before executing GEOADD and capture the result
START_TIME=$(redis-cli -h $REDIS_HOST -p $REDIS_PORT -n $REDIS_DB time | awk '{print $1$2}')

# Execute GEOADD command
redis-cli -h $REDIS_HOST -p $REDIS_PORT -n $REDIS_DB geoadd "mygeo" 77.86952343480942 13.21105683994044 "favorit-suv-000000000000000000000000"

# Send TIME command after executing GEOADD and capture the result
END_TIME=$(redis-cli -h $REDIS_HOST -p $REDIS_PORT -n $REDIS_DB time | awk '{print $1$2}')

# Calculate and print the latency in microseconds
LATENCY_MICROSECONDS=$((END_TIME - START_TIME))
echo "Latency: $LATENCY_MICROSECONDS microseconds"
