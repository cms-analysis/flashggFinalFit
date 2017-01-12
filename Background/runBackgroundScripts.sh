#!/bin/bash

#bash variables
FILE="";
EXT="auto"; #extensiom for all folders and files created by this script
PROCS="ggh"
CATS="UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,UntaggedTag_4,VBFTag_0,VBFTag_1,VBFTag_2,VHHadronicTag,VHTightTag,VHLooseTag"
SCALES="HighR9EE,LowR9EE,HighR9EB,LowR9EB"
SMEARS="HighR9EE,LowR9EE,HighR9EB,LowR9EB" #DRY RUN
FTESTONLY=0
PSEUDODATAONLY=0
PSEUDODATADAT=""
SIGFILE=""
BKGPLOTSONLY=0
SEED=0
INTLUMI=1
ISDATA=0
UNBLIND=0

usage(){
	echo "The script runs background scripts:"
		echo "options:"

echo "-h|--help)"
echo "-i|--inputFile)"
echo "-p|--procs ) (default= ggh)"
echo "-f|--flashggCats) (default= UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,UntaggedTag_4,VBFTag_0,VBFTag_1,VBFTag_2,TTHHadronicTag,TTHLeptonicTag,VHHadronicTag,VHTightTag,VHLooseTag,VHEtTag)"
echo "--ext)  (default= auto)"
echo "--fTestOnly) "
echo "--pseudoDataOnly) "
echo "--pseudoDataDat)"
echo "--sigFile) "
echo "--bkgPlotsOnly)"
echo "--seed) for pseudodata random number gen seed (default $SEED)"
echo "--intLumi) specified in fb^-{1} (default $INTLUMI)) "
echo "--isData) specified in fb^-{1} (default $DATA)) "
echo "--unblind) specified in fb^-{1} (default $UNBLIND)) "
		echo "--batch) which batch system to use (None (''),LSF,IC) (default '$BATCH')) "
}


#------------------------------ parsing


# options may be followed by one colon to indicate they have a required argument
if ! options=$(getopt -u -o hi:p:f: -l help,inputFile:,procs:,flashggCats:,ext:,fTestOnly,pseudoDataOnly,bkgPlotsOnly,pseudoDataDat:,sigFile:,seed:,intLumi:,unblind,isData,batch: -- "$@")
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
-f|--flashggCats) CATS=$2; shift ;;
--ext) EXT=$2; echo "test" ; shift ;;
--fTestOnly) FTESTONLY=1; echo "ftest" ;;
--pseudoDataOnly) PSEUDODATAONLY=1;;
--pseudoDataDat) PSEUDODATADAT=$2; shift;;
--sigFile) SIGFILE=$2; shift;;
--bkgPlotsOnly) BKGPLOTSONLY=1;;
--seed) SEED=$2; shift;;
--intLumi) INTLUMI=$2; shift;;
--isData) ISDATA=1;;
--unblind) UNBLIND=1;;
--batch) BATCH=$2; shift;;

(--) shift; break;;
(-*) usage; echo "$0: error - unrecognized option $1" 1>&2; usage >> /dev/stderr; exit 1;;
(*) break;;
esac
shift
done


OUTDIR="outdir_${EXT}"
echo "[INFO] outdir is $OUTDIR, INTLUMI $INTLUMI" 

if [ $ISDATA == 1 ]; then
DATAEXT="-Data"
fi
echo "INTLUMI is $intLumi"
OUTDIR="outdir_${EXT}"

mkdir -p $OUTDIR

if [ $FTESTONLY == 0 -a $PSEUDODATAONLY == 0 -a $BKGPLOTSONLY == 0 ]; then
#IF not particular script specified, run all!
FTESTONLY=1
PSEUDODATAONLY=1
BKGPLOTSONLY=1
fi

if [[ $BATCH == "IC" ]]; then
#DEFAULTQUEUE="hep.q -l h_rt=0:20:0"
DEFAULTQUEUE="hep.q"
BATCHQUERY=qstat
fi
if [[ $BATCH == "LSF" ]]; then
DEFAULTQUEUE=1nh
BATCHQUERY=bjobs
fi

####################################################
################## PSEUDODATAONLY ###################
####################################################

if [ $PSEUDODATAONLY == 1 ] && [ $ISDATA == 0 ]; then

mkdir -p $OUTDIR/pseudoData

echo "--------------------------------------"
echo "Running Pseudodata"
echo "--> Create fake data by fitting simulations, throwing toys and adding datasets"
echo "--> generating $INTLUMI fb^{-1} of pseudodata."
echo "--------------------------------------"

echo " ./bin/pseudodataMaker -i $PSEUDODATADAT --pseudodata 1 --plotdir $OUTDIR/pseudoData -f $CATS --seed $SEED --intLumi $INTLUMI "
./bin/pseudodataMaker -i $PSEUDODATADAT --pseudodata 1 --plotdir $OUTDIR/pseudoData -f $CATS --seed $SEED --intLumi $INTLUMI  -y $OUTDIR/pseudoData/yields_pseudodata.txt
FILE=$OUTDIR/pseudoData/pseudoWS.root

