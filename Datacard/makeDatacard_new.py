# NEW datacard making scrit
#  * Uses Pandas dataframe to store all info about processes
#  * Option for merging across years

print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG DATACARD MAKER RUN II ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
import os, sys
import re
from optparse import OptionParser
import ROOT
import pandas as pd
import glob

def leave():
  print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG DATACARD MAKER RUN II (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
  sys.exit(1)

#cats = 'RECO_0J_PTH_GT10_Tag0,RECO_VBFTOPO_JET3_HIGHMJJ,RECO_VBFLIKEGGH,RECO_1J_PTH_120_200_Tag0,RECO_PTH_GT200_Tag0,RECO_GE2J_PTH_0_60_Tag1,RECO_GE2J_PTH_60_120_Tag1,RECO_GE2J_PTH_60_120_Tag0,RECO_VBFTOPO_VHHAD,RECO_1J_PTH_120_200_Tag1,RECO_GE2J_PTH_120_200_Tag1,RECO_GE2J_PTH_120_200_Tag0,RECO_1J_PTH_0_60_Tag1,RECO_VBFTOPO_BSM,RECO_VBFTOPO_JET3VETO_HIGHMJJ,RECO_0J_PTH_0_10_Tag0,RECO_PTH_GT200_Tag1,RECO_VBFTOPO_JET3VETO_LOWMJJ,RECO_1J_PTH_0_60_Tag0,RECO_1J_PTH_60_120_Tag1,RECO_0J_PTH_0_10_Tag1,RECO_0J_PTH_GT10_Tag1,RECO_GE2J_PTH_0_60_Tag0,RECO_1J_PTH_60_120_Tag0,RECO_VBFTOPO_JET3_LOWMJJ'
#merged_cats = ['RECO_0J_PTH_GT10_Tag0', 'RECO_0J_PTH_GT10_Tag1', 'RECO_0J_PTH_0_10_Tag0', 'RECO_0J_PTH_0_10_Tag1', 'RECO_PTH_GT200_Tag0', 'RECO_PTH_GT200_Tag1', 'RECO_1J_PTH_120_200_Tag0', 'RECO_1J_PTH_120_200_Tag1', 'RECO_1J_PTH_60_120_Tag0', 'RECO_1J_PTH_60_120_Tag1', 'RECO_1J_PTH_0_60_Tag0', 'RECO_1J_PTH_0_60_Tag1', 'RECO_VBFTOPO_BSM', 'RECO_VBFTOPO_JET3VETO_Tag0', 'RECO_VBFTOPO_JET3VETO_Tag1', 'RECO_VBFTOPO_JET3_Tag0', 'RECO_VBFTOPO_JET3_Tag1', 'RECO_GE2J_PTH_120_200_Tag0', 'RECO_GE2J_PTH_120_200_Tag1', 'RECO_GE2J_PTH_60_120_Tag0', 'RECO_GE2J_PTH_60_120_Tag1', 'RECO_GE2J_PTH_0_60_Tag0', 'RECO_GE2J_PTH_0_60_Tag1'] #full merging
#merged_cats = ['RECO_PTH_GT200_Tag0','RECO_PTH_GT200_Tag1','RECO_VBFTOPO_BSM']
merged_cats = ['RECO_0J_PTH_GT10_Tag1']
lumi = {'2016':'35.9', '2017':'41.5', '2018':'59.8'}
decay = "hgg"

def get_options():
  parser = OptionParser()
  parser.add_option('--merge', dest='merge', default=False, action="store_true", help="Merge specified categories across years")
  parser.add_option('--prune', dest='prune', default=False, action="store_true", help="Prune proc x cat which make up less than 0.1% of given total category")
  parser.add_option('--doSystematics', dest='doSystematics', default=False, action="store_true", help="Include systematics calculations and add to datacard")
  parser.add_option('--removeNoTag', dest='removeNoTag', default=False, action="store_true", help="Remove processing of NoTag")
  parser.add_option('--years', dest='years', default='2016', help="Comma separated list of years")
  parser.add_option('--procs', dest='procs', default='', help='Comma separated list of signal processes')
  parser.add_option('--cats', dest='cats', default='', help='Comma separated list of analysis categories (no year tags)')
  parser.add_option('--xobs', dest='xobs', default='CMS_hgg_mass', help='Observable (default for hgg)')
  parser.add_option('--modelWSDir', dest='modelWSDir', default='Models', help='Input model WS directory') 
  parser.add_option('--inputWSDir', dest='inputWSDir', default='/vols/cms/jl2117/hgg/ws/test_stage1_1', help='Input WS directory (without year tag _201X)') 
  return parser.parse_args()
(opt,args) = get_options()

# Check if input WS exist: adding year tag
for year in opt.years.split(","):
  print " --> Will take %s signal workspaces from %s_%s"%(year,opt.inputWSDir,year)
  if not os.path.isdir( "%s_%s"%(opt.inputWSDir,year) ):
    print " --> [ERROR] Directory %s_%s does not exist. Leaving..."%(opt.inputWSDir,year)
    leave()

# If procs are not specified then extract from inputWSDir (for each year):
if opt.procs == '':
  procsByYear = {}
  wsFullFileNamesByYear = {}
  for year in opt.years.split(","):
    procsByYear[year] = []
    wsFullFileNamesByYear[year] = ''
    inputWSDir = "%s_%s"%(opt.inputWSDir,year)
    # Extract full list of input ws filenames
    ws_fileNames = []
    for root, dirs, files in os.walk( inputWSDir ):
      for fileName in files:
	if not fileName.startswith('output_'): continue
	if not fileName.endswith('.root'): continue 
	ws_fileNames.append( fileName )
    # Concatenate with input dir to get full list of complete file names
    for fileName in ws_fileNames: wsFullFileNamesByYear[year] += "%s/%s,"%(inputWSDir,fileName)
    wsFullFileNamesByYear[year] = wsFullFileNamesByYear[year][:-1]

    # Extract processes from fileNames
    for fileName in ws_fileNames:
      if 'M125' not in fileName: continue
      procsByYear[year].append( fileName.split("pythia8_")[1].split(".root")[0] )  

    # Check equal and save as comma separated string
    if len(procsByYear) != 1:
      for year2 in procsByYear:
        if year2 == year: continue
        if set(procsByYear[year2]) != set(procsByYear[year]):
          print " --> [ERROR] Mis-match in process for %s and %s. Intersection = %s"%(year,year2,(set(procsByYear[year2]).symmetric_difference(set(procsByYear[year]))))
          leave()

    #Save as comma separated string
    opt.procs = ",".join(procsByYear[year])

# Initiate pandas dataframe
columns_data = ['year','type','proc','proc_s0','cat','inputWSFile','nominalDataName','modelWSFile','model','rate','prune']
data = pd.DataFrame( columns=columns_data )

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Mapping to STXS process name
def procToSTXS( _proc ):
  #Do mapping
  proc_map = {"GG2H":"ggH","VBF":"qqH","WH2HQQ":"WH_had","ZH2HQQ":"ZH_had","QQ2HLNU":"WH_lep","QQ2HLL":"ZH_lep","TTH":"ttH","BBH":"bbH"}
  for key in proc_map: _proc = re.sub( key, proc_map[key], _proc )
  return _proc

def procToData( _proc ):
  proc_map = {"GG2H":"ggh","VBF":"vbf"}
  for key in proc_map: _proc = re.sub( key, proc_map[key], _proc )
  return _proc

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# FILL DATAFRAME: all processes
print " .........................................................................................."

# Add NOTAG to categories for signal: prune = 1
cats_sig = opt.cats if opt.removeNoTag else "%s,NOTAG"%opt.cats

# Signal processes
for year in opt.years.split(","):
  for cat in cats_sig.split(","):
    for proc in opt.procs.split(","):
      # Mapping to STXS definition here
      _proc = "%s_%s_hgg"%(procToSTXS(proc),year)
      _proc_s0 = procToData(proc.split("_")[0])

      # If want to merge some categories
      if opt.merge:
        if cat in merged_cats: _cat = cat
        else: _cat = "%s_%s"%(cat,year)
      else: _cat = "%s_%s"%(cat,year)

      # Input flashgg ws
      _inputWSFile = glob.glob("%s_%s/*M125*%s*"%(opt.inputWSDir,year,proc))[0]
      _nominalDataName = "%s_125_13TeV_%s"%(_proc_s0,cat)

      # Input model ws 
      if cat == "NOTAG": _modelWSFile, _model = '-', '-'
      else:
	_modelWSFile = "./%s/signal_%s/CMS-HGG_sigfit_mva_%s_%s.root"%(opt.modelWSDir,year,proc,cat)
	_model = "wsig_13TeV:hggpdfsmrel_%s_13TeV_%s_%s"%(year,proc,cat)

      # Extract rate from lumi
      _rate = float(lumi[year])*1000

      # Prune NOTAG and if FWDH in process name
      if( cat == "NOTAG" )|( "FWDH" in proc ): _prune = 1
      else: _prune = 0

      # Add signal process to dataFrame:
      print " --> [VERBOSE] Adding to dataFrame: (proc,cat) = (%s,%s)"%(_proc,_cat)
      data.loc[len(data)] = [year,'sig',_proc,_proc_s0,_cat,_inputWSFile,_nominalDataName,_modelWSFile,_model,_rate,_prune]

# Background and data processes
# Merged...
if opt.merge:
  for cat in opt.cats.split(","):
    _proc_bkg = "bkg_mass"
    _proc_data = "data_obs"
    _modelWSFile = "./%s/background_merged/CMS-HGG_mva_13TeV_multipdf.root"%opt.modelWSDir  
    _inputWSFile = '-' #not needed for data/bkg
    _nominalDataName = '-' #not needed for data/bkg

    if cat in merged_cats:
      _cat = cat
      _model_bkg = "multipdf:CMS_hgg_%s_13TeV_bkgshape"%_cat
      _model_data = "multipdf:roohist_data_mass_%s"%_cat
      print " --> [VERBOSE] Adding to dataFrame: (proc,cat) = (%s,%s)"%(_proc_bkg,_cat)
      print " --> [VERBOSE] Adding to dataFrame: (proc,cat) = (%s,%s)"%(_proc_data,_cat)
      data.loc[len(data)] = ["merged",'bkg',_proc_bkg,'-',_cat,_inputWSFile,_nominalDataName,_modelWSFile,_model_bkg,1.,0]
      data.loc[len(data)] = ["merged",'data',_proc_data,'-',_cat,_inputWSFile,_nominalDataName,_modelWSFile,_model_data,-1,0]
    else:
      # Loop over years and fill entry per year
      for year in opt.years.split(","):
        _cat = "%s_%s"%(cat,year)
        _model_bkg = "multipdf:CMS_hgg_%s_13TeV_bkgshape"%_cat
        _model_data = "multipdf:roohist_data_mass_%s"%_cat
        print " --> [VERBOSE] Adding to dataFrame: (proc,cat) = (%s,%s)"%(_proc_bkg,_cat)
        print " --> [VERBOSE] Adding to dataFrame: (proc,cat) = (%s,%s)"%(_proc_data,_cat)
        data.loc[len(data)] = [year,'bkg',_proc_bkg,'-',_cat,_inputWSFile,_nominalDataName,_modelWSFile,_model_bkg,1.,0]
        data.loc[len(data)] = [year,'data',_proc_data,'-',_cat,_inputWSFile,_nominalDataName,_modelWSFile,_model_data,-1,0] 
# Fully separate: i.e. processed separately in FinalFits
else:
  for cat in opt.cats.split(","):
    _proc_bkg = "bkg_mass"
    _proc_data = "data_obs"
    # Loop over years and fill entry per year
    for year in opt.years.split(","):
      # FIXME: change year tag to after sqrts to suit current models
      _cat = "%s_%s"%(cat,year)
      _catStripYear = cat
      _modelWSFile = "./%s/background_%s/CMS-HGG_mva_13TeV_multipdf.root"%(opt.modelWSDir,year)
      _inputWSFile = '-' #not needed for data/bk
      _nominalDataName = '-' #not needed for data/bkg
      _model_bkg = "multipdf:CMS_hgg_%s_13TeV_bkgshape"%_cat
      #_model_bkg = "multipdf:CMS_hgg_%s_13TeV_%s_bkgshape"%(_catStripYear,year)
      _model_data = "multipdf:roohist_data_mass_%s"%_catStripYear
      print " --> [VERBOSE] Adding to dataFrame: (proc,cat) = (%s,%s)"%(_proc_bkg,_cat)
      print " --> [VERBOSE] Adding to dataFrame: (proc,cat) = (%s,%s)"%(_proc_data,_cat)
      data.loc[len(data)] = [year,'bkg',_proc_bkg,'-',_cat,_inputWSFile,_nominalDataName,_modelWSFile,_model_bkg,1.,0]
      data.loc[len(data)] = [year,'data',_proc_data,'-',_cat,_inputWSFile,_nominalDataName,_modelWSFile,_model_data,-1,0]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Systematics uncertainty sources: FIXME input as a json file instead
# List of dicts to store info about uncertainty sources
experimental_systematics = [ 
                {'name':'lumi_13TeV','title':'lumi_13TeV','type':'constant','prior':'lnN','merge':0,'value':{'2016':'1.025','2017':'1.023'}},
                {'name':'LooseMvaSF','title':'CMS_hgg_LooseMvaSF','type':'factory','prior':'lnN','merge':0},
                {'name':'PreselSF','title':'CMS_hgg_PreselSF','type':'factory','prior':'lnN','merge':1},
                {'name':'JER','title':'CMS_hgg_res_j','type':'factory','prior':'lnN','merge':0},
                {'name':'metJecUncertainty','title':'CMS_hgg_MET_JEC','type':'factory','prior':'lnN','merge':1},
              ]

# THEORY SYSTEMATICS:

# For type:factory
# Tier system: adds different uncertainties to dataFrame
#   1) shape: only tier used for STXS measurement. Integral of each STXS bin remains constant, looking for shape variations within one bin
#   2) ishape: (CHECK) inclusive shifts in each STXS bin x analysis category
#   3) norm: used for interpretation. Shifts in cross section of each STXS bin but inclusive cross-section for production mode remains constant.
#   4) inorm: (CHECK) inclusive shifts in each STXS bin
#   5) inc: (CHECK) inclusive shifts in each production mode

# Relations: shape = ishape/inorm
#            norm  = inorm/inc
# Specify as list in dict: e.g. 'tiers'=['inc','inorm','norm','ishape','shape']
theory_systematics = [ 
                {'name':'BR_hgg','title':'BR_hgg','type':'constant','prior':'lnN','merge':1,'value':"0.98/1.021"},
                #{'name':'THU_ggH_Mu','title':'CMS_hgg_THU_ggH_Mu','type':'factory','prior':'lnN','merge':1,'tiers':['inorm']},
                #{'name':'THU_ggH_Res','title':'CMS_hgg_THU_ggH_Res','type':'factory','prior':'lnN','merge':1,'tiers':['inorm']},
                #{'name':'THU_ggH_Mig01','title':'CMS_hgg_THU_ggH_Mig01','type':'factory','prior':'lnN','merge':1,'tiers':['inorm']},
                #{'name':'THU_ggH_Mig12','title':'CMS_hgg_THU_ggH_Mig12','type':'factory','prior':'lnN','merge':1,'tiers':['inorm']},
                #{'name':'THU_ggH_VBF2j','title':'CMS_hgg_THU_ggH_VBF2j','type':'factory','prior':'lnN','merge':1,'tiers':['inorm']},
                #{'name':'THU_ggH_VBF3j','title':'CMS_hgg_THU_ggH_VBF3j','type':'factory','prior':'lnN','merge':1,'tiers':['inorm']},
                #{'name':'THU_ggH_PT60','title':'CMS_hgg_THU_ggH_PT60','type':'factory','prior':'lnN','merge':1,'tiers':['inorm']},
                #{'name':'THU_ggH_PT120','title':'CMS_hgg_THU_ggH_PT120','type':'factory','prior':'lnN','merge':1,'tiers':['inorm']},
                #{'name':'THU_ggH_qmtop','title':'CMS_hgg_THU_ggH_qmtop','type':'factory','prior':'lnN','merge':1,'tiers':['inorm']},
                # Scale weights are grouped: [1,2], [3,6], [4,8]
                #{'name':'scaleWeight_0','title':'CMS_hgg_scaleWeight_0','type':'factory','prior':'lnN','merge':1}, # nominal weight
                {'name':'scaleWeight_1','title':'CMS_hgg_scaleWeight_1','type':'factory','prior':'lnN','merge':1,'tiers':['shape']},
                {'name':'scaleWeight_2','title':'CMS_hgg_scaleWeight_2','type':'factory','prior':'lnN','merge':1,'tiers':['shape']},
                {'name':'scaleWeight_3','title':'CMS_hgg_scaleWeight_3','type':'factory','prior':'lnN','merge':1,'tiers':['shape']},
                {'name':'scaleWeight_4','title':'CMS_hgg_scaleWeight_4','type':'factory','prior':'lnN','merge':1,'tiers':['shape']},
                #{'name':'scaleWeight_5','title':'CMS_hgg_scaleWeight_5','type':'factory','prior':'lnN','merge':1,'tiers':['norm','shape']}, #Unphysical
                {'name':'scaleWeight_6','title':'CMS_hgg_scaleWeight_6','type':'factory','prior':'lnN','merge':1,'tiers':['shape']},
                #{'name':'scaleWeight_7','title':'CMS_hgg_scaleWeight_7','type':'factory','prior':'lnN','merge':1,'tiers':['norm','shape']}, #Unphysical
                {'name':'scaleWeight_8','title':'CMS_hgg_scaleWeight_8','type':'factory','prior':'lnN','merge':1,'tiers':['shape']}#,
              ]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Yields: for each signal row in dataFrame extract the yield
print " .........................................................................................."
#   * if systematics=True: also extract reweighted yields for each uncertainty source
from calcSystematics import factoryType, calcSystYields

# Create columns in dataFrame to store yields
data['nominal_yield'] = '-'

# Depending on type of systematic: anti-symmetric = 2 (up/down) columns, symmetric = 1 column
#   * store factoryType of systematic in dictionary
experimentalFactoryType = {}
theoryFactoryType = {}
if opt.doSystematics:
  # Extract first row of signal dataframe and use factoryType function to extract type of systematic
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
      else: data['%s_yield'%s['name']] = '-'

# Loop over signal rows in dataFrame: extract yields (nominal & systematic variations)
for ir,r in data[data['type']=='sig'].iterrows():

  print " --> [VERBOSE] Extracting yields: (%s,%s)"%(r['proc'],r['cat'])

  # Open input WS file and extract workspace
  f_in = ROOT.TFile(r.inputWSFile)
  inputWS = f_in.Get("tagsDumper/cms_hgg_13TeV")
  # Extract nominal RooDataSet and yield
  rdata_nominal = inputWS.data(r.nominalDataName)
  data.at[ir,'nominal_yield'] = rdata_nominal.sumEntries()
  
  # Systematics: loop over systematics and use function to extract yield variations
  if opt.doSystematics:
    # For experimental systematics: skip NOTAG (as incorrect weights)
    if "NOTAG" not in r['cat']:
      experimentalSystYields = calcSystYields(r['nominalDataName'],inputWS,experimentalFactoryType)
      for s,f in experimentalFactoryType.iteritems():
        if f in ['a_w','a_h']: 
          for direction in ['up','down']: 
            data.at[ir,"%s_%s_yield"%(s,direction)] = experimentalSystYields["%s_%s"%(s,direction)]
        else:
          data.at[ir,"%s_yield"%s] = experimentalSystYields[s]
    # For theoretical systematics:
    theorySystYields = calcSystYields(r['nominalDataName'],inputWS,theoryFactoryType)
    for s,f in theoryFactoryType.iteritems():
      if f in ['a_w','a_h']: 
	for direction in ['up','down']: 
	  data.at[ir,"%s_%s_yield"%(s,direction)] = theorySystYields["%s_%s"%(s,direction)]
      else:
	data.at[ir,"%s_yield"%s] = theorySystYields[s]

  # Remove the workspace and file from heap
  inputWS.Delete()
  f_in.Delete()
  f_in.Close()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Systematics: use factory function to calculate yield variations
print " .........................................................................................."
from calcSystematics import addConstantSyst, experimentalSystFactory, theorySystFactory, groupSystematics

if opt.doSystematics:

  # Experimental:
  print " --> [VERBOSE] Adding experimental systematics to datacard"
  # Add constant systematics to dataFrame
  for s in experimental_systematics:
    if s['type'] == 'constant': data = addConstantSyst(data,s,opt)
  data = experimentalSystFactory(data, experimental_systematics, experimentalFactoryType, opt )

  # Theory:
  print " --> [VERBOSE] Adding theory systematics to datacard"
  # Add constant systematics to dataFrame
  for s in theory_systematics:
    if s['type'] == 'constant': data = addConstantSyst(data,s,opt)
  data = theorySystFactory(data, theory_systematics, theoryFactoryType, opt )
  # For scale weights: use function to group uncertainties in relevant scheme
  data, theory_systematics = groupSystematics(data, theory_systematics, prefix="scaleWeight", suffix="shape", groupings=[[1,2],[3,6],[4,8]])

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Pruning: if process contributes less than 0.1% of yield in analysis category then ignore
print " .........................................................................................."
if opt.prune:
  print " --> [VERBOSE] Pruning processes which contribute < 0.1% of RECO category yield"
  # Extract per category yields
  catYields = {}
  for cat in data.cat.unique(): catYields[cat] = data[(data['cat']==cat)&(data['type']=='sig')].nominal_yield.sum()
  # Set prune = 1 if < 0.1% of total cat yield
  mask = (data['nominal_yield']<0.001*data.apply(lambda x: catYields[x['cat']], axis=1))&(data['type']=='sig')
  data.loc[mask,'prune'] = 1

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# WRITE TO .TXT FILE
print " .........................................................................................."
fdataName = "Datacard_dummy.txt"
print " --> [VERBOSE] Writing to datacard file: %s"%fdataName
from writeToDatacard import writePreamble, writeProcesses, writeSystematic, writePdfIndex
fdata = open(fdataName,"w")
if not writePreamble(fdata,opt): 
  print " --> [ERROR] in writing preamble. Leaving..."
  leave()
if not writeProcesses(fdata,data,opt):
  print " --> [ERROR] in writing processes. Leaving..."
  leave()
for syst in experimental_systematics:
  if not writeSystematic(fdata,data,syst,opt):
    print " --> [ERROR] in writing systematic %s (experiment). Leaving"%syst['name']
    leave()
for syst in theory_systematics:
  if not writeSystematic(fdata,data,syst,opt):
    print " --> [ERROR] in writing systematic %s (theory). Leaving"%syst['name']
    leave()
if not writePdfIndex(fdata,data,opt):
  print " --> [ERROR] in writing pdf indices. Leaving..."
  leave()
fdata.close()
