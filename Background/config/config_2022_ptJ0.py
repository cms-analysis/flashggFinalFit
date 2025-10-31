# Config file: options for signal fitting

backgroundScriptCfg = {
  
  # Setup
  'inputWS':'../input_output_data_ptJ0_2022/ws/allData.root', # location of 'allData.root' file
  'cats':'auto', # auto: automatically inferred from input ws
  'catOffset':0, # add offset to category numbers (useful for categories from different allData.root files)  
  'ext':'earlyAnalysis_ptJ0', # extension to add to output directory
  'year':'2022', # Use combined when merging all years in category (for plots)

  # Job submission options
  'batch':'condor_lxplus', # [condor,condor_lxplus,SGE,IC,local]
  'queue':'microcentury' # for condor e.g. microcentury
  
}
