#!/usr/bin/env bash

cd /home/hep/mdk16/PhD/ggtt/finalfits_try2/CMSSW_10_2_13/src/flashggFinalFit
#PROCID=$(expr ${SGE_TASK_ID} + 1)

#m=$(sed "${PROCID}q;d" mass.list)
m=$(sed "${SGE_TASK_ID}q;d" mass.list)

./get_limit.sh ${m}
