#!/bin/bash
#bash variables
FILE="";
EXT="auto"; #extensiom for all folders and files created by this script
PROCS="ggh"
CATS="UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,UntaggedTag_4,VBFTag_0,VBFTag_1,VBFTag_2,TTHHadronicTag,TTHLeptonicTag,VHHadronicTag,VHTightTag,VHLooseTag,VHEtTag"
#CATS="UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,UntaggedTag_4,VBFTag_0,VBFTag_1,VBFTag_2,TTHLeptonicTag,VHHadronicTag,VHTightTag,VHLooseTag"
#CATS="UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,UntaggedTag_4,VBFTag_0,VBFTag_1,VBFTag_2,VHHadronicTag,VHTightTag,VHLooseTag"
SCALES="HighR9EE,LowR9EE,HighR9EB,LowR9EB"
#SMEARS="HighR9EE,LowR9EE,HighR9EBRho,LowR9EBRho,HighR9EBPhi,LowR9EBPhi"
SMEARS="HighR9EE,LowR9EE,HighR9EB,LowR9EB" #DRY RUN
PSEUDODATADAT=""
SIGFILE=""
SIGONLY=1
BKGONLY=1
DATACARDONLY=1
COMBINEONLY=1
COMBINEPLOTSONLY=0
SUPERLOOP=1
COUNTER=0
CONTINUELOOP=0
INTLUMI=1
DATAFILE=""
UNBLIND=0
ISDATA=0
VERBOSE=0
BATCH="LSF"
DEFAULTQUEUE="1nh"
usage(){
	echo "The script runs background scripts:"
		echo "options:"
echo "-h|--help)" 
echo "-i|--inputFile) "
echo "-p|--procs) (default $PROCS)"
echo "-f|--flashggCats) (default $CATS) "
echo "--ext) (default $EXT)"
echo "--pseudoDataDat)"
echo "--combine) "
echo "--combineOnly) "
echo "--combinePlotsOnly) "
echo "--superloop) Used to loop over the whole process N times (default $SUPERLOOP)"
echo "--signalOnly)"
echo "--backgroundOnly) "
echo "--datacardOnly)"
echo "--continueLoop) specify which iteration to start loop at (default $COUNTER)"
echo "--intLumi) specified in fb^-{1} (default $INTLUMI)) "
echo "--isData) ACTUAL DATA (default $DATA)) "
echo "--isFakeData) FAKE DATA (default 0)) "
echo "--unblind) specified in fb^-{1} (default $UNBLIND)) "
echo "--dataFile) specified in fb^-{1} (default $DATAFILE)) "
echo "--batch) which batch system to use (LSF,IC) (default $BATCH)) "
}


#------------------------------ parsing


# options may be followed by one colon to indicate they have a required argument
if ! options=$(getopt -u -o hi:p:f: -l help,inputFile:,procs:,flashggCats:,ext:,smears:,scales:,pseudoDataDat:,sigFile:,combine,combineOnly,combinePlotsOnly,signalOnly,backgroundOnly,datacardOnly,superloop:,continueLoop:,intLumi:,unblind,isData,isFakeData,dataFile:,batch:,verbose -- "$@")
then
# something went wrong, getopt will put out an error message for us
exit 1
fi
set -- $options

while [ $# -gt 0 ]
do
case $1 in
-h|--help) usage; exit 0;;
-i|--inputFile) FILE=$2; shift ;;
-p|--procs) PROCS=$2; shift ;;
--scales) SCALES=$2; shift ;;
--smears) SMEARS=$2; shift ;;
-f|--flashggCats) CATS=$2; shift ;;
--ext) EXT=$2; echo "test" ; shift ;;
--pseudoDataDat) PSEUDODATADAT=$2; shift;;
--dataFile) DATAFILE=$2; shift;;
--batch) BATCH=$2; echo " BATCH $BATCH " ; shift;;
--signalOnly) COMBINEONLY=0;BKGONLY=0;SIGONLY=1;DATACARDONLY=0;;
--backgroundOnly) COMBINEONLY=0;BKGONLY=1;SIGONLY=0;DATACARDONLY=0;;
--datacardOnly) COMBINEONLY=0;BKGONLY=0;SIGONLY=0;DATACARDONLY=1;;
--combine) COMBINEONLY=1;;#;BKGONLY=0;SIGONLY=0;DATACARDONLY=0;;
--combineOnly) COMBINEONLY=1;BKGONLY=0;SIGONLY=0;DATACARDONLY=0;;
--combinePlotsOnly) COMBINEPLOTSONLY=1;COMBINEONLY=1;BKGONLY=0;SIGONLY=0;DATACARDONLY=0;;
--superloop) SUPERLOOP=$2 ; shift;;
--continueLoop) COUNTER=$2; CONTINUELOOP=1 ; shift;;
--intLumi) INTLUMI=$2; echo " test $INTLUMI" ;shift ;;
--isData) ISDATA=1;; 
--verbose) VERBOSE=1;; 
--isFakeData) ISDATA=0;; 
--unblind) UNBLIND=1;;

