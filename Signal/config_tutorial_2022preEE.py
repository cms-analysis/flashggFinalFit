# Config file: options for signal fitting

_year = '2022preEE'

signalScriptCfg = {
  
  # Setup
  'inputWSDir':'PATH_TO_INPUTS/workspaces/signal_%s'%_year,
  'procs':'auto', # if auto: inferred automatically from filenames
  'cats':'auto', # if auto: inferred automatically from (0) workspace
  'ext':'tutorial_%s'%_year,
  'analysisRM': 'tutorial' # To specify replacement dataset (defined in ./commonTools/replacementMap.py)
  'analysisXSBR': 'tutorial' # To specify XSBR dataset (defined in ./commonTools/XSBRMap.py)
  'year':'%s'%_year, # Use 'combined' if merging all years: not recommended
  'massPoints':'120,125,130',

  #Photon shape systematics  
  'scales':'Scale', # separate nuisance per year
  'scalesCorr':'', # correlated across years
  'scalesGlobal':'', # affect all processes equally, correlated across years
  'smears':'Smearing', # separate nuisance per year

  # Job submission options
  'batch':'condor', # ['condor','SGE','IC','local']
  'queue':'espresso',

}
