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

# HHWWgg Specific Instructions 

## Clone Repository 

After cloning the repository, the main HHWWgg script is HHWWggFinalFitScript.sh, which is used to call each of the finalfit steps. 

## Background 

### f-Test

To produce a background model, you first need a config file. You can begin with the example Background/HHWWgg_Synch_Background_Config.py. This contains the parameters for running the background fits. 

An explanation of the important parameters to set:
  
  * inputWSDir: Input workspace directory. This is the directory containing your hadded data workspace. If you are running on one year of data, for example 2017, this directory should contain one file: allData.root 
  * cats: These are the categories to fit, where these categories are originally defined in flashgg. For example, for the current state of the HHWWgg semileptonic analysis there are two categories: HHWWggTag_0 corresponding to the semi-leptonic electron channel, and HHWWggTag_1 corresponding to the semi-leptonic muon channel. To produced background models for both categories, you should specify both categories separated by commas like so: 'HHWWggTag_0,HHWWggTag_1'
  * ext: Extension. This is used for the naming scheme of the output directory and files. This should be chosen and kept consistent for the extension used for the signal modelling. 
  * year: The data year. 2017 for 2017 data. 
  * unblind: (1): Data is unblinded. (0): Data blinded. 
  * batch and queue: These are for running in batch mode, which is currently not setup for HHWWgg. For now it automatically runs locally. 
  * analysis: This should be set to HHWWgg to run the HHWWgg specific naming schemes. 
  * mode: The function to run the script on. Options: [std,fTestOnly,bkgPlotsOnly]

After setting the python configuration file you want to use in the backgroundftest option in HHWWggFinalFitScript.sh, and setting the proper parameters in your configuration file, you can run the background ftest with:

```
. HHWWggFinalFitScript.sh backgroundftest 
```

If this works properly, you should see the directory Background/outdir_<extension>/bkgfTest-Data containing many output images including multipdf_<category>.png/pdf showing the different functional fits to the data for each category. You should also see a root file Background/CMS-HGG-multipdf_<extension>.root containing the RooWorkspace "multipdf" containing the functional fit variables, pdfs and parameters, which can be seen with multipdf->Print(). 

## Signal 

Next are the functions to run on the signal. You can begin with the example configuration Signal/HHWWgg_Synch_Signal_Config.py. 

This configuration contains the following parameters:
  * systematics: Set to 1 to look for systematic trees in signal workspace. Set to 0 to not generate a systematics dat file.
  * inputWSDir: Input workspace directory. This should contain all signal files you'd like to run over. For example, this could contain all resonant mass points. 
  * useprocs: Use production modes. For HHWWgg, this needs to be set to look for certain processes, as this needs to correspond to the file names. For example, to run on Spin-0 or Spin-2 resonant files, you would set this to ggF. To run on NMSSM, this should be set to GluGluToHHTo. Again, the point is this corresponds to the input file naming convention. 
  * cats: Categories. Same definition as Background instructions. These are the categories that will be looked for in the signal workspaces. 
  * ext: Extension. Same definition as Background instructions. This should be the same as the extension used for the background model you want to combine with your signal models. 
  * analysis: Set to HHWWgg to configure for HHWWgg file naming conventions.
  * analysis_type: Used for HHWWgg. Set to either EFT, Res or NMSSM. Used to configure the names of the workspaces, used for easily looping over mass points, mass pairs or benchmarks. 
  * year: Data taking year. 
  * scales, scalesCorr, scalesGlobal, smears: Systematic trees to look for in signal workspaces. 
  * batch and queue: Set to empty strings as HHWWgg only configured to run locally. 
  * mode: Function to run on signal. To run with systematics, set to "std" and run HHWWggFinalFitScript.sh twice. To run without systematics, run the following steps in order: std, sigFitOnly, packageOnly, sigPlotsOnly 

After setting the parameters properly, you are ready to run the signal fit steps. 

To run with systematics, you should set the mode to "std", make sure the correct configuration file name is specified in HHWWggFinalFitScript for the signal step, and then run the command . HHWWggFinalFitScript.sh signal. 

This should run the fTest step, providing the recommended number of gaussians to use to fit each signal category. If this runs properly, you should find a directory Signal/outdir_<entension>_<signalPoint>_<Process>. In this directory you should find sigfTest containing the gaussian sum f-test fits for rv (right vertex) and wv (wrong vertex) for each category.

To continue with the signal fitting, run the same command: . HHWWggFinalFitScript.sh signal. If this runs properly, you should see many new folders added to the Signal/outdir directory. 

## Datacard 

The next step is to create the datacard containing information from the Background and Signal workspaces to be used by combine. An example configuration file used for this step is HHWWgg_Synch_Combine_Config.py. Most if not all of the parameters here are previously explained in either the Signal or Background sections. The main thing to remember is that the extension needs to stay consistent here. As long as the parameters are set properly, and the datacard step of HHWWggFinalFitScript.sh is looking for the proper configuration file, you should now run: 

```
. HHWWggFinalFitScript.sh datacard 
```

If it works properly, this should create a directory Datacard/<extension>, containing the datacard. Note that the datacard ending with "_cleaned.txt" is the one used in the combine step.

## Combine

If you are satisfied with the datacard, you can now run combine with: 

```
. HHWWggFinalFitScript.sh combine  
```

If this works properly, the background and signal models will be used to compute the upper limit of the signal process. Note that if a branching ratio was not defined in the signal model steps (for HHWWgg, it is currently not) then this result will be the quantile values of the upper limit of cross section (production->HH->WWgg->finalstate). In order to obtain the upper limit on WWgg you need to divide by the branching ratio of the final state * 2 because either W can decay into this, and then divide by the branching ratio of HH->WWgg * 2 because either H can decay to WW or gg. For the moment, these computations are done in Plots/FinalResults/plot_limits.py 