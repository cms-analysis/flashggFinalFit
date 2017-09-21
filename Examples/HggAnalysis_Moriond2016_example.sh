#!/bin/bash
##These are the files we will use for the signal and background model building
#shortcut for path where the files are stored
INPUTPATH=root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/moriond2016/flashgg-workspaces/
#files usef for teh signal model: each process has three mass points 120, 125 and 130 geV.
FILE=$INPUTPATH/output_GluGluHToGG_M120_13TeV_amcatnloFXFX_pythia8.root,$INPUTPATH/output_GluGluHToGG_M130_13TeV_amcatnloFXFX_pythia8.root,$INPUTPATH/output_GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8.root,$INPUTPATH/output_VBFHToGG_M120_13TeV_amcatnlo_pythia8.root,$INPUTPATH/output_VBFHToGG_M130_13TeV_amcatnlo_pythia8.root,$INPUTPATH/output_VBFHToGG_M125_13TeV_amcatnlo_pythia8.root,$INPUTPATH/output_ZHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_ZHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_ZHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_WHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_WHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_WHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_ttHJetToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_ttHJetToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root
#shortcut for just the 125 GeV files.
FILE125=$INPUTPATH/output_GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8.root,$INPUTPATH/output_VBFHToGG_M125_13TeV_amcatnlo_pythia8.root,$INPUTPATH/output_ZHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_WHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root
#same as $FILE but where the heaviest file (VBF 125) has been reduced. this is simply for memory management puproses.
FILEEFFACC=$INPUTPATH/output_GluGluHToGG_M120_13TeV_amcatnloFXFX_pythia8.root,$INPUTPATH/output_GluGluHToGG_M130_13TeV_amcatnloFXFX_pythia8.root,$INPUTPATH/output_GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8.root,$INPUTPATH/output_VBFHToGG_M120_13TeV_amcatnlo_pythia8.root,$INPUTPATH/output_VBFHToGG_M130_13TeV_amcatnlo_pythia8.root,$INPUTPATH/output_ZHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_ZHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_ZHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_WHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_WHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_WHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_ttHJetToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_ttHJetToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_VBFHToGG_M125_13TeV_amcatnlo_pythia8._reduced.root
#the real data, for background model and final results
DATA=$INPUTPATH/DoubleEG.root

##define the other options 
#name of this run
EXT=HggAnalysis_Moriond2016_example
#processes to consider
PROCS=ggh,vbf,tth,wh,zh
#tags (aka categories) to consider
CATS=UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1,TTHHadronicTag,TTHLeptonicTag
#output dir
OUTDIR=outdir_$EXT
#photon energy scale and smear categories
SCALES="HighR9EB,HighR9EE,LowR9EB,LowR9EE"
SMEARS="HighR9EBPhi,HighR9EBRho,HighR9EEPhi,HighR9EERho,LowR9EBPhi,LowR9EBRho,LowR9EEPhi,LowR9EERho"
#amount of data
INTLUMI=2.69
BATCH=LSF


##signal model preparation
#The first tiem you run this command, it will run the signal f-test to determine the number of gaussians to use for each tag/process. You'll be prompted to use the output of this to fill in the required config file. Then re-run to build the signal model.
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT --batch $BATCH --intLumi $INTLUMI --smears $SMEARS --scales $SCALES --signalOnly 

##background model preparations
#by default this produces blinded plots... use option --unblind to unblind.
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT --intLumi $INTLUMI --backgroundOnly --dataFile $DATA --isData --batch $BATCH 
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT --intLumi $INTLUMI --backgroundOnly --dataFile $DATA --isData --batch $BATCH  --unblind


##making the datacard
# this step generates the datacard using the signal model as input.
#./runFinalFitsScripts.sh -i $FILE125 -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --datacardOnly --dataFile $DATA --isData --batch $BATCH

## final combine results
# run combine using the signal, background and datacard from previous steps. If YOU ARE STILL BLINDED, BE CAREFUL. Make sure you are using pseudodata or making only 'expected' results using the configurations available in Plots/FinalResults
./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --combineOnly --dataFile $DATA --isData --batch $BATCH
# skip the jobs and just make plots from previous files
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --combineOnly --combinePlotsOnly --dataFile $DATA --isData --batch $BATCH

# other tables and plots
#./makeEffAcc.py $FILEEFFACC Signal/outdir_${EXT}/sigfit/effAccCheck_all.root
#./yieldsTable.py -w $FILE125 -s Signal/signumbers.txt -u Background/CMS-HGG_multipdf_$EXT.root --factor 1.030671341


######### Other workflows ############
# use the below to make fake data to practice with if you are waiting for real data.
#cd Background && ./bin/makeFakeData -b CMS-HGG_multipdf_${EXT}.root -s $CMSSW_BASE/src/flashggFinalFit/Signal/outdir_$EXT/CMS-HGG_sigfit_${EXT}.root -o CMS-HGG_multipdf_${EXT}_FAKE_${SEED}.root --isMultiPdf --useBinnedData -S 13 -f $CATS --seed 0  && cp CMS-HGG_multipdf_${EXT}_FAKE_${SEED}.root CMS-HGG_multipdf_${EXT}_FAKE.root && cd -
# combine using fake data
#generate background model from pseudodata
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --backgroundOnly --pseudoDataDat $samples --batch $BATCH
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --combineOnly --dataFile $DATA --isFakeData --batch $BATCH
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --combineOnly --dataFile $DATA --isFakeData --combinePlotsOnly --batch $BATCH
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --combineOnly --combinePlotsOnly --dataFile $DATA --isFakeData --batch $BATCH
