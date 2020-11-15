import os

# Paths and directory
cwd__ = os.environ['CMSSW_BASE']+"/src/flashggFinalFit/Datacard"
cmsswbase__ = os.environ['CMSSW_BASE']

# Centre of mass energy string
sqrts__ = "13TeV"

# Luminosity map in fb^-1
lumiMap = {'2016':35.92, '2017':41.53, '2018':59.74, 'combined':137.19}
lumiScaleFactor = 1000. # Converting from pb to fb

# Constants
BR_W_lnu = 3.*10.86*0.01
BR_Z_ll = 3*3.3658*0.01
BR_Z_nunu = 20.00*0.01
BR_Z_qq = 69.91*0.01
BR_W_qq = 67.41*0.01

# Production modes and decay channel
productionModes = ['ggH','qqH','ttH','tHq','tHW','ggZH','WH','ZH','bbH']
decayMode = 'hgg'

# flashgg input WS objects
inputWSName__ = "tagsDumper/cms_hgg_13TeV"
inputNuisanceExtMap = {'scales':'MCScale','scalesCorr':'','smears':'MCSmear'}
# output WS objects
outputWSName__ = "wsig"
outputWSObjectTitle__ = "hggpdfsmrel"
outputWSNuisanceTitle__ = "CMS_hgg_nuisance"
outputNuisanceExtMap = {'scales':'%sscale'%sqrts__,'scalesCorr':'%sscaleCorr'%sqrts__,'smears':'%ssmear'%sqrts__,'scalesGlobal':'%sscale'%sqrts__}

bkgWSName__ = "multipdf"
