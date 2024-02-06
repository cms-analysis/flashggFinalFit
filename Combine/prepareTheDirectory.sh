mkdir Models
mkdir Models/signal
mkdir Models/background
cp ../Background/outdir_earlyAnalysis/CMS-HGG*.root ./Models/background/
# Comment in/out as needed, I am not totally sure about these year suffixes
#for file in Models/background/*.root; do mv "$file" "${file%.root}_2022.root"; done
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