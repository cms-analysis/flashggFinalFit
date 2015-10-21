# Background Scripts
This is where the background model determined. For now, while we await data, pseudodata can be generated using the simulation sampels avaible.
## Background workflow

The workflow looks like this:
* Starting from flashgg signal and background samples root file
* Manually create a dat file listing available samples and whether they are signal or background, which will be used to assemble the pseudodata.
* Generate pseudodata by fitting the signal and background to either gaussians or bernsetins and throwing the number of toys equal to sum of the weight of events in a given category.
* Generate the background model from the pseudodata using `./bin/fTest`
* Make validation plots using `./bin/makeParametricSignalModelPlots`

Thankfully this whole process can be run in one command using the signal pilot script `runBackgroundScripts.sh`

WARNING: the pseudodata generation assumes that the background and signal samples have weights corresping to 1/fb.

## Quickstart

To run a basic version of the background workflow you can use the `./runBackgroundScripts.sh` script. 
```
cmsenv
FILE=/afs/cern.ch/user/l/lcorpe/work/public/big_test_jobs_2/everything.root
SAMPLES=/afs/cern.ch/user/l/lcorpe/work/public/big_test_jobs_2/samples.txt
./runBackgroundScripts.sh -p ggh -f UntaggedTag_0 --ext test --pseudoDataDat $SAMPLES --sigFile ../Signal/CMS-HGG_sigfit.root --seed 0 --intLumi 1
```
The available options can be seen by doing `runSignalScripts.sh -h`. They are all self-explanatory, aside from 
* `--intLumi`: This can be used to set how much pseudodata is to be generated.
* `--sigFile`: Optional argument to provide a previously-produced signal model to make the validation plots with (so you can see relative size of signal and background on one plot)
* `--pseudoDataDat`: Specify the list of available samples using the format: <type>,<filepath> where type can be `sig` or `bkg`.

## Script-byscript guide
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
* `--intLumi`: The intlumi option allows you to control how much pseudodata is generated. This assumes that the samples are normalised to 1/fb.

Working FLASHgg example:
```
SAMPLES=/afs/cern.ch/user/l/lcorpe/work/public/big_test_jobs_2/samples.txt
/bin/pseudodataMaker -i $SAMPLES --pseudodata 1 --plotdir plots -f UntaggedTag_0 --seed 0 --intLumi 1
```
Example of output plots can be found at:
```
https://lcorpe.web.cern.ch/lcorpe/outdir_intlumitest1fb/pseudoData/
```
### Generating the background model

The script `./bin/fTest` generates the background model using the envelope method. The idea is to fit the background to various possible background pdfs.
More explanation is probably needed of the envelope method, but this will be added in at a later date. The input to this script is either real data or the pseudodata from the previous step.

FLASHgg working example:
```
./bin/fTest -i pseudoWS.root --saveMultiPdf CMS-HGG_multipdf.root  -D bkgfTest -f UnatggedTag_0
```

Example output can be found at:
```
https://lcorpe.web.cern.ch/lcorpe/outdir_intlumitest1fb/bkgfTest/
```

### Background Validation Plots

The final script is the background validation plots. This also generates uncertainties on the background model. In general one can submit a job to the batch for each category, but for simplicity one can also run locally. The actual script is controlled using a python wrapper.

More information about the options can be found by using `./scripts/subBkgPlots.py -h`.

The `-s` option, which provides a signal file to add to the plots, is not compulsory.

FLASHgg working example:
```
./scripts/subBkgPlots.py -b CMS-HGG_multipdf.root -d bkgPlots -S 13 --isMultiPdf --useBinnedData  --doBands --runLocal --massStep 2 -s ../Signal/CMS-HGG_sigfit.root -L 120 -H 130 -f UntaggedTag_0 -l UntaggedTag_0 
```
Example output can be found here:
```
https://lcorpe.web.cern.ch/lcorpe/outdir_intlumitest1fb/bkgPlots/
```

