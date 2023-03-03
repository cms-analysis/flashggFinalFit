outdate=`date +%F` 

STEP=0
usage(){
    echo "Script to run yields and datacard making. Yields need to be done before running datacards"
    echo "options:"
    
    echo "-h|--help) "
    echo "-s|--step) "
}
# options may be followed by one colon to indicate they have a required argument
if ! options=$(getopt -u -o s:h -l help,step: -- "$@")
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
(--) shift; break;;
(-*) usage; echo "$0: error - unrecognized option $1" 1>&2; usage >> /dev/stderr; exit 1;;
(*) break;;
esac
shift
done

fits=("xsec" "ALT_L1" "ALT_L1Zg" "ALT_0PH" "ALT_0M")

if [[ $STEP == "t2w" ]]; then
    for fit in ${fits[*]}
    do
        python RunText2Workspace.py --ext $fit --mode $fit --batch Rome
    done
elif [[ $STEP == "fit" ]]; then
    for obs in " " " --doObserved "
    do
        for fit in ${fits[*]}
        do
            python RunFits.py --inputJson inputs.json --ext $fit --mode $fit --batch local $obs
        done
    done
elif [[ $STEP == "plot" ]]; then
    #for obs in " " " --doObserved "
    for obs in " "
    do
        for fit in ${fits[*]}
        do
            python PlotScans.py --inputJson inputs.json --mode $fit  --ext $fit --outdir $outdate-fits $obs
        done
    done
else
    echo "Step $STEP is not one among t2w,fit,plot. Exiting."
fi

