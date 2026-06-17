# Datacard making script: uses output pkl file of makeYields.py script

print(" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG DATACARD MAKER RUN II ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ")
import os, sys
import re
from optparse import OptionParser
import ROOT
import pandas as pd
import glob
import pickle
from collections import OrderedDict as od
from systematics import theory_systematics, experimental_systematics, signal_shape_systematics

def get_options():
  parser = OptionParser()
  parser.add_option('--ext', dest='ext', default='', help="Extension (used when running RunYields.py)")
  parser.add_option('--years', dest='years', default='2022preEE,2022postEE', help="Comma separated list of years in makeYields output")
  # For pruning processes
  parser.add_option('--prune', dest='prune', default=False, action="store_true", help="Prune proc x cat which make up less than pruneThreshold (default 0.1%) of given total category")
  parser.add_option('--pruneThreshold', dest='pruneThreshold', default=0.001, type='float', help="Threshold with which to prune proc x cat as fraction of total category yield (default=0.1%)")
  parser.add_option('--mass', dest='mass', default='125', help="MH mass: required for doTrueYield")
  parser.add_option('--analysis', dest='analysis', default='HIG-25-020', help="Analysis extension: required for doTrueYield (see ./tools/XSBR.py for example)")
  # For yield/systematics:
  parser.add_option('--doSystematics', dest='doSystematics', default=False, action="store_true", help="Include systematics calculations and add to datacard")
  parser.add_option('--doMCStatUncertainty', dest='doMCStatUncertainty', default=False, action="store_true", help="Add uncertainty for MC stats")
  # For output
  parser.add_option('--saveDataFrame', dest='saveDataFrame', default=False, action="store_true", help='Save final dataframe as pkl file') 
  parser.add_option('--output', dest='output', default='Datacard', help='Datacard name') 
  return parser.parse_args()
(opt,args) = get_options()

def leave():
  print(" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG DATACARD MAKER RUN II (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ")
  exit(0)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Concatenate dataframes
print(" --> Loading per category dataframes into single dataframe")
extStr = "_%s"%opt.ext if opt.ext != '' else ''
pkl_files = glob.glob("./yields%s/*.pkl"%extStr)
pkl_files.sort() # Categories in alphabetical order
data = pd.DataFrame()
for f_pkl_name in pkl_files:
  with open(f_pkl_name,"rb") as f_pkl: 
    df = pickle.load(f_pkl)
    data = pd.concat([data,df], ignore_index=True, axis=0, sort=False)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Systematics: use factory function to calculate yield variations
if opt.doSystematics:
  from tools.calcSystematics import factoryType, addConstantSyst, experimentalSystFactory, theorySystFactory, groupSystematics, envelopeSystematics, renameSyst

  print(" ..........................................................................................")

  # Extract factory types of systematics
  print(" --> Extracting factory types for systematics")
  experimentalFactoryType = {}
  theoryFactoryType = {}

  for s in experimental_systematics:
    if s['type'] == 'factory':
      experimentalFactoryType[s['name']] = factoryType(data,s)

  for s in theory_systematics: 
    if s['type'] == 'factory': 
      theoryFactoryType[s['name']] = factoryType(data,s)
  
  # Experimental:
  print(" --> Adding experimental systematics variations to dataFrame")
  # Add constant systematics to dataFrame
  for s in experimental_systematics:
    if s['type'] == 'constant': data = addConstantSyst(data,s,opt)
  data = experimentalSystFactory(data, experimental_systematics, experimentalFactoryType, opt )

  # Theory:
  print(" --> Adding theory systematics variations to dataFrame")
  # Add constant systematics to dataFrame
  for s in theory_systematics:
    if s['type'] == 'constant': data = addConstantSyst(data,s,opt)
  # Theory factory: group scale weights after calculation in relevant grouping scheme
  data = theorySystFactory(data, theory_systematics, theoryFactoryType, opt)

  # Rename systematics
  #for s in theory_systematics: s['title'] = renameSyst(s['title'],"scaleWeight","scale")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Pruning: if process contributes less than 0.1% of yield in analysis category then ignore
