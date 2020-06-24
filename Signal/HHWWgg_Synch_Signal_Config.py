# Config file: options for signal fitting

_year = '2017'

signalScriptCfg = {
  
  # Setup
  'systematics':1, # (0): Use empty systematics dat file. (1): Use generated systematics dat file 
  'inputWSDir':'/eos/user/a/atishelm/ntuples/HHWWgg/HHWWgg_v2-6_Workspaces_X600_Synch_Hadded',
  'usrprocs':'ggF', # if you want user input production categories 
  # 'usrprocs':'GluGluToHHTo', # if you want user input production categories 
  #Procs will be inferred automatically from filenames
  'cats':'HHWWggTag_0,HHWWggTag_1',
  # 'ext':'HHWWgg_v2-3_%s_2CatsSyst'%_year,
  'ext':'HHWWgg_v2-6_%s_Synch'%_year,
  # 'analysis':'stage1_2', # To specify which replacement dataset mapping (defined in ./python/replacementMap.py)
  'analysis':'HHWWgg', # To specify which replacement dataset mapping (defined in ./python/replacementMap.py)
  # 'analysis_type':'EFT', # For HHWWgg: Res, EFT or NMSSM 
  'analysis_type':'Res', # For HHWWgg: Res, EFT or NMSSM 
  # 'analysis_type':'NMSSM', # For HHWWgg: Res, EFT or NMSSM 
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

  # Mode allows script to carry out single function
  'mode':'std', # Options: [std,calcPhotonSyst,writePhotonSyst,sigFitOnly,packageOnly,sigPlotsOnly]
  ##-- Steps to run: 
  # No systematics: std, sigFitOnly, packageOnly, sigPlotsOnly
  # With systematics: std, std 
  'verbosity':'0',

}
