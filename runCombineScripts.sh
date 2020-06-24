#!/bin/bash
#bash variables
ANALYSIS=""
ANALYSIS_TYPE=""
HHWWGGCATLABEL="NotLabelled"
FILE="";
EXT="auto"; #extensiom for all folders and files created by this script
SHORTEXT="a"
PROCS="ggh"
CATS="UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,UntaggedTag_4,VBFTag_0,VBFTag_1,VBFTag_2,TTHHadronicTag,TTHLeptonicTag,VHHadronicTag,VHTightTag,VHLooseTag,VHEtTag"
#CATS="UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,UntaggedTag_4,VBFTag_0,VBFTag_1,VBFTag_2,TTHLeptonicTag,VHHadronicTag,VHTightTag,VHLooseTag"
#CATS="UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,UntaggedTag_4,VBFTag_0,VBFTag_1,VBFTag_2,VHHadronicTag,VHTightTag,VHLooseTag"
SCALES="HighR9EE,LowR9EE,HighR9EB,LowR9EB"
#SCALESCORR="MaterialCentral,MaterialForward,FNUFEE,FNUFEB,ShowerShapeHighR9EE,ShowerShapeHighR9EB,ShowerShapeLowR9EE,ShowerShapeLowR9EB"
SCALESCORR="MaterialCentral,MaterialForward"
#SCALESGLOBAL="NonLinearity:0:2.6"
SCALESGLOBAL="NonLinearity,Geant4,LightYield,Absolute"
SMEARS="HighR9EE,LowR9EE,HighR9EB,LowR9EB" #DRY RUN
MASSLIST="120,125,130" #DRY RUN
PSEUDODATADAT=""
SIGFILE=""
SIGONLY=1
BKGONLY=1
DATACARDONLY=1
COMBINEONLY=1
COMBINEPLOTSONLY=0
SIMULATENOUSMASSPOINTFITTING=0
USEDCBP1G=0
COUNTER=0
CONTINUELOOP=0
INTLUMI=1
YEAR=2016
DATAFILE=""
UNBLIND=0
ISDATA=0
BS=0
VERBOSE=0
BATCH="LSF"
DOSYSTEMATICS="1"
DEFAULTQUEUE="1nh"
UEPS="none"
NEWGGHSCHEME=0
DOSTXS=0
DOSTAGE1=0
usage(){
	echo "The script runs background scripts:"
		echo "options:"
echo "-h|--help)" 
echo "--analysis) (default $ANALYSIS)"
echo "--analysis_type) (default $ANALYSIS_TYPE)"
echo "--HHWWggCatLabel) (default $HHWWGGCATLABEL)"
echo "-i|--inputFile) "
echo "-p|--procs) (default $PROCS)"
echo "-f|--flashggCats) (default $CATS) "
echo "--uepsFile) (default $UEPS) "
echo "--newGghScheme) (default $NEWGGHSCHEME) "
echo "--doSTXS) (default $DOSTXS) "
echo "--doStage1) (default $DOSTAGE1) "
echo "--ext) (default $EXT)"
exho "--shortExt) (default $SHORTEXT)"
echo "--pseudoDataDat)"
echo "--combine) "
echo "--combineOnly) "
echo "--combinePlotsOnly) "
echo "--useDCB_1G) Use the functional form ofi a Double Crystal Ball + one Gaussian (same mean) (default $USEDCBP1G)"
echo "--useSSF) SSF = Simultaneous Signal Fitting. Do a fit where the mass points are all fitted at once where the parameters have MH dependence (default $SIMULATENOUSMASSPOINTFITTING)"
echo "--signalOnly)"
echo "--backgroundOnly) "
echo "--datacardOnly)"
echo "--continueLoop) specify which iteration to start loop at (default $COUNTER)"
echo "--intLumi) specified in fb^-{1} (default $INTLUMI)) "
echo "--year) dataset year (default $YEAR)) "
echo "--isData) ACTUAL DATA (default $DATA)) "
echo "--isFakeData) FAKE DATA (default 0)) "
echo "--unblind) specified in fb^-{1} (default $UNBLIND)) "
echo "--dataFile) specified in fb^-{1} (default $DATAFILE)) "
echo "--batch) which batch system to use (LSF,IC) (default $BATCH)) "
echo "--doSystematics) run with or without systematics (default $DOSYSTEMATICS)"
}


