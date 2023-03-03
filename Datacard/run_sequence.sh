#ext=`date +%F` 
ext='2023-03-02'

STEP=0
usage(){
    echo "Script to run yields and datacard making. Yields need to be done before running datacards"
    echo "options:"
    
    echo "-h|--help) "
    echo "-s|--step) "
    echo "-d|--dryRun) "
}
# options may be followed by one colon to indicate they have a required argument
if ! options=$(getopt -u -o s:hd -l help,step:,dryRun -- "$@")
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

smprocs=("GG2H" "VBF" "TTH" "WMINUSH2HQQ" "WPLUSH2HQQ" "QQ2HLL")
smprocs_csv=$(IFS=, ; echo "${smprocs[*]}")

if [[ $STEP == "yields" ]]; then
    # for mu-simple: exclude ALT processes
    python RunYields.py --cats "auto" --inputWSDirMap 2016preVFP=cards/signal_2016preVFP,2016postVFP=cards/signal_2016postVFP,2017=cards/signal_2017,2018=cards/signal_2018 --procs $smprocs_csv --mergeYears --doSystematics --skipZeroes --ext ${ext}_xsec --batch Rome --queue cmsan ${DROPT}
    
    # for the single fai fits: include one ALT sample at a time
    for altproc in "ALT_L1" "ALT_L1Zg" "ALT_0PH" "ALT_0M"
    # to get the interference correctly need the SM (fa1=0), the pure BSM (fai=1) and the mixed one (fai=0.5)
    do
	# for bookkeeping mistake, for VBF the files are called ALT_xxx for VBF and ALTxx for VH,TTH
	altproc_nonvbf=`echo ${altproc} | sed 's|_||g'`
        vbfsamples="VBF,VBF_${altproc},VBF_${altproc}f05"
	zhsamples="QQ2HLL,ZH_${altproc_nonvbf},ZH_${altproc_nonvbf}f05ph0"
        if [[ $altproc == "ALT_0PH" ]]; then # not all the WH alternative samples are available yet
	    whsamples="WMINUSH2HQQ,WPLUSH2HQQ,WH_${altproc_nonvbf},WH_${altproc_nonvbf}f05ph0"
        else
            whsamples="WMINUSH2HQQ,WPLUSH2HQQ"
        fi
	if [[ $altproc == "ALT_0M" ]]; then
	    tthsamples="TTH,TTH_${altproc_nonvbf},TTH_${altproc_nonvbf}f05ph0"
	else
	    tthsamples="TTH"
	fi
	if [[ $altproc == "ALT_L1" ]] || [[ $altproc == "ALT_L1Zg" ]]; then
	    zhsamples=`echo ${zhsamples} | sed 's|L1|0L1|g'`
	fi
        python RunYields.py --cats "auto" --inputWSDirMap 2016preVFP=cards/signal_2016preVFP,2016postVFP=cards/signal_2016postVFP,2017=cards/signal_2017,2018=cards/signal_2018 --procs "GG2H,$tthsamples,$vbfsamples,$whsamples,$zhsamples" --mergeYears --doSystematics --skipZeroes --ext ${ext}_${altproc} --batch Rome --queue cmsan ${DROPT}
    done
elif [[ $STEP == "datacards" ]]; then
    for fit in "xsec" "ALT_L1" "ALT_L1Zg" "ALT_0PH" "ALT_0M"
    do
	echo "making datacards for all years together for type of fit: $fit"
        python makeDatacard.py --years 2016preVFP,2016postVFP,2017,2018 --ext ${ext}_${fit} --prune --doSystematics --output "Datacard_${fit}" --pruneCat RECO_VBFLIKEGGH_Tag1,RECO_VBFLIKEGGH_Tag0
	python cleanDatacard.py --datacard "Datacard_${fit}" --factor 2 --removeDoubleSided
	mv "Datacard_${fit}_cleaned.txt" "Datacard_${fit}.txt"
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


