#!/bin/bash

if [ $# -ne 1 ]; then
  echo "Usage: $0 <variable, eg. pt>"
  exit 1
fi

differential_variable="$1"

folder_name="runFits_${differential_variable}"

cd "runFits_${differential_variable}"

python3 ../../Plots/makeSplusBModelPlot.py --inputWSFile ../Datacard_${differential_variable}.root --cats all --doZeroes --blindingRegion 125,125 --translateCats ../../Plots/cats.json --doBands --doToyVeto --saveToyYields --ext _stage2
