#!/bin/bash

cd /afs/cern.ch/user/f/fderiggi/AC/CMSSW_10_2_13/src/flashggFinalFit/Combine

eval `scramv1 runtime -sh`

text2workspace.py Datacard_xsec.txt -o Datacard_xsec.root -m 125 higgsMassRange=122,128 -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel     --PO "map=.*/ggH.*:r_ggH[1,0,2]"     --PO "map=.*/bbH.*:r_ggH[1,0,2]"     --PO "map=.*/qqH.*:r_VBF[1,0,3]"     --PO "map=.*/WPLUSH2HQQ.*:r_VH[1,0,3]"     --PO "map=.*/WMINUSH2HQQ.*:r_VH[1,0,3]"     --PO "map=.*/ZH_had.*:r_VH[1,0,3]"     --PO "map=.*/ggZH_had.*:r_VH[1,0,3]"     --PO "map=.*/WPLUSH_lep.*:r_VH[1,0,3]"     --PO "map=.*/WMINUSH_lep.*:r_VH[1,0,3]"     --PO "map=.*/ZH_lep.*:r_VH[1,0,3]"     --PO "map=.*/ZH.*:r_VH[1,0,3]"     --PO "map=.*/WH.*:r_VH[1,0,3]"     --PO "map=.*/ggZH_ll.*:r_VH[1,0,3]"     --PO "map=.*/ggZH_nunu.*:r_VH[1,0,3]"     --PO "map=.*/ttH.*:r_top[1,0,3]"     --PO "map=.*/tHq.*:r_top[1,0,3]"     --PO "map=.*/tHW.*:r_top[1,0,3]"
