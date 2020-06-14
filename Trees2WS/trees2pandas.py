# Script to convert flashgg trees to RooWorkspace (compatible for finalFits)

print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG TREES 2 WS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
import os, sys
import re
from optparse import OptionParser
import ROOT
import pandas
import uproot
import pickle

# List of main variables to be stored in dataFrame: dZ and central
main_var = ["CMS_hgg_mass*","weight","stage1p2bin","centralObjectWeight","dZ","*sigma","btagReshapeNorm_*"]
main_var_nnlops = ["CMS_hgg_mass*","weight","stage1p2bin","centralObjectWeight","dZ","*sigma","btagReshapeNorm_*","NNLOPSweight"]
main_var_notag = ["CMS_hgg_mass*","weight","stage1p2bin","*sigma"]
# Array columns to be treated separately
array_columns = {'alphaSWeights':2,'scaleWeights':9,'pdfWeights':60}
columns = {}
for ac,nWeights in array_columns.iteritems(): columns[ac] = ["%s_%g"%(ac[:-1],i) for i in range(0,nWeights)] 

# List of shape systs to add as RooDataHists output workspace
shapeSysts = ['FNUFEB', 'FNUFEE', 'JECAbsoluteYEAR', 'JECAbsolute', 'JECBBEC1YEAR', 'JECBBEC1', 'JECEC2YEAR', 'JECEC2', 'JECFlavorQCD', 'JECHFYEAR', 'JECHF', 'JECRelativeBal', 'JECRelativeSampleYEAR', 'JEC', 'JER', 'MCScaleGain1EB', 'MCScaleGain6EB', 'MCScaleHighR9EB', 'MCScaleHighR9EE', 'MCScaleLowR9EB', 'MCScaleLowR9EE', 'MCSmearHighR9EBPhi', 'MCSmearHighR9EBRho', 'MCSmearHighR9EEPhi', 'MCSmearHighR9EERho', 'MCSmearLowR9EBPhi', 'MCSmearLowR9EBRho', 'MCSmearLowR9EEPhi', 'MCSmearLowR9EERho', 'MaterialCentralBarrel', 'MaterialForward', 'MaterialOuterBarrel', 'MvaShift', 'PUJIDShift', 'ShowerShapeHighR9EB', 'ShowerShapeHighR9EE', 'ShowerShapeLowR9EB', 'ShowerShapeLowR9EE', 'SigmaEOverEShift', 'metJecUncertainty', 'metJerUncertainty', 'metPhoUncertainty', 'metUncUncertainty'] 

# Variable to add to dataframe from systematic trees
syst_var = ["CMS_hgg_mass","weight","stage1p2bin"]

