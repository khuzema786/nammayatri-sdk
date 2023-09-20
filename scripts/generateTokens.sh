#!/bin/bash

# List of phone numbers
PHONE_NUMBERS=("6000000008" "7007007007" "7010437483" "7557200859" "7777777123" "7777777705" "7777777774" "7779841410" "7779898981" "7888888775" "7904281259" "8310736887" "8340123456" "8340505050" "8340834001" "8340834010" "8340834011" "8340834013" "8340834014" "8340834099" "8879591975" "8888886789" "8888888803" "8888888843" "8888888885" "9000000123" "9000000124" "9000020000" "9090909005" "9123643702" "9123643742" "9148729916" "9148729919" "9164990000" "9164990002" "9182038110" "9222222220" "9222222228" "9222222231" "9276544443" "9380357679" "9380357879" "9380358679" "9629811769" "9642000006" "9642400000" "9642400001" "9642400004" "9642429378" "9671102079")

# Iterate over each phone number
for phone_number in "${PHONE_NUMBERS[@]}"; do
  # Send a POST request to the first endpoint with the phone number
  response=$(curl -s -X POST "https://api.sandbox.beckn.juspay.in/dobpp/ui/auth" --header 'Content-Type: application/json' --data "{ \"mobileNumber\": \"$phone_number\", \"mobileCountryCode\": \"+91\", \"merchantId\": \"7f7896dd-787e-4a0b-8675-e9e6fe93bb8f\" }")
  authId=$(echo "$response" | jq -r '.authId')

  # Send a POST request to the second endpoint with the extracted authId
  response=$(curl -s -X POST "https://api.sandbox.beckn.juspay.in/dobpp/ui/auth/$authId/verify" --header 'Content-Type: application/json' --data "{ \"otp\": \"7891\", \"deviceToken\": \"8e83b5dc-99a0-4306-b90d-2345f3050ddd972\" }")
  token=$(echo "$response" | jq -r '.token')

  # Send a POST request to the second endpoint with the extracted authId
#   response=$(curl -s -X POST "https://api.sandbox.beckn.juspay.in/dobpp/ui/auth/$authId/verify" --header "token: $token" --header "vt: AUTO_RICKSHAW" --header "mId: 7f7896dd-787e-4a0b-8675-e9e6fe93bb8f" --header "Content-Type: application/json" --data "[{ \"pt\": { \"lat\":  13.21105683994044, \"lon\": 77.86952343480942 }, \"ts\": \"2023-09-11T11:51:42+00:00\", \"acc\": 0}]")
#   token=$(echo "$response" | jq -r '.token')

  echo "\"$token\","
done
