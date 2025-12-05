# Config file: options for signal fitting

backgroundScriptCfg = {
  
  # Setup
  'inputWS':'/net/data_cms3a-1/daumann/PhD/Final_fits_repo/CMSSW_14_1_0_pre4/src/flashggFinalFit/input_output_Full_2024_Preliminary_16_10_25_2024/ws/allData_2024_allRuns.root', # location of 'allData.root' file
  'cats':'auto', # auto: automatically inferred from input ws
  'catOffset':0, # add offset to category numbers (useful for categories from different allData.root files)  
  'ext':'partialAnalysis_Full_2024_Preliminary_16_10_25_2024', # extension to add to output directory
  'year':'2024', # Use combined when merging all years in category (for plots)

  # Job submission options
  'batch':'condor', # [condor,condor_lxplus,SGE,IC,local]
  'queue':'microcentury' # for condor e.g. microcentury
  
}
