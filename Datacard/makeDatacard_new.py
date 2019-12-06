# NEW datacard making scrit
#  * Uses Pandas dataframe to store all info about processes
#  * Option for merging across years

print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG DATACARD MAKER RUN II ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
import os, sys
import re
from optparse import OptionParser
import pandas as pd

def leave():
  print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG DATACARD MAKER RUN II (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
  sys.exit(1)

merged_cats = ['RECO_0J_PTH_GT10_Tag0', 'RECO_0J_PTH_GT10_Tag1', 'RECO_0J_PTH_0_10_Tag0', 'RECO_0J_PTH_0_10_Tag1', 'RECO_PTH_GT200_Tag0', 'RECO_PTH_GT200_Tag1', 'RECO_1J_PTH_120_200_Tag0', 'RECO_1J_PTH_120_200_Tag1', 'RECO_1J_PTH_60_120_Tag0', 'RECO_1J_PTH_60_120_Tag1', 'RECO_1J_PTH_0_60_Tag0', 'RECO_1J_PTH_0_60_Tag1', 'RECO_VBFTOPO_BSM', 'RECO_VBFTOPO_JET3VETO_Tag0', 'RECO_VBFTOPO_JET3VETO_Tag1', 'RECO_VBFTOPO_JET3_Tag0', 'RECO_VBFTOPO_JET3_Tag1', 'RECO_GE2J_PTH_120_200_Tag0', 'RECO_GE2J_PTH_120_200_Tag1', 'RECO_GE2J_PTH_60_120_Tag0', 'RECO_GE2J_PTH_60_120_Tag1', 'RECO_GE2J_PTH_0_60_Tag0', 'RECO_GE2J_PTH_0_60_Tag1'] #full merging
#merged_cats = ['RECO_PTH_GT200_Tag0','RECO_PTH_GT200_Tag1','RECO_VBFTOPO_BSM']
lumi = {'2016':'35.9', '2017':'41.5', '2018':'59.8'}
decay = "hgg"

def get_options():
  parser = OptionParser()
  parser.add_option('--merge', dest='merge', default=False, action="store_true", help="Merge specified categories across years")
  parser.add_option('--years', dest='years', default='2016', help="Comma separated list of years")
  parser.add_option('--procs', dest='procs', default='', help='Comma separated list of signal processes')
  parser.add_option('--cats', dest='cats', default='', help='Comma separated list of analysis categories (no year tags)')
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
    if len(procsByYear) == 1: continue
    else:
      for year2 in procsByYear:
        if year2 == year: continue
        if set(procsByYear[year2]) != set(procsByYear[year]):
          print " --> [ERROR] Mis-match in process for %s and %s. Intersection = %s"%(year,year2,(set(procsByYear[year2]).symmetric_difference(set(procsByYear[year]))))
          leave()
  
    #Save as comma separated string
    opt.procs = ",".join(procsByYear[year])

# Initiate pandas dataframe
columns_data = ['year','proc','cat','modelWSFile','model','rate']
data = pd.DataFrame( columns=columns_data )

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Mapping to STXS process name
#def procToSTXS( _proc ):
#  #Do mapping
#  return _proc

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# FILL DATAFRAME: all processes

# Signal processes
for year in opt.years.split(","):
  for cat in opt.cats.split(","):
    for proc in opt.procs.split(","):
      # FIXME: add mapping to STXS definition here
      #_proc = "%s_%s"%(procToSTXS[proc],year)
      _proc = "%s_%s_%s"%(proc,decay,year)

      # If want to merge some categories
      if opt.merge:
        if cat in merged_cats: _cat = cat
        else: _cat = "%s_%s"%(cat,year)
      else: _cat = "%s_%s"%(cat,year)

      # Input model ws 
      _modelWSFile = "./%s/signal_%s/CMS-HGG_sigfit_mva_%s_%s.root"%(opt.modelWSDir,year,proc,cat)
      _model = "wsig_13TeV:hggpdfsmrel_%s_13TeV_%s_%s"%(year,proc,cat)

      # Extract rate from lumi
      _rate = float(lumi[year])*1000

      # FIXME: add column to dataFrame for pruning: check entries
      # true/false options in X

      # Add signal process to dataFrame:
      data.loc[len(data)] = [year,_proc,_cat,_modelWSFile,_model,_rate]

# Background and data processes
# Merged...
if opt.merge:
  for cat in opt.cats.split(","):
    _proc_bkg = "bkg_mass"
    _proc_data = "data_obs"
    _modelWSFile = "./%s/background_merged/CMS-HGG_mva_13TeV_multipdf.root"%opt.modelWSDir  

    if cat in merged_cats:
      _cat = cat
      _model_bkg = "multipdf:CMS_hgg_%s_13TeV"%_cat
      _model_data = "multipdf:roohist_data_mass_%s"%_cat
      data.loc[len(data)] = ["merged",_proc_bkg,_cat,_modelWSFile,_model_bkg,1.]
      data.loc[len(data)] = ["merged",_proc_data,_cat,_modelWSFile,_model_data,-1]
    else:
      # Loop over years and fill entry per year
      for year in opt.years.split(","):
        _cat = "%s_%s"%(cat,year)
        _model_bkg = "multipdf:CMS_hgg_%s_13TeV"%_cat
        _model_data = "multipdf:roohist_data_mass_%s"%_cat
        data.loc[len(data)] = [year,_proc_bkg,_cat,_modelWSFile,_model_bkg,1.]
        data.loc[len(data)] = [year,_proc_data,_cat,_modelWSFile,_model_data,-1] 
# Fully separate...
else:
  for cat in opt.cats.split(","):
    _proc_bkg = "bkg_mass"
    _proc_data = "data_obs"
    # Loop over years and fill entry per year
    for year in opt.years.split(","):
      _cat = "%s_%s"%(cat,year)
      _modelWSFile = "./%s/background_%s/CMS-HGG_mva_13TeV_multipdf.root"%(opt.modelWSDir,year)
      _model_bkg = "multipdf:CMS_hgg_%s_13TeV"%_cat
      _model_data = "multipdf:roohist_data_mass_%s"%_cat
      data.loc[len(data)] = [year,_proc_bkg,_cat,_modelWSFile,_model_bkg,1.]
      data.loc[len(data)] = [year,_proc_data,_cat,_modelWSFile,_model_data,-1]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CALCULATE SYSTEMATICS AND ADD TO DATAFRAME


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# WRITE TO .TXT FILE
#from writeToDatacard import writePreamble, writeProcesses, writeSystematic, writePdfIndex
from writeToDatacard import writePreamble, writeProcesses, writePdfIndex
fdata = open("Datacard_dummy.txt","w")
if not writePreamble(fdata,opt): 
  print " --> [ERROR] in writing preamble. Leaving..."
  leave()
if not writeProcesses(fdata,data,opt):
  print " --> [ERROR] in writing processes. Leaving..."
  leave()
if not writePdfIndex(fdata,data,opt):
  print " --> [ERROR] in writing pdf indices. Leaving..."
  leave()
fdata.close()
