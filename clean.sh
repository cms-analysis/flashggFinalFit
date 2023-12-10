#!/usr/bin/env bash

set -x
#set -e

#trees=/home/hep/mdk16/PhD/ggtt/ResonantGGTT/Outputs/Radion/outputTrees
#trees=/home/hep/mdk16/PhD/ggtt/ResonantGGTT/Outputs/Graviton/outputTrees
#trees=/home/hep/mdk16/PhD/ggtt/ResonantGGTT/Outputs/NMSSM_Y_tautau/outputTrees
#trees=/home/hep/mdk16/PhD/ggtt/ResonantGGTT/Outputs/Y_gg_High_Mass/outputTrees
#trees=/home/hep/mdk16/PhD/ggtt/ResonantGGTT/Outputs/Y_gg_Low_Mass/outputTrees
#trees=/home/hep/mdk16/PhD/ggtt/ResonantGGTT/Outputs/NMSSM_Y_gg_Low_Mass_HLT/outputTrees

trees=/home/hep/mdk16/PhD/ggtt/ResonantGGTT/Outputs/Y_gg_Low_Mass/LimitVsMinNum/10/outputTrees

pushd $trees
 rm -r 2016/*/
 rm -r 2017/*/
 rm -r 2018/*/
 rm -r combined/*/
popd

#cd flashggFinalFit

pushd Signal
 rm -r outdir*/
 rm config_ggtt_*.py*
 sed -i '/ggtt_resonant/d' tools/replacementMap.py
 sed -i -e :a -e '/^\n*$/{$d;N;ba' -e '}' tools/replacementMap.py #remove blank lines at end
 sed -i '/ggtt_resonant/d' tools/XSBRMap.py
 sed -i -e :a -e '/^\n*$/{$d;N;ba' -e '}' tools/XSBRMap.py #remove blank lines at end
popd 

pushd SignalModelInterpolation
  rm -r outdir
  rm -r res_bkg_outdir
popd

pushd Background
 rm -r outdir*/
 rm config_ggtt_*mx*.py*
 rm bkgmodel*.pdf
 rm bkgmodel*.png
 rm -r plots
popd

pushd Datacard
 rm -r yields*/
 rm Datacard*.txt
popd

pushd Combine
 rm -r Models
 rm -r runFits_mu_inclusive
 rm -r t2w_jobs
 rm Datacard*.txt 
 rm *.root
 rm combine_results*.txt
 rm impacts*
 rm NLL_Scan*
 rm ggttres*.png
popd
