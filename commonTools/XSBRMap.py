# Python script to hold XS * BR for normalisation of signal models
from collections import OrderedDict as od
from commonObjects import *
  
# Add analyses to globalReplacementMap. See "STXS" as an example
globalXSBRMap = od()

# For case of fixed xs/br Use 'mode':constant 'factor':X e.g.
#globalXSBRMap['example'] = od()
#globalXSBRMap['example']['decay'] = {'mode':'constant','factor':1}
#globalXSBRMap['example']['PROCNAME'] = {'mode':'constant','factor':0.001}

# For case of inclusive production mode then have no additional factor beyond V branching ratios
globalXSBRMap['example'] = od()
globalXSBRMap['example']['decay'] = {'mode':'hgg'}
globalXSBRMap['example']['GG2H'] = {'mode':'ggH'}
globalXSBRMap['example']['VBF'] = {'mode':'qqH'}
globalXSBRMap['example']['WH2HQQ'] = {'mode':'WH','factor':BR_W_qq}
globalXSBRMap['example']['ZH2HQQ'] = {'mode':'qqZH','factor':BR_Z_qq}
globalXSBRMap['example']['QQ2HLNU'] = {'mode':'WH','factor':BR_W_lnu}
globalXSBRMap['example']['QQ2HLL'] = {'mode':'qqZH','factor':(BR_Z_ll+BR_Z_nunu)}
globalXSBRMap['example']['GG2HQQ'] = {'mode':'ggZH','factor':BR_Z_qq}
globalXSBRMap['example']['GG2HLL'] = {'mode':'ggZH','factor':BR_Z_ll}
globalXSBRMap['example']['GG2HNUNU'] = {'mode':'ggZH','factor':BR_Z_nunu}
globalXSBRMap['example']['TTH'] = {'mode':'ttH'}
globalXSBRMap['example']['BBH'] = {'mode':'bbH'}
globalXSBRMap['example']['THQ'] = {'mode':'tHq'}
globalXSBRMap['example']['THW'] = {'mode':'tHW'}
# ...

# For tutorial analysis: use 13.6 TeV cross sections and branching fraction
# These are not yet stored in Combine, so we will use the constant-factor approach 
# Setting the values at MH=125.38 GeV
globalXSBRMap['tutorial'] = od()
globalXSBRMap['tutorial']['decay'] = {'mode':'hgg'}
globalXSBRMap['tutorial']['GG2H'] = {'mode':'constant', 'factor':51.96}
globalXSBRMap['tutorial']['VBF'] = {'mode':'constant', 'factor':4.067}

