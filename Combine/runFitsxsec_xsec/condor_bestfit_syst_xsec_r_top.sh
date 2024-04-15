#!/bin/sh
ulimit -s unlimited
set -e
cd /afs/cern.ch/user/f/fderiggi/AC/CMSSW_10_2_13/src
export SCRAM_ARCH=slc7_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval `scramv1 runtime -sh`
cd /afs/cern.ch/user/f/fderiggi/AC/CMSSW_10_2_13/src/flashggFinalFit/Combine/runFitsxsec_xsec

if [ $1 -eq 0 ]; then
  combine --floatOtherPOIs 1 -t -1 -P r_top --redefineSignalPOIs r_top,r_VBF,r_VH,r_ggH --setParameters r_ggH=1,r_top=1,r_VH=1,r_VBF=1 --robustFit=1 --setRobustFitAlgo=Minuit2,Migrad --X-rtd FITTER_NEW_CROSSING_ALGO --setRobustFitTolerance=0.1 --X-rtd FITTER_NEVER_GIVE_UP --X-rtd FITTER_BOUND --cminFallbackAlgo Minuit2,0:1. --saveInactivePOI 1 --saveWorkspace --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -M MultiDimFit -m 125.38 -d /afs/cern.ch/user/f/fderiggi/AC/CMSSW_10_2_13/src/flashggFinalFit/Combine/Datacard_xsec.root --setParameterRanges r_ggH=0.0,2.0:r_VBF=0.0,2.0:r_VH=0.0,3.0:r_top=0.0,4.0 -n _bestfit_syst_xsec_r_top
fi

