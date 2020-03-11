# Config file: options for combine fitting

import sys 

mode = sys.argv[1] # datacard or combine 
print'mode: ',mode 

combineScriptCfg = {
  
  # Setup
  'analysis':'HHWWgg',
  'mode':mode,
  # 'mode':'combine',
  'inputWSDir':'/eos/user/a/atishelm/ntuples/HHWWgg/HHWWgg_v2-3_Workspaces_AllEvents_Hadded', # all files 
  # 'inputWSDir':'/eos/user/a/atishelm/ntuples/HHWWgg/HHWWgg_v2-3_Workspaces_AllEvents_Hadded_Shorter', # less files for testing 
  #Procs will be inferred automatically from filenames
  'cats':'HHWWggTag_0',
  'ext':'HHWWgg_v2-3_2017',
  'year':'2017', 
  'signalProcs':'ggF',

  # Add UE/PS systematics to datacard (only relevant if mode == datacard)
  'doUEPS':0,

  #Photon shape systematics  
  'scales':'HighR9EB,HighR9EE,LowR9EB,LowR9EE,Gain1EB,Gain6EB',
  'scalesCorr':'MaterialCentralBarrel,MaterialOuterBarrel,MaterialForward,FNUFEE,FNUFEB,ShowerShapeHighR9EE,ShowerShapeHighR9EB,ShowerShapeLowR9EE,ShowerShapeLowR9EB',
  'scalesGlobal':'NonLinearity:UntaggedTag_0:2,Geant4',
  'smears':'HighR9EBPhi,HighR9EBRho,HighR9EEPhi,HighR9EERho,LowR9EBPhi,LowR9EBRho,LowR9EEPhi,LowR9EERho',

  # Job submission options
  # 'batch':'HTCONDOR',
  # 'queue':'workday',

  'batch':'',
  'queue':'',

  'printOnly':0 # For dry-run: print command only
  
}
