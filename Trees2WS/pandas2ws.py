# Script to convert flashgg trees to RooWorkspace (compatible for finalFits)

print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG TREES 2 WS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
import os, sys
import re
from optparse import OptionParser
import ROOT
import pandas
from root_numpy import array2tree
import pickle

array_columns = {'alphaSWeights':2,'scaleWeights':9,'pdfWeights':60}

# List of shape systs to add as RooDataHists output workspace
shapeSysts = ['FNUFEB', 'FNUFEE', 'JECAbsoluteYEAR', 'JECAbsolute', 'JECBBEC1YEAR', 'JECBBEC1', 'JECEC2YEAR', 'JECEC2', 'JECFlavorQCD', 'JECHFYEAR', 'JECHF', 'JECRelativeBal', 'JECRelativeSampleYEAR', 'JEC', 'JER', 'MCScaleGain1EB', 'MCScaleGain6EB', 'MCScaleHighR9EB', 'MCScaleHighR9EE', 'MCScaleLowR9EB', 'MCScaleLowR9EE', 'MCSmearHighR9EBPhi', 'MCSmearHighR9EBRho', 'MCSmearHighR9EEPhi', 'MCSmearHighR9EERho', 'MCSmearLowR9EBPhi', 'MCSmearLowR9EBRho', 'MCSmearLowR9EEPhi', 'MCSmearLowR9EERho', 'MaterialCentralBarrel', 'MaterialForward', 'MaterialOuterBarrel', 'MvaShift', 'PUJIDShift', 'ShowerShapeHighR9EB', 'ShowerShapeHighR9EE', 'ShowerShapeLowR9EB', 'ShowerShapeLowR9EE', 'SigmaEOverEShift', 'metJecUncertainty', 'metJerUncertainty', 'metPhoUncertainty', 'metUncUncertainty']

