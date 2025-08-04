
# Final Fits (higgsdnafinalfit)

This is the branch for using final fits with the output of HiggsDNA.

Welcome to the new Final Fits package. Here lies a a series of scripts which are used to run the final stages of CMS Hgg analyses: signal modelling, background modelling, datacard creation, final statistical interpretation and final result plots.

You can follow the latest Final Fits tutorial [here](https://gitlab.cern.ch/jspah/higgsdna_finalfits_tutorial_24/-/tree/master). Slides from an older flashgg-based tutorial series can be found [here](https://indico.cern.ch/event/963619/contributions/4112177/attachments/2151275/3627204/finalfits_tutorial_201126.pdf)

## Download and setup instructions

```
export SCRAM_ARCH=el9_amd64_gcc12
cmsrel CMSSW_14_1_0_pre4
cd CMSSW_14_1_0_pre4/src
cmsenv

COMBINE_TAG=high_mass_analysis
COMBINEHARVESTER_TAG=high_mass_analysis
FINALFIT_TAG=high_mass_finalfit

# Install Combine with the latest EL9 compatible branch
git clone https://github.com/pdevouge/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit && git fetch origin ${COMBINE_TAG} && git checkout ${COMBINE_TAG}

# Install CombineTools in CombineHarvester
cd ${CMSSW_BASE}/src
git clone -b $COMBINEHARVESTER_TAG https://github.com/pdevouge/CombineHarvester.git

# Compile libraries
cd ${CMSSW_BASE}/src
cmsenv
scram b clean
scram b -j 8

# Install Final Fit package
git clone -b $FINALFIT_TAG https://github.com/pdevouge/flashggFinalFit.git
cd flashggFinalFit/
source setup.sh
```

## Contents
The Finals Fits package contains several subfolders which are used for the following steps:

* Create the Signal Model (see `Signal` dir)
* Create the Background Model (see `Background` dir)
* Generate a Datacard (see `Datacard` dir)
* Running fits with combine (see `Combine` dir)
* Scripts to produce plots (see `Plots` dir)

The signal modelling, background modelling and datacard creation can be ran in parallel. Of course the final fits (`Combine`) requires the output of these three steps. In addition, the scripts in the `Trees2WS` dir are a series of lightweight scripts for converting standard ROOT trees into a RooWorkspace that can be read by the Final Fits package.

Finally, the objects and tools which are common to all subfolders are defined in the `tools` directory. If your input workspaces differ from the flashgg output workspace structure, then you may need to change the options here.

Each of the relevant folders are documented with specific `README.md` files. 

## How to run finalfit
### Tree2ws

First we need to convert the HiggsDNA output into RooWorkspace files ready for Final Fits.

#### Signal
To convert the root files from HiggsDNA into RooWorkspace, we need to run the following command. 

`python3 RunWSScripts.py --inputDir signal/2022preEE/root/ --inputConfig config_high_mass.py --year 2022preEE --mode trees2ws --batch local --modeOpts "--minMass 100 --maxMass 5500"`

All the RooWorkspace have the same binning for the mass (minMass-maxMass), so we need to select a range big enough to encapsulate all of our masses.

#### Data
For the data we run the following command.

`python3 RunWSScripts.py --inputDir Data/Pre/root/ --inputConfig config_high_mass.py --year 2022preEE --mode trees2ws_data --batch local --modeOpts "--applyMassCut --massCutRange 500,1000"`

Notice here that we select only a subset of the mass. This is because contrary to the signal samples, we only have one set of MC samples, which contains the entire mass range.

### Signal

The next step is to run the signal description. We need to pass a config file like [this one](https://github.com/pdevouge/flashggFinalFit/blob/high_mass_finalfit/Signal/config_high_mass_2022preEE.py). The config file contains the location of the signal RooWorskpaces, the process, category, along with the width and mass points for which we want to construct the final model.

`python3 RunSignalScripts.py --inputConfig config_high_mass_2022preEE.py --mode signalFit --modeOpts " --doPlots --skipSystematics --skipVertexScenarioSplit --skipBeamspotReweigh --nBins 500  --minMass 100 --maxMass 1100"`

The `--nBins` argument is used for the fit and for the plot of the final analytical model. <br>
For the results extraction with Combine, we package the individual ROOT files from the signalFit step into a single file per category. This is not really needed for now since we only have one category and one year, and this is just used (for now) to format our ROOT file for Combine.

`python3 RunPackager.py --cats inclusive --exts highmass_2022preEE_500-1000 --mergeYears --massPoints 500,550,600,650,700,750,800,900,1000 --batch local`

### Background

The background description is also based on a config file like [this one](https://github.com/pdevouge/flashggFinalFit/blob/high_mass_finalfit/Background/config_highmass.py). Again, the config file contains the location of the RooWorskpaces and the category. The mass range is determined by the RooWorkspace mass range `--massCutRange`.

`python3 RunBackgroundScripts.py --inputConfig config_highmass.py --mode fTestParallel {--plotDiff}`

### Datacard

We can now construct the datacard from the signal RooWorkspaces. First we calculate the nominal and systematic-varied yields for each signal (proc,cat) combination. For the nominal mass, you can choose one in the middle of the range.

`python3 RunYields.py --inputWSDirMap 2022preEE=../../2022preEE/workspaces/signal --cats inclusive --procs rsg --ext highmass_500-1000 {--mergeYears} --skipCOWCorr {--doSystematics} --batch local --mass 750`

Then, we construct the datacard as follow. 

`python3 makeDatacard.py --ext highmass_500-1000 --years 2022preEE --prune --doTrueYield --skipCOWCorr {--doSystematics} --doMCStatUncertainty --saveDataFrame --output Datacard_highmass_500-1000 --mass 750`

### Combine

The last step is to run Combine and obtain the limits. First we need to copy everything into this directory, by following these commands.
```
mkdir -p Models/signal
mkdir -p Models/background
cp ../Signal/outdir_packaged/CMS-HGG_sigfit_packaged*.root Models/signal/
cp ../Background/outdir_highmass_500-1000/CMS-HGG_multipdf*.root Models/background/
cp ../Datacard/Datacard_highmass_500-1000.txt .
```

The text datacard created in the previous (Datacard) section contains (or points to) all of the inputs that Combine requires to do statistical inference. By running the text2workspace command, we convert the text datacard into a workspace that contains the inputs. In the conversion, we also specify a model that describes the parameters of interest (POIs) and how they are related to the rates of processes in the workspace.
In flashggFinalFit, we have a job submission script to run text2workspace. We simply run the following command:

`python3 RunText2Workspace.py --mode mu_inclusive --batch local --ext _highmass_500-1000 --common_opts "-m 750 higgsMassRange=500,1000"`

Next, we create a new directory which will host all of our results:
```
mkdir limits_500-1000
```

From there, we can extract the limits for a given mass point by running the next command:

`combineTool.py -M AsymptoticLimits -d Datacard_highmass_500-1000_mu_inclusive.root --there -n .limit --parallel 4 -m 750 --run blind`

The previous command can be ran over any mass point within the (minMass-maxMass) limits of the signal model. Note that by default, combineTool.py saves the output files into the same location as Datacard_highmass_500-1000_mu_inclusive.root. One should move all of these into the previously created directory.

We can finally cd into `limits_500-1000` and merge the different root files into a json file containing the limits for each mass point:

`combineTool.py -M CollectLimits *.limit.* --use-dirs -o limits.json`
