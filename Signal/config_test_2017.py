# Config file: options for signal fitting

_year = '2017'

signalScriptCfg = {
    # Setup
    'inputWSDir':'cards/cards_current/signal_%s'%_year,
    'procs':'GG2H,VBF,VBF_ALT0L1,VBF_ALT0L1f05ph0,VBF_ALT0L1Zg,VBF_ALT0L1Zgf05ph0,VBF_ALT0M,VBF_ALT0Mf05ph0,VBF_ALT0PH,VBF_ALT0PHf05ph0,VBF_ALT0PM,WH_WM,WH_WP,WH_ALT0L1f05ph0,WH_ALT0PH,WH_ALT0PHf05ph0,WH_ALT0PM,ZH_ALT0L1,ZH_ALT0L1f05ph0,ZH_ALT0L1Zg,ZH_ALT0L1Zgf05ph0,ZH_ALT0M,ZH_ALT0Mf05ph0,ZH_ALT0PH,ZH_ALT0PHf05ph0,ZH_ALT0PM,TTH,TTH_ALT0M,TTH_ALT0Mf05ph0,TTH_ALT0PM', # if auto: inferred automatically from filenames
    'cats':'VBFTag_1,VBFTag_3,VBFTag_5,VBFTag_6,VBFTag_7', # if auto: inferred automatically from (0) workspace
    'ext':'2022-10-28_year%s'%_year,
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
