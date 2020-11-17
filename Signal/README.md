# Signal modelling

Add some intro details here.

There are a number of steps to perform when constructing the signal model (described below). It is recommended to construct a signal model for each year separately. This allows to keep track of both the year-dependent resolution effects and the year-dependent systematic uncertainties. Each step up to the packaging is ran using the `RunSignalScripts.py` script, which takes as input a config file e.g.:

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
python RunSignalScripts.py --inputConfig {config_file}.py --mode {mode} --modeOpts "{list of options for specific mode}" --jobOpts "{list of options for job submission}"
```
To simply print the job scripts without submitting then add the option: `--printOnly`

## Signal F-test

Test for determining the optimal number of gaussians to use in signal model. If you want to use Double Crystal Ball (DCB) + Gaussian function for the models then you can skip the F-test.

```
python RunSignalScripts.py --inputConfig config_test_2016.py --mode fTest
```
This will create a separate job per analysis category, which outputs a json file (`./outdir_{ext}/fTest/json`) specifying the optimal number of Gaussians for each signal process for both the RV (right-vertex) and WV (wrong-vertex) scenarios. The optimal number of gaussians is chosen as the number which minimises the reduced chi2.

In general, we only need to know the shape for the signal processes which have a sizeable contribution in a given category. By default the fTest script will only calculate the optimal number of Gaussians for the 5 signal processes in a category with the highest sum of weights. The other signal processes are set to (nRV,nWV)=(1,1). To toggle this number add the option `--nProcsToFTest X` into the `--modeOpts` string, where X will replace 5. To determine the optimum for all signal processes then set X = -1.
```
python RunSignalScripts.py --inputConfig config_test_2016.py --mode fTest --modeOpts "--nProcsToFTest X"
```
To produce the fTest plots then add `--doPlots` to the `--modeOpts` string.

For other options when running `fTest`, see `./scripts/fTest`

## Photon systematics

## Extracting the efficiency x acceptance

## Extracting the diagonal process for a given category

## Final model construction

Add details about replacementMap and XSBRMap


## Packaging the output

## Signal model plots
