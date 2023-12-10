# Config file: options for signal fitting

signalScriptCfg = {
  
  # Setup
  #'inputWSDir':'/home/hep/mdk16/PhD/ggtt/CMSSW_10_2_0/src/HHToGGTT/output_trees/ws/signal_%s'%_year,
  #'inputWSDir':'/home/hep/mdk16/PhD/ggtt/ParamNN/outputTrees/ws/signal_%s'%_year,
  'inputWSDir':'<trees/year/m/ws/signal_year>',
  'procs':'auto', # if auto: inferred automatically from filenames
  'cats':'auto', # if auto: inferred automatically from (0) workspace
  'ext':'ggtt_resonant_<m>',
  'analysis':'ggtt_resonant_<m>', # To specify which replacement dataset mapping (defined in ./python/replacementMap.py)
  'year':'<year>', # Use 'combined' if merging all years: not recommended
  'massPoints':'<mh>',

  #Photon shape systematics  
  'scales':'',
  'scalesCorr':'',
  'scalesGlobal':'',
  'smears':'',

  # Job submission options
  'batch':'IC', # ['condor','SGE','IC','local']
  'queue':'hep.q'
  #'batch':'condor', # ['condor','SGE','IC','local']
  #'queue':'espresso',

}
