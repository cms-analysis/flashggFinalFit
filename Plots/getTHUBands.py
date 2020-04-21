import os, sys
import math
import re
from optparse import OptionParser
import ROOT
import pandas as pd
import glob
import pickle
import json

print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG THU BANDS RUN II ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
def leave():
  print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG THU BANDS RUN II (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
  sys.exit(1)

paramMergingSchemes = {
  "stage1p2_minimal":{
    "r_ggH_0J_low":['ggH_0J_PTH_0_10'],
    "r_ggH_0J_high":['ggH_0J_PTH_GT10','bbH'],
    "r_ggH_1J_low":['ggH_1J_PTH_0_60'],
    "r_ggH_1J_med":['ggH_1J_PTH_60_120'],
    "r_ggH_1J_high":['ggH_1J_PTH_120_200'],
    "r_ggH_2J_low":['ggH_GE2J_MJJ_0_350_PTH_0_60','ggZH_had_GE2J_MJJ_0_350_PTH_0_60'],
    "r_ggH_2J_med":['ggH_GE2J_MJJ_0_350_PTH_60_120','ggZH_had_GE2J_MJJ_0_350_PTH_60_120'],
    "r_ggH_2J_high":['ggH_GE2J_MJJ_0_350_PTH_120_200','ggZH_had_GE2J_MJJ_0_350_PTH_120_200'],
    "r_ggH_VBFlike":['ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'],
    "r_ggH_BSM_low":['ggH_PTH_200_300','ggZH_had_PTH_200_300'],
    "r_ggH_BSM_high":['ggH_PTH_300_450','ggH_PTH_450_650','ggH_PTH_GT650','ggZH_had_PTH_300_450','ggZH_had_PTH_450_650','ggZH_had_PTH_GT650'],
    "r_qqH_VHhad":['qqH_GE2J_MJJ_60_120','WH_had_GE2J_MJJ_60_120','ZH_had_GE2J_MJJ_60_120'],
    "r_qqH_low_mjj_2jlike":['qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'],
    "r_qqH_low_mjj_3jlike":['qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'],
    "r_qqH_high_mjj_2jlike":['qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'],
    "r_qqH_high_mjj_3jlike":['qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'],
    "r_qqH_BSM":['qqH_GE2J_MJJ_GT350_PTH_GT200','WH_had_GE2J_MJJ_GT350_PTH_GT200','ZH_had_GE2J_MJJ_GT350_PTH_GT200'],
    "r_WH_lep_low":['WH_lep_PTV_0_75'],
    "r_WH_lep_high":['WH_lep_PTV_75_150','WH_lep_PTV_150_250_0J','WH_lep_PTV_150_250_GE1J','WH_lep_PTV_GT250'],
    "r_ZH_lep":['ZH_lep_PTV_0_75','ZH_lep_PTV_75_150','ZH_lep_PTV_150_250_0J','ZH_lep_PTV_150_250_GE1J','ZH_lep_PTV_GT250','ggZH_ll_PTV_75_150','ggZH_ll_PTV_150_250_GE1J','ggZH_nunu_PTV_75_150','ggZH_nunu_PTV_150_250_0J','ggZH_nunu_PTV_150_250_GE1J','ggZH_nunu_PTV_GT250'],
    "r_ttH_low":['ttH_PTH_0_60'],
    "r_ttH_medlow":['ttH_PTH_60_120'],
    "r_ttH_medhigh":['ttH_PTH_120_200'],
    "r_ttH_high":['ttH_PTH_200_300','ttH_PTH_GT300'],
    "r_tHq":['tHq']
    # Missing procs: ggZH_ll_PTV_0_75,ggZH_ll_PTV_150_250_0J,ggZH_ll_PTV_GT250,ggZH_nunu_PTV_0_75,ggZH_had_1J_PTH_60_120,ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25,ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25,ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25,WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25,ggZH_had_0J_PTH_0_10,ggZH_had_0J_PTH_GT10,ggZH_had_1J_PTH_120_200,ggZH_had_1J_PTH_0_60
  },

  "stage1p2_intermediate":{
    "r_ggH_0J_low":['ggH_0J_PTH_0_10'],
    "r_ggH_0J_high":['ggH_0J_PTH_GT10','bbH'],
    "r_ggH_1J_low":['ggH_1J_PTH_0_60'],
    "r_ggH_1J_med":['ggH_1J_PTH_60_120'],
    "r_ggH_1J_high":['ggH_1J_PTH_120_200'],
    "r_ggH_2J_low":['ggH_GE2J_MJJ_0_350_PTH_0_60','ggZH_had_GE2J_MJJ_0_350_PTH_0_60'],
    "r_ggH_2J_med":['ggH_GE2J_MJJ_0_350_PTH_60_120','ggZH_had_GE2J_MJJ_0_350_PTH_60_120'],
    "r_ggH_2J_high":['ggH_GE2J_MJJ_0_350_PTH_120_200','ggZH_had_GE2J_MJJ_0_350_PTH_120_200'],
    "r_ggH_VBFlike":['ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'],
    "r_ggH_BSM_low":['ggH_PTH_200_300','ggZH_had_PTH_200_300'],
    "r_ggH_BSM_high":['ggH_PTH_300_450','ggH_PTH_450_650','ggH_PTH_GT650','ggZH_had_PTH_300_450','ggZH_had_PTH_450_650','ggZH_had_PTH_GT650'],
    "r_qqH_VHhad":['qqH_GE2J_MJJ_60_120','WH_had_GE2J_MJJ_60_120','ZH_had_GE2J_MJJ_60_120'],
    "r_qqH_low_mjj":['qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'],
    "r_qqH_high_mjj":['qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'],
    "r_qqH_BSM":['qqH_GE2J_MJJ_GT350_PTH_GT200','WH_had_GE2J_MJJ_GT350_PTH_GT200','ZH_had_GE2J_MJJ_GT350_PTH_GT200'],
    "r_WH_lep_low":['WH_lep_PTV_0_75'],
    "r_WH_lep_high":['WH_lep_PTV_75_150','WH_lep_PTV_150_250_0J','WH_lep_PTV_150_250_GE1J','WH_lep_PTV_GT250'],
    "r_ZH_lep":['ZH_lep_PTV_0_75','ZH_lep_PTV_75_150','ZH_lep_PTV_150_250_0J','ZH_lep_PTV_150_250_GE1J','ZH_lep_PTV_GT250','ggZH_ll_PTV_75_150','ggZH_ll_PTV_150_250_GE1J','ggZH_nunu_PTV_75_150','ggZH_nunu_PTV_150_250_0J','ggZH_nunu_PTV_150_250_GE1J','ggZH_nunu_PTV_GT250'],
    "r_ttH_low":['ttH_PTH_0_60','ttH_PTH_60_120'],
    "r_ttH_high":['ttH_PTH_120_200','ttH_PTH_200_300','ttH_PTH_GT300'],
    "r_tHq":['tHq']
    # Missing procs: ggZH_ll_PTV_0_75,ggZH_ll_PTV_150_250_0J,ggZH_ll_PTV_GT250,ggZH_nunu_PTV_0_75,ggZH_had_1J_PTH_60_120,ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25,ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25,ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25,WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25,ggZH_had_0J_PTH_0_10,ggZH_had_0J_PTH_GT10,ggZH_had_1J_PTH_120_200,ggZH_had_1J_PTH_0_60
  },

  "stage1p2_maximal":{
    "r_ggH_0J_low":['ggH_0J_PTH_0_10'],
    "r_ggH_0J_high":['ggH_0J_PTH_GT10','bbH'],
    "r_ggH_1J_low":['ggH_1J_PTH_0_60'],
    "r_ggH_1J_med":['ggH_1J_PTH_60_120'],
    "r_ggH_1J_high":['ggH_1J_PTH_120_200'],
    "r_ggH_2J_low":['ggH_GE2J_MJJ_0_350_PTH_0_60','ggZH_had_GE2J_MJJ_0_350_PTH_0_60'],
    "r_ggH_2J_med":['ggH_GE2J_MJJ_0_350_PTH_60_120','ggZH_had_GE2J_MJJ_0_350_PTH_60_120'],
    "r_ggH_2J_high":['ggH_GE2J_MJJ_0_350_PTH_120_200','ggZH_had_GE2J_MJJ_0_350_PTH_120_200'],
    "r_ggH_VBFlike":['ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'],
    "r_ggH_BSM":['ggH_PTH_200_300','ggZH_had_PTH_200_300','ggH_PTH_300_450','ggH_PTH_450_650','ggH_PTH_GT650','ggZH_had_PTH_300_450','ggZH_had_PTH_450_650','ggZH_had_PTH_GT650'],
    "r_qqH_VHhad":['qqH_GE2J_MJJ_60_120','WH_had_GE2J_MJJ_60_120','ZH_had_GE2J_MJJ_60_120'],
    "r_qqH_low_mjj":['qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'],
    "r_qqH_high_mjj":['qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'],
    "r_qqH_BSM":['qqH_GE2J_MJJ_GT350_PTH_GT200','WH_had_GE2J_MJJ_GT350_PTH_GT200','ZH_had_GE2J_MJJ_GT350_PTH_GT200'],
    "r_WH_lep":['WH_lep_PTV_0_75','WH_lep_PTV_75_150','WH_lep_PTV_150_250_0J','WH_lep_PTV_150_250_GE1J','WH_lep_PTV_GT250'],
    "r_ZH_lep":['ZH_lep_PTV_0_75','ZH_lep_PTV_75_150','ZH_lep_PTV_150_250_0J','ZH_lep_PTV_150_250_GE1J','ZH_lep_PTV_GT250','ggZH_ll_PTV_75_150','ggZH_ll_PTV_150_250_GE1J','ggZH_nunu_PTV_75_150','ggZH_nunu_PTV_150_250_0J','ggZH_nunu_PTV_150_250_GE1J','ggZH_nunu_PTV_GT250'],
    "r_ttH":['ttH_PTH_0_60','ttH_PTH_60_120','ttH_PTH_120_200','ttH_PTH_200_300','ttH_PTH_GT300'],
    "r_tHq":['tHq']
    # Missing procs: ggZH_ll_PTV_0_75,ggZH_ll_PTV_150_250_0J,ggZH_ll_PTV_GT250,ggZH_nunu_PTV_0_75,ggZH_had_1J_PTH_60_120,ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25,ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25,ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25,WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25,ggZH_had_0J_PTH_0_10,ggZH_had_0J_PTH_GT10,ggZH_had_1J_PTH_120_200,ggZH_had_1J_PTH_0_60
  }
}

theory_systematics = [
    'BR_hgg',
    'THU_ggH_Mu','THU_ggH_Res','THU_ggH_Mig01','THU_ggH_Mig12','THU_ggH_VBF2j','THU_ggH_VBF3j','THU_ggH_PT60','THU_ggH_PT120','THU_ggH_qmtop','pdf_Higgs_ggH','alphaS_ggH',
    'THU_qqH_Yield','THU_qqH_PTH200','THU_qqH_MJJ60','THU_qqH_MJJ120','THU_qqH_MJJ350','THU_qqH_MJJ700','THU_qqH_MJJ1000','THU_qqH_MJJ1500','THU_qqH_PTHJJ25','THU_qqH_JET01','pdf_Higgs_qqH','alphaS_qqH',
    'QCDscale_VH','pdf_Higgs_VH','alphaS_VH',
    'QCDscale_ttH','pdf_Higgs_ttH','alphaS_ttH',
    'QCDscale_tHq','pdf_Higgs_tHq','alphaS_tHq'
]

proc_map = {"GG2H":"ggH","VBF":"qqH","WH2HQQ":"WH_had","ZH2HQQ":"ZH_had","GG2HQQ":"ggZH_had","QQ2HLNU":"WH_lep","QQ2HLL":"ZH_lep","GG2HLL":"ggZH_ll","GG2HNUNU":"ggZH_nunu","TTH":"ttH","BBH":"bbH","THQ":"tHq","THW":"tHW","TH":"tHq"}

def get_options():
  parser = OptionParser()
  parser.add_option('--paramMergingScheme', dest='paramMergingScheme', default='none', help="Parameter merging scenario e.g. maximal_mjj")
  parser.add_option('--POI', dest='POI', default='', help="Parameter of interest")
  parser.add_option("--inputWS", dest="inputWS", default='', help="Input workspace")
  parser.add_option("--year", dest="year", default='2016', help="Year to extract THU from")
  return parser.parse_args()
(opt,args) = get_options()

def rooiter(x):
  iter = x.iterator()
  ret = iter.Next()
  while ret:
    yield ret
    ret = iter.Next()

if opt.POI == 'all': pois = paramMergingSchemes[opt.paramMergingScheme].keys()
else:
  if opt.POI not in paramMergingSchemes[opt.paramMergingScheme]: 
    print " --> [ERROR] POI %s not defined in parameter merging scenario"%opt.POI
    leave()
  pois = [opt.POI]

# Open ROOT file and extract workspace
f = ROOT.TFile(opt.inputWS)
w = f.Get("w")
# Extract all XS x BR
br_hgg = w.function("fbr_13TeV").getVal()
xsbr = {}
print " --> Extracting XS from input workspace"
for fxs in rooiter(w.allFunctions().selectByName("fxs_*")):
  # Extract process
  fname = fxs.GetName()
  proc = fname.split("fxs_")[-1].split("_13TeV")[0]
  pm = proc.split("_")[0]
  proc = re.sub(pm,proc_map[pm],proc)
  xsbr[proc] = fxs.getVal()*br_hgg*1000

# Loop over params in merging scheme
poi_xsbr = {}
poi_xsbr_var = {}
for poi, procs in paramMergingSchemes[opt.paramMergingScheme].iteritems():
  if poi not in pois: continue
  poi_xsbr[poi] = 0
  poi_xsbr_var[poi] = {}
  for ts in theory_systematics: 
    if not w.var(ts): continue #If var not in workspace
    poi_xsbr_var[poi]['%s_Up01Sigma'%ts], poi_xsbr_var[poi]['%s_Down01Sigma'%ts] = 0, 0
  # Loop over STXS bins in poi: calculate variations in XS due to syst
  for proc in procs:
    # Add nominal cross section
    poi_xsbr[poi] += xsbr[proc]
    print " --> Extracting vars: %s (POI:%s)"%(proc,poi)
    syst_var = {}
    nominal_yield = 0
    # Extract relevant normalisation for proc
    allNorms = w.allFunctions().selectByName("n_exp_final*%s_%s_hgg"%(proc,opt.year))
    for norm in rooiter(allNorms): nominal_yield += norm.getVal()
    for ts in theory_systematics:
      if not w.var(ts): continue #If var not in workspace
      syst_var['%s_Up01Sigma'%ts] = 0
      w.var(ts).setVal(1.)
      if nominal_yield == 0.: syst_var['%s_Up01Sigma'%ts] = 1.
      else: 
        for norm in rooiter(allNorms): syst_var['%s_Up01Sigma'%ts] += (norm.getVal()/nominal_yield)
      w.var(ts).setVal(0)
      syst_var['%s_Down01Sigma'%ts] = 0
      w.var(ts).setVal(-1.)
      if nominal_yield == 0.: syst_var['%s_Up01Sigma'%ts] = 1.
      else:
        for norm in rooiter(allNorms): syst_var['%s_Down01Sigma'%ts] += (norm.getVal()/nominal_yield)
      w.var(ts).setVal(0)
      # Changes to cross section
      poi_xsbr_var[poi]['%s_Up01Sigma'%ts] += xsbr[proc]*syst_var['%s_Up01Sigma'%ts]
      poi_xsbr_var[poi]['%s_Down01Sigma'%ts] += xsbr[proc]*syst_var['%s_Down01Sigma'%ts]

# Loop over pois and save xsbr with uncertainties
xsbr_theory = {}
for poi in paramMergingSchemes[opt.paramMergingScheme]:
  if poi not in pois: continue
  xsbr_theory[poi] = {}
  print " --> Calculating theory uncertainty: %s"%poi
  FracHigh01Sigma2, FracLow01Sigma2 = 0,0
  # Loop over systematics:
  for ts in theory_systematics:
    if not w.var(ts): continue #If var not in workspace
    up_fracvar, down_fracvar = (poi_xsbr_var[poi]['%s_Up01Sigma'%ts]/poi_xsbr[poi]-1), (poi_xsbr_var[poi]['%s_Down01Sigma'%ts]/poi_xsbr[poi]-1)
    print "    * %s: (upfracvar,downfracvar) = (%.3f,%.3f)"%(ts,up_fracvar,down_fracvar)
    if up_fracvar >= 0: 
      FracHigh01Sigma2 += up_fracvar*up_fracvar
      FracLow01Sigma2 += down_fracvar*down_fracvar
    else: 
      FracHigh01Sigma2 += down_fracvar*down_fracvar
      FracLow01Sigma2 += up_fracvar*up_fracvar
  FracHigh01Sigma = math.sqrt(FracHigh01Sigma2)
  FracLow01Sigma = math.sqrt(FracLow01Sigma2)
  xsbr_theory[poi]['nominal'] = poi_xsbr[poi]
  xsbr_theory[poi]['High01Sigma'] = poi_xsbr[poi]*FracHigh01Sigma
  xsbr_theory[poi]['Low01Sigma'] = poi_xsbr[poi]*FracLow01Sigma
  xsbr_theory[poi]['FracHigh01Sigma'] = FracHigh01Sigma
  xsbr_theory[poi]['FracLow01Sigma'] = FracLow01Sigma

# Write to json file
print " --> Writing to json file: xsbr_theory_%s.json"%opt.POI
if not os.path.isdir("./jsons"): os.system("mkdir ./jsons")
with open("./jsons/xsbr_theory_%s_%s.json"%(opt.POI,opt.paramMergingScheme),'w') as jsonfile: json.dump(xsbr_theory,jsonfile)
