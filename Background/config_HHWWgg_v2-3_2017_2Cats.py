# Config file: options for signal fitting

backgroundScriptCfg = {
  
  # Setup
  'inputWSDir':'/eos/user/a/atishelm/ntuples/HHWWgg/HHWWgg_2017_Data_WithSyst_Hadded/final', 
  #Procs will be inferred automatically from filenames
  'cats':'HHWWggTag_0,HHWWggTag_1',
  # 'ext':'HHWWgg_v2-3_2017_2CatsSyst',
  'ext':'HHWWgg_v2-4_2017_2CatsSyst',
  'year':'2017', 
  'unblind':0,

  # Job submission options
  'batch':'HTCONDOR',
  'queue':'espresso',

  'analysis':'HHWWgg',

  # Mode allows script to carry out single function
  'mode':'fTestOnly', # Options: [std,fTestOnly,bkgPlotsOnly]
  
}
