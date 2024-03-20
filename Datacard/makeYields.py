# Script to calculate yields from input flashgg workspaces
#  * Uses Pandas dataframe to store all proc x cat yields
#  * Including systematic variations
#  * Output to be used for creating datacard

import os, sys
import re
from optparse import OptionParser
import ROOT
import pandas as pd
import glob
import pickle
import math
from collections import OrderedDict
from systematics import theory_systematics, experimental_systematics, signal_shape_systematics

from commonObjects import *
from commonTools import *

print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG DATACARD MAKER RUN II ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
def leave():
  print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG DATACARD MAKER RUN II (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
  exit(1)

def get_options():
  parser = OptionParser()
  parser.add_option('--inputWSDirMap', dest='inputWSDirMap', default='2016:/vols/cms/jl2117/hgg/ws/UL/Sept20/MC_final/signal_2016', help="Map. Format: year=inputWSDir (separate years by comma)")
  parser.add_option('--cat', dest='cat', default='', help='Analysis category')
  parser.add_option('--procs', dest='procs', default='auto', help='Comma separated list of signal processes. auto = automatically inferred from input workspaces')
  parser.add_option('--ext', dest='ext', default='', help='Extension for saving') 
  parser.add_option('--mass', dest='mass', default='125', help='Input workspace mass')
  parser.add_option('--mergeYears', dest='mergeYears', default=False, action="store_true", help="Merge category across years")
  parser.add_option('--skipBkg', dest='skipBkg', default=False, action="store_true", help="Only add signal processes to datacard")
  parser.add_option('--bkgScaler', dest='bkgScaler', default=1., type="float", help="Add overall scale factor for background")
  parser.add_option('--sigModelWSDir', dest='sigModelWSDir', default='./Models/signal', help='Input signal model WS directory') 
  parser.add_option('--sigModelExt', dest='sigModelExt', default='packaged', help='Extension used when saving signal model') 
  parser.add_option('--bkgModelWSDir', dest='bkgModelWSDir', default='./Models/background', help='Input background model WS directory') 
  parser.add_option('--bkgModelExt', dest='bkgModelExt', default='multipdf', help='Extension used when saving background model') 
  # For yields calculations:
  parser.add_option('--skipZeroes', dest='skipZeroes', default=False, action="store_true", help="Skip signal processes with 0 sum of weights")
  parser.add_option('--skipCOWCorr', dest='skipCOWCorr', default=False, action="store_true", help="Skip centralObjectWeight correction for events in acceptance. Use if no centralObjectWeight in workspace")
  # For systematics:
  parser.add_option('--doSystematics', dest='doSystematics', default=False, action="store_true", help="Include systematics calculations and add to datacard")
  parser.add_option('--ignore-warnings', dest='ignore_warnings', default=False, action="store_true", help="Skip errors for missing systematics. Instead output warning message")
  return parser.parse_args()
(opt,args) = get_options()

# Extract years and inputWSDir
inputWSDirMap = od()
for i in opt.inputWSDirMap.split(","): 
  print " --> Taking %s input workspaces from: %s"%(i.split("=")[0],i.split("=")[1]) 
  if not os.path.isdir( i.split("=")[1] ):
    print " --> [ERROR] Directory %s does not exist. Leaving..."%i.split("=")[1]
    leave()
  inputWSDirMap[i.split("=")[0]] = i.split("=")[1]
years = inputWSDirMap.keys()

procsMap = od()
if opt.procs == 'auto':
  for y,iWSDir in inputWSDirMap.iteritems():
    WSFileNames = extractWSFileNames(iWSDir)
    procsMap[y] = extractListOfProcs(WSFileNames)
  # Require common procs for each year
  for i,iy in enumerate(years):
    for j,jy in enumerate(years):
      if j > i:
	if set(procsMap[iy].split(",")) != set(procsMap[jy].split(",")):
	  print " --> [ERROR] Mis-match in list of process for %s and %s. Intersection = %s"%(iy,jy,(set(procsMap[jy]).symmetric_difference(set(procsMap[iy]))))
	  leave()
  # Define list of procs (alphabetically ordered)
  procs = procsMap[years[0]].split(",")
else: procs = opt.procs.split(",")
procs.sort()

# Initiate pandas dataframe
columns_data = ['year','type','procOriginal','proc','proc_s0','cat','inputWSFile','nominalDataName','modelWSFile','model','rate']
data = pd.DataFrame( columns=columns_data )

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# FILL DATAFRAME: all processes
print " .........................................................................................."

# Signal processes
for year in years:
  for proc in procs:

    # Identifier
    _id = "%s_%s_%s_%s"%(proc,year,opt.cat,sqrts__)

    # Mapping to STXS definition here
    _procOriginal = proc
    _proc = "%s_%s_%s"%(procToDatacardName(proc),year,decayMode)
    _proc_s0 = procToData(proc)

    # Define category: add year tag if not merging
    if opt.mergeYears: _cat = opt.cat
    else: _cat = "%s_%s"%(opt.cat,year)

    # Input flashgg ws 
    print "%s/*M%s*_%s.root"%(inputWSDirMap[year],opt.mass,proc)
    _inputWSFile = glob.glob("%s/*M%s*_%s.root"%(inputWSDirMap[year],opt.mass,proc))[0]
    _nominalDataName = "%s_%s_%s_%s"%(_proc_s0,opt.mass,sqrts__,opt.cat)

    # If opt.skipZeroes check nominal yield if 0 then do not add
    skipProc = False
    if opt.skipZeroes:
      f = ROOT.TFile(_inputWSFile)
      w = f.Get(inputWSName__)
      sumw = w.data(_nominalDataName).sumEntries()
      if sumw == 0.: skipProc = True
      w.Delete()
      f.Close()
    if skipProc: continue

    # Input model ws 
    if opt.cat == "NOTAG": _modelWSFile, _model = '-', '-'
    else:
      _modelWSFile = "%s/CMS-HGG_sigfit_%s_%s.root"%(opt.sigModelWSDir,opt.sigModelExt,_cat)
      _model = "%s_%s:%s_%s"%(outputWSName__,sqrts__,outputWSObjectTitle__,_id)

    # Extract rate from lumi
    _rate = float(lumiMap[year])*1000

    # Add signal process to dataFrame:
    print " --> Adding to dataFrame: (proc,cat) = (%s,%s)"%(_proc,_cat)
    data.loc[len(data)] = [year,'sig',_procOriginal,_proc,_proc_s0,_cat,_inputWSFile,_nominalDataName,_modelWSFile,_model,_rate]

# Background and data processes
if( not opt.skipBkg)&( opt.cat != "NOTAG" ):
  _proc_bkg = "bkg_mass"
  _proc_data = "data_obs"
  if opt.mergeYears:
    _cat = opt.cat
    _modelWSFile = "%s/CMS-HGG_%s_%s.root"%(opt.bkgModelWSDir,opt.bkgModelExt,_cat)
    _model_bkg = "%s:CMS_%s_%s_%s_bkgshape"%(bkgWSName__,decayMode,_cat,sqrts__)
    _model_data = "%s:roohist_data_mass_%s"%(bkgWSName__,_cat)
    _proc_s0 = '-' #not needed for data/bkg
    _inputWSFile = '-' #not needed for data/bkg
    _nominalDataName = '-' #not needed for data/bkg
    print " --> Adding to dataFrame: (proc,cat) = (%s,%s)"%(_proc_bkg,_cat)
    print " --> Adding to dataFrame: (proc,cat) = (%s,%s)"%(_proc_data,_cat)
    data.loc[len(data)] = ["merged",'bkg',_proc_bkg,_proc_bkg,'-',_cat,_inputWSFile,_nominalDataName,_modelWSFile,_model_bkg,opt.bkgScaler]
    data.loc[len(data)] = ["merged",'data',_proc_data,_proc_data,'-',_cat,_inputWSFile,_nominalDataName,_modelWSFile,_model_data,-1]

  # Category separate per year
  else:
    for year in years:
      _cat = "%s_%s"%(opt.cat,year)
      _catStripYear = opt.cat
      _modelWSFile = "%s/CMS-HGG_%s_%s.root"%(opt.bkgModelWSDir,opt.bkgModelExt,_cat)
      _model_bkg = "%s:CMS_%s_%s_%s_bkgshape"%(bkgWSName__,decayMode,_cat,sqrts__)
      _model_data = "%s:roohist_data_mass_%s"%(bkgWSName__,_catStripYear)
      _proc_s0 = '-' #not needed for data/bkg
      _inputWSFile = '-' #not needed for data/bkg
      _nominalDataName = '-' #not needed for data/bkg
      print " --> Adding to dataFrame: (proc,cat) = (%s,%s)"%(_proc_bkg,_cat)
      print " --> Adding to dataFrame: (proc,cat) = (%s,%s)"%(_proc_data,_cat)
      data.loc[len(data)] = ["year",'bkg',_proc_bkg,_proc_bkg,'-',_cat,_inputWSFile,_nominalDataName,_modelWSFile,_model_bkg,opt.bkgScaler]
      data.loc[len(data)] = ["year",'data',_proc_data,_proc_data,'-',_cat,_inputWSFile,_nominalDataName,_modelWSFile,_model_data,-1]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Yields: for each signal row in dataFrame extract the yield
print " .........................................................................................."
#   * if systematics=True: also extract reweighted yields for each uncertainty source
from tools.calcSystematics import factoryType, calcSystYields

# Create columns in dataFrame to store yields
data['nominal_yield'] = '-'
data['sumw2'] = '-'
if not opt.skipCOWCorr: data['nominal_yield_COWCorr'] = '-'

# Add columns in dataFrame for systematic yield variations
if opt.doSystematics:
  # Extract type of systematic using factoryType function (defined in tools.calcSystematics)
  #  * a_h: anti-symmetric RooDataHist (2 columns in dataframe)
  #  * a_w: anti-symmetric weight in nominal RooDataSet (2 columns in dataframe)
  #  * s_w: symmetric (single) weight in nominal RooDataSet (1 column in dataframe)
  experimentalFactoryType = {}
  theoryFactoryType = {}
  # No experimental systematics for NOTAG
  if opt.cat != "NOTAG":
    for s in experimental_systematics: 
      if s['type'] == 'factory': 
	# Fix for HEM as only in 2018 workspaces
	if s['name'] == 'JetHEM': experimentalFactoryType[s['name']] = "a_h"
	else: experimentalFactoryType[s['name']] = factoryType(data,s)
	if experimentalFactoryType[s['name']] in ["a_w","a_h"]:
	  data['%s_up_yield'%s['name']] = '-'
	  data['%s_down_yield'%s['name']] = '-'
	else: data['%s_yield'%s['name']] = '-'
  for s in theory_systematics: 
    if s['type'] == 'factory': 
      theoryFactoryType[s['name']] = factoryType(data,s)
      if theoryFactoryType[s['name']] in ["a_w","a_h"]:
	data['%s_up_yield'%s['name']] = '-'
	data['%s_down_yield'%s['name']] = '-'
	if not opt.skipCOWCorr:
	  data['%s_up_yield_COWCorr'%s['name']] = '-'
	  data['%s_down_yield_COWCorr'%s['name']] = '-'
      else: 
	data['%s_yield'%s['name']] = '-'
	if not opt.skipCOWCorr: data['%s_yield_COWCorr'%s['name']] = '-'

# Loop over signal rows in dataFrame: extract yields (nominal & systematic variations)
totalSignalRows = float(data[data['type']=='sig'].shape[0])
for ir,r in data[data['type']=='sig'].iterrows():

  print " --> Extracting yields: (%s,%s) [%.3f/%.3f = %.1f%%]"%(r['proc'],r['cat'],float(ir),totalSignalRows,100*(float(ir+1)/totalSignalRows))

  # Open input WS file and extract workspace
  f_in = ROOT.TFile(r.inputWSFile)
  inputWS = f_in.Get(inputWSName__)
  # Extract nominal RooDataSet and yield
  rdata_nominal = inputWS.data(r.nominalDataName)

  # Calculate nominal yield, sumw2 and add COW correction for in acceptance events
  contents = ""
  y, y_COWCorr = 0, 0
  sumw2 = 0
  for i in range(0,rdata_nominal.numEntries()):
    p = rdata_nominal.get(i)
    w = rdata_nominal.weight()
    y += w
    sumw2 += w*w
    # Extract contents from first event
    if i == 0: contents = p.contentsString()
    if not opt.skipCOWCorr:
      f_COWCorr = p.getRealValue("centralObjectWeight") if "centralObjectWeight" in contents else 1.
      f_NNLOPS = abs(p.getRealValue("NNLOPSweight")) if "NNLOPSweight" in contents else 1.
      if f_COWCorr == 0: continue
      else: y_COWCorr += w*(f_NNLOPS/f_COWCorr)
  data.at[ir,'nominal_yield'] = y
  data.at[ir,'sumw2'] = sumw2
  if not opt.skipCOWCorr: data.at[ir,'nominal_yield_COWCorr'] = y_COWCorr
  print "\t\t ==> nominal_yield = %f " % (y*_rate/1000.)

  # Systematics: loop over systematics and use function to extract yield variations
  if opt.doSystematics:

    # For experimental systematics: skip NOTAG events
    if "NOTAG" not in r['cat']:
      # Skip centralObjectWeight correction as concerns events in acceptance
      experimentalSystYields = calcSystYields(r['nominalDataName'],contents,inputWS,experimentalFactoryType,skipCOWCorr=True,proc=r['proc'],year=r['year'],ignoreWarnings=opt.ignore_warnings)
      for s,f in experimentalFactoryType.iteritems():
	if f in ['a_w','a_h']: 
	  for direction in ['up','down']: 
	    data.at[ir,"%s_%s_yield"%(s,direction)] = experimentalSystYields["%s_%s"%(s,direction)]
	else:
	  data.at[ir,"%s_yield"%s] = experimentalSystYields[s]

    # For theoretical systematics:
    theorySystYields = calcSystYields(r['nominalDataName'],contents,inputWS,theoryFactoryType,skipCOWCorr=opt.skipCOWCorr,proc=r['proc'],year=r['year'],ignoreWarnings=opt.ignore_warnings)
    for s,f in theoryFactoryType.iteritems():
      if f in ['a_w','a_h']: 
	for direction in ['up','down']: 
	  data.at[ir,"%s_%s_yield"%(s,direction)] = theorySystYields["%s_%s"%(s,direction)]
	  if not opt.skipCOWCorr: data.at[ir,"%s_%s_yield_COWCorr"%(s,direction)] = theorySystYields["%s_%s_COWCorr"%(s,direction)]
      else:
	data.at[ir,"%s_yield"%s] = theorySystYields[s]
	if not opt.skipCOWCorr: data.at[ir,"%s_yield_COWCorr"%s] = theorySystYields["%s_COWCorr"%s]

  # Remove the workspace and file from heap
  inputWS.Delete()
  f_in.Close()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SAVE YIELDS DATAFRAME
print " .........................................................................................."
extStr = "_%s"%opt.ext if opt.ext != '' else ''
print " --> Saving yields dataframe: ./yields%s/%s.pkl"%(extStr,opt.cat)
if not os.path.isdir("./yields%s"%extStr): os.system("mkdir ./yields%s"%extStr)
with open("./yields%s/%s.pkl"%(extStr,opt.cat),"wb") as fD: pickle.dump(data,fD)
