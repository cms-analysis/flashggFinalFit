STEP=0
usage(){
    echo "Script to run fits and plots of fit output."
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

bestfit="../Combine/runFitsxsec_xsec_savedWS/higgsCombine_bestfit_syst_obs_xsec_r_ggH.MultiDimFit.mH125.root"
yields="../Datacard/yields_2023-03-02_xsec"

if [[ $STEP == "spb" ]]; then
    python makeSplusBModelPlot.py --inputWSFile $bestfit --loadSnapshot MultiDimFit --cats all --doZeroes --pdir . --ext _test --unblind
elif [[ $STEP == "catweights" ]]; then
    python getCatInfo.py --inputWSFile $bestfit --cats all --doBkgRenormalization --saveCatInfo --ext _allCats
elif [[ $STEP == "bands" ]]; then
    python makeToys.py --inputWSFile $bestfit --loadSnapshot MultiDimFit --nToys 500 --POIs r_ggH,r_VBF,r_top,r_VH --batch Rome --queue cmsan --ext _test_with_bands
elif [[ $STEP == "spb2-calc" ]]; then
    # first time, with bands calculation
    python makeSplusBModelPlot.py --inputWSFile $bestfit --loadSnapshot MultiDimFit --cats all --doZeroes --pdir . --ext _test_with_bands --unblind --doBands --saveToyYields --doSumCategories --doCatWeights --saveWeights
elif [[ $STEP == "spb2" ]]; then
    # next times, when toys are merged
    python makeSplusBModelPlot.py --inputWSFile $bestfit --loadSnapshot MultiDimFit --cats all --doZeroes --pdir . --ext _test_with_bands --unblind --doBands --loadToyYields SplusBModels_test_with_bands/toys/toyYields_CMS_hgg_mass.pkl --doSumCategories --doCatWeights --saveWeights
elif [[ $STEP == "tables" ]]; then
    # make tables with yields
    groups=("ggh" "qqh" "vh" "top")
    for group in ${groups[*]}
    do
	python makeYieldsTables.py --inputPklDir $yields --loadCatInfo pkl/catInfo_allCats.pkl --group $group
    done
else
    echo "Step $STEP is not one among yields,datacard,links. Exiting."
fi