cats = ['RECO_0J_PTH_0_10_Tag0', 'RECO_0J_PTH_0_10_Tag1', 'RECO_0J_PTH_0_10_Tag2', 'RECO_0J_PTH_GT10_Tag0', 'RECO_0J_PTH_GT10_Tag1', 'RECO_0J_PTH_GT10_Tag2', 'RECO_1J_PTH_0_60_Tag0', 'RECO_1J_PTH_0_60_Tag1', 'RECO_1J_PTH_0_60_Tag2', 'RECO_1J_PTH_120_200_Tag0', 'RECO_1J_PTH_120_200_Tag1', 'RECO_1J_PTH_120_200_Tag2', 'RECO_1J_PTH_60_120_Tag0', 'RECO_1J_PTH_60_120_Tag1', 'RECO_1J_PTH_60_120_Tag2', 'RECO_GE2J_PTH_0_60_Tag0', 'RECO_GE2J_PTH_0_60_Tag1', 'RECO_GE2J_PTH_0_60_Tag2', 'RECO_GE2J_PTH_120_200_Tag0', 'RECO_GE2J_PTH_120_200_Tag1', 'RECO_GE2J_PTH_120_200_Tag2', 'RECO_GE2J_PTH_60_120_Tag0', 'RECO_GE2J_PTH_60_120_Tag1', 'RECO_GE2J_PTH_60_120_Tag2', 'RECO_PTH_200_300_Tag0', 'RECO_PTH_200_300_Tag1', 'RECO_PTH_300_450_Tag0', 'RECO_PTH_300_450_Tag1', 'RECO_PTH_450_650_Tag0', 'RECO_PTH_GT650_Tag0', 'RECO_THQ_LEP', 'RECO_TTH_HAD_PTH_0_60_Tag0', 'RECO_TTH_HAD_PTH_0_60_Tag1', 'RECO_TTH_HAD_PTH_0_60_Tag2', 'RECO_TTH_HAD_PTH_0_60_Tag3', 'RECO_TTH_HAD_PTH_120_200_Tag0', 'RECO_TTH_HAD_PTH_120_200_Tag1', 'RECO_TTH_HAD_PTH_120_200_Tag2', 'RECO_TTH_HAD_PTH_120_200_Tag3', 'RECO_TTH_HAD_PTH_60_120_Tag0', 'RECO_TTH_HAD_PTH_60_120_Tag1', 'RECO_TTH_HAD_PTH_60_120_Tag2', 'RECO_TTH_HAD_PTH_60_120_Tag3', 'RECO_TTH_HAD_PTH_GT200_Tag0', 'RECO_TTH_HAD_PTH_GT200_Tag1', 'RECO_TTH_HAD_PTH_GT200_Tag2', 'RECO_TTH_HAD_PTH_GT200_Tag3', 'RECO_TTH_LEP_PTH_0_60_Tag0', 'RECO_TTH_LEP_PTH_0_60_Tag1', 'RECO_TTH_LEP_PTH_0_60_Tag2', 'RECO_TTH_LEP_PTH_0_60_Tag3', 'RECO_TTH_LEP_PTH_120_200_Tag0', 'RECO_TTH_LEP_PTH_120_200_Tag1', 'RECO_TTH_LEP_PTH_60_120_Tag0', 'RECO_TTH_LEP_PTH_60_120_Tag1', 'RECO_TTH_LEP_PTH_GT200_Tag0', 'RECO_TTH_LEP_PTH_GT200_Tag1', 'RECO_VBFLIKEGGH_Tag0', 'RECO_VBFLIKEGGH_Tag1', 'RECO_VBFTOPO_BSM_Tag0', 'RECO_VBFTOPO_BSM_Tag1', 'RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag0', 'RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag1', 'RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag0', 'RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag1', 'RECO_VBFTOPO_JET3_HIGHMJJ_Tag0', 'RECO_VBFTOPO_JET3_HIGHMJJ_Tag1', 'RECO_VBFTOPO_JET3_LOWMJJ_Tag0', 'RECO_VBFTOPO_JET3_LOWMJJ_Tag1', 'RECO_VBFTOPO_VHHAD_Tag0', 'RECO_VBFTOPO_VHHAD_Tag1', 'RECO_VH_MET_Tag0', 'RECO_VH_MET_Tag1', 'RECO_WH_LEP_HIGH_Tag0', 'RECO_WH_LEP_HIGH_Tag1', 'RECO_WH_LEP_HIGH_Tag2', 'RECO_WH_LEP_LOW_Tag0', 'RECO_WH_LEP_LOW_Tag1', 'RECO_WH_LEP_LOW_Tag2', 'RECO_ZH_LEP_Tag0', 'RECO_ZH_LEP_Tag1', 'NOTAG'] 
#cats = ['RECO_0J_PTH_0_10_Tag0', 'NOTAG', 'RECO_THQ_LEP']

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
   
def get_options():
  parser = OptionParser()
  parser.add_option('--inputTreeFile',dest='inputTreeFile', default="/vols/cms/jl2117/hgg/ws/Feb20/trees/output_1.root", help='Input tree file')
  parser.add_option('--inputTreeDir',dest='inputTreeDir', default="tagsDumper/trees", help='Input tree file')
  parser.add_option('--inputMass',dest='inputMass', default="125", help='Input mass')
  parser.add_option('--productionMode',dest='productionMode', default="ggh", help='Production mode [ggh,vbf,wh,zh,tth,thq,ggzh,bbh]')
  parser.add_option('--year',dest='year', default="2016", help='Year')
  parser.add_option('--decayExt',dest='decayExt', default='', help='Decay extension')
  return parser.parse_args()
(opt,args) = get_options()

# Add HEM to shape systs if year = 2018
if opt.year == '2018': shapeSysts.append('JetHEM')

# Checks
if opt.productionMode not in ['ggh','vbf','wh','zh','tth','thq','thw','ggzh','bbh']: 
  print " --> [ERROR] Production mode (%s) not valid"%opt.productionMode
  sys.exit(1)

# Uproot file:
f = uproot.open(opt.inputTreeFile)
# Extract id from input file
f_id = re.sub(".root","",opt.inputTreeFile.split("_")[-1])
# Extract file handle for output file
f_out_name = "_".join(opt.inputTreeFile.split("/")[-1].split("_")[:-1])

# Dataframe to store all events in file
data = pandas.DataFrame()