#------------------------------ parsing


# options may be followed by one colon to indicate they have a required argument
if ! options=$(getopt -u -o hi:p:f: -l help,inputFile:,procs:,bs:,flashggCats:,uepsFile:,newGghScheme,doSTXS,doStage1,ext:,smears:,massList:,scales:,scalesCorr:,scalesGlobal:,,pseudoDataDat:,sigFile:,combine,combineOnly,combinePlotsOnly,signalOnly,backgroundOnly,datacardOnly,useSSF:,useDCB_1G:,continueLoop:,intLumi:,year:,unblind,isData,isFakeData,analysis:,analysis_type:,HHWWggCatLabel:,shortExt:,dataFile:,batch:,doSystematics:,verbose -- "$@")
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
--scalesCorr) SCALESCORR=$2; shift ;;
--scalesGlobal) SCALESGLOBAL=$2; shift ;;
--smears) SMEARS=$2; shift ;;
--massList) MASSLIST=$2; shift ;;
-f|--flashggCats) CATS=$2; shift ;;
--uepsFile) UEPS=$2; shift ;;
--newGghScheme) NEWGGHSCHEME=1;;
--doSTXS) DOSTXS=1;;
--doStage1) DOSTAGE1=1;;
--ext) EXT=$2; echo "test ext $EXT " ; shift ;;
--pseudoDataDat) PSEUDODATADAT=$2; shift;;
--analysis) ANALYSIS=$2; shift;;
--analysis_type) ANALYSIS_TYPE=$2; shift;; 
--HHWWggCatLabel) HHWWGGCATLABEL=$2; shift;;
--shortExt) SHORTEXT=$2; echo "short ext $SHORTEXT"; shift ;;
--dataFile) DATAFILE=$2; shift;;
--batch) BATCH=$2; echo " BATCH $BATCH " ; shift;;
--doSystematics) DOSYSTEMATICS=$2; echo " DOSYSTEMATICS $DOSYSTEMATICS" ; shift;; 
--signalOnly) COMBINEONLY=0;BKGONLY=0;SIGONLY=1;DATACARDONLY=0;;
--backgroundOnly) COMBINEONLY=0;BKGONLY=1;SIGONLY=0;DATACARDONLY=0;;
--datacardOnly) COMBINEONLY=0;BKGONLY=0;SIGONLY=0;DATACARDONLY=1;;
--combine) COMBINEONLY=1;;#;BKGONLY=0;SIGONLY=0;DATACARDONLY=0;;
--combineOnly) COMBINEONLY=1;BKGONLY=0;SIGONLY=0;DATACARDONLY=0;;
--combinePlotsOnly) COMBINEPLOTSONLY=1;COMBINEONLY=0;BKGONLY=0;SIGONLY=0;DATACARDONLY=0;;
--useSSF) SIMULATENOUSMASSPOINTFITTING=$2 ; shift;;
--useDCB_1G) USEDCBP1G=$2 ; shift;;
--continueLoop) COUNTER=$2; CONTINUELOOP=1 ; shift;;
--intLumi) INTLUMI=$2; echo " test $INTLUMI" ;shift ;;
--year) YEAR=$2; shift ;;
--bs) BS=$2; echo " test BS $BS" ;shift ;;
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
echo "[INFO] MASSLIST is $MASSLIST"
if (($VERBOSE==1)) ; then echo "[INFO] SMEARS $SMEARS" ;fi
if (($VERBOSE==1)) ; then echo "[INFO] SCALES $SCALES" ;fi
if (($VERBOSE==1)) ; then echo "[INFO] SCALESORR $SCALESCORR" ;fi
if (($VERBOSE==1)) ; then echo "[INFO] SCALESGLOBAL $SCALESGLOBAL" ;fi

if [[ $BATCH == "IC" ]]; then
DEFAULTQUEUE="hep.q"
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
################### DATCACARD  #####################
####################################################

if [ $DATACARDONLY == 1 ]; then

echo "------------------------------------------------"
echo "------------> Create DATACARD"
echo "------------------------------------------------"

