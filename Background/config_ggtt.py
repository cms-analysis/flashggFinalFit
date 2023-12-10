# Config file: options for signal fitting

backgroundScriptCfg = {
  
  # Setup
  #'inputWSDir':'/home/hep/mdk16/PhD/ggtt/CMSSW_10_2_0/src/HHToGGTT/output_trees/ws/data_2018/', # location of 'allData.root' file
  #'inputWSDir':'/home/hep/mdk16/PhD/ggtt/ParamNN/outputTrees/ws/data_2018/',
  'inputWSFile':'<trees/year/m/ws/signal_year>/allData.root',
  'cats':'auto', # auto: automatically inferred from input ws
  'ext':'ggtt_resonant_<m>', # extension to add to output directory
  'year':'combined', # Use combined when merging all years in category (for plots)

  # Job submission options
  'batch':'local', # [condor,SGE,IC,local]
  'queue':'hep.q' # for condor e.g. microcentury
  
}
