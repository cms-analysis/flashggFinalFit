# NEW datacard making scrit
#  * Uses Pandas dataframe to store all info about processes
#  * Option for merging across years

print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG DATACARD MAKER RUN II ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
import os, sys
import re
from optparse import OptionParser
import ROOT
import pandas as pd
import glob
import pickle

def leave():
  print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG DATACARD MAKER RUN II (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
  sys.exit(1)

# cats = 'RECO_0J_PTH_0_10_Tag0,RECO_0J_PTH_0_10_Tag1,RECO_0J_PTH_0_10_Tag2,RECO_0J_PTH_GT10_Tag0,RECO_0J_PTH_GT10_Tag1,RECO_0J_PTH_GT10_Tag2,RECO_1J_PTH_0_60_Tag0,RECO_1J_PTH_0_60_Tag1,RECO_1J_PTH_0_60_Tag2,RECO_1J_PTH_60_120_Tag0,RECO_1J_PTH_60_120_Tag1,RECO_1J_PTH_60_120_Tag2,RECO_1J_PTH_120_200_Tag0,RECO_1J_PTH_120_200_Tag1,RECO_1J_PTH_120_200_Tag2,RECO_GE2J_PTH_0_60_Tag0,RECO_GE2J_PTH_0_60_Tag1,RECO_GE2J_PTH_0_60_Tag2,RECO_GE2J_PTH_60_120_Tag0,RECO_GE2J_PTH_60_120_Tag1,RECO_GE2J_PTH_60_120_Tag2,RECO_GE2J_PTH_120_200_Tag0,RECO_GE2J_PTH_120_200_Tag1,RECO_GE2J_PTH_120_200_Tag2,RECO_PTH_200_300_Tag0,RECO_PTH_200_300_Tag1,RECO_PTH_300_450_Tag0,RECO_PTH_300_450_Tag1,RECO_PTH_450_650_Tag0,RECO_PTH_450_650_Tag1,RECO_PTH_GT650_Tag0,RECO_PTH_GT650_Tag1,RECO_VBFTOPO_VHHAD_Tag0,RECO_VBFTOPO_VHHAD_Tag1,RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag0,RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag1,RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag0,RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag1,RECO_VBFTOPO_JET3_LOWMJJ_Tag0,RECO_VBFTOPO_JET3_LOWMJJ_Tag1,RECO_VBFTOPO_JET3_HIGHMJJ_Tag0,RECO_VBFTOPO_JET3_HIGHMJJ_Tag1,RECO_VBFTOPO_BSM_Tag0,RECO_VBFTOPO_BSM_Tag1,RECO_VBFLIKEGGH_Tag0,RECO_VBFLIKEGGH_Tag1,RECO_TTH_HAD_LOW_Tag0,RECO_TTH_HAD_LOW_Tag1,RECO_TTH_HAD_LOW_Tag2,RECO_TTH_HAD_LOW_Tag3,RECO_TTH_HAD_HIGH_Tag0,RECO_TTH_HAD_HIGH_Tag1,RECO_TTH_HAD_HIGH_Tag2,RECO_TTH_HAD_HIGH_Tag3,RECO_WH_LEP_LOW_Tag0,RECO_WH_LEP_LOW_Tag1,RECO_WH_LEP_LOW_Tag2,RECO_WH_LEP_HIGH_Tag0,RECO_WH_LEP_HIGH_Tag1,RECO_WH_LEP_HIGH_Tag2,RECO_ZH_LEP_Tag0,RECO_ZH_LEP_Tag1,RECO_TTH_LEP_LOW_Tag0,RECO_TTH_LEP_LOW_Tag1,RECO_TTH_LEP_LOW_Tag2,RECO_TTH_LEP_LOW_Tag3,RECO_TTH_LEP_HIGH_Tag0,RECO_TTH_LEP_HIGH_Tag1,RECO_TTH_LEP_HIGH_Tag2,RECO_TTH_LEP_HIGH_Tag3,RECO_THQ_LEP'

mergedYear_cats = ['RECO_0J_PTH_0_10_Tag0', 'RECO_0J_PTH_0_10_Tag1', 'RECO_0J_PTH_0_10_Tag2', 'RECO_0J_PTH_GT10_Tag0', 'RECO_0J_PTH_GT10_Tag1', 'RECO_0J_PTH_GT10_Tag2', 'RECO_1J_PTH_0_60_Tag0', 'RECO_1J_PTH_0_60_Tag1', 'RECO_1J_PTH_0_60_Tag2', 'RECO_1J_PTH_60_120_Tag0', 'RECO_1J_PTH_60_120_Tag1', 'RECO_1J_PTH_60_120_Tag2', 'RECO_1J_PTH_120_200_Tag0', 'RECO_1J_PTH_120_200_Tag1', 'RECO_1J_PTH_120_200_Tag2', 'RECO_GE2J_PTH_0_60_Tag0', 'RECO_GE2J_PTH_0_60_Tag1', 'RECO_GE2J_PTH_0_60_Tag2', 'RECO_GE2J_PTH_60_120_Tag0', 'RECO_GE2J_PTH_60_120_Tag1', 'RECO_GE2J_PTH_60_120_Tag2', 'RECO_GE2J_PTH_120_200_Tag0', 'RECO_GE2J_PTH_120_200_Tag1', 'RECO_GE2J_PTH_120_200_Tag2', 'RECO_PTH_200_300_Tag0', 'RECO_PTH_200_300_Tag1', 'RECO_PTH_300_450_Tag0', 'RECO_PTH_300_450_Tag1', 'RECO_PTH_450_650_Tag0', 'RECO_PTH_450_650_Tag1', 'RECO_PTH_GT650_Tag0', 'RECO_PTH_GT650_Tag1', 'RECO_VBFTOPO_VHHAD_Tag0', 'RECO_VBFTOPO_VHHAD_Tag1', 'RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag0', 'RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag1', 'RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag0', 'RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag1', 'RECO_VBFTOPO_JET3_LOWMJJ_Tag0', 'RECO_VBFTOPO_JET3_LOWMJJ_Tag1', 'RECO_VBFTOPO_JET3_HIGHMJJ_Tag0', 'RECO_VBFTOPO_JET3_HIGHMJJ_Tag1', 'RECO_VBFTOPO_BSM_Tag0', 'RECO_VBFTOPO_BSM_Tag1', 'RECO_VBFLIKEGGH_Tag0', 'RECO_VBFLIKEGGH_Tag1', 'RECO_TTH_HAD_LOW_Tag0', 'RECO_TTH_HAD_LOW_Tag1', 'RECO_TTH_HAD_LOW_Tag2', 'RECO_TTH_HAD_LOW_Tag3', 'RECO_TTH_HAD_HIGH_Tag0', 'RECO_TTH_HAD_HIGH_Tag1', 'RECO_TTH_HAD_HIGH_Tag2', 'RECO_TTH_HAD_HIGH_Tag3', 'RECO_WH_LEP_LOW_Tag0', 'RECO_WH_LEP_LOW_Tag1', 'RECO_WH_LEP_LOW_Tag2', 'RECO_WH_LEP_HIGH_Tag0', 'RECO_WH_LEP_HIGH_Tag1', 'RECO_WH_LEP_HIGH_Tag2', 'RECO_ZH_LEP_Tag0', 'RECO_ZH_LEP_Tag1', 'RECO_TTH_LEP_LOW_Tag0', 'RECO_TTH_LEP_LOW_Tag1', 'RECO_TTH_LEP_LOW_Tag2', 'RECO_TTH_LEP_LOW_Tag3', 'RECO_TTH_LEP_HIGH_Tag0', 'RECO_TTH_LEP_HIGH_Tag1', 'RECO_TTH_LEP_HIGH_Tag2', 'RECO_TTH_LEP_HIGH_Tag3', 'RECO_THQ_LEP'] 

catsSplittingScheme_NoTag = "tagsetone"
catsSplittingScheme = {
  'tagsetone':['RECO_0J_PTH_0_10_Tag0', 'RECO_0J_PTH_0_10_Tag1', 'RECO_0J_PTH_0_10_Tag2', 'RECO_0J_PTH_GT10_Tag0', 'RECO_0J_PTH_GT10_Tag1', 'RECO_0J_PTH_GT10_Tag2', 'RECO_1J_PTH_0_60_Tag0', 'RECO_1J_PTH_0_60_Tag1', 'RECO_1J_PTH_0_60_Tag2', 'RECO_1J_PTH_60_120_Tag0', 'RECO_1J_PTH_60_120_Tag1', 'RECO_1J_PTH_60_120_Tag2', 'RECO_1J_PTH_120_200_Tag0', 'RECO_1J_PTH_120_200_Tag1', 'RECO_1J_PTH_120_200_Tag2', 'RECO_GE2J_PTH_0_60_Tag0', 'RECO_GE2J_PTH_0_60_Tag1', 'RECO_GE2J_PTH_0_60_Tag2', 'RECO_GE2J_PTH_60_120_Tag0', 'RECO_GE2J_PTH_60_120_Tag1', 'RECO_GE2J_PTH_60_120_Tag2', 'RECO_GE2J_PTH_120_200_Tag0', 'RECO_GE2J_PTH_120_200_Tag1', 'RECO_GE2J_PTH_120_200_Tag2'],
  'tagsettwo':['RECO_PTH_200_300_Tag0', 'RECO_PTH_200_300_Tag1', 'RECO_PTH_300_450_Tag0', 'RECO_PTH_300_450_Tag1', 'RECO_PTH_450_650_Tag0', 'RECO_PTH_450_650_Tag1', 'RECO_PTH_GT650_Tag0', 'RECO_PTH_GT650_Tag1', 'RECO_VBFTOPO_VHHAD_Tag0', 'RECO_VBFTOPO_VHHAD_Tag1', 'RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag0', 'RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag1', 'RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag0', 'RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag1', 'RECO_VBFTOPO_JET3_LOWMJJ_Tag0', 'RECO_VBFTOPO_JET3_LOWMJJ_Tag1', 'RECO_VBFTOPO_JET3_HIGHMJJ_Tag0', 'RECO_VBFTOPO_JET3_HIGHMJJ_Tag1', 'RECO_VBFTOPO_BSM_Tag0', 'RECO_VBFTOPO_BSM_Tag1', 'RECO_VBFLIKEGGH_Tag0', 'RECO_VBFLIKEGGH_Tag1'],
  'tagsetthree':['RECO_TTH_HAD_LOW_Tag0', 'RECO_TTH_HAD_LOW_Tag1', 'RECO_TTH_HAD_LOW_Tag2', 'RECO_TTH_HAD_LOW_Tag3', 'RECO_TTH_HAD_HIGH_Tag0', 'RECO_TTH_HAD_HIGH_Tag1', 'RECO_TTH_HAD_HIGH_Tag2', 'RECO_TTH_HAD_HIGH_Tag3', 'RECO_WH_LEP_LOW_Tag0', 'RECO_WH_LEP_LOW_Tag1', 'RECO_WH_LEP_LOW_Tag2', 'RECO_WH_LEP_HIGH_Tag0', 'RECO_WH_LEP_HIGH_Tag1', 'RECO_WH_LEP_HIGH_Tag2', 'RECO_ZH_LEP_Tag0', 'RECO_ZH_LEP_Tag1', 'RECO_TTH_LEP_LOW_Tag0', 'RECO_TTH_LEP_LOW_Tag1', 'RECO_TTH_LEP_LOW_Tag2', 'RECO_TTH_LEP_LOW_Tag3', 'RECO_TTH_LEP_HIGH_Tag0', 'RECO_TTH_LEP_HIGH_Tag1', 'RECO_TTH_LEP_HIGH_Tag2', 'RECO_TTH_LEP_HIGH_Tag3', 'RECO_THQ_LEP']
  }

stxsBinMergingScheme = {'ggH_VBFlike':['ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'],
                        'ggH_BSM':['ggH_PTH_200_300','ggH_PTH_300_450','ggH_PTH_450_650','PTH_GT650'],
                        'ggH_BSM_high':['ggH_PTH_300_450','ggH_PTH_450_650','PTH_GT650'],
                        'VBF_2j':['qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'],
                        'VBF_3j':['qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'],
                        'WH_lep':['WH_lep_PTV_0_75','WH_lep_PTV_75_150','WH_lep_PTV_150_250_0J','WH_lep_PTV_150_250_GE1J','WH_lep_PTV_GT250'],
                        'WH_lep_high':['WH_lep_PTV_75_150','WH_lep_PTV_150_250_0J','WH_lep_PTV_150_250_GE1J','WH_lep_PTV_GT250'],
                        'ZH_lep':['ZH_lep_PTV_0_75','ZH_lep_PTV_75_150','ZH_lep_PTV_150_250_0J','ZH_lep_PTV_150_250_GE1J','ZH_lep_PTV_GT250'],
                        #'top':['ttH_PTH_0_60','ttH_PTH_60_120','ttH_PTH_120_200','ttH_PTH_200_300','ttH_PTH_GT300','tHq'], 
                        'ttH':['ttH_PTH_0_60','ttH_PTH_60_120','ttH_PTH_120_200','ttH_PTH_200_300','ttH_PTH_GT300'], 
                        'ttH_low':['ttH_PTH_0_60','ttH_PTH_60_120'], 
                        'ttH_high':['ttH_PTH_120_200','ttH_PTH_200_300','ttH_PTH_GT300']
                       }
lumi = {'2016':'35.9', '2017':'41.5', '2018':'59.8'}
decay = "hgg"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Mapping to STXS bin and nominal dataset name:
def procToSTXS( _proc ):
  #Do mapping
  proc_map = {"GG2H":"ggH","VBF":"qqH","WH2HQQ":"WH_had","ZH2HQQ":"ZH_had","QQ2HLNU":"WH_lep","QQ2HLL":"ZH_lep","TTH":"ttH","BBH":"bbH","THQ":"tHq","THW":"tHW"}
  for key in proc_map: _proc = re.sub( key, proc_map[key], _proc )
  return _proc

def procToData( _proc ):
  proc_map = {"GG2H":"ggh","VBF":"vbf","WH2HQQ":"wh","ZH2HQQ":"zh","QQ2HLNU":"wh","QQ2HLL":"zh","TTH":"tth","BBH":"bbH","THQ":"thq","THW":"thw"}
  for key in proc_map: _proc = re.sub( key, proc_map[key], _proc )
  return _proc

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Systematics uncertainty sources: FIXME input as a json file instead
# List of dicts to store info about uncertainty sources

# SHAPE NUISANCES: effect encoded in signal model
signal_shape_systematics = [
		{'name':'CMS_hgg_nuisance_deltafracright','title':'CMS_hgg_nuisance_deltafracright','type':'signal_shape','mean':'0.0','sigma':'0.02'},
		{'name':'CMS_hgg_nuisance_NonLinearity_13TeVscale','title':'CMS_hgg_nuisance_NonLinearity_13TeVscale','type':'signal_shape','mean':'0.0','sigma':'0.001'},
		{'name':'CMS_hgg_nuisance_Geant4_13TeVscale','title':'CMS_hgg_nuisance_Geant4_13TeVscale','type':'signal_shape','mean':'0.0','sigma':'0.0005'},
		{'name':'CMS_hgg_nuisance_HighR9EB_13TeVscale','title':'CMS_hgg_nuisance_HighR9EB_13TeVscale','type':'signal_shape','mean':'0.0','sigma':'1.0'},
		{'name':'CMS_hgg_nuisance_HighR9EE_13TeVscale','title':'CMS_hgg_nuisance_HighR9EE_13TeVscale','type':'signal_shape','mean':'0.0','sigma':'1.0'},
		{'name':'CMS_hgg_nuisance_LowR9EB_13TeVscale','title':'CMS_hgg_nuisance_LowR9EB_13TeVscale','type':'signal_shape','mean':'0.0','sigma':'1.0'},
		{'name':'CMS_hgg_nuisance_LowR9EE_13TeVscale','title':'CMS_hgg_nuisance_LowR9EE_13TeVscale','type':'signal_shape','mean':'0.0','sigma':'1.0'},
		{'name':'CMS_hgg_nuisance_ShowerShapeHighR9EB_scale','title':'CMS_hgg_nuisance_ShowerShapeHighR9EB_scale','type':'signal_shape','mean':'0.0','sigma':'1.0'},
		{'name':'CMS_hgg_nuisance_ShowerShapeHighR9EE_scale','title':'CMS_hgg_nuisance_ShowerShapeHighR9EE_scale','type':'signal_shape','mean':'0.0','sigma':'1.0'},
		{'name':'CMS_hgg_nuisance_ShowerShapeLowR9EB_scale','title':'CMS_hgg_nuisance_ShowerShapeLowR9EB_scale','type':'signal_shape','mean':'0.0','sigma':'1.0'},
		{'name':'CMS_hgg_nuisance_ShowerShapeLowR9EE_scale','title':'CMS_hgg_nuisance_ShowerShapeLowR9EE_scale','type':'signal_shape','mean':'0.0','sigma':'1.0'},
		{'name':'CMS_hgg_nuisance_MaterialCentralBarrel_scale','title':'CMS_hgg_nuisance_MaterialCentralBarrel_scale','type':'signal_shape','mean':'0.0','sigma':'1.0'},
		{'name':'CMS_hgg_nuisance_MaterialOuterBarrel_scale','title':'CMS_hgg_nuisance_MaterialOuterBarrel_scale','type':'signal_shape','mean':'0.0','sigma':'1.0'},
		{'name':'CMS_hgg_nuisance_MaterialForward_scale','title':'CMS_hgg_nuisance_MaterialForward_scale','type':'signal_shape','mean':'0.0','sigma':'1.0'},
		{'name':'CMS_hgg_nuisance_FNUFEE_scale','title':'CMS_hgg_nuisance_FNUFEE_scale','type':'signal_shape','mean':'0.0','sigma':'1.0'},
		{'name':'CMS_hgg_nuisance_FNUFEB_scale','title':'CMS_hgg_nuisance_FNUFEB_scale','type':'signal_shape','mean':'0.0','sigma':'1.0'},
		{'name':'CMS_hgg_nuisance_HighR9EBPhi_13TeVsmear','title':'CMS_hgg_nuisance_HighR9EBPhi_13TeVsmear','type':'signal_shape','mean':'0.0','sigma':'1.0'},
		{'name':'CMS_hgg_nuisance_HighR9EBRho_13TeVsmear','title':'CMS_hgg_nuisance_HighR9EBRho_13TeVsmear','type':'signal_shape','mean':'0.0','sigma':'1.0'},
		{'name':'CMS_hgg_nuisance_HighR9EEPhi_13TeVsmear','title':'CMS_hgg_nuisance_HighR9EEPhi_13TeVsmear','type':'signal_shape','mean':'0.0','sigma':'1.0'},
		{'name':'CMS_hgg_nuisance_HighR9EERho_13TeVsmear','title':'CMS_hgg_nuisance_HighR9EERho_13TeVsmear','type':'signal_shape','mean':'0.0','sigma':'1.0'},
		{'name':'CMS_hgg_nuisance_LowR9EBPhi_13TeVsmear','title':'CMS_hgg_nuisance_LowR9EBPhi_13TeVsmear','type':'signal_shape','mean':'0.0','sigma':'1.0'},
		{'name':'CMS_hgg_nuisance_LowR9EBRho_13TeVsmear','title':'CMS_hgg_nuisance_LowR9EBRho_13TeVsmear','type':'signal_shape','mean':'0.0','sigma':'1.0'},
		{'name':'CMS_hgg_nuisance_LowR9EEPhi_13TeVsmear','title':'CMS_hgg_nuisance_LowR9EEPhi_13TeVsmear','type':'signal_shape','mean':'0.0','sigma':'1.0'},
		{'name':'CMS_hgg_nuisance_LowR9EERho_13TeVsmear','title':'CMS_hgg_nuisance_LowR9EERho_13TeVsmear','type':'signal_shape','mean':'0.0','sigma':'1.0'}
	      ]

# EXPERIMENTAL SYSTEMATICS
experimental_systematics = [ 
		{'name':'lumi_13TeV','title':'lumi_13TeV','type':'constant','prior':'lnN','correlateAcrossYears':0,'value':{'2016':'1.025','2017':'1.023','2018':'1.025'}},
		{'name':'LooseMvaSF','title':'CMS_hgg_LooseMvaSF','type':'factory','prior':'lnN','correlateAcrossYears':0},
		{'name':'PreselSF','title':'CMS_hgg_PreselSF','type':'factory','prior':'lnN','correlateAcrossYears':1},
		{'name':'electronVetoSF','title':'CMS_hgg_electronVetoSF','type':'factory','prior':'lnN','correlateAcrossYears':0},
		{'name':'TriggerWeight','title':'CMS_hgg_TriggerWeight','type':'factory','prior':'lnN','correlateAcrossYears':0},
		{'name':'SigmaEOverEShift','title':'CMS_hgg_SigmaEOverEShift','type':'factory','prior':'lnN','correlateAcrossYears':0},
		{'name':'MvaShift','title':'CMS_hgg_phoIdMva','type':'factory','prior':'lnN','correlateAcrossYears':1},
		{'name':'PUJIDShift','title':'CMS_hgg_PUJIDShift','type':'factory','prior':'lnN','correlateAcrossYears':0},
		{'name':'JEC','title':'CMS_scale_j','type':'factory','prior':'lnN','correlateAcrossYears':0},
		{'name':'JER','title':'CMS_res_j','type':'factory','prior':'lnN','correlateAcrossYears':0},
		{'name':'metJecUncertainty','title':'CMS_hgg_MET_scale_j','type':'factory','prior':'lnN','correlateAcrossYears':1},
		{'name':'metJerUncertainty','title':'CMS_hgg_MET_res_j','type':'factory','prior':'lnN','correlateAcrossYears':1},
		{'name':'metPhoUncertainty','title':'CMS_hgg_MET_PhotonScale','type':'factory','prior':'lnN','correlateAcrossYears':1},
		{'name':'metUncUncertainty','title':'CMS_hgg_MET_Unclustered','type':'factory','prior':'lnN','correlateAcrossYears':1},
	      ]

# THEORY SYSTEMATICS:

# For type:factory
# Tier system: adds different uncertainties to  dataFrame
#   1) shape: only tier used for STXS measurement. Integral of each STXS bin remains constant, looking for shape variations within one bin
#   2) ishape: (CHECK) inclusive shifts in each STXS bin x analysis category
#   3) norm: used for interpretation. Shifts in cross section of each STXS bin but inclusive cross-section for production mode remains constant.
#   4) inorm: (CHECK) inclusive shifts in each STXS bin
#   5) inc: (CHECK) inclusive shifts in each production mode

# Relations: shape = ishape/inorm
#            norm  = inorm/inc
# Specify as list in dict: e.g. 'tiers'=['inc','inorm','norm','ishape','shape']
theory_systematics = [ 
		{'name':'BR_hgg','title':'BR_hgg','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':"0.98/1.021"},
		#{'name':'THU_ggH_Mu','title':'CMS_hgg_THU_ggH_Mu','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['inorm']},
		#{'name':'THU_ggH_Res','title':'CMS_hgg_THU_ggH_Res','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['inorm']},
		#{'name':'THU_ggH_Mig01','title':'CMS_hgg_THU_ggH_Mig01','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['inorm']},
		#{'name':'THU_ggH_Mig12','title':'CMS_hgg_THU_ggH_Mig12','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['inorm']},
		#{'name':'THU_ggH_VBF2j','title':'CMS_hgg_THU_ggH_VBF2j','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['inorm']},
		#{'name':'THU_ggH_VBF3j','title':'CMS_hgg_THU_ggH_VBF3j','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['inorm']},
		#{'name':'THU_ggH_PT60','title':'CMS_hgg_THU_ggH_PT60','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['inorm']},
		#{'name':'THU_ggH_PT120','title':'CMS_hgg_THU_ggH_PT120','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['inorm']},
		#{'name':'THU_ggH_qmtop','title':'CMS_hgg_THU_ggH_qmtop','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['inorm']},
		# Scale weights are grouped: [1,2], [3,6], [4,8]
		#{'name':'scaleWeight_0','title':'CMS_hgg_scaleWeight_0','type':'factory','prior':'lnN','correlateAcrossYears':1}, # nominal weight
		{'name':'scaleWeight_1','title':'CMS_hgg_THU_scaleWeight_1','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape','mnorm']},
		{'name':'scaleWeight_2','title':'CMS_hgg_THU_scaleWeight_2','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape','mnorm']},
		{'name':'scaleWeight_3','title':'CMS_hgg_THU_scaleWeight_3','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape','mnorm']},
		{'name':'scaleWeight_4','title':'CMS_hgg_THU_scaleWeight_4','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape','mnorm']},
		#{'name':'scaleWeight_5','title':'CMS_hgg_scaleWeight_5','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['norm','shape']}, #Unphysical
		{'name':'scaleWeight_6','title':'CMS_hgg_THU_scaleWeight_6','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape','mnorm']},
		#{'name':'scaleWeight_7','title':'CMS_hgg_scaleWeight_7','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['norm','shape']}, #Unphysical
		{'name':'scaleWeight_8','title':'CMS_hgg_THU_scaleWeight_8','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape','mnorm']},
		{'name':'alphaSWeight_0','title':'CMS_hgg_alphaSWeight_0','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']},
		{'name':'alphaSWeight_1','title':'CMS_hgg_alphaSWeight_1','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']},
	      ]