cd Datacard

echo "Analysis: $ANALYSIS"
echo "analysis_type: $ANALYSIS_TYPE"
if [ $ANALYSIS == "HHWWgg" ]; then 

    # echo "./makeDatacard.py -i $FILE  -o Datacard_13TeV_${EXT}.txt -p $PROCS -c $CATS --photonCatScales $SCALES --photonCatSmears $SMEARS --isMultiPdf --mass 125 --intLumi $INTLUMI --year $YEAR --uepsfilename $UEPS --newGghScheme --analysis HHWWgg "
    # ./makeDatacard.py -i $FILE  -o Datacard_13TeV_${EXT}.txt -p $PROCS -c $CATS --photonCatScales $SCALES --photonCatSmears $SMEARS --isMultiPdf --mass 125 --intLumi $INTLUMI --year $YEAR --uepsfilename $UEPS --newGghScheme --analysis HHWWgg 
  
    systematicsOption=""
    
    if [[ $DOSYSTEMATICS == "1" ]]; then
      systematicsOption=" --doSystematics "
    fi

    # shortExt=""
    echo "shortExt: $SHORTEXT"

    datacardDirec="${SHORTEXT}_${HHWWGGCATLABEL}_datacards"
    mkdir -p $datacardDirec

    DatacardName="Datacard_13TeV_${EXT}.txt"
    DatacardNameCleaned="Datacard_13TeV_${EXT}_cleaned.txt"
    echo "python makeDatacard.py --inputWSDir $FILE --years $YEAR --procs $PROCS --analysis $ANALYSIS --cats $CATS ${systematicsOption} --removeNoTag --DatacardName $DatacardName --ext $SHORTEXT --analysis_type $ANALYSIS_TYPE"
    python makeDatacard.py --inputWSDir $FILE --years $YEAR --procs $PROCS --analysis $ANALYSIS --cats $CATS ${systematicsOption} --removeNoTag --DatacardName $DatacardName --ext $SHORTEXT --analysis_type $ANALYSIS_TYPE
    
    # echo "python cleanDatacard.py --inputWSDir $FILE --years $YEAR --procs $PROCS --analysis $ANALYSIS --cats $CATS ${systematicsOption} --removeNoTag"
    echo "python cleanDatacard.py --datacard $DatacardName --outfilename $DatacardNameCleaned"
    python cleanDatacard.py --datacard $DatacardName --outfilename $DatacardNameCleaned
    mv $DatacardName $datacardDirec
    mv $DatacardNameCleaned $datacardDirec

    # echo "python makeDatacard.py -i $FILE  -o Datacard_13TeV_${EXT}.txt -p $PROCS -c $CATS --photonCatScales $SCALES --photonCatSmears $SMEARS --isMultiPdf --mass 125 --intLumi $INTLUMI --year $YEAR --uepsfilename $UEPS --newGghScheme --analysis HHWWgg "
    # python makeDatacard.py -i $FILE  -o Datacard_13TeV_${EXT}.txt -p $PROCS -c $CATS --photonCatScales $SCALES --photonCatSmears $SMEARS --isMultiPdf --mass 125 --intLumi $INTLUMI --year $YEAR --uepsfilename $UEPS --newGghScheme --analysis HHWWgg 

  # echo "./makeParametricModelDatacardFLASHgg.py -i $FILE -o Datacard_13TeV_${EXT}.txt -p $PROCS -c $CATS --photonCatScales $SCALES --photonCatSmears $SMEARS --isMultiPdf --mass 125 --intLumi $INTLUMI --uepsfilename $UEPS --analysis HHWWgg"
  # ./makeParametricModelDatacardFLASHgg.py -i $FILE  -o Datacard_13TeV_${EXT}.txt -p $PROCS -c $CATS --photonCatScales $SCALES --photonCatSmears $SMEARS --isMultiPdf --mass 125 --intLumi $INTLUMI --uepsfilename $UEPS --analysis HHWWgg #--submitSelf

