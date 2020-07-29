# Script for calculating UEPS variations
# Output json: UE/PS shifts for all available proc x cats

import os, sys
import re
from optparse import OptionParser
import ROOT
import pandas as pd
import glob
import json
import pickle
import math
from collections import OrderedDict

# Mapping to STXS bin and nominal dataset name:
def procToSTXS( _proc ):
  #Do mapping
  proc_map = {"GG2H":"ggH","VBF":"qqH","WH2HQQ":"WH_had","ZH2HQQ":"ZH_had","QQ2HLNU":"WH_lep","QQ2HLL":"ZH_lep","TTH":"ttH","BBH":"bbH","THQ":"tHq","THW":"tHW","TH":"tHq","GG2HQQ":"ggZH_had","GG2HLL":"ggZH_ll","GG2HNUNU":"ggZH_nunu"}
  for key in proc_map:
    if key == _proc.split("_")[0]: _proc = re.sub( key, proc_map[key], _proc )
  return _proc

def get_options():
  parser = OptionParser()
  parser.add_option('--inputUEPSYieldsDir', dest='inputUEPSYieldsDir', default='./ueps_dataframes', help="Path to input UEPS yields pkl files (from extractUEPS.py)")
  parser.add_option('--year', dest='year', default='2016', help='Year tag to add to output')
  return parser.parse_args()
(opt,args) = get_options()

# Concatenate dataframe
pkl_files = glob.glob("%s/yields_*.pkl"%opt.inputUEPSYieldsDir)
data = pd.DataFrame()
for f_pkl_name in pkl_files:
  with open(f_pkl_name,"rb") as f_pkl:
    df = pickle.load(f_pkl)
    data = pd.concat([data,df], ignore_index=True, axis=0, sort=False)

# Calculate total yields for each stage 0 and 1.2 bins
stage0Yields = {}
stage0YieldsError = {}
stage1p2Yields = {}
stage1p2YieldsError = {}
stage0_procs = []
for proc in data['proc'].unique():
  if proc.split("_")[0] not in stage0Yields.keys(): 
    for mode in ['nominal','ue_up','ue_down','ps_up','ps_down']:
      stage0Yields['%s_%s'%(proc.split("_")[0],mode)] = data[(data['type']==mode)&(data['proc'].str.contains(proc.split("_")[0]))]['theory_yield'].sum()
      if stage0Yields['%s_%s'%(proc.split("_")[0],mode)] == 0: stage0YieldsError['%s_%s'%(proc.split("_")[0],mode)] = 0
      else: 
        stage0YieldsError['%s_%s'%(proc.split("_")[0],mode)] = math.sqrt( data[(data['type']==mode)&(data['proc'].str.contains(proc.split("_")[0]))]['theory_wsq'].sum() )
  for mode in ['nominal','ue_up','ue_down','ps_up','ps_down']:
    stage1p2Yields['%s_%s'%(proc,mode)] = data[(data['type']==mode)&(data['proc']==proc)]['theory_yield'].sum()
    if stage1p2Yields['%s_%s'%(proc,mode)] == 0: stage1p2YieldsError['%s_%s'%(proc,mode)] = 0
    else: 
      stage1p2YieldsError['%s_%s'%(proc,mode)] = math.sqrt( data[(data['type']==mode)&(data['proc']==proc)]['theory_wsq'].sum() )

