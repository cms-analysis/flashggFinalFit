PATH=~/eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces/
FILE=$PATH/output_GluGluHToGG_M120_13TeV_amcatnloFXFX_pythia8.root,$PATH/output_GluGluHToGG_M130_13TeV_amcatnloFXFX_pythia8.root,$PATH/output_GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8.root,$PATH/output_VBFHToGG_M120_13TeV_amcatnlo_pythia8.root,$PATH/output_VBFHToGG_M130_13TeV_amcatnlo_pythia8.root,$PATH/output_VBFHToGG_M125_13TeV_amcatnlo_pythia8.root,$PATH/output_ZHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,$PATH/output_ZHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,$PATH/output_ZHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,$PATH/output_WHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,$PATH/output_WHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,$PATH/output_WHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,$PATH/output_ttHJetToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,$PATH/output_ttHJetToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,$PATH/output_ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root
FILE125=$PATH/output_GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8.root,$PATH/output_VBFHToGG_M125_13TeV_amcatnlo_pythia8.root,$PATH/output_ZHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,$PATH/output_WHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,$PATH/output_ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root

FILEEFFACC=$PATH/output_GluGluHToGG_M120_13TeV_amcatnloFXFX_pythia8.root,$PATH/output_GluGluHToGG_M130_13TeV_amcatnloFXFX_pythia8.root,$PATH/output_GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8.root,$PATH/output_VBFHToGG_M120_13TeV_amcatnlo_pythia8.root,$PATH/output_VBFHToGG_M130_13TeV_amcatnlo_pythia8.root,$PATH/output_ZHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,$PATH/output_ZHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,$PATH/output_ZHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,$PATH/output_WHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,$PATH/output_WHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,$PATH/output_WHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,$PATH/output_ttHJetToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,$PATH/output_ttHJetToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,$PATH/output_ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,$PATH/output_VBFHToGG_M125_13TeV_amcatnlo_pythia8._reduced.root

EXT=HggAnalysis_110316_example
PROCS=ggh,vbf,tth,wh,zh
#PROCS=ggh,vbf,zh,wh
CATS=UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1,TTHHadronicTag,TTHLeptonicTag
OUTDIR=outdir_$EXT
SCALES="HighR9EB,HighR9EE,LowR9EB,LowR9EE"
SMEARS="HighR9EBPhi,HighR9EBRho,HighR9EEPhi,HighR9EERho,LowR9EBPhi,LowR9EBRho,LowR9EEPhi,LowR9EERho"
INTLUMI=2.69
DATA=$PATH/DoubleEG.root


./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT --batch IC --intLumi $INTLUMI --smears $SMEARS --scales $SCALES  --signalOnly 
#./makeEffAcc.py $FILEEFFACC Signal/outdir_${EXT}/sigfit/effAccCheck_all.root
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT --intLumi $INTLUMI --backgroundOnly --dataFile $DATA --isData --batch IC 
#cd Background && ./bin/makeFakeData -b CMS-HGG_multipdf_${EXT}.root -s $CMSSW_BASE/src/flashggFinalFit/Signal/outdir_$EXT/CMS-HGG_sigfit_${EXT}.root -o CMS-HGG_multipdf_${EXT}_FAKE_${SEED}.root --isMultiPdf --useBinnedData -S 13 -f $CATS --seed $SEED  && cp CMS-HGG_multipdf_${EXT}_FAKE_${SEED}.root CMS-HGG_multipdf_${EXT}_FAKE.root && cd -
#./runFinalFitsScripts.sh -i $FILE125 -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --datacardOnly --dataFile $DATA --isData --batch IC
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --combineOnly --dataFile $DATA --isData --batch IC
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --combineOnly --dataFile $DATA --isFakeData --batch IC
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --combineOnly --dataFile $DATA --isFakeData --combinePlotsOnly --batch IC
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --combineOnly --combinePlotsOnly --dataFile $DATA --isFakeData --batch IC
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --combineOnly --combinePlotsOnly --dataFile $DATA --isData --batch IC

#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --backgroundOnly --pseudoDataDat $samples --batch IC
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --combineOnly --pseudoDataDat $samples --batch IC

#./yieldsTable.py -w $FILE125 -s Signal/signumbers.txt -u Background/CMS-HGG_multipdf_$EXT.root --factor 1.030671341
##mv Plots/FinalResults/combineJobs13TeV_$EXT Plots/FinalResults/combineJobs13TeV_${EXT}_${SEED}
#cp -r /home/hep/lc1113/public_html/outdir_HggAnalysis_250216/combinePlots /home/hep/lc1113/public_html/outdir_HggAnalysis_250216/combinePlots_$SEED
#cp Background/BkgPlots/*{png,pdf} /home/hep/lc1113/public_html/outdir_HggAnalysis_250216/combinePlots_$SEED/.


####  UNBLINDING ###########

#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT --intLumi $INTLUMI --backgroundOnly --dataFile $DATA --isData --batch IC  --unblind#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --combineOnly --dataFile $DATA --isData --batch IC 
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --combineOnly --dataFile $DATA --isData --batch IC 
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --combineOnly --combinePlotsOnly --dataFile $DATA --isData --batch IC 
 
