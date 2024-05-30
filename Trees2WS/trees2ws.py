# Script to convert HiggsDNA TTrees to RooWorkspace (compatible for finalFits)
# Assumes tree names of the format: 
#  * <productionMode>_<MH>_<sqrts>_<category> e.g. ggh_125_13TeV_RECO_0J_PTH_0_10_Tag0
# For systematics: requires trees of the format:
#  * <productionMode>_<MH>_<sqrts>_<category>_<syst>Up01sigma e.g. ggh_125_13TeV_RECO_0J_PTH_0_10_Tag0_JECUp01sigma
#  * <productionMode>_<MH>_<sqrts>_<category>_<syst>Down01sigma e.g. ggh_125_13TeV_RECO_0J_PTH_0_10_Tag0_JECDown01sigma

import os, sys
import re
from optparse import OptionParser

def get_options():
  parser = OptionParser()
  parser.add_option('--inputConfig',dest='inputConfig', default="", help='Input config: specify list of variables/systematics/analysis categories')
  parser.add_option('--inputTreeFile',dest='inputTreeFile', default="./output_0.root", help='Input tree file')
  parser.add_option('--inputMass',dest='inputMass', default="125", help='Input mass')
  parser.add_option('--productionMode',dest='productionMode', default="ggh", help='Production mode [ggh,vbf,wh,zh,tth,thq,ggzh,bbh]')
  parser.add_option('--year',dest='year', default="2016", help='Year')
  parser.add_option('--decayExt',dest='decayExt', default='', help='Decay extension')
  parser.add_option('--doNNLOPS',dest='doNNLOPS', default=False, action="store_true", help='Add NNLOPS weight variable: NNLOPSweight')
  parser.add_option('--doSystematics',dest='doSystematics', default=False, action="store_true", help='Add systematics datasets to output WS')
  parser.add_option('--doSTXSSplitting',dest='doSTXSSplitting', default=False, action="store_true", help='Split output WS per STXS bin')
  return parser.parse_args()
(opt,args) = get_options()

from collections import OrderedDict as od
from importlib import import_module

import ROOT
import pandas
import numpy as np
import uproot
import awkward as ak

from commonTools import *
from commonObjects import *
from tools.STXS_tools import *

print(" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG TREES 2 WS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ")
def leave():
  print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG TREES 2 WS (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
  exit(0)

# Function to add vars to workspace
def add_vars_to_workspace(_ws=None,_data=None,_stxsVar=None):
  # Add intLumi var
  intLumi = ROOT.RooRealVar("intLumi","intLumi",1000.,0.,999999999.)
  intLumi.setConstant(True)
  getattr(_ws,'import')(intLumi)
  # Add vars specified by dataframe columns: skipping cat, stxsvar and type
  _vars = od()
  for var in _data.columns:
    if var in ['type','cat',_stxsVar,'']: continue
    if var == "CMS_hgg_mass": 
      _vars[var] = ROOT.RooRealVar(var,var,125.,100.,180.)
      _vars[var].setBins(160)
    elif var == "dZ": 
      _vars[var] = ROOT.RooRealVar(var,var,0.,-20.,20.)
      _vars[var].setBins(40)
    elif var == "weight": 
      _vars[var] = ROOT.RooRealVar(var,var,0.)
    else:
      _vars[var] = ROOT.RooRealVar(var,var,1.,-999999,999999)
      _vars[var].setBins(1)
    getattr(_ws,'import')(_vars[var],ROOT.RooFit.Silence())
  return _vars.keys()

# Function to make RooArgSet
def make_argset(_ws=None,_varNames=None):
  _aset = ROOT.RooArgSet()
  for v in _varNames: _aset.add(_ws.var(v))
  return _aset

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Production modes to skip theory weights: fill with 1's
modesToSkipTheoryWeights = ['bbh','thq','thw']

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Extract options from config file:
options = od()
if opt.inputConfig != '':
  if os.path.exists( opt.inputConfig ):

    # Import config options
    _cfg = import_module(re.sub(".py","",opt.inputConfig)).trees2wsCfg

    #Extract options
    inputTreeDir     = _cfg['inputTreeDir']
    mainVars         = _cfg['mainVars']
    stxsVar          = _cfg['stxsVar']
    systematicsVars  = _cfg['systematicsVars']
    theoryWeightContainers = _cfg['theoryWeightContainers']
    systematics      = _cfg['systematics']
    cats             = _cfg['cats']

  else:
    print( "[ERROR] %s config file does not exist. Leaving..."%opt.inputConfig)
    leave()
else:
  print( "[ERROR] Please specify config file to run from. Leaving..."%opt.inputConfig)
  leave()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# For theory weights: create vars for each weight
theoryWeightColumns = {}
for ts, nWeights in theoryWeightContainers.items(): theoryWeightColumns[ts] = ["%s_%g"%(ts[:-1],i) for i in range(0,nWeights)] # drop final s from container name

# If year == 2018, add HET
if opt.year == '2018': systematics.append("JetHEM")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# UPROOT file
f = uproot.open(opt.inputTreeFile)
if inputTreeDir == '': listOfTreeNames == f.keys()
else: listOfTreeNames = f[inputTreeDir].keys()
# If cats = 'auto' then determine from list of trees
if cats == 'auto':
  cats = []
  for tn in listOfTreeNames:
    if "sigma" in tn: continue
    c = tn.split("_%s_"%sqrts__)[-1].split(";")[0]
    cats.append(c)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 1) Convert tree to pandas dataframe
