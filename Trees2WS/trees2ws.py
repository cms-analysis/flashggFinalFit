# Script to convert flashgg trees to RooWorkspace (compatible for finalFits)
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
  parser.add_option('--doNOTAG',dest='doNOTAG', default=False, action="store_true", help='Add NOTAG dataset to output WS')
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
from root_numpy import array2tree

from commonTools import *
from commonObjects import *
from tools.STXS_tools import *

print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG TREES 2 WS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
def leave():
  print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG TREES 2 WS (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
  sys.exit(1)

# Function to add vars to workspace
def add_vars_to_workspace(_ws=None,_data=None,_stxsVar=None):
  # Add intLumi var
  intLumi = ROOT.RooRealVar("intLumi","intLumi",1000.,0.,999999999.)
  intLumi.setConstant(True)
  getattr(_ws,'import')(intLumi)
  # Add vars specified by dataframe columns: skipping cat, stxsvar and type
  _vars = od()
  for var in _data.columns:
    if var in ['type','cat',_stxsVar]: continue
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
    notagVars        = _cfg['notagVars']
    systematicsVars  = _cfg['systematicsVars']
    theoryWeightContainers = _cfg['theoryWeightContainers']
    systematics      = _cfg['systematics']
    cats             = _cfg['cats']

  else:
    print "[ERROR] %s config file does not exist. Leaving..."%opt.inputConfig
    leave()
else:
  print "[ERROR] Please specify config file to run from. Leaving..."%opt.inputConfig
  leave()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# For theory weights: create vars for each weight
theoryWeightColumns = {}
for ts, nWeights in theoryWeightContainers.iteritems(): theoryWeightColumns[ts] = ["%s_%g"%(ts[:-1],i) for i in range(0,nWeights)] # drop final s from container name

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
    elif "NOTAG" in tn: continue
    elif "ERROR" in tn: continue
    c = tn.split("_%s_"%sqrts__)[-1].split(";")[0]
    cats.append(c)

if opt.doNOTAG:
  # Check if NOTAG tree exists
  for tn in listOfTreeNames:
    if "sigma" in tn: continue
    if "NOTAG" in tn: cats.append("NOTAG")
  if "NOTAG" not in cats:
    print " --> [WARNING] NOTAG tree does not exist in input file. Not including NOTAG"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 1) Convert tree to pandas dataframe
# Create dataframe to store all events in file
data = pandas.DataFrame()
if opt.doSystematics: sdata = pandas.DataFrame()

