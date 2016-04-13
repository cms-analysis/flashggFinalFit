# FLASHgg Final Fits
The Final Fits package is a series of scripts which are used to run the final stages of the CMS Hgg analysis: signal modelling, background modelling, datacard creation and final statistical interpretation and final result plots.

## Download and setup instructions

```
cmsrel CMSSW_7_1_5
cd CMSSW_7_1_5/src
cmsenv
git cms-init
# Install Combine as per Twiki: https://twiki.cern.ch/twiki/bin/viewauth/CMS/SWGuideHiggsAnalysisCombinedLimit#ROOT6_SLC6_release_CMSSW_7_1_X
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd ${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit
git fetch origin
#git checkout v5.0.1 #at present only master branch has up to date XS files
cd ${CMSSW_BASE}/src
# Install Flashgg Final Fit packages
git clone git@github.com:cms-analysis/flashggFinalFit.git
cd ${CMSSW_BASE}/src
cmsenv
scram b -j9
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

`runFinalFitsScripts.sh` has many options to control and run different parts of the final fits. Examples of how they are used can be found in `HggAnalysis_Moriond2016_example.sh`.

This example is taken from the "Moriond2016" results. You can uncomment different lines in `HggAnalysis_Moriond2016_example.sh` to run different steps of the analysis via the `runFinalFitsScripts.sh` pilot script.  

A few key examples:
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

	Most fo the options are fairly self-explanatory, but some of them could use a little extra explanation:
	* inputFile : The default file to `file` mentioned above.
	* procs: The comma-separated list of processes to run over. eg `ggh,vbf,tth,wzh`. Convention is to use lower case.
	* flashggCats: The comma-separated list of FLASHgg categories you wish to consider. Obviously the more you include the longer everything will take. These again must obviously match the ones in your workspace input `file`.
	* ext: An extension to keep track of all files associated with your exercise. Will be apepnded to output dirs, plots and root files as needed.
	* pseudoDataDat: `samples` file telling which samples to include in the pseudodata as described above.
	* combine: Tell the script to also run the combine jobs (will submit them to the batch)
	* combineOnly: Skip Signal and Background and Datacard, only do combine job submission and plots.
	* combinePlotsOnly: Skip combine job submission, just make combine plots from combine output.
	* signalOnly: Skip Background and Datacard. 
	* backgroundOnly: Skip Signal and Datacard:
	* datacardOnly: Skip Signal and Background
	* superloop: If you want to run the analysis several times with different pseudodatasets. specify how many iterations to do with this option. 
	* continueLoop: If you want to continue a previously started superloop starting from a specific index, specify it here.
	* intLumi: Override signal weight and intLumi value and adjust to be compatible with the intlumi sepcified witht his option (in fb^{-1}). Also generates more pseudodata as required.

