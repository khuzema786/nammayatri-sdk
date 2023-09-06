#!/bin/bash

config_map_name="beckn-dhall-config-master"
namespace="atlas"
dhall_list=("common.dhall" "dynamic-offer-driver-app.dhall" "globalCommon.dhall" "provider-dashboard.dhall" "rider-app.dhall" "rider-dashboard.dhall")

# Create the directory to store the modified .dhall files
mkdir -p ./dhall

for dhall_file in "${dhall_list[@]}"; do
    dhall_file_modified=$(echo "$dhall_file" | sed 's/\.dhall/\\\.dhall/')

    # Retrieve the content of the specific .dhall file from the ConfigMap
    dhall_content=$(kubectl get configmap "$config_map_name" -n "$namespace" -o jsonpath="{.data.$dhall_file_modified}")

    # Perform text replacements
    dhall_content=$(echo "$dhall_content" | sed -e 's/_v2//g' -e 's/master/sandbox/g' -e 's/, cutOffHedisCluster = False/, cutOffHedisCluster = True/g' -e 's/percentEnable = 100/percentEnable = 0/g' -e 's/\/dev\//\//g' -e 's/, connectDatabase = +0/, connectDatabase = +2/g')

    # Save the modified content to a .dhall file in the 'dhall' directory
    echo "$dhall_content" > "./dhall/$dhall_file"
done
