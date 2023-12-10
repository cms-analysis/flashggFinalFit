#!/usr/bin/env bash

set -x

source /cvmfs/cms.cern.ch/cmsset_default.sh
source /vols/grid/cms/setup.sh

trees=/home/hep/mdk16/PhD/ggtt/ResonantGGTT/tagging_output/forFinalFits/outputTrees

m=$1
mh=125
#nCats=$2

proc="radionm${m}"

#cd flashggFinalFit
source setup.sh

pushd $trees/2018
  #echo *${m}*
  #echo (*${m}* | wc -w)
  let nCats=$(echo Data*${m}* | wc -w)
  echo "Detected ${nCats} categories"
  rm -rf ${m}
  mkdir -p ${m}
  hadd -f ${m}/${proc}.root ${proc}_${mh}*.root
  hadd -f ${m}/Data.root Data*${proc}*.root
  #hadd -f ${m}/VH.root VH*${proc}cat*.root
popd

pushd Trees2WS
 python trees2ws.py --inputConfig config_ggtt.py --inputTreeFile ${trees}/2018/${m}/${proc}.root --inputMass ${mh} --productionMode ${proc} --year 2018 
 python trees2ws_data.py --inputConfig config_ggtt.py --inputTreeFile ${trees}/2018/${m}/Data.root
 #python trees2ws.py --inputConfig config_ggtt.py --inputTreeFile ${trees}/2018/${m}/VH.root --inputMass 125 --productionMode VH --year 2018
popd

pushd ${trees}/2018/${m}
 mv ws ws_data
 mkdir -p ws/data_2018
 mkdir -p ws/signal_2018

 cp ws_data/Data.root ws/data_2018/allData.root
 cp ws_${proc}/${proc}_${proc}.root ws/signal_2018/output_${proc}_M${mh}_13TeV_pythia8_${proc}.root
 #cp ws_VH/VH_VH.root ws/signal_2018/output_VH_M${mh}_13TeV_pythia8_VH.root
popd

pushd Signal
 cp config_ggtt.py config_ggtt_${m}.py
 sed -i "s;<trees/year/m/ws/signal_year>;${trees}/2018/${m}/ws/signal_2018;g" config_ggtt_${m}.py
 sed -i "s;<m>;${m};g" config_ggtt_${m}.py
 sed -i "s;<mh>;${mh};g" config_ggtt_${m}.py

 if [[ -z $(grep "ggtt_resonant_${m}" tools/replacementMap.py) ]]; then
    sed "s;<m>;${m};g" tools/replacementTemplate.py | sed "s;<proc>;${proc};g" >> tools/replacementMap.py
 fi
 if [[ -z $(grep "ggtt_resonant_${m}" tools/XSBRMap.py) ]]; then
  sed "s;<m>;${m};g" tools/XSBRTemplate.py | sed "s;<proc>;${proc};g" >> tools/XSBRMap.py
 fi

 #sed -i "s/radionm500/${proc}/g" tools/XSBRMap.py
 #sed -i "s/radionm500/${proc}/g" tools/replacementMap.py

 low_bound=$(expr ${mh} - 5)
 high_bound=$(expr ${mh} + 5)
 python RunSignalScripts.py --inputConfig config_ggtt_${m}.py --mode fTest --modeOpts "--doPlots --mass ${mh} --MHLow $low_bound --MHHigh $high_bound"
 #python RunSignalScripts.py --inputConfig config_ggtt_${m}.py --mode fTest --modeOpts "--doPlots"
 python RunSignalScripts.py --inputConfig config_ggtt_${m}.py --mode signalFit --groupSignalFitJobsByCat --modeOpts "--skipSystematics --skipVertexScenarioSplit --replacementThreshold 1000 --MHNominal ${mh} --MHLow $low_bound --MHHigh $high_bound"
 #python RunSignalScripts.py --inputConfig config_ggtt_${m}.py --mode signalFit --groupSignalFitJobsByCat --modeOpts "--skipSystematics --skipVertexScenarioSplit --replacementThreshold 1000"
 python RunPackager.py --cats auto --exts ggtt_resonant_${m} --batch local --massPoints ${mh} --year 2018 --inputWSDir ${trees}/2018/${m}/ws/signal_2018/ #--mergeYears

 pushd outdir_packaged
  for ((i = 0 ; i < ${nCats} ; i++)); do
   mv CMS-HGG_sigfit_packaged_${proc}cat${i}_2018.root CMS-HGG_sigfit_packaged_${proc}cat${i}.root 
  done
 popd

 for ((i = 0 ; i < ${nCats} ; i++)); do
   #python RunPlotter.py --procs ${proc} --cats ${proc}cat${i} --years 2018 --ext packaged --mass ${mh} --MH ${mh}
   python RunPlotter.py --procs ${proc} --cats ${proc}cat${i} --years 2018 --ext packaged
 done
 for ((i = 0 ; i < ${nCats} ; i++)); do
   #python RunPlotter.py --procs VH --cats ${proc}cat${i} --years 2018 --ext packaged --mass ${mh} --MH ${mh}
   python RunPlotter.py --procs VH --cats ${proc}cat${i} --years 2018 --ext packaged
 done
 
 #python RunPlotter.py --procs ${proc},VH --cats all --years 2018 --ext ggtt_resonant_${m} --mass ${mh} --MH ${mh}
 #python RunPlotter.py --procs VH --cats all --years 2018 --ext ggtt_resonant_${m} --mass ${mh} --MH ${mh}
 #python RunPlotter.py --procs all --cats all --years 2018 --ext ggtt_resonant_${m} --mass ${mh} --MH ${mh}

 python RunPlotter.py --procs ${proc} --cats all --years 2018 --ext ggtt_resonant_${m} --mass ${mh} --MH ${mh}
 python RunPlotter.py --procs all --cats all --years 2018 --ext ggtt_resonant_${m} --mass ${mh} --MH ${mh}

 pushd outdir_packaged
  for ((i = 0 ; i < ${nCats} ; i++)); do
    mv CMS-HGG_sigfit_packaged_${proc}cat${i}.root CMS-HGG_sigfit_packaged_${proc}cat${i}_2018.root
  done
 popd