cats = ['RECO_0J_PTH_0_10_Tag0', 'RECO_0J_PTH_0_10_Tag1', 'RECO_0J_PTH_0_10_Tag2', 'RECO_0J_PTH_GT10_Tag0', 'RECO_0J_PTH_GT10_Tag1', 'RECO_0J_PTH_GT10_Tag2', 'RECO_1J_PTH_0_60_Tag0', 'RECO_1J_PTH_0_60_Tag1', 'RECO_1J_PTH_0_60_Tag2', 'RECO_1J_PTH_120_200_Tag0', 'RECO_1J_PTH_120_200_Tag1', 'RECO_1J_PTH_120_200_Tag2', 'RECO_1J_PTH_60_120_Tag0', 'RECO_1J_PTH_60_120_Tag1', 'RECO_1J_PTH_60_120_Tag2', 'RECO_GE2J_PTH_0_60_Tag0', 'RECO_GE2J_PTH_0_60_Tag1', 'RECO_GE2J_PTH_0_60_Tag2', 'RECO_GE2J_PTH_120_200_Tag0', 'RECO_GE2J_PTH_120_200_Tag1', 'RECO_GE2J_PTH_120_200_Tag2', 'RECO_GE2J_PTH_60_120_Tag0', 'RECO_GE2J_PTH_60_120_Tag1', 'RECO_GE2J_PTH_60_120_Tag2', 'RECO_PTH_200_300_Tag0', 'RECO_PTH_200_300_Tag1', 'RECO_PTH_300_450_Tag0', 'RECO_PTH_300_450_Tag1', 'RECO_PTH_450_650_Tag0', 'RECO_PTH_GT650_Tag0', 'RECO_THQ_LEP', 'RECO_TTH_HAD_PTH_0_60_Tag0', 'RECO_TTH_HAD_PTH_0_60_Tag1', 'RECO_TTH_HAD_PTH_0_60_Tag2', 'RECO_TTH_HAD_PTH_0_60_Tag3', 'RECO_TTH_HAD_PTH_120_200_Tag0', 'RECO_TTH_HAD_PTH_120_200_Tag1', 'RECO_TTH_HAD_PTH_120_200_Tag2', 'RECO_TTH_HAD_PTH_120_200_Tag3', 'RECO_TTH_HAD_PTH_60_120_Tag0', 'RECO_TTH_HAD_PTH_60_120_Tag1', 'RECO_TTH_HAD_PTH_60_120_Tag2', 'RECO_TTH_HAD_PTH_60_120_Tag3', 'RECO_TTH_HAD_PTH_GT200_Tag0', 'RECO_TTH_HAD_PTH_GT200_Tag1', 'RECO_TTH_HAD_PTH_GT200_Tag2', 'RECO_TTH_HAD_PTH_GT200_Tag3', 'RECO_TTH_LEP_PTH_0_60_Tag0', 'RECO_TTH_LEP_PTH_0_60_Tag1', 'RECO_TTH_LEP_PTH_0_60_Tag2', 'RECO_TTH_LEP_PTH_0_60_Tag3', 'RECO_TTH_LEP_PTH_120_200_Tag0', 'RECO_TTH_LEP_PTH_120_200_Tag1', 'RECO_TTH_LEP_PTH_60_120_Tag0', 'RECO_TTH_LEP_PTH_60_120_Tag1', 'RECO_TTH_LEP_PTH_GT200_Tag0', 'RECO_TTH_LEP_PTH_GT200_Tag1', 'RECO_VBFLIKEGGH_Tag0', 'RECO_VBFLIKEGGH_Tag1', 'RECO_VBFTOPO_BSM_Tag0', 'RECO_VBFTOPO_BSM_Tag1', 'RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag0', 'RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag1', 'RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag0', 'RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag1', 'RECO_VBFTOPO_JET3_HIGHMJJ_Tag0', 'RECO_VBFTOPO_JET3_HIGHMJJ_Tag1', 'RECO_VBFTOPO_JET3_LOWMJJ_Tag0', 'RECO_VBFTOPO_JET3_LOWMJJ_Tag1', 'RECO_VBFTOPO_VHHAD_Tag0', 'RECO_VBFTOPO_VHHAD_Tag1', 'RECO_VH_MET_Tag0', 'RECO_VH_MET_Tag1', 'RECO_WH_LEP_HIGH_Tag0', 'RECO_WH_LEP_HIGH_Tag1', 'RECO_WH_LEP_HIGH_Tag2', 'RECO_WH_LEP_LOW_Tag0', 'RECO_WH_LEP_LOW_Tag1', 'RECO_WH_LEP_LOW_Tag2', 'RECO_ZH_LEP_Tag0', 'RECO_ZH_LEP_Tag1', 'NOTAG']

procToWSFileName = {
  "ggh":"GluGluHToGG",
  "vbf":"VBFHToGG",
  "wh":"WHToGG",
  "zh":"ZHToGG",
  "tth":"ttHJetToGG",
  "thq":"THQ_ctcvcp_HToGG",
  "thw":"THW_ctcvcp_HToGG",
  "ggzh":"ggZH_HToGG",
  "bbh":"bbHToGG"
}

