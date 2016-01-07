# Background Scripts
This is where the background model determined. Either true data can be used or pseudodata can be generated using the simulation samples avaible.

## Background workflow

The workflow looks like this:
* Start eitehr from data (default) or from flashgg signal and background sample root files
* (if using pseudodata) Manually create a dat file listing available samples and whether they are signal or background, which will be used to assemble the pseudodata. See example samples=/afs/cern.ch/user/l/lcorpe/public/HggDryRunDec15/flashgg_source_files/samples.txt
* (if using pseudodata) Generate pseudodata by fitting the signal and background to either gaussians or bernsetins and throwing the number of toys equal to sum of the weight of events in a given category.
* Generate the background model from the data or pseudodata using `./bin/fTest`
* Make validation plots using `./bin/makeParametricSignalModelPlots`

Thankfully this whole process can be run in one command using the signal pilot script `runBackgroundScripts.sh`

## Quickstart

To run a basic version of the background workflow you can use the `./runBackgroundScripts.sh` script.
All plots using data and pseudodata are blinded by default.

```
cmsenv
sig=$PWD/../Signal/outdir_hgg_dry_run_2015/CMS-HGG_sigfit_hgg_dry_run_2015.root #previously generated using Signal scripts, used for validation plots
samples=/afs/cern.ch/user/l/lcorpe/public/HggDryRunDec15/flashgg_source_files/samples.txt # used for pseudodata generation if needed
data=/afs/cern.ch/user/l/lcorpe/public/HggDryRunDec15/flashgg_source_files/alldata.root # the true data
# if using data :
./runBackgroundScripts.sh -p ggh,vbf,wzh,tth -f UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1 --ext hgg_dry_run_2015 --sigFile $sig --seed 0 --intLumi 2.46  --isData  -i $data
# or if you wish to generate  pseudodata :
./runBackgroundScripts.sh -p ggh,vbf,wzh,tth -f UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1 --ext hgg_dry_run_2015 --sigFile $sig --seed 0 --intLumi 2.46 --pseudoDataDat $samples
```
The available options can be seen by doing `runSignalScripts.sh -h`. They are all self-explanatory, aside from 
* `--intLumi`: This can be used to set how much pseudodata is to be generated.
* `--sigFile`: Optional argument to provide a previously-produced signal model to make the validation plots with (so you can see relative size of signal and background on one plot)
* `--pseudoDataDat`: Specify the list of available samples using the format: <type>,<filepath> where type can be `sig` or `bkg`.

## Script-byi-script guide
### Generating the pseudodata

One can use the `/bin/pseudodataMaker` script to regenerate this. Example output is provided here.

The pseudodata maker works by looping through the list of samples provided in the input. Each must be specified as type either signal (`sig`) or background (`bkg`) using the format:
```
<type>,<sample path>
```
There should be one line per sample file.
For each sample file, the script loops through the datasets asscoiated with each tag or category. It fits the signal samples to 3 gaussians, and the background samples to a bernstein of order 3. The resulting pdf is then used to generate random events, where the total number of events generated per sample is equal to the sum of weights in the original sample. The datasets per sample are then summed into a single dataset per tag/category. 

The options are self explanatory, aside from the two listed below which probably deserve extra explanation:
* `--seed`: The seed is given to the random number generator inside RooFit. This allows you to force a particular seed, ie if you want to generate two separate and different pseudo-datasets. To do this, simply provide different seeds each time.
* `--intLumi`: The intlumi option allows you to control how much pseudodata is generated. 

Working FLASHgg example:

```
samples=/afs/cern.ch/user/l/lcorpe/public/HggDryRunDec15/flashgg_source_files/samples.txt 
./bin/pseudodataMaker -i $samples  --pseudodata 1 --plotdir outdir_hgg_dry_run_2015/pseudoData -f UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1 --seed 0 --intLumi 2.46
```
Example of output plots can be found at:

