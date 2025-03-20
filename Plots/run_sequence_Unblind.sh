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
fits=( "ALT_0M" ) 





if [[ $STEP == "spb" ]]; then #STEP TO USE TO PRODUCE THE PLOT WITHOUT THE BANDS
    for fit in ${fits[*]} 
    do
	python  makeSplusBModelPlot.py --inputWSFile ../Combine/Datacard_$fit.root --cats all --doZeroes --ext Unblind_spb_$fit --blindingRegion 125,125 --mass 125.38 
    done

elif [[ $STEP == "spb_sb_fit" ]]; then #STEP TO USE TO PRODUCE THE PLOT WITHOUT THE BANDS with s fit
    for fit in ${fits[*]} 
    do
	python  makeSplusBModelPlot.py  --inputWSFile ../Combine/runFitsALT_0M_ALT_0M/higgsCombine_bestfit_syst_obs_ALT_0M_CMS_zz4l_fai1.MultiDimFit.mH125.38.root --cats all --doZeroes --ext Unblind_spb_sb_fit_$fit --unblind --mass 125.38 
    done

elif [[ $STEP == "bands_sb_fit" ]]; then
    for fit in ${fits[*]} 
    do
	python makeToys.py --outputDir /eos/home-f/fderiggi/AC/SplusBModelsUnblind_v4_$fit --inputWSFile /eos/cms/store/group/phys_higgs/cmshgg/fderiggi/runFits_Unblind/runFitsALT_0M_ALT_0M/higgsCombine_bestfit_syst_obs_ALT_0M_CMS_zz4l_fai1.MultiDimFit.mH125.38.root  --nToys 100 --POIs CMS_zz4l_fai1,muV.muf  --batch condor --queue tomorrow --ext Unblind_test_with_bands_v4_$fit
    done
  elif [[ $STEP == "spb2-calc" ]]; then
     cat='all'
    for fit in ${fits[*]} 
    do
      
	python makeSplusBModelPlot.py  --cats ${cat} --loadSnapshot MultiDimFit --translateCats cats.json  --toydir  /eos/home-f/fderiggi/AC/SplusBModelsUnblind_v3_$fit  --inputWSFile /eos/cms/store/group/phys_higgs/cmshgg/fderiggi/runFits_Unblind//runFitsALT_0M_ALT_0M/higgsCombine_bestfit_syst_obs_ALT_0M_CMS_zz4l_fai1.MultiDimFit.mH125.38.root  --doSumCategories --doCatWeights --doZeroes --ext Unblind_test_with_bands_v3_$fit --mass 125.38 --unblind --doBands --doToyVeto  --saveToyYields --saveWeights 
  
    done  

elif [[ $STEP == "spb2" ]]; then
    # next times, when toys are merged
    python makeSplusBModelPlot.py --inputWSFile $bestfit --loadSnapshot MultiDimFit --cats all --doZeroes --pdir . --ext $ext ---blindingRegion 125,125 --doBands --loadToyYields SplusBModelsUnblind_test_with_bands/toys/toyYields_CMS_hgg_mass.pkl --doSumCategories --doCatWeights --saveWeights




elif [[ $STEP == "makeJson" ]]; then
    # next times, when toys are merged
    python makeSplusBModelPlot.py  --cats all --loadSnapshot MultiDimFit --translateCats cats.json    --inputWSFile ../Combine/Datacard_ALT_0M.root  --doSumCategories --doCatWeights --doZeroes --ext fa3  --mass 125.38 --unblind   --saveWeights  --doYield



elif [[ $STEP == "makePlot" ]]; then
    # next times, when toys are merged
    python3 makeYieldPlot.py --cats RECO_VBFTOPO_ACGGH_Tag0,RECO_VBFTOPO_ACGGH_Tag1,RECO_VBFTOPO_ACVBFSM_Tag0,RECO_VBFTOPO_ACVBFBSM_Tag0,RECO_VBFTOPO_ACVBFBSM_Tag1  --out VBF

    python3 makeYieldPlot.py --cats RECO_VH_MET_Tag0,RECO_VH_MET_Tag1,RECO_VH_MET_Tag2,RECO_VH_MET_Tag3,RECO_WH_LEP_Tag0,RECO_WH_LEP_Tag1,RECO_WH_LEP_Tag2,RECO_WH_LEP_Tag3,RECO_ZH_LEP_Tag0,RECO_ZH_LEP_Tag1 --out VHLEP

    python3 makeYieldPlot.py --cats  RECO_VBFTOPO_ACVHHADBSM_Tag0,RECO_VBFTOPO_ACVHHADBSM_Tag1,RECO_VBFTOPO_ACVHHADSM_Tag0,RECO_VBFTOPO_ACVHHADSM_Tag1,RECO_VBFTOPO_ACVHHADSM_Tag2 --out VHHAD




else
    echo "Step $STEP is not one among the listed ones. Exiting."


fi
















