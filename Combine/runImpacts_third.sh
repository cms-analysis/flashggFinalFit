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

combineTool.py -M Impacts -d Datacard_${differential_variable}.root --freezeParameters MH -m 125.38 -o impacts.json

for param in ${paramStrNoOne//\,/\ }
do
  plotImpacts.py -i impacts.json -o impacts_${param} --POI ${param}
done