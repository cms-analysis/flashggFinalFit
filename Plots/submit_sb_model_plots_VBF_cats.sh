#!/bin/bash

cd /vols/build/cms/jl2117/hgg/FinalFits/legacy/May20/CMSSW_10_2_13/src/flashggFinalFit/Plots
eval `scramv1 runtime -sh`

python makeSplusBModelPlot.py --inputWSFile postfit_ws/bestfit_syst_obs_mu.root --loadSnapshot MultiDimFit --cats RECO_VBFTOPO_BSM_Tag0,RECO_VBFTOPO_BSM_Tag1,RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag0,RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag1,RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag0,RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag1,RECO_VBFTOPO_JET3_HIGHMJJ_Tag0,RECO_VBFTOPO_JET3_HIGHMJJ_Tag1,RECO_VBFTOPO_JET3_LOWMJJ_Tag0,RECO_VBFTOPO_JET3_LOWMJJ_Tag1 --unblind --doBands --saveToyYields --doSumCategories --doCatWeights --saveWeights --doZeroes --parameterMap r_ggH:1.007,r_VBF:0.994,r_VH:0.756,r_top:1.407 --ext _pass0_mu_VBF_cats --translateCats cats_VBF.json --translatePOIs pois_mu.json --skipIndividualCatPlots
