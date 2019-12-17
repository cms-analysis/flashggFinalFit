# Signal Scripts
This is where the signal model built from the MC workspaces. Including: fitting each Tag/Process distribution in right vertex (RV) and wrong vertex (WV) scenarios, interpolation between mass points, and normalisation. The signal modelling uses a Simultaneous Signal Fit (SSF - fitting all mass points simultaneously, rather than using linear interpolation). Also, instead of using a sum of Gaussians for the model it is possible to use a Gaussian core plus DCBs (`--useDCB 1`).

## Signal workflow

The workflow looks like this:
* Start from flashgg output root file
* Generate `dat/config.dat` using `./bin/signalFTest` (number of gaussians to fit) (or use a template from a previous example and modify the nGaussians until they fit nicely).
* Generate `./bin/calcPhotonSystConsts` using `dat/photonCatSyst.dat` (photon systematics config file)
* Generate signal model file using `./bin/SignalFit` and the output of the above.
* Make validation plots using `./bin/makeParametricSignalModelPlots`

## Submission script

To run the signal workflow you can use the `RunSignalScripts.py` script. 

The options for the signal fit can be specified in a config file e.g. `example_config_stage1_1.py` or directly in the command line. 
```
cmsenv
python RunSignalScript.py --inputConfig example_config_stage1_1.py
```

The config file will look as follows:
```
signalScriptCfg = {
  
  # Setup
  'inputWSDir':'/vols/cms/jl2117/hgg/ws/test_stage1_1_2018', # directory if input workspaces
  #Procs will be inferred automatically from filenames
  'cats':'RECO_0J_PTH_GT10_Tag0,RECO_0J_PTH_GT10_Tag1', #analysis categories
  'ext':'stage1_1_2018', # extension to be added to output directory
  'analysis':'stage1_1', # To specify which replacement dataset mapping (defined in ./python/replacementMap.py)
  'year':'2018', # selects which integrated luminosity is used
  'beamspot':'3.4',
  'numberOfBins':'320',
  'massPoints':'120,125,130',

  # Use DCB in fit
  'useDCB':0,

  #Photon shape systematics  
  'scales':'HighR9EB,HighR9EE,LowR9EB,LowR9EE,Gain1EB,Gain6EB',
  'scalesCorr':'MaterialCentralBarrel,MaterialOuterBarrel,MaterialForward,FNUFEE,FNUFEB,ShowerShapeHighR9EE,ShowerShapeHighR9EB,ShowerShapeLowR9EE,ShowerShapeLowR9EB',
  'scalesGlobal':'NonLinearity:UntaggedTag_0:2,Geant4',
  'smears':'HighR9EBPhi,HighR9EBRho,HighR9EEPhi,HighR9EERho,LowR9EBPhi,LowR9EBRho,LowR9EEPhi,LowR9EERho',

  # Job submission options
  'batch':'HTCONDOR',
  'queue':'microcentury',

  # Mode allows script to carry out single function
  'mode':'std', # Options: [std,phoSystOnly,sigFitOnly,packageOnly,sigPlotsOnly]
}
```

Running with `'mode':"std"` will first run the signal f-Test, and then will prompt you to use the output of this f-Test to manually fill out the required configuration file which determines how many gaussians to use for each tag/process/RightVertex-WrongVertex-Scenario. Once you have filled in the file, simply re-run the same command to proceed with the signal model building. In practise this method of determining the number of Gaussians to use is not particularly efficient. 

Another suggestion is to start from the exampke nGaussians file `dat/newConfig_HggAnalysis_ICHEP2016_example.dat` and modify your nGaussians until you are happy with them. If the relevant config file already exists, the code will skip the f-Test by default.

This example takes all processes and tags into account, and therefore will be lengthy to run, so to practice you may consider restricting to only ggh and vbf for example.

Note: the `signalFTest` and `SignalFit` steps can be very time consuming (>1h). To speed up, this process can be submitted to the batch by specifying a queue to use (eg `--batch HTCONDOR` or `--batch IC`). If this is the case, the individual Tag/Process `signalFTest` or `SignaFit` jobs are submitted to a default queue ( `hepshort.q` or `1nh` depending on which batch system you use), and then the status is monitored every 10s. However, if no batch system is specified, the default is to run over each Tag/Process one after another.

The other modes split up the individual elements of the signal modelling:
* Calculating photon systematics: `phoSystOnly`
* Signal fit: `sigFitOnly`
* Packaging the output: `packageOnly`
* Making the signal plots: `sigPlotsOnly`

## NEW: Replacement dataset map
By default, if the stats in a particular proc/tag/RV-WV are too low, a "replacement" pdf is used: this means that we use the dataset from a different category to do the fitting and then normalise it using the original dataset. 

Previously the choice of replacement dataset was hardcoded in the `./test/SignalFit.cpp` script. Now, you can add an analysis specific mapping to the `./python/replacementMap.py` python module, following the structure given. 

Also, you can trigger the replacement fit by specifying "-1" instead of giving a number of gaussians in the config file. Furthermore, instead of using the 'default' replacement dataset for the RV, you can specify it in the config file as an extra value on the line. For the WV, since the shape depends only on detector effects, if is expected to be the same for all categories. The default one-category WV mapping is also specified in `./python/replacementMap.py`.

### Weighted Signal Plot

In recent analyses we have made a sum of all signal models weighted by S/B. This can be made after you've run the full workflow using the script `plotweightedsigEd.cpp`, which lives in the Background directory. Step-by-step instructions, starting from `Plots/FinalResults/`:
```
text2workspace.py CMS-HGG_mva_13TeV_datacard.txt -m 125
combine CMS-HGG_mva_13TeV_datacard.root -M MultiDimFit -n _SigModel -m 125.0 --saveWorkspace
../../Background/bin/plotweightedsigEd -i higgsCombine_SigModel.MultiDimFit.mH125.root --name myWeightedSignalPlot -v1 --label m_{H}=125GeV
```
