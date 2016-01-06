# FLASHgg Final Fits
The Final Fits package is a series of scripts which are used to run the final stages of the CMS Hgg analysis. 
## Download and setup instructions
```
cmsrel CMSSW_7_1_5
cd CMSSW_7_1_5/src
cmsenv
# Install Combine as per Twiki: https://twiki.cern.ch/twiki/bin/viewauth/CMS/SWGuideHiggsAnalysisCombinedLimit#ROOT6_SLC6_release_CMSSW_7_1_X
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
git fetch origin
git checkout v5.0.1
# Install Flashgg Final Fit packages  
git clone git@github.com:sethzenz/flashggFinalFit.git flashggFinalFit
cd ${CMSSW_BASE}/src
scram b -j 9
cd ${CMSSW_BASE}/src/flashggFinalFit/
# Make dummy 13TeV XS files. 
chmod +x convertXS.py
./convertXS.py # create 13TeV XS from 8TeV as placeholder
```

Two packages need to be built with their own makefiles, if needed.  Please note that there will be verbose warnings from BOOST etc:

```
cd ${CMSSW_BASE}/src/flashggFinalFit/Background
make
cd ${CMSSW_BASE}/src/flashggFinalFit/Signal
make
```

## Contents
The FLASHgg Finals Fits package contains several subfolders which care sused for the following steps:
	* Create the Signal Model (see `Signal` dir)
	* Create the Background Model (see `Background` dir)
	* Generate a Datacard (see `Datacard` dir)
* Run `combine` and generate statistical interpretation plots. (see `Plots/FinalResults` dir)


## Quickstart

	In theory each of the above shoudl be run one by one. You will find sintructions for each in individual `README.md` files in each relevant subdir. Thankfully, if you just want to run a basic version of the Final Fits, you can use a dedicated pilot script: `runFinalFitsScripts.sh`
	```
	file=/afs/cern.ch/user/l/lcorpe/work/public/big_test_jobs_2/everything.root
	samples=samples=/afs/cern.ch/user/l/lcorpe/work/public/big_test_jobs_2/samples.txt
	./runFinalFitsScripts.sh -i $file -p ggh -f UntaggedTag_0 --ext intlumitest1fb --pseudoDataDat $samples --intLumi 1
	```
	This script will run all parts of the analysis, and produce the output plots as needed.
	`file` should be the FLASHgg output file containign at minimum all the RooDataSets for the signal processes and tags you wish to consier, as well as their systematic variations.
	`samples` is a dat file containing all sampels you wish to use to generate pseudodata. Open the file up to check the required format: 
	```
	<type>,<full sample path>
	```
	where type can be `sig` or `bkg`.

	Tou can run `./runFinalFitsScripts.sh -h` to check the available options.

## Some interesting options

	Most fo the options are fairly self-explanatory, but some of them could use a little extra explanations:
	* inputFile : The default file to `file` mentioned above,
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
	* intLumi: Override signal weight and intLumi value and adjust to be compatible with the intlumi sepcified witht his option (in fb^{-1}). Also generates more pseudodata as requried.


