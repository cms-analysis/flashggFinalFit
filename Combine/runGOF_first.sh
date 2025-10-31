#!/bin/bash

if [ $# -ne 1 ]; then
  echo "Usage: $0 <variable, eg. pt>"
  exit 1
fi

differential_variable="$1"

folder_name="runFits_${differential_variable}"

check_create_subfolder() {
    if [ ! -d "$folder_name" ]; then
        mkdir "$folder_name"
        mkdir "$folder_name/asimov"
        mkdir "$folder_name/combined"
        mkdir "$folder_name/unblinded"
        mkdir "$folder_name/SplusBModels_stage2"
        mkdir "$folder_name/SplusBModels_stage3"
        mkdir "$folder_name/impact"
        mkdir "$folder_name/impact_unblinded"
        mkdir "$folder_name/gof"
        mkdir "$folder_name/hesse"
        mkdir "$folder_name/hesse/Plots"
        echo "Folders '$folder_name' created successfully."
    else
        echo "Folders '$folder_name' already exists."
    fi
}

# Check if fit folder is present
check_create_subfolder

# cp "./Datacard_${differential_variable}.root" "$folder_name/impact_unblinded/Datacard_${differential_variable}.root"

cd "runFits_${differential_variable}/gof"

combine -M GoodnessOfFit ../../Datacard_${differential_variable}.root --algo saturated -m 125.38 --freezeParameters MH -n .goodnessOfFit_data


echo "Initial fit for GoF for ${differential_variable} done. Now launch ./runGOF_second.sh <variable>"