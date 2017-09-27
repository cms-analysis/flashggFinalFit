#datacard=CMS-HGG_mva_13TeV_datacard.root
datacard=CMS-HGG_mva_13TeV_datacard_PPCC_pMH_qqHPerProcessChannelCompatibility.root
proc=qqH

dirname=r_${proc}_impacts
mkdir $dirname 
cp $datacard $dirname/.
cd $dirname
echo "===============step 1========"
"combineTool.py -M Impacts -d $datacard -m 125 --doInitialFit --robustFit 1 -t -1 --expectSignal 1 --setPhysicsModelParameterRanges r_ggH=-1.00,3.00:r_qqH=-1,3:r_VH=-1.00,3.00:r_ttH=-1.00,3.00 --floatOtherPOIs=1 -P r_${proc} --setPhysicsModelParameters pdfindex_UntaggedTag_0_13TeV=1,pdfindex_UntaggedTag_1_13TeV=3,pdfindex_UntaggedTag_2_13TeV=3,pdfindex_UntaggedTag_3_13TeV=3,pdfindex_VBFTag_0_13TeV=2,pdfindex_VBFTag_1_13TeV=0,pdfindex_VBFTag_2_13TeV=9,pdfindex_TTHHadronicTag_13TeV=0,pdfindex_TTHLeptonicTag_13TeV=2,pdfindex_VHHadronicTag_13TeV=0,pdfindex_VHLeptonicLooseTag_13TeV=1,pdfindex_VHMetTag_13TeV=2,pdfindex_WHLeptonicTag_13TeV=1,pdfindex_ZHLeptonicTag_13TeV=0 --minimizerAlgoForMinos Minuit2,Migrad  "
echo "============================="
combineTool.py -M Impacts -d $datacard -m 125 --doInitialFit --robustFit 1 -t -1 --expectSignal 1 --setPhysicsModelParameterRanges r_ggH=-1.00,3.00:r_qqH=-1,3:r_VH=-1.00,3.00:r_ttH=-1.00,3.00 --floatOtherPOIs=1 -P r_${proc} --setPhysicsModelParameters pdfindex_UntaggedTag_0_13TeV=1,pdfindex_UntaggedTag_1_13TeV=3,pdfindex_UntaggedTag_2_13TeV=3,pdfindex_UntaggedTag_3_13TeV=3,pdfindex_VBFTag_0_13TeV=2,pdfindex_VBFTag_1_13TeV=0,pdfindex_VBFTag_2_13TeV=9,pdfindex_TTHHadronicTag_13TeV=0,pdfindex_TTHLeptonicTag_13TeV=2,pdfindex_VHHadronicTag_13TeV=0,pdfindex_VHLeptonicLooseTag_13TeV=1,pdfindex_VHMetTag_13TeV=2,pdfindex_WHLeptonicTag_13TeV=1,pdfindex_ZHLeptonicTag_13TeV=0 --minimizerAlgoForMinos Minuit2,Migrad  
echo "===============step 2========"
echo "combineTool.py -M Impacts -d $datacard -m 125 --robustFit 1 -t -1 --expectSignal 1 --redefineSignalPOIs r_${proc} --doFits --job-mode SGE --task-name final_${proc} --sub-opts='-q hep.q -l h_rt=0:59:0' --setPhysicsModelParameterRanges r_ggH=-1.00,3.00:r_qqH=-1,3:r_VH=-1.00,3.00:r_ttH=-1.00,3.00  --minimizerAlgoForMinos Minuit2,Migrad --setPhysicsModelParameters pdfindex_UntaggedTag_0_13TeV=1,pdfindex_UntaggedTag_1_13TeV=3,pdfindex_UntaggedTag_2_13TeV=3,pdfindex_UntaggedTag_3_13TeV=3,pdfindex_VBFTag_0_13TeV=2,pdfindex_VBFTag_1_13TeV=0,pdfindex_VBFTag_2_13TeV=9,pdfindex_TTHHadronicTag_13TeV=0,pdfindex_TTHLeptonicTag_13TeV=2,pdfindex_VHHadronicTag_13TeV=0,pdfindex_VHLeptonicLooseTag_13TeV=1,pdfindex_VHMetTag_13TeV=2,pdfindex_WHLeptonicTag_13TeV=1,pdfindex_ZHLeptonicTag_13TeV=0"
echo "============================="
combineTool.py -M Impacts -d $datacard -m 125 --robustFit 1 -t -1 --expectSignal 1 --redefineSignalPOIs r_${proc} --doFits --job-mode SGE --task-name final_${proc} --sub-opts='-q hep.q -l h_rt=0:59:0' --setPhysicsModelParameterRanges r_ggH=-1.00,3.00:r_qqH=-1,3:r_VH=-1.00,3.00:r_ttH=-1.00,3.00  --minimizerAlgoForMinos Minuit2,Migrad  --setPhysicsModelParameters pdfindex_UntaggedTag_0_13TeV=1,pdfindex_UntaggedTag_1_13TeV=3,pdfindex_UntaggedTag_2_13TeV=3,pdfindex_UntaggedTag_3_13TeV=3,pdfindex_VBFTag_0_13TeV=2,pdfindex_VBFTag_1_13TeV=0,pdfindex_VBFTag_2_13TeV=9,pdfindex_TTHHadronicTag_13TeV=0,pdfindex_TTHLeptonicTag_13TeV=2,pdfindex_VHHadronicTag_13TeV=0,pdfindex_VHLeptonicLooseTag_13TeV=1,pdfindex_VHMetTag_13TeV=2,pdfindex_WHLeptonicTag_13TeV=1,pdfindex_ZHLeptonicTag_13TeV=0
RUN=1
while (( $RUN > 0 )) ; do
  RUN=`qstat |wc -l`
  echo "Running $RUN jobs"
  sleep 30
done
echo "===============step 3========"
echo "combineTool.py -M Impacts -d $datacard --redefineSignalPOIs r_${proc}  -m 125 -o impacts_${proc}.json"
echo "============================="
combineTool.py -M Impacts -d $datacard --redefineSignalPOIs r_${proc}  -m 125 -o impacts_${proc}.json
echo "===============step 4========"
echo "plotImpacts.py -i impacts_${proc}.json -o impacts_${proc}"
echo "============================="
plotImpacts.py -i impacts_${proc}.json -o impacts_${proc}
cd -
cp $dirname/impacts_${proc}.pdf .
