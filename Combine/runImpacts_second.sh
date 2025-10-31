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
    echo "Launch ./runImpacts_first.sh <variable> first."
fi

cd "runFits_${differential_variable}/impact"

if [ ! -e "Datacard_${differential_variable}.root" ]; then
    echo "Launch ./runImpacts_first.sh <variable> first."
fi


combineTool.py -M Impacts -d Datacard_${differential_variable}.root --freezeParameters MH -m 125.38 --robustFit 1 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 --cminDefaultMinimizerStrategy=0 --doFits -t -1 --setParameters ${paramStr} --job-mode condor --task-name impacts_second --sub-opts='+JobFlavour = "workday"'

condor_submit -spool ./condor_impacts_second.sub

echo "Impacts for ${differential_variable} sent to condor. Wait until finished and then launch ./runImpacts_third.sh <variable>"