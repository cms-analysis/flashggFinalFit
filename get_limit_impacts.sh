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
  # Get fit results
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
  ##echo $exp_limit


  # Get PDF indices
  index_names=$(grep 'discrete' Datacard_${procTemplate}_${m}.txt | cut -d' ' -f1 | sed -z 's/\n/,/g')
  #echo $index_names
  combine -t -1 --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -M MultiDimFit -m ${mh} --rMin $l --rMax $h -d Datacard_${procTemplate}_${m}_${procTemplate}.root -n _Scan_r_test_${mo} --freezeParameters MH,MX,MY --setParameters MX=${mx},MY=${my},r=${exp_limit} --saveSpecifiedIndex $index_names
  index_values=$(python getSavedIndices.py higgsCombine_Scan_r_test_${mo}.MultiDimFit.mH${mh}.root)
  #echo $index_values


  # Run impacts with PDF indices fixed
  combineTool.py --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -M Impacts -t -1 --robustFit 1 -m ${mh} -d Datacard_${procTemplate}_${m}_${procTemplate}.root -n ${mo} --freezeParameters MH,MX,MY,${index_names} --setParameters MX=${mx},MY=${my},r=${exp_limit}${index_values} --autoMaxPOIs "r" --rMin $ll --rMax $hh --doInitialFit
  combineTool.py --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -M Impacts --robustFit 1 -t -1 -m ${mh} -d Datacard_${procTemplate}_${m}_${procTemplate}.root -n ${mo} --freezeParameters MH,MX,MY,${index_names} --setParameters MX=${mx},MY=${my},r=${exp_limit}${index_values} --autoMaxPOIs "r" --rMin $ll --rMax $hh --doFits --parallel 8
  combineTool.py -M Impacts -m ${mh} -d Datacard_${procTemplate}_${m}_${procTemplate}.root -n ${mo} -o impacts_${mo}.json
  plotImpacts.py -i impacts_${mo}.json -o impacts_${mo}
  python remove_bkg_model_params.py impacts_${mo}.json impacts_no_bkg_${mo}.json
  plotImpacts.py -i impacts_no_bkg_${mo}.json -o impacts_no_bkg_${mo}


  # Get LL scan
  combine -t -1 --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -M MultiDimFit -m ${mh} --algo grid --points 100 --rMin $l --rMax $h -d Datacard_${procTemplate}_${m}_${procTemplate}.root -n _Scan_r_${mo} --freezeParameters MH,MX,MY --setParameters MX=${mx},MY=${my},r=${exp_limit}${index_values}
  combine -t -1 --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -M MultiDimFit -m ${mh} --algo grid --points 100 --rMin $(bc <<< "${exp_limit}-0.005") --rMax $(bc <<< "${exp_limit}+0.005") -d Datacard_${procTemplate}_${m}_${procTemplate}.root -n _Scan_r_fine_${mo} --freezeParameters MH,MX,MY --setParameters MX=${mx},MY=${my},r=${exp_limit}${index_values}
  combine -t -1 --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -M MultiDimFit -m ${mh} --algo grid --points 100 --rMin $l --rMax $h -d Datacard_${procTemplate}_${m}_${procTemplate}.root -n _Scan_r_no_sys_${mo} --freezeParameters MH,MX,MY,allConstrainedNuisances --setParameters MX=${mx},MY=${my},r=${exp_limit}${index_values}
  python plotLScanBasic.py $exp_limit NLL_Scan_${mo} higgsCombine_Scan_r_no_sys_${mo}.MultiDimFit.mH${mh}.root higgsCombine_Scan_r_${mo}.MultiDimFit.mH${mh}.root higgsCombine_Scan_r_fine_${mo}.MultiDimFit.mH${mh}.root 
  
  rm higgsCombine*${mo}*
popd