# Create new dataframe
_columns = ['type','proc','cat','exp_yield','exp_error','theory_yield','theory_error','proc_s0_yield','proc_s0_error','proc_yield','proc_error']
df = pd.DataFrame(columns=_columns)
# Loop over unique: proc,cat,types in input dataframe and fill
for proc in data['proc'].unique():
  print " --> Adding process to dataframe: %s"%procToSTXS(proc)
  for cat in data[data['proc']==proc]['cat'].unique():
    for mode in data[(data['proc']==proc)&(data['cat']==cat)]['type'].unique():
      mask = (data['type']==mode)&(data['proc']==proc)&(data['cat']==cat)
      ey = data[mask]['exp_yield'].sum()
      ee = math.sqrt(data[mask]['exp_wsq'].sum())
      ty = data[mask]['theory_yield'].sum()
      te = math.sqrt(data[mask]['theory_wsq'].sum())
      s0y = stage0Yields["%s_%s"%(proc.split("_")[0],mode)]
      s0e = stage0YieldsError["%s_%s"%(proc.split("_")[0],mode)]
      s1p2y = stage1p2Yields["%s_%s"%(proc,mode)]
      s1p2e = stage1p2YieldsError["%s_%s"%(proc,mode)]
      df.loc[len(df)] = [mode,procToSTXS(proc),cat,ey,ee,ty,te,s0y,s0e,s1p2y,s1p2e]

# Save dataframe

# Calculate fractions
df['stxs_frac'] = df.apply(lambda x: x['proc_yield']/x['proc_s0_yield'], axis=1)
df['stxs_frac_error'] = df.apply(lambda x: x['stxs_frac']*math.sqrt((x['proc_error']/x['proc_yield'])**2+(x['proc_s0_error']/x['proc_s0_yield'])**2), axis=1)
with open("./ueps_dataframe_tmp.pkl","wb") as f: pickle.dump(df,f)

#df['ea_frac'] = df.apply(lambda x: x['exp_yield']/x['proc_yield'], axis=1)
#df['ea_frac_error'] = df.apply(lambda x: x['ea_frac']*math.sqrt((x['exp_error']/x['exp_yield'])*(x['exp_error']/x['exp_yield'])+(x['proc_error']/x['proc_yield'])*()), axis=1)

# Loop over processes
ueps_norm = {}
ueps_norm_err = {}
#ueps_shape = {}
for proc in df['proc'].unique():
  print " --> Proc = %s"%proc
  ueps_norm[proc] = {}
  ueps_norm_err[proc] = {}
  mask = (df['proc']==proc)&(df['type']=='nominal')
  nominal_stxs_frac = df[mask].iloc[0].stxs_frac
  nominal_stxs_frac_err = df[mask].iloc[0].stxs_frac_error
  for mode in ['ue_up','ue_down','ps_up','ps_down']:
    mask = (df['proc']==proc)&(df['type']==mode)
    if len(df[mask]) == 0: 
      ueps_norm[proc][mode] = 1.
      ueps_norm_err[proc][mode] = 0.#nominal_stxs_frac_err
    else: 
      var_stxs_frac = df[mask].iloc[0].stxs_frac/nominal_stxs_frac
      var_stxs_frac_err = var_stxs_frac*math.sqrt((df[mask].iloc[0].stxs_frac_error/df[mask].iloc[0].stxs_frac)**2+(nominal_stxs_frac_err/nominal_stxs_frac)**2)
      ueps_norm[proc][mode] = var_stxs_frac
      ueps_norm_err[proc][mode] = var_stxs_frac_err
      
  # Loop over cats 
  # Not enough stats for ttH shape uncertainties therefore skip
  #if "ttH" in proc: continue
  #mask = (df['proc']==proc)&(df['type']=='nominal')
  #for cat in df[mask]['cat'].unique():
  #  key = "%s__%s"%(proc,cat)
  #  mask = (df['proc']==proc)&(df['type']=='nominal')&(df['cat']==cat)
  #  if len(df[mask])==0: continue
  #  ueps_shape[key] = {}
  #  nominal_ea_frac = df[mask].iloc[0].ea_frac
  #  for mode in ['ue_up','ue_down','ps_up','ps_down']:
  #    mask = (df['proc']==proc)&(df['type']==mode)&(df['cat']==cat)
  #    if len(df[mask]) == 0: ueps_shape[key][mode] = 1.
  #    elif nominal_ea_frac < 0.01: ueps_shape[key][mode] = 1.
  #    else: 
  #      var_ea_frac = df[mask].iloc[0].ea_frac/nominal_ea_frac
  #      ueps_shape[key][mode] = var_ea_frac

