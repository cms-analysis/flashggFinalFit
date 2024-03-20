outdate=`date +%F` 

STEP=0
usage(){
    echo "Script to run fits and plots of fit output. dryRun option is for the fitting only, that can be run in batch."
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
    DROPT=" --dryRun "
fi

#fits=("xsec" "ALT_L1" "ALT_L1Zg" "ALT_0PH" "ALT_0M")
fits=("ALT_L1" "ALT_L1Zg" "ALT_0PH" "ALT_0M")
#fits=("xsec" )

if [[ $STEP == "t2w" ]]; then
    for fit in ${fits[*]}
    do
        python RunText2Workspace.py --ext $fit --mode $fit --batch Rome
    done
elif [[ $STEP == "fit" ]]; then
    #for obs in " " " --doObserved "
    for obs in " "
    do
        for fit in ${fits[*]}
        do
            python RunFits.py --inputJson inputs.json --ext $fit --mode $fit --queue cmsan --batch lxbatch  ${DROPT} $obs
        done
    done
elif [[ $STEP == "collect" ]]; then
    for obs in " " " --doObserved "
    do
	for fit in ${fits[*]}
	do
	    python CollectFits.py --inputJson inputs.json --ext $fit --mode $fit $obs
	done
    done
elif [[ $STEP == "plot" ]]; then
    for obs in " " " --doObserved "
    do
        for fit in ${fits[*]}
        do
            python PlotScans.py --inputJson inputs.json --mode $fit  --ext $fit --outdir $outdate-fits $obs
        done
    done
else
    echo "Step $STEP is not one among t2w,fit,plot. Exiting."
fi

