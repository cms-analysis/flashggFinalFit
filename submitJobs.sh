#!/usr/bin/env bash

set -e

n_masses=$(cat mass.list | wc -w)

for m in $(cat mass.list); do
 if [[ -z $(grep "ggtt_resonant_${m}" Signal/tools/replacementMap.py) ]]; then
  sed "s;<m>;${m};g" Signal/tools/replacementTemplate.py >> Signal/tools/replacementMap.py
 fi
 if [[ -z $(grep "ggtt_resonant_${m}" Signal/tools/XSBRMap.py) ]]; then
  sed "s;<m>;${m};g" Signal/tools/XSBRTemplate.py >> Signal/tools/XSBRMap.py
 fi
done

qsub -q hep.q -l h_rt=600 -t 1-${n_masses}:1 get_limit_batch.sh
