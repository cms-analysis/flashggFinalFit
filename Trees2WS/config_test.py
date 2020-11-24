# Input config file for running trees2ws

trees2wsCfg = {

  # Name of RooDirectory storing input tree
  'inputTreeDir':'tagsDumper/trees',

  # Variables to be added to dataframe: use wildcard * for common strings
  'mainVars':["CMS_hgg_mass","weight","centralObjectWeight","dZ","*sigma"], # Vars to add to nominal RooDatasets
  'dataVars':["CMS_hgg_mass","weight"], # Vars for data workspace (trees2ws_data.py script)
  'stxsVar':'stage1p2bin', # Var for STXS splitting: if using option doSTXSSplitting
  'notagVars':["weight","*sigma"], # Vars to add to NOTAG RooDataset
  'systematicsVars':["CMS_hgg_mass","weight"], # Variables to add to sytematic RooDataHists
  'theoryWeightContainers':{'alphaSWeights':2,'scaleWeights':9,'pdfWeights':60}, # Theory weights to add to nominal + NOTAG RooDatasets, value corresponds to number of weights (0-N)

  # List of systematics: use string YEAR for year-dependent systematics
  'systematics':['FNUFEB', 'FNUFEE', 'JECAbsoluteYEAR', 'JECAbsolute', 'JECBBEC1YEAR', 'JECBBEC1', 'JECEC2YEAR', 'JECEC2', 'JECFlavorQCD', 'JECHFYEAR', 'JECHF', 'JECRelativeBal', 'JECRelativeSampleYEAR', 'JEC', 'JER', 'MCScaleGain1EB', 'MCScaleGain6EB', 'MCScaleHighR9EB', 'MCScaleHighR9EE', 'MCScaleLowR9EB', 'MCScaleLowR9EE', 'MCSmearHighR9EBPhi', 'MCSmearHighR9EBRho', 'MCSmearHighR9EEPhi', 'MCSmearHighR9EERho', 'MCSmearLowR9EBPhi', 'MCSmearLowR9EBRho', 'MCSmearLowR9EEPhi', 'MCSmearLowR9EERho', 'MaterialCentralBarrel', 'MaterialForward', 'MaterialOuterBarrel', 'MvaShift', 'PUJIDShift', 'ShowerShapeHighR9EB', 'ShowerShapeHighR9EE', 'ShowerShapeLowR9EB', 'ShowerShapeLowR9EE', 'SigmaEOverEShift', 'metJecUncertainty', 'metJerUncertainty', 'metPhoUncertainty', 'metUncUncertainty'],

  # Analysis categories: python list of cats or use 'auto' to extract from input tree
  'cats':'auto'

}
