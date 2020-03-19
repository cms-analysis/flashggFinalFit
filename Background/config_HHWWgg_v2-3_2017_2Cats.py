# Config file: options for signal fitting

backgroundScriptCfg = {
  
  # Setup
  'inputWSDir':'/eos/user/a/atishelm/ntuples/HHWWgg/HHWWgg_2017_Data_NoSyst_Hadded/final', 
  #Procs will be inferred automatically from filenames
  'cats':'HHWWggTag_0,HHWWggTag_1',
  'ext':'HHWWgg_v2-3_2017_2Cats',
  'year':'2017', 
  'unblind':0,

  # Job submission options
  'batch':'HTCONDOR',
  'queue':'espresso',

  'analysis':'HHWWgg',

  # Mode allows script to carry out single function
  'mode':'bkgPlotsOnly', # Options: [std,fTestOnly,bkgPlotsOnly]
  
}
