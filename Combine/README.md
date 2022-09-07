# Running the fits

Now the signal and background models and the datacard has been produced, it is time to run the fits using [combine](https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/). We have replaced the old combineHarvester.py script (specific to H->gg) with the common tools. Please refer to the linked manual for the details on fitting and the options you can use.

## Copy everything across

The very first step is to copy your signal and background models, and the `.txt` datacard to this directory. I have not written a script for this yet so please do it by hand. The signal and background models must match the specified paths in the `.txt` datacard (the default is `./Models/signal` and `./Models/background`, you can change this with the `--sigModelWSDir` and `--bkgModelWSDir` options in the `Datacard/RunYields.py` script) i.e.
```
mkdir Models
mkdir Models/signal
mkdir Models/background
cp /path-to-signal-models/CMS-HGG*.root ./Models/signal/
cp /path-to-background-models/CMS-HGG*.root ./Models/background/
cp /path-to-datacard/Datacard.txt .
```

## Building the workspace

Then you are ready to build the `RooWorkspace` from the `.txt` datacard i.e. construct the likelihood function. At this step you need to specify the signal parametrization (physics model) you want to use in the fit. These parametrizations are defined in `models.py`:

 * `mu_inclusive`: common signal strength for all signal processes

 * `mu`: per-production mode signal strength. This uses the `multiSignalModel` in combine to define the mapping between the parameter of interest (poi) and each signal process. The mapping is of the format `--PO \"map={cat}/{proc}:poi[nominal,min,max]\"`, where you can use wildcards to scale all processes which match the input string by the same poi. See also STXS `stage0`, `stage1p2_maximal` and `stage1p2_minimal` for example. You will need to write your own entry in the `models.py` file for a specific mapping.

 * `kappas`: an example of using a pre-defined `PhysicsModel` in combine. You can find the full list [here](https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit/tree/102x/python). If needed, you will need to add an entry into the `models.py` file.

Once you have decided/defined your signal parametrization you can run: 
```
python RunText2Workspace.py --mode {model} --dryRun
```
where `{model}` matches the key in `models.py`. For the simplest case, where you scale all signal processes equally then use `--mode mu_inclusive`.

The `--dryRun` option means the script (produced in `t2w_jobs`) will not be submitted. You can then go and run this script locally (recommend for analyses with a small number of categories as this step should not take too long). For bigger analyses you will want to submit the job to your favourite batch system e.g.
```
python RunText2Workspace.py --mode {model} --batch condor --queue workday
```
The output will be a compiled `RooWorkspace` with the name `Datacard_{model}.root`.

## Running the fits

