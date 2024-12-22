#!/bin/bash

# Define the folders to copy
folders=("goblin" "basic_cannon" "giant" "minion" "musketeer" "mini_pekka")

# Define the destination
destination="meow1:~/tmp/detector"

# Loop through each folder and copy it using scp
for folder in "${folders[@]}"; do
    scp -r "$folder" "$destination"
done
