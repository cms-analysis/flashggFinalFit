# Signal modelling

There are a number of steps to perform when constructing the signal model (described below). It is recommended to construct a signal model for each year separately. This allows to keep track of both the year-dependent resolution effects and the year-dependent systematic uncertainties. Each step up to the packaging is ran using the `RunSignalScripts.py` script, which takes as input a config file e.g.:

```
# Config file: options for signal fitting

_year = '2022preEE'

signalScriptCfg = {

  # Setup
  'inputWSDir':'/eos/user/j/jlangfor/icrf/hgg/FinalFitsTutorial/higgsdna_finalfits_tutorial_24/inputs/workspaces/signal_%s'%_year,
  'procs':'auto', # if auto: inferred automatically from filenames
  'cats':'auto', # if auto: inferred automatically from (0) workspace
  'ext':'tutorial_%s'%_year,
  'analysis':'tutorial', # To specify which replacement dataset mapping (defined in ./python/replacementMap.py)
  'year':'%s'%_year, # Use 'combined' if merging all years: not recommended
  'massPoints':'120,125,130',

  #Photon shape systematics  
  'scales':'Scale', # separate nuisance per year
  'scalesCorr':'', # correlated across years
  'scalesGlobal':'', # affect all processes equally, correlated across years
  'smears':'Smearing', # separate nuisance per year

  # Job submission options
  'batch':'condor', # ['condor','SGE','IC','local']
  'queue':'espresso',

}
```
The basic command for using `RunSignalScripts.py` is the following:
```
python3 RunSignalScripts.py --inputConfig {config_file}.py --mode {mode} --modeOpts "{list of options for specific mode}" --jobOpts "{list of options for job submission}"
```
To simply print the job scripts without submitting then add the option: `--printOnly`. You can then go to the respective `outdir_{ext}/{mode}/jobs` directory to run the individual scripts locally (great for testing and debugging!)

In this new final fits package we have introduced a number of additional options which were not previously available. Firstly, you can now run the signal model for a single mass point: the polynominal defining the mass dependence on the fit parameters is set to a constant. Additionally, you can skip the splitting into the right vertex (RV) and wrong vertex (WV) scenarios (in fact the fraction of WV events for anything but ggH 0J is ~0, so the general rule of thumb is that it is okay to skip the splitting). In the new package the minimizer has been replaced with `scipy.minimize`, which means we no longer require the specialised ROOT class for the simultaneous signal fit for different mass points. For developers of this package you can find the Python class which performs the signal fit in `tools.simultaneousFit`. A simple application of this is shown in `simpleFit.py`. The construction of the final signal model is done using the Python class in `tools.finalModel.py`

## Signal F-test

Test for determining the optimal number of gaussians to use in signal model. If you want to use the Double Crystal Ball (DCB) + Gaussian function for the models then you can skip the F-test.

```
python3 RunSignalScripts.py --inputConfig config_tutorial_2022preEE.py --mode fTest
```
This will create a separate job per analysis category, which outputs a json file (`./outdir_{ext}/fTest/json`) specifying the optimal number of Gaussians for each signal process for both the RV (right-vertex) and WV (wrong-vertex) scenarios. The optimal number of gaussians is chosen as the number which minimises the reduced chi2.

In general, we only need to know the shape for the signal processes which have a sizeable contribution in a given category. By default the fTest script will only calculate the optimal number of Gaussians for the 5 signal processes in a category with the highest sum of weights. The other signal processes are set to (nRV,nWV)=(1,1). To toggle this number add the option `--nProcsToFTest X` into the `--modeOpts` string, where X will replace 5. To determine the optimum for all signal processes then set X = -1.
```
python3 RunSignalScripts.py --inputConfig config_tutorial_2022preEE.py --mode fTest --modeOpts "--nProcsToFTest X"
```
To produce the fTest plots then add `--doPlots` to the `--modeOpts` string.

For other options when running `fTest`, see `./scripts/fTest`

## Photon systematics

For calculating the effect of the photon systematics on the mean, width and rate of the signal spectrum.
```
python3 RunSignalScripts.py --inputConfig config_tutorial_2022preEE.py --mode calcPhotonSyst
```
This will again create a separate job per category, where the output is a pandas dataframe stored as a `.pkl` file. The dataframe contains the constants which describe how the systematics (specified in the `config` file) affect the mean, sigma and rate of each signal process. The final model construction will lift these constants directly from the `.pkl` files (replaced the monolithic `.dat` files in the old Final Fits).

If you do not wish to account for the photon systematics then this step can be skipped completely.

For other options when running `calcPhotonSyst`, see `./scripts/calcPhotonSyst` and add whatever you need to the `--modeOpts` string.

## Normalising the signal model: efficiency x acceptance

