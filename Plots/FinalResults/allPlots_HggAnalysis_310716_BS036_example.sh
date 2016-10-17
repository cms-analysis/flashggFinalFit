#Full suite of plots as used for the Moriond2016 result
EXT=HggAnalysis_310716_BS036_example
INTLUMI=12.9
##########################################
############## MU SCANS #################
##########################################

#./makeCombinePlots.py -d combinePlotsOptions_${EXT}.dat --verbose  -b
#./makeCombinePlots.py -f combineJobs13TeV_$EXT/MuScanFloatMH/MuScanFloatMH.root --mu -t "$INTLUMI fb^{-1} (13#scale[0.5]{ }TeV)" -o MuScanFloatMH --MHtext 0.17:0.7:"#splitline{m_{H}=125.09 #pm 0.24 GeV}{#hat{m}_{H}=125.33 GeV}" -b
#./makeCombinePlots.py -f combineJobs13TeV_$EXT/MuScanFixMH_v2/MuScanFixMH_v2.root --mu -t "$INTLUMI fb^{-1} (13#scale[0.5]{ }TeV)" --MHtext 0.17:0.7:"m_{H}=125.09 GeV" -o MuScanFixMH_v2  -b
#./makeCombinePlots.py -f combineJobs13TeV_$EXT/MuScanFixMH125.97_v2/MuScanFixMH125.97_v2.root --mu -t "$INTLUMI fb^{-1} (13#scale[0.5]{ }TeV)" --MHtext 0.17:0.7:"m_{H}=125.97 GeV" -o MuScanFixMH125.97_v2  -b
#./makeCombinePlots.py -f combineJobs13TeV_$EXT/MuScanProfileMH/MuScanProfileMH.root --mu -t "$INTLUMI fb^{-1} (13#scale[0.5]{ }TeV)" --MHtext 0.17:0.7:"m_{H} Profiled" -o MuScanProfileMH  -b #RooRealVar::MH = 125.973 +/- 0.292702  L(115 - 135) // [GeV]
#./makeCombinePlots.py -f combineJobs13TeV_$EXT/MuScanAllSyst/MuScanAllSyst.root --mu -t "$INTLUMI fb^{-1} (13#scale[0.5]{ }TeV)" --MHtext 0.17:0.7:"m_{H}=125.97 GeV" -o MuScanAllSyst  -b
#./makeCombinePlots.py -f combineJobs13TeV_$EXT/MuScanNoSyst/MuScanNoSyst.root --mu -t "$INTLUMI fb^{-1} (13#scale[0.5]{ }TeV)" --MHtext 0.17:0.7:"m_{H}=125.97 GeV" -o MuScanNoSyst  -b
#./makeCombinePlots.py -f combineJobs13TeV_$EXT/MuScanNoTheory/MuScanNoTheory.root --mu -t "$INTLUMI fb^{-1} (13#scale[0.5]{ }TeV)" --MHtext 0.17:0.7:"m_{H}=125.97 GeV" -o MuScanNoTheory  -b
#exit 1
##########################################
############## MH SCANS #################
##########################################

#./makeCombinePlots.py -f combineJobs13TeV_$EXT/MHScan/MHScan.root --mh -t "$INTLUMI fb^{-1} (13#scale[0.5]{ }TeV)"  -o MHScan  -b

##########################################
#########  PER TAG CH COMP ###############
##########################################

