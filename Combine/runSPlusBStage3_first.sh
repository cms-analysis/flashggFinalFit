#!/bin/bash

if [ $# -ne 1 ]; then
  echo "Usage: $0 <variable, eg. pt>"
  exit 1
fi

differential_variable="$1"

folder_name="runFits_${differential_variable}"

source variable_parameters.sh

paramStrNoOne_var="paramStrNoOne_${differential_variable}"
paramStrNoOne=$(eval "echo \${$paramStrNoOne_var}")

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

cd ./runFits_${differential_variable}/SplusBModels_stage3

for param in ${paramStrNoOne//\,/\ }
do
    python3 ../../../Plots/makeToys.py --inputWSFile ../unblinded/higgsCombineDataPostFitScanFit_${param}.MultiDimFit.mH125.38.root --loadSnapshot MultiDimFit --ext _${param} --nToys 1000 --POIs $param --batch condor --queue workday --dryRun
    

    cd ./SplusBModels_${param}/toys

    # Fetch the toy directory
    current_dir=$(pwd)

    cd ./jobs
    # Replace the wrong path from the .sh file
    sed -i "0,/^cd /s|cd .*|cd \"$current_dir\"|" sub_toys.sh

    condor_submit -spool ./sub_toys.sub

    cd ../../..

    # Its sufficient to compute the toys for one parameter (because in the inputWS all the other params are contained as well)
done

echo "Toys sent to HTCondor for ${differential_variable}. When done, launch ./runSPlusBStage3_second.sh <variable>"