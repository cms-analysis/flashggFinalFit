# Config file: options for signal fitting

backgroundScriptCfg = {
  
  # Setup
  'inputWSDir':'/vols/cms/es811/FinalFits/ws_ReweighAndNewggHweights', 
  #Procs will be inferred automatically from filenames
  'cats':'UntaggedTag_0,VBFTag_0',
  'ext':'test_hig16040',
  'year':'2016', 
  'unblind':0,

  # Job submission options
  'batch':'IC',
  'queue':'hep.q',

  # Mode allows script to carry out single function
  'mode':'std', # Options: [std,fTestOnly,bkgPlotsOnly]
  'printOnly':0 # For dry-run: print command only
  
}
