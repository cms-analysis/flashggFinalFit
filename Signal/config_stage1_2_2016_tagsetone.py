# Config file: options for signal fitting

_year = '2016'

signalScriptCfg = {
  
  # Setup
  'inputWSDir':'/vols/cms/jl2117/hgg/ws/Feb20_unblinding/stage1_2_%s/tagsetone'%_year, 
  #Procs will be inferred automatically from filenames
  #'cats':'RECO_0J_PTH_0_10_Tag0,RECO_0J_PTH_0_10_Tag1,RECO_0J_PTH_0_10_Tag2,RECO_0J_PTH_GT10_Tag0,RECO_0J_PTH_GT10_Tag1,RECO_0J_PTH_GT10_Tag2,RECO_1J_PTH_0_60_Tag0,RECO_1J_PTH_0_60_Tag1,RECO_1J_PTH_0_60_Tag2,RECO_1J_PTH_60_120_Tag0,RECO_1J_PTH_60_120_Tag1,RECO_1J_PTH_60_120_Tag2,RECO_1J_PTH_120_200_Tag0,RECO_1J_PTH_120_200_Tag1,RECO_1J_PTH_120_200_Tag2,RECO_GE2J_PTH_0_60_Tag0,RECO_GE2J_PTH_0_60_Tag1,RECO_GE2J_PTH_0_60_Tag2,RECO_GE2J_PTH_60_120_Tag0,RECO_GE2J_PTH_60_120_Tag1,RECO_GE2J_PTH_60_120_Tag2,RECO_GE2J_PTH_120_200_Tag0,RECO_GE2J_PTH_120_200_Tag1,RECO_GE2J_PTH_120_200_Tag2',
  #'cats':'RECO_PTH_200_300_Tag0,RECO_PTH_200_300_Tag1,RECO_PTH_300_450_Tag0,RECO_PTH_300_450_Tag1,RECO_PTH_450_650_Tag0,RECO_PTH_450_650_Tag1,RECO_PTH_GT650_Tag0,RECO_PTH_GT650_Tag1,RECO_VBFTOPO_VHHAD_Tag0,RECO_VBFTOPO_VHHAD_Tag1,RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag0,RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag1,RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag0,RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag1,RECO_VBFTOPO_JET3_LOWMJJ_Tag0,RECO_VBFTOPO_JET3_LOWMJJ_Tag1,RECO_VBFTOPO_JET3_HIGHMJJ_Tag0,RECO_VBFTOPO_JET3_HIGHMJJ_Tag1,RECO_VBFTOPO_BSM_Tag0,RECO_VBFTOPO_BSM_Tag1,RECO_VBFLIKEGGH_Tag0,RECO_VBFLIKEGGH_Tag1',
  #'cats':'RECO_TTH_HAD_LOW_Tag0,RECO_TTH_HAD_LOW_Tag1,RECO_TTH_HAD_LOW_Tag2,RECO_TTH_HAD_LOW_Tag3,RECO_TTH_HAD_HIGH_Tag0,RECO_TTH_HAD_HIGH_Tag1,RECO_TTH_HAD_HIGH_Tag2,RECO_TTH_HAD_HIGH_Tag3,RECO_WH_LEP_LOW_Tag0,RECO_WH_LEP_LOW_Tag1,RECO_WH_LEP_LOW_Tag2,RECO_WH_LEP_HIGH_Tag0,RECO_WH_LEP_HIGH_Tag1,RECO_WH_LEP_HIGH_Tag2,RECO_ZH_LEP_Tag0,RECO_ZH_LEP_Tag1,RECO_TTH_LEP_LOW_Tag0,RECO_TTH_LEP_LOW_Tag1,RECO_TTH_LEP_LOW_Tag2,RECO_TTH_LEP_LOW_Tag3,RECO_TTH_LEP_HIGH_Tag0,RECO_TTH_LEP_HIGH_Tag1,RECO_TTH_LEP_HIGH_Tag2,RECO_TTH_LEP_HIGH_Tag3,RECO_THQ_LEP',
  'cats':'RECO_0J_PTH_0_10_Tag0',
  'ext':'stage1_2_tagsetone_%s'%_year,
  'analysis':'stage1_2', # To specify which replacement dataset mapping (defined in ./python/replacementMap.py)
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
  'batch':'IC',
  'queue':'hep.q',

  # Mode allows script to carry out single function
  'mode':'sigFitOnly', # Options: [std,getFractions,sigFitOnly,sigFitOnly,sigFitOnly,packageOnly,sigPlotsOnly]
}
