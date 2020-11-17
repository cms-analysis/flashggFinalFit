# Script to calculate eff x acc for different mass points
# * Relies on the presense of NOTAG dataset. If not there, script will give NAN as output
# * Also needs to run on all processed categories: take from file

print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG GET FRACTIONS MAKER RUN II ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
import os, sys
import re
from optparse import OptionParser
import ROOT
import pandas as pd
import glob
import pickle
import json
from collections import OrderedDict as od

from commonTools import *
from commonObjects import *

def leave():
  print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG GET FRACTIONS RUN II (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
  sys.exit(1)

def get_options():
  parser = OptionParser()
  parser.add_option('--inputWSDir', dest='inputWSDir', default='', help='Input WS directory')
  parser.add_option('--ext', default='test', help='Extension (to define analysis)')
  parser.add_option('--procs', dest='procs', default='', help='Signal processes')
  parser.add_option('--massPoints', dest='massPoints', default='120,125,130', help='MH')
  parser.add_option('--skipCOWCorr', dest='skipCOWCorr', default=False, action="store_true", help="Skip centralObjectWeight correction for events in acceptance")
  parser.add_option('--doSTXSFractions', dest='doSTXSFractions', default=False, action="store_true", help="Fractional cross sections in each STXS bin (per stage0 process)")
  return parser.parse_args()
(opt,args) = get_options()

# Extract all processed analysis categories
WSFileNames = extractWSFileNames(opt.inputWSDir)
if not WSFileNames: leave()
allCats = extractListOfCats(WSFileNames)
if containsNOTAG(WSFileNames): allCats += ",NOTAG"
else:
  print " --> [ERROR] getEffAcc.py requires NOTAG dataset. Must use standard weights method in signalFit.py"
  leave()

# Define dataframe to store yields: cow = centralObjectWeight
if opt.skipCOWCorr: columns_data = ['massPoint','proc','cat','granular_key','nominal_yield']
else: columns_data = ['massPoint','proc','cat','granular_key','nominal_yield','nominal_yield_COWCorr']
data = pd.DataFrame( columns=columns_data )

# Loop over mass points: write separate json file for each masspoint
for _mp in opt.massPoints.split(","):
  print " --> Processing mass point: %s"%_mp
  # Loop over processes
  for _proc in opt.procs.split(","):
    print "    * proc = %s"%_proc
    # Find corresponding file
    _WSFileName = glob.glob("%s/output*M%s*%s.root"%(opt.inputWSDir,_mp,_proc))[0]
    f = ROOT.TFile(_WSFileName,'read')
    inputWS = f.Get(inputWSName__)

    # Loop over categories
    for _cat in allCats.split(","):
      nominalDataName = "%s_%s_%s_%s"%(procToData(_proc.split("_")[0]),_mp,sqrts__,_cat)
      _granular_key = "%s__%s"%(_proc,_cat)
      nominalData = inputWS.data(nominalDataName)
      _nominal_yield = nominalData.sumEntries()
      # Central Object Weight corrections (for events in acceptance)
      if not opt.skipCOWCorr:
        # Loop over events and sum w/ centralObjectWeight
        _nominal_yield_COWCorr = 0
        for i in range(nominalData.numEntries()):
	  p = nominalData.get(i)
	  w = nominalData.weight()
	  f_COWCorr, f_NNLOPS = p.getRealValue("centralObjectWeight"), abs(p.getRealValue("NNLOPSweight"))
	  # If NNLOPS weight does not exist, set to 1
	  if not f_NNLOPS: f_NNLOPS = 1.
	  # Skip event with 0 centralObjectWeight
	  if f_COWCorr == 0: continue
	  else: _nominal_yield_COWCorr += w*(f_NNLOPS/f_COWCorr)

      # Add entry to dataframe
      if opt.skipCOWCorr: data.loc[len(data)] = [_mp,_proc,_cat,_granular_key,_nominal_yield]
      else: data.loc[len(data)] = [_mp,_proc,_cat,_granular_key,_nominal_yield,_nominal_yield_COWCorr]

    # Garbage removal
    inputWS.Delete()
    f.Close()

# Calculate eff x Acc for each mass point and store in json files
if not os.path.isdir("%s/outdir_%s"%(swd__,opt.ext)): os.system("mkdir %s/outdir_%s"%(swd__,opt.ext))
if not os.path.isdir("%s/outdir_%s/getEffAcc"%(swd__,opt.ext)): os.system("mkdir %s/outdir_%s/getEffAcc"%(swd__,opt.ext))
if not os.path.isdir("%s/outdir_%s/getEffAcc/json"%(swd__,opt.ext)): os.system("mkdir %s/outdir_%s/getEffAcc/json"%(swd__,opt.ext))
# Loop over mass points
for _mp in opt.massPoints.split(","):
  df = data[data['massPoint']==_mp]
  effAcc = {}
  for ir,r in df.iterrows():
    if r['cat'] == "NOTAG": continue
    if opt.skipCOWCorr: proc_yield = df[df['proc']==r['proc']].nominal_yield.sum()
    else: proc_yield = df[df['proc']==r['proc']].nominal_yield_COWCorr.sum()
    ea = r['nominal_yield']/proc_yield
    if ea < 0.: ea = 0.
    effAcc[r['granular_key']] = ea
  
  # Write to file
  if opt.skipCOWCorr: outfileName = "%s/outdir_%s/getEffAcc/json/effAcc_M%s_%s_skipCOWCorr.json"%(swd__,opt.ext,_mp,opt.ext)
  else: outfileName = "%s/outdir_%s/getEffAcc/json/effAcc_M%s_%s.json"%(swd__,opt.ext,_mp,opt.ext)
  with open(outfileName,'w') as jsonfile: json.dump(effAcc,jsonfile)

# Calculate fractional cross section of each STXS bin (in terms of stage0 bin) for normalisation: output in txt file
if opt.doSTXSFractions:
  if opt.skipCOWCorr:
    print " --> [ERROR] Must include centralObjectWeight corrections for signal normalisation fractions"
    leave()
  if not os.path.isdir("%s/outdir_%s/getEffAcc/fractions"%(swd__,opt.ext)): os.system("mkdir %s/outdir_%s/getEffAcc/fractions"%(swd__,opt.ext))

  # Loop over mass points
  for _mp in opt.massPoints.split(","):
    fout = open("%s/outdir_%s/getEffAcc/fractions/STXS_fractions_M%s.txt"%(swd__,opt.ext,_mp),"w")
    fout.write(" --> STXS fractions:\n") 
    for proc_s0 in ['GG2H','VBF','WH2HQQ','ZH2HQQ','QQ2HLNU','QQ2HLL',"GG2HQQ","GG2HLL","GG2HNUNU",'TTH','THQ','THW','BBH']:
      mask = (data.apply( lambda x: x['proc'].split("_")[0] == proc_s0, axis=1))&(data['massPoint']==_mp)
      proc_s0_yield = data[mask].nominal_yield_COWCorr.sum()
      if proc_s0_yield > 0:
	fout.write("\n * %s:\n"%proc_s0)
	for proc in data[mask].proc.unique():
	  mask = (data['proc']==proc)&(data['massPoint']==_mp)
	  proc_yield = data[mask].nominal_yield_COWCorr.sum()
	  fout.write("    * %s = %.4f\n"%(proc,proc_yield/proc_s0_yield))
    fout.close()      

