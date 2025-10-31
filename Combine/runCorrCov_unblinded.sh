#!/bin/bash

if [ $# -ne 1 ]; then
  echo "Usage: $0 <variable, eg. pt>"
  exit 1
fi

differential_variable="$1"

# Import bins and pdfindices for considered variable...

source variable_parameters.sh

paramStr_var="paramStr_${differential_variable}"
paramStrNoOne_var="paramStrNoOne_${differential_variable}"
pdfIndeces_var="pdfIndeces_${differential_variable}"

paramStr=$(eval "echo \${$paramStr_var}")
paramStrNoOne=$(eval "echo \${$paramStrNoOne_var}")
pdfIndeces=$(eval "echo \${$pdfIndeces_var}")

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
        mkdir "$folder_name/hesse"
        mkdir "$folder_name/gof"
        mkdir "$folder_name/hesse/Plots"
        echo "Folders '$folder_name' created successfully."
    else
        echo "Folders '$folder_name' already exists."
    fi
}

# Check if fit folder is present
check_create_subfolder

cp "./Datacard_${differential_variable}.root" "$folder_name/hesse/Datacard_${differential_variable}.root"

cd "runFits_${differential_variable}/hesse"

mkdir -p ./Plots/data

if [ ! -f "./robustHessefirstStep_data.root" ]; then
    combine -M MultiDimFit Datacard_${differential_variable}.root --freezeParameters MH -m 125.38 -n firstStep_data \
        --cminDefaultMinimizerStrategy=0 --saveWorkspace \
        --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants \
        --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 \
        --saveFitResult --saveSpecifiedIndex ${pdfIndeces} --floatOtherPOIs 1 --robustHesse 1 --robustHesseSave 1

    echo "Hesse successfully created."
else
    echo "Hesse already found. Using robustHessefirstStep_data.root found in the directory."
fi

cd ../../../Plots

python3 makeCorrMatrix.py --inputJson ./inputs_robustHesse.json --mode ${differential_variable} --input ../Combine/runFits_${differential_variable}/hesse/robustHessefirstStep_data.root --output ../Combine/runFits_${differential_variable}/hesse/Plots/data --translate ../Combine/poi_differential_hesse_noLabels.json  --doObserved --year 2022 --noPreliminary
python3 makeCorrMatrix.py --inputJson ./inputs_robustHesse.json --mode ${differential_variable} --input ../Combine/runFits_${differential_variable}/hesse/robustHessefirstStep_data.root --output ../Combine/runFits_${differential_variable}/hesse/Plots/data --translate ../Combine/poi_differential_hesse_noLabels.json  --doObserved --doCov --year 2022 --noPreliminary

