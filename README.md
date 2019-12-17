# FLASHgg Final Fits
The Final Fits package is a series of scripts which are used to run the final stages of the CMS Hgg analysis: signal modelling, background modelling, datacard creation and final statistical interpretation and final result plots.

## Download and setup instructions

```
export SCRAM_ARCH=slc7_amd64_gcc700
cmsrel CMSSW_10_2_13
cd CMSSW_10_2_13/src
cmsenv
git cms-init

# Install the GBRLikelihood package which contains the RooDoubleCBFast implementation
git clone git@github.com:jonathon-langford/HiggsAnalysis.git
# Install Combine as per the documentation here: cms-analysis.github.io/HiggsAnalysis-CombinedLimit/
git clone git@github.com:cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit

# Compile external libraries
cd HiggsAnalysis
cmsenv
scram b -j 9

# Install Flashgg Final Fit packages
cd ..
git clone -b dev_runII_102x git@github.com:cms-analysis/flashggFinalFit.git
cd flashggFinalFit/
```

Two packages need to be built with their own makefiles, if needed. Please note that there will be verbose warnings from BOOST etc, which can be ignored. So long as the `make` commands finish without error, then the compilation happened fine.:

```
cd ${CMSSW_BASE}/src/flashggFinalFit/Background
make
cd ${CMSSW_BASE}/src/flashggFinalFit/Signal
make
```

## Contents
The FLASHgg Finals Fits package contains several subfolders which are used for the following steps:

* Create the Signal Model (see `Signal` dir)
* Create the Background Model (see `Background` dir)
* Generate a Datacard (see `Datacard` dir)
* Run `combine` and generate statistical interpretation plots. (see `Plots/FinalResults` dir)

Each of the relevant folders are documented with specific `README.md` files.

## Known issues

Recently some issues with memory have been observed with the workspaces (probably because there are so many processes and tags now). Crashes can occur due to a `std::bad_alloc()` error, which for now I have managed to circumvent by submitting to the batch (this is at Imperial College), e.g. for making the photon systematic dat files and the S+B fits. The problem is due to all the workspaces being loaded by the WSTFileWrapper class, so at some point this should be revisited and improved somwhow. 

## Updates in dev_runII_102x branch

* New, easier to navigate submission scripts: option for config file
* Integration with HTCondor
* Python module for replacement dataset map: used when too few entries to construct signal model
* Pruning: removes processes below threshold in datacard

Still some remaining updates to come in next months:

* New datacard making script
* Transition to combineTools package rather than having analysis specific script (./Plots/FinalResults/combineHarvester.py)
* Option for skipping the RV/WV split in Signal modelling
* Full functionality for merging categories across years. Currently run through each year separately

### Temporary: extracting datacards + results
The above updates will be propagated to the `Datacard` and `Results` folders soon. For now you can make the Datacards and do the fit using the `RunCombineScripts.py` submission script:
```
cmsenv
python RunCombineScripts.py --inputConfig example_config_stage1_1.py
```
The script requires an input config file of the following format (change options where necessary):
```
combineScriptCfg = {
  
  # Setup
  'mode':'datacard', # Options are datacard,combine,combinePlots
  'inputWSDir':'/vols/cms/jl2117/hgg/ws/test_stage1_1_2018', #directory of input workspaces
  #Procs will be inferred automatically from filenames
  'cats':'RECO_0J_PTH_GT10_Tag0,RECO_0J_PTH_GT10_Tag1,' #analysis categories
  'ext':'stage1_1_2018', #extension to be added to output directory. Must match that of S & B modelling
  'year':'2018', 
  'signalProcs':'all',

  # Add UE/PS systematics to datacard (only relevant if mode == datacard)
  'doUEPS':0,

  #Photon shape systematics  
  'scales':'HighR9EB,HighR9EE,LowR9EB,LowR9EE,Gain1EB,Gain6EB',
  'scalesCorr':'MaterialCentralBarrel,MaterialOuterBarrel,MaterialForward,FNUFEE,FNUFEB,ShowerShapeHighR9EE,ShowerShapeHighR9EB,ShowerShapeLowR9EE,ShowerShapeLowR9EB',
  'scalesGlobal':'NonLinearity:UntaggedTag_0:2,Geant4',
  'smears':'HighR9EBPhi,HighR9EBRho,HighR9EEPhi,HighR9EERho,LowR9EBPhi,LowR9EBRho,LowR9EEPhi,LowR9EERho',

  # Job submission options
  'batch':'HTCONDOR',
  'queue':'workday',

  'printOnly':0 # For dry-run: print command only
  
}
```
The modes are used for the following (run in sequential order):
  * `datacard` - build the .txt datacard using the S & B models. The yield variations from systematics are also calculated and specified in the datacard. To merge datacards for different years then use the `combineCards.py` script (in combine).
  * `combine`  - compile the RooWorkspace from the .txt datacard. Run the fit in combine. Input options are specified in `Plots/FinalResults/combineHarvesterOptions_Template.dat`
  * `combinePlots` - create plots from finished combine jobs. Options are specified in `Plots/FinalResults/combinePlotsOptions_Template.dat`

