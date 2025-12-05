# Config file: options for signal fitting
signalScriptCfg = {
  
  # Setup
  'inputWSDir':'../input_output_Full_2024_Preliminary_16_10_25_2024/ws_signal/', # dir storing flashgg workspaces
  'procs':'auto', # if auto: inferred automatically from filenames (requires names to be of from *pythia8_{PROC}.root)
  'cats':'auto', # if auto: inferred automatically from (0) workspace
  #'ext':'earlyAnalysis_freeze_include', # output directory extension
  'ext':'partialAnalysis_Full_2024_Preliminary_16_10_25_2024', # output directory extension
  'analysis':'earlyAnalysisInOut', # To specify replacement dataset and XS*BR mapping (defined in ./tools/replacementMap.py and ./tools/XSBRMap.py respectively)
  'year':'2024', # Use 'combined' if merging all years: not recommended
  'massPoints':'120,125,130', # You can now run with a single mass point if necessary

  #Photon shape systematics  
  'scales':'ScaleEB,ScaleEE', # separate nuisance per year
  'scalesCorr':'FNUF,Material', # correlated across years
  #'scalesGlobal':'NonLinearity,Geant4', # affect all processes equally, correlated across years
  # Removed nonLinearity for HIG-23-014 
  'scalesGlobal':'Geant4', # affect all processes equally, correlated across years
  'smears':'Smearing', # separate nuisance per year

  # Job submission options
  'batch':'condor', # ['condor_lxplus','condor','SGE','IC','local']
  'queue':'microcentury' # use hep.q for IC
}