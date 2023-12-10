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
  python RunText2Workspace.py --mode ${procTemplate} --dryRun --ext _${procTemplate}_${m} --common_opts "-m ${mh} higgsMassRange=${mggl},${mggh} --channel-masks" --batch local
  ./t2w_jobs/t2w_${procTemplate}_${procTemplate}_${m}.sh
popd
