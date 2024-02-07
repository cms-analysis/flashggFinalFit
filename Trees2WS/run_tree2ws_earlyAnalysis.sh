#!/bin/bash

# Thanks ChatGPT, you saved my sanity

# Define an array of input masses
inputMasses=(120 125 130)

# Define an array of eras
eras=("preEE" "postEE")

# Define an array of production modes and corresponding process strings
productionModes=("ggh:GluGluHtoGG" "vbf:VBFHtoGG" "vh:VHtoGG" "tth:ttHtoGG")

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
            python trees2ws.py --inputMass "$mass" --productionMode "$mode" --year 2022"$era" --doSystematics --inputConfig config_2022.py --inputTreeFile /net/scratch_cms3a/spaeh/private/PhD/analyses/early_Run3_Hgg/HiggsDNA/earlyRun3_production_v13/signal/earlyRun3_NTuples_Jan24_v13_signal_wSFs/root/"$process"_M-"$mass"_"$era"/*.root --outputWSDir "$outputDir"
        done
        
        # Check if ws_signal directory exists and is empty
        wsSignalDir="$outputDir/ws_signal"
        if [ ! -d "$wsSignalDir" ]; then
            mkdir -p "$outputDir"
        fi
        # Copy converted .root files into ws_signal directory
        cp "$outputDir"/ws_*/"$process"_M-*_"$era"/*.root "$wsSignalDir"

    done
done