```
https://lcorpe.web.cern.ch/lcorpe/outdir_hgg_dry_run_2015/pseudoData/
```
### Generating the background model

The script `./bin/fTest` generates the background model using the envelope method. The idea is to fit the background to various possible background pdfs.
More explanation is probably needed of the envelope method, but this will be added in at a later date. The input to this script is either real data or the pseudodata from the previous step.

FLASHgg working example:

```
# using data:
data=/afs/cern.ch/user/l/lcorpe/public/HggDryRunDec15/flashgg_source_files/alldata.root 
./bin/fTest -i $data --saveMultiPdf CMS-HGG_multipdf_hgg_dry_run_2015/.root  -D hgg_dry_run_2015//bkgfTest-Data -f UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1  --isData 1
# OR using pseudodata:
pseudodata=outdir_hgg_dry_run_2015/pseudoData/pseudoWS.root # created by pseudodataMaker
./bin/fTest -i $pseudodata --saveMultiPdf CMS-HGG_multipdf_hgg_dry_run_2015.root  -D outdir_hgg_dry_run_2015/bkgfTest -f UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1
```

Example output can be found at:

```
# for the data:
https://lcorpe.web.cern.ch/lcorpe/outdir_hgg_dry_run_2015/bkgfTest-Data/
# for the pseudodata:
https://lcorpe.web.cern.ch/lcorpe/outdir_hgg_dry_run_2015/bkgfTest/
```

### Background Validation Plots

The final script is the background validation plots. This also generates uncertainties on the background model. In general one can submit a job to the batch for each category, but for simplicity one can also run locally. The actual script is controlled using a python wrapper.

More information about the options can be found by using `./scripts/subBkgPlots.py -h`.

The `-s` option, which provides a signal file to add to the plots, is not compulsory.

FLASHgg working example:

```
bkg=CMS-HGG_multipdf_hgg_dry_run_2015.root #created in previous step 
sig=$PWD/../Signal/outdir_hgg_dry_run_2015/CMS-HGG_sigfit_hgg_dry_run_2015.root
# for true data:
./scripts/subBkgPlots.py -b $bkg -d outdir_hgg_dry_run_2015/bkgPlots-Data -S 13 --isMultiPdf --useBinnedData  --doBands --runLocal  --massStep 2 -s /afs/cern.ch/work/l/lcorpe/private/FinalFits_Jan16/CMSSW_7_1_5/src/flashggFinalFit/Background/../Signal/outdir_hgg_dry_run_2015/CMS-HGG_sigfit_hgg_dry_run_2015.root -L 100 -H 180 -f UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1 -l UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1 --intLumi 2.46
# for pseudodata (basically exaclt the same)
./scripts/subBkgPlots.py -b $bkg -d outdir_hgg_dry_run_2015/bkgPlots -S 13 --isMultiPdf --useBinnedData  --doBands --runLocal --massStep 2 -s $sig -L 100 -H 180 -f UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1 -l UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1 --intLumi 2.46
```

Example output can be found here:

```
# for data:
https://lcorpe.web.cern.ch/lcorpe/outdir_hgg_dry_run_2015/bkgPlots-Data/
# For pseudodata 
https://lcorpe.web.cern.ch/lcorpe/outdir_hgg_dry_run_2015/bkgPlots/
```

Notes:

* Technically this step can be submitted to the batch, but I generally do not use this feature.

## To Do

* Try to undertsand why there are differences between the nEvents using data and nEvents using pseudodata.

## Notes

Some notes whcih might be helpful:

* At present there is a discrepancy between the total number of events provided by the data and the pseudodata when summing up all the samples. As such the results provided using pseudodata should be taken with a pinch of salt until the differences are understood.
* Keep an eye out for situatiosn where you are using too many orders in your candidate background functions. As for the signal workflow, sometimes the extra PDFs added for high order are geative or 0, and this causes headaches with roofit. For example, during the dry run I had to force nBernsteins < 7 otherwise I got segfaults and nonsense later int he workflow.

