# Setup script for standalone usage of flashggFinalFit
export CMSSW_BASE=$(dirname $(dirname $(pwd)))
export PYTHONPATH=$PYTHONPATH:${CMSSW_BASE}/src/flashggFinalFit/tools
export SCRAM_ARCH=None
