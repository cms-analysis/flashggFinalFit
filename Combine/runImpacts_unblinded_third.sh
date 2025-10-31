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

if [ ! -d "$folder_name" ]; then
    echo "Launch ./runImpacts_unblinded_first_<variable>.sh first."
fi

cd "runFits_${differential_variable}/impact_unblinded"

impact_dir=$(realpath .)

if [ ! -e "Datacard_${differential_variable}.root" ]; then
    echo "Launch ./runImpacts_unblinded_first_<variable>.sh first."
fi

combineTool.py -M Impacts -d Datacard_${differential_variable}.root --freezeParameters MH -m 125.38 -o impacts.json

python3 $impact_dir/../../../Plots/correctImpacts.py --impactsJson impacts.json --frozenParam MH --dropBkgModelParams

# # Switch to Combine v9 for getting pull in impacts.
# cd /afs/cern.ch/user/n/niharrin/cernbox/PhD/Higgs/CMSSW_11_3_4/src
# echo "Switch to Combine v9..."
# cmsenv
cd $impact_dir

for param in ${paramStrNoOne//\,/\ }
do
  plotImpacts.py -i impacts_corrected_dropBkgModelParams.json -o impacts_unblinded_${param} --POI ${param} --translate ../../pois_differential.json
done

# Return back to Combine v8
# echo "Switch back to Combine v8"
# cmsenv