# Config file: options for signal fitting

_year = '2016'

signalScriptCfg = {

    # Setup
    'inputWSDir':'cards/cards_current/signal_%s'%_year,
    'procs':'auto', # if auto: inferred automatically from filenames
    'cats':'auto', # if auto: inferred automatically from (0) workspace
    'ext':'2022-07-12_year%s'%_year,
    'analysis':'AC', # To specify which replacement dataset mapping (defined in ./python/replacementMap.py)
    'year':'%s'%_year, # Use 'combined' if merging all years: not recommended
    'massPoints':'120,125,130',
    'xvar': 'CMS_hgg_mass',
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
