#!/bin/bash

cd /vols/build/cms/jl2117/hgg/FinalFits/legacy/May20/CMSSW_10_2_13/src/flashggFinalFit/Plots
eval `scramv1 runtime -sh`

python makeSplusBModelPlot.py --inputWSFile postfit_ws/bestfit_syst_obs_mu.root --loadSnapshot MultiDimFit --cats RECO_VBFTOPO_VHHAD_Tag0,RECO_VBFTOPO_VHHAD_Tag1,RECO_VH_MET_Tag0,RECO_VH_MET_Tag1,RECO_WH_LEP_HIGH_Tag0,RECO_WH_LEP_HIGH_Tag1,RECO_WH_LEP_HIGH_Tag2,RECO_WH_LEP_LOW_Tag0,RECO_WH_LEP_LOW_Tag1,RECO_WH_LEP_LOW_Tag2,RECO_ZH_LEP_Tag0,RECO_ZH_LEP_Tag1 --unblind --doBands --saveToyYields --doSumCategories --doCatWeights --saveWeights --doZeroes --parameterMap r_ggH:1.007,r_VBF:0.994,r_VH:0.756,r_top:1.407 --ext _pass0_mu_VH_cats --translateCats cats_VH.json --translatePOIs pois_mu.json --skipIndividualCatPlots
