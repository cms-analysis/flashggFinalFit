#!/bin/bash
ulimit -s unlimited
set -e
cd /eos/user/p/pkrueper/HiggsDNA_and_FinalFits_tutorial24/FF_standalone/src
export SCRAM_ARCH=None
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval `scramv1 runtime -sh`
cd /eos/user/p/pkrueper/HiggsDNA_and_FinalFits_tutorial24/FF_standalone/src/flashggFinalFit/Signal
cd ..
source /eos/user/p/pkrueper/HiggsDNA_and_FinalFits_tutorial24/FF_standalone/src/flashggFinalFit/setup_standalone.sh
cd Trees2WS
export MAMBA_EXE='/eos/home-p/pkrueper/HiggsDNA_and_FinalFits_tutorial24/higgsdna_finalfits_tutorial_24/y/micromamba';
export MAMBA_ROOT_PREFIX='/eos/home-p/pkrueper/HiggsDNA_and_FinalFits_tutorial24/higgsdna_finalfits_tutorial_24/micromamba';
__mamba_setup="$("$MAMBA_EXE" shell hook --shell bash --root-prefix "$MAMBA_ROOT_PREFIX" 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__mamba_setup"
else
    alias micromamba="$MAMBA_EXE"  # Fallback on help from micromamba activate
fi
unset __mamba_setup
micromamba activate flashggFinalFit
export PYTHONPATH=$PYTHONPATH:/eos/user/p/pkrueper/HiggsDNA_and_FinalFits_tutorial24/FF_standalone/src/flashggFinalFit/tools:/eos/user/p/pkrueper/HiggsDNA_and_FinalFits_tutorial24/FF_standalone/src/flashggFinalFit/Trees2WS/tools

proc_x_stxs_x_era=('THW_FID' 'THQ_FID')
length=${#proc_x_stxs_x_era[@]}

for ((i=0;i<length;i++)); do python3 trees2ws.py --inputConfig config_tutorial.py --inputTreeFile /eos/user/p/pkrueper/STXS_test/run3hggstxs_1p2/src/run3hggstxs/postprocessing/18sep_signalTESTT/preEE/${proc_x_stxs_x_era[i]}/nominal  --inputMass 125 --productionMode ${proc_x_stxs_x_era[i]}  --year preEE --doSystematics;done
