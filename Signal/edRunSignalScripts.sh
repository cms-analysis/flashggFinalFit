#!/bin/bash

FILE="/vols/cms/szenz/ws_826b/output_GluGluHToGG_M120_13TeV_amcatnloFXFX_pythia8.root,/vols/cms/szenz/ws_826b/output_VBFHToGG_M120_13TeV_amcatnlo_pythia8.root,/vols/cms/szenz/ws_826b/output_WHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_826b/output_ZHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_826b/output_ttHJetToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_826b/output_GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8.root,/vols/cms/szenz/ws_826b/output_VBFHToGG_M125_13TeV_amcatnlo_pythia8.root,/vols/cms/szenz/ws_826b/output_WHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_826b/output_ZHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_826b/output_ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_826b/output_GluGluHToGG_M130_13TeV_amcatnloFXFX_pythia8.root,/vols/cms/szenz/ws_826b/output_VBFHToGG_M130_13TeV_amcatnlo_pythia8.root,/vols/cms/szenz/ws_826b/output_WHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_826b/output_ZHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_826b/output_ttHJetToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root"

#EXT="AllTags06Feb_nGausSSForder1"
EXT="AllTags06Feb_nGausSSFfinetuned"
echo "Ext is $EXT"
PROCS="ggh,vbf,tth,wh,zh"
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
BSWIDTH=3.400000
echo "Bswidth is $BSWIDTH"
NBINS=320
echo "Nbins is $NBINS"

SCALES="HighR9EB,HighR9EE,LowR9EB,LowR9EE"
SCALESCORR="MaterialCentral,MaterialForward,FNUFEE,FNUFEB,ShowerShapeHighR9EE,ShowerShapeHighR9EB,ShowerShapeLowR9EE,ShowerShapeLowR9EB"
SCALESGLOBAL="NonLinearity:UntaggedTag_0:2,Geant4"
SMEARS="HighR9EBPhi,HighR9EBRho,HighR9EEPhi,HighR9EERho,LowR9EBPhi,LowR9EBRho,LowR9EEPhi,LowR9EERho"

#MASSLIST="120,123,124,125,126,127,130"
MASSLIST="120,125,130"
MLOW=120
MHIGH=130
echo "Masslist is $MASSLIST"

./runSignalScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT --intLumi $INTLUMI --batch $BATCH --massList $MASSLIST --bs $BSWIDTH \
                        --smears $SMEARS --scales $SCALES --scalesCorr $SCALESCORR --scalesGlobal $SCALESGLOBAL --useSSF 1 --useDCB_1G 0
                        #--smears $SMEARS --scales $SCALES --scalesCorr $SCALESCORR --scalesGlobal $SCALESGLOBAL --useSSF 0 --useDCB_1G 0
                        #--smears $SMEARS --scales $SCALES --scalesCorr $SCALESCORR --scalesGlobal $SCALESGLOBAL --useSSF 1 --useDCB_1G 1
