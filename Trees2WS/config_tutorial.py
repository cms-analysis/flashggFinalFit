# Input config file for running trees2ws

trees2wsCfg = {

  # Name of RooDirectory storing input tree
  'inputTreeDir':'tagsDumper',

  # Variables to be added to dataframe: use wildcard * for common strings
  'mainVars':["CMS_hgg_mass","weight","dZ",'weight_TriggerSFUp', 'weight_PreselSFDown',
       'weight_AlphaSUp', 'weight_PileupDown', 'weight_ElectronVetoSFDown',
       'weight_SF_photon_IDUp', 'weight_PS_ISRUp', 'weight_SF_photon_IDDown',
       'weight_PS_FSRUp', 'weight_ElectronVetoSFUp', 'weight_AlphaSDown',
        'weight_PS_ISRDown', 'weight_TriggerSFDown',
       'weight_PreselSFUp', 'weight_PS_FSRDown', 
       'weight_LHEPdfUp','weight_LHEPdfDown' ,'weight_PileupUp', 'weight_LHEScaleUp','weight_LHEScaleDown'],#,"weight_*"], # Var for the nominal RooDataSets
  'dataVars':["CMS_hgg_mass","weight"], # Vars to be added for data
  'stxsVar':'',
  'systematicsVars':["CMS_hgg_mass","weight"], # Variables to add to sytematic RooDataHists
  'theoryWeightContainers':{},

  # List of systematics: use string YEAR for year-dependent systematics
  # 'systematics':["Scale","Smearing"],
  'systematics': ['energyErrShift',  'FNUF' , 'jec_syst_Total',  'Material' , 'ScaleEB2G_IJazZ'  ,'ScaleEE2G_IJazZ'  ,'Smearing2G_IJazZ'],#['SDummy'],

  # Analysis categories: python list of cats or use 'auto' to extract from input tree
  'cats':'auto'

}
