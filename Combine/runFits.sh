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

cp "./Datacard_${differential_variable}.root" "$folder_name/asimov/Datacard_${differential_variable}.root"
cp "./checkPdfIdx.C" "$folder_name/asimov/checkPdfIdx.C"

cd "runFits_${differential_variable}/asimov"

for param in ${paramStrNoOne//\,/\ }
do
  combine -M MultiDimFit Datacard_${differential_variable}.root --freezeParameters MH -m 125.38 -n firstStep_${param} \
  --cminDefaultMinimizerStrategy=0 --expectSignal 1 --saveWorkspace \
  --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants \
  --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 \
  -t -1 --setParameters ${paramStr} -P ${param} --saveFitResult --saveSpecifiedIndex ${pdfIndeces} --floatOtherPOIs 1

  pdfIdx=$(root -l -q 'checkPdfIdx.C("higgsCombinefirstStep_'"${param}"'.MultiDimFit.mH125.38.root")')
  substring=='Processing checkPdfIdx.C("higgsCombinefirstStep_'"${param}"'.MultiDimFit.mH125.38.root")... '
  # Remove "Processing checkPdfIdx.C... " from the beginning
  pdfIdx=$(echo "$pdfIdx" | awk -F'X' '{print $2}')
  # Remove the last comma
  pdfIdx="${pdfIdx%,}"
  echo ${pdfIdx}

  combineTool.py -M MultiDimFit Datacard_${differential_variable}.root --freezeParameters MH -m 125.38 -n AsimovPostFitScanFit_${param} \
  --cminDefaultMinimizerStrategy=0 --algo grid --points 30 --split-points 1 --expectSignal 1 \
  --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants \
  --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 \
  -t -1 -P ${param} --saveFitResult \
  --job-mode condor --task-name AsimovScan_${param} --sub-opts='+JobFlavour = "workday"' \
  --setParameters${pdfIdx},${paramStr} --floatOtherPOIs 1 --alignEdges 1 --saveSpecifiedIndex ${pdfIndeces}

  combineTool.py -M MultiDimFit higgsCombinefirstStep_${param}.MultiDimFit.mH125.38.root -m 125.38 -n AsimovPostFitScanStat_${param} --split-points 1 \
  --cminDefaultMinimizerStrategy=0 --expectSignal 1 \
  --algo grid --points 30 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants \
  --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 \
  --freezeParameters allConstrainedNuisances,MH -t -1 --setParameters${pdfIdx},${paramStr} \
  --job-mode condor --task-name AsimovPostFitScanStat_${param} --sub-opts='+JobFlavour = "workday"' \
  -P ${param} --saveFitResult --snapshotName MultiDimFit --floatOtherPOIs 1 --alignEdges 1 --saveSpecifiedIndex ${pdfIndeces}

done

# Go back to the main directory
cd ../..

# Submit to condor from eos using the spool option
./multi_submit.sh $differential_variable "asimov"

echo "Fits for ${differential_variable} sent to condor."