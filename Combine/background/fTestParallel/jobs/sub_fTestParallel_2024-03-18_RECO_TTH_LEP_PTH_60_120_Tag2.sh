#!/bin/bash
ulimit -s unlimited
set -e
cd /mnt/cmsrm-home01.roma1.infn.it/cmshome/fderiggi/CMSSW_10_2_13/src
export SCRAM_ARCH=slc7_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval `scramv1 runtime -sh`
cd /mnt/cmsrm-home01.roma1.infn.it/cmshome/fderiggi/CMSSW_10_2_13/src/flashggFinalFit/Background
export PYTHONPATH=$PYTHONPATH:/mnt/cmsrm-home01.roma1.infn.it/cmshome/fderiggi/CMSSW_10_2_13/src/flashggFinalFit/tools:/mnt/cmsrm-home01.roma1.infn.it/cmshome/fderiggi/CMSSW_10_2_13/src/flashggFinalFit/Background/tools

/mnt/cmsrm-home01.roma1.infn.it/cmshome/fderiggi/CMSSW_10_2_13/src/flashggFinalFit/Background/runBackgroundScripts.sh -i data/data_all/ws//allData.root -p none -f RECO_TTH_LEP_PTH_60_120_Tag2 --ext 2024-03-18 --catOffset 54 --intLumi 138 --year all --batch Rome --queue cmsan --sigFile none --isData --fTest
