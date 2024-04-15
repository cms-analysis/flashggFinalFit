#!/bin/bash

cd /afs/cern.ch/user/f/fderiggi/AC/CMSSW_10_2_13/src/flashggFinalFit/Combine

eval `scramv1 runtime -sh`

text2workspace.py Datacard_ALT_L1.txt -o Datacard_ALT_L1.root -m 125 higgsMassRange=122,128 -P HiggsAnalysis.CombinedLimit.FL1_Interference_JHU_rw_MengsMuV:FL1_Interference_JHU_rw_MengsMuV     --PO "altSignal=ALT_L1"
