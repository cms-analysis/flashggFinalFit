import os, sys
import glob
import re
from optparse import OptionParser
import ROOT
import pandas
import uproot
import pickle

def get_options():
  parser = OptionParser()
  parser.add_option('--inputTreeFile',dest='inputTreeFile', default="", help="Input file")
  parser.add_option('--year',dest='year',default="2016", help="Year")
  parser.add_option('--mode',dest='mode',default="nominal", help="Looping over nominal trees or UEPS trees")
  parser.add_option('--ext',dest='ext',default="", help="Extension for saving dataframe")
  return parser.parse_args()
(opt,args) = get_options()

from tools.STXS_tools import flashggSTXSDict
from commonTools import *

# Analysis categories
if opt.mode == "nominal":
  cats = ['RECO_0J_PTH_0_10_Tag0', 'RECO_0J_PTH_0_10_Tag1', 'RECO_0J_PTH_0_10_Tag2', 'RECO_0J_PTH_GT10_Tag0', 'RECO_0J_PTH_GT10_Tag1', 'RECO_0J_PTH_GT10_Tag2', 'RECO_1J_PTH_0_60_Tag0', 'RECO_1J_PTH_0_60_Tag1', 'RECO_1J_PTH_0_60_Tag2', 'RECO_1J_PTH_120_200_Tag0', 'RECO_1J_PTH_120_200_Tag1', 'RECO_1J_PTH_120_200_Tag2', 'RECO_1J_PTH_60_120_Tag0', 'RECO_1J_PTH_60_120_Tag1', 'RECO_1J_PTH_60_120_Tag2', 'RECO_GE2J_PTH_0_60_Tag0', 'RECO_GE2J_PTH_0_60_Tag1', 'RECO_GE2J_PTH_0_60_Tag2', 'RECO_GE2J_PTH_120_200_Tag0', 'RECO_GE2J_PTH_120_200_Tag1', 'RECO_GE2J_PTH_120_200_Tag2', 'RECO_GE2J_PTH_60_120_Tag0', 'RECO_GE2J_PTH_60_120_Tag1', 'RECO_GE2J_PTH_60_120_Tag2', 'RECO_PTH_200_300_Tag0', 'RECO_PTH_200_300_Tag1', 'RECO_PTH_300_450_Tag0', 'RECO_PTH_300_450_Tag1', 'RECO_PTH_450_650_Tag0', 'RECO_PTH_GT650_Tag0', 'RECO_THQ_LEP', 'RECO_TTH_HAD_PTH_0_60_Tag0', 'RECO_TTH_HAD_PTH_0_60_Tag1', 'RECO_TTH_HAD_PTH_120_200_Tag0', 'RECO_TTH_HAD_PTH_120_200_Tag1', 'RECO_TTH_HAD_PTH_200_300_Tag0', 'RECO_TTH_HAD_PTH_200_300_Tag1', 'RECO_TTH_HAD_PTH_60_120_Tag0', 'RECO_TTH_HAD_PTH_60_120_Tag1', 'RECO_TTH_HAD_PTH_GT300_Tag0', 'RECO_TTH_HAD_PTH_GT300_Tag1', 'RECO_TTH_LEP_PTH_0_60_Tag0', 'RECO_TTH_LEP_PTH_0_60_Tag1', 'RECO_TTH_LEP_PTH_120_200_Tag0', 'RECO_TTH_LEP_PTH_120_200_Tag1', 'RECO_TTH_LEP_PTH_200_300_Tag0', 'RECO_TTH_LEP_PTH_60_120_Tag0', 'RECO_TTH_LEP_PTH_60_120_Tag1', 'RECO_TTH_LEP_PTH_GT300_Tag0', 'RECO_VBFLIKEGGH_Tag0', 'RECO_VBFLIKEGGH_Tag1', 'RECO_VBFTOPO_BSM_Tag0', 'RECO_VBFTOPO_BSM_Tag1', 'RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag0', 'RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag1', 'RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag0', 'RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag1', 'RECO_VBFTOPO_JET3_HIGHMJJ_Tag0', 'RECO_VBFTOPO_JET3_HIGHMJJ_Tag1', 'RECO_VBFTOPO_JET3_LOWMJJ_Tag0', 'RECO_VBFTOPO_JET3_LOWMJJ_Tag1', 'RECO_VBFTOPO_VHHAD_Tag0', 'RECO_VBFTOPO_VHHAD_Tag1', 'RECO_VH_MET_Tag0', 'RECO_VH_MET_Tag1', 'RECO_VH_MET_Tag2', 'RECO_WH_LEP_PTV_0_75_Tag0', 'RECO_WH_LEP_PTV_0_75_Tag1', 'RECO_WH_LEP_PTV_75_150_Tag0', 'RECO_WH_LEP_PTV_75_150_Tag1', 'RECO_WH_LEP_PTV_GT150_Tag0', 'RECO_ZH_LEP_Tag0', 'RECO_ZH_LEP_Tag1','NOTAG']
