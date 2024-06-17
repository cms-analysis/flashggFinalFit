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

COMBINE_TAG=07b56c67ba6e4304b42c3a6cdba710d59c719192
COMBINEHARVESTER_TAG=94017ba5a3a657f7b88669b1a525b19d34ea41a2
FINALFIT_TAG=higgsdnafinalfit

# Install Combine with the latest EL9 compatible branch
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit && git fetch origin ${COMBINE_TAG} && git checkout ${COMBINE_TAG}

# Install CombineTools in CombineHarvester
cd ${CMSSW_BASE}/src
bash <(curl -s https://raw.githubusercontent.com/cms-analysis/CombineHarvester/${COMBINEHARVESTER_TAG}/CombineTools/scripts/sparse-checkout-https.sh)
cd CombineHarvester && git fetch origin ${COMBINEHARVESTER_TAG} && git checkout ${COMBINEHARVESTER_TAG}

# Compile libraries
cd ${CMSSW_BASE}/src
cmsenv
scram b clean
scram b -j 8

# Install Final Fit package
git clone -b $FINALFIT_TAG https://github.com/cms-analysis/flashggFinalFit.git
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
