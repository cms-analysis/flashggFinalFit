#!/bin/bash

#bash variables
FILE="";
EXT="auto"; #extensiom for all folders and files created by this script
PROCS="ggh"
CATS="UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,UntaggedTag_4,VBFTag_0,VBFTag_1,VBFTag_2"
SCALES="HighR9EE,LowR9EE,HighR9EB,LowR9EB"
SMEARS="HighR9EE,LowR9EE,HighR9EB,LowR9EB" #DRY RUN
FTESTONLY=0
CALCPHOSYSTONLY=0
SIGFITONLY=0
SIGPLOTSONLY=0
INTLUMI=1
BATCH=""
DEFAULTQUEUE=""

usage(){
	echo "The script runs three signal scripts in this order:"
		echo "signalFTest --> determines number of gaussians to use for fits of each Tag/Process"
		echo "calcPhotonSystConsts --> scale and smear ets of photons systematic variations"
		echo "SignalFit --> actually determine the number of gaussians to fit"
		echo "options:"
		echo "-h|--help) "
		echo "-i|--inputFile) "
		echo "-p|--procs) "
		echo "-f|--flashggCats) (default UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,UntaggedTag_4,VBFTag_0,VBFTag_1,VBFTag_2,TTHHadronicTag,TTHLeptonicTag,VHHadronicTag,VHTightTag,VHLooseTag,VHEtTag)"
		echo "--ext)  (default auto)"
		echo "--fTestOnly) "
		echo "--calcPhoSystOnly) "
		echo "--sigFitOnly) "
		echo "--sigPlotsOnly) "
		echo "--intLumi) specified in fb^-{1} (default $INTLUMI)) "
		echo "--batch) which batch system to use (None (''),LSF,IC) (default '$BATCH')) "
}


#------------------------------ parsing


# options may be followed by one colon to indicate they have a required argument
if ! options=$(getopt -u -o hi:p:f: -l help,inputFile:,procs:,smears:,scales:,flashggCats:,ext:,fTestOnly,calcPhoSystOnly,sigFitOnly,sigPlotsOnly,intLumi:,batch: -- "$@")
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
--smears) SMEARS=$2; shift ;;
--scales) SCALES=$2; shift ;;
-f|--flashggCats) CATS=$2; shift ;;
--ext) EXT=$2; echo "test" ; shift ;;
--fTestOnly) FTESTONLY=1; echo "ftest" ;;
--calcPhoSystOnly) CALCPHOSYSTONLY=1;;
--sigFitOnly) SIGFITONLY=1;;
--sigPlotsOnly) SIGPLOTSONLY=1;;
--intLumi) INTLUMI=$2; shift ;;
--batch) BATCH=$2; shift;;

(--) shift; break;;
(-*) usage; echo "$0: error - unrecognized option $1" 1>&2; usage >> /dev/stderr; exit 1;;
(*) break;;
esac
shift
done

echo "INTLUMI $INTLUMI"

OUTDIR="outdir_$EXT"
echo "[INFO] outdir is $OUTDIR" 
if [[ $FILE == "" ]];then
echo "ERROR, input file (--inputFile or -i) is mandatory!"
exit 0
fi

if [ $FTESTONLY == 0 -a $CALCPHOSYSTONLY == 0 -a $SIGFITONLY == 0 -a $SIGPLOTSONLY == 0 ]; then
#IF not particular script specified, run all!
FTESTONLY=1
CALCPHOSYSTONLY=1
SIGFITONLY=1
SIGPLOTSONLY=1
fi

if [[ $BATCH == "IC" ]]; then
DEFAULTQUEUE=hepshort.q
fi
if [[ $BATCH == "LSF" ]]; then
DEFAULTQUEUE=1nh
fi
####################################################
################## SIGNAL F-TEST ###################
####################################################
#ls dat/newConfig_${EXT}.dat
if [ -e dat/newConfig_${EXT}.dat ]; then
  echo "[INFO] sigFTest dat file $OUTDIR/dat/copy_newConfig_${EXT}.dat already exists, so SKIPPING SIGNAL FTEST"
