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
  parser.add_option('--mode',dest='mode',default="nominal", help="Looping over nominal trees or UEPS trees")
  parser.add_option('--ext',dest='ext',default="", help="Extension for saving dataframe")
  return parser.parse_args()
(opt,args) = get_options()


# Analysis categories
cats = ['RECO_0J_PTH_0_10_Tag0', 'RECO_0J_PTH_0_10_Tag1', 'RECO_0J_PTH_0_10_Tag2', 'RECO_0J_PTH_GT10_Tag0', 'RECO_0J_PTH_GT10_Tag1', 'RECO_0J_PTH_GT10_Tag2', 'RECO_1J_PTH_0_60_Tag0', 'RECO_1J_PTH_0_60_Tag1', 'RECO_1J_PTH_0_60_Tag2', 'RECO_1J_PTH_120_200_Tag0', 'RECO_1J_PTH_120_200_Tag1', 'RECO_1J_PTH_120_200_Tag2', 'RECO_1J_PTH_60_120_Tag0', 'RECO_1J_PTH_60_120_Tag1', 'RECO_1J_PTH_60_120_Tag2', 'RECO_GE2J_PTH_0_60_Tag0', 'RECO_GE2J_PTH_0_60_Tag1', 'RECO_GE2J_PTH_0_60_Tag2', 'RECO_GE2J_PTH_120_200_Tag0', 'RECO_GE2J_PTH_120_200_Tag1', 'RECO_GE2J_PTH_120_200_Tag2', 'RECO_GE2J_PTH_60_120_Tag0', 'RECO_GE2J_PTH_60_120_Tag1', 'RECO_GE2J_PTH_60_120_Tag2', 'RECO_PTH_200_300_Tag0', 'RECO_PTH_200_300_Tag1', 'RECO_PTH_300_450_Tag0', 'RECO_PTH_300_450_Tag1', 'RECO_PTH_450_650_Tag0', 'RECO_PTH_GT650_Tag0', 'RECO_THQ_LEP', 'RECO_TTH_HAD_PTH_0_60_Tag0', 'RECO_TTH_HAD_PTH_0_60_Tag1', 'RECO_TTH_HAD_PTH_0_60_Tag2', 'RECO_TTH_HAD_PTH_0_60_Tag3', 'RECO_TTH_HAD_PTH_120_200_Tag0', 'RECO_TTH_HAD_PTH_120_200_Tag1', 'RECO_TTH_HAD_PTH_120_200_Tag2', 'RECO_TTH_HAD_PTH_120_200_Tag3', 'RECO_TTH_HAD_PTH_60_120_Tag0', 'RECO_TTH_HAD_PTH_60_120_Tag1', 'RECO_TTH_HAD_PTH_60_120_Tag2', 'RECO_TTH_HAD_PTH_60_120_Tag3', 'RECO_TTH_HAD_PTH_GT200_Tag0', 'RECO_TTH_HAD_PTH_GT200_Tag1', 'RECO_TTH_HAD_PTH_GT200_Tag2', 'RECO_TTH_HAD_PTH_GT200_Tag3', 'RECO_TTH_LEP_PTH_0_60_Tag0', 'RECO_TTH_LEP_PTH_0_60_Tag1', 'RECO_TTH_LEP_PTH_0_60_Tag2', 'RECO_TTH_LEP_PTH_0_60_Tag3', 'RECO_TTH_LEP_PTH_120_200_Tag0', 'RECO_TTH_LEP_PTH_120_200_Tag1', 'RECO_TTH_LEP_PTH_60_120_Tag0', 'RECO_TTH_LEP_PTH_60_120_Tag1', 'RECO_TTH_LEP_PTH_GT200_Tag0', 'RECO_TTH_LEP_PTH_GT200_Tag1', 'RECO_VBFLIKEGGH_Tag0', 'RECO_VBFLIKEGGH_Tag1', 'RECO_VBFTOPO_BSM_Tag0', 'RECO_VBFTOPO_BSM_Tag1', 'RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag0', 'RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag1', 'RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag0', 'RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag1', 'RECO_VBFTOPO_JET3_HIGHMJJ_Tag0', 'RECO_VBFTOPO_JET3_HIGHMJJ_Tag1', 'RECO_VBFTOPO_JET3_LOWMJJ_Tag0', 'RECO_VBFTOPO_JET3_LOWMJJ_Tag1', 'RECO_VBFTOPO_VHHAD_Tag0', 'RECO_VBFTOPO_VHHAD_Tag1', 'RECO_VH_MET_Tag0', 'RECO_VH_MET_Tag1', 'RECO_WH_LEP_HIGH_Tag0', 'RECO_WH_LEP_HIGH_Tag1', 'RECO_WH_LEP_HIGH_Tag2', 'RECO_WH_LEP_LOW_Tag0', 'RECO_WH_LEP_LOW_Tag1', 'RECO_WH_LEP_LOW_Tag2', 'RECO_ZH_LEP_Tag0', 'RECO_ZH_LEP_Tag1', 'NOTAG']

