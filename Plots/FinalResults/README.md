# Combine Scripts

This is where the combine jobs are created and submitted, and the plots are generated. 

## Combine workflow

The workflow looks like this:
* Move your sigfit, multipdf and datacard into this working dir. (otherwise you jobs will fail!)
Like this:
```
cd Plots/FinalResults
cp ../../Signal/CMS-HGG_sigfit.root CMS-HGG_mva_13TeV_sigfit.root
cp ../../CMS-HGG_multipdf_.root CMS-HGG_mva_13TeV_multipdf.root
cp ../../Datacard/Datacard_13TeV.txt CMS-HGG_mva_13TeV_datacard.txt
```
* Use the template to determine what kind of jobs you wish to run.
To do this, use this template:
```
combineHarvesterOptions13TeV_Template.dat
```
And replace the required arguments like `!EXT!` and `!INTLUMI!` byt the desired values.
* Use the `combineHarvester.py` to generate and submit jobs to the batch using this syntax, specifying the queue you wish to use:
```
./combineHarvester.py -d combineHarvesterOptions13TeV.dat -q 1nh
```
* Use the same script to hadd the output once jobs are done.
```
./combineHarvester.py --hadd combineJobs13TeV
```
* Adapt the template for generating plots:
```
combinePlotsOptions_Template.dat
```
And replace the required arguments like `!EXT!` and `!INTLUMI!` byt the desired values.
* Use the `./makeCombinePlots.py` to make plots, for example.
```
./makeCombinePlots.py -d combinePlotsOptions.dat 
./makeCombinePlots.py -f combineJobs13TeV/MuScan/MuScan.root --mu -t "#sqrt{s}\=13TeV L\=x fb^{-1}" -o mu
```


Congratulations, you have finished!



