# Config file: options for signal fitting

backgroundScriptCfg = {
  
    # Setup
    'inputWSDir':'cards/cards_fithgg/2017', # location of 'allData.root' file
    'cats':'auto', # auto: automatically inferred from input ws
    'catOffset':0, # add offset to category numbers (useful for categories from different allData.root files)  
    'ext':'test1', # extension to add to output directory
    #'year':'combined', # Use combined when merging all years in category (for plots)
    'year': '2017',
    'xvar': 'dipho_mass', # not yet used, should be passed to the C++ macros
    'plotdir': 'plots',

    # Job submission options
    'batch':'condor', # [condor,SGE,IC,local]
    'queue':'espresso' # for condor e.g. espresso
  
}
