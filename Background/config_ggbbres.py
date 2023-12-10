# Config file: options for signal fitting

backgroundScriptCfg = {
  
  # Setup
  'inputWSFile':'<trees/year/m/ws/signal_year>/allData.root',
  'cats':'auto', # auto: automatically inferred from input ws
  'ext':'<proc_template>_<signal_year>_<m>', # extension to add to output directory
  'year':'combined', # Use combined when merging all years in category (for plots)

  # Job submission options
  'batch':'local', # [condor,SGE,IC,local]
  'queue':'hep.q' # for condor e.g. microcentury
  
}
