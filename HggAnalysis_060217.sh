#The electron and muon SF's have been updated to the final ones:
#https://github.com/cms-analysis/flashgg/pull/750
#So we should perhaps see a normalization change in TTHLeptonic and not much else.  It would be good to check this when time permits, and indeed we can switch to these if everything is under control.
FILE=/vols/cms/szenz/ws_826b/output_GluGluHToGG_M120_13TeV_amcatnloFXFX_pythia8.root,/vols/cms/szenz/ws_826b/output_GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8.root,/vols/cms/szenz/ws_826b/output_GluGluHToGG_M130_13TeV_amcatnloFXFX_pythia8.root,/vols/cms/szenz/ws_826b/output_ttHJetToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_826b/output_ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_826b/output_ttHJetToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_826b/output_VBFHToGG_M120_13TeV_amcatnlo_pythia8.root,/vols/cms/szenz/ws_826b/output_VBFHToGG_M125_13TeV_amcatnlo_pythia8.root,/vols/cms/szenz/ws_826b/output_VBFHToGG_M130_13TeV_amcatnlo_pythia8.root,/vols/cms/szenz/ws_826b/output_WHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_826b/output_WHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_826b/output_WHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_826b/output_ZHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_826b/output_ZHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_826b/output_ZHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root
FILE125=/vols/cms/szenz/ws_826b/output_GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8.root,/vols/cms/szenz/ws_826b/output_ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_826b/output_VBFHToGG_M125_13TeV_amcatnlo_pythia8.root,/vols/cms/szenz/ws_826b/output_WHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms/szenz/ws_826b/output_ZHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root
DATA=/vols/cms/szenz/ws_826b/allData.root

EXT=HggAnalysis_060217
#PROCS=ggh,vbf,tth,wh,zh
PROCS=ggh,vbf,wh,zh,tth
CATS=UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1,VBFTag_2,TTHHadronicTag,TTHLeptonicTag,VHMetTag,VHHadronicTag,VHLeptonicLooseTag,ZHLeptonicTag,WHLeptonicTag
OUTDIR=outdir_$EXT
SCALES="HighR9EB,HighR9EE,LowR9EB,LowR9EE"
SCALESCORR="MaterialCentral,MaterialForward,FNUFEE,FNUFEB,ShowerShapeHighR9EE,ShowerShapeHighR9EB,ShowerShapeLowR9EE,ShowerShapeLowR9EB"
SCALESGLOBAL="NonLinearity:UntaggedTag_0:2,Geant4"
SMEARS="HighR9EBPhi,HighR9EBRho,HighR9EEPhi,HighR9EERho,LowR9EBPhi,LowR9EBRho,LowR9EEPhi,LowR9EERho"
INTLUMI=36.8
BS=3.6
MASSLIST=120,125,130

#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT --batch IC --intLumi $INTLUMI --smears $SMEARS --scales $SCALES --scalesCorr $SCALESCORR --scalesGlobal $SCALESGLOBAL --bs $BS  --signalOnly  --massList $MASSLIST --useDCB_1G 0 --useSSF 1 
./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT --intLumi $INTLUMI --backgroundOnly --dataFile $DATA --isData --batch IC 
#./yieldsTable.py -w $FILE125 -s Signal/signumbers_${EXT}.txt -u Background/CMS-HGG_multipdf_$EXT.root --factor $INTLUMI --order "Total,ggh,vbf,wh,zh,tth:Untagged Tag 0,Untagged Tag 1,Untagged Tag 2,Untagged Tag 3,VBF Tag 0,VBF Tag 1,VBF Tag 2,TTH Hadronic Tag,TTH Leptonic Tag,VH Met Tag,VH LeptonicLoose Tag,VH Hadronic Tag,ZH Leptonic Tag,WH Leptonic Tag,Total" 
#./runFinalFitsScripts.sh -i $FILE125 -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --datacardOnly --dataFile $DATA --isData --batch IC --smears $SMEARS --scales $SCALES --scalesCorr $SCALESCORR --scalesGlobal $SCALESGLOBAL 
#./Signal/bin/reduceSamples -i $VBF125 -f 0.1
#./makeEffAcc.py $FILEEA Signal/outdir_${EXT}/sigfit/effAccCheck_all.root $INTLUMI
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --combineOnly --dataFile $DATA --isData --batch IC
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --combineOnly --combinePlotsOnly --dataFile $DATA --isData --batch IC

#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --backgroundOnly --pseudoDataDat $samples --batch IC
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --combineOnly --pseudoDataDat $samples --batch IC

##mv Plots/FinalResults/combineJobs13TeV_$EXT Plots/FinalResults/combineJobs13TeV_${EXT}_${SEED}
#cp -r /home/hep/lc1113/public_html/outdir_HggAnalysis_250216/combinePlots /home/hep/lc1113/public_html/outdir_HggAnalysis_250216/combinePlots_$SEED
#cp Background/BkgPlots/*{png,pdf} /home/hep/lc1113/public_html/outdir_HggAnalysis_250216/combinePlots_$SEED/.


####  UNBLINDING ###########

#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT --intLumi $INTLUMI --backgroundOnly --dataFile $DATA --isData --batch IC  --unblind
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --combineOnly --dataFile $DATA --isData --batch IC 
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --combineOnly --dataFile $DATA --isData --batch IC 
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --combineOnly --combinePlotsOnly --dataFile $DATA --isData --batch IC 
 
