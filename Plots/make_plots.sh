#!/usr/bin/env bash

set -x

#source /cvmfs/cms.cern.ch/cmsset_default.sh
#source /vols/grid/cms/setup.sh

tag=XtoYH_mx360my90

#cmsenv
#source setup.sh

nToys=10
#nToys=500
#Need run toys after generating a Datacard.root file with only the signals used
make_toys(){
    pushd Plots 
        rm -rf SplusBModels_$tag
        python makeToysHH.py --inputWSFile ../Combine/Datacard_ggbbres_mx360my90_ggbbres.root --ext $tag --dryRun --nToys $nToys --dropResonantBkg
        iter=0
        while [ $iter -lt $nToys ]
        do                      
            ./SplusBModels_${tag}/toys/jobs/sub_toy_$(($iter+1)).sh &
            ./SplusBModels_${tag}/toys/jobs/sub_toy_$(($iter+2)).sh &
            ./SplusBModels_${tag}/toys/jobs/sub_toy_$(($iter+3)).sh &
            ./SplusBModels_${tag}/toys/jobs/sub_toy_$(($iter+4)).sh &
            ./SplusBModels_${tag}/toys/jobs/sub_toy_$(($iter+5)).sh &
            ./SplusBModels_${tag}/toys/jobs/sub_toy_$(($iter+6)).sh &
            ./SplusBModels_${tag}/toys/jobs/sub_toy_$(($iter+7)).sh &
            ./SplusBModels_${tag}/toys/jobs/sub_toy_$(($iter+8)).sh &
            ./SplusBModels_${tag}/toys/jobs/sub_toy_$(($iter+9)).sh &
            ./SplusBModels_${tag}/toys/jobs/sub_toy_$iter.sh                                     
            iter=$(($iter+10))
        done
    popd        
}

#Should be run with a Datacard.root file with everything
make_SpB(){
    pushd Plots 
        python makeSplusBModelPlot.py --inputWSFile ../Combine/Datacard_ggbbres_mx360my90_ggbbres.root  --cat "all" --doBands --ext 
    popd        
}

make_toys
#make_SpB
