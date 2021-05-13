# Converting ROOT trees to workspaces

This package offers a brand new functionality of Final Fits which enables you to convert flat ROOT trees to Final Fits compatible workspaces. This means (at least for quick sensitivity studies) you can skip the lengthy process of making the flashgg workspaces.

The input options for converting trees to workspaces are steered by a config file:
```
trees2wsCfg = {

  # Name of RooDirectory storing input tree
  'inputTreeDir':'tagsDumper/trees',

  # Variables to be added to dataframe: use wildcard * for common strings
  'mainVars':["CMS_hgg_mass","weight","dZ","*sigma"], # Vars added to nominal MC RooDataSets
  'dataVars':["CMS_hgg_mass","weight"], # Vars to be added nominal data RooDataSets
  'stxsVar':'', # Var for STXS splitting: if using the option -doSTXSSplitting
  'notagVars':["weight"], # Vars to add to NOTAG RooDataset: if using option --doNOTAG
  'systematicsVars':["CMS_hgg_mass","weight"], # Variables to add to sytematic RooDataHists
  'theoryWeightContainers':{'alphaSWeights':2,'scaleWeights':9,'pdfWeights':60}, # Theory weights to add to nominal + NOTAG RooDatasets, value corresponds to number of weights (0-N).

  # List of systematics: use string YEAR for year-dependent systematics
  'systematics':['FNUFEB', 'FNUFEE','JECAbsoluteYEAR'],

  # Analysis categories: python list of cats or use 'auto' to extract from input tree
  'cats':'auto'

}
```
It is important that the input trees have the following name structure:

  * For MC: `{inputTreeDir}/{production_mode}_{mass}_{sqrts}_{category}`. For example, for ggH production at MH=125GeV, sqrts=13TeV falling in the `RECO_0J_PTH_0_10_Tag0` category the tree in the input ROOT file would be: `tagsDumper/trees/ggh_125_13TeV_RECO_0J_PTH_0_10_Tag0`.

  * For data: `{inputTreeDir}/Data_{sqrts}_{category}`. For example, for data events at sqrts=13TeV falling in the `RECO_0J_PTH_0_10_Tag0` category the tree in the input ROOT file would be: `tagsDumper/trees/Data_13TeV_RECO_0J_PTH_0_10_Tag0`.

The variables then correspond to tree branches that will be added to the output `RooDataSets` and `RooDataHists`. The `mainVars` are included in the nominal MC `RooDataSet`'s. As a bare minimum for the signal fitting to work you will need the mass variable (e.g. `CMS_hgg_mass`), the event `weight` and `dZ`. In addition you can add `*sigma` to include all the systematics which are stored as event weight factors. Of course it goes without saying but each variable that you want to add must be defined as a separate branch in the input ROOT tree.

The `dataVars` are the variables which enter the data `RooDataSet`'s. The only thing you need here is the mass variable (e.g. `CMS_hgg_mass`) and the event `weight` (=1). The `systematics` list defines the systematic variations to be saved as `RooDataHists`. They each require separate trees with naming format e.g. `tagsDumper/trees/ggh_125_13TeV_RECO_0J_PTH_0_10_Tag0_{syst}Up01sigma` and `tagsDumper/trees/ggh_125_13TeV_RECO_0J_PTH_0_10_Tag0_{syst}Down01sigma` for the up and down variations respectively.

For variables stored as arrays in the input trees e.g. `pdfWeights` then you can use the `theoryWeightContainers` input, which requires the name of the array and the number of entries per event.

## Running the tool

For MC e.g.:

