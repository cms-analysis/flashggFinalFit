#!/bin/bash

cd /afs/cern.ch/user/f/fderiggi/AC/CMSSW_10_2_13/src/flashggFinalFit/Combine

eval `scramv1 runtime -sh`

text2workspace.py Datacard_ALT_0M_WHLEP_VHLEP_MET.txt -o Datacard_ALT_0M_WHLEP_VHLEP_MET.root -m 125 higgsMassRange=122,128 -P HiggsAnalysis.CombinedLimit.FA3_Interference_JHU_ggHSyst_rw_MengsMuV_HeshyXsec_ggHInt_ggHphase:FA3_Interference_JHU_ggHSyst_rw_MengsMuV_HeshyXsec_ggHInt_ggHphase     --PO altSignal=ALT_0M
