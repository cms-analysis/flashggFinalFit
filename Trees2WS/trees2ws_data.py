# Script to convert data trees to RooWorkspace (compatible for finalFits)
# Assumes tree names of the format:
# * Data_<sqrts>_category

import os, sys
import re
from optparse import OptionParser

def get_options():
  parser = OptionParser()
  parser.add_option('--inputConfig',dest='inputConfig', default="", help='Input config: specify list of variables/analysis categories')
  parser.add_option('--inputTreeFile',dest='inputTreeFile', default=None, help='Input tree file')
  parser.add_option('--outputWSDir',dest='outputWSDir', default=None, help='Output dir (default is same as input dir)')
  return parser.parse_args()
(opt,args) = get_options()

from collections import OrderedDict as od
from importlib import import_module

import ROOT
import uproot
from root_numpy import array2tree
from collections import OrderedDict as od

from commonTools import *
from commonObjects import *


print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG TREES 2 WS (DATA) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
def leave():
  print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG TREES 2 WS (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
  sys.exit(1)

# Function to add vars to workspace
def add_vars_to_workspace(_ws=None,_dataVars=None):
  # Add intLumi var
  intLumi = ROOT.RooRealVar("intLumi","intLumi",1000.,0.,999999999.)
  intLumi.setConstant(True)
  getattr(_ws,'import')(intLumi)
  _vars = od()
  for var in _dataVars:
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
# Extract options from config file:
options = od()
if opt.inputConfig != '':
  if os.path.exists( opt.inputConfig ):

    # Import config options
    _cfg = import_module(re.sub(".py","",opt.inputConfig)).trees2wsCfg

    #Extract options
    inputTreeDir     = _cfg['inputTreeDir']
    dataVars         = _cfg['dataVars']
    cats             = _cfg['cats']

  else:
    print "[ERROR] %s config file does not exist. Leaving..."%opt.inputConfig
    leave()
else:
  print "[ERROR] Please specify config file to run from. Leaving..."%opt.inputConfig
  leave()

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

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Open input ROOT file
f = ROOT.TFile(opt.inputTreeFile)

# Open output ROOT file and initiate workspace to store RooDataSets
if opt.outputWSDir is not None: outputWSDir = opt.outputWSDir+"/ws"
else: outputWSDir = "/".join(opt.inputTreeFile.split("/")[:-1])+"/ws"
if not os.path.exists(outputWSDir): os.system("mkdir %s"%outputWSDir)
outputWSFile = outputWSDir+"/"+opt.inputTreeFile.split("/")[-1]
print " --> Creating output workspace: (%s)"%outputWSFile
fout = ROOT.TFile(outputWSFile,"RECREATE")
foutdir = fout.mkdir(inputWSName__.split("/")[0])
foutdir.cd()
ws = ROOT.RooWorkspace(inputWSName__.split("/")[1],inputWSName__.split("/")[1])

# Add variables to workspace
varNames = add_vars_to_workspace(ws,dataVars)

# Make argset
aset = make_argset(ws,varNames)

# Loop over categories and 
for cat in cats:
  print " --> Extracting events from category: %s"%cat
  if inputTreeDir == '': treeName = "Data_%s_%s"%(sqrts__,cat)
  else: treeName = "%s/Data_%s_%s"%(inputTreeDir,sqrts__,cat)
  print "    * tree: %s"%treeName
  t = f.Get(treeName)

  # Define dataset for cat
  dname = "Data_%s_%s"%(sqrts__,cat)  
  d = ROOT.RooDataSet(dname,dname,aset,'weight')

  # Loop over events in tree and add to dataset with weight 1
  for ev in t:
    for var in dataVars: 
      if var == "weight": continue
      ws.var(var).setVal(getattr(ev,var))
    d.add(aset,1.)

  # Add dataset to worksapce
  getattr(ws,'import')(d)
  
# Write workspace to file
ws.Write()

# Close file
fout.Close()
ws.Delete()
fout.Delete()