stxs_stage1p2_dict = {
  0:"UNKNOWN",
  -1:"GG2H_FWDH", 
  1:"GG2H_PTH_200_300", 
  2:"GG2H_PTH_300_450", 
  3:"GG2H_PTH_450_650", 
  4:"GG2H_PTH_GT650", 
  5:"GG2H_0J_PTH_0_10", 
  6:"GG2H_0J_PTH_GT10", 
  7:"GG2H_1J_PTH_0_60", 
  8:"GG2H_1J_PTH_60_120", 
  9:"GG2H_1J_PTH_120_200", 
  10:"GG2H_GE2J_MJJ_0_350_PTH_0_60", 
  11:"GG2H_GE2J_MJJ_0_350_PTH_60_120", 
  12:"GG2H_GE2J_MJJ_0_350_PTH_120_200", 
  13:"GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25", 
  14:"GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25", 
  15:"GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25", 
  16:"GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25", 
  -2:"QQ2HQQ_FWDH",
  17:"QQ2HQQ_0J", 
  18:"QQ2HQQ_1J", 
  19:"QQ2HQQ_GE2J_MJJ_0_60", 
  20:"QQ2HQQ_GE2J_MJJ_60_120", 
  21:"QQ2HQQ_GE2J_MJJ_120_350", 
  22:"QQ2HQQ_GE2J_MJJ_GT350_PTH_GT200", 
  23:"QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25", 
  24:"QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25", 
  25:"QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25", 
  26:"QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25", 
  -3:"QQ2HLNU_FWDH",
  27:"QQ2HLNU_PTV_0_75", 
  28:"QQ2HLNU_PTV_75_150", 
  29:"QQ2HLNU_PTV_150_250_0J", 
  30:"QQ2HLNU_PTV_150_250_GE1J", 
  31:"QQ2HLNU_PTV_GT250", 
  -4:"QQ2HLL_FWDH",
  32:"QQ2HLL_PTV_0_75", 
  33:"QQ2HLL_PTV_75_150", 
  34:"QQ2HLL_PTV_150_250_0J", 
  35:"QQ2HLL_PTV_150_250_GE1J", 
  36:"QQ2HLL_PTV_GT250", 
  -5:"GG2HLL_FWDH",
  37:"GG2HLL_PTV_0_75", 
  38:"GG2HLL_PTV_75_150", 
  39:"GG2HLL_PTV_150_250_0J", 
  40:"GG2HLL_PTV_150_250_GE1J", 
  41:"GG2HLL_PTV_GT250", 
  -6:"TTH_FWDH",
  42:"TTH_PTH_0_60", 
  43:"TTH_PTH_60_120", 
  44:"TTH_PTH_120_200", 
  45:"TTH_PTH_200_300", 
  46:"TTH_PTH_GT300", 
  -7:"BBH_FWDH",
  47:"BBH", 
  -8:"TH_FWDH",
  48:"TH"
}


# Dict of vars to add to final workspace
ws_vars = [ # [name,default value, min value, max value, bins]
  {'name':"IntLumi", 'default':1000, 'minValue':0, 'maxValue':999999999, 'constant':True},
  {'name':"CMS_hgg_mass", 'default':125., 'minValue':100., 'maxValue':180., 'bins':160},
  {'name':"dZ", 'default':0, 'minValue':-20, 'maxValue':20, 'bins':40},
  {'name':"centralObjectWeight", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"LooseMvaSFUp01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"PreselSFUp01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"electronVetoSFUp01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"TriggerWeightUp01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"FracRVWeightUp01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"FracRVNvtxWeightUp01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"MuonIDWeightUp01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"ElectronIDWeightUp01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"ElectronRecoWeightUp01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"MuonIsoWeightUp01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"JetBTagCutWeightUp01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"JetBTagReshapeWeightUp01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"PrefireProbabilityUp01sigma", 'default':0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_MuUp01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_ResUp01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_Mig01Up01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_Mig12Up01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_VBF2jUp01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_VBF3jUp01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_PT60Up01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_PT120Up01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_qmtopUp01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"LooseMvaSFDown01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"PreselSFDown01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"electronVetoSFDown01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"TriggerWeightDown01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"FracRVWeightDown01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"FracRVNvtxWeightDown01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"MuonIDWeightDown01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"ElectronIDWeightDown01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"ElectronRecoWeightDown01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"MuonIsoWeightDown01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"JetBTagCutWeightDown01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"JetBTagReshapeWeightDown01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"PrefireProbabilityDown01sigma", 'default':0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_MuDown01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_ResDown01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_Mig01Down01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_Mig12Down01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_VBF2jDown01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_VBF3jDown01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_PT60Down01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_PT120Down01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1},
  {'name':"THU_ggH_qmtopDown01sigma", 'default':1.0, 'minValue':-999999, 'maxValue':999999, 'bins':1}
]
for ac, nWeights in array_columns.iteritems():
  for i in range(0,nWeights):
    ws_vars.append({'name':"%s_%g"%(ac[:-1],i), 'default':1.0, 'minValue':-999999, 'maxValue':999999}) 

