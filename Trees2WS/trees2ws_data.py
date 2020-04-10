# Script to convert flashgg trees to RooWorkspace (compatible for finalFits)

print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG TREES 2 WS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
import os, sys
import re
from optparse import OptionParser
import ROOT
import uproot
from root_numpy import array2tree

def get_options():
  parser = OptionParser()
  parser.add_option('--inputTreeFile',dest='inputTreeFile', default=None, help='Input tree file')
  parser.add_option('--inputTreeDir',dest='inputTreeDir', default="tagsDumper/trees", help='Input tree file')
  parser.add_option('--outputWSPath',dest='outputWSPath', default=None, help="Output workspace folder")
  return parser.parse_args()
(opt,args) = get_options()

cats = ['RECO_0J_PTH_0_10_Tag0', 'RECO_0J_PTH_0_10_Tag1', 'RECO_0J_PTH_0_10_Tag2', 'RECO_0J_PTH_GT10_Tag0', 'RECO_0J_PTH_GT10_Tag1', 'RECO_0J_PTH_GT10_Tag2', 'RECO_1J_PTH_0_60_Tag0', 'RECO_1J_PTH_0_60_Tag1', 'RECO_1J_PTH_0_60_Tag2', 'RECO_1J_PTH_120_200_Tag0', 'RECO_1J_PTH_120_200_Tag1', 'RECO_1J_PTH_120_200_Tag2', 'RECO_1J_PTH_60_120_Tag0', 'RECO_1J_PTH_60_120_Tag1', 'RECO_1J_PTH_60_120_Tag2', 'RECO_GE2J_PTH_0_60_Tag0', 'RECO_GE2J_PTH_0_60_Tag1', 'RECO_GE2J_PTH_0_60_Tag2', 'RECO_GE2J_PTH_120_200_Tag0', 'RECO_GE2J_PTH_120_200_Tag1', 'RECO_GE2J_PTH_120_200_Tag2', 'RECO_GE2J_PTH_60_120_Tag0', 'RECO_GE2J_PTH_60_120_Tag1', 'RECO_GE2J_PTH_60_120_Tag2', 'RECO_PTH_200_300_Tag0', 'RECO_PTH_200_300_Tag1', 'RECO_PTH_300_450_Tag0', 'RECO_PTH_300_450_Tag1', 'RECO_PTH_450_650_Tag0', 'RECO_PTH_GT650_Tag0', 'RECO_THQ_LEP', 'RECO_TTH_HAD_PTH_0_60_Tag0', 'RECO_TTH_HAD_PTH_0_60_Tag1', 'RECO_TTH_HAD_PTH_0_60_Tag2', 'RECO_TTH_HAD_PTH_0_60_Tag3', 'RECO_TTH_HAD_PTH_120_200_Tag0', 'RECO_TTH_HAD_PTH_120_200_Tag1', 'RECO_TTH_HAD_PTH_120_200_Tag2', 'RECO_TTH_HAD_PTH_120_200_Tag3', 'RECO_TTH_HAD_PTH_60_120_Tag0', 'RECO_TTH_HAD_PTH_60_120_Tag1', 'RECO_TTH_HAD_PTH_60_120_Tag2', 'RECO_TTH_HAD_PTH_60_120_Tag3', 'RECO_TTH_HAD_PTH_GT200_Tag0', 'RECO_TTH_HAD_PTH_GT200_Tag1', 'RECO_TTH_HAD_PTH_GT200_Tag2', 'RECO_TTH_HAD_PTH_GT200_Tag3', 'RECO_TTH_LEP_PTH_0_60_Tag0', 'RECO_TTH_LEP_PTH_0_60_Tag1', 'RECO_TTH_LEP_PTH_0_60_Tag2', 'RECO_TTH_LEP_PTH_0_60_Tag3', 'RECO_TTH_LEP_PTH_120_200_Tag0', 'RECO_TTH_LEP_PTH_120_200_Tag1', 'RECO_TTH_LEP_PTH_60_120_Tag0', 'RECO_TTH_LEP_PTH_60_120_Tag1', 'RECO_TTH_LEP_PTH_GT200_Tag0', 'RECO_TTH_LEP_PTH_GT200_Tag1', 'RECO_VBFLIKEGGH_Tag0', 'RECO_VBFLIKEGGH_Tag1', 'RECO_VBFTOPO_BSM_Tag0', 'RECO_VBFTOPO_BSM_Tag1', 'RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag0', 'RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag1', 'RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag0', 'RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag1', 'RECO_VBFTOPO_JET3_HIGHMJJ_Tag0', 'RECO_VBFTOPO_JET3_HIGHMJJ_Tag1', 'RECO_VBFTOPO_JET3_LOWMJJ_Tag0', 'RECO_VBFTOPO_JET3_LOWMJJ_Tag1', 'RECO_VBFTOPO_VHHAD_Tag0', 'RECO_VBFTOPO_VHHAD_Tag1', 'RECO_VH_MET_Tag0', 'RECO_VH_MET_Tag1', 'RECO_WH_LEP_HIGH_Tag0', 'RECO_WH_LEP_HIGH_Tag1', 'RECO_WH_LEP_HIGH_Tag2', 'RECO_WH_LEP_LOW_Tag0', 'RECO_WH_LEP_LOW_Tag1', 'RECO_WH_LEP_LOW_Tag2', 'RECO_ZH_LEP_Tag0', 'RECO_ZH_LEP_Tag1']

