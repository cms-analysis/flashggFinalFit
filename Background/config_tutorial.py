# Config file: options for signal fitting

backgroundScriptCfg = {
  
  # Setup
  'inputWS':'/eos/user/j/jlangfor/icrf/hgg/FinalFitsTutorial/higgsdna_finalfits_tutorial_24/inputs/workspaces/data/allData_2022preEE.root', # location of 'allData.root' file
  'cats':'auto', # auto: automatically inferred from input ws
  'catOffset':0, # add offset to category numbers (useful for categories from different allData.root files)  
  'ext':'tutorial', # extension to add to output directory
  'year':'combined', # Use combined when merging all years in category (for plots)

  # Job submission options
  'batch':'condor', # [condor,SGE,IC,local]
  'queue':'espresso' # for condor e.g. microcentury
  
}