elif opt.mode == "ueps":
  cats = ['RECO_0J_PTH_0_10_Tag0', 'RECO_0J_PTH_0_10_Tag1', 'RECO_0J_PTH_0_10_Tag2', 'RECO_0J_PTH_GT10_Tag0', 'RECO_0J_PTH_GT10_Tag1', 'RECO_0J_PTH_GT10_Tag2', 'RECO_1J_PTH_0_60_Tag0', 'RECO_1J_PTH_0_60_Tag1', 'RECO_1J_PTH_0_60_Tag2', 'RECO_1J_PTH_120_200_Tag0', 'RECO_1J_PTH_120_200_Tag1', 'RECO_1J_PTH_120_200_Tag2', 'RECO_1J_PTH_60_120_Tag0', 'RECO_1J_PTH_60_120_Tag1', 'RECO_1J_PTH_60_120_Tag2', 'RECO_GE2J_PTH_0_60_Tag0', 'RECO_GE2J_PTH_0_60_Tag1', 'RECO_GE2J_PTH_0_60_Tag2', 'RECO_GE2J_PTH_120_200_Tag0', 'RECO_GE2J_PTH_120_200_Tag1', 'RECO_GE2J_PTH_120_200_Tag2', 'RECO_GE2J_PTH_60_120_Tag0', 'RECO_GE2J_PTH_60_120_Tag1', 'RECO_GE2J_PTH_60_120_Tag2', 'RECO_PTH_200_300_Tag0', 'RECO_PTH_200_300_Tag1', 'RECO_PTH_300_450_Tag0', 'RECO_PTH_300_450_Tag1', 'RECO_PTH_450_650_Tag0', 'RECO_PTH_GT650_Tag0', 'RECO_THQ_LEP', 'RECO_TTH_HAD_PTH_0_60_Tag0', 'RECO_TTH_HAD_PTH_0_60_Tag1', 'RECO_TTH_HAD_PTH_0_60_Tag2', 'RECO_TTH_HAD_PTH_0_60_Tag3', 'RECO_TTH_HAD_PTH_120_200_Tag0', 'RECO_TTH_HAD_PTH_120_200_Tag1', 'RECO_TTH_HAD_PTH_120_200_Tag2', 'RECO_TTH_HAD_PTH_120_200_Tag3', 'RECO_TTH_HAD_PTH_60_120_Tag0', 'RECO_TTH_HAD_PTH_60_120_Tag1', 'RECO_TTH_HAD_PTH_60_120_Tag2', 'RECO_TTH_HAD_PTH_60_120_Tag3', 'RECO_TTH_HAD_PTH_GT200_Tag0', 'RECO_TTH_HAD_PTH_GT200_Tag1', 'RECO_TTH_HAD_PTH_GT200_Tag2', 'RECO_TTH_HAD_PTH_GT200_Tag3', 'RECO_TTH_LEP_PTH_0_60_Tag0', 'RECO_TTH_LEP_PTH_0_60_Tag1', 'RECO_TTH_LEP_PTH_0_60_Tag2', 'RECO_TTH_LEP_PTH_0_60_Tag3', 'RECO_TTH_LEP_PTH_120_200_Tag0', 'RECO_TTH_LEP_PTH_120_200_Tag1', 'RECO_TTH_LEP_PTH_60_120_Tag0', 'RECO_TTH_LEP_PTH_60_120_Tag1', 'RECO_TTH_LEP_PTH_GT200_Tag0', 'RECO_TTH_LEP_PTH_GT200_Tag1', 'RECO_VBFLIKEGGH_Tag0', 'RECO_VBFLIKEGGH_Tag1', 'RECO_VBFTOPO_BSM_Tag0', 'RECO_VBFTOPO_BSM_Tag1', 'RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag0', 'RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag1', 'RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag0', 'RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag1', 'RECO_VBFTOPO_JET3_HIGHMJJ_Tag0', 'RECO_VBFTOPO_JET3_HIGHMJJ_Tag1', 'RECO_VBFTOPO_JET3_LOWMJJ_Tag0', 'RECO_VBFTOPO_JET3_LOWMJJ_Tag1', 'RECO_VBFTOPO_VHHAD_Tag0', 'RECO_VBFTOPO_VHHAD_Tag1', 'RECO_VH_MET_Tag0', 'RECO_VH_MET_Tag1', 'RECO_VH_MET_Tag2', 'RECO_WH_LEP_PTV_0_75_Tag0', 'RECO_WH_LEP_PTV_0_75_Tag1', 'RECO_WH_LEP_PTV_75_150_Tag0', 'RECO_WH_LEP_PTV_75_150_Tag1', 'RECO_WH_LEP_PTV_GT150_Tag0', 'RECO_ZH_LEP_Tag0', 'RECO_ZH_LEP_Tag1', 'NOTAG']
