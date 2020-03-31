#!/bin/bash

cd /vols/build/cms/jl2117/hgg/FinalFits/legacy/Feb20_unblinding/old_bkg/CMSSW_10_2_13/src/flashggFinalFit/Combine_march20 

eval `scramv1 runtime -sh`

text2workspace.py Datacard.txt -o Datacard_stage0.root -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel -m 125 higgsMassRange=122,128 \
--PO "map=.*/ggH_.*:r_ggH[1,0,2]" \
--PO "map=.*/qqH_.*:r_VBF[1,0,3]" \
--PO "map=.*/WH_had_.*:r_VH_had[1,0,6]" \
--PO "map=.*/ZH_had_.*:r_VH_had[1,0,6]" \
--PO "map=.*/WH_lep.*:r_WH_lep[1,0,6]" \
--PO "map=.*/ZH_lep.*:r_ZH_lep[1,0,6]" \
--PO "map=.*/ttH.*:r_ttH[1,0,2]" \
--PO "map=.*/tHq.*:r_tHq[1,0,8]"