The final models are normalised according to the following equation:
![equation](https://latex.codecogs.com/gif.latex?N_{ij}&space;=&space;(\sigma&space;\cdot&space;BR)_i&space;\times&space;(\epsilon&space;\cdot&space;\mathcal{A})_{ij}&space;\times&space;\mathcal{L})

where `Nij` is the number of signal events of process, i in category j. The `(eff x acc)ij` defines the fraction of signal process, i falling in category, j. 

The output of HiggsDNA is configured such that the sum of weights for a process, i in category, j is exactly the efficiency-times-acceptance e.g. if 40% of ggH events land in `cat0`, then the sum of weights will be equal to 0.4. This makes the calculation of the signal model normalisation significantly easier than what we had in the past for flashgg. In this branch we have deprecated the `getEffAcc` functionality which calculated the efficiency-times-acceptance using the `NOTAG` dataset. If this functionality is still required then go back to an old branch of Final Fits e.g. `dev_fggfinalfits_lite`.

## Extracting the diagonal process for a given category

There are two options in the final model construction which require the knowledge of the diagonal process (i.e. highest sum of weights) in the analysis categories. The following mode determines the diagonal proc and outputs this info in a json file to be read by the final model construction:
```
python3 RunSignalScripts.py --inputConfig config_tutorial_2022preEE.py --mode getDiagProc
```

## Final model construction

Before you build the final models you MUST define the replacement dataset and the `xs x BR` mappings. 

 * In `tools/replacementMap.py` you need to specify the replacement (process,category) to use when the number of events is below a threshold (defined by by the `--replacementThreshold` option, where the default threshold is 100 events). The mapping is selected by the `analysis` option in the input config file. For a thorough example see the `STXS` mapping. You will need to produce a similar map, configured for your analysis.

 * In `tools/XSBRMap.py` you need to specify the normalisation of your signal processes. We use the [data files](https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit/tree/102x/data/lhc-hxswg/sm) in combine to build MH-dependent cross sections and branching ratios for the major Higgs boson production modes and decay channels. You then need to specify in the mapping how each of your signal processes are normalised according to these cross sections/branching ratios (see `factor` in `STXS` map for an example). If your signal process has an arbitrary normalisation e.g. 0.001 pb with a branching ratio of 1 then you can use the `'mode':'constant'` feature (see lines 10 and 11). Again the mapping is selected by the `analysis` option in the input config file.

You are now ready to run the actual fit:
```
python3 RunSignalScripts.py -inputConfig config_tutorial_2022preEE.py --mode signalFit --groupSignalFitJobsByCat
```
The `groupSignalFitJobsByCat` option will create a submission script per category. If removed, the default is to have a single script per process x category (which can be a very large number!). The output is a separate ROOT file for each process x category containing the signal fit workspace.

There are many different options for running the `signalFit` which can be added to the `--modeOpts` string. These are defined in `./scripts/signalFit`:

 * `--doPlots`: plot interpolation of signal model, the various normalisation inputs and the shape pdf split into its individual components.
 * `--nBins`: number of bins to use in fit. Default = 80.
 * `--useDiagonalProcForShape`: use the shape of the diagonal process in the category (requires running the `getDiagProc` mode first).
 * `--beamspotWidthMC X` and `--beamspotWidthData Y`: change the beamspot width values for MC and data [cm] for when reweighting the MC to match the data beamspot distribution. You can skip this reweighting using the option `--skipBeamspotReweigh'. Default is set to the 2022 (postEE) values.
 * `--useDCB`: use DCB + 1 Gaussian as pdf instead of N Gaussians.
 * `--doVoigtian`: replace all Gaussians in the signal model with Voigtians (used for Higgs total width studies).
 * `--skipVertexScenarioSplit`: skip splitting the pdf into the RV and WV scenario and instead fit all events together.
 * `--skipZeroes`: skip generating signal models for (proc,cat) with 0 events.
 * `--skipSystematics`: skip adding photon systematics to signal models. Use if have not ran the `calcPhotonSyst` mode.
 * `--useDiagonalProcForSyst`: takes the systematic constants from diagonal process (requires running the `getDiagProc` mode first). Useful if the MC statistics are low which can lead to dubious values for systematics constants.
 * `--replacementThreshold`: change the threshold number of entries with which to use replacement dataset. Default = 100
 * `--MHPolyOrder`: change the order of the polynomial which defines the MH dependence of fit parameters. Default is a linear interpolation (1). If using only one mass point then this is automatically set to 0.
 * `minimizerMethod` and `minimizerTolerance`: options for scipy minimize, used for fit

## Packaging the output

Package the individual ROOT files from the `signalFit` into a single file per category. Here you can also merge across years to package all years into a single file. For example, packaging 2016, 2017 and 2018 models for categories `cat0` and `cat1`:
``` 
python3 RunPackager.py --cats cat0,cat1 --exts test_2016,test_2017,test_2018 --mergeYears
```
where `exts` are the `outdir` extensions that you want to merge. To automatically infer the categories from an input flashgg workspace use:
```
--cats auto --inputWSDir {path to flashgg workspace dir}
```
The output are the packaged signal models ready for the final fits!

## Signal model plots

Run on the packaged signal models to produce this kind of [plot](http://cms-results.web.cern.ch/cms-results/public-results/preliminary-results/HIG-19-015/CMS-PAS-HIG-19-015_Figure_012-a.pdf). 
```
python3 RunPlotter.py --procs all --years 2016,2017,2018 --cats cat0 --ext packaged
```
The options are defined in `RunPlotter.py`. Use `--cats all` to plot the sum of all analysis categories in `./outdir_{ext}` directory.

To weight the categories according to their respective (S/S+B) then you can use the `--loadCatWeight X` option, where X is the output json file of `../Plots/getCatInfo.py`.



