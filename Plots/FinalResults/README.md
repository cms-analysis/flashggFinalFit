# Combine Scripts

This is where the combine jobs are created and submitted, and the plots are generated.  

## Combine workflow

The workflow looks like this:
* Move your sigfit, multipdf and datacard into this working dir. (otherwise your jobs will fail!)
Like this:

Make sure your copied files have exactly the names listed below: these are the names expected in the first section of the datacard, and if tehy do not match, your combine jobs will fail instantly.

```
cd Plots/FinalResults
cp ../../Signal/CMS-HGG_sigfit_<ext>.root CMS-HGG_mva_13TeV_sigfit.root
cp ../../CMS-HGG_multipdf_<ext>.root CMS-HGG_mva_13TeV_multipdf.root
cp ../../Datacard/Datacard_13TeV_<ext>.txt CMS-HGG_mva_13TeV_datacard.txt
```

* Use the template to determine what kind of jobs you wish to run. 
To do this, use this template. By default, the *expected* p-value (at mh125 and across full mh range) and *expected* mh scan are produced, but there are many other example in the template which you can uncomment if needed).

```
combineHarvesterOptions13TeV_Template.dat
```

And replace the required arguments like `!EXT!` and `!INTLUMI!` byt the desired values. If you are using the pilot script (`runFinalFitsScripts.sh` from `flashggFinalFit` dir,  using option `--combineOnly` ), this is done automatically.

* Use the `combineHarvester.py` to generate and submit jobs to the batch using this syntax, specifying the queue you wish to use:

```
./combineHarvester.py -d combineHarvesterOptions13TeV_hgg_dry_run_2015.dat -q 1nh --batch LSF --verbose
#or if you are running at IC:
./combineHarvester.py -d combineHarvesterOptions13TeV_hgg_dry_run_2015.dat -q hepshort.q --batch IC --verbose
```

* Use the same script to hadd the output once jobs are done.

```
./combineHarvester.py --hadd combineJobs13TeV_hgg_dry_run_2015
```

* Adapt the template for generating plots (this takes the output of your hadded combine jobs and makes them into the relevant plot: limit, p-value, mh scan, mu scan etc ...):

```
combinePlotsOptions_Template.dat
```

And replace the required arguments like `!EXT!` and `!INTLUMI!` byt the desired values. This is done automagically if using the pilot script.

* Use the `./makeCombinePlots.py` to make plots, for example.

```
./makeCombinePlots.py -d combinePlotsOptions.dat #if using the dat file 
./makeCombinePlots.py -f combineJobs13TeV/MuScan/MuScan.root --mu -t "#sqrt{s}\=13TeV L\=x fb^{-1}" -o mu #if using manually
```

Example output can be found here:
```
https://twiki.cern.ch/twiki/bin/view/CMS/FLASHggFramework#Combine
```


Congratulations, you have finished!

## Notes

What works:
* Expected p-value plots seem to be working well, producing sane results.
What doesn't work:
* Expected mH scan with systematics seems to be finding suprious minima at 122.00 even when one specifies a particular mH for the expected signal model.
* The Expected mH scan appears to have large discontinuities which I suspect are due to the discrete pdfIndices(used by the envelope method)  being handled incorrectly. Freezing the discrete pdfIndices does not appear to improve the situation at first glance. Adding the option -S0 (no systematics) does appear to fix things.
* Renoving the systematics (eg doing -S0) does not appear to visibly change the significance of the final result. One might expect the -2DLL vs mH curve to widen, but it does not, or the p-value to get worse, which is also does not...
* Some warnings appear in combine pertaining to the background model: many params are at their limit. Perhaps there is an issue with the background model which needs to be pinned down? Need to investigate if this is simply a hangover from using the envelope method.


Running Notes:
* Make sure your copied files have exactly the names listed below: these are the names expected in the first section of the datacard, and if tehy do not match, your combine jobs will fail instantly.
* When submitting combine jobs, at CERN the 8nh queue is at present apparently baaically not working... while for the 1nh queue it is so oversubscribed that the jobs do not begin for almost an hour in my experience. In that case it is almost worth running them all locally. At IC on the other hand, the jobs start instantly and are done within a few minutes...


## To Do

Iterate with Nick regarding the above issues. Initial suggestions:
* For the expected, try using post-fit and freezing nuisances instead of using -S0.
* Signal model always finding minimum at 122.00, maybe issue with signal model. Manueally check that chaging MH changes signal model as expcted (see example on combine twiki)
* Background warnings: check if parameters which are complained about are actually use in the fit at all. Some option for MultiDimFit could help (--SaveSpecificIndex or similar?).
* Investigate discontinuites in MH scan.



