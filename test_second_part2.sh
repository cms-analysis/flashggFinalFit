#!/usr/bin/env bash

set -e

#cd /home/hep/mdk16/PhD/ggtt/finalfits_try2/CMSSW_10_2_13/src/flashggFinalFit
cd /home/users/yagu/XYH/FinalFit/CMSSW_10_2_13/src/flashggFinalFit
source /cvmfs/cms.cern.ch/cmsset_default.sh
source setup.sh

# trees=/home/hep/mdk16/PhD/ggtt/ResonantGGTT/Outputs/Y_tautau/outputTrees
# sig_model=/home/hep/mdk16/PhD/ggtt/ResonantGGTT/Outputs/Y_tautau/Interpolation
# res_bkg_model=/home/hep/mdk16/PhD/ggtt/ResonantGGTT/Outputs/Y_tautau/ResonantBkg

# trees=/home/hep/mdk16/PhD/ggtt/ResonantGGTT/Outputs/Graviton/outputTrees
# sig_model=/home/hep/mdk16/PhD/ggtt/ResonantGGTT/Outputs/Graviton/Interpolation
# res_bkg_model=/home/hep/mdk16/PhD/ggtt/ResonantGGTT/Outputs/Graviton/ResonantBkg

# trees=/home/hep/mdk16/PhD/ggtt/ResonantGGTT/Outputs/Radion/outputTrees
# sig_model=/home/hep/mdk16/PhD/ggtt/ResonantGGTT/Outputs/Radion/Interpolation
# res_bkg_model=/home/hep/mdk16/PhD/ggtt/ResonantGGTT/Outputs/Radion/ResonantBkg

# trees=/home/hep/mdk16/PhD/ggtt/ResonantGGTT/Outputs/Y_gg_High_Mass/outputTrees
# sig_model=/home/hep/mdk16/PhD/ggtt/ResonantGGTT/Outputs/Y_gg_High_Mass/Interpolation
# res_bkg_model=/home/hep/mdk16/PhD/ggtt/ResonantGGTT/Outputs/Y_gg_High_Mass/ResonantBkg

trees=/home/users/yagu/XYH/XtoYH_pNN/Outputs/trained/outputTrees
#/home/hep/mdk16/PhD/ggtt/ResonantGGTT/Outputs/Y_gg_Low_Mass/outputTrees
sig_model=/home/users/yagu/XYH/XtoYH_pNN/Interpolation/
#/home/hep/mdk16/PhD/ggtt/ResonantGGTT/Outputs/Y_gg_Low_Mass/Interpolation
res_bkg_model=/home/users/yagu/XYH/XtoYH_pNN/Outputs/Graviton/ResonantBkg/
#/home/hep/mdk16/PhD/ggtt/ResonantGGTT/Outputs/Y_gg_Low_Mass/ResonantBkg
#dy_bkg_model=/home/hep/mdk16/PhD/ggtt/ResonantGGTT/RelicDYEstimation

sig_years="2016 2017 2018"
bkg_years="combined"

proc_template="ggttres"

wait_batch() {
  while [[ -n $(qstat -xml | grep "${1}") ]]; do
    echo $(qstat -xml | grep "${1}" | wc -l) "batch jobs remaining..."
    echo $(qstat -xml -s r | grep "${1}" | wc -l) "batch jobs running..."
    sleep 10
  done
}

get_mx() {
  echo $1 | cut -d'x' -f2 | cut -d'm' -f1
}

get_my() {
  echo $1 | cut -d'y' -f2
}

#graviton, radion, Y->tautau settings
# mggl=100
# mggh=180
# plot_blinding_region="115,135"
# get_mh() {
#   echo 125
# }
# lumiMap="lumiMap = {'2016':36.31, '2017':41.48, '2018':59.83, 'combined':137.65, 'merged':137.65}"

#low mass Y->gg settings
mggl=65
mggh=1000
plot_blinding_region="68,135"
get_mh () {
  echo $(get_my $1)
}
do_scan=1
step_sf=1
lumiMap="lumiMap = {'2016':36.31, '2017':41.48, '2018':54.67, 'combined':132.46, 'merged':132.46}"
do_dy_bkg=0

