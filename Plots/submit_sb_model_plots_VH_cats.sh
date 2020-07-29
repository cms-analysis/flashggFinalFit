#!/bin/bash

cd /vols/build/cms/jl2117/hgg/FinalFits/legacy/Jun20/CMSSW_10_2_13/src/flashggFinalFit/Plots
eval `scramv1 runtime -sh`

python makeSplusBModelPlot.py --inputWSFile InputWS_fixedMH/bestfit_mu.root --loadSnapshot MultiDimFit --cats RECO_VBFTOPO_VHHAD_Tag0,RECO_VBFTOPO_VHHAD_Tag1,RECO_VH_MET_Tag0,RECO_VH_MET_Tag1,RECO_WH_LEP_HIGH_Tag0,RECO_WH_LEP_HIGH_Tag1,RECO_WH_LEP_HIGH_Tag2,RECO_WH_LEP_LOW_Tag0,RECO_WH_LEP_LOW_Tag1,RECO_WH_LEP_LOW_Tag2,RECO_ZH_LEP_Tag0,RECO_ZH_LEP_Tag1 --unblind --doBands --loadToyYields SplusBModels_pass1_shift_VH/toyYields_CMS_hgg_mass.pkl --doSumCategories --doCatWeights --loadWeights jsons/catsWeights_sospb_pass1_shift_VH_CMS_hgg_mass.json --doZeroes --ext _Jul20_pass0_VH --translateCats cats_VH.json --translatePOIs pois_mu.json --doToyVeto --skipIndividualCatPlots