else 
  if [ $DOSTAGE1 == 1 ]; then
    echo "./makeDatacard.py -i $FILE  -o Datacard_13TeV_${EXT}.txt -p $PROCS -c $CATS --photonCatScales $SCALES --photonCatSmears $SMEARS --isMultiPdf --mass 125 --intLumi $INTLUMI --year $YEAR --uepsfilename $UEPS --newGghScheme --doSTXS"
    ./makeDatacard.py -i $FILE  -o Datacard_13TeV_${EXT}.txt -p $PROCS -c $CATS --photonCatScales $SCALES --photonCatSmears $SMEARS --isMultiPdf --mass 125 --intLumi $INTLUMI --year $YEAR --uepsfilename $UEPS --newGghScheme --doSTXS
  else
    if [ $NEWGGHSCHEME == 1 ] && [ $DOSTXS == 1 ]; then
    echo "./makeParametricModelDatacardFLASHgg.py -i $FILE  -o Datacard_13TeV_${EXT}.txt -p $PROCS -c $CATS --photonCatScales $SCALES --photonCatSmears $SMEARS --isMultiPdf --mass 125 --intLumi $INTLUMI --uepsfilename $UEPS --newGghScheme --doSTXS"
    ./makeParametricModelDatacardFLASHgg.py -i $FILE  -o Datacard_13TeV_${EXT}.txt -p $PROCS -c $CATS --photonCatScales $SCALES --photonCatSmears $SMEARS --isMultiPdf --mass 125 --intLumi $INTLUMI --uepsfilename $UEPS --newGghScheme --doSTXS #--submitSelf
    fi
    if [ $NEWGGHSCHEME == 1 ] && [ $DOSTXS == 0 ]; then
        echo "./makeParametricModelDatacardFLASHgg.py -i $FILE  -o Datacard_13TeV_${EXT}.txt -p $PROCS -c $CATS --photonCatScales $SCALES --photonCatSmears $SMEARS --isMultiPdf --mass 125 --intLumi $INTLUMI --uepsfilename $UEPS --newGghScheme"
        ./makeParametricModelDatacardFLASHgg.py -i $FILE  -o Datacard_13TeV_${EXT}.txt -p $PROCS -c $CATS --photonCatScales $SCALES --photonCatSmears $SMEARS --isMultiPdf --mass 125 --intLumi $INTLUMI --uepsfilename $UEPS --newGghScheme #--submitSelf
    fi
    if [ $NEWGGHSCHEME == 0 ] && [ $DOSTXS == 1 ]; then
    echo "./makeParametricModelDatacardFLASHgg.py -i $FILE  -o Datacard_13TeV_${EXT}.txt -p $PROCS -c $CATS --photonCatScales $SCALES --photonCatSmears $SMEARS --isMultiPdf --mass 125 --intLumi $INTLUMI --uepsfilename $UEPS --doSTXS"
    ./makeParametricModelDatacardFLASHgg.py -i $FILE  -o Datacard_13TeV_${EXT}.txt -p $PROCS -c $CATS --photonCatScales $SCALES --photonCatSmears $SMEARS --isMultiPdf --mass 125 --intLumi $INTLUMI --uepsfilename $UEPS --doSTXS #--submitSelf
    fi
    if [ $NEWGGHSCHEME == 0 ] && [ $DOSTXS == 0 ]; then
    echo "./makeParametricModelDatacardFLASHgg.py -i $FILE  -o Datacard_13TeV_${EXT}.txt -p $PROCS -c $CATS --photonCatScales $SCALES --photonCatSmears $SMEARS --isMultiPdf --mass 125 --intLumi $INTLUMI --uepsfilename $UEPS"
    ./makeParametricModelDatacardFLASHgg.py -i $FILE  -o Datacard_13TeV_${EXT}.txt -p $PROCS -c $CATS --photonCatScales $SCALES --photonCatSmears $SMEARS --isMultiPdf --mass 125 --intLumi $INTLUMI --uepsfilename $UEPS #--submitSelf
    fi
  fi
fi
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

