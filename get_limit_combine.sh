#!/usr/bin/env bash

set -e

mh=125

mggl=$1
mggh=$2
mx=$3
my=$4
mh=$5
procTemplate=$6

m="mx${mx}my${my}"
mo="mx${mx}my${my}mh${mh}"

pushd Combine  
  echo "Nominal limit being calculated"
  combine --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -M AsymptoticLimits -m ${mh} -d Datacard_${procTemplate}_${m}_${procTemplate}.root -n _AsymptoticLimit_r_${procTemplate}_${mo} --freezeParameters MH,MX,MY --run=blind --setParameters MX=${mx},MY=${my} > combine_results_${procTemplate}_${mo}.txt
  # Toy limits
  #combine --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 -m ${mh} -d Datacard_${procTemplate}_${m}_${procTemplate}.root -n _HybridNew_r_${procTemplate}_${mo} --freezeParameters MH,MX,MY -M HybridNew --LHCmode LHC-limits --expectedFromGrid 0.5 --setParameters MX=${mx},MY=${my} --saveHybridResult --rMin=${l} --rMax=${h} --fork 16 -T 500 > combine_results_${procTemplate}_toys_${mo}.txt
  exp_limit=$(grep 'Expected 50.0%' combine_results_${procTemplate}_${mo}.txt)
  l=$(grep 'Expected 16.0%:' combine_results_${procTemplate}_${mo}.txt)
  h=$(grep 'Expected 84.0%' combine_results_${procTemplate}_${mo}.txt)
  ll=$(grep 'Expected  2.5%' combine_results_${procTemplate}_${mo}.txt)
  hh=$(grep 'Expected 97.5%' combine_results_${procTemplate}_${mo}.txt)
  exp_limit=${exp_limit: -6}
  l=${l: -6}
  h=${h: -6}
  ll=${ll: -6}
  hh=${hh: -6}

  echo "No resonant bkg limit being calculated"
  combine --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -M AsymptoticLimits -m ${mh} -d Datacard_${procTemplate}_${m}_${procTemplate}.root -n _AsymptoticLimit_r_${procTemplate}_${mo} --freezeParameters MH,MX,MY --run=blind --setParameters MX=${mx},MY=${my},res_bkg_scaler=0 > combine_results_${procTemplate}_no_res_bkg_${mo}.txt

  if [[ -n $(grep ABCD Datacard_${procTemplate}_${m}.txt) ]]; then
  echo "No DY bkg limit being calculated"
   combine --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -M AsymptoticLimits -m ${mh} -d Datacard_${procTemplate}_${m}_${procTemplate}.root -n _AsymptoticLimit_r_${procTemplate}_${mo} --freezeParameters MH,MX,MY --freezeNuisanceGroups ABCD --run=expected --setParameters MX=${mx},MY=${my},dy_bkg_scaler=0 > combine_results_${procTemplate}_no_dy_bkg_${mo}.txt
  fi

  echo "No systematics limit being calculated"
  combine --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -M AsymptoticLimits -m ${mh} -d Datacard_${procTemplate}_${m}_${procTemplate}.root -n _AsymptoticLimit_r_${procTemplate}_${mo} --freezeParameters MH,MX,MY,allConstrainedNuisances --run=expected --setParameters MX=${mx},MY=${my} > combine_results_${procTemplate}_no_sys_${mo}.txt
  # Toy limits
  #combine --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 -m ${mh} -d Datacard_${procTemplate}_${m}_${procTemplate}.root -n _HybridNew_r_${procTemplate}_no_sys_${mo} --freezeParameters MH,MX,MY,allConstrainedNuisances -M HybridNew --LHCmode LHC-limits --expectedFromGrid 0.5 --setParameters MX=${mx},MY=${my} --saveHybridResult --rMin=${l} --rMax=${h} --fork 8 -T 5000  > combine_results_${procTemplate}_no_sys_toys_${mo}.txt

  echo "No PDF index floating limit being calculated"
  index_names=$(grep 'discrete' Datacard_${procTemplate}_${m}.txt | cut -d' ' -f1 | sed -z 's/\n/,/g')
  combine -t -1 --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -M MultiDimFit -m ${mh} --rMin $l --rMax $h -d Datacard_${procTemplate}_${m}_${procTemplate}.root -n _Scan_r_test_${mo} --freezeParameters MH,MX,MY --setParameters MX=${mx},MY=${my},r=${exp_limit} --saveSpecifiedIndex $index_names
  index_values=$(python getSavedIndices.py higgsCombine_Scan_r_test_${mo}.MultiDimFit.mH${mh}.root)
  combine --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -M AsymptoticLimits -m ${mh} -d Datacard_${procTemplate}_${m}_${procTemplate}.root -n _AsymptoticLimit_r_${procTemplate}_${mo} --freezeParameters MH,MX,MY,allConstrainedNuisances,${index_names} --run=expected --setParameters MX=${mx},MY=${my}${index_values} > combine_results_${procTemplate}_no_sys_pdfIndexFixed_${mo}.txt


  rm higgsCombine*${mo}*
popd
