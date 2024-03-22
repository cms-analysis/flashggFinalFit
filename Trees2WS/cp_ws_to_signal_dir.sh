#!/bin/bash


extract_bins() {
    local path="$1"
    local bins=()

    # Use find to search for folders matching the pattern ws_<proc>_<bins>
    while IFS= read -r folder; do
        # Append the folder name to the bins array
        bins+=("$folder")
    done < <(find "$path" -type d -name 'ws_*_*' 2>/dev/null)

    # Output the bins array
    printf '%s\n' "${bins[@]}"
}

# Check if the correct number of command-line arguments is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <path>"
    exit 1
fi

# Get the path from the command-line argument
path="$1"

# Define the gen-level bins
source_directories=($(extract_bins "$path"))


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
