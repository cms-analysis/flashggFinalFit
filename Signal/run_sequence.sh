#!/bin/bash

YEAR=-753
STEP=0

usage(){
    echo "The script runs background scripts:"
    echo "options:"
    
    echo "-h|--help) "
    echo "-y|--year) "
    echo "-s|--step) "
}
# options may be followed by one colon to indicate they have a required argument
if ! options=$(getopt -u -o s:y: -l help,step:,year: -- "$@")
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
(--) shift; break;;
(-*) usage; echo "$0: error - unrecognized option $1" 1>&2; usage >> /dev/stderr; exit 1;;
(*) break;;
esac
shift
done

echo "Requested to run the step ${STEP} for the year: ${YEAR}"
if [[ $YEAR < 2016 || $YEAR>2018 ]]; then
    echo "Year $YEAR does not belong to Run2. Exiting."
    exit
fi

if [[ $STEP == "fTest" ]]; then
    python RunSignalScripts.py --inputConfig config_test_${YEAR}.py --mode fTest --modeOpts "--xvar dipho_mass --doPlots --outdir plots --nProcsToFTest -1" --printOnly 
elif [[ $STEP == 'signalFit' ]]; then
    python RunSignalScripts.py --inputConfig config_test_${YEAR}.py --mode signalFit --modeOpts="--skipSystematics --xvar dipho_mass --doPlots --outdir plots" --printOnly
elif [[ $STEP == 'packager' ]]; then
    python RunPackager.py --cats auto --inputWSDir cards/cards_fithgg/${YEAR}/ --exts test1_${YEAR} --mergeYears --printOnly
elif [[ $STEP == 'plotter' ]]; then
    python RunPlotter.py --procs all --cats all --years ${YEAR} --ext packaged --outdir plots
else
    echo "Step $STEP is not one among fTest, signalFit, packager, plotter. Exiting."
fi


