#!/bin/bash

# Check if the correct number of command-line arguments is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <path>"
    exit 1
fi

# Get the path from the command-line argument
path="$1"

# Define the source directories
source_directories=("ws_GG2H" "ws_TTH" "ws_VBF" "ws_VH")

# Create the destination directory if it does not exist
destination_directory="$path/ws_signals"
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