(--) shift; break;;
(-*) usage; echo "$0: error - unrecognized option $1" 1>&2; usage >> /dev/stderr; exit 1;;
(*) break;;
esac
shift
done

if (($VERBOSE==1)) ; then echo "[INFO] SMEARS $SMEARS" ;fi
if (($VERBOSE==1)) ; then echo "[INFO] SCALES $SCALES" ;fi

if [[ $BATCH == "IC" ]]; then
DEFAULTQUEUE=hepshort.q
#DEFAULTQUEUE=hepmedium.q
BATCHOPTION=" --batch $BATCH"
fi
if [[ $BATCH == "LSF" ]]; then
DEFAULTQUEUE=1nh
#DEFAULTQUEUE=hepmedium.q
BATCHOPTION=" --batch $BATCH"
fi

echo "[INFO] INTLUMI $INTLUMI"

OUTDIR="outdir_${EXT}"

echo "[INFO] outdir is $OUTDIR" 

####################################################
##################### SIGNAL #######################
####################################################

if [ $CONTINUELOOP == 0 ]; then
if [ $SIGONLY == 1 ]; then

echo "------------------------------------------------"
echo "------------>> Running SIGNAL"
echo "------------------------------------------------"

cd Signal
echo "./runSignalScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT --intLumi $INTLUMI $BATCHOPTION"
./runSignalScripts.sh -i $FILE -p $PROCS -f $CATS --ext $EXT --intLumi $INTLUMI $BATCHOPTION --smears $SMEARS --scales $SCALES
cd -
if [ $USER == lcorpe ]; then
echo " Processing of the Signal model for final fit exercice $EXT is done, see output here: https://lcorpe.web.cern.ch/lcorpe/$OUTDIR/ " |  mail -s "FINAL FITS: $EXT " lc1113@imperial.ac.uk
fi
fi
fi

##Signal script only need to be run once, outside of superloop
while [ $COUNTER -lt $SUPERLOOP ]; do
echo "[INFO] on loop number $COUNTER/$SUPERLOOP"



####################################################
################## BACKGROUND  ###################
####################################################
if [ $BKGONLY == 1 ]; then

echo "------------------------------------------------"
echo "-------------> Running BACKGROUND"
echo "------------------------------------------------"
if [ $UNBLIND == 1 ]; then
BLINDINGOPT=" --unblind"
fi
if [ $ISDATA == 1 ]; then
DATAOPT=" --isData"
DATAFILEOPT=" -i $DATAFILE"
else
PSEUDODATAOPT="  --pseudoDataDat $PSEUDODATADAT"
fi

SIGFILES=$PWD/Signal/$OUTDIR/CMS-HGG_sigfit_${EXT}.root

cd Background
echo "./runBackgroundScripts.sh -p $PROCS -f $CATS --ext $EXT --sigFile $SIGFILES --seed $COUNTER --intLumi $INTLUMI $BLINDINGOPT $PSEUDODATAOPT $DATAOPT $DATAFILEOPT $BATCHOPTION "
./runBackgroundScripts.sh -p $PROCS -f $CATS --ext $EXT --sigFile $SIGFILES --seed $COUNTER --intLumi $INTLUMI $BLINDINGOPT $PSEUDODATAOPT $DATAOPT $DATAFILEOPT $BATCHOPTION

cd -
if [ $USER == lcorpe ]; then
echo " Processing of the Background model for final fit exercice $EXT is done, see output here: https://lcorpe.web.cern.ch/lcorpe/$OUTDIR/ " |  mail -s "FINAL FITS: $EXT " lc1113@imperial.ac.uk
fi
fi

####################################################
################### DATCACARD  #####################
####################################################

if [ $DATACARDONLY == 1 ]; then

echo "------------------------------------------------"
echo "------------> Create DATACARD"
echo "------------------------------------------------"