popd

pushd Background
 cp config_ggtt.py config_ggtt_${m}.py
 sed -i "s;<trees/year/m/ws/signal_year>;${trees}/2018/${m}/ws/data_2018;g" config_ggtt_${m}.py
 sed -i "s;<m>;${m};g" config_ggtt_${m}.py
 #python RunBackgroundScripts.py --inputConfig config_ggtt_${m}.py --mode fTestParallel

 low_bound=$(expr ${mh} - 5)
 high_bound=$(expr ${mh} + 5)
 python RunBackgroundScripts_lite.py --inputConfig config_ggtt_${m}.py --mode fTest --modeOpts "--blindingRegion ${low_bound},${high_bound}"
popd

pushd Datacard
 python RunYields.py --inputWSDirMap 2018=${trees}/2018/${m}/ws/signal_2018 --cats auto --procs auto --batch local --ext ggtt_resonant_${m} --mass ${mh}
 #python makeDatacard.py --years 2018 --ext ggtt_resonant_${m} --prune --output Datacard_ggtt_resonant_${m}
 python makeDatacard.py --years 2018 --ext ggtt_resonant_${m} --output Datacard_ggtt_resonant_${m} --mass ${mh}
 #echo "VH_scaler rateParam * VH_*_hgg 1" >> Datacard_ggtt_resonant_${m}.txt
 #echo "nuisance edit freeze VH_scaler" >> Datacard_ggtt_resonant_${m}.txt
 echo "signal_scaler rateParam * radionm* 0.001" >> Datacard_ggtt_resonant_${m}.txt
 echo "nuisance edit freeze signal_scaler" >> Datacard_ggtt_resonant_${m}.txt
popd

