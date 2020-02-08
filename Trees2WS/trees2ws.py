# Script to convert flashgg trees to RooWorkspace (compatible for finalFits)

print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG TREES 2 WS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
import os, sys
import re
from optparse import OptionParser
import ROOT
import pandas
import uproot
from root_numpy import array2tree

# List of main variables to be stored in dataFrame: #FIXME add dZ and centralObjectWeight when in tree
main_var = ["CMS_hgg_mass*","weight","stage1p2bin","*sigma"]
# Array columns to be treated separately
array_columns = {'alphaSWeights':2,'scaleWeights':9,'pdfWeights':60}
columns = {}
for ac,nWeights in array_columns.iteritems(): columns[ac] = ["%s_%g"%(ac[:-1],i) for i in range(0,nWeights)] 

# List of shape systs to add as RooDataHists output workspace
shapeSysts = ['metJecUncertainty', 'SigmaEOverEShift', 'ShowerShapeHighR9EB', 'MCScaleLowR9EB', 'JEC', 'MCSmearLowR9EBRho', 'MCSmearHighR9EEPhi', 'MCScaleGain6EB', 'MCSmearLowR9EERho', 'FNUFEE', 'MCScaleLowR9EE', 'MaterialOuterBarrel', 'metJerUncertainty', 'MCSmearLowR9EEPhi', 'ShowerShapeLowR9EE', 'MCSmearHighR9EBRho', 'MCSmearLowR9EBPhi', 'MCSmearHighR9EERho', 'FNUFEB', 'JER', 'metUncUncertainty', 'MCScaleGain1EB', 'MCScaleHighR9EE', 'MCScaleHighR9EB', 'MCSmearHighR9EBPhi', 'MaterialCentralBarrel', 'MaterialForward', 'MvaShift', 'PUJIDShift', 'ShowerShapeHighR9EE', 'ShowerShapeLowR9EB', 'metPhoUncertainty']
# Variable to add to dataframe from systematic trees
syst_var = ["CMS_hgg_mass","weight","stage1p2bin"]

cats = ['RECO_0J_PTH_0_10_Tag0', 'RECO_0J_PTH_0_10_Tag1', 'RECO_0J_PTH_GT10_Tag0', 'RECO_0J_PTH_GT10_Tag1', 'RECO_1J_PTH_0_60_Tag0', 'RECO_1J_PTH_0_60_Tag1', 'RECO_1J_PTH_120_200_Tag0', 'RECO_1J_PTH_120_200_Tag1', 'RECO_1J_PTH_60_120_Tag0', 'RECO_1J_PTH_60_120_Tag1', 'RECO_GE2J_PTH_0_60_Tag0', 'RECO_GE2J_PTH_0_60_Tag1', 'RECO_GE2J_PTH_120_200_Tag0', 'RECO_GE2J_PTH_120_200_Tag1', 'RECO_GE2J_PTH_60_120_Tag0', 'RECO_GE2J_PTH_60_120_Tag1', 'RECO_PTH_200_300', 'RECO_PTH_300_450', 'RECO_PTH_450_650', 'RECO_PTH_GT650', 'RECO_THQ_LEP', 'RECO_TTH_HAD_HIGH_Tag0', 'RECO_TTH_HAD_HIGH_Tag1', 'RECO_TTH_HAD_HIGH_Tag2', 'RECO_TTH_HAD_HIGH_Tag3', 'RECO_TTH_HAD_LOW_Tag0', 'RECO_TTH_HAD_LOW_Tag1', 'RECO_TTH_HAD_LOW_Tag2', 'RECO_TTH_HAD_LOW_Tag3', 'RECO_TTH_LEP_HIGH_Tag0', 'RECO_TTH_LEP_HIGH_Tag1', 'RECO_TTH_LEP_HIGH_Tag2', 'RECO_TTH_LEP_HIGH_Tag3', 'RECO_TTH_LEP_LOW_Tag0', 'RECO_TTH_LEP_LOW_Tag1', 'RECO_TTH_LEP_LOW_Tag2', 'RECO_TTH_LEP_LOW_Tag3', 'RECO_VBFLIKEGGH_Tag0', 'RECO_VBFLIKEGGH_Tag1', 'RECO_VBFTOPO_BSM_Tag0', 'RECO_VBFTOPO_BSM_Tag1', 'RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag0', 'RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag1', 'RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag0', 'RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag1', 'RECO_VBFTOPO_JET3_HIGHMJJ_Tag0', 'RECO_VBFTOPO_JET3_HIGHMJJ_Tag1', 'RECO_VBFTOPO_JET3_LOWMJJ_Tag0', 'RECO_VBFTOPO_JET3_LOWMJJ_Tag1', 'RECO_VBFTOPO_VHHAD_Tag0', 'RECO_VBFTOPO_VHHAD_Tag1', 'RECO_WH_LEP_HIGH_Tag0', 'RECO_WH_LEP_HIGH_Tag1', 'RECO_WH_LEP_HIGH_Tag2', 'RECO_WH_LEP_LOW_Tag0', 'RECO_WH_LEP_LOW_Tag1', 'RECO_WH_LEP_LOW_Tag2', 'RECO_ZH_LEP','NOTAG']