```
python trees2ws.py --inputConfig config_test.py --inputTreeFile output_2016_GG2H.root --inputMass 125 --productionMode ggh --year 2016 (--doSystematics)
```
The output is a `RooWorkspace` containing the `RooDataSets` and `RooDataHists` derived from the input tree. These are stored in a ROOT file in the `ws_{process}` directory which is produced in the same directory as the input tree file. There are a number of additional options:

 * `--doNOTAG`: include the `NOTAG` dataset (requires input tree of the form `tagsDumper/trees/ggh_125_13TeV_NOTAG`). The variables added are those specified in the `notagVars` list in the input config file.
 * `--doNNLOPS`: add NNLOPS weight into nominal `RooDataSet`. Requires `NNLOPSWeight` as branch in tree.
 * `--doSTXSSplitting`: split the input tree into separate workspace files for each STXS bin (defined with the `stxsVar` input). Used to generate separate procs for each STXS bin to then be processed separately in the signal modelling and datacard generation steps. Something similar could be done for differential analyses.

For data e.g.:
```
python trees2ws_data.py --inputConfig config_test.py --inputTreeFile output_2016_data.root
```
The output is a `RooWorkspace` with a `RooDataSet` for each category, containing the `dataVars`. You only require the mass variable for the nominal background modelling.


## Parallelization

The `RunWSScripts.py` can be used to submit many `trees2ws` jobs for a large number of input tree files. 
```
python RunWSScripts.py --inputDir /{path-to-input-trees} --inputConfig config_test.py --year 2016 --ext test_2016 --mode trees2ws --batch condor --queue longlunch
```
This will submit a separate job per input tree file in the specified path. Use the option `--printOnly` to write the submission scripts without submitting. For the additional commands specific to the `trees2ws.py` script then use the `--modeOpts` option e.g. `--modeOpts "--doNOTAG --doSTXSSplitting`.

This script also supports running over multiple data input tree files. Simply change the `--inputDir` to the path to the input data trees and use `--mode trees2ws_data`.

## Hadding the output

If you have multiple output workspaces per signal process then you can hadd them together to get a single workspace per signal process. This is again steered with `RunWSScripts.py`. For this you will need to have/setup a working (and compiled) flashgg area.
```
# For MC
python RunWSScripts.py --inputDir /{path-to-input-trees} --year 2016 --ext test_2016 --mode haddMC --batch condor --queue longlunch --flashggPath /{path-to-flashgg-area} (--printOnly)

# For data
python RunWSScripts.py --inputDir /{path-to-input-data-trees} --year 2016 --ext test_2016 --mode haddData --batch condor --queue longlunch --flashggPath /{path-to-flashgg-area} (--printOnly)
```
The default output is stored in the `./outdir_{ext}/haddMC` and `./outdir_{ext}/haddData` folders. You can change the output directory using the `--outputWSDir` option. 

You want at this point to have a single workspace per signal process (per year) and a single workspace per year for data (`allData_{year}.root`). If you are intending to merge categories across years then you should merge the per yer data workspaces e.g.
```
cd /{path-to-flashgg-area}
cmsenv
hadd_workspaces allData.root allData_201*.root
```

## Mass shifting

There is an additional script which allows you to shift the mass of an input MC workspace (simply shift the mass variable of each event by some fixed amount). Note, it is no longer required to have multiple mass point in the signal fitting so this functionality is not particularly useful. For example the following command would shift all the mass values up by 5 GeV.

```
python mass_shifter.py --inputWSFile {inputWSFile.root} --inputMass 125 --targetMass 130
```

Note, the input WS requires `M{inputMass}` (e.g. `M125`) in its name. You can use the `RunWSScripts.py` to submit fr multiple workspaces (and multiple target mass points) e.g.

```
python RunWSScripts.py --inputDir /{path-to-input-workspaces} --mode mass_shift --inputMass 125 --targetMasses 120,130 --ext test_2016 --batch condor --queue longlunch (--printOnly)
```
The output is a mass shifted workspace in the same directory as the input workspace.

## Renaming

Finally, there is a light weight script to rename workspace ROOT files and make them suitable for the FinalFits package. This is the `WSRenamer.py` script which takes as input the path to the input workspaces. Before using this, you must first change the script to match your particular analysis... should be pretty clear from the examples in the script how it can work.
