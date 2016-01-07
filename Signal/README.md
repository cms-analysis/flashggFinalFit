# Signal Scripts
This is where the signal model determined. Including: fitting each Tag/Process distribution in right vertex (RV) and wrong vertex (WV) scenarios, interpolation between mass points, and normalisation.

## Signal workflow

The workflow looks like this:
* Start from flashgg output root file
* Generate `dat/config.dat` using `./bin/signalFTest` (number of gaussians to fit)
* Generate `./bin/calcPhotonSystConsts` using `dat/photonCatSyst.dat` (photon systematics config file)
* Generate signal model file using `./bin/SignalFit` and the output of teh above.
* Make validation plots using `./bin/makeParametricSignalModelPlots`

Thankfully this whole process can be run in one command using the signal pilot script `runSignalScripts.sh`

## Quickstart

To run a basic version of the signal workflow you can use the `runSignalScripts.sh` script. This example is taken from the "Hgg Dry Run 2015" exercise:
```
cmsenv
file=/afs/cern.ch/user/l/lcorpe/public/HggDryRunDec15/flashgg_source_files/allsig.root
./runSignalScripts.sh -i $file -p ggh,vbf,wzh,tth -f UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1 --ext hgg_dry_run_2015 --intLumi 2.46
```

This example takes all processes and tags into account, and therefore will be lengthy to run, so to practice you may consider restricting to only ggh and vbf for example.

The available options can be seen by doing `runSignalScripts.sh -h`. They are all self-explanatory, aside from `--intLumi`: This can be used to over-ride the built in value of IntLumi and amend the MC event weights as needed.

Note: the `signalFTest` step can be very time consuming (>1h). To speed up, this process can be submitted to the batch by specifying a queue to use (eg `--batch LSF` or `--batch IC`). If this is the case, the individual Tag/Process signalFTest jobs are submitted to a default queue ( `hepshort.q` or `1nh` depending on which batch system you use) and teh final results are combined into one final dat file, and then the status is monitored every 10s. However, if no batch system is specified, the default is to run over each Tag/Process one after another.

## Script-byscript guide
### Generating the dat/config.dat file.

One can use the `./bin/signalFTest` script to regenerate this. Example output is provided here.

The signalFtest has as its purpose to detrmine how many gaussians should be used to fit the mgg distribution for each Tag/Process, both in the cases that the "right vertex" (RV) and "wrong vertex" (WV) have been selected (this uses a `dZ<1` cut).

The output is the `dat/newConfig.dat` file which lists this information. At present, the script always returns a fairly arbitrary number of gaussians, with the idea beaing that the user can change the values as they like after inspecting the output plots. Efforts are underway to automatise this further usign a chi2/ndof method (or similar).

Working FLASHgg example:

```
file=/afs/cern.ch/user/l/lcorpe/public/HggDryRunDec15/flashgg_source_files/allsig.root
./bin/signalFTest -i $file -d dat/newConfig_hgg_dry_run_2015.dat -p ggh,vbf,wzh,tth -f UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1 -o outdir_hgg_dry_run_2015
```
Example output can be found at:

```
https://twiki.cern.ch/twiki/bin/view/CMS/FLASHggFramework#Signal #(Under signalFTest)
```

### Generating the dat/photonCatSyst.dat file

The script `./bin/calcPhotonSystConsts` generates the photon category systematics config file, taking as input the flashgg signal workspaces.

NB: The systematics functionality is currently only supported for Photon Energy Scale and Photon Energy Smear for flashgg. The code will be updated to allow other types (eg gloval scale, global smearing, material effects) in due course.

FLASHgg working example:

```
file=/afs/cern.ch/user/l/lcorpe/public/HggDryRunDec15/flashgg_source_files/allsig.root
./bin/calcPhotonSystConsts -i /afs/cern.ch/user/l/lcorpe/public/HggDryRunDec15/flashgg_source_files/allsig.root -o dat/photonCatSyst_hgg_dry_run_2015.dat -p ggh,vbf,wzh,tth -s HighR9EE,LowR9EE,HighR9EB,LowR9EB -r HighR9EE,LowR9EE,HighR9EB,LowR9EB -D outdir_hgg_dry_run_2015 -f UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1
```

Example output can be found at:

```
https://twiki.cern.ch/twiki/bin/view/CMS/FLASHggFramework#Signal #(Under Systematics)
```

* Note: the `signalFTest` step can be very time consuming (>1h). To speed up, this process can be submitted to the batch by specifying a queue to use (eg `--batch LSF` or `--batch IC`). If this is the case, the individual Tag/Process signalFTest jobs are submitted to a default queue ( `hepshort.q` or `1nh` depending on which batch system you use) and the final results are combined into one final dat file. The status of jobs is monitored every 10s. However, if no batch system is specified, the default is to run over each Tag/Process one after another as in the example above.
* If submitting to the batch, be warned that the CERN/LSF `1nh` queue can be clogged up. If you have access to IC queues, it maybe be worth using those instead!
* It is recommended (for now at least) to pick the nGaussians by hand rather than blindly trust the output of `signalFTest`. In many cases, picking too many gaussians for low stats categories can cause huge headaches later on in the chain (eg seg faults, stupid fits...). So if there is any category where the stats are very low or indeed any negative weights are visible, it is recommended to pick only 1 gaussian. In particular, the problems arise because `combine` and `rooFit` are not great at dealing with situations where any PDF in the signal model is 0 or negative. Picking just one gaussian avoids this issue.

