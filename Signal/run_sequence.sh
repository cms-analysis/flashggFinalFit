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

if [[ $STEP == "fTest" ]] || [[ $STEP == "calcPhotonSyst" ]] || [[ $STEP == 'signalFit' ]]; then
    for year in ${years[*]}
    do
	if [[ $year == $YEAR ]] || [[ $YEAR == "all" ]]; then
	    echo "====> Running $STEP for year $year"
	    if [[ $STEP == "fTest" ]]; then
		python RunSignalScripts.py --inputConfig config_test_${year}.py --mode fTest --modeOpts "--doPlots --outdir plots --nProcsToFTest -1" ${DROPT}
	    elif [[ $STEP == "calcPhotonSyst" ]]; then
		python RunSignalScripts.py --inputConfig config_test_${year}.py --mode calcPhotonSyst ${DROPT}
	    elif [[ $STEP == 'signalFit' ]]; then
		python RunSignalScripts.py --inputConfig config_test_${year}.py --mode signalFit --modeOpts="--doPlots --outdir plots" ${DROPT}
	    fi
	fi
    done
elif [[ $STEP == 'packager' ]]; then
    python RunPackager.py --cats "auto" --inputWSDir cards/signal_2016preVFP --outputExt packaged --exts 2023-02-13_year2016preVFP,2023-02-13_year2016postVFP,2023-02-13_year2017,2023-02-13_year2018 --mergeYears --batch Rome --queue cmsan ${DROPT}
elif [[ $STEP == 'plotter' ]]; then
    smprocs=("GG2H" "VBF" "TTH" "WMINUSH2HQQ" "WPLUSH2HQQ" "QQ2HLL")
    smprocs_csv=$(IFS=, ; echo "${smprocs[*]}")
    # just plot all the (SM) processes, all the categories, all the years together. Can be split with --year ${YEAR}. Do not include BSM to maintain the expected total yield for SM
    echo "Now plotting all categories for these SM processes: $smprocs_csv"
    python RunPlotter.py --procs $smprocs_csv --cats "all" --year 2016preVFP,2016postVFP,2017,2018 --ext packaged --outdir plots
    # split by category, all processes together
    significantCats=("RECO_VBFTOPO_ACGGH_Tag0" "RECO_VBFTOPO_ACGGH_Tag1" "RECO_VBFTOPO_ACVBFBSM_Tag0" "RECO_VBFTOPO_ACVBFBSM_Tag1" "RECO_VBFTOPO_ACVBFSM_Tag0" "RECO_VBFTOPO_VHHAD_Tag0" "RECO_VBFTOPO_VHHAD_Tag1")
    significantCats_csv=$(IFS=, ; echo "${significantCats[*]}")
    for cat in ${significantCats[*]}
    do
    	echo "=> Now plotting all processes together for cat: $cat"
    	python RunPlotter.py --procs $smprocs_csv --cats cat --year 2016preVFP,2016postVFP,2017,2018 --outdir plots --ext packaged --outdir plots --translateCats ../Plots/cats.json
    done
    # split by process, all the categories together (the SM + some alternatives)
    for proc in ${smprocs[*]}
    do
    	echo "=> Now plotting proc $proc for all categories"
    	python RunPlotter.py --procs $proc --cats "all" --year 2016preVFP,2016postVFP,2017,2018 --ext packaged --outdir plots
    done
fi