#high mass Y->gg settings
# mggl=100
# mggh=1000
# plot_blinding_region="115,900"
# get_mh () {
#   echo $(get_my $1)
# }
# do_scan=1
# step_sf=1
# lumiMap="lumiMap = {'2016':36.31, '2017':41.48, '2018':59.83, 'combined':137.65, 'merged':137.65}"

sed -i "/lumiMap/s/.*/${lumiMap}/" tools/commonObjects.py

for year in $bkg_years ; do
  masses=$(python detect_mass_points.py ${trees}/${year})
done
echo "Detected mass points:" $masses

for year in $bkg_years ; do
  pushd ${trees}/${year}
    for m in $masses ; do
      let nCats=$(echo Data*${m}* | wc -w)
      let nCR=$(echo Data*${m}*cr_* | wc -w)
      echo "Detected $nCR control regions"
      let nCats=${nCats}-${nCR}
      echo "Detected ${nCats} categories"
      popd
      break 2
    done
done

pushd Background

  #check jobs successful
  for ((i = 0 ; i < ${nCats} ; i++)); do
    for year in $bkg_years ; do
      for m in $masses ; do

        proc=${proc_template}${m}
        if ! test -f outdir_ggtt_resonant_${m}/fTest/output/CMS-HGG_multipdf_${proc}cat${i}.root; then
          failed_jobs=${failed_jobs}"${year} ${m} cat${i} 0.01 -> 0.005 \n"
          echo ${year} ${m} cat${i}
#          pushd outdir_ggtt_resonant_${year}_${m}/fTest/jobs
          pushd outdir_ggtt_resonant_${m}/fTest/jobs
            sed -i 's/--gofCriteria 0.01/--gofCriteria 0.005/g' sub_fTest_ggtt_resonant_${m}_${proc}cat${i}.sh
            set +e
            ./sub_fTest_ggtt_resonant_${m}_${proc}cat${i}.sh >> rerunning_background.log #2>&1
            set -e
          popd
        fi

        if ! test -f outdir_ggtt_resonant_${m}/fTest/output/CMS-HGG_multipdf_${proc}cat${i}.root; then
          failed_jobs=${failed_jobs}"${year} ${m} cat${i} 0.005 -> 0.001 \n"
          pushd outdir_ggtt_resonant_${year}_${m}/fTest/jobs
            sed -i 's/--gofCriteria 0.005/--gofCriteria 0.001/g' sub_fTest_ggtt_resonant_${m}_${proc}cat${i}.sh
            set +e
            ./sub_fTest_ggtt_resonant_${m}_${proc}cat${i}.sh >> rerunning_background.log 2>&1
            set -e
          popd
        fi

        if ! test -f outdir_ggtt_resonant_${m}/fTest/output/CMS-HGG_multipdf_${proc}cat${i}.root; then
          failed_jobs=${failed_jobs}"${year} ${m} cat${i} 0.001 -> 0.0 \n"
          pushd outdir_ggtt_resonant_${year}_${m}/fTest/jobs
            sed -i 's/--gofCriteria 0.001/--gofCriteria 0.0/g' sub_fTest_ggtt_resonant_${m}_${proc}cat${i}.sh
            ./sub_fTest_ggtt_resonant_${m}_${proc}cat${i}.sh >> rerunning_background.log 2>&1
          popd
        fi

        #mv outdir_ggtt_resonant_${year}_${m}/fTest/output/CMS-HGG_multipdf_${proc}cat${i}.root outdir_ggtt_resonant_${year}_${m}/fTest/output/CMS-HGG_multipdf_${proc}cat${i}_${year}.root

      done
    done
  done

### not sure how the 3 line renaming works...
  for year in $bkg_years ; do
    rename .root _${year}.root outdir_ggtt_resonant_${year}_*/fTest/output/*.root
  done
#####
  echo -e $failed_jobs
popd

