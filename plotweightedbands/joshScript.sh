#!/bin/bash
MHhat=125.97
Muhat=0.95
((startIndex=$1*10000))
index=$startIndex

#CMS-HGG_mva_13TeV_datacardMuScan_postFit.root

#cd /vols/cms02/lc1113/FinalFits_Feb15_2/CMSSW_7_1_5/src/flashggFinalFit/Plots/FinalResults/plotweightedbands
cd /vols/cms/lc1113/FinalFits_June16_0/CMSSW_7_4_7/src/flashggFinalFit/plotweightedbands
eval `scramv1 runtime -sh`


while (( $index < $startIndex+ 5)); 
do
echo "---> combine cms_hgg_datacard_FiducialRDiffXsScan_postFit.root -m $MHhat --snapshotName MultiDimFit -M GenerateOnly --saveWorkspace --toysFrequentist --bypassFrequentistFit -t 1 --expectSignal=$Muhat -n combout_step0_$index -s -1"
combine higgsCombineCMS-HGG_mva_13TeV_datacardMuScan_postFit.ProfileMH.root  -m $MHhat --snapshotName MultiDimFit -M GenerateOnly --saveWorkspace --toysFrequentist --bypassFrequentistFit -t 1 --expectSignal=$Muhat -n combout_step0_$index -s -1

ls higgsCombinecombout_step0_${1}*.root
mv higgsCombinecombout_step0_${1}*.root higgsCombinecombout_step0_done_$index.root

echo "---> combine higgsCombinecombout_step0_done_$index.root -m $MHhat -M MultiDimFit --floatOtherPOIs=1 --saveWorkspace --toysFrequentist --bypassFrequentistFit -t 1 --expectSignal=$Muhat -n combout_step1_$index -s -1"
combine higgsCombinecombout_step0_done_$index.root -m $MHhat -M MultiDimFit --floatOtherPOIs=1 --saveWorkspace --toysFrequentist --bypassFrequentistFit -t 1 --expectSignal=$Muhat -n combout_step1_$index -s -1
#combine higgsCombinecombout_step0_done_$index.root -m $MHhat -M MultiDimFit --floatOtherPOIs=1 --saveWorkspace --toysFrequentist --bypassFrequentistFit  --expectSignal=$Muhat -n combout_step1_$index 

ls higgsCombinecombout_step1_${1}*.root
mv higgsCombinecombout_step1_${1}*.root higgsCombinecombout_step1_done_$index.root

echo "---> combine higgsCombinecombout_step1_done_$index.root -m $MHhat --snapshotName MultiDimFit -M GenerateOnly --saveToys --toysFrequentist --bypassFrequentistFit -t -1 -n combout_step2_$index"
combine higgsCombinecombout_step1_done_$index.root -m $MHhat --snapshotName MultiDimFit -M GenerateOnly --saveToys --toysFrequentist --bypassFrequentistFit -t -1 -n combout_step2_$index

ls higgsCombinecombout_step2_${1}*.root
mv higgsCombinecombout_step2_${1}*.root higgsCombinecombout_step2_done_$index.root

(( index=$index+1))
done;