if [ $ANALYSIS == "HHWWgg" ]; then 
  fileDir="${FILE%/*}" # get directory 
  fileEnd="${FILE##*/}"
  fileID=${fileEnd::-5} # remove .root   
  if [ $ANALYSIS_TYPE == "NMSSM" ]; then 
    # HHWWggmass="$(cut -d'_' -f1 <<<$fileID)" # get text before first '_'. ex: SM, X250, X260, ...
    # HHWWggLabel1="${mass}_WWgg_qqlnugg" 
    massX="$(cut -d'_' -f1 <<<$fileID)"
    massY="$(cut -d'_' -f2 <<<$fileID)"
    HHWWggmass="${massX}_${massY}"
    HHWWggLabel="${HHWWggmass}_HHWWgg_qqlnu" 
  else 
    HHWWggmass="$(cut -d'_' -f1 <<<$fileID)" # get text before first '_'. ex: SM, X250, X260, ...
    # HHWWggLabel1="${mass}_WWgg_qqlnugg" 
    HHWWggLabel="${HHWWggmass}_HHWWgg_qqlnu" 
  fi 
  OUTDIR+="_${HHWWggLabel}"
fi 

echo "HHWWggmass: $HHWWggmass"

if [ ! -d "Signal/$OUTDIR" ]; then
  echo "Signal/$OUTDIR doesn't exist, maybe your EXT is wrong? Exiting..."
  exit 1
fi
#need 
# Datacard_13TeV_HHWWgg_v2-3_2017_2Cats_X650_HHWWgg_qqlnu_cleaned.txt

#looked for 
# Datacard_13TeV_HHWWgg_v2-3_2017_2Cats_cleaned.txt

datacardDirec="${SHORTEXT}_${HHWWGGCATLABEL}_datacards"

DatacardName="Datacard_13TeV_${EXT}_cleaned.txt"
if [ $ANALYSIS == "HHWWgg" ]; then 
  DatacardName="Datacard_13TeV_${EXT}_${HHWWggLabel}_cleaned.txt"
fi

DatacardLocation="${datacardDirec}/${DatacardName}"

cd Plots/FinalResults
# ls ../../Signal/$OUTDIR/CMS-HGG_*sigfit*oot  > tmp.txt
if [ $ANALYSIS == "HHWWgg" ]; then 
  # ls ../../Signal/$OUTDIR/CMS-HGG_*sigfit*oot  > tmp.txt
  ls ../../Signal/$OUTDIR/CMS-HGG_mva_13TeV_sigfit.root  > tmp.txt
else
  ls ../../Signal/$OUTDIR/CMS-HGG_*sigfit*oot  > tmp.txt
fi

while read p;
do
q=$(basename $p)

mkdir -p ./Models
mkdir -p ./Models/${EXT}
# mkdir -p ./Models/${EXT}/${q}
# mkdir -p ./Models/${EXT}/${q}/${EXT}
# mkdir -p ./Models/${EXT}/${q}/${EXT}/mva 

cp $p ./Models/${EXT}/${q/$EXT/mva} 
#echo " cp $p ./Inputs/${EXT}/${q/$EXT/mva} "
done < tmp.txt

mkdir -p ${HHWWGGCATLABEL}_limits

echo "FAKE: ${FAKE}"
echo "BACKGROUND COMMAND: cp ../../Background/CMS-HGG_multipdf_${EXT}${FAKE}.root"

echo "EXT: $EXT"
echo "SHORTEXT: $SHORTEXT"
# shorterEXT=$EXT
shorterEXT=${EXT%_*}
# echo ${foo##*:}
echo "shorterEXT: $shorterEXT"

if [ $ANALYSIS == "HHWWgg" ]; then 
  # echo "cp ../../Signal/$OUTDIR/CMS-HGG_mva_13TeV_sigfit.root ./Models/${EXT}/CMS-HGG_mva_13TeV_sigfit.root"
  cp ../../Signal/$OUTDIR/CMS-HGG_mva_13TeV_sigfit.root ./Models/${EXT}/CMS-HGG_mva_13TeV_sigfit.root
else 
  cp ../../Signal/$OUTDIR/CMS-HGG_sigfit_${EXT}.root ./Models/${EXT}/CMS-HGG_mva_13TeV_sigfit.root
fi 
cp ../../Background/CMS-HGG_multipdf_${EXT}${FAKE}.root ./Models/${EXT}/CMS-HGG_mva_13TeV_multipdf${FAKE}.root
cp ../../Datacard/${DatacardLocation} CMS-HGG_mva_13TeV_datacard_${EXT}.txt