procToWSFileName = {
  "ggh":"GluGluHToGG"
}


stxs_stage1p2_dict = {
  0:"UNKNOWN",
  -1:"GG2H_FWDH", 
  1:"GG2H_PTH_200_300", 
  2:"GG2H_PTH_300_450", 
  3:"GG2H_PTH_450_650", 
  4:"GG2H_PTH_GT650", 
  5:"GG2H_0J_PTH_0_10", 
  6:"GG2H_0J_PTH_GT10", 
  7:"GG2H_1J_PTH_0_60", 
  8:"GG2H_1J_PTH_60_120", 
  9:"GG2H_1J_PTH_120_200", 
  10:"GG2H_GE2J_MJJ_0_350_PTH_0_60", 
  11:"GG2H_GE2J_MJJ_0_350_PTH_60_120", 
  12:"GG2H_GE2J_MJJ_0_350_PTH_120_200", 
  13:"GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25", 
  14:"GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25", 
  15:"GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25", 
  16:"GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25", 
  -2:"QQ2HQQ_FWDH",
  17:"QQ2HQQ_0J", 
  18:"QQ2HQQ_1J", 
  19:"QQ2HQQ_GE2J_MJJ_0_60", 
  20:"QQ2HQQ_GE2J_MJJ_60_120", 
  21:"QQ2HQQ_GE2J_MJJ_120_350", 
  22:"QQ2HQQ_GE2J_MJJ_GT350_PTH_GT200", 
  23:"QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25", 
  24:"QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25", 
  25:"QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25", 
  26:"QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25", 
  -3:"QQ2HLNU_FWDH",
  27:"QQ2HLNU_PTV_0_75", 
  28:"QQ2HLNU_PTV_75_150", 
  29:"QQ2HLNU_PTV_150_250_0J", 
  30:"QQ2HLNU_PTV_150_250_GE1J", 
  31:"QQ2HLNU_PTV_GT250", 
  -4:"QQ2HLL_FWDH",
  32:"QQ2HLL_PTV_0_75", 
  33:"QQ2HLL_PTV_75_150", 
  34:"QQ2HLL_PTV_150_250_0J", 
  35:"QQ2HLL_PTV_150_250_GE1J", 
  36:"QQ2HLL_PTV_GT250", 
  -5:"GG2HLL_FWDH",
  37:"GG2HLL_PTV_0_75", 
  38:"GG2HLL_PTV_75_150", 
  39:"GG2HLL_PTV_150_250_0J", 
  40:"GG2HLL_PTV_150_250_GE1J", 
  41:"GG2HLL_PTV_GT250", 
  -6:"TTH_FWDH",
  42:"TTH_PTH_0_60", 
  43:"TTH_PTH_60_120", 
  44:"TTH_PTH_120_200", 
  45:"TTH_PTH_200_300", 
  46:"TTH_PTH_GT300", 
  -7:"BBH_FWDH",
  47:"BBH", 
  -8:"TH_FWDH",
  48:"TH"
}