### Signal Fit
The main script is SignalFit. This takes as input two dat files and a root file.

* `-d datfile`, which specifies information about how many gaussians to fit in each category under right vertex and wring vertex hypotheses. an example file which can be found at `dat/newConfig.dat`. This file can also be generated using the script  `./bin/SignaFTest`.
* `-s systematics datfile`, which tells how to propagate single photon systematics to diphoton categories. Default is example file at `dat/photonCatSyst.dat`. These configs can be generated using `./bin/calcPhotonSystConsts`.

`./bin/SignalFit` should run locally in < 1hr. 

The `--changeIntLumi` can be used to over-ride the existing value of IntLumi in the workspace and scale the event weights appropriately. it shoudl be specified in fb^{-1}.

FLASHgg working example:

```
file=/afs/cern.ch/user/l/lcorpe/public/HggDryRunDec15/flashgg_source_files/allsig.root
./bin/SignalFit -i $file -d dat/newConfig_hgg_dry_run_2015.dat  --mhLow=120 --mhHigh=130 -s dat/photonCatSyst_hgg_dry_run_2015.dat --procs ggh,vbf,wzh,tth -o outdir_hgg_dry_run_2015/CMS-HGG_sigfit_hgg_dry_run_2015.root -p outdir_hgg_dry_run_2015/sigfit -f UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1 --changeIntLumi 2.46
```

Example output can be found here:

```
https://twiki.cern.ch/twiki/bin/view/CMS/FLASHggFramework#Signal #(Under SignalFit)
```

Notes:

* The final signal model `SignalFit.cpp` combination can take a long time to run, and I suspect there is a memory leak. The machines on the Imperial College batch system cannot handle the final model construction: the script runs all the way to the end but crashes before the final root file can be saved. Therefore, it is recommended to work at CERN lxplus machines for this step.
* It would be great to paralellise this step somehow (eg like the SignalFTest step). The infrasctructure to split the individual Tags/Processes into jobs is in place, but combining the output into a single signal model is not trivial...

### Making the Signal Plots

To generate validation plots, one can use the `./bin/makeParametricSignalModelPlots` script, which is used as follows.
```
./bin/makeParametricSignalModelPlots -i outdir_hgg_dry_run_2015/CMS-HGG_sigfit_hgg_dry_run_2015.root  -o outdir_hgg_dry_run_2015 -p ggh,vbf,wzh,tth -f UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1
```

Example output can be found here:

```
https://twiki.cern.ch/twiki/bin/view/CMS/FLASHggFramework#Signal #(Under Signal Validation Plots)
```
## Outstanding Issues

A Number if issues remain which should be addressed in time for Moriond 2016.

* Automated selection of nGaussians from the signalFTest ?
* Low stats categories: need to determine best way to handle Tags/Processes/Vertex Scenarios where there are very low stats, how to avoid stupid fits and in particular, negative or iedntiaclly zero PDFs which screw up `rooFit` and `combine`? Current workaround is to use 1 gaussian only, but another (better?) option would be to use a ggh RV or WV template (ie the same signal model as this high stats category). This is especially true of WV scenarios, where we expect the shape to be completely dominated by the fact we got the vertex wrong, and therefore the shaps should be the same.
* It would be great to paralellise the SignalFit step somehow (eg like the SignalFTest step). The infrasctructure to split the individual Tags/Processes into jobs is in place, but combining the output into a single signal model is not trivial...

## Notes on running

* Note: the `signalFTest` step can be very time consuming (>1h). To speed up, this process can be submitted to the batch by specifying a queue to use (eg `--batch LSF` or `--batch IC`). If this is the case, the individual Tag/Process signalFTest jobs are submitted to a default queue ( `hepshort.q` or `1nh` depending on which batch system you use) and teh final results are combined into one final dat file, and then the status is monitored every 10s. However, if no batch system is specified, the default is to run over each Tag/Process one after another.
* If submitting to the batch, be warned that the CERN/LSF `1nh` queue can be clogged up. If you have access to IC queues, it maybe be worth using those instead!
* It is recommended (for now at least) to pick the nGaussians by hand rather than blindly trust the output of `signalFTest`. In many cases, picking too many gaussians for low stats categories can cause huge headaches later on in the chain (eg seg faults, stupid fits...). So if there is any category where the stats are very low indeed any negative eights are visible, it is recommended to pick only 1 gaussian. In particular, the problems arise because `combine` and `rooFit` are not great at dealing with situations where any PDF in the signal model is 0 or negative. Picking just one gaussian avoids this issue.
* The final signal model `SignalFit.cpp` combination takes a long time to run, and I suspect there is a memory leak. The machines on the Imperial College batch system cannot handle the final model construction: the script runs all the way to the end but crashes before the final root file can be saved. Therefore, it is recommended to work at CERN lxplus machines for this step.
