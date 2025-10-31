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



cd "runFits_${differential_variable}/combined"

for param in ${paramStrNoOne//\,/\ }
do
  python3 ../../../Plots/plot1DScan_combined.py ../unblinded/higgsCombineDataPostFitScanFit_${param}.MultiDimFit.mH125.38.root --POI ${param} --observed ../unblinded/higgsCombine.second_DataScan_${param}.MultiDimFit.mH125.38.root:Observed-stat-only:1 --expected ../asimov/higgsCombineAsimovPostFitScanFit_${param}.root:Expected:2 ../asimov/higgsCombineAsimovPostFitScanStat_${param}.root:Expected-stat-only:2 -o ${param}_statsyst_fixedMH_combined --breakdown1 syst,stat --breakdown2 syst,stat --translate ../../pois_differential.json
done

# Go back to the main directory
cd ../..
