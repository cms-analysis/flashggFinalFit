# NEW scrip to calculate yields from input workspaces
#  * Uses Pandas dataframe to store all proc x cat yields
#  * Including systematic variations
#  * Output to be used for creating datacard

print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG DATACARD MAKER RUN II ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
import os, sys
import re
from optparse import OptionParser
import ROOT
import pandas as pd
import glob
import pickle
from collections import OrderedDict
from systematics import theory_systematics, experimental_systematics, signal_shape_systematics

def leave():
  print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG DATACARD MAKER RUN II (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
  sys.exit(1)

mergedYear_cats = ['RECO_0J_PTH_0_10_Tag0', 'RECO_0J_PTH_0_10_Tag1', 'RECO_0J_PTH_0_10_Tag2', 'RECO_0J_PTH_GT10_Tag0', 'RECO_0J_PTH_GT10_Tag1', 'RECO_0J_PTH_GT10_Tag2', 'RECO_1J_PTH_0_60_Tag0', 'RECO_1J_PTH_0_60_Tag1', 'RECO_1J_PTH_0_60_Tag2', 'RECO_1J_PTH_120_200_Tag0', 'RECO_1J_PTH_120_200_Tag1', 'RECO_1J_PTH_120_200_Tag2', 'RECO_1J_PTH_60_120_Tag0', 'RECO_1J_PTH_60_120_Tag1', 'RECO_1J_PTH_60_120_Tag2', 'RECO_GE2J_PTH_0_60_Tag0', 'RECO_GE2J_PTH_0_60_Tag1', 'RECO_GE2J_PTH_0_60_Tag2', 'RECO_GE2J_PTH_120_200_Tag0', 'RECO_GE2J_PTH_120_200_Tag1', 'RECO_GE2J_PTH_120_200_Tag2', 'RECO_GE2J_PTH_60_120_Tag0', 'RECO_GE2J_PTH_60_120_Tag1', 'RECO_GE2J_PTH_60_120_Tag2', 'RECO_PTH_200_300_Tag0', 'RECO_PTH_200_300_Tag1', 'RECO_PTH_300_450_Tag0', 'RECO_PTH_300_450_Tag1', 'RECO_PTH_450_650_Tag0', 'RECO_PTH_GT650_Tag0', 'RECO_THQ_LEP', 'RECO_TTH_HAD_PTH_0_60_Tag0', 'RECO_TTH_HAD_PTH_0_60_Tag1', 'RECO_TTH_HAD_PTH_0_60_Tag2', 'RECO_TTH_HAD_PTH_0_60_Tag3', 'RECO_TTH_HAD_PTH_120_200_Tag0', 'RECO_TTH_HAD_PTH_120_200_Tag1', 'RECO_TTH_HAD_PTH_120_200_Tag2', 'RECO_TTH_HAD_PTH_120_200_Tag3', 'RECO_TTH_HAD_PTH_60_120_Tag0', 'RECO_TTH_HAD_PTH_60_120_Tag1', 'RECO_TTH_HAD_PTH_60_120_Tag2', 'RECO_TTH_HAD_PTH_60_120_Tag3', 'RECO_TTH_HAD_PTH_GT200_Tag0', 'RECO_TTH_HAD_PTH_GT200_Tag1', 'RECO_TTH_HAD_PTH_GT200_Tag2', 'RECO_TTH_HAD_PTH_GT200_Tag3', 'RECO_TTH_LEP_PTH_0_60_Tag0', 'RECO_TTH_LEP_PTH_0_60_Tag1', 'RECO_TTH_LEP_PTH_0_60_Tag2', 'RECO_TTH_LEP_PTH_0_60_Tag3', 'RECO_TTH_LEP_PTH_120_200_Tag0', 'RECO_TTH_LEP_PTH_120_200_Tag1', 'RECO_TTH_LEP_PTH_60_120_Tag0', 'RECO_TTH_LEP_PTH_60_120_Tag1', 'RECO_TTH_LEP_PTH_GT200_Tag0', 'RECO_TTH_LEP_PTH_GT200_Tag1', 'RECO_VBFLIKEGGH_Tag0', 'RECO_VBFLIKEGGH_Tag1', 'RECO_VBFTOPO_BSM_Tag0', 'RECO_VBFTOPO_BSM_Tag1', 'RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag0', 'RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag1', 'RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag0', 'RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag1', 'RECO_VBFTOPO_JET3_HIGHMJJ_Tag0', 'RECO_VBFTOPO_JET3_HIGHMJJ_Tag1', 'RECO_VBFTOPO_JET3_LOWMJJ_Tag0', 'RECO_VBFTOPO_JET3_LOWMJJ_Tag1', 'RECO_VBFTOPO_VHHAD_Tag0', 'RECO_VBFTOPO_VHHAD_Tag1', 'RECO_VH_MET_Tag0', 'RECO_VH_MET_Tag1', 'RECO_WH_LEP_HIGH_Tag0', 'RECO_WH_LEP_HIGH_Tag1', 'RECO_WH_LEP_HIGH_Tag2', 'RECO_WH_LEP_LOW_Tag0', 'RECO_WH_LEP_LOW_Tag1', 'RECO_WH_LEP_LOW_Tag2', 'RECO_ZH_LEP_Tag0', 'RECO_ZH_LEP_Tag1'] 

lumi = {'2016':'35.92', '2017':'41.53', '2018':'59.74'}
decay = "hgg"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Mapping to STXS bin and nominal dataset name:
def procToSTXS( _proc ):
  #Do mapping
  proc_map = {"GG2H":"ggH","VBF":"qqH","WH2HQQ":"WH_had","ZH2HQQ":"ZH_had","QQ2HLNU":"WH_lep","QQ2HLL":"ZH_lep","TTH":"ttH","BBH":"bbH","THQ":"tHq","THW":"tHW","TH":"tHq","GG2HQQ":"ggZH_had","GG2HLL":"ggZH_ll","GG2HNUNU":"ggZH_nunu"}
  for key in proc_map: 
    if key == _proc.split("_")[0]: _proc = re.sub( key, proc_map[key], _proc )
  return _proc

def procToData( _proc ):
  proc_map = {"GG2H":"ggh","VBF":"vbf","WH2HQQ":"wh","ZH2HQQ":"zh","QQ2HLNU":"wh","QQ2HLL":"zh","TTH":"tth","BBH":"bbh","THQ":"thq","THW":"thw","TH":"thq","GG2HQQ":"ggzh","GG2HLL":"ggzh","GG2HNUNU":"ggzh"}
  for key in proc_map: 
    if key == _proc.split("_")[0]: _proc = re.sub( key, proc_map[key], _proc )
    #_proc = re.sub( key, proc_map[key], _proc )
  return _proc

def get_options():
  parser = OptionParser()
  parser.add_option('--mergeYears', dest='mergeYears', default=False, action="store_true", help="Merge specified categories across years")
  parser.add_option('--doBkgSplit', dest='doBkgSplit', default=False, action="store_true", help="Split background models to different files (is used fTestParallel)")
  parser.add_option('--skipBkg', dest='skipBkg', default=False, action="store_true", help="Only add signal processes to datacard")
  parser.add_option('--bkgScaler', dest='bkgScaler', default=1., type="float", help="Add overall scale factor for background")
  parser.add_option('--skipCOWCorr', dest='skipCOWCorr', default=False, action="store_true", help="Skip centralObjectWeight correction for events in acceptance")
  parser.add_option('--doSystematics', dest='doSystematics', default=False, action="store_true", help="Include systematics calculations and add to datacard")
  parser.add_option('--years', dest='years', default='2016', help="Comma separated list of years")
  parser.add_option('--procs', dest='procs', default='', help='Comma separated list of signal processes. If not specified then will infer automatically from files in WS')
  parser.add_option('--cat', dest='cat', default='', help='Analysis category')
  parser.add_option('--modelWSDir', dest='modelWSDir', default='Models', help='Input model WS directory') 
  parser.add_option('--packagedSignal', dest='packagedSignal', default=False, action="store_true", help='Signal models packaged into one file per category') 
  parser.add_option('--inputWSDir', dest='inputWSDir', default='/vols/cms/jl2117/hgg/ws/test_stage1_1', help='Input WS directory (without year tag _201X)') 
  parser.add_option('--ext', dest='ext', default='', help='Extension for saving') 
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
columns_data = ['year','type','proc','proc_s0','cat','inputWSFile','nominalDataName','modelWSFile','model','rate']
data = pd.DataFrame( columns=columns_data )

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# FILL DATAFRAME: all processes
print " .........................................................................................."

# Signal processes
for year in opt.years.split(","):
  for proc in opt.procs.split(","):
    # Mapping to STXS definition here
    _proc = "%s_%s_hgg"%(procToSTXS(proc),year)
    _proc_s0 = procToData(proc.split("_")[0])

    # If want to merge some categories
    if opt.mergeYears:
      if opt.cat in mergedYear_cats: _cat = opt.cat
      else: _cat = "%s_%s"%(opt.cat,year)
    else: _cat = "%s_%s"%(opt.cat,year)

    # Input flashgg ws
    _inputWSFile = glob.glob("%s_%s/*M125*_%s.root"%(opt.inputWSDir,year,proc))[0]
    _nominalDataName = "%s_125_13TeV_%s"%(_proc_s0,opt.cat)

    # Input model ws 
    if opt.cat == "NOTAG": _modelWSFile, _model = '-', '-'
    else:
      if opt.packagedSignal: _modelWSFile = "./%s/signal/CMS-HGG_sigfit_mva_%s.root"%(opt.modelWSDir,opt.cat)
      else: _modelWSFile = "./%s/signal_%s/CMS-HGG_sigfit_mva_%s_%s.root"%(opt.modelWSDir,year,proc,opt.cat)
      _model = "wsig_13TeV:hggpdfsmrel_%s_13TeV_%s_%s"%(year,proc,opt.cat)

    # Extract rate from lumi
    _rate = float(lumi[year])*1000

    # Add signal process to dataFrame:
    print " --> [VERBOSE] Adding to dataFrame: (proc,cat) = (%s,%s)"%(_proc,_cat)
    data.loc[len(data)] = [year,'sig',_proc,_proc_s0,_cat,_inputWSFile,_nominalDataName,_modelWSFile,_model,_rate]

if( not opt.skipBkg)&( opt.cat != "NOTAG" ):
  # Background and data processes
  # Merged...
  if opt.mergeYears:
    _proc_bkg = "bkg_mass"
    _proc_data = "data_obs"
    if opt.doBkgSplit: _modelWSFile = "./%s/background_merged/CMS-HGG_mva_13TeV_multipdf_%s.root"%(opt.modelWSDir,opt.cat)
    else: _modelWSFile = "./%s/background_merged/CMS-HGG_mva_13TeV_multipdf.root"%opt.modelWSDir
    _inputWSFile = '-' #not needed for data/bkg
    _nominalDataName = '-' #not needed for data/bkg

    if opt.cat in mergedYear_cats:
      _cat = opt.cat
      _model_bkg = "multipdf:CMS_hgg_%s_13TeV_bkgshape"%_cat
      _model_data = "multipdf:roohist_data_mass_%s"%_cat
      print " --> [VERBOSE] Adding to dataFrame: (proc,cat) = (%s,%s)"%(_proc_bkg,_cat)
      print " --> [VERBOSE] Adding to dataFrame: (proc,cat) = (%s,%s)"%(_proc_data,_cat)
      data.loc[len(data)] = ["merged",'bkg',_proc_bkg,'-',_cat,_inputWSFile,_nominalDataName,_modelWSFile,_model_bkg,opt.bkgScaler]
      data.loc[len(data)] = ["merged",'data',_proc_data,'-',_cat,_inputWSFile,_nominalDataName,_modelWSFile,_model_data,-1]
    else:
      # Loop over years and fill entry per year
      for year in opt.years.split(","):
	_cat = "%s_%s"%(opt.cat,year)
	_model_bkg = "multipdf:CMS_hgg_%s_13TeV_bkgshape"%_cat
	_model_data = "multipdf:roohist_data_mass_%s"%_cat
	print " --> [VERBOSE] Adding to dataFrame: (proc,cat) = (%s,%s)"%(_proc_bkg,_cat)
	print " --> [VERBOSE] Adding to dataFrame: (proc,cat) = (%s,%s)"%(_proc_data,_cat)
	data.loc[len(data)] = [year,'bkg',_proc_bkg,'-',_cat,_inputWSFile,_nominalDataName,_modelWSFile,_model_bkg,opt.bkgScaler,0]
	data.loc[len(data)] = [year,'data',_proc_data,'-',_cat,_inputWSFile,_nominalDataName,_modelWSFile,_model_data,-1,0] 

  # Fully separate: i.e. processed separately in FinalFits
  else:
    _proc_bkg = "bkg_mass"
    _proc_data = "data_obs"
    # Loop over years and fill entry per year
    for year in opt.years.split(","):
      _cat = "%s_%s"%(opt.cat,year)
      _catStripYear = opt.cat
      if opt.doBkgSplit: _modelWSFile = "./%s/background_%s/CMS-HGG_mva_13TeV_multipdf_%s.root"%(opt.modelWSDir,year,opt.cat)
      else: _modelWSFile = "./%s/background_%s/CMS-HGG_mva_13TeV_multipdf.root"%(opt.modelWSDir,year)
      _inputWSFile = '-' #not needed for data/bk
      _nominalDataName = '-' #not needed for data/bkg
      _model_bkg = "multipdf:CMS_hgg_%s_13TeV_bkgshape"%_cat
      _model_data = "multipdf:roohist_data_mass_%s"%_catStripYear
      print " --> [VERBOSE] Adding to dataFrame: (proc,cat) = (%s,%s)"%(_proc_bkg,_cat)
      print " --> [VERBOSE] Adding to dataFrame: (proc,cat) = (%s,%s)"%(_proc_data,_cat)
      data.loc[len(data)] = [year,'bkg',_proc_bkg,'-',_cat,_inputWSFile,_nominalDataName,_modelWSFile,_model_bkg,opt.bkgScaler]
      data.loc[len(data)] = [year,'data',_proc_data,'-',_cat,_inputWSFile,_nominalDataName,_modelWSFile,_model_data,-1]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Yields: for each signal row in dataFrame extract the yield
print " .........................................................................................."
#   * if systematics=True: also extract reweighted yields for each uncertainty source
from calcSystematics import factoryType, calcSystYields

# Create columns in dataFrame to store yields
data['nominal_yield'] = '-'
if not opt.skipCOWCorr: data['nominal_yield_COWCorr'] = '-'

if opt.doSystematics:
  # Depending on type of systematic: anti-symmetric = 2 (up/down) columns, symmetric = 1 column
  #   * store factoryType of systematic in dictionary
  experimentalFactoryType = {}
  theoryFactoryType = {}
  if opt.doSystematics:
    # Extract first row of signal dataframe and use factoryType function to extract type of systematic
    if opt.cat != "NOTAG":
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
	  if not opt.skipCOWCorr:
	    data['%s_up_yield_COWCorr'%s['name']] = '-'
	    data['%s_down_yield_COWCorr'%s['name']] = '-'
	else: 
	  data['%s_yield'%s['name']] = '-'
	  if not opt.skipCOWCorr: data['%s_yield_COWCorr'%s['name']] = '-'

# Loop over signal rows in dataFrame: extract yields (nominal & systematic variations)
totalSignalRows = float(data[data['type']=='sig'].shape[0])
for ir,r in data[data['type']=='sig'].iterrows():

  print " --> [VERBOSE] Extracting yields: (%s,%s) [%.1f%%]"%(r['proc'],r['cat'],100*(float(ir)/totalSignalRows))

  # Open input WS file and extract workspace
  f_in = ROOT.TFile(r.inputWSFile)
  inputWS = f_in.Get("tagsDumper/cms_hgg_13TeV")
  # Extract nominal RooDataSet and yield
  rdata_nominal = inputWS.data(r.nominalDataName)
  data.at[ir,'nominal_yield'] = rdata_nominal.sumEntries()

  # Calculate nominal yield with COW correction for in acceptance events
  if not opt.skipCOWCorr:
    y_COWCorr = 0
    for i in range(0,rdata_nominal.numEntries()):
      p = rdata_nominal.get(i)
      w = rdata_nominal.weight()
      f_COWCorr, f_NNLOPS = p.getRealValue("centralObjectWeight"), abs(p.getRealValue("NNLOPSweight"))
      if f_COWCorr == 0: continue
      else: y_COWCorr += w*(f_NNLOPS/f_COWCorr)
    data.at[ir,'nominal_yield_COWCorr'] = y_COWCorr
       
  # Systematics: loop over systematics and use function to extract yield variations
  if opt.doSystematics:
    # For experimental systematics: skip NOTAG events
    if "NOTAG" not in r['cat']:
      experimentalSystYields = calcSystYields(r['nominalDataName'],inputWS,experimentalFactoryType)
      for s,f in experimentalFactoryType.iteritems():
	if f in ['a_w','a_h']: 
	  for direction in ['up','down']: 
	    data.at[ir,"%s_%s_yield"%(s,direction)] = experimentalSystYields["%s_%s"%(s,direction)]
	else:
	  data.at[ir,"%s_yield"%s] = experimentalSystYields[s]
    # For theoretical systematics:
    theorySystYields = calcSystYields(r['nominalDataName'],inputWS,theoryFactoryType,skipCOWCorr=opt.skipCOWCorr)
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
  f_in.Delete()
  f_in.Close()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SAVE YIELDS DATAFRAME
print " .........................................................................................."
print " --> [VERBOSE] Saving yields dataframe: ./yields%s/%s.pkl"%(opt.ext,opt.cat)
if not os.path.isdir("./yields%s"%opt.ext): os.system("mkdir ./yields%s"%opt.ext)
with open("./yields%s/%s.pkl"%(opt.ext,opt.cat),"wb") as fD: pickle.dump(data,fD)