# Dict of vars to add to final workspace
ws_vars = [ # [name,default value, min value, max value, bins]
  {'name':"IntLumi", 'default':1000, 'minValue':0, 'maxValue':999999999, 'constant':True},
  {'name':"CMS_hgg_mass", 'default':125., 'minValue':100., 'maxValue':180., 'bins':160},
  {'name':"dZ", 'default':0, 'minValue':-20, 'maxValue':20, 'bins':40},
  {'name':"centralObjectWeight", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"LooseMvaSFUp01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"PreselSFUp01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"electronVetoSFUp01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"TriggerWeightUp01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"FracRVWeightUp01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"FracRVNvtxWeightUp01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"MuonIDWeightUp01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"ElectronIDWeightUp01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"ElectronRecoWeightUp01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"MuonIsoWeightUp01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"JetBTagCutWeightUp01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"JetBTagReshapeWeightUp01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"PrefireProbabilityUp01sigma", 'default':0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_MuUp01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_ResUp01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_Mig01Up01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_Mig12Up01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_VBF2jUp01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_VBF3jUp01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_PT60Up01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_PT120Up01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_qmtopUp01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"LooseMvaSFDown01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"PreselSFDown01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"electronVetoSFDown01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"TriggerWeightDown01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"FracRVWeightDown01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"FracRVNvtxWeightDown01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"MuonIDWeightDown01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"ElectronIDWeightDown01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"ElectronRecoWeightDown01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"MuonIsoWeightDown01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"JetBTagCutWeightDown01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"JetBTagReshapeWeightDown01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"PrefireProbabilityDown01sigma", 'default':0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_MuDown01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_ResDown01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_Mig01Down01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_Mig12Down01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_VBF2jDown01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_VBF3jDown01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_PT60Down01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_PT120Down01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_qmtopDown01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1}
]
for ac, nWeights in array_columns.iteritems():
  for i in range(0,nWeights):
    ws_vars.append({'name':"%s_%g"%(ac[:-1],i), 'default':1.0, 'minValue':-999999, 'maxValue':999999}) 

