# Impacts

Impacts documentation to come here. 

# Bias studies

Here we provide a script to perform a simple bias study. 

## Inputs

The only pre-requisite is a workspace with a single category, 
and therefore a single multipdf (the object that controls the envelope method) 
and a single pdf index corresponding to the choice of functional form.

To create this, it's simple to use the existing combineCards functionality, for example:
```
combineCards.py Datacard.txt --ic cat_name > Datacard_cat_name.txt
```

This creates a .txt datacard with only categories matching the reg exp `cat_name` included. 
Be careful: you will probably have to manually delete some pdfindex lines at the bottom; 
the script does not know that these correspond to the analysis categories, 
and therefore will leave them all in (you only want the one corresponding to the category you are studying). 

Once that is done, you can run your usual `text2workspace` command to generate the `-d, --datacard` input for this script. 

## Usage

The script is split into three different stages:
 * `-t, --toys`:  throw and save a total of `-n,--nToys` toys for each of the candidate functions included in the envelope
 * `-f, --fits`:  fit each of those toys and extract the uncertainty
 * `-p, --plots`: plot the pull distribution of the resulting fits

You can then inspect the output plots and hope to see an approximately gaussian shape with zero mean and unit width.
Normally, provided that the absolute value of the mean is less than 0.14, this is considered satisfactory. 

The three steps can be run in one go, but it's probably safer to run them one-by-one. 
Here is an example:

```
./RunBiasStudy.py -d Datacard_mu_ggH_cat0.root -t 
./RunBiasStudy.py -d Datacard_mu_ggH_cat0.root -f -c "--cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 --freezeParameters MH" 
./RunBiasStudy.py -d Datacard_mu_ggH_cat0.root -p --gaussianFit
```
The options for the second step are passed to combine; these are recommended to get the fit to converge. 
The additional option on the plotting is fairly self-explanatory; it adds a gaussian fit to the output plot.

## More options

There are various things one can tweak for these studies. 
Here is a list of the common options: 
 * `-n,--nToys`: the default number of toys is 1000 per function, but can be lowered or raised. 
 * `-e,--expectSignal`: the injected signal strength is 1 by default, but zero can also be checked, or higher values for searches. 
 * `-s,--seed`: the default value of -1 finds a random seed; you can fix this for reproducility if you prefer.
 * `--poi`: if your parameter of interest is called something other than `r`, say so here.
 * `--split`: default number of toys to be thrown or fits to be performed in one go. Set to 500 but may need to be lowered for memory reasons if you have a more complicated fit. 
 * `--selectFunction`: you can specify a string here to only select certain functions for these studies (e.g. `bern` to match all Bernstein polynomials, `exp1` to match just the first-order exponential).
