#!/bin/bash

# Define your working directory here
WORKDIR="\/home\/users\/yagu\/XYH\/FinalFit\/CMSSW_10_2_13\/src\/flashggFinalFit"
Tree_Output_DIR="\/home\/users\/yagu\/XYH\/XtoYH_pNN\/Outputs\/trained\/outputTrees"
Signal_Model_DIR="\/home\/users\/yagu\/XYH\/XtoYH_pNN\/Interpolation"
Resbkg_Model_DIR="\/home\/users\/yagu\/XYH\/XtoYH_pNN\/Outputs\/Graviton\/ResonantBkg"

# Define the list of files to process
files=("test_first_part.sh" "test_second_part.sh" "test_third_part.sh" "test_fourth_part.sh" "test_fifth_part.sh" "test_sixth_part.sh" "./Background/scripts/fTest.py" "get_limit_continuous_2d.sh" "get_limit_hadd_tree2ws.sh" "./Background/RootDict.cxx" "get_limit_datacard.sh" "get_limit_combine.sh" "get_limit_workspace.sh")

# Define the old and new strings
WORK_old_string="\/home\/users\/yagu\/XYH\/FinalFit\/CMSSW_10_2_13\/src\/flashggFinalFit"
WORK_new_string=$WORKDIR

Tree_old_string="\/home\/users\/yagu\/XYH\/XtoYH_pNN\/Outputs\/trained\/outputTrees"
Tree_new_string=$Tree_Output_DIR

Sig_old_string="\/home\/users\/yagu\/XYH\/XtoYH_pNN\/Interpolation"
Sig_new_string=$Signal_Model_DIR

Resbkg_old_string="\/home\/users\/yagu\/XYH\/XtoYH_pNN\/Outputs\/Graviton\/ResonantBkg"
Resbkg_new_string=$Resbkg_Model_DIR

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        # Use 'sed' to perform the substitution in each file
	echo 1
        grep -rl $WORK_old_string $file | xargs sed -i "s/$WORK_old_string/$WORK_new_string/g"
	echo 2
	grep -rl $Tree_old_string $file | xargs sed -i "s/$Tree_old_string/$Tree_new_string/g"
	echo 3
	grep -rl $Sig_old_string $file | xargs sed -i "s/$Sig_old_string/$Sig_new_string/g"
	echo 4
	grep -rl $Resbkg_old_string $file | xargs sed -i "s/$Resbkg_old_string/$Resbkg_new_string/g"
	echo 5
	echo "Substituted in file: $file"
    else
        echo "File $file not found. Skipping."
    fi
done