# Extract events: loop over events
for cat in cats:
  print " --> [VERBOSE] Extracting events from category: %s"%cat
  treeName = "%s/%s_%s_13TeV_%s"%(opt.inputTreeDir,opt.productionMode,opt.inputMass,cat)
  # Extract tree from uproot
  t = f[treeName]
  if len(t) == 0: continue

  # Convert tree to pandas dataFrame: treat NOTAG differently as different variables
  if cat == "NOTAG":
    dfs_tomerge = {}
    # No theory weights for bbh, thw and thq therefore skip
    if opt.productionMode not in  ["bbh","thw","thq"]:
      for ac, acNames in columns.iteritems(): 
        dfs_tomerge[ac] = t.pandas.df(ac)
        dfs_tomerge[ac].columns = acNames
    # Add notag vars to dataframe
    dfs_tomerge['main'] = t.pandas.df(main_var_notag) 
    # Merge all columns
    df = pandas.concat( dfs_tomerge.values(), axis=1)
    # Add column to specify untagged 
    df['type'] = 'notag'
    # Add dummy columns for centralObjectWeight, dZ and NNLOPs
    df['dZ'] = -1.
    df['centralObjectWeight'] = df.apply(lambda x: 0.5*(x['THU_ggH_qmtopUp01sigma']+x['THU_ggH_qmtopDown01sigma']), axis=1)
    df['NNLOPSweight'] = df.apply(lambda x: 0.5*(x['THU_ggH_qmtopUp01sigma']+x['THU_ggH_qmtopDown01sigma']), axis=1)
  else:
    dfs_tomerge = {}
    # No theory weights for bbh, thw and thq therefore skip
    if opt.productionMode not in  ["bbh","thw","thq"]:
      for ac, acNames in columns.iteritems(): 
	dfs_tomerge[ac] = t.pandas.df(ac)
	dfs_tomerge[ac].columns = acNames
    if opt.productionMode == "ggh": dfs_tomerge['main'] = t.pandas.df(main_var_nnlops)
    else: dfs_tomerge['main'] = t.pandas.df(main_var)
    # Merge all columns
    df = pandas.concat( dfs_tomerge.values(), axis=1)
    # Add column to specify "nominal"
    df['type'] = 'nominal'
    # If not ggH then add column for NNLOPS weight = 1
    if opt.productionMode != "ggh": df['NNLOPSweight'] = 1.

    # For tagged events: loop over shape systematic variations and extract dataframes with reduced variables
    print " --> [VERBOSE] Systematics from category: %s"%cat
    for s in shapeSysts:
      for direction in ['Up','Down']:
	sTreeName = "%s_%s%s01sigma"%(treeName,s,direction)
        # If YEAR in sTreeName then change to year being processes
	sTreeName = re.sub("YEAR",opt.year,sTreeName)
	st = f[sTreeName]
	sdf = st.pandas.df(syst_var)
	sdf['type'] = "%s%s"%(s,direction)
	# Add dataFrame to total dataFrame
	df = pandas.concat([df,sdf], ignore_index=True, axis=0, sort=False)

  # Add column to dataframe specifying category
  df['cat'] = cat

  # Add to overall dataFrame
  data = pandas.concat([data,df], ignore_index=True, axis=0, sort=False)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Split up dataframe into separate dataframes for each STXS stage 1.2 bin
print " --> [VERBOSE] Splitting up dataframes and saving as pickle files"

for b in data.stage1p2bin.unique():
  stxsBin = stxs_stage1p2_dict[int(b)]
  mask = (data['stage1p2bin']==b)
  # Deal with decay strings for ggzh
  if opt.productionMode == 'ggzh':
    if opt.decayExt == '_ZToQQ': stxsBin = re.sub("GG2H","GG2HQQ",stxsBin)
    elif opt.decayExt == '_ZToNuNu': stxsBin = re.sub("GG2HLL","GG2HNUNU",stxsBin)
  # Convert tHq and tHW to separate bins
  elif opt.productionMode == 'thq': stxsBin = re.sub("TH","THQ",stxsBin)
  elif opt.productionMode == 'thw': stxsBin = re.sub("TH","THW",stxsBin)
  outputPickleDir = "/".join(opt.inputTreeFile.split("/")[:-1])+"/pickle_%s_%s"%(opt.productionMode,stxsBin)
  if not os.path.exists(outputPickleDir): os.system("mkdir %s"%outputPickleDir)
  outputPickleFile = "%s/%s_%s_%s.pkl"%(outputPickleDir,f_out_name,stxsBin,f_id)
  with open( outputPickleFile, "wb") as fout: pickle.dump( data[mask], fout )
  print " --> [VERBOSE] Written %s to file: %s"%(stxsBin,outputPickleFile)
  



