# Combine Scripts

This is where the combine jobs are created and submitted, and the plots are generated.  

## Combine workflow

The workflow looks like this:
* Move your sigfit, multipdf and datacard into this working dir. (otherwise your jobs will fail!)
Like this:

Make sure your copied files have exactly the names listed below: these are the names expected in the first section of the datacard, and if they do not match, your combine jobs will fail instantly.

```
cd Plots/FinalResults
cp ../../Signal/CMS-HGG_sigfit_<ext>_<proc>_<tagname>.root CMS-HGG_mva_13TeV_sigfit_<proc>_<tagname>.root #to do with each of your (nTags x nProcs) sig files 
cp ../../Background/CMS-HGG_multipdf_<ext>.root CMS-HGG_mva_13TeV_multipdf.root
cp ../../Datacard/Datacard_13TeV_<ext>.txt CMS-HGG_mva_13TeV_datacard.txt
```

* Use the template to determine what kind of jobs you wish to run. 
To do this, use this template. BE CAREFUL: This template produces UNBLINDED results. If you want to make blinded plots, only run the jobs marked "expected" 

```
combineHarvesterOptions13TeV_Template.dat
```

And replace the required arguments like `!EXT!` and `!INTLUMI!` byt the desired values. If you are using the pilot script (`runFinalFitsScripts.sh` from `flashggFinalFit` dir,  using option `--combineOnly` ), this is done automatically.

* Use the `combineHarvester.py` to generate and submit jobs to the batch using this syntax, specifying the queue you wish to use:

```
./combineHarvester.py -d combineHarvesterOptions13TeV_<extension>.dat -q 1nh --batch LSF --verbose
#or if you are running at IC:
./combineHarvester.py -d combineHarvesterOptions13TeV_<extension>.dat -q hepshort.q --batch IC --verbose
```

* Use the same script to hadd the output once jobs are done.

```
./combineHarvester.py --hadd combineJobs13TeV_<extension>
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

Running Notes:
* Make sure your copied files have exactly the names listed below: these are the names expected in the first section of the datacard, and if they do not match, your combine jobs will fail instantly.

