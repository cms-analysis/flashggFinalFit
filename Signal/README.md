# Signal modelling

Add some intro details here.

There are a number of steps to perform when constructing the signal model (described below). It is recommended to construct a signal model for each year separately. This allows to keep track of both the year-dependent resolution effects and the year-dependent systematic uncertainties. Each step up to the packaging is ran using the `RunSignalScripts.py` script, which takes as input a config file to specify the options for the signal modelling.

For example: this config file corresponds to running over 2016 signal workspaces:
```
# Config file: options for signal fitting

signalScriptCfg = {
  
  # Setup
  'inputWSDir':'/vols/cms/jl2117/hgg/ws/UL/Sept20/MC_final/signal_2016', # dir storing flashgg workspaces
  'procs':'auto', # if auto: inferred automatically from filenames
  'cats':'auto', # if auto: inferred automatically from (0) workspace
  'ext':'test_2016', # output directory extension
  'analysis':'example', # To specify replacement dataset and XS*BR mapping (defined in ./tools/replacementMap.py and ./tools/XSBRMap.py respectively)
  'year':'2016', # Use 'combined' if merging all years: not recommended
  'massPoints':'120,125,130',

  #Photon shape systematics  
  'scales':'HighR9EB,HighR9EE,LowR9EB,LowR9EE,Gain1EB,Gain6EB', # separate nuisance per year
  'scalesCorr':'MaterialCentralBarrel,MaterialOuterBarrel,MaterialForward,FNUFEE,FNUFEB,ShowerShapeHighR9EE,ShowerShapeHighR9EB,ShowerShapeLowR9EE,ShowerShapeLowR9EB', # correlated across years
  'scalesGlobal':'NonLinearity,Geant4', # affect all processes equally, correlated across years
  'smears':'HighR9EBPhi,HighR9EBRho,HighR9EEPhi,HighR9EERho,LowR9EBPhi,LowR9EBRho,LowR9EEPhi,LowR9EERho', # separate nuisance per year

  # Job submission options
  'batch':'condor', # ['condor','SGE','IC','local']
  'queue':'espresso' # use hep.q for IC

}
```
The basic command for using `RunSignalScripts.py` is the following:
```
python RunSignalScripts.py --inputConfig config_{}.py --mode {mode} --modeOpts "{list of options for specific mode}" --jobOpts "{list of options for job submission}"
```
The available modes are:

 * fTest
 * calcPhotonSyst
 * getDiagProc
 * getEffAcc
 * signalFit

## Signal F-test

Test for determining the optimal number of gaussians to use in signal model. If using Double Crystall Ball + Gaussian function for model then you can skip the F-test.

```
python RunSignalScripts.py

## Photon systematics

## Extracting the efficiency x acceptance

## Extracting the diagonal process for a given category

## Final model construction

Add details about replacementMap and XSBRMap


## Packaging the output

## Signal model plots