# Create dataframe to store all events in file
data = pandas.DataFrame()
if opt.doSystematics: sdata = pandas.DataFrame()

# Loop over categories: fill dataframe
for cat in cats:
  print( " --> Extracting events from category: %s"%cat)
  if inputTreeDir == '': treeName = "%s_%s_%s_%s"%(opt.productionMode,opt.inputMass,sqrts__,cat)
  else: treeName = "%s/%s_%s_%s_%s"%(inputTreeDir,opt.productionMode,opt.inputMass,sqrts__,cat)
  print("    * tree: %s"%treeName)
  # Extract tree from uproot
  t = f[treeName]
  if len(t) == 0: continue
  
  # Convert tree to pandas dataframe
  dfs = {}

  # Theory weights
  for ts, tsColumns in theoryWeightColumns.items():
    if opt.productionMode in modesToSkipTheoryWeights: 
      dfs[ts] = pandas.DataFrame(np.ones(shape=(len(t),theoryWeightContainers[ts])))
    else:
      dfs[ts] = pandas.DataFrame(np.reshape(np.array(t[ts].array()),(len(t),len(tsColumns))))
    dfs[ts].columns = tsColumns

  # Main variables to add to nominal RooDataSets
  # For wildcards use filter_name functionality
  mainVars_dropWildcards = []
  for var in mainVars:
    if "*" not in var:
      mainVars_dropWildcards.append(var)
      
  dfs['main'] = t.arrays(mainVars_dropWildcards, library='pd')

  for var in mainVars:
    if "*" in var:
      dfs[var] = t.arrays(filter_name=var, library='pd')

  # Concatenate current dataframes
  df = pandas.concat(dfs.values(), axis=1)

  # Add STXS splitting var if splitting necessary
  if opt.doSTXSSplitting: df[stxsVar] = t.arrays(stxsVar, library='pd')

  # For experimental phase space
  df['type'] = 'nominal'
  # Add NNLOPS variable
  if(opt.doNNLOPS):
    if opt.productionMode == 'ggh': df['NNLOPSweight'] = t.arrays(['NNLOPSweight'], library='pd')
    else: df['NNLOPSweight'] = 1.

  # Add columns specifying category add to overall dataframe
  df['cat'] = cat
  data = pandas.concat([data,df], ignore_index=True, axis=0, sort=False)

  # For systematics trees: only for events in experimental phase space
  if opt.doSystematics:
    sdf = pandas.DataFrame()
    for s in systematics:
      print("    --> Systematic: %s"%re.sub("YEAR",opt.year,s))
      for direction in ['Up','Down']:
        streeName = "%s_%s%s01sigma"%(treeName,s,direction)
        # If year in streeName then replace by year being processed
        streeName = re.sub("YEAR",opt.year,streeName)
        st = f[streeName]
        if len(st)==0: continue
        sdf = st.arrays(systematicsVars, library='pd')
        sdf['type'] = "%s%s"%(s,direction)
        # Add STXS splitting var if splitting necessary
        if opt.doSTXSSplitting: sdf[stxsVar] = st.arrays(stxsVar, library='pd')
    
        # Add column specifying category and add to systematics dataframe
        sdf['cat'] = cat
        sdata = pandas.concat([sdata,sdf], ignore_index=True, axis=0, sort=False)
     
