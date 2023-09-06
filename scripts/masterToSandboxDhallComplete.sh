#!/bin/bash

config_map_name="beckn-dhall-config-master"  # Specify the desired ConfigMap name
namespace="atlas"
dhall_list=("common.dhall" "dynamic-offer-driver-app.dhall" "globalCommon.dhall" "provider-dashboard.dhall" "rider-app.dhall" "rider-dashboard.dhall")

# Create the directory to store the modified .dhall files
mkdir -p ./dhall

# Start creating the ConfigMap YAML file
config_map_yaml="apiVersion: v1
kind: ConfigMap
metadata:
  name: $config_map_name
  namespace: $namespace
data:"

for dhall_file in "${dhall_list[@]}"; do
    dhall_file_modified=$(echo "$dhall_file" | sed 's/\.dhall/\\\.dhall/')

    # Retrieve the content of the specific .dhall file from the ConfigMap
    dhall_content=$(kubectl get configmap "$config_map_name" -n "$namespace" -o jsonpath="{.data.$dhall_file_modified}")

    # Perform text replacements
    dhall_content=$(echo "$dhall_content" | sed -e 's/_v2//g' -e 's/master/sandbox/g' -e 's/, cutOffHedisCluster = False/, cutOffHedisCluster = True/g' -e 's/percentEnable = 100/percentEnable = 0/g' -e 's/\/dev\//\//g' -e 's/, connectDatabase = +0/, connectDatabase = +2/g')

    # Append the modified content to the ConfigMap YAML
    config_map_yaml="$config_map_yaml
  $dhall_file: |"
    
    # Append the indented content
    config_map_yaml="$config_map_yaml
$(echo "$dhall_content" | sed 's/^/    /')"
done

# Copy the generated ConfigMap YAML to the clipboard
echo "$config_map_yaml" | pbcopy
