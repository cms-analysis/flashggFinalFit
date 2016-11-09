#!/bin/bash

FILE="/vols/cms/szenz/ws_750_30July/output_GluGluHToGG_M120_13TeV_amcatnloFXFX_pythia8.root,/vols/cms/szenz/ws_750_30July/output_VBFHToGG_M120_13TeV_amcatnlo_pythia8.root,/vols/cms/szenz/ws_750_30July/output_WHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_750_30July/output_ZHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_750_30July/output_ttHJetToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_750_30July/output_GluGluHToGG_M123_13TeV_amcatnloFXFX_pythia8.root,/vols/cms/szenz/ws_750_30July/output_VBFHToGG_M123_13TeV_amcatnlo_pythia8.root,/vols/cms/szenz/ws_750_30July/output_WHToGG_M123_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_750_30July/output_ZHToGG_M123_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_750_30July/output_ttHJetToGG_M123_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_750_30July/output_GluGluHToGG_M124_13TeV_amcatnloFXFX_pythia8.root,/vols/cms/szenz/ws_750_30July/output_VBFHToGG_M124_13TeV_amcatnlo_pythia8.root,/vols/cms/szenz/ws_750_30July/output_WHToGG_M124_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_750_30July/output_ZHToGG_M124_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_750_30July/output_ttHJetToGG_M124_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_750_30July/output_GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8.root,/vols/cms/szenz/ws_750_30July/output_VBFHToGG_M125_13TeV_amcatnlo_pythia8.root,/vols/cms/szenz/ws_750_30July/output_WHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_750_30July/output_ZHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_750_30July/output_ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_750_30July/output_GluGluHToGG_M126_13TeV_amcatnloFXFX_pythia8.root,/vols/cms/szenz/ws_750_30July/output_VBFHToGG_M126_13TeV_amcatnlo_pythia8.root,/vols/cms/szenz/ws_750_30July/output_WHToGG_M126_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_750_30July/output_ZHToGG_M126_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_750_30July/output_ttHJetToGG_M126_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_750_30July/output_GluGluHToGG_M127_13TeV_amcatnloFXFX_pythia8.root,/vols/cms/szenz/ws_750_30July/output_VBFHToGG_M127_13TeV_amcatnlo_pythia8.root,/vols/cms/szenz/ws_750_30July/output_WHToGG_M127_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_750_30July/output_ZHToGG_M127_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_750_30July/output_ttHJetToGG_M127_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_750_30July/output_GluGluHToGG_M130_13TeV_amcatnloFXFX_pythia8.root,/vols/cms/szenz/ws_750_30July/output_VBFHToGG_M130_13TeV_amcatnlo_pythia8.root,/vols/cms/szenz/ws_750_30July/output_WHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_750_30July/output_ZHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_750_30July/output_ttHJetToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root"

DATA="/vols/cms/szenz/ws_748_25July/allData.root"

EXT="EdFullTest"
echo "Ext is $EXT"
PROCS="ggh,vbf,tth,wh,zh"
echo "Procs are $PROCS"
CATS="UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1,TTHHadronicTag,TTHLeptonicTag"
echo "Cats are $CATS"
OUTDIR="edInterpolationPlots"
echo "Outdir is $OUTDIR"
INTLUMI=12.9
echo "Intlumi is $INTLUMI"
BATCH="IC"
echo "Batch is $BATCH"
QUEUE="hep.q"
echo "Batch is $QUEUE"
BSWIDTH=3.600000
echo "Bswidth is $BSWIDTH"
NBINS=320
echo "Nbins is $NBINS"

SCALES="HighR9EB,HighR9EE,LowR9EB,LowR9EE"
SCALESCORR="MaterialCentral,MaterialForward,FNUFEE,FNUFEB,ShowerShapeHighR9EE,ShowerShapeHighR9EB,ShowerShapeLowR9EE,ShowerShapeLowR9EB"
SCALESGLOBAL="NonLinearity:UntaggedTag_0:2,Geant4"
SMEARS="HighR9EBPhi,HighR9EBRho,HighR9EEPhi,HighR9EERho,LowR9EBPhi,LowR9EBRho,LowR9EEPhi,LowR9EERho"

#A)
MASSLIST="120,123,124,125,126,127,130"
SKIPMASSES="121,122,128,129"
MLOW=120
MHIGH=130
echo "Masslist is $MASSLIST"
SIGFILE="/home/hep/es811/FinalFitsStudies/Testing1/CMSSW_7_4_7/src/flashggFinalFit/Signal/outdir_${EXT}/CMS-HGG_sigfit_${EXT}.root"

echo "./runBackgroundScripts.sh -i $DATA -p $PROCS -f $CATS --ext $EXT --intLumi $INTLUMI --batch $BATCH --sigFile $SIGFILE --isData --unblind"
./runBackgroundScripts.sh -i $DATA -p $PROCS -f $CATS --ext $EXT --intLumi $INTLUMI --batch $BATCH --sigFile $SIGFILE --isData --unblind
