#!/bin/bash

cd /vols/build/cms/jl2117/hgg/FinalFits/legacy/Feb20_unblinding/old_bkg/CMSSW_10_2_13/src/flashggFinalFit/Combine_march20 

eval `scramv1 runtime -sh`

text2workspace.py Datacard.txt -o Datacard_stage1p2_maximal_mjj.root -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel -m 125 higgsMassRange=122,128 \
--PO "map=.*/ggH_0J_PTH_0_10.*:r_ggH_0J_low[1,0,4]" \
--PO "map=.*/ggH_0J_PTH_GT10.*:r_ggH_0J_high[1,0,2]" \
--PO "map=.*/ggH_1J_PTH_0_60.*:r_ggH_1J_low[1,0,4]" \
--PO "map=.*/ggH_1J_PTH_60_120.*:r_ggH_1J_med[1,0,4]" \
--PO "map=.*/ggH_1J_PTH_120_200.*:r_ggH_1J_high[1,0,4]" \
--PO "map=.*/ggH_GE2J_MJJ_0_350_PTH_0_60.*:r_ggH_2J_low[1,0,4]" \
--PO "map=.*/ggH_GE2J_MJJ_0_350_PTH_60_120.*:r_ggH_2J_med[1,0,4]" \
--PO "map=.*/ggH_GE2J_MJJ_0_350_PTH_120_200.*:r_ggH_2J_high[1,0,4]" \
--PO "map=.*/ggH_PTH_.*:r_ggH_BSM[1,0,4]" \
--PO "map=.*/ggH_GE2J_MJJ_350_700_.*.*:r_ggH_VBFlike[1,0,6]" \
--PO "map=.*/ggH_GE2J_MJJ_GT700_.*.*:r_ggH_VBFlike[1,0,6]" \
--PO "map=.*/qqH_GE2J_MJJ_350_700_PTH_0_200_.*:r_qqH_low_mjj[1,0,4]" \
--PO "map=.*/qqH_GE2J_MJJ_GT700_PTH_0_200_.*:r_qqH_high_mjj[1,0,4]" \
--PO "map=.*/qqH_GE2J_.*_PTH_GT200.*:r_qqH_BSM[1,0,4]" \
--PO "map=.*/WH_had_GE2J_MJJ_350_700_PTH_0_200_.*:r_qqH_low_mjj[1,0,4]" \
--PO "map=.*/WH_had_GE2J_MJJ_GT700_PTH_0_200_.*:r_qqH_high_mjj[1,0,4]" \
--PO "map=.*/WH_had_GE2J_.*_PTH_GT200.*:r_qqH_BSM[1,0,4]" \
--PO "map=.*/ZH_had_GE2J_MJJ_350_700_PTH_0_200_.*:r_qqH_low_mjj[1,0,4]" \
--PO "map=.*/ZH_had_GE2J_MJJ_GT700_PTH_0_200_.*:r_qqH_high_mjj[1,0,4]" \
--PO "map=.*/ZH_had_GE2J_.*_PTH_GT200.*:r_qqH_BSM[1,0,4]" \
--PO "map=.*/qqH_GE2J_MJJ_60_120.*:r_qqH_VHhad[1,0,6]" \
--PO "map=.*/WH_had_GE2J_MJJ_60_120.*:r_qqH_VHhad[1,0,6]" \
--PO "map=.*/ZH_had_GE2J_MJJ_60_120.*:r_qqH_VHhad[1,0,6]" \
--PO "map=.*/WH_lep.*hgg:r_WH_lep[1,0,6]" \
--PO "map=.*/ZH_lep.*hgg:r_ZH_lep[1,0,6]" \
--PO "map=.*/ttH.*hgg:r_ttH[1,0,2]" \
--PO "map=.*/tHq.*hgg:r_tHq[1,0,8]"
