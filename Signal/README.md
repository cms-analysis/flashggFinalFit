# Signal Scripts
This is where the signal model determined. Including: fitting each Tag/Process distribution in right vertex (RV) and wrong vertex (WV) scenarios, interpolation between mass points, and normalisation.

## Signal workflow

The workflow looks like this:
* Start from flashgg output root file
* Generate `dat/config.dat` using `./bin/signalFTest` (number of gaussians to fit)
* Generate `./bin/calcPhotonSystConsts` using `dat/photonCatSyst.dat` (photon systematics config file)
* Generate signal model file using `./bin/SignalFit` and the output of the above.
* Make validation plots using `./bin/makeParametricSignalModelPlots`

Thankfully this whole process can be run in one command using the signal pilot script `runSignalScripts.sh`

## Quickstart

To run a basic version of the signal workflow you can use the `runSignalScripts.sh` script. 
```
cmsenv
./runSignalScripts.sh -i <comma separated signal files> -p <process names eg: ggh,vbf,wzh,tth> -f <tag names eg: UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1,..> --ext <extension to identify this processsing run>  --intLumi <amount of lumi in fb^{-1} eg 2.69> --smears <photon energy smear categories> --scales <photon energy scale categories> --batch <IC or LSF (Cern)... or blank if you want to run everything locally (slow) >
```

or a specific example from the `HggAnalysis_Moriond2016_example` referenced in the `README.md` of the main `flashggFinalFits` directory:
```
./runSignalScripts.sh -i root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_GluGluHToGG_M120_13TeV_amcatnloFXFX_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_GluGluHToGG_M130_13TeV_amcatnloFXFX_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_VBFHToGG_M120_13TeV_amcatnlo_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_VBFHToGG_M130_13TeV_amcatnlo_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_VBFHToGG_M125_13TeV_amcatnlo_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_ZHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_ZHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_ZHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_WHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_WHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_WHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_ttHJetToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_ttHJetToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root -p ggh,vbf,tth,wh,zh -f UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1,TTHHadronicTag,TTHLeptonicTag --ext HggAnalysis_Moriond2016_example --intLumi 2.69  --batch LSF
```

Running this command will first run the signal f-Test, and then will prompt you to use the output of this f-Test to manually fill out the required configuration file which determines how many gaussians to use for each tag/process/RightVertex-WrongVertex-Scenario. Once you have filled in the file, simply re-run the same command to proceed with the signal model building.

This example takes all processes and tags into account, and therefore will be lengthy to run, so to practice you may consider restricting to only ggh and vbf for example.

The available options can be seen by doing `runSignalScripts.sh -h`. They are all self-explanatory, aside from `--intLumi`: This can be used to over-ride the built in value of IntLumi and amend the MC event weights as needed.

Note: the `signalFTest` and `SignalFit` steps can be very time consuming (>1h). To speed up, this process can be submitted to the batch by specifying a queue to use (eg `--batch LSF` or `--batch IC`). If this is the case, the individual Tag/Process `signalFTest` or `SignaFit` jobs are submitted to a default queue ( `hepshort.q` or `1nh` depending on which batch system you use), and then the status is monitored every 10s. However, if no batch system is specified, the default is to run over each Tag/Process one after another.

## Script-byscript guide
### Generating the dat/config.dat file.

One can use the `./bin/signalFTest` script to regenerate this. 

The signalFtest has as its purpose to determine how many gaussians should be used to fit the mgg distribution for each Tag/Process, both in the cases that the "right vertex" (RV) and "wrong vertex" (WV) have been selected (this uses a `dZ<1` cut).

The output is the `dat/newConfig.dat` file which lists this information. At present, the script always returns a fairly arbitrary number of gaussians, with the idea being that the user can change the values as they like after inspecting the output plots.

By default, if the stats in a particular proc/tag/RV-WV are too low, a "replacement" pdf is used: this means that we use the dataset from a different category to do the fitting and then normalise it using the original dataset. You can trigger this yourself by specifying "-1" instead of giving a number of gaussians in the config file. Furthermore, instead of using the 'default' replacement dataset for the RV, you can specify it in the config file as an extra value on the line. For the WV, since the shape depends only on detector effects, if is expected to be the same for all categories, the "UntaggedTag_2" shape is always used if a replacement is needed.

```
#proc cat nGausRV nGausWV #optional repalcement proc for RV # optional replacement tag for RV
ggh TTHHadronicTag -1 -1 tth TTHHadronicTag
```


Working FLASHgg example:

```
./bin/signalFTest -i root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_GluGluHToGG_M120_13TeV_amcatnloFXFX_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_GluGluHToGG_M130_13TeV_amcatnloFXFX_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_VBFHToGG_M120_13TeV_amcatnlo_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_VBFHToGG_M130_13TeV_amcatnlo_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_VBFHToGG_M125_13TeV_amcatnlo_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_ZHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_ZHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_ZHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_WHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_WHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_WHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_ttHJetToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_ttHJetToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root  -p ggh,vbf,wh,zh,tth -f UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1,TTHHadronicTag,TTHLeptonicTag -o $CMSSW_BASE/src/flashggFinalFit/Signal/outdir_HggAnalysis_Moriond2016_example 
```

Example output can be found at:

```
https://twiki.cern.ch/twiki/bin/view/CMS/FLASHggFramework#Signal #(Under signalFTest)
```

The option ` --considerOnly <tagname> ` can be used in conjunction with only specifying one process name in order to do the fTest only for a single tag/process combination. This is used for example in `python/submitSignaFTest.py`, which submits each tag/proc to the batch separately. 

The python script  `python/submitSignaFTest.py` is used like this:
```
./python/submitSignaFTest.py --procs <processes separated by comma> --flashggCats <tag names separated by comma>  --outDir < output dir? --i <input files separated by comma>  --batch <LSF (ie CERN) or IC> -q <your favourite queue>
```
ie
```
./python/submitSignaFTest.py --procs ggh,vbf,tth,wh,zh --flashggCats UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1,TTHHadronicTag,TTHLeptonicTag --outDir outdir_HggAnalysis_Moriond2016_example --i root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_GluGluHToGG_M120_13TeV_amcatnloFXFX_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_GluGluHToGG_M130_13TeV_amcatnloFXFX_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_VBFHToGG_M120_13TeV_amcatnlo_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_VBFHToGG_M130_13TeV_amcatnlo_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_VBFHToGG_M125_13TeV_amcatnlo_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_ZHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_ZHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_ZHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_WHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_WHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_WHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_ttHJetToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_ttHJetToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root --batch LSF -q 1nh
```

* Note that the script will loop through the input files until it finds the datasets it needs to do the fits. You should have one signal dataset per tag\*process and per mass point (in general 120, 125 and 130). The datasets can be all in the same file or split into any number of smaller files: the `WSFileWrapper` (Workspace file wrapper) class will go through each subfile and find the relevant dataset.

* Note: the `signalFTest` step can be very time consuming (>1h). To speed up, this process can be submitted to the batch by specifying a queue to use (eg `--batch LSF` or `--batch IC`). If this is the case, the individual Tag/Process signalFTest jobs are submitted to a default queue ( `hepshort.q` or `1nh` depending on which batch system you use). The status of jobs is monitored every 10s. However, if no batch system is specified, the default is to run over each Tag/Process one after another as in the example above.

### Generating the dat/photonCatSyst.dat file

The script `./bin/calcPhotonSystConsts` generates the photon category systematics config file, taking as input the flashgg signal workspaces.


FLASHgg working example:

```
./bin/calcPhotonSystConsts -i <input files comma separated> -o <output file> -p <comma separated process names> -s <photon energy scale categories> -r <photon energy scale categories>  -D <output dir for plots> -f <comma separated tag names>
```
e.g
```
./bin/calcPhotonSystConsts -i root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_GluGluHToGG_M120_13TeV_amcatnloFXFX_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_GluGluHToGG_M130_13TeV_amcatnloFXFX_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_VBFHToGG_M120_13TeV_amcatnlo_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_VBFHToGG_M130_13TeV_amcatnlo_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_VBFHToGG_M125_13TeV_amcatnlo_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_ZHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_ZHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_ZHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_WHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_WHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_WHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_ttHJetToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_ttHJetToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root -o dat/photonCatSyst_HggAnalysis_Moriond2016_example.dat -p ggh,vbf,tth,wh,zh -s HighR9EB,HighR9EE,LowR9EB,LowR9EE -r HighR9EBPhi,HighR9EBRho,HighR9EEPhi,HighR9EERho,LowR9EBPhi,LowR9EBRho,LowR9EEPhi,LowR9EERho -D outdir_HggAnalysis_Moriond2016_example -f UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1,TTHHadronicTag,TTHLeptonicTag
```

Example output can be found at:

```
https://twiki.cern.ch/twiki/bin/view/CMS/FLASHggFramework#Signal #(Under Systematics)
```
* Note that the script will loop through the input files until it finds the workspaces it needs to do the fits. You should have one signal workspace per tag\*process and per mass point (in general 120, 125 and 130). The workspaces can be all in the same file or split into any number of smaller files: the `WSFileWrapper` (Workspace file wrapper) class will go through each subfile and find the relevant workspace.


