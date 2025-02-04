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
        mkdir "$folder_name/SplusBModels_stage2"
        mkdir "$folder_name/SplusBModels_stage3"
        mkdir "$folder_name/unblinded"
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


cd "runFits_${differential_variable}/unblinded"

for param in ${paramStrNoOne//\,/\ }
do

  combine -M MultiDimFit higgsCombineDataPostFitScanFit_${param}.MultiDimFit.mH125.38.root -m 125.38 --cminDefaultMinimizerStrategy=0 --algo grid --points 100 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -P ${param} --saveFitResult --freezeParameters MH,allConstrainedNuisances --floatOtherPOIs 1  -n .second_DataScan_${param} --snapshotName "MultiDimFit" -w w
  

done

# Go back to the main directory
cd ../..

echo "Stat. only and Stat+Syst fits for ${differential_variable} ready. Execute runFits_unblinded_third.sh <variable> for the plots."