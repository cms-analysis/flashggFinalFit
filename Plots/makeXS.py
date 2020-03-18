# Script to make results plot

import os, sys
import re
from optparse import OptionParser
import ROOT
import pandas as pd
import glob
import pickle
# Scripts for plotting
from usefulStyle import setCanvas, drawCMS, drawEnPu, drawEnYear, formatHisto
from shanePalette import set_color_palette

print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG RESULTS PLOT RUN II ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
def leave():
  print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG RESULTS PLOT RUN II (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
  sys.exit(1)

def rooiter(x):
  iter = x.iterator()
  ret = iter.Next()
  while ret:
    yield ret
    ret = iter.Next()

productionModes = ['ggH','qqH','WH_had','ZH_had','WH_lep','ZH_lep','ttH','tHq']

stxsBins = {
  "ggH":['ggH_0J_PTH_0_10','ggH_0J_PTH_GT10','ggH_1J_PTH_0_60','ggH_1J_PTH_60_120','ggH_1J_PTH_120_200','ggH_GE2J_MJJ_0_350_PTH_0_60','ggH_GE2J_MJJ_0_350_PTH_60_120','ggH_GE2J_MJJ_0_350_PTH_120_200','ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ggH_PTH_200_300','ggH_PTH_300_450','ggH_PTH_450_650','ggH_PTH_GT650'],
  "qqH":['qqH_0J','qqH_1J','qqH_GE2J_MJJ_0_60','qqH_GE2J_MJJ_60_120','qqH_GE2J_MJJ_120_350','qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','qqH_GE2J_MJJ_GT350_PTH_GT200'],
  "WH_had":['WH_had_0J','WH_had_1J','WH_had_GE2J_MJJ_0_60','WH_had_GE2J_MJJ_60_120','WH_had_GE2J_MJJ_120_350','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_GT350_PTH_GT200'],
  "ZH_had":['ZH_had_0J','ZH_had_1J','ZH_had_GE2J_MJJ_0_60','ZH_had_GE2J_MJJ_60_120','ZH_had_GE2J_MJJ_120_350','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_GT350_PTH_GT200'],
  "WH_lep":['WH_lep_PTV_0_75','WH_lep_PTV_75_150','WH_lep_PTV_150_250_0J','WH_lep_PTV_150_250_GE1J','WH_lep_PTV_GT250'],
  "ZH_lep":['ZH_lep_PTV_0_75','ZH_lep_PTV_75_150','ZH_lep_PTV_150_250_0J','ZH_lep_PTV_150_250_GE1J','ZH_lep_PTV_GT250'],
  "ttH":['ttH_PTH_0_60','ttH_PTH_60_120','ttH_PTH_120_200','ttH_PTH_200_300','ttH_PTH_GT300'],
  "tHq":['tHq']
}

paramMergingSchemes = {
  "stage0":{
    "ggH":['ggH_0J_PTH_0_10','ggH_0J_PTH_GT10','ggH_1J_PTH_0_60','ggH_1J_PTH_60_120','ggH_1J_PTH_120_200','ggH_GE2J_MJJ_0_350_PTH_0_60','ggH_GE2J_MJJ_0_350_PTH_60_120','ggH_GE2J_MJJ_0_350_PTH_120_200','ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ggH_PTH_200_300','ggH_PTH_300_450','ggH_PTH_450_650','ggH_PTH_GT650'],
    "VBF":['qqH_0J','qqH_1J','qqH_GE2J_MJJ_0_60','qqH_GE2J_MJJ_60_120','qqH_GE2J_MJJ_120_350','qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','qqH_GE2J_MJJ_GT350_PTH_GT200'],
    "VH_had":['WH_had_0J','WH_had_1J','WH_had_GE2J_MJJ_0_60','WH_had_GE2J_MJJ_60_120','WH_had_GE2J_MJJ_120_350','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_GT350_PTH_GT200','ZH_had_0J','ZH_had_1J','ZH_had_GE2J_MJJ_0_60','ZH_had_GE2J_MJJ_60_120','ZH_had_GE2J_MJJ_120_350','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_GT350_PTH_GT200'],
    "WH_lep":['WH_lep_PTV_0_75','WH_lep_PTV_75_150','WH_lep_PTV_150_250_0J','WH_lep_PTV_150_250_GE1J','WH_lep_PTV_GT250'],
    "ZH_lep":['ZH_lep_PTV_0_75','ZH_lep_PTV_75_150','ZH_lep_PTV_150_250_0J','ZH_lep_PTV_150_250_GE1J','ZH_lep_PTV_GT250'],
    "ttH":['ttH_PTH_0_60','ttH_PTH_60_120','ttH_PTH_120_200','ttH_PTH_200_300','ttH_PTH_GT300'],
    "tHq":['tHq']
  },
  "maximal_mjj":{
    "ggH_BSM":['ggH_PTH_200_300','ggH_PTH_300_450','ggH_PTH_450_650','ggH_PTH_GT650'],
    "ggH_VBF_like":['ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'],
    "qqH_VH_like":['qqH_GE2J_MJJ_60_120','WH_had_GE2J_MJJ_60_120','ZH_had_GE2J_MJJ_60_120'],
    "qqH_MJJ_350_700":['qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'],
    "qqH_MJJ_GT700":['qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'],
    "qqH_BSM":['qqH_GE2J_MJJ_GT350_PTH_GT200','WH_had_GE2J_MJJ_GT350_PTH_GT200','ZH_had_GE2J_MJJ_GT350_PTH_GT200'],
    "qqH_other":['qqH_0J','qqH_1J','qqH_GE2J_MJJ_0_60','qqH_GE2J_MJJ_120_350','WH_had_0J','WH_had_1J','WH_had_GE2J_MJJ_0_60','WH_had_GE2J_MJJ_120_350','ZH_had_0J','ZH_had_1J','ZH_had_GE2J_MJJ_0_60','ZH_had_GE2J_MJJ_120_350'],
    "WH_lep":['WH_lep_PTV_0_75','WH_lep_PTV_75_150','WH_lep_PTV_150_250_0J','WH_lep_PTV_150_250_GE1J','WH_lep_PTV_GT250'],
    "ZH_lep":['ZH_lep_PTV_0_75','ZH_lep_PTV_75_150','ZH_lep_PTV_150_250_0J','ZH_lep_PTV_150_250_GE1J','ZH_lep_PTV_GT250'],
    "ttH":['ttH_PTH_0_60','ttH_PTH_60_120','ttH_PTH_120_200','ttH_PTH_200_300','ttH_PTH_GT300']
  },
  "intermediate_mjj":{
    "ggH_BSM_low":['ggH_PTH_200_300'],
    "ggH_BSM_high":['ggH_PTH_300_450','ggH_PTH_450_650','ggH_PTH_GT650'],
    "ggH_VBF_like":['ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'],
    "qqH_VH_like":['qqH_GE2J_MJJ_60_120','WH_had_GE2J_MJJ_60_120','ZH_had_GE2J_MJJ_60_120'],
    "qqH_MJJ_350_700":['qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'],
    "qqH_MJJ_GT700":['qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'],
    "qqH_BSM":['qqH_GE2J_MJJ_GT350_PTH_GT200','WH_had_GE2J_MJJ_GT350_PTH_GT200','ZH_had_GE2J_MJJ_GT350_PTH_GT200'],
    "qqH_other":['qqH_0J','qqH_1J','qqH_GE2J_MJJ_0_60','qqH_GE2J_MJJ_120_350','WH_had_0J','WH_had_1J','WH_had_GE2J_MJJ_0_60','WH_had_GE2J_MJJ_120_350','ZH_had_0J','ZH_had_1J','ZH_had_GE2J_MJJ_0_60','ZH_had_GE2J_MJJ_120_350'],
    "WH_lep_low":['WH_lep_PTV_0_75'],
    "WH_lep_high":['WH_lep_PTV_75_150','WH_lep_PTV_150_250_0J','WH_lep_PTV_150_250_GE1J','WH_lep_PTV_GT250'],
    "ZH_lep":['ZH_lep_PTV_0_75','ZH_lep_PTV_75_150','ZH_lep_PTV_150_250_0J','ZH_lep_PTV_150_250_GE1J','ZH_lep_PTV_GT250'],
    "ttH_low":['ttH_PTH_0_60','ttH_PTH_60_120'],
    "ttH_high":['ttH_PTH_120_200','ttH_PTH_200_300','ttH_PTH_GT300']
  }
}

proc_map = {"GG2H":"ggH","VBF":"qqH","WH2HQQ":"WH_had","ZH2HQQ":"ZH_had","QQ2HLNU":"WH_lep","QQ2HLL":"ZH_lep","TTH":"ttH","BBH":"bbH","THQ":"tHq","THW":"tHW","TH":"tHq"}
inv_proc_map = {v: k for k, v in proc_map.iteritems()}

def get_options():
  parser = OptionParser()
  parser.add_option('--paramMergingScheme', dest='paramMergingScheme', default='none', help="Parameter merging scenario e.g. maximal_mjj")
  parser.add_option('--inputWS', dest='inputWS', default='none', help="Input workspace to determineParameter merging scenario e.g. maximal_mjj")
  return parser.parse_args()
(opt,args) = get_options()

# Add counter for each POI
xs = {}
for pm in productionModes:
  for stxsBin in stxsBins[pm]:
    paramFound = False
    if opt.paramMergingScheme in paramMergingSchemes:
      for p, mergeBins in paramMergingSchemes[opt.paramMergingScheme].iteritems():
        if paramFound: continue
        if stxsBin in mergeBins:
          param = p
          paramFound = True
    if not paramFound: param = stxsBin
    # Add counter to dict
    xs[param] = 0

# Open ROOT file and loop over XS
if not os.path.exists( opt.inputWS ): 
  print " --> [ERROR] Input worksapce file does not exist. Leaving"
  leave()
fin = ROOT.TFile( opt.inputWS )
ws = fin.Get("w")
br_hgg = ws.function("fbr_13TeV").getVal()
allXS = ws.allFunctions().selectByName("fxs_*")
for _XS in rooiter(allXS):
  _stxsBin = "_".join(_XS.GetName().split("_")[1:-1])
  _pm = _stxsBin.split("_")[0]
  if _pm not in proc_map:
    print " --> [ERROR] Process not recognised: %s"%_stxsBin
    leave()
  else:
    stxsBin = re.sub( _pm, proc_map[_pm], _stxsBin )
 
    paramFound = False
    if opt.paramMergingScheme in paramMergingSchemes:
      for p, mergeBins in paramMergingSchemes[opt.paramMergingScheme].iteritems():
        if paramFound: continue
        if stxsBin in mergeBins: 
          xs[p] += _XS.getVal()*br_hgg*1000
          paramFound = True
    if not paramFound: xs[stxsBin] += _XS.getVal()*br_hgg*1000
     
      
    
   


