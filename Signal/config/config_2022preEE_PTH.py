# Config file: options for signal fitting
signalScriptCfg = {
  
  # Setup
  'inputWSDir':'../input_output_PTH_2022preEE/ws_signal/', # dir storing flashgg workspaces
  #'inputWSDir':'/net/scratch_cms3a/spaeh/private/PhD/analyses/early_Run3_Hgg/fitting/CMSSW_10_2_13/src/flashggFinalFit/input_output_freeze/ws_signal/',
  'procs':'auto', # if auto: inferred automatically from filenames (requires names to be of from *pythia8_{PROC}.root)
  'cats':'auto', # if auto: inferred automatically from (0) workspace
  #'ext':'Run3FidXSAnalysis_freeze_include', # output directory extension
  'ext':'Run3FidXSAnalysis_PTH_2022preEE', # output directory extension
  'analysisRM': 'Run3FidXSAnalysisPTH' # To specify replacement dataset (defined in ./commonTools/replacementMap.py)
  'analysisXSBR': 'Run3FidXSAnalysis' # To specify XSBR dataset (defined in ./commonTools/XSBRMap.py)
  'year':'2022preEE', # Use 'combined' if merging all years: not recommended
  'massPoints':'120,125,130', # You can now run with a single mass point if necessary

  #Photon shape systematics  
  'scales':'ScaleEE,ScaleEB', # separate nuisance per year
  'scalesCorr':'FNUF,Material', # correlated across years
  'scalesGlobal':'NonLinearity,Geant4', # affect all processes equally, correlated across years
  'smears':'Smearing', # separate nuisance per year

  # Job submission options
  'batch':'condor_lxplus', # ['condor_lxplus','condor','SGE','IC','local']
  'queue':'microcentury' # use hep.q for IC
}