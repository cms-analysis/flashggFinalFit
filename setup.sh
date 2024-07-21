# Add tools dir to PYTHONPATH
eval `scramv1 runtime -sh`

export PYTHONPATH=${PYTHON27PATH}
export PYTHONPATH=$PYTHONPATH:${CMSSW_BASE}/src/flashggFinalFit/tools
export PYTHONPATH=$PYTHONPATH:${CMSSW_BASE}/src/flashggFinalFit/Signal/tools