# If not splitting by STXS bin then add dummy column to dataframe
if not opt.doSTXSSplitting:
  data[stxsVar] = 'nosplit'  
  if opt.doSystematics: sdata[stxsVar] = 'nosplit'

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 2) Convert pandas dataframe to RooWorkspace
for stxsId in data[stxsVar].unique():

  # Split output files for different STXS bins
  if opt.doSTXSSplitting:
    df = data[data[stxsVar]==stxsId]
    if opt.doSystematics: sdf = sdata[sdata[stxsVar]==stxsId]

    # Extract stxsBin
    stxsBin = flashggSTXSDict[int(stxsId)]
    if opt.productionMode == "wh": 
      if "QQ2HQQ" in stxsBin: stxsBin = re.sub("QQ2HQQ","WH2HQQ",stxsBin)
    elif opt.productionMode == "zh": 
      if "QQ2HQQ" in stxsBin: stxsBin = re.sub("QQ2HQQ","ZH2HQQ",stxsBin)
    # ggZH: split by decay mode
    elif opt.productionMode == "ggzh":
      if opt.decayExt == "_ZToQQ": stxsBin = re.sub("GG2H","GG2HQQ",stxsBin)
      elif opt.decayExt == "_ZToNuNu": stxsBin = re.sub("GG2HLL","GG2HNUNU",stxsBin)
    # For tHL split into separate bins for tHq and tHW
    elif opt.productionMode == "thq": stxsBin = re.sub("TH","THQ",stxsBin)
    elif opt.productionMode == 'thw': stxsBin = re.sub("TH","THW",stxsBin)

    # Define output workspace file
    outputWSDir = "/".join(opt.inputTreeFile.split("/")[:-1])+"/ws_%s"%stxsBin
    if not os.path.exists(outputWSDir): os.system("mkdir %s"%outputWSDir)
    outputWSFile = outputWSDir+"/"+re.sub(".root","_%s.root"%stxsBin,opt.inputTreeFile.split("/")[-1])
    print(" --> Creating output workspace for STXS bin: %s (%s)"%(stxsBin,outputWSFile))
    
  else:
    df = data
    if opt.doSystematics: sdf = sdata

    # Define output workspace file
    outputWSDir = "/".join(opt.inputTreeFile.split("/")[:-1])+"/ws_%s"%dataToProc(opt.productionMode)
    if not os.path.exists(outputWSDir): os.system("mkdir %s"%outputWSDir)
    outputWSFile = outputWSDir+"/"+re.sub(".root","_%s.root"%dataToProc(opt.productionMode),opt.inputTreeFile.split("/")[-1])
    print(" --> Creating output workspace: (%s)"%outputWSFile)
    
  # Open file and initiate workspace
  fout = ROOT.TFile(outputWSFile,"RECREATE")
  foutdir = fout.mkdir(inputWSName__.split("/")[0])
  foutdir.cd()
  ws = ROOT.RooWorkspace(inputWSName__.split("/")[1],inputWSName__.split("/")[1])
  
  # Add variables to workspace
  varNames = add_vars_to_workspace(ws,df,stxsVar)

  # Loop over cats
  for cat in cats:

    # a) make RooDataSets: type = nominal
    mask = (df['cat']==cat)

    # Make argset
    aset = make_argset(ws,varNames)

    # Define RooDataSet
    dName = "%s_%s_%s_%s"%(opt.productionMode,opt.inputMass,sqrts__,cat)
    d = ROOT.RooDataSet(dName,dName,aset,'weight') 

    # Loop over events in dataframe and add entry
    for row in df[mask][varNames].to_numpy():
      for i, val in enumerate(row):
        aset[i].setVal(val)
      d.add(aset,aset.getRealValue("weight"))

    # Add to workspace
    getattr(ws,'import')(d)

    if opt.doSystematics:
      # b) make RooDataHists for systematic variations
      for s in systematics:
        for direction in ['Up','Down']:
          # Create mask for systematic variation
          mask = (sdf['type']=='%s%s'%(s,direction))&(sdf['cat']==cat)
          
          # Define RooDataHist
          hName = "%s_%s_%s_%s_%s%s01sigma"%(opt.productionMode,opt.inputMass,sqrts__,cat,s,direction)

          # Make argset: drop weight column for histogrammed observables
          systematicsVarsDropWeight = []
          for var in systematicsVars:
            if var != "weight": systematicsVarsDropWeight.append(var)
          aset = make_argset(ws,systematicsVarsDropWeight)
          
          h = ROOT.RooDataHist(hName,hName,aset)
          for row, weight in zip(sdf[mask][systematicsVarsDropWeight].to_numpy(),sdf[mask]["weight"].to_numpy()):
            for i, val in enumerate(row):
              aset[i].setVal(val)
            h.add(aset,weight)
          
          # Add to workspace
          getattr(ws,'import')(h)

  # Write WS to file
  ws.Write()

  # Close file and delete workspace from heap
  fout.Close()