stxs_stage1p2_dict = {
  0:"UNKNOWN",
  -1:"GG2H_FWDH",
  1:"GG2H_PTH_200_300",
  2:"GG2H_PTH_300_450",
  3:"GG2H_PTH_450_650",
  4:"GG2H_PTH_GT650",
  5:"GG2H_0J_PTH_0_10",
  6:"GG2H_0J_PTH_GT10",
  7:"GG2H_1J_PTH_0_60",
  8:"GG2H_1J_PTH_60_120",
  9:"GG2H_1J_PTH_120_200",
  10:"GG2H_GE2J_MJJ_0_350_PTH_0_60",
  11:"GG2H_GE2J_MJJ_0_350_PTH_60_120",
  12:"GG2H_GE2J_MJJ_0_350_PTH_120_200",
  13:"GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25",
  14:"GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25",
  15:"GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25",
  16:"GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25",
  -2:"QQ2HQQ_FWDH",
  17:"QQ2HQQ_0J",
  18:"QQ2HQQ_1J",
  19:"QQ2HQQ_GE2J_MJJ_0_60",
  20:"QQ2HQQ_GE2J_MJJ_60_120",
  21:"QQ2HQQ_GE2J_MJJ_120_350",
  22:"QQ2HQQ_GE2J_MJJ_GT350_PTH_GT200",
  23:"QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25",
  24:"QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25",
  25:"QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25",
  26:"QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25",
  -3:"QQ2HLNU_FWDH",
  27:"QQ2HLNU_PTV_0_75",
  28:"QQ2HLNU_PTV_75_150",
  29:"QQ2HLNU_PTV_150_250_0J",
  30:"QQ2HLNU_PTV_150_250_GE1J",
  31:"QQ2HLNU_PTV_GT250",
  -4:"QQ2HLL_FWDH",
  32:"QQ2HLL_PTV_0_75",
  33:"QQ2HLL_PTV_75_150",
  34:"QQ2HLL_PTV_150_250_0J",
  35:"QQ2HLL_PTV_150_250_GE1J",
  36:"QQ2HLL_PTV_GT250",
  -5:"GG2HLL_FWDH",
  37:"GG2HLL_PTV_0_75",
  38:"GG2HLL_PTV_75_150",
  39:"GG2HLL_PTV_150_250_0J",
  40:"GG2HLL_PTV_150_250_GE1J",
  41:"GG2HLL_PTV_GT250",
  -6:"TTH_FWDH",
  42:"TTH_PTH_0_60",
  43:"TTH_PTH_60_120",
  44:"TTH_PTH_120_200",
  45:"TTH_PTH_200_300",
  46:"TTH_PTH_GT300",
  -7:"BBH_FWDH",
  47:"BBH",
  -8:"TH_FWDH",
  48:"TH"
}

def extractProductionMode(_f):
  if "GluGluHToGG" in _f: return 'ggh'
  elif "VBF" in _f: return 'vbf'
  elif "WHToGG" in _f: return 'wh'
  elif "ZHToGG" in _f: return 'zh'
  elif "ttHJetToGG" in _f: return 'tth'
  else:
    print " --> Production mode not recognised for file: %s. Skipping."%_f
    sys.exit(1)

def extractType(_f):
  if "UpPS" in _f: return "ps_up"
  elif "DownPS" in _f: return "ps_down"
  elif "CUETP8M1Up" in _f: return "ue_up"
  elif "CUETP8M1Down" in _f: return "ue_down"
  else:
    print " --> Type (UEPS) not recognised for file: %s. Skipping"%_f
    sys.exit(1)

# Define variables to store in dataframe
tree_vars = ["stage1p2bin","weight","centralObjectWeight","NNLOPSweight"]
tree_vars_notag = ["stage1p2bin","weight","THU_ggH_qmtopUp01sigma","THU_ggH_qmtopDown01sigma"]

# Define dataframe to store 
_columns = ['file_id','production_mode','type','proc','cat','stage1p2bin','exp_yield','exp_wsq','theory_yield','theory_wsq']
data = pandas.DataFrame( columns=_columns )

# Extract files in nominal dir
f_name = opt.inputTreeFile
print " --> Processing file: %s"%f_name

# Extract production mode, type, file id
pm = extractProductionMode(f_name)
if opt.mode == "nominal": ftype = "nominal"
else: ftype = extractType(f_name)
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
    df['centralObjectWeight'] = df.apply(lambda x: 0.5*(x['THU_ggH_qmtopUp01sigma']+x['THU_ggH_qmtopDown01sigma']), axis=1)
    df['NNLOPSweight'] = df.apply(lambda x: 0.5*(x['THU_ggH_qmtopUp01sigma']+x['THU_ggH_qmtopDown01sigma']), axis=1) 
  else: df = t.pandas.df(tree_vars)

  # Loop over different procs and fill entries in total dataframe
  for stxsid in df['stage1p2bin'].unique():
    proc = stxs_stage1p2_dict[stxsid]
    if pm == "vbf": proc = re.sub("QQ2HQQ","VBF",proc)
    elif pm == "wh": proc = re.sub("QQ2HQQ","WH2HQQ",proc)
    elif pm == "zh": proc = re.sub("QQ2HQQ","ZH2HQQ",proc)
    mask = (df['stage1p2bin']==stxsid)
    exp_yield = df[mask]['weight'].sum() 
    exp_wsq = df[mask].apply(lambda x: x['weight']*x['weight'],axis=1).sum()
    theory_yield = df[mask].apply( lambda x: x['weight']*(x['NNLOPSweight']/x['centralObjectWeight']), axis=1).sum()
    theory_wsq = df[mask].apply( lambda x: (x['weight']*(x['NNLOPSweight']/x['centralObjectWeight']))*(x['weight']*(x['NNLOPSweight']/x['centralObjectWeight'])), axis=1).sum()
    data.loc[len(data)] = [f_id,pm,ftype,proc,cat,stxsid,exp_yield,exp_wsq,theory_yield,theory_wsq]

# Save dataframe
if not os.path.isdir("ueps_dataframes"): os.system("mkdir ueps_dataframes")
with open("./ueps_dataframes/yields%s.pkl"%opt.ext,"wb") as fD: pickle.dump(data,fD)