# Define argsets to enter different levels of RooDataSets
argSets = {
  'nominal':'weight,CMS_hgg_mass,dZ,centralObjectWeight,LooseMvaSFUp01sigma,PreselSFUp01sigma,electronVetoSFUp01sigma,TriggerWeightUp01sigma,FracRVWeightUp01sigma,FracRVNvtxWeightUp01sigma,MuonIDWeightUp01sigma,ElectronIDWeightUp01sigma,ElectronRecoWeightUp01sigma,MuonIsoWeightUp01sigma,JetBTagCutWeightUp01sigma,JetBTagReshapeWeightUp01sigma,PrefireProbabilityUp01sigma,THU_ggH_MuUp01sigma,THU_ggH_ResUp01sigma,THU_ggH_Mig01Up01sigma,THU_ggH_Mig12Up01sigma,THU_ggH_VBF2jUp01sigma,THU_ggH_VBF3jUp01sigma,THU_ggH_PT60Up01sigma,THU_ggH_PT120Up01sigma,THU_ggH_qmtopUp01sigma,LooseMvaSFDown01sigma,PreselSFDown01sigma,electronVetoSFDown01sigma,TriggerWeightDown01sigma,FracRVWeightDown01sigma,FracRVNvtxWeightDown01sigma,MuonIDWeightDown01sigma,ElectronIDWeightDown01sigma,ElectronRecoWeightDown01sigma,MuonIsoWeightDown01sigma,JetBTagCutWeightDown01sigma,JetBTagReshapeWeightDown01sigma,PrefireProbabilityDown01sigma,THU_ggH_MuDown01sigma,THU_ggH_ResDown01sigma,THU_ggH_Mig01Down01sigma,THU_ggH_Mig12Down01sigma,THU_ggH_VBF2jDown01sigma,THU_ggH_VBF3jDown01sigma,THU_ggH_PT60Down01sigma,THU_ggH_PT120Down01sigma,THU_ggH_qmtopDown01sigma,pdfWeight_0,pdfWeight_1,pdfWeight_2,pdfWeight_3,pdfWeight_4,pdfWeight_5,pdfWeight_6,pdfWeight_7,pdfWeight_8,pdfWeight_9,pdfWeight_10,pdfWeight_11,pdfWeight_12,pdfWeight_13,pdfWeight_14,pdfWeight_15,pdfWeight_16,pdfWeight_17,pdfWeight_18,pdfWeight_19,pdfWeight_20,pdfWeight_21,pdfWeight_22,pdfWeight_23,pdfWeight_24,pdfWeight_25,pdfWeight_26,pdfWeight_27,pdfWeight_28,pdfWeight_29,pdfWeight_30,pdfWeight_31,pdfWeight_32,pdfWeight_33,pdfWeight_34,pdfWeight_35,pdfWeight_36,pdfWeight_37,pdfWeight_38,pdfWeight_39,pdfWeight_40,pdfWeight_41,pdfWeight_42,pdfWeight_43,pdfWeight_44,pdfWeight_45,pdfWeight_46,pdfWeight_47,pdfWeight_48,pdfWeight_49,pdfWeight_50,pdfWeight_51,pdfWeight_52,pdfWeight_53,pdfWeight_54,pdfWeight_55,pdfWeight_56,pdfWeight_57,pdfWeight_58,pdfWeight_59,scaleWeight_0,scaleWeight_1,scaleWeight_2,scaleWeight_3,scaleWeight_4,scaleWeight_5,scaleWeight_6,scaleWeight_7,scaleWeight_8,alphaSWeight_0,alphaSWeight_1',
  'nominal_sub':'weight,CMS_hgg_mass,dZ,centralObjectWeight,LooseMvaSFUp01sigma,PreselSFUp01sigma,electronVetoSFUp01sigma,TriggerWeightUp01sigma,FracRVWeightUp01sigma,FracRVNvtxWeightUp01sigma,MuonIDWeightUp01sigma,ElectronIDWeightUp01sigma,ElectronRecoWeightUp01sigma,MuonIsoWeightUp01sigma,JetBTagCutWeightUp01sigma,JetBTagReshapeWeightUp01sigma,PrefireProbabilityUp01sigma,THU_ggH_MuUp01sigma,THU_ggH_ResUp01sigma,THU_ggH_Mig01Up01sigma,THU_ggH_Mig12Up01sigma,THU_ggH_VBF2jUp01sigma,THU_ggH_VBF3jUp01sigma,THU_ggH_PT60Up01sigma,THU_ggH_PT120Up01sigma,THU_ggH_qmtopUp01sigma,LooseMvaSFDown01sigma,PreselSFDown01sigma,electronVetoSFDown01sigma,TriggerWeightDown01sigma,FracRVWeightDown01sigma,FracRVNvtxWeightDown01sigma,MuonIDWeightDown01sigma,ElectronIDWeightDown01sigma,ElectronRecoWeightDown01sigma,MuonIsoWeightDown01sigma,JetBTagCutWeightDown01sigma,JetBTagReshapeWeightDown01sigma,PrefireProbabilityDown01sigma,THU_ggH_MuDown01sigma,THU_ggH_ResDown01sigma,THU_ggH_Mig01Down01sigma,THU_ggH_Mig12Down01sigma,THU_ggH_VBF2jDown01sigma,THU_ggH_VBF3jDown01sigma,THU_ggH_PT60Down01sigma,THU_ggH_PT120Down01sigma,THU_ggH_qmtopDown01sigma',
  'shapeSyst':'CMS_hgg_mass',
  'notag':'weight,THU_ggH_MuUp01sigma,THU_ggH_ResUp01sigma,THU_ggH_Mig01Up01sigma,THU_ggH_Mig12Up01sigma,THU_ggH_VBF2jUp01sigma,THU_ggH_VBF3jUp01sigma,THU_ggH_PT60Up01sigma,THU_ggH_PT120Up01sigma,THU_ggH_qmtopUp01sigma,THU_ggH_MuDown01sigma,THU_ggH_ResDown01sigma,THU_ggH_Mig01Down01sigma,THU_ggH_Mig12Down01sigma,THU_ggH_VBF2jDown01sigma,THU_ggH_VBF3jDown01sigma,THU_ggH_PT60Down01sigma,THU_ggH_PT120Down01sigma,THU_ggH_qmtopDown01sigma,pdfWeight_0,pdfWeight_1,pdfWeight_2,pdfWeight_3,pdfWeight_4,pdfWeight_5,pdfWeight_6,pdfWeight_7,pdfWeight_8,pdfWeight_9,pdfWeight_10,pdfWeight_11,pdfWeight_12,pdfWeight_13,pdfWeight_14,pdfWeight_15,pdfWeight_16,pdfWeight_17,pdfWeight_18,pdfWeight_19,pdfWeight_20,pdfWeight_21,pdfWeight_22,pdfWeight_23,pdfWeight_24,pdfWeight_25,pdfWeight_26,pdfWeight_27,pdfWeight_28,pdfWeight_29,pdfWeight_30,pdfWeight_31,pdfWeight_32,pdfWeight_33,pdfWeight_34,pdfWeight_35,pdfWeight_36,pdfWeight_37,pdfWeight_38,pdfWeight_39,pdfWeight_40,pdfWeight_41,pdfWeight_42,pdfWeight_43,pdfWeight_44,pdfWeight_45,pdfWeight_46,pdfWeight_47,pdfWeight_48,pdfWeight_49,pdfWeight_50,pdfWeight_51,pdfWeight_52,pdfWeight_53,pdfWeight_54,pdfWeight_55,pdfWeight_56,pdfWeight_57,pdfWeight_58,pdfWeight_59,scaleWeight_0,scaleWeight_1,scaleWeight_2,scaleWeight_3,scaleWeight_4,scaleWeight_5,scaleWeight_6,scaleWeight_7,scaleWeight_8,alphaSWeight_0,alphaSWeight_1',
  'notag_sub':'weight,THU_ggH_MuUp01sigma,THU_ggH_ResUp01sigma,THU_ggH_Mig01Up01sigma,THU_ggH_Mig12Up01sigma,THU_ggH_VBF2jUp01sigma,THU_ggH_VBF3jUp01sigma,THU_ggH_PT60Up01sigma,THU_ggH_PT120Up01sigma,THU_ggH_qmtopUp01sigma,THU_ggH_MuDown01sigma,THU_ggH_ResDown01sigma,THU_ggH_Mig01Down01sigma,THU_ggH_Mig12Down01sigma,THU_ggH_VBF2jDown01sigma,THU_ggH_VBF3jDown01sigma,THU_ggH_PT60Down01sigma,THU_ggH_PT120Down01sigma,THU_ggH_qmtopDown01sigma'
}

