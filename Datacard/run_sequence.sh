ext=`date +%F` 

STEP=0
usage(){
    echo "Script to run yields and datacard making. Yields need to be done before running datacards"
    echo "options:"
    
    echo "-h|--help) "
    echo "-s|--step) "
    echo "-d|--dryRun) "
}
# options may be followed by one colon to indicate they have a required argument
if ! options=$(getopt -u -o s:h -l help,step:,dryRun -- "$@")
then
# something went wrong, getopt will put out an error message for us
exit 1
fi
set -- $options
while [ $# -gt 0 ]
do
case $1 in
-h|--help) usage; exit 0;;
-s|--step) STEP=$2; shift ;;
-d|--dryRun) DR=$2; shift ;;
(--) shift; break;;
(-*) usage; echo "$0: error - unrecognized option $1" 1>&2; usage >> /dev/stderr; exit 1;;
(*) break;;
esac
shift
done

DROPT=""
if [[ $DR ]]; then
    DROPT=" --printOnly "
fi

if [[ $STEP == "yields" ]]; then
    # for mu-simple: exclude ALT processes
    python RunYields.py --cats "VBFTag_1,VBFTag_3,VBFTag_5,VBFTag_6,VBFTag_7" --inputWSDirMap 2016preVFP=cards/cards_current/signal_2016preVFP,2016postVFP=cards/cards_current/signal_2016postVFP,2017=cards/cards_current/signal_2017,2018=cards/cards_current/signal_2018 --procs "GG2H,TTH,VBF,WH_WM,WH_WP,ZH" --mergeYears --doSystematics --ext ${ext}_xsec --batch condor --queue espresso ${DROPT}
    
    # for the single fai fits: include one ALT sample at a time
    for altproc in "ALT0L1" "ALT0L1Zg" "ALT0PH" "ALT0M"
    # to get the interference correctly need the SM (fa1=0), the pure BSM (fai=1) and the mixed one (fai=0.5)
    # temporary approx: only the VBF is BSM
    do
        vbfsamples="VBF,VBF_${altproc},VBF_${altproc}f05ph0"
        #whaltsamples="WH_ALT0L1f05ph0,WH_ALT0PH,WH_ALT0PHf05ph0" # not all are completed
        if [[ $altproc == "ALT0M" ]]; then
            zhsamples="ZH" # ZH alternative samples have some missing systematics
        else
            zhsamples="ZH,ZH_${altproc},ZH_${altproc}f05ph0"
        fi
        python RunYields.py --cats "VBFTag_1,VBFTag_3,VBFTag_5,VBFTag_6,VBFTag_7" --inputWSDirMap 2016preVFP=cards/cards_current/signal_2016preVFP,2016postVFP=cards/cards_current/signal_2016postVFP,2017=cards/cards_current/signal_2017,2018=cards/cards_current/signal_2018 --procs "GG2H,TTH,WH_WM,WH_WP,$vbfsamples,$zhsamples" --mergeYears --doSystematics --ext ${ext}_${altproc} --batch condor --queue espresso ${DROPT}
    done
elif [[ $STEP == "datacards" ]]; then
    for fit in "xsec" "ALT0L1" "ALT0L1Zg" "ALT0PH" "ALT0M"
    do
        python makeDatacard.py --years 2016preVFP,2016postVFP,2017,2018 --ext ${ext}_${fit} --prune --doSystematics --output "Datacard_${fit}"
    done
elif [[ $STEP == "links" ]]; then
    cd Models 
    rm signal background 
    echo "linking Models/signal to ../../Signal/outdir_packaged"
    ln -s ../../Signal/outdir_packaged signal
    echo "linking Models/background to ../../Background/outdir_2022-11-21"
    ln -s ../../Background/outdir_2022-11-21 background
    cd -
else
    echo "Step $STEP is not one among yields,datacard,links. Exiting."
fi


