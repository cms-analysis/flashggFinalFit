mkdir Models
mkdir Models/signal
mkdir Models/background
cp ../Background/outdir_earlyAnalysis/CMS-HGG*.root ./Models/background/
#cp ../Background/outdir_earlyAnalysis_2022preEE/CMS-HGG*.root ./Models/background/
# Comment this renaming stuff in/out as needed, I am not totally sure about these year suffixes
#for file in Models/background/*resolution.root; do mv "$file" "${file%.root}_2022preEE.root"; done
#cp ../Background/outdir_earlyAnalysis_2022postEE/CMS-HGG*.root ./Models/background/
#for file in Models/background/*resolution.root; do mv "$file" "${file%.root}_2022postEE.root"; done
cp ../Signal/outdir_packaged/CMS-HGG*.root ./Models/signal/
# See above
for file in Models/signal/*_2022.root; do
    if [ -f "$file" ]; then
        new_name="${file%_2022.root}.root"
        mv "$file" "$new_name"
        echo "Renamed $file to $new_name"
    fi
done
cp ../Datacard/Datacard.txt .

# Note that you might need to manually rename some paths in the datacard depending on the settings of the year 2022
# Currently: Add 2022 to the background shapes, should be: 2022_13TeV_bkgshape
# Uncapitalise Scales and Smearing nuisance parameters
# pdfindex_best_resolution_13TeV --> pdfindex_best_resolution_2022_13TeV et. al.