# Loop over categories: fill dataframe
for cat in cats:
  print " --> Extracting events from category: %s"%cat
  if inputTreeDir == '': treeName = "%s_%s_%s_%s"%(opt.productionMode,opt.inputMass,sqrts__,cat)
  else: treeName = "%s/%s_%s_%s_%s"%(inputTreeDir,opt.productionMode,opt.inputMass,sqrts__,cat)
  print "    * tree: %s"%treeName
  # Extract tree from uproot
  t = f[treeName]
  if len(t) == 0: continue
  
  # Convert tree to pandas dataframe
  dfs = {}

  # Theory weights
  for ts, tsColumns in theoryWeightColumns.iteritems():
    if opt.productionMode in modesToSkipTheoryWeights or 'ALT' in opt.productionMode: 
      dfs[ts] = pandas.DataFrame(np.ones(shape=(len(t),theoryWeightContainers[ts])))
    else:
      dfs[ts] = t.pandas.df(ts)
    dfs[ts].columns = tsColumns

  # Main variables to add to nominal RooDataSets
  dfs['main'] = t.pandas.df(mainVars) if cat!='NOTAG' else t.pandas.df(notagVars)

  # Concatenate current dataframes
  df = pandas.concat(dfs.values(), axis=1)

  # Add STXS splitting var if splitting necessary
  if opt.doSTXSSplitting: df[stxsVar] = t.pandas.df(stxsVar)

  # For NOTAG: fix extract centralObjectWeight from theory weights if available
  if cat == 'NOTAG':
    df['type'] = 'NOTAG'
    if opt.doNNLOPS:
      if opt.productionMode == 'ggh':
        if 'THU_ggH_VBF2jUp01sigma' in df:
          df['centralObjectWeight'] = df.apply(lambda x: 0.5*(x['THU_ggH_VBF2jUp01sigma']+x['THU_ggH_VBF2jDown01sigma']), axis=1)
          df['NNLOPSweight'] = df.apply(lambda x: 0.5*(x['THU_ggH_VBF2jUp01sigma']+x['THU_ggH_VBF2jDown01sigma']), axis=1)
        else:
          df['centralObjectWeight'] = 1.
          df['NNLOPSweight'] = 1.
      else:
        df['centralObjectWeight'] = 1.
        df['NNLOPSweight'] = 1.
    else:
      if "centralObjectWeight" in mainVars: df['centralObjectWeight'] = 1.

  # For experimental phase space (not NOTAG)
  else:
    df['type'] = 'nominal'
    # Add NNLOPS variable
    if(opt.doNNLOPS):
      if opt.productionMode == 'ggh': df['NNLOPSweight'] = t.pandas.df('NNLOPSweight')
      else: df['NNLOPSweight'] = 1.

  # Add columns specifying category add to overall dataframe
  df['cat'] = cat
  data = pandas.concat([data,df], ignore_index=True, axis=0, sort=False)


  # For systematics trees: only for events in experimental phase space
  if opt.doSystematics:
    if cat == "NOTAG": continue
    sdf = pandas.DataFrame()
    for s in systematics:
      print "    --> Systematic: %s"%re.sub("YEAR",opt.year,s)
      for direction in ['Up','Down']:
        streeName = "%s_%s%s01sigma"%(treeName,s,direction)
        # If year in streeName then replace by year being processed
        streeName = re.sub("YEAR",opt.year,streeName)
        st = f[streeName]
        if len(st)==0: continue
        sdf = st.pandas.df(systematicsVars)
        sdf['type'] = "%s%s"%(s,direction)
        # Add STXS splitting var if splitting necessary
        if opt.doSTXSSplitting: sdf[stxsVar] = st.pandas.df(stxsVar)
    
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
    print " --> Creating output workspace for STXS bin: %s (%s)"%(stxsBin,outputWSFile)
    
  else:
    df = data
    if opt.doSystematics: sdf = sdata

    # Define output workspace file
    outputWSDir = "/".join(opt.inputTreeFile.split("/")[:-1])+"/ws_%s"%dataToProc(opt.productionMode)
    if not os.path.exists(outputWSDir): os.system("mkdir %s"%outputWSDir)
    outputWSFile = outputWSDir+"/"+re.sub(".root","_%s.root"%dataToProc(opt.productionMode),opt.inputTreeFile.split("/")[-1])
    print " --> Creating output workspace: (%s)"%outputWSFile
    
  # Open file and initiate workspace
  fout = ROOT.TFile(outputWSFile,"RECREATE")
  foutdir = fout.mkdir(inputWSName__.split("/")[0])
  foutdir.cd()
  ws = ROOT.RooWorkspace(inputWSName__.split("/")[1],inputWSName__.split("/")[1])
  
  # Add variables to workspace
  varNames = add_vars_to_workspace(ws,df,stxsVar)

  # Loop over cats
  for cat in cats:

    # a) make RooDataSets: type = nominal/notag
    mask = (df['cat']==cat)
    # Convert dataframe to structured array, then to ROOT tree
    sa = df[mask].to_records()
    t = array2tree(sa)

    # Define RooDataSet
    dName = "%s_%s_%s_%s"%(opt.productionMode,opt.inputMass,sqrts__,cat)
    
    # Make argset
    aset = make_argset(ws,varNames)

    # Convert tree to RooDataset and add to workspace
    d = ROOT.RooDataSet(dName,dName,t,aset,'','weight')
    getattr(ws,'import')(d)

    # Delete trees and RooDataSet from heap
    t.Delete()
    d.Delete()
    del sa

    if opt.doSystematics:
      # b) make RooDataHists for systematic variations
      if cat == "NOTAG": continue
      for s in systematics:
        for direction in ['Up','Down']:
          # Create mask for systematic variation
          mask = (sdf['type']=='%s%s'%(s,direction))&(sdf['cat']==cat)
          # Convert dataframe to structured array, then to ROOT tree
          sa = sdf[mask].to_records()
          t = array2tree(sa)
          
          # Define RooDataHist
          hName = "%s_%s_%s_%s_%s%s01sigma"%(opt.productionMode,opt.inputMass,sqrts__,cat,s,direction)

          # Make argset 
          systematicsVarsDropWeight = []
          for var in systematicsVars:
            if var != "weight": systematicsVarsDropWeight.append(var)
          aset = make_argset(ws,systematicsVarsDropWeight)
          
          h = ROOT.RooDataHist(hName,hName,aset)
          for ev in t:
            for v in systematicsVars:
              if v == "weight": continue
              else: ws.var(v).setVal(getattr(ev,v))
            h.add(aset,getattr(ev,'weight'))
          
          # Add to workspace
          getattr(ws,'import')(h)

          # Delete trees and RooDataHist
          t.Delete()
          h.Delete()
          del sa

  # Write WS to file
  ws.Write()

  # Close file and delete workspace from heap
  fout.Close()
  ws.Delete()
  fout.Delete()
