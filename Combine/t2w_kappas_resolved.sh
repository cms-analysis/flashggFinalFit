#!/bin/bash

cd /vols/build/cms/jl2117/hgg/FinalFits/legacy/Feb20_unblinding/old_bkg/CMSSW_10_2_13/src/flashggFinalFit/Combine_march20

eval `scramv1 runtime -sh`

text2workspace.py Datacard.txt -o Datacard_kappas_resolved.root -P HiggsAnalysis.CombinedLimit.LHCHCGModels:K1 -m 125 higgsMassRange=122,128 --PO BRU=0
