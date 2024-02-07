#!/bin/bash

# Thanks ChatGPT, you saved my sanity

# Define an array of input masses
inputMasses=(120 125 130)

# Define an array of eras
eras=("preEE" "postEE")

# Define an array of production modes and corresponding process strings
productionModes=("ggh:GluGluHtoGG" "vbf:VBFHtoGG" "vh:VHtoGG" "tth:ttHtoGG")

# Check if path argument is provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <path_to_root_files>"
    exit 1
fi

path_to_root_files="$1"

# Function to check if a directory is empty
is_directory_empty() {
    local dir="$1"
    if [ -z "$(ls -A "$dir")" ]; then
        return 0  # Directory is empty
    else
        return 1  # Directory is not empty
    fi
}

# Loop over the production modes, eras, and input masses
for modeString in "${productionModes[@]}"; do
    # Split the modeString into mode and process
    IFS=':' read -r -a modeArray <<< "$modeString"
    mode="${modeArray[0]}"
    process="${modeArray[1]}"
    
    for era in "${eras[@]}"; do
        # Create output directory if it doesn't exist
        outputDir="../input_output_2022$era"
        if [ ! -d "$outputDir" ]; then
            mkdir -p "$outputDir"
        fi
        
        for mass in "${inputMasses[@]}"; do
            python trees2ws.py --inputMass "$mass" --productionMode "$mode" --year 2022"$era" --doSystematics --inputConfig config_2022.py --inputTreeFile "$path_to_root_files"/"$process"_M-"$mass"_"$era"/*.root --outputWSDir "$outputDir"
        done
    done
done
