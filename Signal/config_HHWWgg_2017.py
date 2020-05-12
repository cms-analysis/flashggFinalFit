# Config file: options for signal fitting

_year = '2017'

signalScriptCfg = {
  
  # Setup
  'systematics':0, # (0): Use empty systematics dat file. (1): Use generated systematics dat file 

  'inputWSDir':'/eos/user/a/atishelm/ntuples/HHWWgg/HHWWgg_v2-3_Workspaces_AllEvents_Hadded_X250Only',
  # 'inputWSDir':'/eos/user/a/atishelm/ntuples/HHWWgg/HHWWgg_v2-3_1TotalCategory_Hadded',
  
  # 'inputWSDir':'/eos/user/a/atishelm/ntuples/HHWWgg/HHWWgg_v2-3_Workspaces_AllEvents_Hadded_Shorter',
  'usrprocs':'ggF', # if you want user input production categories 
  #Procs will be inferred automatically from filenames
  #'cats':'RECO_0J_PTH_0_10_Tag0,RECO_0J_PTH_0_10_Tag1,RECO_0J_PTH_GT10_Tag0,RECO_0J_PTH_GT10_Tag1,RECO_1J_PTH_0_60_Tag0,RECO_1J_PTH_0_60_Tag1,RECO_1J_PTH_120_200_Tag0,RECO_1J_PTH_120_200_Tag1,RECO_1J_PTH_60_120_Tag0,RECO_1J_PTH_60_120_Tag1,RECO_GE2J_PTH_0_60_Tag0,RECO_GE2J_PTH_0_60_Tag1,RECO_GE2J_PTH_120_200_Tag0,RECO_GE2J_PTH_120_200_Tag1,RECO_GE2J_PTH_60_120_Tag0,RECO_GE2J_PTH_60_120_Tag1,RECO_PTH_200_300,RECO_PTH_300_450,RECO_PTH_450_650,RECO_PTH_GT650,RECO_THQ_LEP,RECO_TTH_HAD_HIGH_Tag0,RECO_TTH_HAD_HIGH_Tag1,RECO_TTH_HAD_HIGH_Tag2,RECO_TTH_HAD_HIGH_Tag3,RECO_TTH_HAD_LOW_Tag0,RECO_TTH_HAD_LOW_Tag1,RECO_TTH_HAD_LOW_Tag2,RECO_TTH_HAD_LOW_Tag3,RECO_TTH_LEP_HIGH_Tag0,RECO_TTH_LEP_HIGH_Tag1,RECO_TTH_LEP_HIGH_Tag2,RECO_TTH_LEP_HIGH_Tag3,RECO_TTH_LEP_LOW_Tag0,RECO_TTH_LEP_LOW_Tag1,RECO_TTH_LEP_LOW_Tag2,RECO_TTH_LEP_LOW_Tag3,RECO_VBFLIKEGGH_Tag0,RECO_VBFLIKEGGH_Tag1,RECO_VBFTOPO_BSM_Tag0,RECO_VBFTOPO_BSM_Tag1,RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag0,RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag1,RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag0,RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag1,RECO_VBFTOPO_JET3_HIGHMJJ_Tag0,RECO_VBFTOPO_JET3_HIGHMJJ_Tag1,RECO_VBFTOPO_JET3_LOWMJJ_Tag0,RECO_VBFTOPO_JET3_LOWMJJ_Tag1,RECO_VBFTOPO_VHHAD_Tag0,RECO_VBFTOPO_VHHAD_Tag1,RECO_WH_LEP_HIGH_Tag0,RECO_WH_LEP_HIGH_Tag1,RECO_WH_LEP_HIGH_Tag2,RECO_WH_LEP_LOW_Tag0,RECO_WH_LEP_LOW_Tag1,RECO_WH_LEP_LOW_Tag2,RECO_ZH_LEP',
  'cats':'HHWWggTag_0',
  #'cats':'RECO_0J_PTH_0_10_Tag0',
  'ext':'HHWWgg_v2-3_%s_1TotCatX250Only'%_year,
  # 'analysis':'stage1_2', # To specify which replacement dataset mapping (defined in ./python/replacementMap.py)
  'analysis':'HHWWgg', # To specify which replacement dataset mapping (defined in ./python/replacementMap.py)
  'year':'%s'%_year, 
  'beamspot':'3.4',
  'numberOfBins':'320',
  'massPoints':'120,125,130',

  # Use DCB in fit
  'useDCB':0,

  #Photon shape systematics  
  'scales':'HighR9EB,HighR9EE,LowR9EB,LowR9EE,Gain1EB,Gain6EB',
  'scalesCorr':'MaterialCentralBarrel,MaterialOuterBarrel,MaterialForward,FNUFEE,FNUFEB,ShowerShapeHighR9EE,ShowerShapeHighR9EB,ShowerShapeLowR9EE,ShowerShapeLowR9EB',
  'scalesGlobal':'NonLinearity:UntaggedTag_0:2,Geant4',
  'smears':'HighR9EBPhi,HighR9EBRho,HighR9EEPhi,HighR9EERho,LowR9EBPhi,LowR9EBRho,LowR9EEPhi,LowR9EERho',

  # Job submission options
  # 'batch':'IC',
  # 'queue':'hep.q',

  # 'batch':'HTCONDOR',
  # 'queue':'espresso',

  'batch':'', # If you want to run locally just leave these empty 
  'queue':'',

  # 'runLocal':'1',

  # Mode allows script to carry out single function
  # 'mode':'std', # Options: [std,calcPhotonSyst,writePhotonSyst,sigFitOnly,packageOnly,sigPlotsOnly]
  'mode':'sigPlotsOnly', # Options: [std,calcPhotonSyst,writePhotonSyst,sigFitOnly,packageOnly,sigPlotsOnly]
  ##-- Steps to run: 
  # No systematics: std, sigFitOnly, packageOnly, sigPlotsOnly
  # With systematics: std, std 
  'verbosity':'0',

}
