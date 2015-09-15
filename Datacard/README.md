# Datacard Script
This is where the datacard for use in the combone script later..

## Datacard workflow

The workflow looks like this:
* Generate the datacard using `./makeParametricModelDatacardFLASHgg.py`

## Usage

You can use the script as follows:
```
./makeParametricModelDatacardFLASHgg.py -i ../Signal/CMS-HGG_sigfit.root  -o Datacard_13TeV.txt -p ggh -c UntaggedTag_0 --photonCatScales HighR9EE,LowR9EE,HighR9EB,LowR9EB --photonCatSmears HighR9EE,LowR9EE,HighR9EBRho,LowR9EBRho,HighR9EBPhi,LowR9EBPhi --isMultiPdf
```