else
  if [ $FTESTONLY == 1 ]; then
    mkdir -p $OUTDIR/fTest
    echo "=============================="
    echo "Running Signal F-Test"
    echo "-->Determine Number of gaussians"
    echo "=============================="
    if [ -z $BATCH ]; then
      echo "./bin/signalFTest -i $FILE -d dat/newConfig_$EXT.dat -p $PROCS -f $CATS -o $OUTDIR"
      ./bin/signalFTest -i $FILE -d dat/newConfig_$EXT.dat -p $PROCS -f $CATS -o $OUTDIR
    else
      echo "./python/submitSignaFTest.py --procs $PROCS --flashggCats $CATS --outDir $OUTDIR --i $FILE --batch $BATCH -q $DEFAULTQUEUE"
       ./python/submitSignaFTest.py --procs $PROCS --flashggCats $CATS --outDir $OUTDIR --i $FILE --batch $BATCH -q $DEFAULTQUEUE

      PEND=`ls -l $OUTDIR/fTestJobs/sub*| grep -v "\.run" | grep -v "\.done" | grep -v "\.fail" | grep -v "\.err" |grep -v "\.log"  |wc -l`
      echo "PEND $PEND"
      while (( $PEND > 0 )) ; do
        PEND=`ls -l $OUTDIR/fTestJobs/sub* | grep -v "\.run" | grep -v "\.done" | grep -v "\.fail" | grep -v "\.err" | grep -v "\.log" |wc -l`
        RUN=`ls -l $OUTDIR/fTestJobs/sub* | grep "\.run" |wc -l`
        FAIL=`ls -l $OUTDIR/fTestJobs/sub* | grep "\.fail" |wc -l`
        DONE=`ls -l $OUTDIR/fTestJobs/sub* | grep "\.done" |wc -l`
        (( PEND=$PEND-$RUN-$FAIL-$DONE ))
        echo " PEND $PEND - RUN $RUN - DONE $DONE - FAIL $FAIL"
        if (( $RUN > 0 )) ; then PEND=1 ; fi
        if (( $FAIL > 0 )) ; then 
          echo "ERROR at least one job failed :"
          ls -l $OUTDIR/fTestJobs/sub* | grep "\.fail"
          exit 1
        fi
        sleep 10
      done
    fi
    mkdir -p $OUTDIR/dat
    cat $OUTDIR/fTestJobs/outputs/* > dat/newConfig_${EXT}_temp.dat
    sort -u dat/newConfig_${EXT}_temp.dat  > dat/tmp_newConfig_${EXT}_temp.dat 
    mv dat/tmp_newConfig_${EXT}_temp.dat dat/newConfig_${EXT}_temp.dat
    cp dat/newConfig_${EXT}_temp.dat $OUTDIR/dat/copy_newConfig_${EXT}_temp.dat
    rm -rf $OUTDIR/sigfTest
    mv $OUTDIR/fTest $OUTDIR/sigfTest
  fi
  echo "[INFO] sigFTest jobs completed, check output and do:"
  echo "cp $PWD/dat/newConfig_${EXT}_temp.dat $PWD/dat/newConfig_${EXT}.dat"
  echo "and manually amend chosen number of gaussians using the output pdfs here:"
	echo "Signal/outdir_${EXT}/sigfTest/"
  echo "then re-run the same command to continue !"
  CALCPHOSYSTONLY=0
  SIGFITONLY=0
  SIGPLOTSONLY=0
	exit 1
fi
####################################################
################## CALCPHOSYSTCONSTS ###################
####################################################

if [ $CALCPHOSYSTONLY == 1 ]; then

  echo "=============================="
  echo "Running calcPho"
  echo "-->Determine effect of photon systematics"
  echo "=============================="

  echo "./bin/calcPhotonSystConsts -i $FILE -o dat/photonCatSyst_$EXT.dat -p $PROCS -s $SCALES -r $SMEARS -D $OUTDIR -f $CATS"
  ./bin/calcPhotonSystConsts -i $FILE -o dat/photonCatSyst_$EXT.dat -p $PROCS -s $SCALES -r $SMEARS -D $OUTDIR -f $CATS 
  cp dat/photonCatSyst_$EXT.dat $OUTDIR/dat/copy_photonCatSyst_$EXT.dat
fi
####################################################
####################### SIGFIT #####################
####################################################
if [ $SIGFITONLY == 1 ]; then

  echo "=============================="
  echo "Running SignalFit"
  echo "-->Create actual signal model"
  echo "=============================="


  if [[ $BATCH == "" ]]; then
    echo "./bin/SignalFit -i $FILE -d dat/newConfig_$EXT.dat  --mhLow=120 --mhHigh=130 -s dat/photonCatSyst_$EXT.dat --procs $PROCS -o $OUTDIR/CMS-HGG_mva_13TeV_sigfit.root -p $OUTDIR/sigfit -f $CATS --changeIntLumi $INTLUMI "
    ./bin/SignalFit -i $FILE -d dat/newConfig_$EXT.dat  --mhLow=120 --mhHigh=130 -s dat/photonCatSyst_$EXT.dat --procs $PROCS -o $OUTDIR/CMS-HGG_mva_13TeV_sigfit.root -p $OUTDIR/sigfit -f $CATS --changeIntLumi $INTLUMI #--pdfWeights 26
  else
    echo " ./python/submitSignalFit.py -i $FILE -d dat/newConfig_$EXT.dat  --mhLow=120 --mhHigh=130 -s dat/photonCatSyst_$EXT.dat --procs $PROCS -o $OUTDIR/CMS-HGG_sigfit_$EXT.root -p $OUTDIR/sigfit -f $CATS --changeIntLumi $INTLUMI --batch $BATCH -q $DEFAULTQUEUE "
    ./python/submitSignalFit.py -i $FILE -d dat/newConfig_$EXT.dat  --mhLow=120 --mhHigh=130 -s dat/photonCatSyst_$EXT.dat --procs $PROCS -o $OUTDIR/CMS-HGG_sigfit_$EXT.root -p $OUTDIR/sigfit -f $CATS --changeIntLumi $INTLUMI --batch $BATCH -q $DEFAULTQUEUE

    PEND=`ls -l $OUTDIR/sigfit/SignalFitJobs/sub*| grep -v "\.run" | grep -v "\.done" | grep -v "\.fail" | grep -v "\.err" |grep -v "\.log"  |wc -l`
    echo "PEND $PEND"
    while (( $PEND > 0 )) ;do
      PEND=`ls -l $OUTDIR/sigfit/SignalFitJobs/sub* | grep -v "\.run" | grep -v "\.done" | grep -v "\.fail" | grep -v "\.err" | grep -v "\.log" |wc -l`
      RUN=`ls -l $OUTDIR/sigfit/SignalFitJobs/sub* | grep "\.run" |wc -l`
      FAIL=`ls -l $OUTDIR/sigfit/SignalFitJobs/sub* | grep "\.fail" |wc -l`
      DONE=`ls -l $OUTDIR/sigfit/SignalFitJobs/sub* | grep "\.done" |wc -l`
      (( PEND=$PEND-$RUN-$FAIL-$DONE ))
      echo " PEND $PEND - RUN $RUN - DONE $DONE - FAIL $FAIL"
      if (( $RUN > 0 )) ; then PEND=1 ; fi
      if (( $FAIL > 0 )) ; then 
        echo "ERROR at least one job failed :"
        ls -l $OUTDIR/sigfit/SignalFitJobs/sub* | grep "\.fail"
        exit 1
      fi
      sleep 10
  
    done

    ls $PWD/$OUTDIR/CMS-HGG_sigfit_${EXT}_*.root > out.txt
    echo "ls ../Signal/$OUTDIR/CMS-HGG_sigfit_${EXT}_*.root > out.txt"
    counter=0
    while read p ; do
      if (($counter==0)); then
        SIGFILES="$p"
      else
        SIGFILES="$SIGFILES,$p"
      fi
      ((counter=$counter+1))
    done < out.txt
    echo "SIGFILES $SIGFILES"
    echo "./bin/PackageOutput -i $SIGFILES --procs $PROCS -l $INTLUMI -p $OUTDIR/sigfit -W wsig_13TeV -f $CATS -L 120 -H 130 -o $OUTDIR/CMS-HGG_sigfit_$EXT.root"
    ./bin/PackageOutput -i $SIGFILES --procs $PROCS -l $INTLUMI -p $OUTDIR/sigfit -W wsig_13TeV -f $CATS -L 120 -H 130 -o $OUTDIR/CMS-HGG_sigfit_$EXT.root > package.out
  fi

fi


#####################################################
#################### SIGNAL PLOTS ###################
#####################################################

if [ $SIGPLOTSONLY == 1 ]; then

echo "=============================="
echo "Make Signal Plots"
echo "-->Create Validation plots"
echo "=============================="

echo " ./bin/makeParametricSignalModelPlots -i $OUTDIR/CMS-HGG_sigfit_$EXT.root  -o $OUTDIR -p $PROCS -f $CATS"
#./bin/makeParametricSignalModelPlots -i $OUTDIR/CMS-HGG_sigfit_$EXT.root  -o $OUTDIR/sigplots -p $PROCS -f $CATS 
./bin/makeParametricSignalModelPlots -i $OUTDIR/CMS-HGG_sigfit_$EXT.root  -o $OUTDIR/sigplots -p $PROCS -f $CATS > signumbers.txt
#mv $OUTDIR/sigfit/initialFits $OUTDIR/initialFits

fi

if [ $USER == "lcorpe" ]; then
cp -r $OUTDIR ~/www/.
cp ~lcorpe/public/index.php ~/www/$OUTDIR/sigplots/.
cp ~lcorpe/public/index.php ~/www/$OUTDIR/systematics/.
cp ~lcorpe/public/index.php ~/www/$OUTDIR/sigfit/.
cp ~lcorpe/public/index.php ~/www/$OUTDIR/sigfTest/.

echo "plots available at: "
echo "https://lcorpe.web.cern.ch/lcorpe/$OUTDIR"

fi

if [ $USER == "lc1113" ]; then
cp -r $OUTDIR ~lc1113/public_html/.
cp ~lc1113/index.php ~lc1113/public_html/$OUTDIR/sigplots/.
cp ~lc1113/index.php ~lc1113/public_html/$OUTDIR/systematics/.
cp ~lc1113/index.php ~lc1113/public_html/$OUTDIR/sigfit/.
cp ~lc1113/index.php ~lc1113/public_html/$OUTDIR/sigfTest/.
echo "plots available at: "
echo "http://www.hep.ph.imperial.ac.uk/~lc1113/$OUTDIR"
fi
