#!/bin/bash

# Check if all required arguments are provided
if [ "$#" -ne 5 ]; then
  echo "Usage: $0 <mId> <vt> <token> <lat> <lon>"
  exit 1
fi

mId="$1"
vt="$2"
token="$3"
lat=$4
lon=$5

while true; do
    timestamp=$(date +"%Y-%m-%dT%H:%M:%S+00:00")
    response=$(curl --location 'https://api.sandbox.beckn.juspay.in/dobpp/ui/driver/location' \
    --header 'Content-Type: application/json;charset=utf-8' \
    --header 'Accept: application/json;charset=utf-8' \
    --header "vt: $vt" \
    --header "mId: $mId" \
    --header "token: $token" \
    --data "[
        {
            \"pt\": {
                \"lat\": $lat,
                \"lon\": $lon
            },
            \"ts\": \"$timestamp\",
            \"acc\": 1
        }
    ]")
    
    echo "[$timestamp] Response: $response"
    
    sleep 20  # Adjust the sleep duration as needed
done
