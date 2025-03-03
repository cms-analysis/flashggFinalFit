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



fits=( "ALT_L1" "ALT_L1Zg" "ALT_0PH" "ALT_0M") 
fits=(  "ALT_0M") 






if [[ $STEP == "spb" ]]; then #STEP TO USE TO PRODUCE THE PLOT WITHOUT THE BANDS
    for fit in ${fits[*]} 
    do
	python  makeSplusBModelPlot.py --inputWSFile ../Combine/Datacard_$fit.root --cats all --doZeroes --ext Unblind_spb_$fit --blindingRegion 125,125 --mass 125.38 --translateCats cats_latex.json
    done

elif [[ $STEP == "spb_test" ]]; then #STEP TO USE TO PRODUCE THE PLOT WITHOUT THE BANDS
    for fit in ${fits[*]} 
    do
	python  makeSplusBModelPlot.py --doCatWeights --inputWSFile ../Combine/Datacard_$fit.root --cats  RECO_VBFTOPO_ACVBFBSM_Tag0 --doZeroes  --blindingRegion 125,125 --mass 125.38 --translateCats cats_latex.json
    done
elif [[ $STEP == "bands" ]]; then
    for fit in ${fits[*]} 
    do
	python makeToys.py --outputDir /eos/home-f/fderiggi/AC/SplusBModelsUnblind_v2_$fit --inputWSFile ../Combine/Datacard_$fit.root   --nToys 500 --POIs CMS_zz4l_fai1  --batch condor --queue tomorrow --ext Unblind_test_with_bands_v2_$fit
    done
  elif [[ $STEP == "spb2-calc" ]]; then
    for fit in ${fits[*]} 
    do
	python makeSplusBModelPlot.py --doCatWeights --toydir /eos/home-f/fderiggi/AC/SplusBModelsUnblind_$fit --inputWSFile ../Combine/Datacard_$fit.root  --cats all --doZeroes --ext  Unblind_test_with_bands_$fit --mass 125.38 --blindingRegion 125,125 --translateCats cats_latex.json --doBands --doToyVeto --saveToyYields
    done  

elif [[ $STEP == "spb2" ]]; then
    # next times, when toys are merged
    python makeSplusBModelPlot.py --inputWSFile $bestfit --loadSnapshot MultiDimFit --cats all --doZeroes --pdir . --ext $ext ---blindingRegion 125,125 --doBands --loadToyYields SplusBModelsUnblind_test_with_bands/toys/toyYields_CMS_hgg_mass.pkl --doSumCategories --doCatWeights --saveWeights

else
    echo "Step $STEP is not one among yields,datacard,links. Exiting."
fi

