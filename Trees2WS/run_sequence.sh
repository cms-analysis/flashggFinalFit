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
}
# options may be followed by one colon to indicate they have a required argument
if ! options=$(getopt -u -o s:y:dh -l help,step:,year:,dryRun -- "$@")
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

if [[ $STEP == "mc" ]]; then
    python RunWSScripts.py --inputConfig config.py --inputDir trees --mode trees2ws --year ${YEAR} --ext test_${YEAR} --batch condor --queue longlunch ${DROPT}
elif [[ $STEP == "data" ]]; then
    python RunWSScripts.py --inputConfig config.py --inputDir trees --mode trees2ws_data --year ${YEAR} --ext test_${YEAR} --batch condor --queue longlunch ${DROPT}    
else
    echo "Step $STEP is not one among mc, data. Exiting."
fi

