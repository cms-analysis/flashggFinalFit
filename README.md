# FLASHgg Final Fits
The Final Fits package is a series of scripts which are used to run the final stages of the CMS Hgg analysis: signal modelling, background modelling, datacard creation and final statistical interpretation and final result plots.

## Download and setup instructions

```
cmsrel CMSSW_7_4_7
cd CMSSW_7_4_7/src
cmsenv
git cms-init
# Install Combine as per Twiki: https://twiki.cern.ch/twiki/bin/viewauth/CMS/SWGuideHiggsAnalysisCombinedLimit#ROOT6_SLC6_release_CMSSW_7_4_X
# They recently migrated to 81X; we will follow shortly, but checkout 74X branch for now
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd ${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit
git fetch origin
git checkout origin/74x-root6
git checkout -b mybranch
cd ${CMSSW_BASE}/src
# Install the GBRLikelihood package which contains the RooDoubleCBFast implementation
git clone git@github.com:bendavid/GBRLikelihood.git HiggsAnalysis/GBRLikelihood
# Compile external libraries
cd ${CMSSW_BASE}/src/HiggsAnalysis
cmsenv
scram b -j9
# Install Flashgg Final Fit packages
cd ${CMSSW_BASE}/src/
git clone git@github.com:cms-analysis/flashggFinalFit.git
cd ${CMSSW_BASE}/src/flashggFinalFit/
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

## Quickstart

In theory each of the above should be run one by one. You will find instructions for each in individual `README.md` files in each relevant subdir. Thankfully, if you just want to run a basic version of the Final Fits, you can use a dedicated pilot script: `runFinalFitsScripts.sh`.

`runFinalFitsScripts.sh` has many options to control and run different parts of the final fits. Examples of how they are used can be found in `HggAnalysis_ICHEP2016_example.sh`.

This example is taken from the "ICHEP2016" results. You can uncomment different lines in `HggAnalysis_ICHEP2016_example.sh` to run different steps of the analysis via the `runFinalFitsScripts.sh` pilot script.  

A few key examples, although many other options exist:
```
#signal model preparation
./runFinalFitsScripts.sh -i <comma separated list of signal files> -p <comma separated list of processes> -f <comma separated list of catgeories/tags> --ext <file extension/name to identify this iteration> --batch <batch system: LSF (Cern) or IC> --intLumi <specified in fb^{-1}> --smears <photon energy smear categories> --scales <photon energy scale categories>  --signalOnly 
#background model preparation
#./runFinalFitsScripts.sh -i <comma separated list of signal files> -p <comma separated list of processes> -f <comma separated list of catgeories/tags> --ext <file extension/name to identify this iteration> --intLumi <specified in fb^{-1}> --backgroundOnly --dataFile <data file> --isData --batch <batch system: LSF (Cern) or IC> 
#datacard generation
#./runFinalFitsScripts.sh -i <comma separated list of signal files>125 -p <comma separated list of processes> -f <comma separated list of catgeories/tags> --ext <file extension/name to identify this iteration>  --intLumi <specified in fb^{-1}> --datacardOnly --dataFile <data file> --isData --batch <batch system: LSF (Cern) or IC>
#running combine and the final results
#./runFinalFitsScripts.sh -i <comma separated list of signal files> -p <comma separated list of processes> -f <comma separated list of catgeories/tags> --ext <file extension/name to identify this iteration>  --intLumi <specified in fb^{-1}> --combineOnly --dataFile <data file> --isData --batch <batch system: LSF (Cern) or IC>
```

This script will run all parts of the analysis, and produce the output plots as needed. Since it considers all the Tags and processes, it will be very long to run. To practice, you may consider running only ggh and vbf processes, for example.

You can run `./runFinalFitsScripts.sh -h` to check the available options.

## Some interesting options

	Most of the options are fairly self-explanatory, but some of them could use a little extra explanation:
	* inputFile : The default file to `file` mentioned above.
	* procs: The comma-separated list of processes to run over. eg `ggh,vbf,tth,wzh`. Convention is to use lower case.
	* flashggCats: The comma-separated list of FLASHgg categories you wish to consider. Obviously the more you include the longer everything will take. These again must obviously match the ones in your workspace input `file`.
	* ext: An extension to keep track of all files associated with your exercise. Will be apepnded to output dirs, plots and root files as needed.
	* combine: Tell the script to also run the combine jobs (will submit them to the batch)
	* combineOnly: Skip Signal and Background and Datacard, only do combine job submission and plots.
	* combinePlotsOnly: Skip combine job submission, just make combine plots from combine output.
	* signalOnly: Skip Background and Datacard. 
	* backgroundOnly: Skip Signal and Datacard:
	* datacardOnly: Skip Signal and Background
	* intLumi: Override signal weight and intLumi value and adjust to be compatible with the intlumi sepcified witht his option (in fb^{-1}).
	* bs: reweight the beamspot to be this value, specified in cm (should be the value from data)

## Known issues

Recently some issues with memory have been observed with the workspaces (probably because there are so many processes and tags now). Crashes can occur due to a `std::bad_alloc()` error, which for now I have managed to circumvent by submitting to the batch (this is at Imperial College), e.g. for making the photon systematic dat files and the S+B fits. The problem is due to all the workspaces being loaded by the WSTFileWrapper class, so at some point this should be revisited and improved somwhow. 
