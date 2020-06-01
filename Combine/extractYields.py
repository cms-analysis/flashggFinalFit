import pandas as pd
import pickle
import ROOT
import re
import sys
from optparse import OptionParser

def get_options():
  parser = OptionParser()
  parser.add_option("-i", "--inputWS", dest="inputWS", default = "", help="Input RooWorkspace")
  return parser.parse_args()
(opt,args) = get_options()

def rooiter(x):
  iter = x.iterator()
  ret = iter.Next()
  while ret:
    yield ret
    ret = iter.Next()

def procToProcS0(p):
  if "ggH" in p: return "ggh"
  elif "qqH" in p: return "qqh"
  elif "WH_had" in p: return "wh"
  elif "ZH_had" in p: return "zh"
  elif "ggZH_had" in p: return "ggzh"
  elif "WH_lep" in p: return "wh"
  elif "ZH_lep" in p: return "zh"
  elif "ggZH_ll" in p: return "ggzh"
  elif "ggZH_nunu" in p: return "ggzh"
  elif "ttH" in p: return "tth"
  elif "tHq" in p: return "thq"
  elif "tHW" in p: return "thw"
  elif "bbH" in p: return "bbh"
  else: 
    print " --> [ERROR] proc s0 not realised for process %s. Leaving"%p
    sys.exit(1)

# Extract normalisations from workspace
f = ROOT.TFile(opt.inputWS)
ws = f.Get("w")
allNorms = ws.allFunctions().selectByName("n_exp_final*")

# Initialise dataFrame: proc, cat, yield
columns_data = ['proc','proc_s0','cat','nominal_yield']
data = pd.DataFrame( columns=columns_data )

# Loop over norms and fill dataframe with signal entries
for _func in rooiter(allNorms):
  _proc =  _func.GetName().split("_proc_")[-1]
  if "bkg_mass" in _proc: continue
  _proc_s0 = procToProcS0(_proc)
  _cat = cat = (_func.GetName().split("_proc_")[0]).split("bin")[-1]
  _nominal_yield = _func.getVal()
  data.loc[len(data)] = [_proc,_proc_s0,_cat,_nominal_yield]
   
# Save dataframe
outputFrame = re.sub(".root","_yields.pkl",opt.inputWS)
with open( outputFrame, "wb" ) as fD: pickle.dump(data,fD) 