if opt.prune:
  print(" ..........................................................................................")
  print(" --> Pruning processes which contribute < %.2f%% of RECO category yield"%(100*opt.pruneThreshold))
  data['prune'] = 0

  print(" --> Using the true yield of process for pruning: N = Product(XS,BR,eff*acc,lumi)")
  mask = (data['type']=='sig')

  # Extract XS*BR using tools.XSBR
  data['xsbr'] = '-'
    
  from tools.XSBR import *
  XSBR = extractXSBR(data,mass=opt.mass,analysis=opt.analysis)
  data.loc[mask,'xsbr'] = data[mask].apply(lambda x: XSBR["XS_%s"%x['proc']]*XSBR['BR'], axis=1)

  # Extract eff*acc using total proc yield: strictly should include NOTAG
  data['ea'] = '-'
  # In HiggsDNA the sumw = eff*acc
  data.loc[mask,'ea'] = data.loc[mask,'nominal_yield']

  # Calculate true yield
  data.loc[mask,'true_yield'] = data[mask].apply(lambda x: x['xsbr']*x['ea']*x['rate'], axis=1)

  # Extract per category tue yields
  catTrueYields = od()
  for cat in data.cat.unique(): catTrueYields[cat] = data[(data['cat']==cat)&(data['type']=='sig')].true_yield.sum()

  # Set prune = 1 if < threshold of total cat yield
  mask = (data['true_yield']<opt.pruneThreshold*data.apply(lambda x: catTrueYields[x['cat']], axis=1))&(data['type']=='sig')
  data.loc[mask,'prune'] = 1

    
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SAVE DATAFRAME
if opt.saveDataFrame:
  print(" ..........................................................................................")
  print(" --> Saving dataFrame: %s.pkl"%opt.output)
  with open("%s.pkl"%opt.output,"wb") as fD: pickle.dump(data,fD)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Adapt proc names to include era
mask_sig = data['type'] == 'sig'
data.loc[mask_sig, "proc"] = (
    data.loc[mask_sig, "proc"].astype(str)
    + "__"
    + data.loc[mask_sig, "year"].astype(str)
    + "__13p6TeV__hgg"
)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# WRITE TO .TXT FILE
print(" ..........................................................................................")
fdataName = "%s.txt"%opt.output
print(" --> Writing to datacard file: %s"%fdataName)
from tools.writeToDatacard import writePreamble, writeProcesses, writeSystematic, writeMCStatUncertainty, writePdfIndex, writeBreak
fdata = open(fdataName,"w")
if not writePreamble(fdata,opt): 
  print(" --> [ERROR] in writing preamble. Leaving...")
  leave()
if not writeProcesses(fdata,data,opt):
  print(" --> [ERROR] in writing processes. Leaving...")
  leave()
if opt.doSystematics:
  for syst in experimental_systematics:
    if not writeSystematic(fdata,data,syst,opt):
      print(" --> [ERROR] in writing systematic %s (experiment). Leaving"%syst['name'])
      leave()
  writeBreak(fdata)
  for syst in theory_systematics:
    if not writeSystematic(fdata,data,syst,opt):
      print(" --> [ERROR] in writing systematic %s (theory). Leaving"%syst['name'])
      leave()
  writeBreak(fdata)
  for syst in signal_shape_systematics:
    if not writeSystematic(fdata,data,syst,opt):
      print(" --> [ERROR] in writing systematic %s (signal shape). Leaving"%syst['name'])
      leave()
if opt.doMCStatUncertainty:
  writeBreak(fdata)
  if not writeMCStatUncertainty(fdata,data,opt):
    print(" --> [ERROR] in writing MC stat uncertainty systematic. Leaving")
    leave()
writeBreak(fdata)
if not writePdfIndex(fdata,data,opt):
  print(" --> [ERROR] in writing pdf indices. Leaving...")
  leave()
fdata.close()

leave()
