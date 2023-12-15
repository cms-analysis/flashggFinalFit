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
  # low mass dy-related commands
  #if [[ -n $(grep ABCD Datacard_${procTemplate}_${m}.txt) ]]; then
  #  combine --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -M FitDiagnostics -m ${mh} -d Datacard_${procTemplate}_${m}_${procTemplate}.root -n _AsymptoticLimit_r_${procTemplate}_${mo} --freezeParameters MH,MX,MY --setParameters MX=${mx},MY=${my} --plots --skipSBFit --rebinFactor 4
    combine --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 -M AsymptoticLimits -m ${mh} -d Datacard_${procTemplate}_${m}_${procTemplate}.root -n _AsymptoticLimit_r_${procTemplate}_${mo} --freezeParameters MH,MX,MY --freezeNuisanceGroups ABCD --run=expected --setParameters MX=${mx},MY=${my},dy_bkg_scaler=0 > combine_results_${procTemplate}_no_dy_bkg_${mo}.txt
  #fi

  combine --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -M AsymptoticLimits -m ${mh} -d Datacard_${procTemplate}_${m}_${procTemplate}.root -n _AsymptoticLimit_r_${procTemplate}_${mo} --freezeParameters MH,MX,MY --run=expected --setParameters MX=${mx},MY=${my} > combine_results_${procTemplate}_${mo}.txt
  combine --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -M AsymptoticLimits -m ${mh} -d Datacard_${procTemplate}_${m}_${procTemplate}.root -n _AsymptoticLimit_r_${procTemplate}_${mo} --freezeParameters MH,MX,MY --run=expected --setParameters MX=${mx},MY=${my},res_bkg_scaler=0 > combine_results_${procTemplate}_no_res_bkg_${mo}.txt
  combine --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -M AsymptoticLimits -m ${mh} -d Datacard_${procTemplate}_${m}_${procTemplate}.root -n _AsymptoticLimit_r_${procTemplate}_${mo} --freezeParameters MH,MX,MY,allConstrainedNuisances --run=expected --setParameters MX=${mx},MY=${my} > combine_results_${procTemplate}_no_sys_${mo}.txt

  exp_limit=$(grep 'Expected 50.0%' combine_results_${procTemplate}_${mo}.txt)
  l=$(grep 'Expected 16.0%:' combine_results_${procTemplate}_${mo}.txt)
  h=$(grep 'Expected 84.0%' combine_results_${procTemplate}_${mo}.txt)
  ll=$(grep 'Expected  2.5%' combine_results_${procTemplate}_${mo}.txt)
  hh=$(grep 'Expected 97.5%' combine_results_${procTemplate}_${mo}.txt)
  exp_limit=${exp_limit: -6}
  l=${l: -6}
  h=${h: -6}
  ll=${l: -6}
  hh=${h: -6}

  # combine --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 -m ${mh} -d Datacard_${procTemplate}_${m}_${procTemplate}.root -n _HybridNew_r_${procTemplate}_${mo} --freezeParameters MH,MX,MY -M HybridNew --LHCmode LHC-limits --expectedFromGrid 0.5 --setParameters MX=${mx},MY=${my} --saveHybridResult --rMin=${l} --rMax=${h} --fork 16 -T 500 > combine_results_${procTemplate}_toys_${mo}.txt
  # combine --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 -m ${mh} -d Datacard_${procTemplate}_${m}_${procTemplate}.root -n _HybridNew_r_${procTemplate}_no_sys_${mo} --freezeParameters MH,MX,MY,allConstrainedNuisances -M HybridNew --LHCmode LHC-limits --expectedFromGrid 0.5 --setParameters MX=${mx},MY=${my} --saveHybridResult --rMin=${l} --rMax=${h} --fork 8 -T 5000  > combine_results_${procTemplate}_no_sys_toys_${mo}.txt

