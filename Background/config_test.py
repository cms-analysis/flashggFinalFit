# Config file: options for signal fitting

backgroundScriptCfg = {
  
    # Setup
    'inputWSDir':'data/data_all/ws/', # location of 'allData.root' file
    'cats':'auto', # auto: automatically inferred from input ws
    'catOffset':0, # add offset to category numbers (useful for categories from different allData.root files)  
    'ext':'2024-03-18', # extension to add to output directory
    'year':'combined', # Use combined when merging all years in category (for plots)
    'xvar': 'CMS_hgg_mass', # not yet used, should be passed to the C++ macros
    'plotdir': 'plots',

    # Job submission options
    'batch':'Rome', # [condor,SGE,IC,Rome,local]
    'queue':'cmsan' # for condor e.g. espresso
  
}