if [ $ANALYSIS == "HHWWgg" ]; then 
  combine CMS-HGG_mva_13TeV_datacard_${EXT}.txt -m 125 -M AsymptoticLimits --run=blind
  
  mv higgsCombineTest.AsymptoticLimits.mH125.root ${HHWWGGCATLABEL}_limits/${shorterEXT}_${HHWWggmass}_${HHWWGGCATLABEL}_HHWWgg_qqlnu.root
  # mv higgsCombineTest.AsymptoticLimits.mH125.root # save for mass point, category 
fi

# if [ $ISDATA == 0 ]; then
# FAKE="_FAKE"
# fi

# if [ ! -d "Signal/$OUTDIR" ]; then
#   echo "Signal/$OUTDIR doesn't exist, maybe your EXT is wrong? Exiting..."
#   exit 1
# fi

# if [ $ANALYSIS == "HHWWgg" ]; then 
#   fileDir="${FILE%/*}" # get directory 
#   fileEnd="${FILE##*/}"
#   fileID=${fileEnd::-5} # remove .root     
#   mass="$(cut -d'_' -f1 <<<$fileID)" # get text before first '_'. ex: SM, X250, X260, ...
#   # HHWWggLabel1="${mass}_WWgg_qqlnugg" 
#   HHWWggLabel="${mass}_HHWWgg_qqlnu" 
# fi 




# cd Plots/FinalResults

# ls ../../Signal/$OUTDIR/CMS-HGG_*sigfit*oot  > tmp.txt

# while read p;
# do
# q=$(basename $p)
# mkdir -p ./Inputs
# mkdir -p ./Inputs/${EXT}
# mkdir -p ./Inputs/${EXT}/${q}
# mkdir -p ./Inputs/${EXT}/${q}/${EXT}
# mkdir -p ./Inputs/${EXT}/${q}/${EXT}/mva 
# cp $p ./Inputs/${EXT}/${q/$EXT/mva} 
# #echo " cp $p ./Inputs/${EXT}/${q/$EXT/mva} "
# done < tmp.txt

# echo "EXT: $EXT" ## hggpdfsmrel_13TeV_ggF_HHWWggTag_0
# #cp ../../Signal/$OUTDIR/CMS-HGG_sigfit_${EXT}.root ./Inputs/${EXT}/CMS-HGG_mva_13TeV_sigfit.root



# if [ $ANALYSIS == "HHWWgg" ]; then 
#   # cp ../../Signal/$OUTDIR/CMS-HGG_sigfit_${EXT}_${HHWWggLabel}.root CMS-HGG_sigfit_data_ggF_HHWWggTag_0_13TeV.root # doesn't give limit for some reason 
#   cp ../../Signal/$OUTDIR/CMS-HGG_mva_13TeV_sigfit.root CMS-HGG_sigfit_data_ggF_HHWWggTag_0_13TeV.root
#   # cp ../../Signal/$OUTDIR/CMS-HGG_mva_13TeV_sigfit.root CMS-HGG_sigfit_data_ggF_HHWWggTag_0_13TeV.root
#   # CMS-HGG_sigfit_HHWWgg_v2-3_2017_SM_HHWWgg_qqlnu.root # bigger for some reason 
#   # CMS-HGG_mva_13TeV_sigfit.root
#   cp ../../Background/CMS-HGG_multipdf_${EXT}.root CMS-HGG_mva_13TeV_multipdf.root 
#   cp ../../Datacard/Datacard_13TeV_${EXT}_${HHWWggLabel}.txt CMS-HGG_mva_13TeV_datacard.txt
#   combine CMS-HGG_mva_13TeV_datacard.txt -m 125 -M AsymptoticLimits --run=blind
#   # combine CMS-HGG_mva_13TeV_datacard.txt -m 125 -M AsymptoticLimits --run=blind -v 2
#   cp higgsCombineTest.AsymptoticLimits.mH125.root ${EXT}_${HHWWggLabel}.root 
#   # cp higgsCombineTest.AsymptoticLimits.mH125.root $outName
# else 
#   cp ../../Background/CMS-HGG_multipdf_${EXT}${FAKE}.root ./Inputs/${EXT}/CMS-HGG_mva_13TeV_multipdf${FAKE}.root
#   cp ../../Datacard/Datacard_13TeV_${EXT}_cleaned.txt CMS-HGG_mva_13TeV_datacard_${EXT}.txt
# fi 




