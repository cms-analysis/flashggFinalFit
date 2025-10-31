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

paramStr=$(eval "echo \${$paramStr_var}")
paramStrNoOne=$(eval "echo \${$paramStrNoOne_var}")

folder_name="runFits_${differential_variable}"

cd ./${folder_name}/unblinded

# Check if the file exists in the current directory
if [ ! -f "./higgsCombine.pvalue.MultiDimFit.mH125.38.root" ]; then
    # If the file does not exist, perform the desired action
    echo "The pvalue file does not exist in the current directory. Creating it..."
    for param in ${paramStrNoOne//\,/\ }
    do
        combine -M MultiDimFit ./higgsCombineDataPostFitScanFit_${param}.MultiDimFit.mH125.38.root --algo fixed --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 --freezeParameters MH --fixedPointPOIs ${paramStr},MH=125.38 -n .pvalue -m 125.38 --saveWorkspace
        break
    done
else
    echo "The pvalue file exists in the current directory. Skipping the creation."
fi



# Variables for the options
FILENAME=$(realpath "./higgsCombine.pvalue.MultiDimFit.mH125.38.root")

# Count the number of elements in paramStrNoOne
NBINS=$(echo "$paramStrNoOne" | tr ',' '\n' | wc -l)

cd ../../

# Run the Python script and capture the output
PVALUE=$(python3 ./pvalue.py --filename "$FILENAME" --nBins $NBINS)

# Print the p-value
echo "The p-value of the variable $differential_variable is: $PVALUE"

