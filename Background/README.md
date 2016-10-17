# Background Scripts
This is where the background model is determined. Either true data can be used or pseudodata can be generated using the simulation samples available.

## Background workflow

The workflow looks like this:
* Start either from data workspace 
* Generate the background model from the data or pseudodata using `./bin/fTest`
* Make validation plots using `./bin/makeParametricSignalModelPlots`

Thankfully this whole process can be run in one command using the signal pilot script `runBackgroundScripts.sh`

## Quickstart

To run a basic version of the background workflow you can use the `./runBackgroundScripts.sh` script.
All plots using data and pseudodata are blinded by default.

```
cmsenv
./runBackgroundScripts.sh -p <comma separated processes> -f <comma separated tag names> --ext <extension to keep track of this processign run> --sigFile <the sigfit output fiel (to plot sig and bkg together in final validation plots>  --intLumi <in fb^{-1}> (--unblind) --isData -i <data file> --batch <LSF (CERN or IC> 
```
eg
```
./runBackgroundScripts.sh -p ggh,vbf,wh,zh,tth -f UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1,TTHHadronicTag,TTHLeptonicTag --ext HggAnalysis_ICHEP2016_example --sigFile /afs/cern.ch/user/l/lcorpe/work/private/FinalFits_ICHEP_Clearup/CMSSW_7_4_7/src/flashggFinalFit/Signal/outdir_HggAnalysis_ICHEP2016_example/CMS-HGG_sigfit_HggAnalysis_ICHEP2016_example.root --seed 0 --intLumi 12.9    --isData  -i root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/ichep2016/flashgg-workspaces//allData.root  --batch SF
```

The available options can be seen by doing `runSignalScripts.sh -h`. They are all self-explanatory, aside from 
* `--intLumi`: This can be used to set how much pseudodata is to be generated.
* `--sigFile`: Optional argument to provide a previously-produced signal model to make the validation plots with (so you can see relative size of signal and background on one plot)
* `--pseudoDataDat`: Specify the list of available samples using the format: <type>,<filepath> where type can be `sig` or `bkg`.

## Script-by-script guide
### Generating the background model

The script `./bin/fTest` generates the background model to be used for the envelope method. The idea is here to pick a sensible subset of all possible functions which could describe the data, and then treat the choice of function as a discrete nuisance parameter in the final stat analysis step. The input to this script is either real data or the pseudodata from the previous step.

FLASHgg working example:

```
./bin/fTest -i root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/ichep2016/flashgg-workspaces//allData.root --saveMultiPdf CMS-HGG_multipdf_HggAnalysis_ICHEP2016_example.root  -D outdir_HggAnalysis_ICHEP2016_example/bkgfTest-Data -f UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1,TTHHadronicTag,TTHLeptonicTag  --isData 1
```

Example output can be found at:

```
# for the data:
https://twiki.cern.ch/twiki/bin/view/CMS/FLASHggFramework#Background #(Under Bkg FTest, Data)
# for the pseudodata:
```

### Background Validation Plots

The final script is the background validation plots. This also generates uncertainties on the background model. In general one can submit a job to the batch for each category, but for simplicity one can also run locally. The actual script is controlled using a python wrapper.

More information about the options can be found by using `./scripts/subBkgPlots.py -h`.

The `-s` option, which provides a signal file to add to the plots, is not compulsory.

FLASHgg working example:

```
./scripts/subBkgPlots.py -b <background file from previous step> -d <output dir for plots> -S <sqrts>  --isMultiPdf --useBinnedData  --doBands --massStep <in GeV>  -s <signal file to include sig model on validation plots> -L <low side of mgg> -H <high side of mgg> -f i<comma separated list fo tags> -l <list of labels for tags, human readable> --intLumi < in fb^{-1}>  (--unblind) --batch <IC or LSF (Cern)> -q <your favourite queue eg 8nm>
```
eg
```
./scripts/subBkgPlots.py -b CMS-HGG_multipdf_HggAnalysis_ICHEP2016_example.root -d outdir_HggAnalysis_ICHEP2016_example/bkgPlots-Data -S 13 --isMultiPdf --useBinnedData  --doBands --massStep 1 -s /afs/cern.ch/user/l/lcorpe/work/private/FinalFits_ICHEP_Clearup/CMSSW_7_4_7/src/flashggFinalFit/Signal/outdir_HggAnalysis_ICHEP2016_example/CMS-HGG_sigfit_HggAnalysis_ICHEP2016_example.root -L 100 -H 180 -f UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1,TTHHadronicTag,TTHLeptonicTag -l UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1,TTHHadronicTag,TTHLeptonicTag --intLumi 12.9  --batch LSF -q 1nh
```

Example output can be found here:

```
# for data:
https://twiki.cern.ch/twiki/bin/view/CMS/FLASHggFramework#Background #(Under Bkg Validation Plots, Data)
```


## Notes

Some notes which might be helpful:

* Keep an eye out for situations where you are using too many orders in your candidate background functions. As for the signal workflow, sometimes the extra PDFs added for high order are negative or 0, and this causes headaches with roofit. For example, during the dry run I had to force nBernsteins < 7 otherwise I got segfaults and nonsense later in the workflow.

