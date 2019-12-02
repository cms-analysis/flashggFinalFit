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