else: 
  print " Mode (%s) not supported."%opt.mode
  sys.exit(1)

def extractType(_f,_y):
  if _y == '2016':
    if "UpPS" in _f: return "ps_up"
    elif "DownPS" in _f: return "ps_down"
    elif "CUETP8M1Up" in _f: return "ue_up"
    elif "CUETP8M1Down" in _f: return "ue_down"
    else:
      print " --> Type (UEPS) not recognised for file: %s. Skipping"%_f
      sys.exit(1)
  elif _y == '2017':
    if "UpPS" in _f: return "ps_up"
    elif "DownPS" in _f: return "ps_down"
    elif "CP5Up" in _f: return "ue_up"
    elif "CP5Down" in _f: return "ue_down"
    else:
      print " --> Type (UEPS) not recognised for file: %s. Skipping"%_f
      sys.exit(1)
  elif _y == '2018':
    if "UpPS" in _f: return "ps_up"
    elif "DownPS" in _f: return "ps_down"
    elif "TuneCP5Down" in _f: return "ue_down"
    elif "TuneCP5Up" in _f: return "ue_up"
    else:
      print " --> Type (UEPS) not recognised for file: %s. Skipping"%_f
      sys.exit(1)
  else:
    print " --> Year not recognised: %s. Skipping"%_y
    sys.exit(1)


# Define variables to store in dataframe
tree_vars = ["stage1p2bin","weight","centralObjectWeight","NNLOPSweight"]
tree_vars_notag = ["stage1p2bin","weight"]#,"THU_ggH_qmtopUp01sigma","THU_ggH_qmtopDown01sigma"]

# Define dataframe to store 
_columns = ['file_id','production_mode','type','proc','cat','year','stage1p2bin','exp_yield','exp_wsq','theory_yield','theory_wsq']
data = pandas.DataFrame( columns=_columns )

# Extract files in nominal dir
f_name = opt.inputTreeFile
print " --> Processing file: %s"%f_name

# Extract production mode, type, file id
pm = signalFromFileName(f_name)[0]
if opt.mode == "nominal": ftype = "nominal"
else: ftype = extractType(f_name,opt.year)
f_id = re.sub(".root","",f_name.split("_")[-1])

# Uproot file
f = uproot.open(f_name)

# Loop over cats
for cat in cats:

  # Extract tree
  if opt.mode == "nominal": t_name = "tagsDumper/trees/%s_125_13TeV_%s"%(pm,cat)
  else: t_name = "tagsDumper/trees/%s_125_%s_13TeV_%s"%(pm,ftype,cat)
  print "   * tree = %s"%t_name    
  t = f[t_name]
  if len(t) == 0: continue
  
  # Convert tree to pandas dataframe: treat notag differently as has different vars
  if cat == "NOTAG":
    df = t.pandas.df(tree_vars_notag)
    df['centralObjectWeight'] = 1. #df.apply(lambda x: 0.5*(x['THU_ggH_qmtopUp01sigma']+x['THU_ggH_qmtopDown01sigma']), axis=1)
    df['NNLOPSweight'] = 1. #df.apply(lambda x: 0.5*(x['THU_ggH_qmtopUp01sigma']+x['THU_ggH_qmtopDown01sigma']), axis=1) 
  else: df = t.pandas.df(tree_vars)

  # Remove entries with 0 central object weight
  df = df[df['centralObjectWeight']!=0.]

  # Loop over different procs and fill entries in total dataframe
  for stxsid in df['stage1p2bin'].unique():
    proc = flashggSTXSDict[stxsid]
    if pm == "vbf": proc = re.sub("QQ2HQQ","VBF",proc)
    elif pm == "wh": proc = re.sub("QQ2HQQ","WH2HQQ",proc)
    elif pm == "zh": proc = re.sub("QQ2HQQ","ZH2HQQ",proc)
    mask = (df['stage1p2bin']==stxsid)
    exp_yield = df[mask]['weight'].sum() 
    exp_wsq = df[mask].apply(lambda x: x['weight']*x['weight'],axis=1).sum()
    theory_yield = df[mask].apply( lambda x: x['weight']*(x['NNLOPSweight']/x['centralObjectWeight']), axis=1).sum()
    theory_wsq = df[mask].apply( lambda x: (x['weight']*(x['NNLOPSweight']/x['centralObjectWeight']))*(x['weight']*(x['NNLOPSweight']/x['centralObjectWeight'])), axis=1).sum()
    data.loc[len(data)] = [f_id,pm,ftype,procToDatacardName(proc),cat,opt.year,stxsid,exp_yield,exp_wsq,theory_yield,theory_wsq]

# Save dataframe
if not os.path.isdir("ueps_dataframes_%s"%opt.year): os.system("mkdir ueps_dataframes_%s"%opt.year)
with open("./ueps_dataframes_%s/yields%s.pkl"%(opt.year,opt.ext),"wb") as fD: pickle.dump(data,fD)
