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

fits=( "ALT_L1" "ALT_L1Zg" "ALT_0PH" "ALT_0M")
fits=( "ALT_0M")
ext2=("GGH" "VBF" "VHHAD"  "TTH" "VH_LEP" "WH_LEP" "ZH_LEP" )


if [[ $STEP == "t2w" ]]; then
    for ext in ${ext2[*]}
    do
        python RunText2Workspace.py --ext ${ext} --mode ALT_0M 
    done
elif [[ $STEP == "fit" ]]; then
    for obs in " " 
   # " --doObserved "
    do
        for fit in ${fits[*]}
        do
            for ext in ${ext2[*]}
            do
            python RunFits.py --inputJson inputs.json --ext $fit_$ext --mode $fit  ${DROPT} $obs
            done 
        done
    done
elif [[ $STEP == "collect" ]]; then
    for obs in " "
    # " --doObserved "
    do
	for fit in ${fits[*]}
	do
            for ext in ${ext2[*]}
            do
        #    python RunFits.py --inputJson inputs.json --ext $fit$ext --mode $fit  ${DROPT} $obs
	    python CollectFits.py --inputJson inputs.json --ext $fit_$ext --mode $fit $obs
	done
   done
   done
elif [[ $STEP == "plot" ]]; then
    for obs in " " 
   #" --doObserved "
    do
        for fit in ${fits[*]}
        do
           string="runFitsTTH_ALT_0M/profile1D_syst_TTH_CMS_zz4l_fai1.root:TTH:2 runFitsVBF_ALT_0M/profile1D_syst_VBF_CMS_zz4l_fai1.root:VBF:3 runFitsVHHAD_ALT_0M/profile1D_syst_VHHAD_CMS_zz4l_fai1.root:VHHAD:4  runFitsVH_LEP_ALT_0M/profile1D_syst_VH_LEP_CMS_zz4l_fai1.root:VH-MET:9 runFitsWH_LEP_ALT_0M/profile1D_syst_WH_LEP_CMS_zz4l_fai1.root:WH-LEP:6 runFitsZH_LEP_ALT_0M/profile1D_syst_ZH_LEP_CMS_zz4l_fai1.root:ZH-LEP:46"
           plot1DScan.py runFitsGGH_ALT_0M/profile1D_syst_GGH_CMS_zz4l_fai1.root   --y-cut 30 --y-max 30 -o  plots/Breakdown --POI CMS_zz4l_fai1 --main-label GGH --translate ../Plots/pois_fa3.json --others $string
        done
    done
else
    echo "Step $STEP is not one among t2w,fit,plot. Exiting."
fi

