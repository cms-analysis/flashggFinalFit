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

echo "Requested to run the step ${STEP} for the year: ${YEAR}"
if [[ $YEAR != "all" && ($YEAR < 2016 || $YEAR>2018) ]]; then
    echo "Year $YEAR does not belong to Run2. Exiting."
    exit
fi

DROPT=""
if [[ $DR ]]; then
    DROPT=" --printOnly "
fi

years=("2016preVFP" "2016postVFP" "2017" "2018")

for year in ${years[*]}
do
    echo "====> Running for year $year"
    if [[ $year == $YEAR ]] || [[ $YEAR == "all" ]]; then
	if [[ $STEP == "fTest" ]]; then
	    python RunSignalScripts.py --inputConfig config_test_${year}.py --mode fTest --modeOpts "--doPlots --outdir plots --nProcsToFTest -1" ${DROPT}
	elif [[ $STEP == "calcPhotonSyst" ]]; then
	    python RunSignalScripts.py --inputConfig config_test_${year}.py --mode calcPhotonSyst ${DROPT}
	elif [[ $STEP == 'signalFit' ]]; then
	    python RunSignalScripts.py --inputConfig config_test_${year}.py --mode signalFit --modeOpts="--doPlots --outdir plots" ${DROPT}
	elif [[ $STEP == 'packager' ]]; then
	    python RunPackager.py --cats "auto" --inputWSDir cards/signal_${year} --exts 2022-11-21_year2016preVFP,2022-11-21_year2016postVFP,2022-11-21_year2017,2022-11-21_year2018 --mergeYears ${DROPT}
	fi
    fi
done

if [[ $STEP == 'plotter' ]]; then
    # just plot all the (SM) processes, all the categories, all the years together. Can be split with --year ${YEAR}. Do not include BSM to maintain the expected total yield for SM
    python RunPlotter.py --procs "GG2H,VBF,WH_WP,WH_WM,TTH" --cats "VBFTag_1,VBFTag_3,VBFTag_5,VBFTag_6,VBFTag_7" --year 2016preVFP,2016postVFP,2017,2018 --ext packaged --outdir plots
    # split by category, all processes together
    for i in 1 3 5 6 7
    do
	python RunPlotter.py --procs "GG2H,VBF,WH_WP,WH_WM,TTH" --cats "VBFTag_$i" --year 2016preVFP,2016postVFP,2017,2018 --ext packaged --outdir plots --translateCats ../Plots/cats.json
    done
    # split by process, all the categories together
    for proc in "GG2H" "VBF" "VBF_ALT0M" "VBF_ALT0Mf05" "VBF_ALT0PH" "VBF_ALT0PHf05" "VBF_ALTL1" "VBF_ALTL1f05" "VBF_ALTL1Zg" "VBF_ALTL1Zgf05" "WH_WP" "WH_WM" "WH_ALT0L1f05ph0" "WH_ALT0PH" "WH_ALT0PHf05ph0" "WH_ALT0PM" "ZH_ALT0L1" "ZH_ALT0L1f05ph0" "ZH_ALT0L1Zg" "ZH_ALT0L1Zgf05ph0" "ZH_ALT0M" "ZH_ALT0Mf05ph0" "ZH_ALT0PH" "ZH_ALT0PHf05ph0" "ZH_ALT0PM" "ZH" "TTH" "TTH_ALT0M" "TTH_ALT0Mf05ph0" "TTH_ALT0PM"
    do
	python RunPlotter.py --procs $proc --cats "VBFTag_1,VBFTag_3,VBFTag_5,VBFTag_6,VBFTag_7" --year 2016preVFP,2016postVFP,2017,2018 --ext packaged --outdir plots --translateProcs ../Plots/jcp.json
    done
fi


