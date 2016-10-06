#This is the config file used to produce the ICHEP 2016 results for CMS Hgg.

#path to all the files used for the analysis
INPUTPATH=root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshgg/analyzed/ichep2016/flashgg-workspaces/
#the MC files: 5 processes x 7 mass points
FILE=$INPUTPATH/output_GluGluHToGG_M120_13TeV_amcatnloFXFX_pythia8.root,$INPUTPATH/output_VBFHToGG_M120_13TeV_amcatnlo_pythia8.root,$INPUTPATH/output_WHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_ZHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_ttHJetToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_GluGluHToGG_M123_13TeV_amcatnloFXFX_pythia8.root,$INPUTPATH/output_VBFHToGG_M123_13TeV_amcatnlo_pythia8.root,$INPUTPATH/output_WHToGG_M123_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_ZHToGG_M123_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_ttHJetToGG_M123_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_GluGluHToGG_M124_13TeV_amcatnloFXFX_pythia8.root,$INPUTPATH/output_VBFHToGG_M124_13TeV_amcatnlo_pythia8.root,$INPUTPATH/output_WHToGG_M124_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_ZHToGG_M124_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_ttHJetToGG_M124_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8.root,$INPUTPATH/output_VBFHToGG_M125_13TeV_amcatnlo_pythia8.root,$INPUTPATH/output_WHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_ZHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_GluGluHToGG_M126_13TeV_amcatnloFXFX_pythia8.root,$INPUTPATH/output_VBFHToGG_M126_13TeV_amcatnlo_pythia8.root,$INPUTPATH/output_WHToGG_M126_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_ZHToGG_M126_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_ttHJetToGG_M126_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_GluGluHToGG_M127_13TeV_amcatnloFXFX_pythia8.root,$INPUTPATH/output_VBFHToGG_M127_13TeV_amcatnlo_pythia8.root,$INPUTPATH/output_WHToGG_M127_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_ZHToGG_M127_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_ttHJetToGG_M127_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_GluGluHToGG_M130_13TeV_amcatnloFXFX_pythia8.root,$INPUTPATH/output_VBFHToGG_M130_13TeV_amcatnlo_pythia8.root,$INPUTPATH/output_WHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_ZHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_ttHJetToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root  
# for the effxacc plot, just use mass points 120, 125, 130 (could use the whole lot in future)
FILEEA=$INPUTPATH/output_GluGluHToGG_M120_13TeV_amcatnloFXFX_pythia8.root,$INPUTPATH/output_VBFHToGG_M120_13TeV_amcatnlo_pythia8.root,$INPUTPATH/output_WHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_ZHToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_ttHJetToGG_M120_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8.root,output_VBFHToGG_M125_13TeV_amcatnlo_pythia8._reduced.root,$INPUTPATH/output_WHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_ZHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_GluGluHToGG_M130_13TeV_amcatnloFXFX_pythia8.root,$INPUTPATH/output_VBFHToGG_M130_13TeV_amcatnlo_pythia8.root,$INPUTPATH/output_WHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_ZHToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_ttHJetToGG_M130_13TeV_amcatnloFXFX_madspin_pythia8.root  
# the 125 GeV subsection of those files. Used for datacard generation
FILE125=$INPUTPATH/output_GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8.root,$INPUTPATH/output_VBFHToGG_M125_13TeV_amcatnlo_pythia8.root,$INPUTPATH/output_WHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_ZHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root,$INPUTPATH/output_ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8.root
# The VBF file. typically it is too large, so we truncate it for use in the datacard.
VBF125=$INPUTPATH/output_VBFHToGG_M125_13TeV_amcatnlo_pythia8.root

# Label for output files and plots
EXT=HggAnalysis_ICHEP2016_example
PROCS=ggh,vbf,wh,zh,tth
CATS=UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1,TTHHadronicTag,TTHLeptonicTag
OUTDIR=outdir_$EXT
# photon energy smears and scales - should match what is in the workspaces
SCALES="HighR9EB,HighR9EE,LowR9EB,LowR9EE"
SCALESCORR="MaterialCentral,MaterialForward,FNUFEE,FNUFEB,ShowerShapeHighR9EE,ShowerShapeHighR9EB,ShowerShapeLowR9EE,ShowerShapeLowR9EB"
SCALESGLOBAL="NonLinearity:UntaggedTag_0:2,Geant4"
SMEARS="HighR9EBPhi,HighR9EBRho,HighR9EEPhi,HighR9EERho,LowR9EBPhi,LowR9EBRho,LowR9EEPhi,LowR9EERho"
INTLUMI=12.9
DATA=$INPUTPATH/allData.root
# beam spot needs to be reweigted to width in data (in MC it is 5.14)
BS=3.6
MASSLIST=120,123,124,125,126,127,130

#create signal model
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT --batch LSF --intLumi $INTLUMI --smears $SMEARS --scales $SCALES --scalesCorr $SCALESCORR --scalesGlobal $SCALESGLOBAL --bs $BS  --signalOnly  --massList $MASSLIST 
#create background model
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT --intLumi $INTLUMI --backgroundOnly --dataFile $DATA --isData --batch LSF 
#make the yields table from the outputs of sig/bkg routines
#./yieldsTable.py -w $FILE125 -s Signal/signumbers_${EXT}.txt -u Background/CMS-HGG_multipdf_$EXT.root --factor $INTLUMI --order "Total,ggh,vbf,wh,zh,tth:Untagged Tag 0,Untagged Tag 1,Untagged Tag 2,Untagged Tag 3,VBF Tag 0,VBF Tag 1,TTH Hadronic Tag,TTH Leptonic Tag,Total"
# make the datacard
#./runFinalFitsScripts.sh -i $FILE125 -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --datacardOnly --dataFile $DATA --isData  --smears $SMEARS --scales $SCALES --scalesCorr $SCALESCORR --scalesGlobal $SCALESGLOBAL 

# reduce the VFB sample (causes bad_alloc as too large) and use that for the effxacc plot.
#./Signal/bin/reduceSamples -i $VBF125 -f 0.1
#./makeEffAcc.py $FILEEA Signal/outdir_${EXT}/sigfit/effAccCheck_all.root $INTLUMI

#run combine
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --combineOnly --dataFile $DATA --isData --batch LSF
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --combineOnly --combinePlotsOnly --dataFile $DATA --isData --batch LSF




####  UNBLINDING ###########
# the below are the unblinded versions of the commands above.
# make bkg model
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT --intLumi $INTLUMI --backgroundOnly --dataFile $DATA --isData --batch LSF  --unblind
# run combine, make plots
#./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --combineOnly --dataFile $DATA --isData --batch LSF 
./runFinalFitsScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT  --intLumi $INTLUMI --combineOnly --combinePlotsOnly --dataFile $DATA --isData --batch LSF 
 
