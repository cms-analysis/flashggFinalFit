#!/usr/bin/env bash

set -e

trees=/home/users/evourlio/public_html/XToYHToggbb_pNN/plots_2023-11-21/trained_invertedFinalState/outputTrees
sig_model=/home/users/evourlio/public_html/XToYHToggbb_pNN/plots_2023-11-21/trained_invertedFinalState/Interpolation/
res_bkg_model=/home/users/evourlio/public_html/XToYHToggbb_pNN/plots_2023-11-21/trained_invertedFinalState/ResonantBkg
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

# H->gg settings
mggl=100
mggh=180
plot_blinding_region="115,135"
get_mh() {
  echo 125
}
lumiMap="lumiMap = {'2016':36.31, '2017':41.48, '2018':59.83, 'combined':137.65, 'merged':137.65}"

# low mass Y->gg settings
#mggl=65
#mggh=1000
#plot_blinding_region="68,135"
#get_mh () {
#  echo $(get_my $1)
#}
#do_scan=1
#step_sf=1
#lumiMap="lumiMap = {'2016':36.31, '2017':41.48, '2018':54.67, 'combined':132.46, 'merged':132.46}"
do_dy_bkg=0

# high mass Y->gg settings
#mggl=100
#mggh=1000
#plot_blinding_region="115,900"
#get_mh () {
#  echo $(get_my $1)
#}
#do_scan=1
#step_sf=1
#lumiMap="lumiMap = {'2016':36.31, '2017':41.48, '2018':59.83, 'combined':137.65, 'merged':137.65}"

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

pushd Combine
 mkdir -p Models
 mkdir -p Models/signal
 mkdir -p Models/res_bkg
 #mkdir -p Models/dy_bkg
 mkdir -p Models/background
 cp ../SignalModelInterpolation/outdir/* ./Models/signal/
 cp ../SignalModelInterpolation/res_bkg_outdir/* ./Models/res_bkg/
#  if [[ -n $do_dy_bkg ]]; then 
#     cp ../SignalModelInterpolation/dy_bkg_outdir/* ./Models/dy_bkg/
#  fi
 set +e
 cp ../Background/outdir_ggtt_resonant_*/fTest/output/CMS-HGG*.root ./Models/background/
 set -e
 cp ../Datacard/Datacard_ggtt_resonant*.txt .

 for m in $masses ; do
  . ../get_limit_workspace.sh $mggl $mggh $(get_mx $m) $(get_my $m) $(get_mh $m)
  #echo "fake"
  #qsub -q hep.q -l h_rt=3600 ../get_limit_workspace.sh $mggl $mggh $(get_mx $m) $(get_my $m) $(get_mh $m)
  #qsub -q hep.q -l h_rt=7200 -pe hep.pe 16 ../get_limit_workspace.sh $mggl $mggh $(get_mx $m) $(get_my $m) $(get_mh $m)
 done