#./makeCombinePlots.py -f combineJobs13TeV_$EXT/MuScanFixMH/MuScanFixMH.root,combineJobs13TeV_$EXT/PerTagChannelCompatibilityFixMH/r_TTHLeptonicTag_13TeV/r_TTHLeptonicTag_13TeV.root,combineJobs13TeV_$EXT/PerTagChannelCompatibilityFixMH/r_TTHHadronicTag_13TeV/r_TTHHadronicTag_13TeV.root,combineJobs13TeV_$EXT/PerTagChannelCompatibilityFixMH/r_VBFTag_1_13TeV/r_VBFTag_1_13TeV.root,combineJobs13TeV_$EXT/PerTagChannelCompatibilityFixMH/r_VBFTag_0_13TeV/r_VBFTag_0_13TeV.root,combineJobs13TeV_$EXT/PerTagChannelCompatibilityFixMH/r_UntaggedTag_3_13TeV/r_UntaggedTag_3_13TeV.root,combineJobs13TeV_$EXT/PerTagChannelCompatibilityFixMH/r_UntaggedTag_2_13TeV/r_UntaggedTag_2_13TeV.root,combineJobs13TeV_$EXT/PerTagChannelCompatibilityFixMH/r_UntaggedTag_1_13TeV/r_UntaggedTag_1_13TeV.root,combineJobs13TeV_$EXT/PerTagChannelCompatibilityFixMH/r_UntaggedTag_0_13TeV/r_UntaggedTag_0_13TeV.root --perprocchcomp -x -3,8.5 -o PerTagChannelCompatibilityFixMH --do1sig  -l 0.55,0.65,0.85,0.90 --text="    ${INTLUMI} fb^{-1} (13#scale[0.5]{ }TeV)"  --mhval "125.09"  -b
#./makeCombinePlots.py -f combineJobs13TeV_$EXT/MuScanProfileMH/MuScanProfileMH.root,combineJobs13TeV_$EXT/PerTagChannelCompatibilityProfileMH/r_TTHLeptonicTag_13TeV/r_TTHLeptonicTag_13TeV.root,combineJobs13TeV_$EXT/PerTagChannelCompatibilityProfileMH/r_TTHHadronicTag_13TeV/r_TTHHadronicTag_13TeV.root,combineJobs13TeV_$EXT/PerTagChannelCompatibilityProfileMH/r_VBFTag_1_13TeV/r_VBFTag_1_13TeV.root,combineJobs13TeV_$EXT/PerTagChannelCompatibilityProfileMH/r_VBFTag_0_13TeV/r_VBFTag_0_13TeV.root,combineJobs13TeV_$EXT/PerTagChannelCompatibilityProfileMH/r_UntaggedTag_3_13TeV/r_UntaggedTag_3_13TeV.root,combineJobs13TeV_$EXT/PerTagChannelCompatibilityProfileMH/r_UntaggedTag_2_13TeV/r_UntaggedTag_2_13TeV.root,combineJobs13TeV_$EXT/PerTagChannelCompatibilityProfileMH/r_UntaggedTag_1_13TeV/r_UntaggedTag_1_13TeV.root,combineJobs13TeV_$EXT/PerTagChannelCompatibilityProfileMH/r_UntaggedTag_0_13TeV/r_UntaggedTag_0_13TeV.root --perprocchcomp -x -3,8.5 -o PerTagChannelCompatibilityProfileMH --do1sig  -l 0.55,0.65,0.85,0.90 --text="  ${INTLUMI} fb^{-1} (13#scale[0.5]{ }TeV)"  --mhval "Profiled"  -b

##########################################
#########  PER PROC CH COMP ##############
##########################################

