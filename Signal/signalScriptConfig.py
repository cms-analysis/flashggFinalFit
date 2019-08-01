# Config file: options for signal fitting

signalScriptCfg = {
  
  # Setup
  'inputWSDir':'/vols/cms/es811/FinalFits/ws_ReweighAndNewggHweights', 
  #Procs will be inferred automatically from filenames
  'cats':'UntaggedTag_0,VBFTag_0',
  'ext':'test',
  'analysis':'test', # To specify which replacement dataset mapping i.e. when too few entries in proc x cat
  'year':'2016', 
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
  'mode':'sigFitOnly', # Options: [std,phoSystOnly,sigFitOnly,packageOnly,sigPlotsOnly]
  'printOnly':1 # For dry-run: print command only
  
}
