# Config file: options for signal fitting

backgroundScriptCfg = {
  
  # Setup
  'inputWS':"/eos/cms/store/group/phys_higgs/cmshgg/Run3HggSTXS_working/IA_nov2025/IA_corrected_5dec/data/ws_data/allData_data.root", # location of 'allData.root' file
  'cats':'auto', # auto: automatically inferred from input ws
  'catOffset':0, # add offset to category numbers (useful for categories from different allData.root files)  
  'ext':'STXS_12', # extension to add to output directory
  'year':'combined', # Use combined when merging all years in category (for plots)

  # Job submission options
  'batch':'condor', # [condor,SGE,IC,local]
  'queue':'espresso' # for condor e.g. microcentury
  
}
