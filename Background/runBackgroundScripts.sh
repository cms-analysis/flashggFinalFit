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
BATCH=""
QUEUE=""
YEAR="2016"
CATOFFSET=0

usage(){
	echo "The script runs background scripts:"
		echo "options:"

echo "-h|--help)"
echo "-i|--inputFile)"
echo "-p|--procs ) (default= ggh)"
echo "-f|--flashggCats) (default= UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,UntaggedTag_4,VBFTag_0,VBFTag_1,VBFTag_2,TTHHadronicTag,TTHLeptonicTag,VHHadronicTag,VHTightTag,VHLooseTag,VHEtTag)"
echo "--ext)  (default= auto)"
echo "--catOffset) "
echo "--fTestOnly) "
echo "--pseudoDataOnly) "
echo "--pseudoDataDat)"
echo "--sigFile) "
echo "--bkgPlotsOnly)"
echo "--seed) for pseudodata random number gen seed (default $SEED)"
echo "--intLumi) specified in fb^-{1} (default $INTLUMI)) "
echo "--year) dataset year (default $YEAR)) "
echo "--isData) specified in fb^-{1} (default $DATA)) "
echo "--unblind) specified in fb^-{1} (default $UNBLIND)) "
echo "--batch) which batch system to use (None (''),HTCONDOR,IC) (default '$BATCH')) "
echo "--queue) queue to submit jobs to (specific to batch))"
}


#------------------------------ parsing


# options may be followed by one colon to indicate they have a required argument
if ! options=$(getopt -u -o hi:p:f: -l help,inputFile:,procs:,flashggCats:,ext:,catOffset:,fTestOnly,pseudoDataOnly,bkgPlotsOnly,pseudoDataDat:,sigFile:,seed:,intLumi:,year:,unblind,isData,batch:,queue: -- "$@")
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
--catOffset) CATOFFSET=$2; shift ;;
--fTestOnly) FTESTONLY=1; echo "ftest" ;;
--pseudoDataOnly) PSEUDODATAONLY=1;;
--pseudoDataDat) PSEUDODATADAT=$2; shift;;
--sigFile) SIGFILE=$2; shift;;
--bkgPlotsOnly) BKGPLOTSONLY=1;;
--seed) SEED=$2; shift;;
--intLumi) INTLUMI=$2; shift;;
--year) YEAR=$2; shift;;
--isData) ISDATA=1;;
--unblind) UNBLIND=1;;
--batch) BATCH=$2; shift;;
--queue) QUEUE=$2; shift;;

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
echo "INTLUMI is $INTLUMI, YEAR is $YEAR"
OUTDIR="outdir_${EXT}"

mkdir -p $OUTDIR

if [ $FTESTONLY == 0 -a $PSEUDODATAONLY == 0 -a $BKGPLOTSONLY == 0 ]; then
#IF not particular script specified, run all!
FTESTONLY=1
PSEUDODATAONLY=1
BKGPLOTSONLY=1
fi

if [[ $BATCH == "IC" ]]; then
BATCHQUERY=qstat
QUEUE="hep.q"
echo "[INFO] Batch = $BATCH, using QUEUE = $QUEUE"
fi
if [[ $BATCH == "HTCONDOR" ]]; then
  BATCHQUERY=condor_q
  if [[ $QUEUE == "" ]]; then
    QUEUE=espresso
    echo "[INFO] Batch = $BATCH, QUEUE not specified. Using QUEUE = $QUEUE"
  fi
  else
    echo "[INFO] Batch = $BATCH, Using QUEUE = $QUEUE"
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

echo " ./bin/fTest -i $FILE --saveMultiPdf $OUTDIR/CMS-HGG_multipdf_$EXT_$CATS.root  -D $OUTDIR/bkgfTest$DATAEXT -f $CATS $OPT --year $YEAR --catOffset $CATOFFSET"
./bin/fTest -i $FILE --saveMultiPdf $OUTDIR/CMS-HGG_multipdf_$EXT_$CATS.root  -D $OUTDIR/bkgfTest$DATAEXT -f $CATS $OPT --year $YEAR --catOffset $CATOFFSET

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
echo "./scripts/subBkgPlots.py -b CMS-HGG_multipdf_$EXT.root -d $OUTDIR/bkgPlots$DATAEXT -S 13 --isMultiPdf --useBinnedData  --doBands --massStep 1 $SIG -L 100 -H 180 -f $CATS -l $CATS --intLumi $INTLUMI $OPT --batch $BATCH -q $QUEUE --year $YEAR"
./scripts/subBkgPlots.py -b CMS-HGG_multipdf_$EXT.root -d $OUTDIR/bkgPlots$DATAEXT -S 13 --isMultiPdf --useBinnedData  --doBands  --massStep 1 $SIG -L 100 -H 180 -f $CATS -l $CATS --intLumi $INTLUMI $OPT --batch $BATCH -q $QUEUE --year $YEAR

# FIX THIS FOR CONDOR: 
#continueLoop=1
#while (($continueLoop==1))
#do
# sleep 10
# $BATCHQUERY
# $BATCHQUERY >qstat_out.txt
# ((number=`cat qstat_out.txt | wc -l `))
# echo $number
#  if (($number==0)) ; then
#     ((continueLoop=0))
#  fi
#done 

OPT=""
fi
