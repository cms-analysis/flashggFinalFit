# Config file: options for signal fitting
#prova
_year = '2016'

signalScriptCfg = {
  
    # Setup
    'procs':'auto', # if auto: inferred automatically from filenames
    'inputWSDir':'/afs/cern.ch/user/f/fderiggi/CMSSW_10_4_0/src/CMGTools/TTHAnalysis/python/plotter/cards/cards_fithgg/ROOT_ALT_%s' % _year,
    'cats':'auto', # if auto: inferred automatically from (0) workspace
    'ext':'2022-05-12_year%s'%_year,
    'analysis':'AC', # To specify which replacement dataset mapping (defined in ./python/replacementMap.py)
    'year':'%s'%_year, # Use 'combined' if merging all years: not recommended
    'massPoints':'120,125,130',
    'xvar': 'dipho_mass',
    'outdir': 'plots',

    #Photon shape systematics  
    'scales':'HighR9EB,HighR9EE,LowR9EB,LowR9EE,Gain1EB,Gain6EB', # separate nuisance per year
    'scalesCorr':'MaterialCentralBarrel,MaterialOuterBarrel,MaterialForward,FNUFEE,FNUFEB,ShowerShapeHighR9EE,ShowerShapeHighR9EB,ShowerShapeLowR9EE,ShowerShapeLowR9EB', # correlated across years
    'scalesGlobal':'NonLinearity,Geant4', # affect all processes equally, correlated across years
    'smears':'HighR9EBPhi,HighR9EBRho,HighR9EEPhi,HighR9EERho,LowR9EBPhi,LowR9EBRho,LowR9EEPhi,LowR9EERho', # separate nuisance per year
    
    # Job submission options
    'batch':'condor', # ['condor','SGE','IC','local']
    'queue':'espresso'
    
}