for i in range(1,60): theory_systematics.append( {'name':'pdfWeight_%g'%i, 'title':'CMS_hgg_pdfWeight_%g'%i, 'type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']} )

def get_options():
  parser = OptionParser()
  parser.add_option('--mergeYears', dest='mergeYears', default=False, action="store_true", help="Merge specified categories across years")
  parser.add_option('--tagSplit', dest='tagSplit', default=False, action="store_true", help="If tags are split according to above splitting scheme")
  parser.add_option('--skipBkg', dest='skipBkg', default=False, action="store_true", help="Only add signal processes to datacard")
  parser.add_option('--prune', dest='prune', default=False, action="store_true", help="Prune proc x cat which make up less than pruneThreshold (default 0.1%) of given total category")
  parser.add_option('--pruneThreshold', dest='pruneThreshold', default=0.001, type='float', help="Threshold with which to prune proc x cat (yield/cat yield)")
  parser.add_option('--doSystematics', dest='doSystematics', default=False, action="store_true", help="Include systematics calculations and add to datacard")
  parser.add_option('--doSTXSBinMerging', dest='doSTXSBinMerging', default=False, action="store_true", help="Calculate additional normalisation systematics for merged STXS bins (specified in stxsBinMergingScheme)")
  parser.add_option('--removeNoTag', dest='removeNoTag', default=False, action="store_true", help="Remove processing of NoTag")
  parser.add_option('--years', dest='years', default='2016', help="Comma separated list of years")
  parser.add_option('--procs', dest='procs', default='', help='Comma separated list of signal processes')
  parser.add_option('--cats', dest='cats', default='', help='Comma separated list of analysis categories (no year tags)')
  parser.add_option('--modelWSDir', dest='modelWSDir', default='Models', help='Input model WS directory') 
  parser.add_option('--inputWSDir', dest='inputWSDir', default='/vols/cms/jl2117/hgg/ws/test_stage1_1', help='Input WS directory (without year tag _201X)') 
  parser.add_option('--saveDataFrame', dest='saveDataFrame', default='', help='Specify name of dataFrame if want to be saved') 
  parser.add_option('--loadDataFrame', dest='loadDataFrame', default='', help='Load dataFrame. Crucial generated with same options or likely to fail!') 
  return parser.parse_args()
