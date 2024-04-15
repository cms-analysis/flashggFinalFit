#!/bin/bash
ulimit -s unlimited
set -e
cd /mnt/cmsrm-home01.roma1.infn.it/cmshome/fderiggi/CMSSW_10_2_13/src
export SCRAM_ARCH=slc7_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval `scramv1 runtime -sh`
cd /mnt/cmsrm-home01.roma1.infn.it/cmshome/fderiggi/CMSSW_10_2_13/src/flashggFinalFit/Signal
export PYTHONPATH=$PYTHONPATH:/mnt/cmsrm-home01.roma1.infn.it/cmshome/fderiggi/CMSSW_10_2_13/src/flashggFinalFit/tools:/mnt/cmsrm-home01.roma1.infn.it/cmshome/fderiggi/CMSSW_10_2_13/src/flashggFinalFit/Signal/tools

python /mnt/cmsrm-home01.roma1.infn.it/cmshome/fderiggi/CMSSW_10_2_13/src/flashggFinalFit/Signal/scripts/packageSignal.py --cat RECO_PTH_GT650_Tag0 --outputExt packaged --massPoints 120,125,130 --exts 2023-02-13_year2016preVFP,2023-02-13_year2016postVFP,2023-02-13_year2017,2023-02-13_year2018 --mergeYears
