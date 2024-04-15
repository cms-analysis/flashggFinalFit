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
ext2=("_WHLEP_VHLEP_MET" "_VHLEP_MET" "_VHLEP_new_syst")

if [[ $STEP == "t2w" ]]; then
    for fit in ${fits[*]}
    do
        python RunText2Workspace.py --ext $fit --mode $fit --batch Rome
    done
elif [[ $STEP == "fit" ]]; then
    for obs in " " 
   # " --doObserved "
    do
        for fit in ${fits[*]}
        do
            for ext in ${ext2[*]}
            do
            python RunFits.py --inputJson inputs.json --ext $fit$ext --mode $fit  ${DROPT} $obs
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
	    python CollectFits.py --inputJson inputs.json --ext $fit$ext --mode $fit $obs
	done
   done
   done
elif [[ $STEP == "plot" ]]; then
    for obs in " " 
   #" --doObserved "
    do
        for fit in ${fits[*]}
        do
            python PlotScans.py --inputJson inputs.json --mode $fit  --ext $fit --outdir $outdate-fits $obs
        done
    done
elif [[ $STEP == "impacts-initial" ]]; then
    for fit in ${fits[*]} 
    do
	python RunImpacts.py --inputJson inputs.json --ext $fit --mode $fit --queue workday   ${DROPT}
    done
elif [[ $STEP == "impacts-scans" ]]; then
    for fit in ${fits[*]}
    do
	python RunImpacts.py --inputJson inputs.json --ext $fit --mode $fit --doFits  --queue tomorrow  ${DROPT}
    done
elif [[ $STEP == "impacts-collect" ]]; then
    for fit in ${fits[*]}
    do
	cd runImpacts${fit}_${fit}
	echo "Making JSON file for fit $fit It might take time, depending on the number of parameters..."
	##combineTool.py -M Impacts -n _bestfit_syst_${fit}_initialFit -d ../Datacard_${fit}.root -i impacts_${fit}.json -m 125.38 -o impacts_${poi}.json
	if [[ $fit == "xsec" ]]; then 
	    pois=("r_ggH" "r_VBF" "r_VH" "r_top")
	    translate="pois_mu.json"
   else 
       pois=("CMS_zz4l_fai1")
       translate="pois_fa3.json"
	fi
	for poi in ${pois[*]}
	do

	#combineTool.py -M Impacts -n _bestfit_syst_${fit}_initialFit -d ../Datacard_${fit}.root -i impacts_${fit}.json -m 125.38 -o impacts_${poi}
	    echo "    ===> Producing impact plots for the *** main-only *** systematics for fit: === $fit === and POI: == $poi === "
       
	    #combineTool.py -M Impacts -n _bestfit_syst_${fit}_initialFit -d ../Datacard_${fit}.root -i impacts_${fit}.json -m 125.38 -o impacts_${poi}.json -P ${poi}
	    plotImpacts.py   -i impacts_${poi}.json -o impacts_${poi}_${fit} --POI ${poi}  --max-pages 1
#--translate "../../Plots/pois_${fit}.json" --max-pages 1
	done
	cd -
    done
else
    echo "Step $STEP is not one among t2w,fit,plot. Exiting."
fi