# Function to add vars to workspace
def add_vars_to_workspace(_ws=None):
  # Add weight var
  weight = ROOT.RooRealVar("weight","weight",0)
  getattr(ws, 'import')(weight)
  # Loop over vars to enter workspace
  _vars = {}
  for var in ws_vars:
    _vars[var['name']] = ROOT.RooRealVar( var['name'], var['name'], var['default'], var['minValue'], var['maxValue'] )
    if 'constant' in var:
      if var['constant']: _vars[var['name']].setConstant(True)
    if 'bins' in var: _vars[var['name']].setBins(var['bins'])
    getattr(_ws, 'import')( _vars[var['name']], ROOT.RooFit.Silence())

# Function to create arg list depending on Data type
def make_argSet( _ws, _argSets, _type ):
  argSet = ROOT.RooArgSet()
  aset = _argSets[_type]
  args = aset.split(",")
  for arg in args: argSet.add( _ws.var(arg) )
  return argSet
    
def get_options():
  parser = OptionParser()
  parser.add_option('--inputPandasFile',dest='inputPandasFile', default="", help='Input pandas dataFrame file')
  parser.add_option('--productionMode',dest='productionMode', default="ggh", help='Production mode [ggh,vbf,wh,zh,tth,th]')
  parser.add_option('--year',dest='year', default="2016", help='Year')
  parser.add_option('--decayExt',dest='decayExt', default="", help='Decay extension (used for ggZH)')
  parser.add_option('--nSplit',dest='nSplit', default=1, type='int', help='Split into n output files')
  return parser.parse_args()