# Define argsets to enter different levels of RooDataSets
argSets = {
  'nominal':'weight,CMS_hgg_mass,dZ,centralObjectWeight,LooseMvaSFUp01sigma,PreselSFUp01sigma,electronVetoSFUp01sigma,TriggerWeightUp01sigma,FracRVWeightUp01sigma,FracRVNvtxWeightUp01sigma,MuonIDWeightUp01sigma,ElectronIDWeightUp01sigma,ElectronRecoWeightUp01sigma,MuonIsoWeightUp01sigma,JetBTagCutWeightUp01sigma,JetBTagReshapeWeightUp01sigma,PrefireProbabilityUp01sigma,THU_ggH_MuUp01sigma,THU_ggH_ResUp01sigma,THU_ggH_Mig01Up01sigma,THU_ggH_Mig12Up01sigma,THU_ggH_VBF2jUp01sigma,THU_ggH_VBF3jUp01sigma,THU_ggH_PT60Up01sigma,THU_ggH_PT120Up01sigma,THU_ggH_qmtopUp01sigma,LooseMvaSFDown01sigma,PreselSFDown01sigma,electronVetoSFDown01sigma,TriggerWeightDown01sigma,FracRVWeightDown01sigma,FracRVNvtxWeightDown01sigma,MuonIDWeightDown01sigma,ElectronIDWeightDown01sigma,ElectronRecoWeightDown01sigma,MuonIsoWeightDown01sigma,JetBTagCutWeightDown01sigma,JetBTagReshapeWeightDown01sigma,PrefireProbabilityDown01sigma,THU_ggH_MuDown01sigma,THU_ggH_ResDown01sigma,THU_ggH_Mig01Down01sigma,THU_ggH_Mig12Down01sigma,THU_ggH_VBF2jDown01sigma,THU_ggH_VBF3jDown01sigma,THU_ggH_PT60Down01sigma,THU_ggH_PT120Down01sigma,THU_ggH_qmtopDown01sigma,pdfWeight_0,pdfWeight_1,pdfWeight_2,pdfWeight_3,pdfWeight_4,pdfWeight_5,pdfWeight_6,pdfWeight_7,pdfWeight_8,pdfWeight_9,pdfWeight_10,pdfWeight_11,pdfWeight_12,pdfWeight_13,pdfWeight_14,pdfWeight_15,pdfWeight_16,pdfWeight_17,pdfWeight_18,pdfWeight_19,pdfWeight_20,pdfWeight_21,pdfWeight_22,pdfWeight_23,pdfWeight_24,pdfWeight_25,pdfWeight_26,pdfWeight_27,pdfWeight_28,pdfWeight_29,pdfWeight_30,pdfWeight_31,pdfWeight_32,pdfWeight_33,pdfWeight_34,pdfWeight_35,pdfWeight_36,pdfWeight_37,pdfWeight_38,pdfWeight_39,pdfWeight_40,pdfWeight_41,pdfWeight_42,pdfWeight_43,pdfWeight_44,pdfWeight_45,pdfWeight_46,pdfWeight_47,pdfWeight_48,pdfWeight_49,pdfWeight_50,pdfWeight_51,pdfWeight_52,pdfWeight_53,pdfWeight_54,pdfWeight_55,pdfWeight_56,pdfWeight_57,pdfWeight_58,pdfWeight_59,scaleWeight_0,scaleWeight_1,scaleWeight_2,scaleWeight_3,scaleWeight_4,scaleWeight_5,scaleWeight_6,scaleWeight_7,scaleWeight_8,alphaSWeight_0,alphaSWeight_1',
  'shapeSyst':'CMS_hgg_mass',
  'notag':'weight,pdfWeight_0,pdfWeight_1,pdfWeight_2,pdfWeight_3,pdfWeight_4,pdfWeight_5,pdfWeight_6,pdfWeight_7,pdfWeight_8,pdfWeight_9,pdfWeight_10,pdfWeight_11,pdfWeight_12,pdfWeight_13,pdfWeight_14,pdfWeight_15,pdfWeight_16,pdfWeight_17,pdfWeight_18,pdfWeight_19,pdfWeight_20,pdfWeight_21,pdfWeight_22,pdfWeight_23,pdfWeight_24,pdfWeight_25,pdfWeight_26,pdfWeight_27,pdfWeight_28,pdfWeight_29,pdfWeight_30,pdfWeight_31,pdfWeight_32,pdfWeight_33,pdfWeight_34,pdfWeight_35,pdfWeight_36,pdfWeight_37,pdfWeight_38,pdfWeight_39,pdfWeight_40,pdfWeight_41,pdfWeight_42,pdfWeight_43,pdfWeight_44,pdfWeight_45,pdfWeight_46,pdfWeight_47,pdfWeight_48,pdfWeight_49,pdfWeight_50,pdfWeight_51,pdfWeight_52,pdfWeight_53,pdfWeight_54,pdfWeight_55,pdfWeight_56,pdfWeight_57,pdfWeight_58,pdfWeight_59,scaleWeight_0,scaleWeight_1,scaleWeight_2,scaleWeight_3,scaleWeight_4,scaleWeight_5,scaleWeight_6,scaleWeight_7,scaleWeight_8,alphaSWeight_0,alphaSWeight_1'
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
    
def get_options():
  parser = OptionParser()
  parser.add_option('--inputTreeFile',dest='inputTreeFile', default="/vols/cms/jl2117/hgg/ws/Feb20/trees/output_1.root", help='Input tree file')
  parser.add_option('--inputTreeDir',dest='inputTreeDir', default="tagsDumper/trees", help='Input tree file')
  return parser.parse_args()
(opt,args) = get_options()


# Uproot file:
f = uproot.open(opt.inputTreeFile)
# Extract id from input file
f_id = re.sub(".root","",opt.inputTreeFile.split("_")[-1])
# FIXME: from file name extract the process
proc_s0 = 'ggh'

# Dataframe to store all events in file
data = pandas.DataFrame()

# Loop over categories:
for cat in cats:
  treeName = "%s/%s_125_13TeV_%s"%(opt.inputTreeDir,proc_s0,cat)
  # Extract tree from uproot
  t = f[treeName]
  if len(t) == 0: continue
  # Convert tree to pandas dataFrame: do array columns separately
  dfs_tomerge = {}
  for ac, acNames in columns.iteritems(): 
    dfs_tomerge[ac] = t.pandas.df(ac)
    dfs_tomerge[ac].columns = acNames
  dfs_tomerge['main'] = t.pandas.df(main_var)
  # Merge
  df = pandas.concat( dfs_tomerge.values(), axis=1)
  # Add column to specify "nominal"
  df['type'] = 'nominal' if cat!='NOTAG' else 'notag'
  # Add columns for dZ = 0 and central object weight (mean of LooseMVAShiftUp
  df['dZ'] = 0.
  df['centralObjectWeight'] = df.apply(lambda x: 0.5*(x['LooseMvaSFUp01sigma']+x['LooseMvaSFDown01sigma']), axis=1) if cat!='NOTAG' else 'notag'

  # Loop over shape systematic variations: extract dataframe with reduced var
  if cat != "NOTAG": # NOTAG does not include syst shifts
    for s in shapeSysts:
      for direction in ['Up','Down']:
	sTreeName = "%s_%s%s01sigma"%(treeName,s,direction)
	st = f[sTreeName]
	sdf = st.pandas.df(syst_var)
	sdf['type'] = "%s%s"%(s,direction)
	# Add dataFrame to total dataFrame
	df = pandas.concat([df,sdf], ignore_index=True, axis=0, sort=False)

  # Add column to dataframe specifying category
  df['cat'] = cat

  # Add to overall dataFrame
  data = pandas.concat([data,df], ignore_index=True, axis=0, sort=False)

# Loop over unique values of STXS stage 1.2 bin: b
for b in data.stage1p2bin.unique():

  # Open file to write to
  outputWSDir = "/".join(opt.inputTreeFile.split("/")[:-1])+"/outputWS_proc_%s_stxs_%s"%(proc_s0,stxs_stage1p2_dict[int(b)])
  if not os.path.exists(outputWSDir): os.system("mkdir %s"%outputWSDir)
  outputWSFile = "%s/output_%s_M125_13TeV_amcatnloFXFX_pythia8_%s_%s.root"%(outputWSDir,procToWSFileName[proc_s0],stxs_stage1p2_dict[int(b)],f_id) 
  fout = ROOT.TFile(outputWSFile,"RECREATE")
  foutdir = fout.mkdir("tagsDumper")
  foutdir.cd()

  # Define output workspace to store RooDataSet and RooDataHist
  ws = ROOT.RooWorkspace("cms_hgg_13TeV","cms_hgg_13TeV")
  # Add variables to workspace
  add_vars_to_workspace(ws) 
    
  # Loop over cats
  for cat in cats:
    # Create mask for nominal dataset
    mask = (data['stage1p2bin']==b)&((data['type']=='nominal')|(data['type']=='notag'))&(data['cat']==cat)
    # Convert dataframe to structured array --> ROOT tree
    sa = data[mask].to_records()
    t = array2tree(sa)
    # Generate RooDataSet
    dname = "%s_125_13TeV_%s"%(proc_s0,cat)
    # Extract ArgSet
    if cat == 'NOTAG': argset = make_argSet( ws, argSets, 'notag') 
    else: argset = make_argSet( ws, argSets, 'nominal')
    # Convert tree to RooDataSet and add to workspace
    d = ROOT.RooDataSet(dname,dname,t,argset,'','weight')
    getattr(ws,'import')(d)

    # Loop over shapeSysts and add RooDataHists
    if cat != 'NOTAG':
      for s in shapeSysts:
        for direction in ['Up','Down']:
          # Create mask for systematic variation
          mask = (data['stage1p2bin']==b)&(data['type']=='%s%s'%(s,direction))&(data['cat']==cat)
          # Convert dataFrame to structured array --> ROOT tree
          sa = data[mask].to_records()
          t = array2tree(sa)
          # Name of RooDataHist
          hname = "%s_125_13TeV_%s_%s%s01sigma"%(proc_s0,cat,s,direction)
          argset = make_argSet( ws, argSets, 'shapeSyst')
          h = ROOT.RooDataHist(hname,hname,argset)
          for ev in t:
            ws.var("CMS_hgg_mass").setVal(ev.CMS_hgg_mass)
            h.add(argset,ev.weight)
          # Add to workspace
          getattr(ws,'import')(h)

  # Export ws to file
  ws.Write()

  # Delete workspace and file from heap
  fout.Close()
  ws.Delete()
  fout.Delete()
  
  
