# Input config file for running trees2ws

trees2wsCfg = {

  # Variables to be added to dataframe: use wildcard * for common strings
  'mainVars':["CMS_hgg_mass","weight","dZ"],
  'dataVars':["CMS_hgg_mass","weight"],
  'stxsVar':'',
  'notagVars':["weight"], # Vars to add to NOTAG RooDataset
  'systematicsVars':["CMS_hgg_mass","weight"], # Variables to add to sytematic RooDataHists
  'theoryWeightContainers':{},

  # List of systematics: use string YEAR for year-dependent systematics
  'systematics':[],

  # Analysis categories: python list of cats or use 'auto' to extract from input tree
  'cats':'auto'

}