(opt,args) = get_options()

# Check if input pandas file exists: if so load dataFrame
if os.path.exists( opt.inputPandasFile ):
  print " --> [VERBOSE] Loading pandas dataFrame: %s"%opt.inputPandasFile
  with open( opt.inputPandasFile, "rb") as f_in: data = pickle.load(f_in)

# Extract STXS bin
stxsBin = stxs_stage1p2_dict[int(data.stage1p2bin.unique()[0])]
# If ggZH then change STXS bin according to decay extension
if opt.productionMode == "ggzh":
  if opt.decayExt == "_ZToQQ": stxsBin = re.sub("GG2H","GG2HQQ",stxsBin)
  elif opt.decayExt == "_ZToNuNu": stxsBin = re.sub("GG2HLL","GG2HNUNU",stxsBin)
# For TH: split into THQ and THW
elif opt.productionMode == "thq": stxsBin = re.sub("TH","THQ",stxsBin)
elif opt.productionMode == 'thw': stxsBin = re.sub("TH","THW",stxsBin)

# Split dataframe into equal sized chunks
for i in range(0,opt.nSplit):

  # Define output WS file
  outputWSDir = "/".join(opt.inputPandasFile.split("/")[:-2])+"/ws_%s_%s"%(opt.productionMode,stxsBin)
  if not os.path.exists(outputWSDir): os.system("mkdir %s"%outputWSDir)
  f_id = re.sub(".pkl","",opt.inputPandasFile.split("_")[-1])
  if opt.nSplit == 1: outputWSFile = "%s/output_%s_M125_13TeV_amcatnloFXFX_pythia8_%s_%s.root"%(outputWSDir,procToWSFileName[opt.productionMode],stxsBin,f_id)
  else: outputWSFile = "%s/output_%s_M125_13TeV_amcatnloFXFX_pythia8_%s_%s_%g.root"%(outputWSDir,procToWSFileName[opt.productionMode],stxsBin,f_id,i)
  fout = ROOT.TFile(outputWSFile,"RECREATE")
  foutdir = fout.mkdir("tagsDumper")
  foutdir.cd()

  # Initiate output workspace to store RooDataSet and RooDataHist
  ws = ROOT.RooWorkspace("cms_hgg_13TeV","cms_hgg_13TeV")
  # Add variables to workspace
  add_vars_to_workspace(ws) 
    
  # Loop over cats
  for cat in cats:
    # Create mask for nominal/notag dataset: splitting into nSplit components
    mask = ((data['type']=='nominal')|(data['type']=='notag'))&(data['cat']==cat)&((data.index%opt.nSplit-i)==0)
    # Convert dataframe to structured array and then to ROOT tree
    sa = data[mask].to_records()
    t = array2tree(sa)
    # Define RooDataSet
    dname = "%s_125_13TeV_%s"%(opt.productionMode,cat)
    # Extract ArgSet
    # FIXME: for bbH and tHW, missing theory weights
    if opt.productionMode in ['bbh','thw']:
      if cat == 'NOTAG': argset = make_argSet( ws, argSets, 'notag_sub') 
      else: argset = make_argSet( ws, argSets, 'nominal_sub')
    else:
      if cat == 'NOTAG': argset = make_argSet( ws, argSets, 'notag') 
      else: argset = make_argSet( ws, argSets, 'nominal')
    # Convert tree to RooDataSet and add to workspace
    d = ROOT.RooDataSet(dname,dname,t,argset,'','weight')
    getattr(ws,'import')(d)
    # Delete trees and RooDataSet
    t.Delete()
    d.Delete()
    del sa

    # Loop over shapeSysts and add RooDataHists
    if cat != 'NOTAG':
      for s in shapeSysts:
	for direction in ['Up','Down']:
	  # Create mask for systematic variation
	  mask = (data['type']=='%s%s'%(s,direction))&(data['cat']==cat)&((data.index%opt.nSplit-i)==0)
	  # Convert dataFrame to structured array and then to ROOT tree
	  sa = data[mask].to_records()
	  t = array2tree(sa)
	  # Name of RooDataHist
	  hname = "%s_125_13TeV_%s_%s%s01sigma"%(opt.productionMode,cat,s,direction)
	  # If YEAR in hname then change to year being processed
	  #hname = re.sub("YEAR",opt.year,hname)
	  argset = make_argSet( ws, argSets, 'shapeSyst')
	  h = ROOT.RooDataHist(hname,hname,argset)
	  # Loop over events and add to workspace
	  for ev in t:
	    ws.var("CMS_hgg_mass").setVal(ev.CMS_hgg_mass)
	    h.add(argset,ev.weight)
	  # Add to workspace
	  getattr(ws,'import')(h)
          # Delete trees and RooDatatHist
	  t.Delete()
	  h.Delete()
	  del sa

  # Export ws to file
  ws.Write()

  # Delete workspace and file from heap
  fout.Close()
  ws.Delete()
  fout.Delete()
    
    
