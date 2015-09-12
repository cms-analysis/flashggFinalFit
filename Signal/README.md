# Running Final Fits Plots - Notes

## Different File Types

We have several types of files, which can be differentiated by their suffix:

* `_Bkg.root`        
-> Output of running over Background MC. Used as input to `./Background/bin/BiasStudy`.

* `_Data.root` or `_data.root`            
-> Output of running over Data. Used as input to `./Background/bin/fTest` to produce `_multipdf.root` files.

* `_Sig.root`
-> Output of running over signal MC without systematic variations. This is used as input to the scripts `./Signal/bin/SignalFit` to create `_sigfit.root` files and `./Signal/bin/signalFTest` to create plots (which help to determine `dat/newConfig.dat`). Also used in Used as input to `./Background/bin/BiasStudy`.

* `_Syst.root`
-> Input for `./Signal/bin/calcPhotonSystConsts` to create `Signal/dat/photonCatSyst.dat`

* `_multipdf.root`
-> Not used for signal model workflow (for Background model).

* `_sigfit.root`
-> Output of `./Signal/binSignalFit`, used as input for `Plots/makeParametricSignalModelPlots.C` to make Signal Plots.

For now, for FLASHgg `_Sig.root` and `_Syst.root` are in the same file.

## Signal workflow

The workflow looks like this: 

                              flashgg output
                              /          \ 
                             /            \
                   		_Sig.root        _Syst.root     
                   		/    \                     \
		               	/       \                      \
	  	  	./bin/signalFTest   \                 ./bin/calcPhotonSystConsts
	               		|           \                        |
		                |            \                       |
	        		dat/config.dat       \            dat/photonCatSyst.dat
		                    	\         \             /
	                       	 \          \          /    
	                      	   \          \       /   
		                            ./bin/SignalFit
		                                   	|
		                                  	|
	                           		_sigfit.root
	                                   		|
	                                  		|
	               		../Plots/makeParametricSignalModelPlots.C                                          
		                                  	|
		                                  	|
                    	            		Plots

## Generating the dat/config.dat file.	

One can use the `./bin/signalFTest` script to regenerate this. Example output is provided here 
http://www.hep.ph.imperial.ac.uk/~lc1113/FinalFit_010615/Signal/fTest/

Working FLASHgg example:
```
file=/afs/cern.ch/work/s/sethzenz/public/test_jobs_3/output_GluGluHToGG_M-125_13TeV_powheg_pythia8.root
./bin/signalFTest -i $file -d dat/newConfig_LCTest2.dat -p ggh
```

Working h2gglobe example:

You will need to get hold of the h2gglobe files on eos. One way to do this is:
```
eosmount $HOME/eos
```
and then substitute lcorpe for your username in the below.
```
./bin/signalFTest -i /afs/cern.ch/user/l/lcorpe//eos/cms/store/group/phys_higgs/cmshgg/analyzed/workspace_store/legacy_freeze_v6/CMS-HGG_mva_8TeV_Sig_2014_01_13.root -d dat/newConfig_LCTest2.dat -p ggh,vbf -n 9 --isFlashgg 0
```


## Generating the dat/photonCatSyst.dat file

The script `./bin/calcPhotonSystConsts` generates this config file, taking as input files of the type “_Syst.root”. Produces output like this:
http://www.hep.ph.imperial.ac.uk/~lc1113/FinalFit_010615/Signal/Systematics/

NB: The systematics functionality is currently only supported for Photon Energy Scale for flashgg.
The code will be updated to allow other types in due course. For h22globe, this is still possible.

FLASHgg working example:
```
./bin/calcPhotonSystConsts -i $file -o dat/photonCatSyst_LCTest.dat -p ggh,tth -s HighR9EE,LowR9EE,HighR9EB,LowR9EB -r HighR9EE,LowR9EE,HighR9EBRho,LowR9EBRho,HighR9EBPhi,LowR9EBPhi
```
h2gglobe working example:
```
./bin/calcPhotonSystConsts -i /afs/cern.ch/user/l/lcorpe/eos/cms/store/group/phys_higgs/cmshgg/analyzed/workspace_store/legacy_freeze_v6/CMS-HGG_mva_8TeV_Syst_2014_01_13.root -o dat/photonCatSyst_LCTest2.dat --isFlashgg 0
```

## Signal Fit
The main script is SignalFit. This takes as input two dat files and a root file.

* `-d datfile`, which specifies information about how many gaussians to fit in each category under right vertex and wring vertex hypotheses. an example file which can be found at `dat/newConfig.dat`. This file can also be generated using the script  `./bin/SignaFTest`. 
* `-s systematics datfile`, which tells how to propagate single photon systematics to diphoton categories. Default is example file at `dat/photonCatSyst.dat`. These configs can be generated using `./bin/calcPhotonSystConsts`. 

`./bin/SignalFit` should run locally in <1hr. (Experimentally, I find ~15min).The output looks something like  `_sigfit.root`

Plots can be obtained by using the Plots/makeParametricSignalModelPlots.C
http://www.hep.ph.imperial.ac.uk/~lc1113/FinalFit_010615/Signal/FinalModel/

FLASHgg working example:
```
./bin/SignalFit -i $file -d dat/newConfig_LCTest2.dat  --mhLow=120 --mhHigh=130 -s dat/photonCatSyst_LCTest.dat --procs ggh,tth
```

h2gglobe working example:
```
./bin/SignalFit -i  -d dat/newConfigMinimal.dat  --mhLow=120 --mhHigh=130 -s dat/photonCatSyst.dat --procs vbf,ggh --isFlashgg 0

```

## Making the Signal Plots

To actually generate plots, there is a macro stored in Plots. Use it like this(for FLASHgg and, just replace file path for h2gglobe):
```
cd ../Plots
root
root [0] gSystem->SetIncludePath("-I$ROOTSYS/include -I$ROOFITSYS/include -I$CMSSW_BASE/src");
root [0] .L $CMSSW_BASE/lib/$SCRAM_ARCH/libHiggsAnalysisCombinedLimit.so
root [0] .L makeParametricSignalModelPlots.C+g
root [0] makeParametricSignalModelPlots("../Signal/CMS-HGG_sigfit.root","outputdir")
```

