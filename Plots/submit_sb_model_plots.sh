#!/bin/bash

cd /vols/build/cms/jl2117/hgg/FinalFits/legacy/May20/CMSSW_10_2_13/src/flashggFinalFit/Plots
eval `scramv1 runtime -sh`

python makeSplusBModelPlot.py --inputWSFile postfit_ws/bestfit_syst_obs_mu_inclusive.root --loadSnapshot MultiDimFit --cats all --unblind --doBands --saveToyYields --doSumCategories --doCatWeights --saveWeights --doZeroes --parameterMap r:1.031 --ext _pass0_mu_inclusive --translateCats cats.json --translatePOIs pois_mu.json
