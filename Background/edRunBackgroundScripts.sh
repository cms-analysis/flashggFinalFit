#!/bin/bash

FILE="/vols/cms/es811/FinalFits/ws_851/output_GluGluHToGG_M120_13TeV_amcatnloFXFX_pythia8_GG2H.root,/vols/cms/es811/FinalFits/ws_851/output_VBFHToGG_M120_13TeV_amcatnlo_pythia8_VBF.root,/vols/cms/es811/FinalFits/ws_851/output_WHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8_WH2HQQ.root,/vols/cms/es811/FinalFits/ws_851/output_ZHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8_QQ2HLL.root,/vols/cms/es811/FinalFits/ws_851/output_WHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8_QQ2HLNU.root,/vols/cms/es811/FinalFits/ws_851/output_ZHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8_ZH2HQQ.root,/vols/cms/es811/FinalFits/ws_851/output_ttHJetToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8_TTH.root,/vols/cms/es811/FinalFits/ws_851/output_GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8_GG2H.root,/vols/cms/es811/FinalFits/ws_851/output_VBFHToGG_M125_13TeV_amcatnlo_pythia8_VBF.root,/vols/cms/es811/FinalFits/ws_851/output_WHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8_WH2HQQ.root,/vols/cms/es811/FinalFits/ws_851/output_ZHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8_QQ2HLL.root,/vols/cms/es811/FinalFits/ws_851/output_WHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8_QQ2HLNU.root,/vols/cms/es811/FinalFits/ws_851/output_ZHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8_ZH2HQQ.root,/vols/cms/es811/FinalFits/ws_851/output_ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8_TTH.root,/vols/cms/es811/FinalFits/ws_851/output_GluGluHToGG_M130_13TeV_amcatnloFXFX_pythia8_GG2H.root,/vols/cms/es811/FinalFits/ws_851/output_VBFHToGG_M130_13TeV_amcatnlo_pythia8_VBF.root,/vols/cms/es811/FinalFits/ws_851/output_WHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8_WH2HQQ.root,/vols/cms/es811/FinalFits/ws_851/output_ZHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8_QQ2HLL.root,/vols/cms/es811/FinalFits/ws_851/output_WHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8_QQ2HLNU.root,/vols/cms/es811/FinalFits/ws_851/output_ZHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8_ZH2HQQ.root,/vols/cms/es811/FinalFits/ws_851/output_ttHJetToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8_TTH.root"

DATA="/vols/cms/es811/FinalFits/ws_851/allData.root"

EXT="STXS_12Feb"
echo "Ext is $EXT"
PROCS="GG2H,VBF,TTH,QQ2HLL,QQ2HLNU,WH2HQQ,ZH2HQQ"
echo "Procs are $PROCS"
#CATS="UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1,TTHHadronicTag,TTHLeptonicTag,ZHLeptonicTag,WHLeptonicTag,VHLeptonicLooseTag,VHHadronicTag,VHMetTag"
CATS="UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1,VBFTag_2,TTHHadronicTag,TTHLeptonicTag,ZHLeptonicTag,WHLeptonicTag,VHLeptonicLooseTag,VHHadronicTag,VHMetTag"
echo "Cats are $CATS"
INTLUMI=36.8
echo "Intlumi is $INTLUMI"
BATCH="IC"
echo "Batch is $BATCH"
QUEUE="hep.q"
echo "Batch is $QUEUE"

SIGFILE="/vols/build/cms/es811/FreshStart/Pass3/CMSSW_7_4_7/src/flashggFinalFit/Signal/outdir_${EXT}/CMS-HGG_sigfit_${EXT}.root"

#echo "./runBackgroundScripts.sh -i $DATA -p $PROCS -f $CATS --ext $EXT --intLumi $INTLUMI --batch $BATCH --sigFile $SIGFILE --isData --unblind"
#./runBackgroundScripts.sh -i $DATA -p $PROCS -f $CATS --ext $EXT --intLumi $INTLUMI --batch $BATCH --sigFile $SIGFILE --isData --unblind
echo "./runBackgroundScripts.sh -i $DATA -p $PROCS -f $CATS --ext $EXT --intLumi $INTLUMI --batch $BATCH --sigFile $SIGFILE --isData"
./runBackgroundScripts.sh -i $DATA -p $PROCS -f $CATS --ext $EXT --intLumi $INTLUMI --batch $BATCH --sigFile $SIGFILE --isData