./makeCombinePlots.py -f combineJobs13TeV_$EXT/MuScanProfileMH/MuScanProfileMH.root,combineJobs13TeV_$EXT/PerProcessChannelCompatibilityProfileMH/r_ttH/r_ttH.root,combineJobs13TeV_$EXT/PerProcessChannelCompatibilityProfileMH/r_qqH/r_qqH.root,combineJobs13TeV_$EXT/PerProcessChannelCompatibilityProfileMH/r_ggH/r_ggH.root --perprocchcomp -x -2,9 -o PerProcChannelCompatibilityProfileMH --do1sig  -l 0.55,0.65,0.85,0.9 --text="  ${INTLUMI} fb^{-1} (13#scale[0.5]{ }TeV)" --MHtext 0.57:0.41:"#bf{#mu_{VH} = 1}"  --mhval "Profiled"  -b
exit 1
#./makeCombinePlots.py -f combineJobs13TeV_$EXT/MuScanFixMH/MuScanFixMH.root,combineJobs13TeV_$EXT/PerProcessChannelCompatibilityFixMH/r_ttH/r_ttH.root,combineJobs13TeV_$EXT/PerProcessChannelCompatibilityFixMH/r_qqH/r_qqH.root,combineJobs13TeV_$EXT/PerProcessChannelCompatibilityFixMH/r_ggH/r_ggH.root --perprocchcomp -x -2,9 -o PerProcChannelCompatibilityFixMH --do1sig  -l 0.55,0.65,0.85,0.9 --text="       ${INTLUMI} fb^{-1} (13#scale[0.5]{ }TeV)" --MHtext 0.57:0.41:"#bf{#mu_{VH}=1}"   --mhval "125.09"  -b
#
#./makeCombinePlots.py -f combineJobs13TeV_$EXT/MuScanFixMH125.97/MuScanFixMH125.97.root,combineJobs13TeV_$EXT/PerProcessChannelCompatibilityFixMH125.97/r_ttH/r_ttH.root,combineJobs13TeV_$EXT/PerProcessChannelCompatibilityFixMH125.97/r_qqH/r_qqH.root,combineJobs13TeV_$EXT/PerProcessChannelCompatibilityFixMH/r_ggH/r_ggH.root --perprocchcomp -x -2,9 -o PerProcChannelCompatibilityFixMH125.97 --do1sig  -l 0.55,0.65,0.9,0.9 --text="${INTLUMI} fb^{-1} (13#scale[0.5]{ }TeV)"  --mhval "125.97"  -b

