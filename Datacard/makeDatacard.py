# NEW datacard making scrit
#  * Uses Pandas dataframe to store all info about processes
#  * Option for merging across years

print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG DATACARD MAKER RUN II ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
import os, sys
import re
from optparse import OptionParser
import ROOT
import pandas as pd
import glob
import pickle
from collections import OrderedDict
from systematics import theory_systematics, experimental_systematics, signal_shape_systematics
#from systematics_scaleWeights import theory_systematics, experimental_systematics, signal_shape_systematics
from cross_sections import stxs_xs

def leave():
  print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG DATACARD MAKER RUN II (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
  sys.exit(1)

stxsBinMergingScheme = OrderedDict()
# Maximal merging scheme
stxsBinMergingScheme['max_ggH_BSM'] = ['ggH_PTH_200_300', 'ggH_PTH_300_450','ggH_PTH_GT650', 'ggH_PTH_450_650']
stxsBinMergingScheme['max_ggH_VBFlike'] = ['ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25']
stxsBinMergingScheme['max_qqH_VBFlike'] = ['qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25', 'qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25', 'ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25', 'ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25', 'WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25', 'ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25', 'ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25']
stxsBinMergingScheme['max_WH_lep'] = ['WH_lep_PTV_150_250_GE1J', 'WH_lep_PTV_75_150', 'WH_lep_PTV_0_75', 'WH_lep_PTV_150_250_0J','WH_lep_PTV_GT250']
stxsBinMergingScheme['max_ZH_lep'] = ['ZH_lep_PTV_150_250_0J', 'ZH_lep_PTV_150_250_GE1J', 'ZH_lep_PTV_0_75', 'ZH_lep_PTV_75_150', 'ggZH_ll_PTV_150_250_0J', 'ggZH_ll_PTV_150_250_GE1J', 'ggZH_ll_PTV_0_75', 'ggZH_ll_PTV_75_150', 'ggZH_nunu_PTV_150_250_0J', 'ggZH_nunu_PTV_150_250_GE1J', 'ggZH_nunu_PTV_0_75', 'ggZH_nunu_PTV_75_150','ZH_lep_PTV_GT250','ggZH_ll_PTV_GT250','ggZH_nunu_PTV_GT250']
stxsBinMergingScheme['max_ttH'] = ['ttH_PTH_200_300', 'ttH_PTH_60_120', 'ttH_PTH_120_200', 'ttH_PTH_0_60','ttH_PTH_GT300']
# Minimal merging scheme
stxsBinMergingScheme['min_ggH_BSM_high'] = ['ggH_PTH_300_450','ggH_PTH_GT650', 'ggH_PTH_450_650']
stxsBinMergingScheme['min_VBFlike_low_mjj_low_pthjj'] = ['ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25']
stxsBinMergingScheme['min_VBFlike_low_mjj_high_pthjj'] = ['ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25']
stxsBinMergingScheme['min_VBFlike_high_mjj_low_pthjj'] = ['ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25']
stxsBinMergingScheme['min_VBFlike_high_mjj_high_pthjj'] = ['ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25']
stxsBinMergingScheme['min_WH_lep_high'] = ['WH_lep_PTV_150_250_GE1J', 'WH_lep_PTV_75_150', 'WH_lep_PTV_150_250_0J','WH_lep_PTV_GT250']
stxsBinMergingScheme['min_ZH_lep'] = ['ZH_lep_PTV_150_250_0J', 'ZH_lep_PTV_150_250_GE1J', 'ZH_lep_PTV_0_75', 'ZH_lep_PTV_75_150', 'ggZH_ll_PTV_150_250_0J', 'ggZH_ll_PTV_150_250_GE1J', 'ggZH_ll_PTV_0_75', 'ggZH_ll_PTV_75_150', 'ggZH_nunu_PTV_150_250_0J', 'ggZH_nunu_PTV_150_250_GE1J', 'ggZH_nunu_PTV_0_75', 'ggZH_nunu_PTV_75_150','ZH_lep_PTV_GT250','ggZH_ll_PTV_GT250','ggZH_nunu_PTV_GT250']
stxsBinMergingScheme['min_ttH_high'] = ['ttH_PTH_200_300', 'ttH_PTH_GT300']

# Scale correlation scheme
scaleCorrelationScheme = OrderedDict()
scaleCorrelationScheme['ggH_scale_0jet'] = ['ggH_0J_PTH_0_10','ggH_0J_PTH_GT10','ggZH_had_0J_PTH_0_10','ggZH_had_0J_PTH_GT10']
scaleCorrelationScheme['ggH_scale_1jet_lowpt'] = ['ggH_1J_PTH_60_120', 'ggH_1J_PTH_120_200', 'ggH_1J_PTH_0_60','ggZH_had_1J_PTH_60_120', 'ggZH_had_1J_PTH_120_200', 'ggZH_had_1J_PTH_0_60']
scaleCorrelationScheme['ggH_scale_2jet_lowpt'] = ['ggH_GE2J_MJJ_0_350_PTH_120_200', 'ggH_GE2J_MJJ_0_350_PTH_60_120', 'ggH_GE2J_MJJ_0_350_PTH_0_60','ggZH_had_GE2J_MJJ_0_350_PTH_120_200', 'ggZH_had_GE2J_MJJ_0_350_PTH_60_120', 'ggZH_had_GE2J_MJJ_0_350_PTH_0_60'] 
scaleCorrelationScheme['ggH_scale_highpt'] = ['ggH_PTH_200_300', 'ggH_PTH_300_450','ggZH_had_PTH_200_300', 'ggZH_had_PTH_300_450']
scaleCorrelationScheme['ggH_scale_veryhighpt'] = ['ggH_PTH_GT650', 'ggH_PTH_450_650','ggZH_had_PTH_GT650', 'ggZH_had_PTH_450_650']
scaleCorrelationScheme['ggH_scale_vbf'] = ['ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25', 'ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25', 'ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25', 'ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25', 'ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25', 'ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25', 'ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25']
scaleCorrelationScheme['vbf_scale_0jet'] = ['qqH_0J']
scaleCorrelationScheme['vbf_scale_1jet'] = ['qqH_1J']
scaleCorrelationScheme['vbf_scale_lowmjj'] = ['qqH_GE2J_MJJ_0_60','qqH_GE2J_MJJ_60_120','qqH_GE2J_MJJ_120_350']
scaleCorrelationScheme['vbf_scale_highmjj_lowpt'] = ['qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25', 'qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25']
scaleCorrelationScheme['vbf_scale_highmjj_highpt'] = ['qqH_GE2J_MJJ_GT350_PTH_GT200']
scaleCorrelationScheme['VH_scale_0jet'] = ['WH_had_0J','ZH_had_0J']
scaleCorrelationScheme['VH_scale_1jet'] = ['WH_had_1J','ZH_had_1J']
scaleCorrelationScheme['VH_scale_lowmjj'] = ['WH_had_GE2J_MJJ_0_60','ZH_had_GE2J_MJJ_0_60','WH_had_GE2J_MJJ_60_120', 'ZH_had_GE2J_MJJ_60_120','ZH_had_GE2J_MJJ_120_350', 'WH_had_GE2J_MJJ_120_350']
scaleCorrelationScheme['VH_scale_highmjj_lowpt'] = ['WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25', 'ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25', 'ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25', 'WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25', 'ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25', 'ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25']
scaleCorrelationScheme['VH_scale_highmjj_highpt'] = ['WH_had_GE2J_MJJ_GT350_PTH_GT200', 'ZH_had_GE2J_MJJ_GT350_PTH_GT200']
scaleCorrelationScheme['WH_scale_lowpt'] = ['WH_lep_PTV_150_250_GE1J', 'WH_lep_PTV_75_150', 'WH_lep_PTV_0_75', 'WH_lep_PTV_150_250_0J']
scaleCorrelationScheme['WH_scale_highpt'] = ['WH_lep_PTV_GT250']
scaleCorrelationScheme['ZH_scale_lowpt'] = ['ZH_lep_PTV_150_250_0J', 'ZH_lep_PTV_150_250_GE1J', 'ZH_lep_PTV_0_75', 'ZH_lep_PTV_75_150', 'ggZH_ll_PTV_150_250_0J', 'ggZH_ll_PTV_150_250_GE1J', 'ggZH_ll_PTV_0_75', 'ggZH_ll_PTV_75_150', 'ggZH_nunu_PTV_150_250_0J', 'ggZH_nunu_PTV_150_250_GE1J', 'ggZH_nunu_PTV_0_75', 'ggZH_nunu_PTV_75_150']
scaleCorrelationScheme['ZH_scale_highpt'] = ['ZH_lep_PTV_GT250','ggZH_ll_PTV_GT250','ggZH_nunu_PTV_GT250']
scaleCorrelationScheme['ttH_scale_lowpt'] = ['ttH_PTH_200_300', 'ttH_PTH_60_120', 'ttH_PTH_120_200', 'ttH_PTH_0_60']
scaleCorrelationScheme['ttH_scale_highpt'] = ['ttH_PTH_GT300']
#scaleCorrelationScheme['tH_scale'] = ['tHq','tHW']
#scaleCorrelationScheme['bbH_scale'] = ['bbH']

lumi = {'2016':'35.92', '2017':'41.53', '2018':'59.74'}
decay = "hgg"

def get_options():
  parser = OptionParser()
  parser.add_option('--years', dest='years', default='2016', help="Comma separated list of years")
  parser.add_option('--ext', dest='ext', default='', help="Extension (used when running makeYields.py)")
  parser.add_option('--skipCOWCorr', dest='skipCOWCorr', default=False, action="store_true", help="Skip centralObjectWeight correction for events in acceptance")
  parser.add_option('--prune', dest='prune', default=False, action="store_true", help="Prune proc x cat which make up less than pruneThreshold (default 0.1%) of given total category")
  parser.add_option('--pruneThreshold', dest='pruneThreshold', default=0.001, type='float', help="Threshold with which to prune proc x cat (yield/cat yield)")
  parser.add_option('--doSystematics', dest='doSystematics', default=False, action="store_true", help="Include systematics calculations and add to datacard")
  parser.add_option('--doSTXSBinMerging', dest='doSTXSBinMerging', default=False, action="store_true", help="Calculate additional normalisation systematics for merged STXS bins (specified in stxsBinMergingScheme)")
  parser.add_option('--doScaleCorrelationScheme', dest='doScaleCorrelationScheme', default=False, action="store_true", help="Partially uncorrelate scale uncertainties for different phase space regions")
  parser.add_option('--saveDataFrame', dest='saveDataFrame', default='', help='Specify name of dataFrame if want to be saved') 
  parser.add_option('--output', dest='output', default='Datacard.txt', help='Datacard name') 
  return parser.parse_args()
(opt,args) = get_options()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Concatenate dataframes
print " --> [VERBOSE] Loading per category dataframes into single dataframe"
pkl_files = glob.glob("./yields%s/*.pkl"%opt.ext)
data = pd.DataFrame()
for f_pkl_name in pkl_files:
  with open(f_pkl_name,"rb") as f_pkl: 
    df = pickle.load(f_pkl)
    data = pd.concat([data,df], ignore_index=True, axis=0, sort=False)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Systematics: use factory function to calculate yield variations
print " .........................................................................................."
from calcSystematics import factoryType, addConstantSyst, experimentalSystFactory, theorySystFactory, groupSystematics, envelopeSystematics, renameSyst

if opt.doSystematics:

  # Extract factory types of systematics
  print " --> [VERBOSE] Extracting factory types for systematics"
  experimentalFactoryType = {}
  theoryFactoryType = {}
  for s in experimental_systematics:
    if s['type'] == 'factory': 
      if s['name'] == 'JetHEM': experimentalFactoryType[s['name']] = "a_h"
      else: experimentalFactoryType[s['name']] = factoryType(data,s)
  for s in theory_systematics:
    if s['type'] == 'factory': theoryFactoryType[s['name']] = factoryType(data,s)
  
  # Experimental:
  print " --> [VERBOSE] Adding experimental systematics variations to dataFrame"
  # Add constant systematics to dataFrame
  for s in experimental_systematics:
    if s['type'] == 'constant': data = addConstantSyst(data,s,opt)
  data = experimentalSystFactory(data, experimental_systematics, experimentalFactoryType, opt )

  # Theory:
  print " --> [VERBOSE] Adding theory systematics variations to dataFrame"
  # Add constant systematics to dataFrame
  for s in theory_systematics:
    if s['type'] == 'constant': data = addConstantSyst(data,s,opt)
  # Theory factory: group scale weights after calculation in relevant grouping scheme
  if opt.doSTXSBinMerging: 
    data = theorySystFactory(data, theory_systematics, theoryFactoryType, opt, stxsMergeScheme=stxsBinMergingScheme)
    data, theory_systematics = groupSystematics(data, theory_systematics, opt, prefix="scaleWeight", groupings=[[4,8]], stxsMergeScheme=stxsBinMergingScheme)
    data, theory_systematics = groupSystematics(data, theory_systematics, opt, prefix="alphaSWeight", groupings=[[0,1]], stxsMergeScheme=stxsBinMergingScheme)
  else: 
    data = theorySystFactory(data, theory_systematics, theoryFactoryType, opt)
    data, theory_systematics = groupSystematics(data, theory_systematics, opt, prefix="scaleWeight", groupings=[[1,2],[3,6],[4,8]])
    #data, theory_systematics = groupSystematics(data, theory_systematics, opt, prefix="alphaSWeight", groupings=[[0,1]])

  # Rename systematics
  for s in theory_systematics: s['title'] = renameSyst(s['title'],"scaleWeight","scale")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Pruning: if process contributes less than 0.1% of yield in analysis category then ignore
print " .........................................................................................."
if opt.prune:
  print " --> [VERBOSE] Pruning processes which contribute < 0.1% of RECO category yield"
  data['prune'] = 0
  # Add cross section and ea info to dataframe, then calc true yield
  data['xsbr'] = '-'
  data['ea'] = '-'
  data['true_yield'] = '-'
  mask = (data['type']=='sig')
  # XSBR
  data.loc[mask,'xsbr'] = data[mask].apply(lambda x : stxs_xs["_".join(x['proc'].split("_")[:-2])], axis=1)
  # Eff x Acc
  procYields = {}
  for proc in data[mask]['proc'].unique(): procYields[proc] = data[data['proc']==proc]['nominal_yield_COWCorr'].sum()
  data.loc[mask,'ea'] = data[mask].apply(lambda x : 0 if procYields[x['proc']] == 0 else x['nominal_yield']/procYields[x['proc']], axis=1 )
  # True yields
  data.loc[mask,'true_yield'] = data[mask].apply(lambda x: x['xsbr']*x['ea']*x['rate'], axis=1)

  # Extract per category yields
  catTrueYields = {}
  for cat in data.cat.unique(): catTrueYields[cat] = data[(data['cat']==cat)&(data['type']=='sig')].true_yield.sum()

  # Set prune = 1 if < 0.1% of total cat yield
  mask = (data['true_yield']<opt.pruneThreshold*data.apply(lambda x: catTrueYields[x['cat']], axis=1))&(data['type']=='sig')&(~data['cat'].str.contains('NOTAG'))
  data.loc[mask,'prune'] = 1
  # Also set all NOTAG events to be pruned
  mask = data['cat'].str.contains("NOTAG")
  data.loc[mask,'prune'] = 1

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SAVE DATAFRAME
if opt.saveDataFrame != '':
  print " .........................................................................................."
  print " --> [VERBOSE] Saving dataFrame: ./hgg_dataFrames/%s.pkl"%opt.saveDataFrame
  if not os.path.isdir("./hgg_dataFrames"): os.system("mkdir ./hgg_dataFrames")
  with open("./hgg_dataFrames/%s.pkl"%opt.saveDataFrame,"wb") as fD: pickle.dump(data,fD)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# WRITE TO .TXT FILE
print " .........................................................................................."
fdataName = "%s"%opt.output
print " --> [VERBOSE] Writing to datacard file: %s"%fdataName
from writeToDatacard import writePreamble, writeProcesses, writeSystematic, writePdfIndex, writeBreak
fdata = open(fdataName,"w")
if not writePreamble(fdata,opt): 
  print " --> [ERROR] in writing preamble. Leaving..."
  leave()
if not writeProcesses(fdata,data,opt):
  print " --> [ERROR] in writing processes. Leaving..."
  leave()
if opt.doSystematics:
  for syst in experimental_systematics:
    if not writeSystematic(fdata,data,syst,opt):
      print " --> [ERROR] in writing systematic %s (experiment). Leaving"%syst['name']
      leave()
  writeBreak(fdata)
  for syst in theory_systematics:
    if not writeSystematic(fdata,data,syst,opt,stxsMergeScheme=stxsBinMergingScheme,scaleCorrScheme=scaleCorrelationScheme):
      print " --> [ERROR] in writing systematic %s (theory). Leaving"%syst['name']
      leave()
  writeBreak(fdata)
  for syst in signal_shape_systematics:
    if not writeSystematic(fdata,data,syst,opt):
      print " --> [ERROR] in writing systematic %s (signal shape). Leaving"%syst['name']
      leave()
if not writePdfIndex(fdata,data,opt):
  print " --> [ERROR] in writing pdf indices. Leaving..."
  leave()
fdata.close()


