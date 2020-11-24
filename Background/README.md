# Background Modelling

This is where the background model is determined. This is the only package yet to be pythonised for the new Final Fits. We have introduced a new mode for running the fTest `fTestParallel` which creates a separate job per analysis category. These jobs can then be submitted in parallel, greatly speeding up the process!

The S+B plotting functionalities in this package have for now been depleted. You can produce the traditional blinded signal + bkg model plots using the `../Plots/makeSplusBModelPlot.py` script (see the `Plots` package for mode details). The `fTestParallel` will by default still produce the standard multipdf style plots.

The new `fTestParallel` method for running the background scripts is only configured for use on true data. Please refer to an older version of Final Fits to run the background modelling on pseudo-data, generated using the background simulation samples. This functionality will be added ASAP!

## Setup

The background modelling package still needs to be built with it's own makefiles. Please note that there will be verbose warnings from BOOST etc, which can be ignored. So long as the `make` commands finish without error, then the compilation happened fine.:

```
cd ${CMSSW_BASE}/src/flashggFinalFit/Background
cmsenv
make
```

If it fails, first try `make clean` and then `make` again. 

## Background f-Test

Takes the output of flashgg (`allData.root`) and outputs a `RooMultiPdf` for each analysis category. The `RooMultiPdf` contains a large collection of background model pdfs from different functions families including exponential functions. Bernstein polynomials, Laurent series and power law functions. In the final fit, the choice of background model pdf from this collection is treated as an additional discrete nuisance parameter (discrete profiling method). This fTest determine which functions are included in the `RooMultiPdf` by requiring some (weak) goodness-of-fit constaint. Note, the normalisation and shape parameters of the background functions are still free to float in the final fit.

The new functionality performs the fTest in parallel for each analysis category:
```
python RunBackgroundScripts.py --inputConfig config_test.py --mode fTestParallel (--printOnly)
```

Similar to the signal scripts the options are steered using an input config file e.g.:
```
backgroundScriptCfg = {

  # Setup
  'inputWSDir':'/vols/cms/jl2117/hgg/ws/UL/Sept20/merged_data', # path to 'allData.root' file
  'cats':'auto', # auto: automatically inferred from input data workspace
  'catOffset':0, # add offset to category numbers (useful for categories from different allData.root files)  
  'ext':'test', # extension to add to output directory
  'year':'combined', # Use combined when merging all years in category (for plots)

  # Job submission options
  'batch':'IC', # [condor,SGE,IC,local]
  'queue':'hep.q' # for condor e.g. microcentury

}
```

The output is a ROOT file containing the `RooMultiPdf`'s for each analysis category in `outdir_{ext}`. These are your background models (which must be copied across to the `Combine` directory when you get to the final fits step). In addition the standard fTest plots are produced in the `outdir_{ext}/bkgfTest-Data` directory, where the numbering matches the `catOffset` for each category (see the submission scripts).

### To do list

 * Pseudodata functionality

 * As mentioned above you can now plot the blinded S+B model plots from the compiled datacard using `../Plots/makeSplusBModelPlot.py` script. We should add a dedicated plotting script in the `Background` package ASAP.

 * The output background models have a prefit normalization which matches the total number of events in the category `RooDataSets`. For categories with high S/B, the prefit normalization (which includes S) will be over-estimating the size of the background. When you then run the expected results (which throws an asimov toy from the pre-fit signal and background models) you will subsequently under-estimate the true sensitivity. This artifact only becomes noticable when dealing with categories with very high S/B, and importantly does NOT affect the observed results since the background model normalisation is floated in the final fit. For now, before running the expected scans you can run a S+B bestfit to data and subsequently throw the asimov toy from the postfit background model. At some point we should change the normalisation in the background modelling to interpolate from the sidebands only, rather than using the absolute event yield. 

 * Pythonize everything to make the code more accessible.

 * Include the 2D fTest functionality (as used in the HH analysis)