##########################################
#########  MUHAT vs MH 1D Scans ##########
##########################################
#./makeCombinePlots.py -f combineJobs13TeV_${EXT}/MultiPdfMuHatvsMH/120.00/120.00.root,combineJobs13TeV_${EXT}/MultiPdfMuHatvsMH/121.00/121.00.root,combineJobs13TeV_${EXT}/MultiPdfMuHatvsMH/122.00/122.00.root,combineJobs13TeV_${EXT}/MultiPdfMuHatvsMH/123.00/123.00.root,combineJobs13TeV_${EXT}/MultiPdfMuHatvsMH/124.00/124.00.root,combineJobs13TeV_${EXT}/MultiPdfMuHatvsMH/125.00/125.00.root,combineJobs13TeV_${EXT}/MultiPdfMuHatvsMH/126.00/126.00.root,combineJobs13TeV_${EXT}/MultiPdfMuHatvsMH/127.00/127.00.root,combineJobs13TeV_${EXT}/MultiPdfMuHatvsMH/128.00/128.00.root,combineJobs13TeV_${EXT}/MultiPdfMuHatvsMH/129.00/129.00.root,combineJobs13TeV_${EXT}/MultiPdfMuHatvsMH/120.50/120.50.root,combineJobs13TeV_${EXT}/MultiPdfMuHatvsMH/121.50/121.50.root,combineJobs13TeV_${EXT}/MultiPdfMuHatvsMH/122.50/122.50.root,combineJobs13TeV_${EXT}/MultiPdfMuHatvsMH/123.50/123.50.root,combineJobs13TeV_${EXT}/MultiPdfMuHatvsMH/124.50/124.50.root,combineJobs13TeV_${EXT}/MultiPdfMuHatvsMH/125.50/125.50.root,combineJobs13TeV_${EXT}/MultiPdfMuHatvsMH/126.50/126.50.root,combineJobs13TeV_${EXT}/MultiPdfMuHatvsMH/127.50/127.50.root,combineJobs13TeV_${EXT}/MultiPdfMuHatvsMH/128.50/128.50.root,combineJobs13TeV_${EXT}/MultiPdfMuHatvsMH/129.50/129.50.root,combineJobs13TeV_${EXT}/MultiPdfMuHatvsMH/130.00/130.00.root --mpdfmaxlh -x 120,130 -y -0.6,2.2 -o MuHat_vs_MH --do1sig  -t "$INTLUMI fb^{-1} (13#scale[0.5]{ }TeV)" --legend 0.16,0.75,0.49,0.84 -b 
##########################################
##########  RV vs RF 2D SCANS   ##########
##########################################
#./makeCombinePlots.py -f combineJobs13TeV_$EXT/RVRFScanFloatMH/RVRFScanFloatMH.root --rvrf -t "$INTLUMI fb^{-1} (13#scale[0.5]{ }TeV)" -o RVRFScanFloatMH  --xbinning 28,-0.99,3.49 --ybinning 9,-0.49,3.49  --MHtext 0.17:0.16:"#scale[0.9]{m_{H}=125.09 #pm 0.24 GeV}" --legend 0.71,0.65,0.89,0.89 -b 
#./makeCombinePlots.py -f combineJobs13TeV_$EXT/RVRFScanProfileMH/RVRFScanProfileMH.root --rvrf -t "$INTLUMI fb^{-1} (13#scale[0.5]{ }TeV)" -o RVRFScanProfileMH_Run1Ranges --xbinning 28,-0.99,3.49 --ybinning 9,-0.49,3.49 --MHtext 0.17:0.16:"#scale[0.9]{m_{H} Profiled}" --legend 0.71,0.65,0.89,0.89 -b 
#./makeCombinePlots.py -f combineJobs13TeV_$EXT/RVRFScanProfileMH/RVRFScanProfileMH.root --rvrf -t "$INTLUMI fb^{-1} (13#scale[0.5]{ }TeV)" -o RVRFScanProfileMH --xbinning 51,-0.99,3.49 --ybinning 25,-0.49,4.49 --MHtext 0.17:0.16:"#scale[0.9]{m_{H} Profiled}" --legend 0.71,0.65,0.89,0.89 -b 
#./makeCombinePlots.py -f combineJobs13TeV_$EXT/RVRFScanFixMH/RVRFScanFixMH.root --rvrf -t "$INTLUMI fb^{-1} (13#scale[0.5]{ }TeV)" -o RVRFScanFixMH --xbinning 28,-0.99,3.49 --ybinning 9,-0.49,3.49 --MHtext 0.17:0.17:"m_{H}=125.09 GeV" --legend 0.71,0.65,0.89,0.89 -b 
#./makeCombinePlots.py -f combineJobs13TeV_$EXT/RVRFScanFixMH125.97/RVRFScanFixMH125.97.root --rvrf -t "$INTLUMI fb^{-1} (13#scale[0.5]{ }TeV)" -o RVRFScanFixMH125.97 --xbinning 28,-0.99,3.49 --ybinning 9,-0.49,3.49  --MHtext 0.17:0.17:"m_{H}=125.97 GeV" --legend 0.71,0.65,0.89,0.89 -b 

##########################################
##########  CV vs CF 2D SCANS   ##########
##########################################
#./makeCombinePlots.py -f combineJobs13TeV_$EXT/CVCFScanFixMH_v2/CVCFScanFixMH_v2.root --cvcf -t "$INTLUMI fb^{-1} (13#scale[0.5]{ }TeV)" -o CVCFScanFixMH --xbinning 30,0,2 --ybinning 40,-1,3 --MHtext 0.17:0.17:"m_{H}=125.09 GeV" --legend 0.71,0.65,0.89,0.89 -b 
##########################################
##########  K GLU vs K GAM 2D SCANS   ##########
##########################################
#./makeCombinePlots.py -f combineJobs13TeV_$EXT/KGluKGamScanFixMH_v2/KGluKGamScanFixMH_v2.root --kglukgam -t "$INTLUMI fb^{-1} (13#scale[0.5]{ }TeV)" -o KGluKGamScanFixMH --xbinning 25,0,2 --ybinning 25,0,2 --MHtext 0.17:0.17:"m_{H}=125.09 GeV" --legend 0.71,0.65,0.89,0.89 -b 