# Print variations to file
with open("./theory_uncertainties/ueps_norm_%s.txt"%opt.year,"w") as f:
  f.write("Proc: (UE down) (UE up) ::: (PS down) (PS up)\n\n")
  for k in df.proc.unique():
    f.write("%-50s: (%.4f +- %.4f) (%.4f +- %.4f) ::: (%.4f +- %.4f) (%.4f +- %.4f)\n"%(k,ueps_norm[k]['ue_down'],ueps_norm_err[k]['ue_down'],ueps_norm[k]['ue_up'],ueps_norm_err[k]['ue_up'],ueps_norm[k]['ps_down'],ueps_norm_err[k]['ps_down'],ueps_norm[k]['ps_up'],ueps_norm_err[k]['ps_up']))

# Clean up systematics
# Max and min thresholds
max_thr, min_thr = 1.5, 0.5
for k, syst_vars in ueps_norm.iteritems():
  for syst in syst_vars: 
    ueps_norm[k][syst] = min(syst_vars[syst],max_thr)
    ueps_norm[k][syst] = max(syst_vars[syst],min_thr)

# One sided: take maximum var
for k, syst_vars in ueps_norm.iteritems():
  for syst in ['ue','ps']:
    if(syst_vars['%s_up'%syst] >= 1.)&(syst_vars['%s_down'%syst] >= 1.):
      if syst_vars['%s_up'%syst] > syst_vars['%s_down'%syst]: 
        ueps_norm[k]['%s_down'%syst] = 1-abs(ueps_norm[k]['%s_up'%syst]-1)
      else:
        ueps_norm[k]['%s_up'%syst] = 1-abs(ueps_norm[k]['%s_down'%syst]-1)
    elif(syst_vars['%s_up'%syst] <= 1.)&(syst_vars['%s_down'%syst] <= 1.):
      if syst_vars['%s_up'%syst] < syst_vars['%s_down'%syst]: 
        ueps_norm[k]['%s_down'%syst] = 1+abs(1-ueps_norm[k]['%s_up'%syst])
      else:
        ueps_norm[k]['%s_up'%syst] = 1+abs(1-ueps_norm[k]['%s_down'%syst])

#for k, syst_vars in ueps_shape.iteritems():
#  for syst in syst_vars: 
#    ueps_shape[k][syst] = min(syst_vars[syst],max_thr)
#    ueps_shape[k][syst] = max(syst_vars[syst],min_thr)

# One sided: take maximum var
#for k, syst_vars in ueps_shape.iteritems():
#  for syst in ['ue','ps']:
#    if(syst_vars['%s_up'%syst] >= 1.)&(syst_vars['%s_down'%syst] >= 1.):
#      if syst_vars['%s_up'%syst] > syst_vars['%s_down'%syst]: 
#        ueps_shape[k]['%s_down'%syst] = 1-abs(ueps_shape[k]['%s_up'%syst]-1)
#      else:
#        ueps_shape[k]['%s_up'%syst] = 1-abs(ueps_shape[k]['%s_down'%syst]-1)
#    elif(syst_vars['%s_up'%syst] <= 1.)&(syst_vars['%s_down'%syst] <= 1.):
#      if syst_vars['%s_up'%syst] < syst_vars['%s_down'%syst]: 
#        ueps_shape[k]['%s_down'%syst] = 1+abs(1-ueps_shape[k]['%s_up'%syst])
#      else:
#        ueps_shape[k]['%s_up'%syst] = 1+abs(1-ueps_shape[k]['%s_down'%syst])
#
# Save json files
with open("./theory_uncertainties/ueps_norm_%s.json"%opt.year,"w") as jsonfile: json.dump(ueps_norm,jsonfile)
#with open("./theory_uncertainties/ueps_shape.json","w") as jsonfile: json.dump(ueps_shape,jsonfile)
