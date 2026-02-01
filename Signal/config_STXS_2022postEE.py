# Config file: options for signal fitting

_year = 'postEE'

signalScriptCfg = {
  
  # Setup
  'inputWSDir':'/eos/user/p/pkrueper/HiggsDNA_and_FinalFits_tutorial24/FF_standalone/src/flashggFinalFit/Workspaces_2dec/signal/postEE',
  'procs':"auto", # if auto: inferred automatically from filenames
  'cats':'auto', # if auto: inferred automatically from (0) workspace
  'ext':'Run3STXS_%s'%_year,
  'analysis':"Run3STXS12",#'tutorial', # To specify which replacement dataset mapping (defined in ./python/replacementMap.py)
  'year':'%s'%_year, # Use 'combined' if merging all years: not recommended
  # tbc


  'massPoints':'125',

  #Photon shape systematics  
    'scales':'ScaleEB2G_IJazZ,ScaleEE2G_IJazZ', # separate nuisance per year
  'scalesCorr':'Material,FNUF', # correlated across years
  'scalesGlobal':'', # affect all processes equally, correlated across years
  'smears':'Smearing2G_IJazZ', # separate nuisance per year
  # Job submission options
  'batch':'condor', # ['condor','SGE','IC','local']
  'queue':'tomorrow', #workday for 8 hours, tomorrow for 24h

}