# Background Scripts
This is where the background model is determined. Either true data can be used or pseudodata can be generated using the simulation samples available.

## Background workflow

The workflow looks like this:
* Start either from data workspace 
* Generate the background model from the data or pseudodata using `./bin/fTest`
* Make validation plots using `./bin/makeParametricSignalModelPlots`

## Submission script

Akin to in the signal package, you can use the `RunBackgroundScripts.py` script to run the full Background model workflow.

The options for the background fit are specified in a config file e.g. `example_config_stage1_1.py` or directly in the command line. Note, you need to specify the year option. We hope to include functionality for merging categories across years in the near future.

To run the script:
```
cmsenv
python RunBackgroundScripts.py --inputConfig example_config_stage1_1.py
```

The config file will look as follows:
```
backgroundScriptCfg = {
  
  # Setup
  'inputWSDir':'/vols/cms/jl2117/hgg/ws/test_stage1_1_2018', # directory of input data workspaces
  #Procs will be inferred automatically from filenames
  'cats':'RECO_0J_PTH_GT10_Tag0,RECO_0J_PTH_GT10_Tag1', # analysis categories
  'ext':'stage1_1_2018', #extension to be added to output directory (match with signal model!)
  'year':'2018', 
  'unblind':0,

  # Job submission options
  'batch':'HTCONDOR',
  'queue':'microcentury',

  # Mode allows script to carry out single function
  'mode':'std', # Options: [std,fTestOnly,bkgPlotsOnly]
}
```

Running with `'mode':"std"` will run the background fTest and then will make the validation plots sequentially. You can separate these steps if necessary.

The output of the fTest will be the RooWorkspace containing the multipdf for each analysis category.

All plots using data and pseudodata are blinded by default.

## To do list
There are some available options which have not yet been configured, concering running on MC PseudoData. To make the fTest with PseudoData please use the master branch of FinalFits (for now).
* `--intLumi`: This can be used to set how much pseudodata is to be generated.
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

