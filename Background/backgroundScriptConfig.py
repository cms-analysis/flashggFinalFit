# Config file: options for signal fitting

backgroundScriptCfg = {
  
  # Setup
  'inputWSDir':'/eos/home-j/jlangfor/hgg/ws/test_stage1_legacy', 
  #Procs will be inferred automatically from filenames
  'cats':'RECO_0J_Tag0,RECO_0J_Tag1,RECO_0J_Tag2,RECO_VBFTOPO_JET3VETO_Tag0',
  'ext':'test_stage1_2017',
  'year':'2017', 
  'unblind':0,

  # Job submission options
  'batch':'HTCONDOR',
  'queue':'espresso',

  # Mode allows script to carry out single function
  'mode':'std', # Options: [std,fTestOnly,bkgPlotsOnly]
  
}
