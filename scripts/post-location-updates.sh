#!/bin/bash

# Check if all required arguments are provided
# if [ "$#" -ne 5 ]; then
#   echo "Usage: $0 <mId> <vt> <token> <lat> <lon>"
#   exit 1
# fi

mId="7f7896dd-787e-4a0b-8675-e9e6fe93bb8f"
vt="AUTO_RICKSHAW"
token="0d3183be-bba3-4620-b7b9-0bc022da7158"
lat=12.935206758994692
lon=77.62451302145342

while true; do
    timestamp=$(date +"%Y-%m-%dT%H:%M:%S+00:00")

    # Generate random offsets for latitude and longitude within a 5km radius
    lat_offset=$(awk -v min=-0.045 -v max=0.045 'BEGIN{srand(); print min+rand()*(max-min)}')
    lon_offset=$(awk -v min=-0.045 -v max=0.045 'BEGIN{srand(); print min+rand()*(max-min)}')

    lat=$(echo "$lat + $lat_offset" | bc)
    lon=$(echo "$lon + $lon_offset" | bc)
    
    response=$(curl -s --location 'https://api.sandbox.beckn.juspay.in/dev/dobpp/ui/driver/location' \
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
    
    # echo "[$timestamp] ($lat, $lon) Response: $response"
    echo "($lat, $lon)"
    
    sleep 2  # Adjust the sleep duration as needed
done