# Dict of vars to add to final workspace
ws_vars = [ # [name,default value, min value, max value, bins]
  {'name':"IntLumi", 'default':0, 'minValue':0, 'maxValue':999999999, 'constant':True},
  {'name':"CMS_hgg_mass", 'default':125., 'minValue':100., 'maxValue':180., 'bins':160}
]

# Define argsets to enter different levels of RooDataSets
argSets = {
  'nominal':'weight,CMS_hgg_mass'
}

# Function to add vars to workspace
def add_vars_to_workspace(_ws=None):
  # Add weight var
  weight = ROOT.RooRealVar("weight","weight",0)
  getattr(ws, 'import')(weight)
  # Loop over vars to enter workspace
  _vars = {}
  for var in ws_vars:
    _vars[var['name']] = ROOT.RooRealVar( var['name'], var['name'], var['default'], var['minValue'], var['maxValue'] )
    if 'constant' in var:
      if var['constant']: _vars[var['name']].setConstant(True)
    if 'bins' in var: _vars[var['name']].setBins(var['bins'])
    getattr(_ws, 'import')( _vars[var['name']], ROOT.RooFit.Silence())

# Function to create arg list depending on Data type
def make_argSet( _ws, _argSets, _type ):
  argSet = ROOT.RooArgSet()
  aset = _argSets[_type]
  args = aset.split(",")
  for arg in args: argSet.add( _ws.var(arg) )
  return argSet
    
# Input file:
f = ROOT.TFile( opt.inputTreeFile )

# Define output workspace to store RooDataSet
ws = ROOT.RooWorkspace("cms_hgg_13TeV","cms_hgg_13TeV")
# Add variables to workspace and create argset
add_vars_to_workspace(ws)
argset = make_argSet( ws, argSets, 'nominal')

# Loop over categoires
for cat in cats:
  print " --> [VERBOSE] Extracting events from category %s and storing in dataset"%cat
  treeName = "%s/Data_13TeV_%s"%(opt.inputTreeDir,cat)
  # Extract tree from uproot
  t = f.Get(treeName)
  # Define dataset for cat
  dname = "Data_13TeV_%s"%cat
  d = ROOT.RooDataSet(dname,dname,argset,'weight')
  # Loop over events in tree and add to dataset with weight of 1
  for ev in t:
    ws.var("CMS_hgg_mass").setVal(ev.CMS_hgg_mass)
    d.add(argset,1.)
  # Add dataset to workspace
  getattr(ws,'import')(d)
  
# Define outputfile
outputWSFile = "%s/%s"%(opt.outputWSPath,opt.inputTreeFile.split("/")[-1])
fout = ROOT.TFile( outputWSFile, "RECREATE" )
foutdir = fout.mkdir("tagsDumper")
foutdir.cd()
# Export ws to file
ws.Write()

fout.Close()
ws.Delete()
fout.Delete()
