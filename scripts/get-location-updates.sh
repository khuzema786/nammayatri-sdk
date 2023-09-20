#!/bin/bash

# Check if all required arguments are provided
# if [ "$#" -ne 5 ]; then
#   echo "Usage: $0 <mId> <vt> <token> <lat> <lon>"
#   exit 1
# fi

token="e61fba99-b9df-4b08-9d1c-69892cd7b297"
ride_id="dbcb2c8c-d569-4af3-9ff9-d8e89a1991f2"

while true; do
    timestamp=$(date +"%Y-%m-%dT%H:%M:%S+00:00")
    
    response=$(curl -s --location --request POST "https://api.sandbox.beckn.juspay.in/dev/app/v2/ride/$ride_id/driver/location" \
    --header "token: $token")
    
    # echo "[$timestamp] Response: $response"
    echo "($(echo "$response" | jq -r '.lat'), $(echo "$response" | jq -r '.lon'))"
    
    sleep 2  # Adjust the sleep duration as needed
done
