mkdir Models
mkdir Models/signal
mkdir Models/background
cp ../Background/outdir_earlyAnalysis_freeze/CMS-HGG*.root ./Models/background/
for file in Models/background/*.root; do mv "$file" "${file%.root}_2022.root"; done
cp ../Signal/outdir_packaged/CMS-HGG*.root ./Models/signal/
cp ../Datacard/Datacard.txt .