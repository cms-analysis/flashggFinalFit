# Script to calculate yields from input parquets
import os, sys
import re
from optparse import OptionParser
import glob
import pickle
import math

import ROOT
import pandas as pd
import pyarrow.parquet as pq

from collections import OrderedDict
from systematics import theory_systematics, experimental_systematics, signal_shape_systematics

from commonObjects import *
from commonTools import *

print(" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG DATACARD MAKER RUN II ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ")
def leave():
  print(" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG DATACARD MAKER RUN II (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ")
  exit(0)

def get_options():
  parser = OptionParser()
  parser.add_option('--inputParquetDirMap', dest='inputParquetDirMap', default='2016:/vols/cms/jl2117/hgg/ws/UL/Sept20/MC_final/signal_2016', help="Map. Format: year=inputParquetDir (separate years by comma)")
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
  # For systematics:
  parser.add_option('--doSystematics', dest='doSystematics', default=False, action="store_true", help="Include systematics calculations and add to datacard")
  parser.add_option('--ignore-warnings', dest='ignore_warnings', default=False, action="store_true", help="Skip errors for missing systematics. Instead output warning message")
  return parser.parse_args()
(opt,args) = get_options()

# Extract years and inputWSDir
inputParquetDirMap = od()
for i in opt.inputParquetDirMap.split(","): 
  print(" --> Taking %s input parquets from: %s"%(i.split("=")[0],i.split("=")[1]) )

  if not os.path.isdir( i.split("=")[1] ):
    print(" --> [ERROR] Directory %s does not exist. Leaving..."%i.split("=")[1])
    leave()

  inputParquetDirMap[i.split("=")[0]] = i.split("=")[1]

years = list(inputParquetDirMap.keys())

procsMap = od()
if opt.procs == 'auto':
  for y, iParquetDir in inputParquetDirMap.items():
    file_names = extractParquetFileNames(iParquetDir)
    procsMap[y] = extractListOfProcs(file_names, mode="parquet").split(",")


# Initiate pandas dataframe
columns_data = ['year','type','proc','proc_s0','cat','inputFile','modelWSFile','model','rate']
data = pd.DataFrame( columns=columns_data )

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# FILL DATAFRAME: all processes
print(" ..........................................................................................")

# Signal processes
for year in years:
  for proc in procsMap[year]:

    # Identifier
    _id = "%s_%s_%s_%s"%(proc,year,opt.cat,sqrts__)

    # Mapping to STXS definition here
    _proc = proc 
    _proc_s0 = proc.split("_")[0]

    # Define category: add year tag if not merging
    if opt.mergeYears: _cat = opt.cat
    else: _cat = "%s_%s"%(opt.cat,year)

    # Input flashgg ws 
    _inputFile = "%s/events__%s.parquet"%(inputParquetDirMap[year],proc)

    # If opt.skipZeroes check nominal yield if 0 then do not add
    f = pq.ParquetFile(_inputFile).read()
    df = f.to_pandas()

    mask_cat = (df['category'] == opt.cat)
    if df[mask_cat]['weight'].sum() == 0:
        continue

    _modelWSFile = "%s/CMS-HGG_sigfit_%s_%s.root"%(opt.sigModelWSDir,opt.sigModelExt,_cat)
    _model = "%s_%s:%s_%s"%(outputWSName__,sqrts__,outputWSObjectTitle__,_id)

    # Extract rate from lumi
    _rate = float(lumiMap[year])*1000

    # Add signal process to dataFrame:
    print(" --> Adding to dataFrame: (proc,cat) = (%s,%s)"%(_proc,_cat))
    data.loc[len(data)] = [year,'sig',_proc,_proc_s0,_cat,_inputFile,_modelWSFile,_model,_rate]


# Background and data processes
_proc_bkg = "bkg_mass"
_proc_data = "data_obs"
if opt.mergeYears:
  _cat = opt.cat
  _modelWSFile = "%s/CMS-HGG_%s_%s.root"%(opt.bkgModelWSDir,opt.bkgModelExt,_cat)
  _model_bkg = "%s:CMS_%s_%s_%s_bkgshape"%(bkgWSName__,decayMode,_cat,sqrts__)
  _model_data = "%s:roohist_data_mass_%s"%(bkgWSName__,_cat)
  _proc_s0 = '-' #not needed for data/bkg
  _inputFile = '-' #not needed for data/bkg
  print(" --> Adding to dataFrame: (proc,cat) = (%s,%s)"%(_proc_bkg,_cat))
  print(" --> Adding to dataFrame: (proc,cat) = (%s,%s)"%(_proc_data,_cat))
  data.loc[len(data)] = ["merged",'bkg',_proc_bkg,_proc_s0,_cat,_inputFile,_modelWSFile,_model_bkg,opt.bkgScaler]
  data.loc[len(data)] = ["merged",'data',_proc_data,_proc_s0,_cat,_inputFile,_modelWSFile,_model_data,-1]

