datacard=CMS-HGG_mva_13TeV_datacard.root
#datacard=CMS-HGG_mva_13TeV_datacard_PPCC_pMH_qqHPerProcessChannelCompatibility.root
#proc=qqH

dirname=r_impacts
mkdir $dirname 
cp $datacard $dirname/.
cd $dirname
echo "===============step 1========"
echo "combineTool.py -M Impacts -d $datacard -m 125 --doInitialFit --robustFit 1 -P r --setPhysicsModelParameters pdfindex_UntaggedTag_0_13TeV=1,pdfindex_UntaggedTag_1_13TeV=3,pdfindex_UntaggedTag_2_13TeV=2,pdfindex_UntaggedTag_3_13TeV=1,pdfindex_VBFTag_0_13TeV=2,pdfindex_VBFTag_1_13TeV=1,pdfindex_VBFTag_2_13TeV=4,pdfindex_TTHHadronicTag_13TeV=0,pdfindex_TTHLeptonicTag_13TeV=1,pdfindex_ZHLeptonicTag_13TeV=0,pdfindex_WHLeptonicTag_13TeV=1,pdfindex_VHLeptonicLooseTag_13TeV=2,pdfindex_VHHadronicTag_13TeV=1,pdfindex_VHMetTag_13TeV=0 --minimizerAlgoForMinos Minuit2,Migrad  "
echo "============================="
combineTool.py -M Impacts -d $datacard -m 125 --doInitialFit --robustFit 1 -P r --setPhysicsModelParameters pdfindex_UntaggedTag_0_13TeV=1,pdfindex_UntaggedTag_1_13TeV=3,pdfindex_UntaggedTag_2_13TeV=2,pdfindex_UntaggedTag_3_13TeV=1,pdfindex_VBFTag_0_13TeV=2,pdfindex_VBFTag_1_13TeV=1,pdfindex_VBFTag_2_13TeV=4,pdfindex_TTHHadronicTag_13TeV=0,pdfindex_TTHLeptonicTag_13TeV=1,pdfindex_ZHLeptonicTag_13TeV=0,pdfindex_WHLeptonicTag_13TeV=1,pdfindex_VHLeptonicLooseTag_13TeV=2,pdfindex_VHHadronicTag_13TeV=1,pdfindex_VHMetTag_13TeV=0 --minimizerAlgoForMinos Minuit2,Migrad  
echo "===============step 2========"
echo "combineTool.py -M Impacts -d $datacard -m 125 --robustFit 1 --redefineSignalPOIs r --doFits --job-mode SGE --task-name final --sub-opts='-q hep.q -l h_rt=0:59:0' --minimizerAlgoForMinos Minuit2,Migrad --setPhysicsModelParameters pdfindex_UntaggedTag_0_13TeV=1,pdfindex_UntaggedTag_1_13TeV=3,pdfindex_UntaggedTag_2_13TeV=2,pdfindex_UntaggedTag_3_13TeV=1,pdfindex_VBFTag_0_13TeV=2,pdfindex_VBFTag_1_13TeV=1,pdfindex_VBFTag_2_13TeV=4,pdfindex_TTHHadronicTag_13TeV=0,pdfindex_TTHLeptonicTag_13TeV=1,pdfindex_ZHLeptonicTag_13TeV=0,pdfindex_WHLeptonicTag_13TeV=1,pdfindex_VHLeptonicLooseTag_13TeV=2,pdfindex_VHHadronicTag_13TeV=1,pdfindex_VHMetTag_13TeV=0"
echo "============================="
combineTool.py -M Impacts -d $datacard -m 125 --robustFit 1 --redefineSignalPOIs r --doFits --job-mode SGE --task-name final --sub-opts='-q hep.q -l h_rt=0:59:0' --minimizerAlgoForMinos Minuit2,Migrad  --setPhysicsModelParameters pdfindex_UntaggedTag_0_13TeV=1,pdfindex_UntaggedTag_1_13TeV=3,pdfindex_UntaggedTag_2_13TeV=2,pdfindex_UntaggedTag_3_13TeV=1,pdfindex_VBFTag_0_13TeV=2,pdfindex_VBFTag_1_13TeV=1,pdfindex_VBFTag_2_13TeV=4,pdfindex_TTHHadronicTag_13TeV=0,pdfindex_TTHLeptonicTag_13TeV=1,pdfindex_ZHLeptonicTag_13TeV=0,pdfindex_WHLeptonicTag_13TeV=1,pdfindex_VHLeptonicLooseTag_13TeV=2,pdfindex_VHHadronicTag_13TeV=1,pdfindex_VHMetTag_13TeV=0
RUN=1
while (( $RUN > 0 )) ; do
  RUN=`qstat |wc -l`
  echo "Running $RUN jobs"
  sleep 30
done
echo "===============step 3========"
echo "combineTool.py -M Impacts -d $datacard --redefineSignalPOIs r  -m 125 -o impacts.json"
echo "============================="
combineTool.py -M Impacts -d $datacard --redefineSignalPOIs r  -m 125 -o impacts.json
echo "===============step 4========"
echo "plotImpacts.py -i impacts.json -o impacts"
echo "============================="
plotImpacts.py -i impacts.json -o impacts
cd -
cp $dirname/impacts.pdf .
