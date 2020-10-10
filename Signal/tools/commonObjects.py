import os

# Constants
sqrts__ = "13TeV"
BR_W_lnu = 3.*10.86*0.01
BR_Z_ll = 3*3.3658*0.01
BR_Z_nunu = 20.00*0.01
BR_Z_qq = 69.91*0.01
BR_W_qq = 67.41*0.01
lumiScaleFactor = 1000.

# Production modes and decay channel
productionModes = ['ggH','qqH','ttH','tHq','tHW','ggZH','WH','ZH','bbH']
decayMode = 'hgg'

# flashgg 
inputWSName__ = "tagsDumper/cms_hgg_13TeV"

# Paths and directory
cwd__ = os.environ['CMSSW_BASE']+"/src/flashggFinalFit/Signal"
cmsswbase__ = os.environ['CMSSW_BASE']