# Category separate per year
else:
  for year in years:
    _cat = "%s_%s"%(opt.cat,year)
    _catStripYear = opt.cat
    _modelWSFile = "%s/CMS-HGG_%s_%s.root"%(opt.bkgModelWSDir,opt.bkgModelExt,_cat)
    _model_bkg = "%s:CMS_%s_%s_%s_bkgshape"%(bkgWSName__,decayMode,_cat,sqrts__)
    _model_data = "%s:roohist_data_mass_%s"%(bkgWSName__,_catStripYear)
    _proc_s0 = '-' #not needed for data/bkg
    _inputFile = '-' #not needed for data/bkg
    print(" --> Adding to dataFrame: (proc,cat) = (%s,%s)"%(_proc_bkg,_cat))
    print(" --> Adding to dataFrame: (proc,cat) = (%s,%s)"%(_proc_data,_cat))
    data.loc[len(data)] = ["year",'bkg',_proc_bkg,_proc_s0,_cat,_inputFile,_modelWSFile,_model_bkg,opt.bkgScaler]
    data.loc[len(data)] = ["year",'data',_proc_data,_proc_s0,_cat,_inputFile,_modelWSFile,_model_data,-1]



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Yields: for each signal row in dataFrame extract the yield
print(" ..........................................................................................")
#   * if systematics=True: also extract reweighted yields for each uncertainty source
from tools.calcSystematics import factoryType, calcSystYields

# Create columns in dataFrame to store yields
data['nominal_yield'] = '-'
data['sumw2'] = '-'

# Add columns in dataFrame for systematic yield variations
if opt.doSystematics:
  # Extract type of systematic using factoryType function (defined in tools.calcSystematics)
  #  * a_h: anti-symmetric RooDataHist (2 columns in dataframe)
  #  * a_w: anti-symmetric weight in nominal RooDataSet (2 columns in dataframe)
  #  * s_w: symmetric (single) weight in nominal RooDataSet (1 column in dataframe)
  experimentalFactoryType = {}
  theoryFactoryType = {}

  # Experimental systematics
  for s in experimental_systematics: 
    if s['type'] == 'factory': 
      experimentalFactoryType[s['name']] = factoryType(data,s)
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
      else: 
        data['%s_yield'%s['name']] = '-'

# Loop over signal rows in dataFrame: extract yields (nominal & systematic variations)
totalSignalRows = float(data[data['type']=='sig'].shape[0])
for ir,r in data[data['type']=='sig'].iterrows():

  print(" --> Extracting yields: (%s,%s) [%.1f%%]"%(r['proc'],r['cat'],100*(float(ir)/totalSignalRows)))

  # Open parquet file and extract events
  f = pq.ParquetFile(r['inputFile']).read()
  df = f.to_pandas()
  mask_cat = (df['category'] == r['cat'])
  df_subset = df[mask_cat]

  # Calculate nominal yield
  y = df_subset['weight'].sum()
  sumw2 = (df_subset['weight']**2).sum()
  data.at[ir,'nominal_yield'] = y
  data.at[ir,'sumw2'] = sumw2

  # Systematics: loop over systematics and use function to extract yield variations
  if opt.doSystematics:

    # For experimental systematics
    experimentalSystYields = calcSystYields(r['inputFile'], experimentalFactoryType, proc=r['proc'], year=r['year'], cat=r['cat'], ignoreWarnings=opt.ignore_warnings)

    for s,f in experimentalFactoryType.items():
      if f in ['a_w','a_h']: 
        for direction in ['up','down']: 
          data.at[ir,"%s_%s_yield"%(s,direction)] = experimentalSystYields["%s_%s"%(s,direction)]
      else:
        data.at[ir,"%s_yield"%s] = experimentalSystYields[s]

    # For theoretical systematics:
    theorySystYields = calcSystYields(r['inputFile'], theoryFactoryType, proc=r['proc'], year=r['year'], cat=r['cat'], ignoreWarnings=opt.ignore_warnings)

    for s,f in theoryFactoryType.items():
      if f in ['a_w','a_h']: 
        for direction in ['up','down']: 
          data.at[ir,"%s_%s_yield"%(s,direction)] = theorySystYields["%s_%s"%(s,direction)]
      else:
        data.at[ir,"%s_yield"%s] = theorySystYields[s]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SAVE YIELDS DATAFRAME
print(" ..........................................................................................")
extStr = "_%s"%opt.ext if opt.ext != '' else ''
print(" --> Saving yields dataframe: ./yields%s/%s.pkl"%(extStr,opt.cat))
if not os.path.isdir("./yields%s"%extStr): os.system("mkdir ./yields%s"%extStr)
with open("./yields%s/%s.pkl"%(extStr,opt.cat),"wb") as fD: pickle.dump(data,fD)