cd Datacard
echo "./makeParametricModelDatacardFLASHgg.py -i $FILE  -o Datacard_13TeV_${EXT}.txt -p $PROCS -c UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1,TTHHadronicTag,TTHLeptonicTag --photonCatScales $SCALES --photonCatSmears $SMEARS --isMultiPdf --mass 125 --theoryNormFactors norm_factors.py #--submitSelf #--intLumi $INTLUMI"
./makeParametricModelDatacardFLASHgg.py -i $FILE  -o Datacard_13TeV_${EXT}.txt -p $PROCS -c UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1,TTHHadronicTag,TTHLeptonicTag --photonCatScales $SCALES --photonCatSmears $SMEARS --isMultiPdf --mass 125 --theoryNormFactors norm_factors.py #--submitSelf #--intLumi $INTLUMI
cd -
fi

####################################################
##################### COMBINE  #####################
####################################################

if [ $COMBINEONLY == 1 ]; then

echo "------------------------------------------------"
echo "------------> Create COMBINE"
echo "------------------------------------------------"

if [ $ISDATA == 0 ]; then
FAKE="_FAKE"
fi

cd Plots/FinalResults
ls ../../Signal/$OUTDIR/CMS-HGG_*sigfit*oot  > tmp.txt
while read p;
do
q=$(basename $p)
cp $p ${q/$EXT/mva} 
echo " cp $p ${q/$EXT/mva} "
done < tmp.txt
cp ../../Signal/$OUTDIR/CMS-HGG_sigfit_${EXT}.root CMS-HGG_mva_13TeV_sigfit.root
cp ../../Background/CMS-HGG_multipdf_${EXT}${FAKE}.root CMS-HGG_mva_13TeV_multipdf${FAKE}.root
cp ../../Datacard/Datacard_13TeV_$EXT.txt CMS-HGG_mva_13TeV_datacard.txt

cp combineHarvesterOptions13TeV_Template${FAKE}.dat combineHarvesterOptions13TeV_${EXT}${FAKE}.dat
cp allPlots_Template${FAKE}.sh allPlots_${EXT}${FAKE}.sh
chmod +x  allPlots_${EXT}${FAKE}.sh
sed -i -e "s/\!EXT\!/$EXT/g" combineHarvesterOptions13TeV_${EXT}${FAKE}.dat 
sed -i -e "s/\!EXT\!/$EXT/g" allPlots_${EXT}${FAKE}.sh 
sed -i -e "s/\!FAKE\!/$FAKE/g" combineHarvesterOptions13TeV_${EXT}${FAKE}.dat
echo "Adding _FAKE  ($FAKE) t multipdf if ISDATA == $ISDATA"
sed -i -e "s/multipdf.root/multipdf${FAKE}.root/g" CMS-HGG_mva_13TeV_datacard.txt 
#INTLUMI="2.7"
sed -i -e "s/\!INTLUMI\!/$INTLUMI/g" combineHarvesterOptions13TeV_${EXT}${FAKE}.dat 

cp combinePlotsOptions_Template${FAKE}.dat combinePlotsOptions_${EXT}${FAKE}.dat
sed -i -e "s/\!EXT\!/$EXT/g" combinePlotsOptions_${EXT}${FAKE}.dat
sed -i -e "s/\!INTLUMI\!/$INTLUMI/g" combinePlotsOptions_${EXT}${FAKE}.dat


if [ $COMBINEPLOTSONLY == 0 ]; then
echo "./combineHarvester.py -d combineHarvesterOptions13TeV_$EXT.dat -q $DEFAULTQUEUE --batch $BATCH --verbose"
./combineHarvester.py -d combineHarvesterOptions13TeV_${EXT}${FAKE}.dat -q $DEFAULTQUEUE --batch $BATCH --verbose #--S0

JOBS=999
RUN=999
PEND=999
FAIL=999
DONE=999

while (( $RUN > 0 ));do
JOBS=`find combineJobs13TeV_$EXT/   -name "*.sh" | wc -l`
#echo "JOBS=`find combineJobs13TeV_$EXT/ -name "*.sh" | wc -l`"
DONE=`find combineJobs13TeV_$EXT/   -name "*.sh.done" | wc -l`
FAIL=`find combineJobs13TeV_$EXT/   -name "*.sh.fail" | wc -l`
((RUN=$JOBS-$DONE-$FAIL-1))
echo "RUN=$RUN"
echo "JOBS=$JOBS"
echo "DONE=$DONE"
echo "FAIL=$FAIL"
sleep 10

echo "[INFO] Processing $JOBS jobs: PEND $PEND, RUN $RUN, FAIL $FAIL"
done

echo "[INFO] ------> All jobs done"
fi
./combineHarvester.py --hadd combineJobs13TeV_$EXT

