#!/bin/bash

# Define the ports to kill
ports_to_kill=(29092 2181 9090 6380 6381)

# Kill processes using the specified ports
for port in "${ports_to_kill[@]}"; do
  echo "Killing processes using port $port"
  pid=$(lsof -t -i:$port)
  if [ -n "$pid" ]; then
    kill -9 $pid
  fi
done

# Get a list of all .yaml files in the current directory
yaml_files=$(find "$(pwd)" -maxdepth 1 -type f -name "*.yaml")

# Loop through each .yaml file and run Docker Compose
for yaml_file in $yaml_files; do
    echo "Running Docker Compose for $yaml_file..."
    docker-compose -f "$yaml_file" up -d
done