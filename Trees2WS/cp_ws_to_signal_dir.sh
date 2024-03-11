#!/bin/bash

# Check if the correct number of command-line arguments is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <path>"
    exit 1
fi

# Get the path from the command-line argument
path="$1"

# Define the source directories
source_directories=("ws_GG2H_in" "ws_GG2H_out" "ws_TTH_in" "ws_TTH_out" "ws_VBF_in" "ws_VBF_out" "ws_VH_in" "ws_VH_out")

# Create the destination directory if it does not exist
destination_directory="$path/ws_signal"
mkdir -p "$destination_directory"

# Iterate over each source directory and copy .root files to the destination
for source_dir in "${source_directories[@]}"; do
    source_path="$path/$source_dir"
    
    # Check if the source directory exists
    if [ -d "$source_path" ]; then
        # Copy .root files to the destination directory
        find "$source_path" -name "*.root" -exec cp {} "$destination_directory" \;
    else
        echo "Warning: Source directory $source_dir not found."
    fi
done

echo "Copy completed successfully."