#  if [[ -n $(python should_do_impacts.py ${mx} ${my} ${mh}) ]]; then
    #index_names=$(grep 'discrete' Datacard_${procTemplate}_${m}.txt | cut -d' ' -f1 | sed -z 's/\n/,/g')
    #combine -t -1 --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 -M MultiDimFit -m ${mh} --rMin $l --rMax $h -d Datacard_${procTemplate}_${m}_${procTemplate}.root -n _Scan_r_test_${mo} --freezeParameters MH,MX,MY --setParameters MX=${mx},MY=${my},r=${exp_limit} --saveSpecifiedIndex $index_names
    #index_values=$(python getSavedIndices.py higgsCombine_Scan_r_test_${mo}.MultiDimFit.mH${mh}.root)

    # combine -t -1 --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 -M MultiDimFit -m ${mh} --algo grid --points 100 --rMin $l --rMax $h -d Datacard_${procTemplate}_${m}_${procTemplate}.root -n _Scan_r_${mo} --freezeParameters MH,MX,MY --setParameters MX=${mx},MY=${my},r=${exp_limit}${index_values}
    # combine -t -1 --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 -M MultiDimFit -m ${mh} --algo grid --points 100 --rMin $(bc <<< "${exp_limit}-0.005") --rMax $(bc <<< "${exp_limit}+0.005") -d Datacard_${procTemplate}_${m}_${procTemplate}.root -n _Scan_r_fine_${mo} --freezeParameters MH,MX,MY --setParameters MX=${mx},MY=${my},r=${exp_limit}${index_values}
    # combine -t -1 --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 -M MultiDimFit -m ${mh} --algo grid --points 100 --rMin $l --rMax $h -d Datacard_${procTemplate}_${m}_${procTemplate}.root -n _Scan_r_no_sys_${mo} --freezeParameters MH,MX,MY,allConstrainedNuisances --setParameters MX=${mx},MY=${my},r=${exp_limit}${index_values}
    # python plotLScanBasic.py $exp_limit NLL_Scan_${mo} higgsCombine_Scan_r_no_sys_${mo}.MultiDimFit.mH${mh}.root higgsCombine_Scan_r_${mo}.MultiDimFit.mH${mh}.root higgsCombine_Scan_r_fine_${mo}.MultiDimFit.mH${mh}.root 

    #python ~/XYH/FinalFit/CMSSW_10_2_13/bin/slc7_amd64_gcc700/combineTool.py -t -1 --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 -M Impacts -m ${mh} -d Datacard_${procTemplate}_${m}_${procTemplate}.root --freezeParameters MH,MX,MY,${index_names} --setParameters MX=${mx},MY=${my},r=${exp_limit}${index_values} --doInitialFit -n ${mo}
    #python ~/XYH/FinalFit/CMSSW_10_2_13/bin/slc7_amd64_gcc700/combineTool.py -t -1 --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 -M Impacts -m ${mh} -d Datacard_${procTemplate}_${m}_${procTemplate}.root --freezeParameters MH,MX,MY,${index_names} --setParameters MX=${mx},MY=${my},r=${exp_limit}${index_values} --doFits --parallel 8 -n ${mo}
    #python ~/XYH/FinalFit/CMSSW_10_2_13/bin/slc7_amd64_gcc700/combineTool.py -M Impacts -d Datacard_${procTemplate}_${m}_${procTemplate}.root -m ${mh} -o impacts_${mo}.json -n ${mo}
    #python ~/XYH/FinalFit/CMSSW_10_2_13/bin/slc7_amd64_gcc700/plotImpacts.py -i impacts_${mo}.json -o impacts_${mo}
    #python3 remove_bkg_model_params.py impacts_${mo}.json impacts_no_bkg_${mo}.json
    #python ~/XYH/FinalFit/CMSSW_10_2_13/bin/slc7_amd64_gcc700/plotImpacts.py -i impacts_no_bkg_${mo}.json -o impacts_no_bkg_${mo}
#  fi
  
  rm higgsCombine*${mo}*
popd