fi

####################################################
################## F-TEST ###################
####################################################
if [ $FTESTONLY == 1 ]; then

echo "--------------------------------------"
echo "Running Background F-Test"
echo "-->Greate background model"
echo "--------------------------------------"
if [ $UNBLIND == 1 ]; then
OPT=" --unblind"
fi
if [ $ISDATA == 0 ]; then
FILE=$OUTDIR/pseudoData/pseudoWS.root
fi
if [ $ISDATA == 1 ]; then
OPT=" --isData 1"
fi

echo " ./bin/fTest -i $FILE --saveMultiPdf CMS-HGG_multipdf_$EXT.root  -D $OUTDIR/bkgfTest$DATAEXT -f $CATS $OPT"
./bin/fTest -i $FILE --saveMultiPdf CMS-HGG_multipdf_$EXT.root  -D $OUTDIR/bkgfTest$DATAEXT -f $CATS $OPT

OPT=""
fi

####################################################
################### BKGPLOTS ###################
####################################################

if [ $BKGPLOTSONLY == 1 ]; then
echo "--------------------------------------"
echo "-->Create Background Validation plots"
echo "--------------------------------------"

if [ "$SIGFILE" != "" ]; then
SIG="-s $SIGFILE"
fi
if [ $UNBLIND == 1 ]; then
OPT=" --unblind"
fi
echo "./scripts/subBkgPlots.py -b CMS-HGG_multipdf_$EXT.root -d $OUTDIR/bkgPlots$DATAEXT -S 13 --isMultiPdf --useBinnedData  --doBands --massStep 1 $SIG -L 100 -H 180 -f $CATS -l $CATS --intLumi $INTLUMI $OPT --batch $BATCH -q $DEFAULTQUEUE "
./scripts/subBkgPlots.py -b CMS-HGG_multipdf_$EXT.root -d $OUTDIR/bkgPlots$DATAEXT -S 13 --isMultiPdf --useBinnedData  --doBands  --massStep 1 $SIG -L 100 -H 180 -f $CATS -l $CATS --intLumi $INTLUMI $OPT --batch $BATCH -q $DEFAULTQUEUE
continueLoop=1
while (($continueLoop==1))
do
 sleep 10
 $BATCHQUERY
 $BATCHQUERY >qstat_out.txt
 ((number=`cat qstat_out.txt | wc -l `))
 echo $number
  if (($number==0)) ; then
     ((continueLoop=0))
  fi
done 

OPT=""
fi


if [ $USER == "lcorpe" ]; then
cp -r ${OUTDIR} ~/www/${OUTDIR}_${SEED}
cp -r $OUTDIR ~/www/.
cp ~lcorpe/public/index.php ~/www/$OUTDIR/pseudoData/.
cp ~lcorpe/public/index.php ~/www/$OUTDIR/bkgPlots/.
cp ~lcorpe/public/index.php ~/www/$OUTDIR/bkgPlot$DATAEXT/.
cp ~lcorpe/public/index.php ~/www/$OUTDIR/bkgfTest$DATAEXT/.
cp ~lcorpe/public/index.php ~/www/$OUTDIR/bkgfTest/.
cp ~lcorpe/public/index.php ~/www/${OUTDIR}_${SEED}/pseudoData/.
cp ~lcorpe/public/index.php ~/www/${OUTDIR}_${SEED}/bkgPlots/.
cp ~lcorpe/public/index.php ~/www/${OUTDIR}_${SEED}/bkgfTest/.

echo "plots available at: "
echo "https://lcorpe.web.cern.ch/lcorpe/$OUTDIR_${SEED}"

fi

if [ $USER == "lc1113" ]; then
cp -r ${OUTDIR} ~lc1113/public_html/${OUTDIR}_${SEED}
cp ~lc1113/index.php ~lc1113/public_html/${OUTDIR}_${SEED}/pseudoData/.
cp ~lc1113/index.php ~lc1113/public_html/${OUTDIR}_${SEED}/bkgPlots/.
cp ~lc1113/index.php ~lc1113/public_html/${OUTDIR}_${SEED}/bkgfTest/.
cp -r $OUTDIR ~lc1113/public_html/.
cp ~lc1113/index.php ~lc1113/public_html/$OUTDIR/pseudoData/.
cp ~lc1113/index.php ~lc1113/public_html/$OUTDIR/bkgPlots/.
cp ~lc1113/index.php ~lc1113/public_html/$OUTDIR/bkgfTest/.
cp ~lc1113/index.php ~lc1113/public_html/$OUTDIR/bkgPlots$DATAEXT/.
cp ~lc1113/index.php ~lc1113/public_html/$OUTDIR/bkgfTest$DATAEXT/
echo "plots available at: "
echo "http://www.hep.ph.imperial.ac.uk/~lc1113/${OUTDIR}_${SEED}"
fi