### Signal Fit
The main script is SignalFit. This takes as input two dat files and a root file.

* `-d datfile`, which specifies information about how many gaussians to fit in each category under right vertex and wring vertex hypotheses. an example file which can be found at `dat/newConfig_HggAnalysis_Moriond16_example.dat`. This file can also be generated using the script  `./bin/SignaFTest`.
* `-s systematics datfile`, which tells how to propagate single photon systematics to diphoton categories. Default is example file at `dat/photonCatSyst.dat`. These configs can be generated using `./bin/calcPhotonSystConsts`.

`./bin/SignalFit` should run locally in < 1hr or on the batch much faster if split into jobs for each tag/process. 

The `--changeIntLumi` can be used to over-ride the existing value of IntLumi in the workspace and scale the event weights appropriately. it should be specified in fb^{-1}.

FLASHgg working example:

```
./bin/SignalFit -i <comma separated signal files> -d <fTest config>  --mhLow=120 --mhHigh=130 -s <calcPhoSystConsts config> --procs <comma separated processes> -o <base name of output signal workspace: blah.root> -p <output folder for plots>  -f <comma separated tag names> --changeIntLumi <intlumi specified in fb^{-a} if different from that specified in workspace> --binnedFit 1 --nBins 320 
```
eg 
```
 $CMSSW_BASE/src/flashggFinalFit/Signal/bin/SignalFit --verbose 0 -i root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_GluGluHToGG_M120_13TeV_amcatnloFXFX_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_GluGluHToGG_M130_13TeV_amcatnloFXFX_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_VBFHToGG_M120_13TeV_amcatnlo_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_VBFHToGG_M130_13TeV_amcatnlo_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_VBFHToGG_M125_13TeV_amcatnlo_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_ZHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_ZHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_ZHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_WHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_WHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_WHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_ttHJetToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_ttHJetToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces//output_ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root -d $CMSSW_BASE/src/flashggFinalFit/Signal/dat/newConfig_HggAnalysis_Moriond2016_example.dat  --mhLow=120 --mhHigh=130 -s $CMSSW_BASE/src/flashggFinalFit/Signal/dat/photonCatSyst_HggAnalysis_Moriond2016_example.dat --procs ggh,vbf,tth,wh,zh -o  $CMSSW_BASE/src/flashggFinalFit/Signal/outdir_HggAnalysis_Moriond2016_example/CMS-HGG_sigfit_HggAnalysis_Moriond2016_example_ggh_UntaggedTag_0.root -p $CMSSW_BASE/src/flashggFinalFit/Signal/outdir_HggAnalysis_Moriond2016_example/sigfit -f UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1,TTHHadronicTag,TTHLeptonicTag --changeIntLumi 2.69 --binnedFit 1 --nBins 320 --split ggh,UntaggedTag_0 
```


Example output can be found here:

```
https://twiki.cern.ch/twiki/bin/view/CMS/FLASHggFramework#Signal #(Under SignalFit)
```

Notes:

* The final signal model `SignalFit.cpp` combination can take a long time to run. One can make the signal process for each tag/process individually by adding the option `--split <process>,<tagname>` to the command.
* This is used to parallelise the task and submit it to the batch using this syntax:

```
./python/submitSignalFit.py -i $FILES -d dat/newConfigxxx.dat  --mhLow=120 --mhHigh=130 -s dat/photonCatSystxxx.dat --procs $PROCS -o $OUTDIR /CMS-HGG_sigfit_$EXT.root -p $OUTDIR/sigfit -f $CATS --changeIntLumi $INTLUMI --batch $BATCH -q $DEFAULTQUEUE
```
* Note that the script will loop through the input files until it finds the workspaces it needs to do the fits. You should have one signal workspace per tag\*process and per mass point (in general 120, 125 and 130). The workspaces can be all in the same file or split into any number of smaller files: the `WSFileWrapper` (Workspace file wrapper) class will go through each subfile and find the relevant workspace.

### Making the Signal Plots

To generate validation plots, one can use the `./bin/makeParametricSignalModelPlots` script, which is used as follows.
```
./bin/makeParametricSignalModelPlots -i outdir_<ext>/CMS-HGG_sigfit_<ext>.root  -o outdir_<ext> -p ggh,vbf,wh,zh,tth -f UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1
```

Example output can be found here:

```
https://twiki.cern.ch/twiki/bin/view/CMS/FLASHggFramework#Signal #(Under Signal Validation Plots)
```
