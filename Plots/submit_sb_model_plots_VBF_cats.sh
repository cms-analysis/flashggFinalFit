#!/bin/bash

cd /vols/build/cms/jl2117/hgg/FinalFits/legacy/Jun20/CMSSW_10_2_13/src/flashggFinalFit/Plots
eval `scramv1 runtime -sh`

python makeSplusBModelPlot.py --inputWSFile InputWS_fixedMH/bestfit_mu.root --loadSnapshot MultiDimFit --cats RECO_VBFTOPO_BSM_Tag0,RECO_VBFTOPO_BSM_Tag1,RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag0,RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag1,RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag0,RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag1,RECO_VBFTOPO_JET3_HIGHMJJ_Tag0,RECO_VBFTOPO_JET3_HIGHMJJ_Tag1,RECO_VBFTOPO_JET3_LOWMJJ_Tag0,RECO_VBFTOPO_JET3_LOWMJJ_Tag1 --unblind --doBands --doToyVeto --loadToyYields SplusBModels_pass1_shift_VBF/toyYields_CMS_hgg_mass.pkl --doSumCategories --doCatWeights --loadWeights jsons/catsWeights_sospb_pass1_shift_VBF_CMS_hgg_mass.json --doZeroes --ext _Jul20_pass0_VBF --translateCats cats_VBF.json --translatePOIs pois_mu.json --skipIndividualCatPlots