# STXS analysis: add factor for bin composition
globalXSBRMap['STXS'] = od()
globalXSBRMap['STXS']['decay'] = {'mode':'hgg'}
# ggH STXS stage 1.2 bins
globalXSBRMap['STXS']['GG2H_FWDH'] = {'mode':'ggH','factor':0.0809}
globalXSBRMap['STXS']['GG2H_PTH_200_300'] = {'mode':'ggH','factor':0.0098}
globalXSBRMap['STXS']['GG2H_PTH_300_450'] = {'mode':'ggH','factor':0.0025}
globalXSBRMap['STXS']['GG2H_PTH_450_650'] = {'mode':'ggH','factor':0.0003}
globalXSBRMap['STXS']['GG2H_PTH_GT650'] = {'mode':'ggH','factor':0.0001}
globalXSBRMap['STXS']['GG2H_0J_PTH_0_10'] = {'mode':'ggH','factor':0.1387}
globalXSBRMap['STXS']['GG2H_0J_PTH_GT10'] = {'mode':'ggH','factor':0.3940}
globalXSBRMap['STXS']['GG2H_1J_PTH_0_60'] = {'mode':'ggH','factor':0.1477}
globalXSBRMap['STXS']['GG2H_1J_PTH_60_120'] = {'mode':'ggH','factor':0.1023}
globalXSBRMap['STXS']['GG2H_1J_PTH_120_200'] = {'mode':'ggH','factor':0.0182}
globalXSBRMap['STXS']['GG2H_GE2J_MJJ_0_350_PTH_0_60'] = {'mode':'ggH','factor':0.0256}
globalXSBRMap['STXS']['GG2H_GE2J_MJJ_0_350_PTH_60_120'] = {'mode':'ggH','factor':0.0410}
globalXSBRMap['STXS']['GG2H_GE2J_MJJ_0_350_PTH_120_200'] = {'mode':'ggH','factor':0.0188}
globalXSBRMap['STXS']['GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'ggH','factor':0.0063}
globalXSBRMap['STXS']['GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'ggH','factor':0.0077}
globalXSBRMap['STXS']['GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'ggH','factor':0.0028}
globalXSBRMap['STXS']['GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'ggH','factor':0.0032}
# ggZH hadronic: merged with ggH STXS stage 1.2 bins in fit
globalXSBRMap['STXS']['GG2HQQ_FWDH'] = {'mode':'ggZH','factor':0.0273*BR_Z_qq}
globalXSBRMap['STXS']['GG2HQQ_PTH_200_300'] = {'mode':'ggZH','factor':0.1393*BR_Z_qq}
globalXSBRMap['STXS']['GG2HQQ_PTH_300_450'] = {'mode':'ggZH','factor':0.0386*BR_Z_qq}
globalXSBRMap['STXS']['GG2HQQ_PTH_450_650'] = {'mode':'ggZH','factor':0.0077*BR_Z_qq}
globalXSBRMap['STXS']['GG2HQQ_PTH_GT650'] = {'mode':'ggZH','factor':0.0020*BR_Z_qq}
globalXSBRMap['STXS']['GG2HQQ_0J_PTH_0_10'] = {'mode':'ggZH','factor':0.0001*BR_Z_qq}
globalXSBRMap['STXS']['GG2HQQ_0J_PTH_GT10'] = {'mode':'ggZH','factor':0.0029*BR_Z_qq}
globalXSBRMap['STXS']['GG2HQQ_1J_PTH_0_60'] = {'mode':'ggZH','factor':0.0200*BR_Z_qq}
globalXSBRMap['STXS']['GG2HQQ_1J_PTH_60_120'] = {'mode':'ggZH','factor':0.0534*BR_Z_qq}
globalXSBRMap['STXS']['GG2HQQ_1J_PTH_120_200'] = {'mode':'ggZH','factor':0.0353*BR_Z_qq}
globalXSBRMap['STXS']['GG2HQQ_GE2J_MJJ_0_350_PTH_0_60'] = {'mode':'ggZH','factor':0.0574*BR_Z_qq}
globalXSBRMap['STXS']['GG2HQQ_GE2J_MJJ_0_350_PTH_60_120'] = {'mode':'ggZH','factor':0.1963*BR_Z_qq}
globalXSBRMap['STXS']['GG2HQQ_GE2J_MJJ_0_350_PTH_120_200'] = {'mode':'ggZH','factor':0.2954*BR_Z_qq}
globalXSBRMap['STXS']['GG2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'ggZH','factor':0.0114*BR_Z_qq}
globalXSBRMap['STXS']['GG2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'ggZH','factor':0.0806*BR_Z_qq}
globalXSBRMap['STXS']['GG2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'ggZH','factor':0.0036*BR_Z_qq}
globalXSBRMap['STXS']['GG2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'ggZH','factor':0.0285*BR_Z_qq}
# qqH STXS stage 1.2 bins: including (qq)VH hadronic processes
globalXSBRMap['STXS']['VBF_FWDH'] = {'mode':'qqH','factor':0.0669}
globalXSBRMap['STXS']['VBF_0J'] = {'mode':'qqH','factor':0.0695}
globalXSBRMap['STXS']['VBF_1J'] = {'mode':'qqH','factor':0.3283}
globalXSBRMap['STXS']['VBF_GE2J_MJJ_0_60'] = {'mode':'qqH','factor':0.0136}
globalXSBRMap['STXS']['VBF_GE2J_MJJ_60_120'] = {'mode':'qqH','factor':0.0240}
globalXSBRMap['STXS']['VBF_GE2J_MJJ_120_350'] = {'mode':'qqH','factor':0.1234}
globalXSBRMap['STXS']['VBF_GE2J_MJJ_GT350_PTH_GT200'] = {'mode':'qqH','factor':0.0398}
globalXSBRMap['STXS']['VBF_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'qqH','factor':0.1026}
globalXSBRMap['STXS']['VBF_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'qqH','factor':0.0385}
globalXSBRMap['STXS']['VBF_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'qqH','factor':0.1509}
globalXSBRMap['STXS']['VBF_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'qqH','factor':0.0425}
globalXSBRMap['STXS']['WH2HQQ_FWDH'] = {'mode':'WH','factor':0.1257*BR_W_qq}
globalXSBRMap['STXS']['WH2HQQ_0J'] = {'mode':'WH','factor':0.0570*BR_W_qq}
globalXSBRMap['STXS']['WH2HQQ_1J'] = {'mode':'WH','factor':0.3113*BR_W_qq}
globalXSBRMap['STXS']['WH2HQQ_GE2J_MJJ_0_60'] = {'mode':'WH','factor':0.0358*BR_W_qq}
globalXSBRMap['STXS']['WH2HQQ_GE2J_MJJ_60_120'] = {'mode':'WH','factor':0.2943*BR_W_qq}
globalXSBRMap['STXS']['WH2HQQ_GE2J_MJJ_120_350'] = {'mode':'WH','factor':0.1392*BR_W_qq}
globalXSBRMap['STXS']['WH2HQQ_GE2J_MJJ_GT350_PTH_GT200'] = {'mode':'WH','factor':0.0088*BR_W_qq}
globalXSBRMap['STXS']['WH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'WH','factor':0.0044*BR_W_qq}
globalXSBRMap['STXS']['WH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'WH','factor':0.0186*BR_W_qq}
globalXSBRMap['STXS']['WH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'WH','factor':0.0009*BR_W_qq}
globalXSBRMap['STXS']['WH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'WH','factor':0.0040*BR_W_qq}
globalXSBRMap['STXS']['ZH2HQQ_FWDH'] = {'mode':'qqZH','factor':0.1143*BR_Z_qq}
globalXSBRMap['STXS']['ZH2HQQ_0J'] = {'mode':'qqZH','factor':0.0433*BR_Z_qq}
globalXSBRMap['STXS']['ZH2HQQ_1J'] = {'mode':'qqZH','factor':0.2906*BR_Z_qq}
globalXSBRMap['STXS']['ZH2HQQ_GE2J_MJJ_0_60'] = {'mode':'qqZH','factor':0.0316*BR_Z_qq}
globalXSBRMap['STXS']['ZH2HQQ_GE2J_MJJ_60_120'] = {'mode':'qqZH','factor':0.3360*BR_Z_qq}
globalXSBRMap['STXS']['ZH2HQQ_GE2J_MJJ_120_350'] = {'mode':'qqZH','factor':0.1462*BR_Z_qq}
globalXSBRMap['STXS']['ZH2HQQ_GE2J_MJJ_GT350_PTH_GT200'] = {'mode':'qqZH','factor':0.0083*BR_Z_qq}
globalXSBRMap['STXS']['ZH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'qqZH','factor':0.0041*BR_Z_qq}
globalXSBRMap['STXS']['ZH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'qqZH','factor':0.0202*BR_Z_qq}
globalXSBRMap['STXS']['ZH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'qqZH','factor':0.0009*BR_Z_qq}
globalXSBRMap['STXS']['ZH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'qqZH','factor':0.0045*BR_Z_qq}
# WH lep STXS stage 1.2 bins
globalXSBRMap['STXS']['QQ2HLNU_FWDH'] = {'mode':'WH','factor':0.1213*BR_W_lnu}
globalXSBRMap['STXS']['QQ2HLNU_PTV_0_75'] = {'mode':'WH','factor':0.4655*BR_W_lnu}
globalXSBRMap['STXS']['QQ2HLNU_PTV_75_150'] = {'mode':'WH','factor':0.2930*BR_W_lnu}
globalXSBRMap['STXS']['QQ2HLNU_PTV_150_250_0J'] = {'mode':'WH','factor':0.0510*BR_W_lnu}
globalXSBRMap['STXS']['QQ2HLNU_PTV_150_250_GE1J'] = {'mode':'WH','factor':0.0397*BR_W_lnu}
globalXSBRMap['STXS']['QQ2HLNU_PTV_GT250'] = {'mode':'WH','factor':0.0295*BR_W_lnu}
# (qq)ZH lep STXS stage 1.2 bins
globalXSBRMap['STXS']['QQ2HLL_FWDH'] = {'mode':'qqZH','factor':0.1121*(BR_Z_ll+BR_Z_nunu)}
globalXSBRMap['STXS']['QQ2HLL_PTV_0_75'] = {'mode':'qqZH','factor':0.4565*(BR_Z_ll+BR_Z_nunu)}
globalXSBRMap['STXS']['QQ2HLL_PTV_75_150'] = {'mode':'qqZH','factor':0.3070*(BR_Z_ll+BR_Z_nunu)}
globalXSBRMap['STXS']['QQ2HLL_PTV_150_250_0J'] = {'mode':'qqZH','factor':0.0516*(BR_Z_ll+BR_Z_nunu)}
globalXSBRMap['STXS']['QQ2HLL_PTV_150_250_GE1J'] = {'mode':'qqZH','factor':0.0427*(BR_Z_ll+BR_Z_nunu)}
globalXSBRMap['STXS']['QQ2HLL_PTV_GT250'] = {'mode':'qqZH','factor':0.0301*(BR_Z_ll+BR_Z_nunu)}
# gg(ZH) lep STXS stage 1.2 bins: separate processes for ll and nunu decays
globalXSBRMap['STXS']['GG2HLL_FWDH'] = {'mode':'ggZH','factor':0.0270*BR_Z_ll}
globalXSBRMap['STXS']['GG2HLL_PTV_0_75'] = {'mode':'ggZH','factor':0.1605*BR_Z_ll}
globalXSBRMap['STXS']['GG2HLL_PTV_75_150'] = {'mode':'ggZH','factor':0.4325*BR_Z_ll}
globalXSBRMap['STXS']['GG2HLL_PTV_150_250_0J'] = {'mode':'ggZH','factor':0.0913*BR_Z_ll}
globalXSBRMap['STXS']['GG2HLL_PTV_150_250_GE1J'] = {'mode':'ggZH','factor':0.2044*BR_Z_ll}
globalXSBRMap['STXS']['GG2HLL_PTV_GT250'] = {'mode':'ggZH','factor':0.0844*BR_Z_ll}
globalXSBRMap['STXS']['GG2HNUNU_FWDH'] = {'mode':'ggZH','factor':0.0271*BR_Z_nunu}
globalXSBRMap['STXS']['GG2HNUNU_PTV_0_75'] = {'mode':'ggZH','factor':0.1591*BR_Z_nunu}
globalXSBRMap['STXS']['GG2HNUNU_PTV_75_150'] = {'mode':'ggZH','factor':0.4336*BR_Z_nunu}
globalXSBRMap['STXS']['GG2HNUNU_PTV_150_250_0J'] = {'mode':'ggZH','factor':0.0905*BR_Z_nunu}
globalXSBRMap['STXS']['GG2HNUNU_PTV_150_250_GE1J'] = {'mode':'ggZH','factor':0.2051*BR_Z_nunu}
globalXSBRMap['STXS']['GG2HNUNU_PTV_GT250'] = {'mode':'ggZH','factor':0.0845*BR_Z_nunu}
# ttH STXS stage 1.2 bins
globalXSBRMap['STXS']['TTH_FWDH'] = {'mode':'ttH','factor':0.0135}
globalXSBRMap['STXS']['TTH_PTH_0_60'] = {'mode':'ttH','factor':0.2250}
globalXSBRMap['STXS']['TTH_PTH_60_120'] = {'mode':'ttH','factor':0.3473}
globalXSBRMap['STXS']['TTH_PTH_120_200'] = {'mode':'ttH','factor':0.2569}
globalXSBRMap['STXS']['TTH_PTH_200_300'] = {'mode':'ttH','factor':0.1076}
globalXSBRMap['STXS']['TTH_PTH_GT300'] = {'mode':'ttH','factor':0.0533}
# bbH STXS stage 1.2 bins
globalXSBRMap['STXS']['BBH_FWDH'] = {'mode':'bbH','factor':0.0487}
globalXSBRMap['STXS']['BBH'] = {'mode':'bbH','factor':0.9513}
# tH STXS stage 1.2 bins: tHq + tHW
globalXSBRMap['STXS']['THQ_FWDH'] = {'mode':'tHq','factor':0.0279}
globalXSBRMap['STXS']['THQ'] = {'mode':'tHq','factor':0.9721}
globalXSBRMap['STXS']['THW_FWDH'] = {'mode':'tHW','factor':0.0106}
globalXSBRMap['STXS']['THW'] = {'mode':'tHW','factor':0.9894}



###################################################################################################################################################################################################
###################################################################################################################################################################################################
###################################################################################################################################################################################################
# Run 3 Fiducial XS analysis: use 13.6 TeV cross sections and branching fraction

globalXSBRMap['Run3FidXSAnalysis'] = od()
globalXSBRMap['Run3FidXSAnalysis']['decay'] = {'mode':'hgg'}
globalXSBRMap['Run3FidXSAnalysis']['GG2H'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['VBF'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['VH'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['TTH'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['BBH'] = {'mode':'constant','factor':0.49}




globalXSBRMap['Run3FidXSAnalysis']['ggh_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['vbf_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vh_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['tth_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['bbh_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['ggh_out'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['vbf_out'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vh_out'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['tth_out'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['bbh_out'] = {'mode':'constant','factor':0.49}




globalXSBRMap['Run3FidXSAnalysis']['ggh_PTH_0p0_15p0_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_PTH_15p0_30p0_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_PTH_30p0_45p0_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_PTH_45p0_80p0_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_PTH_80p0_120p0_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_PTH_120p0_200p0_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_PTH_200p0_350p0_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_PTH_350p0_10000p0_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_PTH_0p0_10000p0_out'] = {'mode':'constant','factor':51.96}

globalXSBRMap['Run3FidXSAnalysis']['vbf_PTH_0p0_15p0_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_PTH_15p0_30p0_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_PTH_30p0_45p0_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_PTH_45p0_80p0_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_PTH_80p0_120p0_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_PTH_120p0_200p0_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_PTH_200p0_350p0_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_PTH_350p0_10000p0_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_PTH_0p0_10000p0_out'] = {'mode':'constant','factor':4.067}

globalXSBRMap['Run3FidXSAnalysis']['vh_PTH_0p0_15p0_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_PTH_15p0_30p0_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_PTH_30p0_45p0_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_PTH_45p0_80p0_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_PTH_80p0_120p0_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_PTH_120p0_200p0_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_PTH_200p0_350p0_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_PTH_350p0_10000p0_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_PTH_0p0_10000p0_out'] = {'mode':'constant','factor':2.3781}

globalXSBRMap['Run3FidXSAnalysis']['tth_PTH_0p0_15p0_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_PTH_15p0_30p0_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_PTH_30p0_45p0_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_PTH_45p0_80p0_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_PTH_80p0_120p0_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_PTH_120p0_200p0_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_PTH_200p0_350p0_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_PTH_350p0_10000p0_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_PTH_0p0_10000p0_out'] = {'mode':'constant','factor':0.5638}

globalXSBRMap['Run3FidXSAnalysis']['bbh_PTH_0p0_15p0_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_PTH_15p0_30p0_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_PTH_30p0_45p0_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_PTH_45p0_80p0_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_PTH_80p0_120p0_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_PTH_120p0_200p0_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_PTH_200p0_350p0_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_PTH_350p0_10000p0_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_PTH_0p0_10000p0_out'] = {'mode':'constant','factor':0.49}




globalXSBRMap['Run3FidXSAnalysis']['ggh_YH_0p0_0p15_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_YH_0p15_0p3_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_YH_0p3_0p6_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_YH_0p6_0p9_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_YH_0p9_2p5_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_YH_0p0_2p5_out'] = {'mode':'constant','factor':51.96}

globalXSBRMap['Run3FidXSAnalysis']['vbf_YH_0p0_0p15_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_YH_0p15_0p3_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_YH_0p3_0p6_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_YH_0p6_0p9_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_YH_0p9_2p5_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_YH_0p0_2p5_out'] = {'mode':'constant','factor':4.067}

globalXSBRMap['Run3FidXSAnalysis']['vh_YH_0p0_0p15_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_YH_0p15_0p3_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_YH_0p3_0p6_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_YH_0p6_0p9_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_YH_0p9_2p5_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_YH_0p0_2p5_out'] = {'mode':'constant','factor':2.3781}

globalXSBRMap['Run3FidXSAnalysis']['tth_YH_0p0_0p15_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_YH_0p15_0p3_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_YH_0p3_0p6_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_YH_0p6_0p9_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_YH_0p9_2p5_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_YH_0p0_2p5_out'] = {'mode':'constant','factor':0.5638}

globalXSBRMap['Run3FidXSAnalysis']['bbh_YH_0p0_0p15_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_YH_0p15_0p3_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_YH_0p3_0p6_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_YH_0p6_0p9_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_YH_0p9_2p5_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_YH_0p0_2p5_out'] = {'mode':'constant','factor':0.49}




globalXSBRMap['Run3FidXSAnalysis']['ggh_NJ_0p0_1p0_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_NJ_1p0_2p0_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_NJ_2p0_3p0_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_NJ_3p0_100p0_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_NJ_0p0_100p0_out'] = {'mode':'constant','factor':51.96}

globalXSBRMap['Run3FidXSAnalysis']['vbf_NJ_0p0_1p0_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_NJ_1p0_2p0_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_NJ_2p0_3p0_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_NJ_3p0_100p0_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_NJ_0p0_100p0_out'] = {'mode':'constant','factor':4.067}

globalXSBRMap['Run3FidXSAnalysis']['vh_NJ_0p0_1p0_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_NJ_1p0_2p0_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_NJ_2p0_3p0_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_NJ_3p0_100p0_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_NJ_0p0_100p0_out'] = {'mode':'constant','factor':2.3781}

globalXSBRMap['Run3FidXSAnalysis']['tth_NJ_0p0_1p0_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_NJ_1p0_2p0_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_NJ_2p0_3p0_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_NJ_3p0_100p0_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_NJ_0p0_100p0_out'] = {'mode':'constant','factor':0.5638}

globalXSBRMap['Run3FidXSAnalysis']['bbh_NJ_0p0_1p0_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_NJ_1p0_2p0_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_NJ_2p0_3p0_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_NJ_3p0_100p0_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_NJ_0p0_100p0_out'] = {'mode':'constant','factor':0.49}




globalXSBRMap['Run3FidXSAnalysis']['ggh_PTJ0_0p0_30p0_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_PTJ0_30p0_75p0_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_PTJ0_75p0_120p0_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_PTJ0_120p0_200p0_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_PTJ0_200p0_10000p0_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_PTJ0_0p0_10000p0_out'] = {'mode':'constant','factor':51.96}

globalXSBRMap['Run3FidXSAnalysis']['vbf_PTJ0_0p0_30p0_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_PTJ0_30p0_75p0_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_PTJ0_75p0_120p0_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_PTJ0_120p0_200p0_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_PTJ0_200p0_10000p0_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_PTJ0_0p0_10000p0_out'] = {'mode':'constant','factor':4.067}

globalXSBRMap['Run3FidXSAnalysis']['vh_PTJ0_0p0_30p0_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_PTJ0_30p0_75p0_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_PTJ0_75p0_120p0_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_PTJ0_120p0_200p0_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_PTJ0_200p0_10000p0_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_PTJ0_0p0_10000p0_out'] = {'mode':'constant','factor':2.3781}

globalXSBRMap['Run3FidXSAnalysis']['tth_PTJ0_0p0_30p0_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_PTJ0_30p0_75p0_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_PTJ0_75p0_120p0_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_PTJ0_120p0_200p0_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_PTJ0_200p0_10000p0_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_PTJ0_0p0_10000p0_out'] = {'mode':'constant','factor':0.5638}

globalXSBRMap['Run3FidXSAnalysis']['bbh_PTJ0_0p0_30p0_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_PTJ0_30p0_75p0_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_PTJ0_75p0_120p0_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_PTJ0_120p0_200p0_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_PTJ0_200p0_10000p0_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_PTJ0_0p0_10000p0_out'] = {'mode':'constant','factor':0.49}




globalXSBRMap['Run3FidXSAnalysis']['ggh_YJ0_0p0_0p5_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_YJ0_0p5_1p2_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_YJ0_1p2_2p0_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_YJ0_2p0_2p5_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_YJ0_NJ0_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_YJ0_0p0_2p5_out'] = {'mode':'constant','factor':51.96}

globalXSBRMap['Run3FidXSAnalysis']['vbf_YJ0_0p0_0p5_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_YJ0_0p5_1p2_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_YJ0_1p2_2p0_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_YJ0_2p0_2p5_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_YJ0_NJ0_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_YJ0_0p0_2p5_out'] = {'mode':'constant','factor':4.067}

globalXSBRMap['Run3FidXSAnalysis']['vh_YJ0_0p0_0p5_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_YJ0_0p5_1p2_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_YJ0_1p2_2p0_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_YJ0_2p0_2p5_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_YJ0_NJ0_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_YJ0_0p0_2p5_out'] = {'mode':'constant','factor':2.3781}

globalXSBRMap['Run3FidXSAnalysis']['tth_YJ0_0p0_0p5_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_YJ0_0p5_1p2_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_YJ0_1p2_2p0_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_YJ0_2p0_2p5_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_YJ0_NJ0_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_YJ0_0p0_2p5_out'] = {'mode':'constant','factor':0.5638}

globalXSBRMap['Run3FidXSAnalysis']['bbh_YJ0_0p0_0p5_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_YJ0_0p5_1p2_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_YJ0_1p2_2p0_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_YJ0_2p0_2p5_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_YJ0_NJ0_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_YJ0_0p0_2p5_out'] = {'mode':'constant','factor':0.49}




globalXSBRMap['Run3FidXSAnalysis']['ggh_AbsYHJ0_0p0_0p6_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_AbsYHJ0_0p6_1p2_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_AbsYHJ0_1p2_1p9_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_AbsYHJ0_1p9_100p0_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_AbsYHJ0_NJ0_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_AbsYHJ0_0p0_100p0_out'] = {'mode':'constant','factor':51.96}

globalXSBRMap['Run3FidXSAnalysis']['vbf_AbsYHJ0_0p0_0p6_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_AbsYHJ0_0p6_1p2_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_AbsYHJ0_1p2_1p9_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_AbsYHJ0_1p9_100p0_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_AbsYHJ0_NJ0_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_AbsYHJ0_0p0_100p0_out'] = {'mode':'constant','factor':4.067}

globalXSBRMap['Run3FidXSAnalysis']['vh_AbsYHJ0_0p0_0p6_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_AbsYHJ0_0p6_1p2_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_AbsYHJ0_1p2_1p9_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_AbsYHJ0_1p9_100p0_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_AbsYHJ0_NJ0_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_AbsYHJ0_0p0_100p0_out'] = {'mode':'constant','factor':2.3781}

globalXSBRMap['Run3FidXSAnalysis']['tth_AbsYHJ0_0p0_0p6_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_AbsYHJ0_0p6_1p2_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_AbsYHJ0_1p2_1p9_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_AbsYHJ0_1p9_100p0_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_AbsYHJ0_NJ0_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_AbsYHJ0_0p0_100p0_out'] = {'mode':'constant','factor':0.5638}

globalXSBRMap['Run3FidXSAnalysis']['bbh_AbsYHJ0_0p0_0p6_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_AbsYHJ0_0p6_1p2_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_AbsYHJ0_1p2_1p9_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_AbsYHJ0_1p9_100p0_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_AbsYHJ0_NJ0_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_AbsYHJ0_0p0_100p0_out'] = {'mode':'constant','factor':0.49}




globalXSBRMap['Run3FidXSAnalysis']['ggh_AbsPhiHJ0_0p0_2p6_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_AbsPhiHJ0_2p6_2p9_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_AbsPhiHJ0_2p9_3p03_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_AbsPhiHJ0_3p03_3p1415926_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_AbsPhiHJ0_NJ_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_AbsPhiHJ0_0p0_Pi_out'] = {'mode':'constant','factor':51.96}

globalXSBRMap['Run3FidXSAnalysis']['vbf_AbsPhiHJ0_0p0_2p6_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_AbsPhiHJ0_2p6_2p9_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_AbsPhiHJ0_2p9_3p03_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_AbsPhiHJ0_3p03_3p1415926_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_AbsPhiHJ0_NJ_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_AbsPhiHJ0_0p0_Pi_out'] = {'mode':'constant','factor':4.067}

globalXSBRMap['Run3FidXSAnalysis']['vh_AbsPhiHJ0_0p0_2p6_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_AbsPhiHJ0_2p6_2p9_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_AbsPhiHJ0_2p9_3p03_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_AbsPhiHJ0_3p03_3p1415926_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_AbsPhiHJ0_NJ_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_AbsPhiHJ0_0p0_Pi_out'] = {'mode':'constant','factor':2.3781}

globalXSBRMap['Run3FidXSAnalysis']['tth_AbsPhiHJ0_0p0_2p6_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_AbsPhiHJ0_2p6_2p9_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_AbsPhiHJ0_2p9_3p03_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_AbsPhiHJ0_3p03_3p1415926_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_AbsPhiHJ0_NJ_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_AbsPhiHJ0_0p0_Pi_out'] = {'mode':'constant','factor':0.5638}

globalXSBRMap['Run3FidXSAnalysis']['bbh_AbsPhiHJ0_0p0_2p6_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_AbsPhiHJ0_2p6_2p9_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_AbsPhiHJ0_2p9_3p03_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_AbsPhiHJ0_3p03_3p1415926_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_AbsPhiHJ0_NJ_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_AbsPhiHJ0_0p0_Pi_out'] = {'mode':'constant','factor':0.49}




globalXSBRMap['Run3FidXSAnalysis']['ggh_DPhiJ0J1_m3p1416_m2p0944_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_DPhiJ0J1_m2p0944_m1p0472_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_DPhiJ0J1_m1p0472_0p0_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_DPhiJ0J1_0p0_1p0472_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_DPhiJ0J1_1p0472_2p0944_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_DPhiJ0J1_2p0944_3p1416_in'] = {'mode':'constant','factor':51.96}
globalXSBRMap['Run3FidXSAnalysis']['ggh_DPhiJ0J1_m3p1416_3p1416_out'] = {'mode':'constant','factor':51.96}

globalXSBRMap['Run3FidXSAnalysis']['vbf_DPhiJ0J1_m3p1416_m2p0944_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_DPhiJ0J1_m2p0944_m1p0472_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_DPhiJ0J1_m1p0472_0p0_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_DPhiJ0J1_0p0_1p0472_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_DPhiJ0J1_1p0472_2p0944_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_DPhiJ0J1_2p0944_3p1416_in'] = {'mode':'constant','factor':4.067}
globalXSBRMap['Run3FidXSAnalysis']['vbf_DPhiJ0J1_m3p1416_3p1416_out'] = {'mode':'constant','factor':4.067}

globalXSBRMap['Run3FidXSAnalysis']['vh_DPhiJ0J1_m3p1416_m2p0944_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_DPhiJ0J1_m2p0944_m1p0472_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_DPhiJ0J1_m1p0472_0p0_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_DPhiJ0J1_0p0_1p0472_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_DPhiJ0J1_1p0472_2p0944_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_DPhiJ0J1_2p0944_3p1416_in'] = {'mode':'constant','factor':2.3781}
globalXSBRMap['Run3FidXSAnalysis']['vh_DPhiJ0J1_m3p1416_3p1416_out'] = {'mode':'constant','factor':2.3781}

globalXSBRMap['Run3FidXSAnalysis']['tth_DPhiJ0J1_m3p1416_m2p0944_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_DPhiJ0J1_m2p0944_m1p0472_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_DPhiJ0J1_m1p0472_0p0_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_DPhiJ0J1_0p0_1p0472_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_DPhiJ0J1_1p0472_2p0944_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_DPhiJ0J1_2p0944_3p1416_in'] = {'mode':'constant','factor':0.5638}
globalXSBRMap['Run3FidXSAnalysis']['tth_DPhiJ0J1_m3p1416_3p1416_out'] = {'mode':'constant','factor':0.5638}

globalXSBRMap['Run3FidXSAnalysis']['bbh_DPhiJ0J1_m3p1416_m2p0944_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_DPhiJ0J1_m2p0944_m1p0472_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_DPhiJ0J1_m1p0472_0p0_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_DPhiJ0J1_0p0_1p0472_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_DPhiJ0J1_1p0472_2p0944_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_DPhiJ0J1_2p0944_3p1416_in'] = {'mode':'constant','factor':0.49}
globalXSBRMap['Run3FidXSAnalysis']['bbh_DPhiJ0J1_m3p1416_3p1416_out'] = {'mode':'constant','factor':0.49}


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Functions for loading XS*BR below
# Importing modules from combine
from HiggsAnalysis.CombinedLimit.DatacardParser import *
from HiggsAnalysis.CombinedLimit.ModelTools import *
from HiggsAnalysis.CombinedLimit.PhysicsModel import *
from HiggsAnalysis.CombinedLimit.SMHiggsBuilder import *
import HiggsAnalysis.CombinedLimit.PhysicsModel as models
class dummy_options:
  def __init__(self):
    self.physModel = "HiggsAnalysis.CombinedLimit.PhysicsModel:floatingHiggsMass"
    self.physOpt = ["higgsMassRange=90,250"]
    self.bin = True
    self.fileName = "dummy.root"
    self.cexpr = False
    self.out = "wsdefault"
    self.verbose = 0
    self.mass = 125
    self.funcXSext = "dummy"

# Functions to get XS/BR
def getXS(_SM,_MHVar,_mh,_pm):
  _MHVar.setVal(_mh)
  return _SM.modelBuilder.out.function("SM_XS_%s_%s"%(_pm,sqrts__)).getVal()
def getBR(_SM,_MHVar,_mh,_dm):
  _MHVar.setVal(_mh)
  return _SM.modelBuilder.out.function("SM_BR_%s"%_dm).getVal()

# Function to initialise XS values from combine
def initialiseXSBR(mass='125'):
  options=dummy_options()
  DC = Datacard()
  MB = ModelBuilder(DC, options)
  physics = models.floatingHiggsMass
  physics.setPhysicsOptions(options.physOpt)
  MB.setPhysics(physics)
  MB.physics.doParametersOfInterest()
  SM = SMHiggsBuilder(MB)
  MHVar = SM.modelBuilder.out.var("MH")

  # Make XS and BR
  SM.makeBR(decayMode)
  for pm in productionModes: SM.makeXS(pm,sqrts__)

  # Store values for each production mode in ordered dict
  xsbr = od()
  for pm in productionModes: xsbr[pm] = getXS(SM,MHVar,float(mass),pm)
  xsbr['constant'] = 1.
  xsbr[decayMode] = getBR(SM,MHVar,float(mass),decayMode)
  # If ggZH and ZH in production modes then make qqZH numpy array
  if('ggZH' in productionModes)&('ZH' in productionModes): xsbr['qqZH'] = xsbr['ZH']-xsbr['ggZH']
  return xsbr

def extractXSBR(d,mass='125',analysis='STXS'):
  # Import cross sections and branching ratios from combine
  xsbr = initialiseXSBR(mass)
  # Define map of procs to XS,BR
  XSBR_for_analysis = od()
  # XS
  for proc in d[d['type']=='sig']['procOriginal'].unique():
    fp = globalXSBRMap[analysis][proc]['factor'] if 'factor' in globalXSBRMap[analysis][proc] else 1.
    mode = globalXSBRMap[analysis][proc]['mode']
    xs = fp*xsbr[mode]
    XSBR_for_analysis['XS_%s'%proc] = xs
  # BR
  fd = globalXSBRMap[analysis]['decay']['factor'] if 'factor' in globalXSBRMap[analysis]['decay'] else 1.
  mode = globalXSBRMap[analysis]['decay']['mode']
  br = fd*xsbr[mode]
  XSBR_for_analysis['BR'] = br
  return XSBR_for_analysis