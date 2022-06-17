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
if ! options=$(getopt -u -o s:y:d -l help,step:,year:,dryRun -- "$@")
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

echo "Requested to run the step ${STEP} for the year: ${YEAR}"
if [[ $YEAR < 2016 || $YEAR>2018 ]]; then
    echo "Year $YEAR does not belong to Run2. Exiting."
    exit
fi

DROPT=""
if [[ $DR ]]; then
    DROPT=" --printOnly "
fi

if [[ $STEP == "fTest" ]]; then
    python RunSignalScripts.py --inputConfig config_test_${YEAR}.py --mode fTest --modeOpts "--doPlots --outdir plots --nProcsToFTest -1" ${DROPT}
elif [[ $STEP == 'signalFit' ]]; then
    python RunSignalScripts.py --inputConfig config_test_${YEAR}.py --mode signalFit --modeOpts="--doPlots --outdir plots" ${DROPT}
elif [[ $STEP == 'packager' ]]; then
    python RunPackager.py --cats auto --inputWSDir cards/cards_current/signal_${YEAR} --exts 2022-04-12_year2016,2022-04-12_year2017,2022-04-12_year2018 --mergeYears ${DROPT}
elif [[ $STEP == 'plotter' ]]; then
    # just plot all the years together. Can be split with --year ${YEAR}
    python RunPlotter.py --procs all --cats all --year 2016,2017,2018 --ext packaged --outdir plots
    # the following doesn't work until one loads a JSON with the cat=>latex name translation via --translateCats option. TO BE DONE.
    python RunPlotter.py --procs all --cats RECO_DCP0_Bsm0_Tag0,RECO_DCP0_Bsm1_Tag0,RECO_DCP0_Bsm2_Tag0,RECO_DCP0_Tag1,RECO_DCP1_Bsm0_Tag0,RECO_DCP1_Bsm1_Tag0,RECO_DCP1_Bsm2_Tag0,RECO_DCP1_Tag1 --year 2016,2017,2018 --ext packaged --outdir plots
else
    echo "Step $STEP is not one among fTest, signalFit, packager, plotter. Exiting."
fi