(opt,args) = get_options()

# For loading dataframe
skipData = False
if opt.loadDataFrame != '':
  if os.path.exists("./hgg_dataFrames/%s.pkl"%opt.loadDataFrame): 
    print " .........................................................................................."
    print " --> [VERBOSE] Loading dataFrame: ./hgg_dataFrames/%s.pkl"%opt.loadDataFrame
    print " --> [WARNING] Please ensure use same options as when dataFrame was generated"
    with open("./hgg_dataFrames/%s.pkl"%opt.loadDataFrame,"rb") as fD: data = pickle.load(fD)
    skipData = True
  else:
    print " --> [ERROR] Could not load dataFrame: ./hgg_dataFrame/%s. Leaving..."%opt.loadDataFrame
    leave()

# Calculate dataFrame
if not skipData:
  # Check if input WS exist: adding year tag
  for year in opt.years.split(","):
    print " --> Will take %s signal workspaces from %s_%s"%(year,opt.inputWSDir,year)
    if not os.path.isdir( "%s_%s"%(opt.inputWSDir,year) ):
      print " --> [ERROR] Directory %s_%s does not exist. Leaving..."%(opt.inputWSDir,year)
      leave()

  # If procs are not specified then extract from inputWSDir (for each year):
  if opt.procs == '':
    procsByYear = {}
    wsFullFileNamesByYear = {}
    for year in opt.years.split(","):
      procsByYear[year] = []
      wsFullFileNamesByYear[year] = ''
      if opt.tagSplit: # only take procs from first tag set 
        inputWSDir = "%s_%s/%s"%(opt.inputWSDir,year,catsSplittingScheme.keys()[0])
        # Check if input dir exists
        if not os.path.isdir(inputWSDir): 
          print " --> [ERROR] Specified option tagSplit but %s does not exist. Leaving..."%inputWSDir
          leave()
      else: inputWSDir = "%s_%s"%(opt.inputWSDir,year)
      # Extract full list of input ws filenames
      ws_fileNames = []
      for root, dirs, files in os.walk( inputWSDir ):
	for fileName in files:
	  if not fileName.startswith('output_'): continue
	  if not fileName.endswith('.root'): continue 
	  ws_fileNames.append( fileName )
      # Concatenate with input dir to get full list of complete file names
      for fileName in ws_fileNames: wsFullFileNamesByYear[year] += "%s/%s,"%(inputWSDir,fileName)
      wsFullFileNamesByYear[year] = wsFullFileNamesByYear[year][:-1]

      # Extract processes from fileNames
      for fileName in ws_fileNames:
	if 'M125' not in fileName: continue
	procsByYear[year].append( fileName.split("pythia8_")[1].split(".root")[0] )  

      # FIXME: add check to see if tagsSplits have equal number of procs

      # Check equal and save as comma separated string
      if len(procsByYear) != 1:
	for year2 in procsByYear:
	  if year2 == year: continue
	  if set(procsByYear[year2]) != set(procsByYear[year]):
	    print " --> [ERROR] Mis-match in process for %s and %s. Intersection = %s"%(year,year2,(set(procsByYear[year2]).symmetric_difference(set(procsByYear[year]))))
	    leave()

      #Save as comma separated string
      opt.procs = ",".join(procsByYear[year])

  # Initiate pandas dataframe
  columns_data = ['year','type','proc','proc_s0','cat','inputWSFile','nominalDataName','modelWSFile','model','rate','prune']
  data = pd.DataFrame( columns=columns_data )


  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # FILL DATAFRAME: all processes
  print " .........................................................................................."

  # Add NOTAG to categories for signal: prune = 1
  cats_sig = opt.cats if opt.removeNoTag else "%s,NOTAG"%opt.cats

  # Signal processes
  for year in opt.years.split(","):
    for cat in cats_sig.split(","):
      for proc in opt.procs.split(","):
	# Mapping to STXS definition here
	_proc = "%s_%s_hgg"%(procToSTXS(proc),year)
	_proc_s0 = procToData(proc.split("_")[0])

	# If want to merge some categories
	if opt.mergeYears:
	  if cat in mergedYear_cats: _cat = cat
	  else: _cat = "%s_%s"%(cat,year)
	else: _cat = "%s_%s"%(cat,year)

	# Input flashgg ws
        if opt.tagSplit:
          if cat == "NOTAG":
            _inputWSFile = glob.glob("%s_%s/%s/*M125*%s*"%(opt.inputWSDir,year,catsSplittingScheme_NoTag,proc))[0]
            _nominalDataName = "%s_125_13TeV_%s"%(_proc_s0,cat)
          else: 
	    for splitname,splitcats in catsSplittingScheme.iteritems():
	      if cat in splitcats: 
		_inputWSFile = glob.glob("%s_%s/%s/*M125*%s*"%(opt.inputWSDir,year,splitname,proc))[0]
		_nominalDataName = "%s_125_13TeV_%s"%(_proc_s0,cat)
        else:
	  _inputWSFile = glob.glob("%s_%s/*M125*%s*"%(opt.inputWSDir,year,proc))[0]
	  _nominalDataName = "%s_125_13TeV_%s"%(_proc_s0,cat)

	# Input model ws 
	if cat == "NOTAG": _modelWSFile, _model = '-', '-'
	else:
	  _modelWSFile = "./%s/signal_%s/CMS-HGG_sigfit_mva_%s_%s.root"%(opt.modelWSDir,year,proc,cat)
	  _model = "wsig_13TeV:hggpdfsmrel_%s_13TeV_%s_%s"%(year,proc,cat)

	# Extract rate from lumi
	_rate = float(lumi[year])*1000

	# Prune NOTAG and if FWDH in process name
	if( cat == "NOTAG" )|( "FWDH" in proc ): _prune = 1
	else: _prune = 0

	# Add signal process to dataFrame:
	print " --> [VERBOSE] Adding to dataFrame: (proc,cat) = (%s,%s)"%(_proc,_cat)
	data.loc[len(data)] = [year,'sig',_proc,_proc_s0,_cat,_inputWSFile,_nominalDataName,_modelWSFile,_model,_rate,_prune]

  if not opt.skipBkg:
    # Background and data processes
    # Merged...
    if opt.mergeYears:
      for cat in opt.cats.split(","):
	_proc_bkg = "bkg_mass"
	_proc_data = "data_obs"
        if opt.tagSplit:
          for splitname,splitcats in catsSplittingScheme.iteritems():
            if cat in splitcats: _modelWSFile = "./%s/background_merged/CMS-HGG_mva_13TeV_multipdf_%s.root"%(opt.modelWSDir,splitname)
        else: _modelWSFile = "./%s/background_merged/CMS-HGG_mva_13TeV_multipdf.root"%opt.modelWSDir
	_inputWSFile = '-' #not needed for data/bkg
	_nominalDataName = '-' #not needed for data/bkg

	if cat in mergedYear_cats:
	  _cat = cat
	  _model_bkg = "multipdf:CMS_hgg_%s_13TeV_bkgshape"%_cat
	  _model_data = "multipdf:roohist_data_mass_%s"%_cat
	  print " --> [VERBOSE] Adding to dataFrame: (proc,cat) = (%s,%s)"%(_proc_bkg,_cat)
	  print " --> [VERBOSE] Adding to dataFrame: (proc,cat) = (%s,%s)"%(_proc_data,_cat)
	  data.loc[len(data)] = ["merged",'bkg',_proc_bkg,'-',_cat,_inputWSFile,_nominalDataName,_modelWSFile,_model_bkg,1.,0]
	  data.loc[len(data)] = ["merged",'data',_proc_data,'-',_cat,_inputWSFile,_nominalDataName,_modelWSFile,_model_data,-1,0]
	else:
	  # Loop over years and fill entry per year
	  for year in opt.years.split(","):
	    _cat = "%s_%s"%(cat,year)
	    _model_bkg = "multipdf:CMS_hgg_%s_13TeV_bkgshape"%_cat
	    _model_data = "multipdf:roohist_data_mass_%s"%_cat
	    print " --> [VERBOSE] Adding to dataFrame: (proc,cat) = (%s,%s)"%(_proc_bkg,_cat)
	    print " --> [VERBOSE] Adding to dataFrame: (proc,cat) = (%s,%s)"%(_proc_data,_cat)
	    data.loc[len(data)] = [year,'bkg',_proc_bkg,'-',_cat,_inputWSFile,_nominalDataName,_modelWSFile,_model_bkg,1.,0]
	    data.loc[len(data)] = [year,'data',_proc_data,'-',_cat,_inputWSFile,_nominalDataName,_modelWSFile,_model_data,-1,0] 
    # Fully separate: i.e. processed separately in FinalFits
    else:
      for cat in opt.cats.split(","):
	_proc_bkg = "bkg_mass"
	_proc_data = "data_obs"
	# Loop over years and fill entry per year
	for year in opt.years.split(","):
	  # FIXME: change year tag to after sqrts to suit current models
	  _cat = "%s_%s"%(cat,year)
	  _catStripYear = cat
	  if opt.tagSplit:
	    for splitname,splitcats in catsSplittingScheme.iteritems():
	      if cat in splitcats: _modelWSFile = "./%s/background_%s/CMS-HGG_mva_13TeV_multipdf_%s.root"%(opt.modelWSDir,year,splitname)
	  else: _modelWSFile = "./%s/background_%s/CMS-HGG_mva_13TeV_multipdf.root"%(opt.modelWSDir,year)
	  _inputWSFile = '-' #not needed for data/bk
	  _nominalDataName = '-' #not needed for data/bkg
	  _model_bkg = "multipdf:CMS_hgg_%s_13TeV_bkgshape"%_cat
	  #_model_bkg = "multipdf:CMS_hgg_%s_13TeV_%s_bkgshape"%(_catStripYear,year)
	  _model_data = "multipdf:roohist_data_mass_%s"%_catStripYear
	  print " --> [VERBOSE] Adding to dataFrame: (proc,cat) = (%s,%s)"%(_proc_bkg,_cat)
	  print " --> [VERBOSE] Adding to dataFrame: (proc,cat) = (%s,%s)"%(_proc_data,_cat)
	  data.loc[len(data)] = [year,'bkg',_proc_bkg,'-',_cat,_inputWSFile,_nominalDataName,_modelWSFile,_model_bkg,1.,0]
	  data.loc[len(data)] = [year,'data',_proc_data,'-',_cat,_inputWSFile,_nominalDataName,_modelWSFile,_model_data,-1,0]

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # Yields: for each signal row in dataFrame extract the yield
  print " .........................................................................................."
  #   * if systematics=True: also extract reweighted yields for each uncertainty source
  from calcSystematics import factoryType, calcSystYields

  # Create columns in dataFrame to store yields
  data['nominal_yield'] = '-'

  # Depending on type of systematic: anti-symmetric = 2 (up/down) columns, symmetric = 1 column
  #   * store factoryType of systematic in dictionary
  experimentalFactoryType = {}
  theoryFactoryType = {}
  if opt.doSystematics:
    # Extract first row of signal dataframe and use factoryType function to extract type of systematic
    for s in experimental_systematics: 
      if s['type'] == 'factory': 
	experimentalFactoryType[s['name']] = factoryType(data,s)
	if experimentalFactoryType[s['name']] in ["a_w","a_h"]:
	  data['%s_up_yield'%s['name']] = '-'
	  data['%s_down_yield'%s['name']] = '-'
	else: data['%s_yield'%s['name']] = '-'
    for s in theory_systematics: 
      if s['type'] == 'factory': 
	theoryFactoryType[s['name']] = factoryType(data,s)
	if theoryFactoryType[s['name']] in ["a_w","a_h"]:
	  data['%s_up_yield'%s['name']] = '-'
	  data['%s_down_yield'%s['name']] = '-'
	else: data['%s_yield'%s['name']] = '-'

  # Loop over signal rows in dataFrame: extract yields (nominal & systematic variations)
  totalSignalRows = float(data[data['type']=='sig'].shape[0])
  for ir,r in data[data['type']=='sig'].iterrows():

    print " --> [VERBOSE] Extracting yields: (%s,%s) [%.1f%%]"%(r['proc'],r['cat'],100*(float(ir)/totalSignalRows))

    # Open input WS file and extract workspace
    f_in = ROOT.TFile(r.inputWSFile)
    inputWS = f_in.Get("tagsDumper/cms_hgg_13TeV")
    # Extract nominal RooDataSet and yield
    rdata_nominal = inputWS.data(r.nominalDataName)
    data.at[ir,'nominal_yield'] = rdata_nominal.sumEntries()
    
    # Systematics: loop over systematics and use function to extract yield variations
    if opt.doSystematics:
      # For experimental systematics: skip NOTAG (as incorrect weights)
      if "NOTAG" not in r['cat']:
        # FIXME: added fix for ggH experimental yields, centralObjectWeight bug
        if r['proc_s0'] == 'ggh': experimentalSystYields = calcSystYields(r['nominalDataName'],inputWS,experimentalFactoryType,ggHFix=True)
        else: experimentalSystYields = calcSystYields(r['nominalDataName'],inputWS,experimentalFactoryType,ggHFix=False)
	for s,f in experimentalFactoryType.iteritems():
	  if f in ['a_w','a_h']: 
	    for direction in ['up','down']: 
	      data.at[ir,"%s_%s_yield"%(s,direction)] = experimentalSystYields["%s_%s"%(s,direction)]
	  else:
	    data.at[ir,"%s_yield"%s] = experimentalSystYields[s]
      # For theoretical systematics:
      theorySystYields = calcSystYields(r['nominalDataName'],inputWS,theoryFactoryType)
      for s,f in theoryFactoryType.iteritems():
	if f in ['a_w','a_h']: 
	  for direction in ['up','down']: 
	    data.at[ir,"%s_%s_yield"%(s,direction)] = theorySystYields["%s_%s"%(s,direction)]
	else:
	  data.at[ir,"%s_yield"%s] = theorySystYields[s]

    # Remove the workspace and file from heap
    inputWS.Delete()
    f_in.Delete()
    f_in.Close()

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # Systematics: use factory function to calculate yield variations
  print " .........................................................................................."
  from calcSystematics import addConstantSyst, experimentalSystFactory, theorySystFactory, groupSystematics

  if opt.doSystematics:

    # Experimental:
    print " --> [VERBOSE] Adding experimental systematics variations to dataFrame"
    # Add constant systematics to dataFrame
    for s in experimental_systematics:
      if s['type'] == 'constant': data = addConstantSyst(data,s,opt)
    data = experimentalSystFactory(data, experimental_systematics, experimentalFactoryType, opt )

    # Theory:
    print " --> [VERBOSE] Adding theory systematics variations to dataFrame"
    # Add constant systematics to dataFrame
    for s in theory_systematics:
      if s['type'] == 'constant': data = addConstantSyst(data,s,opt)
    # Theory factory: group scale weights after calculation in relevant grouping scheme
    if opt.doSTXSBinMerging: 
      data = theorySystFactory(data, theory_systematics, theoryFactoryType, opt, stxsMergeScheme=stxsBinMergingScheme )
      data, theory_systematics = groupSystematics(data, theory_systematics, opt, prefix="scaleWeight", groupings=[[1,2],[3,6],[4,8]], stxsMergeScheme=stxsBinMergingScheme)
      data, theory_systematics = groupSystematics(data, theory_systematics, opt, prefix="alphaSWeight", groupings=[[0,1]], stxsMergeScheme=stxsBinMergingScheme)
    else: 
      data = theorySystFactory(data, theory_systematics, theoryFactoryType, opt)
      data, theory_systematics = groupSystematics(data, theory_systematics, opt, prefix="scaleWeight", groupings=[[1,2],[3,6],[4,8]])
      data, theory_systematics = groupSystematics(data, theory_systematics, opt, prefix="alphaSWeight", groupings=[[0,1]])

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # Pruning: if process contributes less than 0.1% of yield in analysis category then ignore
  print " .........................................................................................."
  if opt.prune:
    print " --> [VERBOSE] Pruning processes which contribute < 0.1% of RECO category yield"
    # Extract per category yields
    catYields = {}
    for cat in data.cat.unique(): catYields[cat] = data[(data['cat']==cat)&(data['type']=='sig')].nominal_yield.sum()
    # Set prune = 1 if < 0.1% of total cat yield
    mask = (data['nominal_yield']<opt.pruneThreshold*data.apply(lambda x: catYields[x['cat']], axis=1))&(data['type']=='sig')
    data.loc[mask,'prune'] = 1

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# WRITE TO .TXT FILE
print " .........................................................................................."
fdataName = "Datacard_dummy.txt"
print " --> [VERBOSE] Writing to datacard file: %s"%fdataName
from writeToDatacard import writePreamble, writeProcesses, writeSystematic, writePdfIndex, writeBreak
fdata = open(fdataName,"w")
if not writePreamble(fdata,opt): 
  print " --> [ERROR] in writing preamble. Leaving..."
  leave()
