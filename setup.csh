# Add tools dir to PYTHONPATH
eval `scramv1 runtime -csh`

setenv PYTHONPATH "${PYTHON27PATH}"
setenv PYTHONPATH "${PYTHONPATH}:${CMSSW_BASE}/src/flashggFinalFit/tools"
