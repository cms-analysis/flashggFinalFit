# Config file: options for combine fitting

combineScriptCfg = {
  
  # Setup
  'mode':'combine',
  'inputWSDir':'/vols/cms/es811/FinalFits/ws_ReweighAndNewggHweights', 
  #Procs will be inferred automatically from filenames
  'cats':'UntaggedTag_0,VBFTag_0',
  'ext':'test_hig16040',
  'year':'2016', 
  'signalProcs':'all',

  # Add UE/PS systematics to datacard (only relevant if mode == datacard)
  'doUEPS':0,

  #Photon shape systematics  
  'scales':'HighR9EB,HighR9EE,LowR9EB,LowR9EE,Gain1EB,Gain6EB',
  'scalesCorr':'MaterialCentralBarrel,MaterialOuterBarrel,MaterialForward,FNUFEE,FNUFEB,ShowerShapeHighR9EE,ShowerShapeHighR9EB,ShowerShapeLowR9EE,ShowerShapeLowR9EB',
  'scalesGlobal':'NonLinearity:UntaggedTag_0:2,Geant4',
  'smears':'HighR9EBPhi,HighR9EBRho,HighR9EEPhi,HighR9EERho,LowR9EBPhi,LowR9EBRho,LowR9EEPhi,LowR9EERho',

  # Job submission options
  'batch':'IC',
  'queue':'hep.q',

  'printOnly':0 # For dry-run: print command only
  
}
