#!/bin/bash

cd /vols/build/cms/jl2117/hgg/FinalFits/legacy/Jun20/CMSSW_10_2_13/src/flashggFinalFit/Plots
eval `scramv1 runtime -sh`

python makeSplusBModelPlot.py --inputWSFile InputWS_fixedMH/bestfit_mu_inclusive.root --loadSnapshot MultiDimFit --cats all --unblind --doBands --doToyVeto --loadToyYields SplusBModels_pass1_shift_mu_inclusive/toyYields_corr_CMS_hgg_mass.pkl --doSumCategories --doCatWeights --loadWeights jsons/catsWeights_sospb_pass1_shift_mu_inclusive_CMS_hgg_mass.json --doZeroes --ext _Jul20_pass0_mu_inclusive --translateCats cats.json --translatePOIs pois_mu.json --skipIndividualCatPlots