exit 1

cp combineHarvesterOptions_Template${FAKE}.dat combineHarvesterOptions_${EXT}${FAKE}.dat
sed -i -e "s/\!EXT\!/$EXT/g" combineHarvesterOptions_${EXT}${FAKE}.dat 
sed -i -e "s/\!FAKE\!/$FAKE/g" combineHarvesterOptions_${EXT}${FAKE}.dat
echo "Adding _FAKE  ($FAKE) t multipdf if ISDATA == $ISDATA"
sed -i -e "s/multipdf.root/multipdf${FAKE}.root/g" CMS-HGG_mva_13TeV_datacard.txt 
sed -i -e "s/\!INTLUMI\!/$INTLUMI/g" combineHarvesterOptions_${EXT}${FAKE}.dat 

# if HHWWgg add local runLocal
runLocalOption=""
if [ $ANALYSIS == "HHWWgg" ]; then 
  runLocalOption=" --runLocal "
fi

echo "./combineHarvester.py -d combineHarvesterOptions_$EXT.dat -q $DEFAULTQUEUE --batch $BATCH --verbose $runLocalOption"
./combineHarvester.py -d combineHarvesterOptions_${EXT}${FAKE}.dat -q $DEFAULTQUEUE --batch $BATCH --verbose $runLocalOption


JOBS=999
RUN=999
PEND=999
FAIL=999
DONE=999

while (( $RUN > 0 ));do
JOBS=`find combineJobs13TeV_$EXT/   -name "*.sh" | wc -l`
DONE=`find combineJobs13TeV_$EXT/   -name "*.sh.done" | wc -l`
FAIL=`find combineJobs13TeV_$EXT/   -name "*.sh.fail" | wc -l`
((RUN=$JOBS-$DONE-$FAIL))
echo "RUN=$RUN"
echo "JOBS=$JOBS"
echo "DONE=$DONE"
echo "FAIL=$FAIL"
sleep 10
echo "[INFO] Processing $JOBS jobs: PEND $PEND, RUN $RUN, FAIL $FAIL"
done

echo "[INFO] ------> All jobs done"
echo "[INFO] ------> Hadding files in directory combineJobs13TeV_$EXT "
./combineHarvester.py --hadd combineJobs13TeV_$EXT

fi

####################################################
################## COMBINE PLOTS ###################
####################################################

if [ $COMBINEPLOTSONLY == 1 ]; then

cd Plots/FinalResults

# All plots
#cp allPlots_Template${FAKE}.sh allPlots_${EXT}${FAKE}.sh
#chmod +x  allPlots_${EXT}${FAKE}.sh
#sed -i -e "s/\!EXT\!/$EXT/g" allPlots_${EXT}${FAKE}.sh 
#sed -i -e "s/\!FAKE\!/$FAKE/g" combineHarvesterOptions_${EXT}${FAKE}.dat
#sed -i -e "s/\!INTLUMI\!/$INTLUMI/g"  allPlots_${EXT}${FAKE}.sh
#./allPlots_${EXT}${FAKE}.sh

# Single plot
cp combinePlotsOptions_Template${FAKE}.dat combinePlotsOptions_${EXT}${FAKE}.dat
sed -i -e "s/\!EXT\!/$EXT/g" combinePlotsOptions_${EXT}${FAKE}.dat
sed -i -e "s/\!INTLUMI\!/$INTLUMI/g" combinePlotsOptions_${EXT}${FAKE}.dat
LEDGER=" --it $COUNTER --itLedger itLedger_$EXT.txt"

echo "./makeCombinePlots.py -d combinePlotsOptions_${EXT}${FAKE}.dat -b $LEDGER "
./makeCombinePlots.py -d combinePlotsOptions_$EXT${FAKE}.dat -b $LEDGER

mkdir -p $OUTDIR/combinePlots
cp *pdf $OUTDIR/combinePlots/.
cp *png $OUTDIR/combinePlots/.
rm *pdf
rm *png

cd -

fi
