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

cd "runFits_${differential_variable}/gof"

if [ ! -e "higgsCombine.goodnessOfFit_toys0.GoodnessOfFit.mH125.38.0.root" ]; then
    echo "Launch ./runGOF_second_<variable>.sh first."
fi

# cp "./Datacard_${differential_variable}.root" "$folder_name/impact_unblinded/Datacard_${differential_variable}.root"

combineTool.py -M CollectGoodnessOfFit --input higgsCombine.goodnessOfFit_data.GoodnessOfFit.mH125.38.root higgsCombine.goodnessOfFit_toys* -m 125.38 -o gof.json

json_file="./gof.json"

higgs_mass=$(jq -r 'keys[0]' "$json_file" | awk '{printf "%.9f\n", $0}')
higgs_mass=$(echo "$higgs_mass" | bc -l)

echo $higgs_mass

plotGof.py gof.json --statistic saturated --mass "$higgs_mass" -o differential_${differential_variable}_gof