When you have built the workspace, you are finally ready to run the fits and extract the results! The options for the fit are steered using the input json files:
```
python RunFits.py --inputJson inputs.json --mode {model}
```
This script uses the functionalities of [combineHarvester](https://cms-analysis.github.io/CombineHarvester/) in `combineTools`. The nominal fit is an `expected` fit (i.e. using an asimov toy dataset). An example input json file specifying the options for the `mu` model:
```
{
    "mu":{
        "pois":"r_ggH,r_VBF,r_VH,r_top",
        "fits":"profile1D:syst:all+profile1D:statonly:all",
        "points":"20:1+20:1",
        "fit_opts":"--saveSpecifiedNuis all --saveInactivePOI 1+--saveSpecifiedNuis all --saveInactivePOI 1"
    }
}
```
 * `pois`: full list of parameters of interest

 * `fits`: mapping for fit details with options deliminated using `:`. The first string specifies the type of fit e.g. `profile1D` corresponds to a 1D likelihood scan, where the other parameters of interest are profiled. Other options for this include `bestfit`, `singles`, `fixed`, `AsymptoticLimit`, `scan1D`, `profile2D`, `scan2D` and `robustHesse` (see bottom of this page for details). The second string is the user specified name of the fit. If this string contains `statonly` then the option `--freezeParameters allConstrainedNuisances` will be added to the combine command. The last string specifies the pois (comma-separated list) to run the fit for. Use `all` to run over all parameters of interest. You can define multiple fits using the `+` deliminator. In the example above there are two types of fit defined, one named `syst` and one named `statonly`.

 *  `points`: number of points in the likelihood scan, followed by the number of points per job. In this example you have 20 points and one point per job. Again, if multiple fits are defined, specify the respective `points` using the `+` deliminator. 

 * `fit_opts`: this is where you specify the combine options you want to use. For example `--setParameters`, `--setParameterRanges`, `--freezeParameters` etc. Separate options for multiple fits using the `+` deliminator. 

For tips, please refer to `example_inputs` directory for a set of example input jsons. 

There's a bunch of additional options when using the `RunFits.py` script:

 * `--ext`: running over a datacard with an extension in the name e.g. for `Datacard_LEPTONIC_mu.root` you would use `--ext _LEPTONIC`.
 * `--setPdfIndices`: set the pdfindex parameters to values specified in `pdfindex.json` when throwing the asimov toy in the expected scan. This can help to obtain closure in the expected scans: the prefit (B-only) pdf indices can differ from the postfit (S+B) pdf indices, which means you can extract a different signal strength to that put in. First run a `bestfit` adding `--saveSpecifiedIndex pdfindex_cat0,pdfindex_cat1,...,pdfindex_catN` to the `fit_opts` of the json file (see `example_inputs/inputs_bestfit.json`). Then make a `pdfindex.json` file using the post-fit values of the pdf indices.
 * `--doObserved`: run the observed fit (unblinding)
 * `--snapshotWSFile`: path to post-fit workspace created using the `--saveWorkspace` option in `fit-opts`. The initial value of the fit parameters will be set to their post-fit values. Useful when running stat-only observed scans, to fix nuisance parameters to their post-fit values (and hence obtain the same central value).
 * `--commonOpts`: combine options to add to all commands
 * `--batch`: batch system e.g. condor
 * `--queue`: batch queue e.g. workday
 * `--dryRun`: do not submit jobs, only create submission scripts

All jobs and outputs will be stored in the `runFits_{model}` directory.

## Collecting the fit results

After the fits are completed, you can collect/hadd the outputs using:
```
python CollectFits.py --inputJson inputs.json --mode {model} (--doObserved)
```

The hadded output will be of the format: `runFits_mu/profile1D_syst_r_ggH.root` for e.g. using the model `mu`, a `profile1D` fit with name `syst` for poi `r_ggH`. This contains the `limit` tree with all of the fit results plus any nuisance parameters that you have specified to save. The tree can then be used to plot the results with whatever fancy plots you can make e.g. for `profile2D` scans you can use the `../Plots/make2DPlot.py` for a smooth 2D likelihood contour.

For the 1D likelihood scans (`profile1D`) and (`scan1D`) fit types, the `CollectFits.py` script will execute `plot1DScan.py` of `combineTools` and the output is stored in `runFits_mu/Plots` directory. You can also use this script to produce plots with overlapping likelihood scans e.g.:
```
plot1DScan.py runFits_mu/profile1D_syst_r_ggH.root --y-cut 20 --y-max 20 --output r_ggH_statsyst --POI r_ggH --translate ../Plots/pois_mu.json --main-label "Expected" --main-color 1 --others runFits_mu/profile1D_statonly_r_ggH.root:"Stat only":2 --logo-sub "Preliminary"
```
Will overlay the systematic and stat-only fit results for the `r_ggH` parameter. 

## Impacts

See [combine manual](https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/part3/nonstandard/#nuisance-parameter-impacts) for details. Method for calculating the impact of nuisance parameters on the parameters of interest. Using your compiled `RooWorkspace` as input (e.g. `Datacard_mu.root`). The first step is to run an initial fit for each POI (as below), where the options in brackets are added for the calculating the expected impacts, setting the POIs to their SM values:
```
combineTool.py -M Impacts -d Datacard_mu.root -m 125 --doInitialFit --robustFit 1 (-t -1 --setParameters r_ggH=1,r_VBF=1,r_VH=1,r_top=1)
```
Then you perform a similar scan for each nuisance parameter:
```
combineTool.py -M Impacts -d Datacard_mu.root -m 125 --robustFit 1 --doFits (-t -1 --setParameters r_ggH=1,r_VBF=1,r_VH=1,r_top=1)
```
This command will run approximately 60 scans, and to speed things up the option `--parallel X` can be given to run `X` combine jobs simultaneously. When all jobs are finished you can collect the output and write to a json file and then plot the standard impacts plots using:
```
combineTool.py -M Impacts -d Datacard_mu.root -m 125 -o impacts.json
plotImpacts.py -i impacts.json -o impacts
```

Be careful: if you are running the observed impacts, the unblinded value of the POI will be displayed in the top right of the plot!


## Supported types of fit

 * `profile1D`: 1D likelihood scan where other pois are profiled
 * `scan1D`: 1D likelihood scan where other pois are fixed
 * `robuseHesse`: make correlation matrix of fit parameters like [this](http://cms-results.web.cern.ch/cms-results/public-results/preliminary-results/HIG-19-015/CMS-PAS-HIG-19-015_Figure_019.pdf). Use `Plots/makeCorrMatrix.py` to plot.
 * `bestfit`: single best-fit point. Add `--saveWorkspace` option to `fit_opts` to save the postfit workspace. This can then be loaded when using `RunFits.py` with the `--snapshotWSFile` option
 * `fixed`: extract deltaNLL for a fixed point in the parameter space specified with e.g. `--setParameters r=1 --fixedPointPOIs r=1` for SM scenario.
 * `singles`: extract +-1sigma confidence interval, assuming gaussian interval. Better to use the full likelihood scan for non-gaussian scenario.
 * `AsymptoticLimits`: use for limits e.g. rare/BSM analyses
 * `profile2D`: 2D likelihood scan, where other pois are profiled. Separate the two pois in the `fits` option options of the input json using a comma.
 * `scan2D`: 2D likelihood scan, where other pois are fixed. Separate the two pois in the `fits` option options of the input json using a comma.

## Bias studies

Scripts/instructions for bias studies are in `Checks` folder.
