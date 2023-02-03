#!/bin/bash

YEAR=-753
STEP=0

usage(){
    echo "The script runs background scripts:"
    echo "options:"
    
    echo "-h|--help) "
    echo "-y|--year) "
    echo "-s|--step) "
    echo "-d|--dryRun) "
    echo "-i|--interactive) "
}
# options may be followed by one colon to indicate they have a required argument
if ! options=$(getopt -u -o s:y:dih -l help,step:,year:,dryRun,interactive -- "$@")
then
# something went wrong, getopt will put out an error message for us
exit 1
fi
set -- $options
while [ $# -gt 0 ]
do
case $1 in
-h|--help) usage; exit 0;;
-y|--year) YEAR=$2; shift ;;
-s|--step) STEP=$2; shift ;;
-d|--dryRun) DR=$2; shift ;;
-i|--interactive) I=$2; shift ;;
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

QUEUE=""
if [[ $I ]]; then
    QUEUE=" --batch local "
else
    QUEUE=" --batch condor --queue longlunch "
fi

if [[ $STEP == "mc" ]]; then
    python RunWSScripts.py --inputConfig config.py --inputDir trees/allSTXScats_signal_IA_UL${YEAR} --mode trees2ws --modeOpts "--doSystematics" --year ${YEAR} --ext ${YEAR} ${QUEUE} ${DROPT}
elif [[ $STEP == "data" ]]; then
    python RunWSScripts.py --inputConfig config.py --inputDir trees/allSTXScats_signal_IA_UL${YEAR} --mode trees2ws_data --year ${YEAR} --ext ${YEAR} ${QUEUE} ${DROPT}    
else
    echo "Step $STEP is not one among mc, data. Exiting."
fi

