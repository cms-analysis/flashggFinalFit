#!/bin/bash

cd /vols/build/cms/jl2117/hgg/FinalFits/legacy/Feb20_unblinding/old_bkg/CMSSW_10_2_13/src/flashggFinalFit/Combine_march20 

eval `scramv1 runtime -sh`

text2workspace.py Datacard.txt -o Datacard_mu.root -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel -m 125 higgsMassRange=122,128 \
--PO "map=.*/ggH.*:r_ggH[1,0,2]" \
--PO "map=.*/qqH.*:r_VBF[1,0,3]" \
--PO "map=.*/WH_had.*:r_VH[1,0,3]" \
--PO "map=.*/ZH_had.*:r_VH[1,0,3]" \
--PO "map=.*/WH_lep.*:r_VH[1,0,3]" \
--PO "map=.*/ZH_lep.*:r_VH[1,0,3]" \
--PO "map=.*/ttH.*:r_top[1,0,3]" \
--PO "map=.*/tHq.*:r_top[1,0,3]"
