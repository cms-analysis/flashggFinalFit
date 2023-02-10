#!/bin/bash

YEAR=-753
STEP=0

usage(){
    echo "The script runs background scripts:"
    echo "options:"
    
    echo "-h|--help) "
    echo "-y|--year): can be the yearId or all"
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

fggDir="/cmshome/dimarcoe/vbfac/flashgg/CMSSW_10_6_29/src/"

DROPT=""
if [[ $DR ]]; then
    DROPT=" --printOnly "
fi

QUEUE=""
if [[ $I ]]; then
    QUEUE=" --batch local "
else
    QUEUE=" --batch Rome --queue cmsan "
fi

years=("2016preVFP" "2016postVFP" "2017" "2018")
 
for year in ${years[*]}
do
    if [[ $year == $YEAR ]] || [[ $YEAR == "all" ]]; then
	if [[ $STEP == "t2ws-mc" ]]; then
	    python RunWSScripts.py --inputConfig config.py --inputDir trees/merged/signal_${year} --mode trees2ws --modeOpts "--doSystematics" --year ${year} --ext GGH_${year} ${QUEUE} ${DROPT}
	elif [[ $STEP == "t2ws-data" ]]; then
	    python RunWSScripts.py --inputConfig config.py --inputDir trees/merged/data_${year} --mode trees2ws_data --year ${year} --ext ${year} ${QUEUE} ${DROPT}    
	elif [[ $STEP == "hadd-mc" ]]; then
	    python RunWSScripts.py --inputDir trees/signal_${year} --mode haddMC --year ${year} --ext ${year} --flashggPath ${fggDir} ${QUEUE} ${DROPT}
	elif [[ $STEP == "hadd-data" ]]; then
	    python RunWSScripts.py --inputDir trees/data_${year} --mode haddData --year ${year} --ext ${year} --flashggPath ${fggDir} ${QUEUE} ${DROPT}
	else
	    echo "Step $STEP is not one among mc, data. Exiting."
	fi
    fi
done