if not writeProcesses(fdata,data,opt):
  print " --> [ERROR] in writing processes. Leaving..."
  leave()
if opt.doSystematics:
  for syst in experimental_systematics:
    if not writeSystematic(fdata,data,syst,opt):
      print " --> [ERROR] in writing systematic %s (experiment). Leaving"%syst['name']
      leave()
  writeBreak(fdata)
  for syst in theory_systematics:
    if opt.doSTXSBinMerging:
      if not writeSystematic(fdata,data,syst,opt,stxsMergeScheme=stxsBinMergingScheme):
	print " --> [ERROR] in writing systematic %s (theory). Leaving"%syst['name']
	leave()
    else:
      if not writeSystematic(fdata,data,syst,opt):
	print " --> [ERROR] in writing systematic %s (theory). Leaving"%syst['name']
	leave()
  writeBreak(fdata)
  for syst in signal_shape_systematics:
    if not writeSystematic(fdata,data,syst,opt):
      print " --> [ERROR] in writing systematic %s (signal shape). Leaving"%syst['name']
      leave()
if not writePdfIndex(fdata,data,opt):
  print " --> [ERROR] in writing pdf indices. Leaving..."
  leave()
fdata.close()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SAVE DATAFRAME
if opt.saveDataFrame != '':
  print " .........................................................................................."
  print " --> [VERBOSE] Saving dataFrame: ./hgg_dataFrames/%s.pkl"%opt.saveDataFrame
  if not os.path.isdir("./hgg_dataFrames"): os.system("mkdir ./hgg_dataFrames")
  with open("./hgg_dataFrames/%s.pkl"%opt.saveDataFrame,"wb") as fD: pickle.dump(data,fD)

