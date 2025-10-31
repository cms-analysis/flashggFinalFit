#!/bin/bash

if [ $# -ne 1 ]; then
  echo "Usage: $0 <variable, eg. pt>"
  exit 1
fi

differential_variable="$1"

folder_name="runFits_${differential_variable}"

source variable_parameters.sh

paramStrNoOne_var="paramStrNoOne_${differential_variable}"
paramStrNoOne=$(eval "echo \${$paramStrNoOne_var}")
catsStrWithCatX_var="catsStrWithCatX_${differential_variable}"
catsStrWithCatX=$(eval "echo \${$catsStrWithCatX_var}")


cd "./runFits_${differential_variable}/SplusBModels_stage3"

mkdir ./Plots

for param in ${paramStrNoOne//\,/\ }
do

    # Extract the ending string (in the format XYpZ_WSpQ) from the current param
    ending=$(echo $param | grep -oE '[0-9]+p[0-9]+_[0-9]+p[0-9]+')

    currentCat=""

    # Find the matching category
    for cat in ${catsStrWithCatX//\,/\ }
    do
        if [[ $cat == *"$ending"* ]]; then
            if [ -z "$currentCat" ]; then
                currentCat="$cat"
            else
                currentCat="${currentCat},${cat}"
            fi
        fi
    done

    # If no matching category is found, set currentCat to "all"
    if [ -z "$currentCat" ]; then
        currentCat="all"
    fi

    python3 ../../../Plots/makeSplusBModelPlot.py --inputWSFile ../unblinded/higgsCombineDataPostFitScanFit_${param}.MultiDimFit.mH125.38.root --loadSnapshot MultiDimFit --cats $currentCat --doZeroes --unblind --translateCats ../../../Plots/cats.json --doBands --doToyVeto --saveToyYields --doSumCategories --doCatWeights --saveWeights --ext _${param} --POI $param


    cd ./SplusBModels_${param}

    IFS='_' read -r -a parts <<< "$param"
    pattern="${parts[2]}_${parts[3]}"

    source_dir="."
    target_dir="../Plots"
    # Iterate over files in the current directory
    for filename in "$source_dir"/*; do
        # Check if the pattern is in the filename
        if [[ "$filename" == *"$pattern"* ]]; then
            # Copy the file to the target directory
            cp "$filename" "$target_dir"
            echo "Copied $(basename "$filename") to $target_dir"
        fi
    done

    # Go one again in the SplusBModels_stage3 directory
    cd ..
done
