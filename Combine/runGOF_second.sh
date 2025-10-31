#!/bin/bash

if [ $# -ne 1 ]; then
  echo "Usage: $0 <variable, eg. pt>"
  exit 1
fi

differential_variable="$1"

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
        mkdir "$folder_name/gof"
        mkdir "$folder_name/hesse"
        mkdir "$folder_name/hesse/Plots"
        echo "Folders '$folder_name' created successfully."
    else
        echo "Folders '$folder_name' already exists."
    fi
}

# Check if fit folder is present
check_create_subfolder

cd "runFits_${differential_variable}/gof"

if [ ! -e "higgsCombine.goodnessOfFit_data.GoodnessOfFit.mH125.38.root" ]; then
    echo "Launch ./runGOF_first_<variable>.sh first."
fi

# cp "./Datacard_${differential_variable}.root" "$folder_name/impact_unblinded/Datacard_${differential_variable}.root"


number_of_jobs=1000
toys_per_job=10
let number_of_toys=number_of_jobs*toys_per_job
let number_of_jobs_minus_one=number_of_jobs-1

# Creating condor submission file + job file with 10000 jobs. Need to split them
combineTool.py -M GoodnessOfFit ../Datacard_${differential_variable}.root --algo saturated -m 125.38 --freezeParameters MH -t $number_of_toys -s -1 --job-mode condor --task-name gof_test -n .goodnessOfFit_toys --sub-opts='+JobFlavour = "workday"'

# Replace the block in the script
sed -i '/if \[ $1 -eq 0 \]; then/,/fi/d' ./condor_gof_test.sh

# Create the new block of script with the actual value of differential_variable
new_block=$(cat <<EOF

if [[ \$1 =~ ^[0-${number_of_jobs_minus_one}]+$ ]] && [ \$1 -ge 0 ] && [ \$1 -le ${number_of_jobs_minus_one} ]; then
toy_start=\$(( \$1 * ${toys_per_job} ))

  combine ../../Datacard_${differential_variable}.root --algo saturated -t ${toys_per_job} -M GoodnessOfFit -m 125.38 --freezeParameters MH -s \$toy_start --toysFrequentist -n .goodnessOfFit_toys\$1
fi
EOF
)

# Append the new block to the script
echo "$new_block" >> ./condor_gof_test.sh

sed -i "s/^queue 1$/queue ${number_of_jobs}/" condor_gof_test.sub

condor_submit -spool ./condor_gof_test.sub

echo "GoF for ${differential_variable} sent to condor. Wait until finished and then launch ./runGOF_third.sh <variable>"