LEDGER=" --it $COUNTER --itLedger itLedger_$EXT.txt"

#./makeCombinePlots.py -f combineJobs13TeV_pilottest090915/Asymptotic/Asymptotic.root --limit -b
#./makeCombinePlots.py -f combineJobs13TeV_pilottest090915/ExpProfileLikelihood/ExpProfileLikelihood.root --pval -b
echo INTLUMI = "$INTLUMI"
echo "./makeCombinePlots.py -d combinePlotsOptions_${EXT}${FAKE}.dat -b $LEDGER "
./makeCombinePlots.py -d combinePlotsOptions_$EXT${FAKE}.dat -b $LEDGER
./allPlots_${EXT}${FAKE}.sh
#./makeCombinePlots.py -f combineJobs13TeV_$EXT/MuScanFloatMH/MuScanFloatMH.root --mu -t "#sqrt{s}\=13TeV L\=$INTLUMI fb^{-1}" -o muFloatMH -b $LEDGER #for some reason doesn't work in datfile
#./makeCombinePlots.py -f combineJobs13TeV_$EXT/MuScanFixMH/MuScanFixMH.root --mu -t "#sqrt{s}\=13TeV L\=$INTLUMI fb^{-1}" -o muFixMH -b $LEDGER #for some reason doesn't work in datfile
#./makeCombinePlots.py -f combineJobs13TeV_$EXT/RVRFScan/RVRFScan.root --rvrf -t "#sqrt{s}\=13TeV L\=$INTLUMI fb^{-1}" -o RVRF --xbinning 30,-1.5,2.5 --ybinning 30,-3,8 -b $LEDGER #
#./makeCombinePlots.py -f combineJobs13TeV_$EXT/RVRFScanFloatMH/RVRFScanFloatMH.root --rvrf -t "#sqrt{s}\=13TeV L\=$INTLUMI fb^{-1}" -o RVRFScanFloatMH --xbinning 30,-1.5,2.5 --ybinning 30,-3,8 -b $LEDGER #
#./makeCombinePlots.py -f combineJobs13TeV_$EXT/RVRFScanFixMH/RVRFScanFixMH.root --rvrf -t "#sqrt{s}\=13TeV L\=$INTLUMI fb^{-1}" -o RVRFScanFixMH --xbinning 30,-1.5,2.5 --ybinning 30,-3,8 -b $LEDGER #

mkdir -p $OUTDIR/combinePlots
cp *pdf $OUTDIR/combinePlots/.
cp *png $OUTDIR/combinePlots/.
#rm *pdf
#rm *png

if [ $USER == "lcorpe" ]; then
cp -r $OUTDIR ~/www/${OUTDIR}
cp -r $OUTDIR ~/www/${OUTDIR}_${COUNTER}
cp ~lcorpe/public/index.php ~/www/$OUTDIR/combinePlots/.
cp ~lcorpe/public/index.php ~/www/${OUTDIR}_${COUNTER}/combinePlots/.
echo "plots available at: "
echo "https://lcorpe.web.cern.ch/lcorpe/$OUTDIR"
echo "or https://lcorpe.web.cern.ch/lcorpe/${OUTDIR}_${COUNTER}"
fi
if [ $USER == "lc1113" ]; then
cp -r $OUTDIR ~lc1113/public_html/
cp -r $OUTDIR ~lc1113/public_html/${OUTDIR}_${COUNTER}
cp ~lc1113/index.php ~lc1113/public_html/$OUTDIR/combinePlots/.
cp ~lc1113/index.php ~lc1113/public_html/${OUTDIR}_$COUNTER/combinePlots/.
echo "plots available at: "
echo "http://www.hep.ph.imperial.ac.uk/~lc1113/$OUTDIR"
echo "or http://www.hep.ph.imperial.ac.uk/~lc1113/${OUTDIR}_${COUNTER}"

fi
cd -
fi

if [ $USER == xlcorpe ] || [ $USER == lc1113 ]; then
echo " All stages of the final fit exercice $EXT  are done, see output here: https://lcorpe.web.cern.ch/lcorpe/$OUTDIR/  or  http://www.hep.ph.imperial.ac.uk/~lc1113/$OUTDIR " |  mail -s "FINAL FITS: $EXT " lc1113@imperial.ac.uk
fi

echo "signal output at Signal/$OUTDIR"
echo "background output at Background/$OUTDIR"
echo "combine output at Plots/FinalResuls/$OUTDIR"


COUNTER=$[COUNTER + 1]
done

