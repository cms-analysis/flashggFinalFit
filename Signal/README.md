# Signal Scripts
This is where the signal model determined. Including interpolation between mass points. 
## Signal workflow

The workflow looks like this:
* Starting from flashgg output root file
* Generate `dat/config.dat` using `./bin/signalFTest` (number of gaussians to fit)
* Generate `./bin/calcPhotonSystConsts` using `dat/photonCatSyst.dat` (photon systematics config file)
* Generate signal model file using `./bin/SignalFit` and the output of teh above.
* Make validation plots using `./bin/makeParametricSignalModelPlots`

Thankfully this whole process can be run in one command using the signal pilot script `runSignalScripts.sh`

## Quickstart

To runa  basic version of the signal workflow you can use the `runSignalScripts.sh` script. 
```
cmsenv
FILE=/afs/cern.ch/user/l/lcorpe/work/public/test_jobs_v8/everythingWithLumi.root
/runSignalScripts.sh -i $FILE -p ggh -f UntaggedTag_0 --ext test --intLumi 1
```
The available options can be seen by doing `runSignalScripts.sh -h`. They are all self-explanatory, aside from `--intLumi`: This can be used to over-ride the built in value of IntLumi and amend the MC event weights as needed.

## Script-byscript guide
### Generating the dat/config.dat file.

One can use the `./bin/signalFTest` script to regenerate this. Example output is provided here.

The signalFtest has as its purpose to detrmine how many gaussians should be used to fit the mgg distribution for each tag,process, both in the cases that the "right vertex" and "wrong vertex" have been selected (this uses a `dZ<1` cut).
The output is the `dat/newConfig.dat` file which lists this information. At present, the script always returns 3 gaussians for the right vertex and 2 gaussians for the wrong vertex, with the idea beaing that the user can change the values as they like after inspecting the output plots. Efforts are underway to automatise this further usign a chi2/ndof method (or similar).

Working FLASHgg example:
```
file=/afs/cern.ch/user/l/lcorpe/work/public/test_jobs_v8/everythingWithLumi.root
./bin/signalFTest -i $file -d dat/newConfig.dat -p ggh -f UntaggedTag_0 -o test
```
Example output can be found at:
```
https://lcorpe.web.cern.ch/lcorpe/outdir_intlumitest1fb/sigfTest/
```
### Generating the dat/photonCatSyst.dat file

The script `./bin/calcPhotonSystConsts` generates the photon category systematics config file, taking as input the flashgg signal workspaces.

NB: The systematics functionality is currently only supported for Photon Energy Scale and Photon Energy Smear for flashgg. The code will be updated to allow other types (eg gloval scale, global smearing, material effects) in due course.

FLASHgg working example:
```
file=/afs/cern.ch/user/l/lcorpe/work/public/test_jobs_v8/everythingWithLumi.root
/bin/calcPhotonSystConsts -i $file -o dat/photonCatSyst.dat -p ggh -f UntaggedTag_0 -s HighR9EE,LowR9EE,HighR9EB,LowR9EB -r HighR9EE,LowR9EE,HighR9EBRho,LowR9EBRho,HighR9EBPhi,LowR9EBPhi -D plotsDir 
```

Example output can be found at:
```
https://lcorpe.web.cern.ch/lcorpe/outdir_intlumitest1fb/systematics/
```

### Signal Fit
The main script is SignalFit. This takes as input two dat files and a root file.

* `-d datfile`, which specifies information about how many gaussians to fit in each category under right vertex and wring vertex hypotheses. an example file which can be found at `dat/newConfig.dat`. This file can also be generated using the script  `./bin/SignaFTest`.
* `-s systematics datfile`, which tells how to propagate single photon systematics to diphoton categories. Default is example file at `dat/photonCatSyst.dat`. These configs can be generated using `./bin/calcPhotonSystConsts`.

`./bin/SignalFit` should run locally in < 1hr. 

The `--changeIntLumi` can be used to over-ride the existing value of IntLumi in the workspace and scale the event weights appropriately. it shoudl be specified in fb^{-1}.

FLASHgg working example:
```
file=/afs/cern.ch/user/l/lcorpe/work/public/test_jobs_v8/everythingWithLumi.root
./bin/SignalFit -i $file -d dat/newConfig.dat  --mhLow=120 --mhHigh=130 -s dat/photonCatSyst.dat --procs ggh -f UntaggedTag_0 -o CMS-HGG_sigfit.root -p sigfit  --changeIntLumi 1
```
Example output cna be found here:
```
https://lcorpe.web.cern.ch/lcorpe/outdir_intlumitest1fb/sigfit/
```

### Making the Signal Plots

To generate validation plots, one can use the `./bin/makeParametricSignalModelPlots` script, which is used as follows.
```
./bin/makeParametricSignalModelPlots -i CMS-HGG_sigfit.root  -o outdir_intlumitest1fb -p ggh -f UntaggedTag_0
```

Example output can be found here:
```
https://lcorpe.web.cern.ch/lcorpe/outdir_intlumitest1fb/sigplots/
```
