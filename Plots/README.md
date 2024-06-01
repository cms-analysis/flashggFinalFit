# Plotting

## Background envelope plot
To make a nice plot of the background model envelope, you can use the following script:
```
python3 makeMultipdfPlot.py --inputWSFile $PATH_TO_BKGMODEL_FILE --cat $CAT --ext $EXT --mass 125.38 --inputSignalWSFile $PATH_TO_SIGMODEL_FILE
```
For example, in the tutorial the command for the EBEB_highR9highR9 category looks like:
```
python3 makeMultipdfPlot.py --inputWSFile ../Background/outdir_tutorial/CMS-HGG_multipdf_EBEB_highR9highR9.root --cat EBEB_highR9highR9 --ext tutorial --mass 125.38 --inputSignalWSFile ../Signal/outdir_packaged/CMS-HGG_sigfit_packaged_EBEB_highR9highR9.root
```


