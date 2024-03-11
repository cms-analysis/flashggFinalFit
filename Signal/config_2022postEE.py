# Config file: options for signal fitting
signalScriptCfg = {
  
  # Setup
  'inputWSDir':'../input_output_2022postEE/ws_signal/', # dir storing flashgg workspaces
  #'inputWSDir':'/net/scratch_cms3a/spaeh/private/PhD/analyses/early_Run3_Hgg/fitting/CMSSW_10_2_13/src/flashggFinalFit/input_output_freeze/ws_signal/',
  'procs':'auto', # if auto: inferred automatically from filenames (requires names to be of from *pythia8_{PROC}.root)
  'cats':'auto', # if auto: inferred automatically from (0) workspace
  #'ext':'earlyAnalysis_freeze_include', # output directory extension
  'ext':'earlyAnalysis_2022postEE', # output directory extension
  'analysis':'earlyAnalysisInOut', # To specify replacement dataset and XS*BR mapping (defined in ./tools/replacementMap.py and ./tools/XSBRMap.py respectively)
  'year':'2022postEE', # Use 'combined' if merging all years: not recommended
  'massPoints':'120,125,130', # You can now run with a single mass point if necessary

  #Photon shape systematics  
  'scales':'scale', # separate nuisance per year
  'scalesCorr':'', # correlated across years
  'scalesGlobal':'', # affect all processes equally, correlated across years
  'smears':'smearing', # separate nuisance per year

  # Job submission options
  'batch':'condor',  # ['condor_lxplus','condor','SGE','IC','local']
  'queue':'microcentury' # use hep.q for IC
}