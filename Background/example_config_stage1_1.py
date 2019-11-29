# Config file: options for signal fitting

backgroundScriptCfg = {
  
  # Setup
  'inputWSDir':'/vols/cms/jl2117/hgg/ws/test_stage1_1_2018', 
  #Procs will be inferred automatically from filenames
  'cats':'RECO_0J_PTH_GT10_Tag0,RECO_0J_PTH_GT10_Tag1,RECO_0J_PTH_0_10_Tag0,RECO_0J_PTH_0_10_Tag1,RECO_PTH_GT200_Tag0,RECO_PTH_GT200_Tag1,RECO_1J_PTH_120_200_Tag0,RECO_1J_PTH_120_200_Tag1,RECO_1J_PTH_60_120_Tag0,RECO_1J_PTH_60_120_Tag1,RECO_1J_PTH_0_60_Tag0,RECO_1J_PTH_0_60_Tag1,RECO_VBFTOPO_BSM,RECO_VBFTOPO_JET3VETO_Tag0,RECO_VBFTOPO_JET3VETO_Tag1,RECO_VBFTOPO_JET3_Tag0,RECO_VBFTOPO_JET3_Tag1,RECO_GE2J_PTH_120_200_Tag0,RECO_GE2J_PTH_120_200_Tag1,RECO_GE2J_PTH_60_120_Tag0,RECO_GE2J_PTH_60_120_Tag1,RECO_GE2J_PTH_0_60_Tag0,RECO_GE2J_PTH_0_60_Tag1',
  'ext':'stage1_1_2018',
  'year':'2018', 
  'unblind':0,

  # Job submission options
  'batch':'HTCONDOR',
  'queue':'microcentury',

  # Mode allows script to carry out single function
  'mode':'std', # Options: [std,fTestOnly,bkgPlotsOnly]
  
}