pushd Combine
 mkdir -p Models
 mkdir -p Models/signal
 mkdir -p Models/background
 cp ../Signal/outdir_packaged/CMS-HGG*${m}*.root ./Models/signal/
 cp ../Background/outdir_ggtt_resonant_${m}/fTest/output/CMS-HGG*${m}*.root ./Models/background/
 cp ../Datacard/Datacard_ggtt_resonant_${m}.txt Datacard_ggtt_resonant_${m}.txt

 pushd Models/background
  for ((i = 0 ; i < ${nCats} ; i++)); do
    mv CMS-HGG_multipdf_${proc}cat${i}.root CMS-HGG_multipdf_${proc}cat${i}_2018.root
  done
 popd

 #python RunText2Workspace.py --mode mu_inclusive --dryRun
 #./t2w_jobs/t2w_mu_inclusive.sh
 python RunText2Workspace.py --mode  ggtt_w_resonant_bkg --dryRun --ext _ggtt_resonant_${m} --common_opts "-m ${mh} higgsMassRange=65,180"
 ./t2w_jobs/t2w_ggtt_w_resonant_bkg_ggtt_resonant_${m}.sh

 #combine --expectSignal 1 -t -1 --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 -M AsymptoticLimits -m ${mh} -d Datacard_mu_inclusive.root -n _AsymptoticLimit_r --freezeParameters MH --run=blind > combine_results.txt
 #combine --expectSignal 1 -t -1 --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 -M MultiDimFit --algo grid --points 100 -m ${mh} -d Datacard_mu_inclusive.root -n _Scan_r --freezeParameters MH --rMin 0 --rMax 5
 #python plotLScan.py higgsCombine_Scan_r.MultiDimFit.mH${mh}.root 

 combine --expectSignal 1 -t -1 --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 -M AsymptoticLimits -m ${mh} -d Datacard_ggtt_resonant_${m}_ggtt_w_resonant_bkg.root -n _AsymptoticLimit_r_ggtt_resonant_${m} --freezeParameters MH --run=blind > combine_results_ggtt_resonant_${m}.txt
 #combine --expectSignal 1 -t -1 --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 -M AsymptoticLimits -m ${mh} -d Datacard_ggtt_resonant_${m}_ggtt_w_resonant_bkg.root -n _AsymptoticLimit_r_VH_scale_0_ggtt_resonant_${m} --freezeParameters MH --run=blind --setParameters VH_scaler=0 > combine_results_VH_scale_0_ggtt_resonant_${m}.txt
 #combine --expectSignal 1 -t -1 --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 -M AsymptoticLimits -m ${mh} -d Datacard_ggtt_resonant_${m}_ggtt_w_resonant_bkg.root -n _AsymptoticLimit_r_VH_scale_2_ggtt_resonant_${m} --freezeParameters MH --run=blind --setParameters VH_scaler=2 > combine_results_VH_scale_2_ggtt_resonant_${m}.txt
 #combine --expectSignal 1 -t -1 --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 -M MultiDimFit --algo grid --points 100 -m ${mh} -d Datacard_ggtt_w_resonant_bkg.root -n _Scan_r --freezeParameters MH --rMin 0 --rMax 5
 #python plotLScan.py higgsCombine_Scan_r.MultiDimFit.mH${mh}.root
  
 tail combine_results_ggtt_resonant_${m}.txt
popd

mkdir -p CollectedPlots/${proc}
cp -r Signal/outdir_ggtt_resonant_${m}/fTest/Plots 	CollectedPlots/${proc}/SignalfTest
cp -r Signal/outdir_ggtt_resonant_${m}/signalFit/Plots 	CollectedPlots/${proc}/SignalFit
mkdir -p CollectedPlots/${proc}/SignalPackaged
cp -r Signal/outdir_packaged/Plots/*${m}* 		CollectedPlots/${proc}/SignalPackaged/
cp -r Background/outdir_ggtt_resonant_${m}/bkgfTest-Data 	CollectedPlots/${proc}/BackgroundfTest
mkdir -p CollectedPlots/${proc}/Background
cp -r Background/bkgmodel* CollectedPlots/${proc}/Background/
cp Combine/combine_results*_ggtt_resonant_${m}.txt 			CollectedPlots/${proc}/
cp Combine/NLL_scan* 				CollectedPlots/${proc}/
cp Combine/higgsCombine_AsymptoticLimit_r*_ggtt_resonant_${m}.AsymptoticLimits.mH${mh}.root CollectedPlots/${proc}/
