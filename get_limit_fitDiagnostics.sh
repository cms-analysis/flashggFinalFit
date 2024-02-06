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
# Asymptotic limits
  echo "Nominal fit being done"
  combine --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -M FitDiagnostics -m ${mh} -d Datacard_${procTemplate}_${m}_${procTemplate}.root -n _FitDiagnostics_r_${procTemplate}_${mo} --freezeParameters MH,MX,MY --setParameters MX=${mx},MY=${my}

  echo "No resonant bkg fit being done"
  combine --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -M FitDiagnostics -m ${mh} -d Datacard_${procTemplate}_${m}_${procTemplate}.root -n _FitDiagnostics_r_${procTemplate}_no_res_bkg_${mo} --freezeParameters MH,MX,MY --setParameters MX=${mx},MY=${my},res_bkg_scaler=0

  if [[ -n $(grep ABCD Datacard_${procTemplate}_${m}.txt) ]]; then
    echo "No DY bkg fit being done"
    combine --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -M FitDiagnostics -m ${mh} -d Datacard_${procTemplate}_${m}_${procTemplate}.root -n _FitDiagnostics_r_${procTemplate}_no_dy_bkg_${mo} --freezeParameters MH,MX,MY --freezeNuisanceGroups ABCD --setParameters MX=${mx},MY=${my},dy_bkg_scaler=0
  fi

  echo "No systematics fit being done"
  combine --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -M FitDiagnostics -m ${mh} -d Datacard_${procTemplate}_${m}_${procTemplate}.root -n _FitDiagnostics_r_${procTemplate}_no_sys_${mo} --freezeParameters MH,MX,MY,allConstrainedNuisances --setParameters MX=${mx},MY=${my}

  echo "No PDF index floating fit being done"
  index_names=$(grep 'discrete' Datacard_${procTemplate}_${m}.txt | cut -d' ' -f1 | sed -z 's/\n/,/g')
  combine -t -1 --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -M MultiDimFit -m ${mh} --rMin $l --rMax $h -d Datacard_${procTemplate}_${m}_${procTemplate}.root -n _Scan_r_test_${mo} --freezeParameters MH,MX,MY --setParameters MX=${mx},MY=${my},r=${exp_limit} --saveSpecifiedIndex $index_names
  index_values=$(python getSavedIndices.py higgsCombine_Scan_r_test_${mo}.MultiDimFit.mH${mh}.root)
  combine --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -M FitDiagnostics -m ${mh} -d Datacard_${procTemplate}_${m}_${procTemplate}.root -n _FitDiagnostics_r_${procTemplate}_no_sys_pdfIndexFixed_${mo} --freezeParameters MH,MX,MY,allConstrainedNuisances,${index_names} --setParameters MX=${mx},MY=${my}${index_values}
popd
