# Datacard Script
This is where the datacard for use in the `combine` tool  later..

## Datacard workflow

The workflow looks like this:
* Generate the datacard using `./makeParametricModelDatacardFLASHgg.py`

## Usage

You can use the script as follows:
```
sig=/afs/cern.ch/user/l/lcorpe/public/HggDryRunDec15/flashgg_source_files/allsig.root
./makeParametricModelDatacardFLASHgg.py -i $sig  -o Datacard_13TeV_hgg_dry_run_2015.txt -p ggh,vbf,wzh,tth -c UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1 --photonCatScales HighR9EE,LowR9EE,HighR9EB,LowR9EB --photonCatSmears HighR9EE,LowR9EE,HighR9EB,LowR9EB --isMultiPdf # --intLumi 2.46
```
