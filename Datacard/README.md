# Datacard generation

This is where you build the `.txt` datacard to be used for the final fits (see `../Combine`).


## Calculate the yields

The first step is to produce a pandas dataframe for each analysis category which holds information on the signal models, background models and the data. For each signal process, the dataframe stores the nominal yields (sum of weights) as well as the varied yields for each systematic uncertainty source (excluding the signal shape uncertainties). The systematics are defined in `systematics.py`. Simply comment out (or add new) systematics where appropriate. If you want to ignore the systematics completely then just run the following command without the `--doSystematics` option:
```
python RunYields.py --cats auto --inputWSDirMap 2016={path to 2016 flashgg workspaces},2017={path to 2017 workspaces},2018={path to 2018 workspaces} --procs auto (--mergeYears) (--doSystematics) --batch condor --queue longlunch
```
This script creates a job for each analysis category in the `yields` directory and submits this job to the batch. The output is the pandas dataframe, stored as a `pkl` file. To produce the job script without submitting, add the option `--dryRun`.

The option `--mergeYears` will merge the signal processes from the different years into the same category. If removed then the categories are separated by year and an additional year tag is added at the end of the category name in the output dataframe. The `auto` inputs for the `--cats` and `--procs` options means that the categories and signal processes are automatically inferred from the input flashgg workspaces. Otherwise use a comma separated list of cats and procs.

The `inputWSDirMap` simply maps the year to the path to input flashgg workspaces. You do not need to process all years together as shown in the example above.

Additional options:

  * `--ext`: add an extension to the output directory for saving.
  * `--bkgScaler`: for adding an overall scale factor for the background models
  * `--doNOTAG`: also calculate the yields for the `NOTAG` datasets. This is useful for the theory shape uncertainties if you want to include out-of-acceptance events (i.e. model the migrations in and out of experimental acceptance). This requires the `NOTAG` datasets to be present in the flashgg workspaces.
  * `--skipZeroes`: do not add signal process to dataframe with 0 sum of weights
  * `--skipCOWCorr`: by default the theory shape uncertainties which use event weights are corrected using the centalObjectWeight of each event. To remove this correction then add this option.
  * `--ignore-warnings`: Skip errors for missing systematics in flashgg workspaces. By default, all missing systematics will throw an error which stops the scripts.

### Systematics details

The systematics are defined in `systematics.py`. Simply comment out (or add new) systematics where appropriate. By default, systematics are not included. Add the option `--doSystematics` to include.

Systematics are separated into the theory uncertainties, experimental yield uncertainties and signal shape uncertainties.

The signal shape uncertainties are defined at the end of `systematics.py`, where for each entry the `'mode'` needs to match the type of systematic in the signal model. These are specified as `param`'s in the output datacard.

The remaining uncertainties affect the yield of each process and appear as `lnN` nuisance parameters in the datacard. Uncertainties with `'type':'constant'` are defined either by the `'value'` directly in the systematics dictionary e.g. `BR_hgg` or by a path to a json file storing the value of the systematic for each signal process it affects e.g. `QCDscale_ggH`.

For systematics of `'type':'factory'`, their value is automatically calculated from the input flashgg workspace. The `'name'` must match the name of the systematic in the flashgg workspace. The function `tools.calcSystematics.factoryType` determines if the systematic is stored as a weight in the nominal RooDataSet e.g. `TriggerWeight` (asymmetric up/down weight), `scaleWeight` (symmetric single weight) or if the systematic is stored as a separate RooDataHist e.g. `JEC`. The `tools.calcSystematics.calcSystYields` function will then calculate the systematic varied yield accordingly... it should all happen under the hood, so for any systematics stored as weights or RooDataHists then set the `'type':'factory'`.

Each systematic has the option to `correlateAcrossYears`. If set to 0 then a separate nuisance parameter will be added to the datacard for each year.

Finally the theory systematics (of `'type':'factory'`) have an additional input `'tiers'`. The value is a list of the different effects of the uncertainty you want to include:

 * `shape`: absolute yield of each signal process is kept constant. This effectively calculates the migrations of events across analysis categories i.e. the shape effects. This is the nominal choice for `scaleWeights`, `PDFWeights` and `alphaSWeights`. If the `NOTAG` dataset is included, then it also accounts for migrations in and out-of acceptance.

 * `ishape`: same as `shape` but the absolute yield of the signal process can vary. There is no difference between `ishape` and the default method for calculating systematic variation i.e. variation for each proc x category. In fact `ishape` is effectively what is used to calculate the experimental systematics.

 * `norm`: absolute yield of production mode (s0) is kept constant. Calculate migrations across sub-processes e.g. migrations across STXS bins for ggH but keeping the total ggH constant. The value is for the whole sub-process i.e. integrated across analysis categories.

 * `inorm`: same as `norm` but the yield of s0 is allowed to vary. This accounts for migrations across sub-processes as well as absolute effect on the yield of a given production mode. Use this for e.g. `THU_ggH_*`

 * `inc`: variations for production mode (s0). The value is the same for all sub-processes i.e. integrated across STXS bins. Usually not used.

 * `mnorm`: specific to the STXS analysis for merged bins. Keep integral of merged bin constant but allows for migrations across merged boundaries. Ask authors for more details.

 
## Make the datacard

Once the `pkl` files have been produced then you are ready to make the datacard:
```
python makeDatacard.py --years 2016,2017,2018 --prune (--doSystematics)
```
The datacard will be produced using the concatenation of all `pkl` files in the `yields` directory. The `--prune` option will prune all signal processes which contribute less than 0.1% to the total signal yield in a given category. This threshold has been shown to have negligible effect on the final results but can be toggled using the `--pruneThreshold 0.001` option.

The pruning by default uses the sum of weights in the input flashgg workspace. If the `NOTAG` dataset is present then you can also calculate the true yields using XS, BR and `eff x acc`. For this add the option `--doTrueYields`, ensuring that the full signal process XSBR map is defined in `tools.XSBR.py` (same as the mapping in the signal modelling).

The output is a `.txt` datacard that can be used for the final fits!

Additional options for the STXS analysis:
 * `--doSTXSMerging`: calculate addition migration uncertainties for merged STXS bins (where `mnorm` tier has been specified).
 * `--doSTXSScaleCorrelationScheme`: de-correlate scale uncertainties for different regions of phase space according to [this](https://twiki.cern.ch/twiki/bin/viewauth/CMS/HiggsWG/SignalModelingTools)


## Cleaning

There is an additional light weight script which cleans up the datacards i.e. remove double-sided uncertainties (both up/down variations act in same direction) and all those with a factor greater than a specified value (useful for low MC stats): 
```
python cleanDatacard.py --datacard Datacard.txt --factor 2 --removeDoubleSided
```


## Combine Cards

The above scripts have the full functionality for merging some cats and splitting others. Nevertheless if you want to run for each year separately this is also fine! At the end you can then build a combined datacard using the `combineCards.py` script of combine. Note, systematics with a common name will be correlated.
```
combineCards.py Datacard_2016.txt Datacard_2017.txt Datacard_2108.txt > Datacard_combined.txt
```
