#define your list of input files for the signal processing
FILE=/vols/cms04/szenz/ggh_sig_jobs_120_130_67/output_GluGluHToGG_M120_13TeV_amcatnloFXFX_pythia8.root,/vols/cms04/szenz/ggh_sig_jobs_120_130_67/output_GluGluHToGG_M130_13TeV_amcatnloFXFX_pythia8.root,/vols/cms04/szenz/ggh_sig_jobs_125_67/output_GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8.root,/vols/cms04/szenz/vbf_sig_jobs_120_130_67/output_VBFHToGG_M120_13TeV_amcatnlo_pythia8.root,/vols/cms04/szenz/vbf_sig_jobs_120_130_67/output_VBFHToGG_M130_13TeV_amcatnlo_pythia8.root,/vols/cms04/szenz/vbf_sig_jobs_125_67/output_VBFHToGG_M125_13TeV_amcatnlo_pythia8.root,/vols/cms04/szenz/wh_sig_jobs_120_130_67/output_VHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms04/szenz/wh_sig_jobs_120_130_67/output_VHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms04/szenz/wh_sig_jobs_125_67/output_VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms04/szenz/zh_sig_jobs_120_130_67/output_VHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms04/szenz/zh_sig_jobs_120_130_67/output_VHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms04/szenz/zh_sig_jobs_125_67/output_VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms04/szenz/tth_sig_jobs_120_130_67/output_ttHJetToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms04/szenz/tth_sig_jobs_120_130_67/output_ttHJetToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms04/szenz/tth_sig_jobs_125_67/output_ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root
#smaller list than the above: just the 125GeV mass points - this is used to make the datacard
FILE125=/vols/cms04/szenz/ggh_sig_jobs_125_67/output_GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8.root,/vols/cms04/szenz/vbf_sig_jobs_125_67/output_VBFHToGG_M125_13TeV_amcatnlo_pythia8.root,/vols/cms04/szenz/wh_sig_jobs_125_67/output_VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms04/szenz/zh_sig_jobs_125_67/output_VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms04/szenz/tth_sig_jobs_125_67/output_ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root
#same as $FILE but with files which are stupidly large reduced (here, VBF 125). Reduction uses Signal/bin/reduceSamples
FILEEFFACC=/vols/cms04/szenz/ggh_sig_jobs_120_130_67/output_GluGluHToGG_M120_13TeV_amcatnloFXFX_pythia8.root,/vols/cms04/szenz/ggh_sig_jobs_120_130_67/output_GluGluHToGG_M130_13TeV_amcatnloFXFX_pythia8.root,/vols/cms04/szenz/ggh_sig_jobs_125_67/output_GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8.root,/vols/cms04/szenz/vbf_sig_jobs_120_130_67/output_VBFHToGG_M120_13TeV_amcatnlo_pythia8.root,/vols/cms04/szenz/vbf_sig_jobs_120_130_67/output_VBFHToGG_M130_13TeV_amcatnlo_pythia8.root,/vols/cms04/szenz/wh_sig_jobs_120_130_67/output_VHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms04/szenz/wh_sig_jobs_120_130_67/output_VHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms04/szenz/wh_sig_jobs_125_67/output_VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms04/szenz/zh_sig_jobs_120_130_67/output_VHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms04/szenz/zh_sig_jobs_120_130_67/output_VHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms04/szenz/zh_sig_jobs_125_67/output_VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms04/szenz/tth_sig_jobs_120_130_67/output_ttHJetToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms04/szenz/tth_sig_jobs_120_130_67/output_ttHJetToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms04/szenz/tth_sig_jobs_125_67/output_ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,/vols/cms02/lc1113/FinalFits_Feb15_2/CMSSW_7_1_5/src/flashggFinalFit/data/samples/110316/output_VBFHToGG_M125_13TeV_amcatnlo_pythia8._reduced.root
#extension for this run - i like to use the date in here so that you can track when a particular set of files were processed
EXT=HggAnalysis_110316_example
#processes you are considering
PROCS=ggh,vbf,tth,wh,zh
#tags or categories you want to consider
CATS=UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1,TTHHadronicTag,TTHLeptonicTag
#add a bit to the label
OUTDIR=outdir_$EXT
#names of photon smears and scales
SCALES="HighR9EB,HighR9EE,LowR9EB,LowR9EE"
SMEARS="HighR9EBPhi,HighR9EBRho,HighR9EEPhi,HighR9EERho,LowR9EBPhi,LowR9EBRho,LowR9EEPhi,LowR9EERho"
#intlumi - how much of it is there? used to scalre whatever is in the wirksapces to teh required amount
INTLUMI=2.69
#datafile
DATA=/vols/cms04/szenz/data_jobs_57/DoubleEG.root

SEED=0
echo "SEED = $SEED"

## SIGNAL MODEL workspaces and plots
##make sig model
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT --batch IC --intLumi $INTLUMI --smears $SMEARS --scales $SCALES  --signalOnly 
## make effxacc plot
#./makeEffAcc.py $FILEEFFACC Signal/outdir_${EXT}/sigfit/effAccCheck_all.root

## BACKGROUND -- BLINDED or FAKE DATA workflow
#make bkg model using blinded data
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT --intLumi $INTLUMI --backgroundOnly --dataFile $DATA --isData --batch IC 
##alternatively, generate pseudodata from simulated background files
# cd Background && ./bin/makeFakeData -b CMS-HGG_multipdf_${EXT}.root -s $CMSSW_BASE/src/flashggFinalFit/Signal/outdir_$EXT/CMS-HGG_sigfit_${EXT}.root -o CMS-HGG_multipdf_${EXT}_FAKE_${SEED}.root --isMultiPdf --useBinnedData -S 13 -f $CATS --seed $SEED  && cp CMS-HGG_multipdf_${EXT}_FAKE_${SEED}.root CMS-HGG_multipdf_${EXT}_FAKE.root && cd -
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --backgroundOnly --pseudoDataDat $samples --batch IC


## BACKGROUND -- UNBLINDED workflow 
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT --intLumi $INTLUMI --backgroundOnly --dataFile $DATA --isData --batch IC  --unblind


## DATACARD
#./runFinalFitsScripts.sh -i $FILE125 -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --datacardOnly --dataFile $DATA --isData --batch IC

## COMBINE blinded
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --combineOnly --dataFile $DATA --isData --batch IC
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --combineOnly --dataFile $DATA --isFakeData --batch IC
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --combineOnly --dataFile $DATA --isFakeData --combinePlotsOnly --batch IC
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --combineOnly --combinePlotsOnly --dataFile $DATA --isFakeData --batch IC
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --combineOnly --combinePlotsOnly --dataFile $DATA --isData --batch IC

#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --combineOnly --pseudoDataDat $samples --batch IC

#./yieldsTable.py -w $FILE125 -s Signal/signumbers.txt -u Background/CMS-HGG_multipdf_$EXT.root --factor 1.030671341
##mv Plots/FinalResults/combineJobs13TeV_$EXT Plots/FinalResults/combineJobs13TeV_${EXT}_${SEED}
#cp -r /home/hep/lc1113/public_html/outdir_HggAnalysis_250216/combinePlots /home/hep/lc1113/public_html/outdir_HggAnalysis_250216/combinePlots_$SEED
#cp Background/BkgPlots/*{png,pdf} /home/hep/lc1113/public_html/outdir_HggAnalysis_250216/combinePlots_$SEED/.

## COMBINE unblinded
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --combineOnly --dataFile $DATA --isData --batch IC 
./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --combineOnly --combinePlotsOnly --dataFile $DATA --isData --batch IC 
 
