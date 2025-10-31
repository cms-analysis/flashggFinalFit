#!/bin/bash

if [ $# -ne 1 ]; then
  echo "Usage: $0 <variable, eg. pt>"
  exit 1
fi

differential_variable="$1"

# Import bins and pdfindices for considered variable...

source variable_parameters.sh


paramStrNoOne_var="paramStrNoOne_${differential_variable}"

paramStrNoOne=$(eval "echo \${$paramStrNoOne_var}")

folder_name="runFits_${differential_variable}"

if [ ! -d "$folder_name" ]; then
    trap 'echo "Launch ./runFits.sh first."; exit 1' ERR
fi

cd "runFits_${differential_variable}/asimov"

if [ ! -d "./scans" ]; then
    mkdir scans
fi


for param in ${paramStrNoOne//\,/\ }
do
    hadd higgsCombineAsimovPostFitScanFit_${param}.root higgsCombineAsimovPostFitScanFit_${param}.POINTS.*

    hadd higgsCombineAsimovPostFitScanStat_${param}.root higgsCombineAsimovPostFitScanStat_${param}.POINTS.*

    plot1DScan.py higgsCombineAsimovPostFitScanFit_${param}.root -o scans/scan_${param} --POI ${param} --others higgsCombineAsimovPostFitScanStat_${param}.root:"stat-only":2 --main-label Expected --translate ../../pois_differential.json
done