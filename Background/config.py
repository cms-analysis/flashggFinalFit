# Config file: options for signal fitting

backgroundScriptCfg = {
  
  # Setup
  #'inputWSDir':'/home/hep/mdk16/PhD/ggtt/CMSSW_10_2_0/src/HHToGGTT/output_trees/ws/data_2018/', # location of 'allData.root' file
  #'inputWSDir':'/home/hep/mdk16/PhD/ggtt/ParamNN/outputTrees/ws/data_2018/',
  'inputWSFile':'/home/hep/mdk16/PhD/ggtt/ResonantGGTT/tagging_output/radionM500_HHggTauTau/outputTrees/2018/500/ws/data_2018/allData.root',
  'cats':'auto', # auto: automatically inferred from input ws
  'ext':'ggtt_resonant_500', # extension to add to output directory
  'year':'2018', # Use combined when merging all years in category (for plots)

  # Job submission options
  'batch':'local', # [condor,SGE,IC,local]
  'queue':'hep.q' # for condor e.g. microcentury
  
}
