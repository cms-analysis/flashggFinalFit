import ROOT
import os
import sys
import json
import re
import numpy as np
import pandas
import pickle
from collections import OrderedDict as od
from commonObjects import *
from commonTools import *

XSBRMap = od()
# For case of fixed xs/br Use 'mode':constant 'factor':X e.g.
#XSBRMap['example'] = od()
#XSBRMap['example']['decay'] = {'mode':'constant','factor':1}
#XSBRMap['example']['PROCNAME'] = {'mode':'constant','factor':0.001}
# For case of inclusive production mode then drop factor e.g.
#XSBRMap['example'] = od()
#XSBRMap['example']['decay'] = {'mode':'hgg'}
#XSBRMap['example']['GG2H'] = {'mode':'ggH'}
#XSBRMap['example']['VBF'] = {'mode':'qqH'}
#XSBRMap['example']['WH2HQQ'] = {'mode':'WH','factor':BR_W_qq}

# Tutorial analysis
XSBRMap['tutorial'] = od()
XSBRMap['tutorial']['decay'] = {'mode':'hgg'}
XSBRMap['tutorial']['GG2H'] = {'mode':'constant', 'factor':51.96}
XSBRMap['tutorial']['VBF'] = {'mode':'constant', 'factor':4.067}

XSBRMap['Run3STXS'] = od()
XSBRMap['Run3STXS']['decay'] = {'mode':'hgg'}
XSBRMap['Run3STXS']['gghtruth'] = {'mode':'constant', 'factor':52.23}
XSBRMap['Run3STXS']['tthtruth'] = {'mode':'constant', 'factor':0.5700}
XSBRMap['Run3STXS']['thtruth'] = {'mode':'constant', 'factor':0.104}
XSBRMap['Run3STXS']['whltruth'] = {'mode':'constant', 'factor':1.4564}
XSBRMap['Run3STXS']['zhltruth'] = {'mode':'constant', 'factor':0.94388}
XSBRMap['Run3STXS']['vbfVhqtruth'] = {'mode':'constant', 'factor':4.078}
# STXS analysis
XSBRMap['STXS'] = od()
XSBRMap['STXS']['decay'] = {'mode':'hgg'}
# ggH STXS stage 1.2 bins
XSBRMap['STXS']['GG2H_FWDH'] = {'mode':'ggH','factor':0.0809}
XSBRMap['STXS']['GG2H_PTH_200_300'] = {'mode':'ggH','factor':0.0098}
XSBRMap['STXS']['GG2H_PTH_300_450'] = {'mode':'ggH','factor':0.0025}
XSBRMap['STXS']['GG2H_PTH_450_650'] = {'mode':'ggH','factor':0.0003}
XSBRMap['STXS']['GG2H_PTH_GT650'] = {'mode':'ggH','factor':0.0001}
XSBRMap['STXS']['GG2H_0J_PTH_0_10'] = {'mode':'ggH','factor':0.1387}
XSBRMap['STXS']['GG2H_0J_PTH_GT10'] = {'mode':'ggH','factor':0.3940}
XSBRMap['STXS']['GG2H_1J_PTH_0_60'] = {'mode':'ggH','factor':0.1477}
XSBRMap['STXS']['GG2H_1J_PTH_60_120'] = {'mode':'ggH','factor':0.1023}
XSBRMap['STXS']['GG2H_1J_PTH_120_200'] = {'mode':'ggH','factor':0.0182}
XSBRMap['STXS']['GG2H_GE2J_MJJ_0_350_PTH_0_60'] = {'mode':'ggH','factor':0.0256}
XSBRMap['STXS']['GG2H_GE2J_MJJ_0_350_PTH_60_120'] = {'mode':'ggH','factor':0.0410}
XSBRMap['STXS']['GG2H_GE2J_MJJ_0_350_PTH_120_200'] = {'mode':'ggH','factor':0.0188}
XSBRMap['STXS']['GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'ggH','factor':0.0063}
XSBRMap['STXS']['GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'ggH','factor':0.0077}
XSBRMap['STXS']['GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'ggH','factor':0.0028}
XSBRMap['STXS']['GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'ggH','factor':0.0032}
# ggZH hadronic: merged with ggH STXS stage 1.2 bins in fit
XSBRMap['STXS']['GG2HQQ_FWDH'] = {'mode':'ggZH','factor':0.0273*BR_Z_qq}
XSBRMap['STXS']['GG2HQQ_PTH_200_300'] = {'mode':'ggZH','factor':0.1393*BR_Z_qq}
XSBRMap['STXS']['GG2HQQ_PTH_300_450'] = {'mode':'ggZH','factor':0.0386*BR_Z_qq}
XSBRMap['STXS']['GG2HQQ_PTH_450_650'] = {'mode':'ggZH','factor':0.0077*BR_Z_qq}
XSBRMap['STXS']['GG2HQQ_PTH_GT650'] = {'mode':'ggZH','factor':0.0020*BR_Z_qq}
XSBRMap['STXS']['GG2HQQ_0J_PTH_0_10'] = {'mode':'ggZH','factor':0.0001*BR_Z_qq}
XSBRMap['STXS']['GG2HQQ_0J_PTH_GT10'] = {'mode':'ggZH','factor':0.0029*BR_Z_qq}
XSBRMap['STXS']['GG2HQQ_1J_PTH_0_60'] = {'mode':'ggZH','factor':0.0200*BR_Z_qq}
XSBRMap['STXS']['GG2HQQ_1J_PTH_60_120'] = {'mode':'ggZH','factor':0.0534*BR_Z_qq}
XSBRMap['STXS']['GG2HQQ_1J_PTH_120_200'] = {'mode':'ggZH','factor':0.0353*BR_Z_qq}
XSBRMap['STXS']['GG2HQQ_GE2J_MJJ_0_350_PTH_0_60'] = {'mode':'ggZH','factor':0.0574*BR_Z_qq}
XSBRMap['STXS']['GG2HQQ_GE2J_MJJ_0_350_PTH_60_120'] = {'mode':'ggZH','factor':0.1963*BR_Z_qq}
XSBRMap['STXS']['GG2HQQ_GE2J_MJJ_0_350_PTH_120_200'] = {'mode':'ggZH','factor':0.2954*BR_Z_qq}
XSBRMap['STXS']['GG2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'ggZH','factor':0.0114*BR_Z_qq}
XSBRMap['STXS']['GG2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'ggZH','factor':0.0806*BR_Z_qq}
XSBRMap['STXS']['GG2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'ggZH','factor':0.0036*BR_Z_qq}
XSBRMap['STXS']['GG2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'ggZH','factor':0.0285*BR_Z_qq}
# qqH STXS stage 1.2 bins: including (qq)VH hadronic processes
XSBRMap['STXS']['VBF_FWDH'] = {'mode':'qqH','factor':0.0669}
XSBRMap['STXS']['VBF_0J'] = {'mode':'qqH','factor':0.0695}
XSBRMap['STXS']['VBF_1J'] = {'mode':'qqH','factor':0.3283}
XSBRMap['STXS']['VBF_GE2J_MJJ_0_60'] = {'mode':'qqH','factor':0.0136}
XSBRMap['STXS']['VBF_GE2J_MJJ_60_120'] = {'mode':'qqH','factor':0.0240}
XSBRMap['STXS']['VBF_GE2J_MJJ_120_350'] = {'mode':'qqH','factor':0.1234}
XSBRMap['STXS']['VBF_GE2J_MJJ_GT350_PTH_GT200'] = {'mode':'qqH','factor':0.0398}
XSBRMap['STXS']['VBF_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'qqH','factor':0.1026}
XSBRMap['STXS']['VBF_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'qqH','factor':0.0385}
XSBRMap['STXS']['VBF_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'qqH','factor':0.1509}
XSBRMap['STXS']['VBF_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'qqH','factor':0.0425}
XSBRMap['STXS']['WH2HQQ_FWDH'] = {'mode':'WH','factor':0.1257*BR_W_qq}
XSBRMap['STXS']['WH2HQQ_0J'] = {'mode':'WH','factor':0.0570*BR_W_qq}
XSBRMap['STXS']['WH2HQQ_1J'] = {'mode':'WH','factor':0.3113*BR_W_qq}
XSBRMap['STXS']['WH2HQQ_GE2J_MJJ_0_60'] = {'mode':'WH','factor':0.0358*BR_W_qq}
XSBRMap['STXS']['WH2HQQ_GE2J_MJJ_60_120'] = {'mode':'WH','factor':0.2943*BR_W_qq}
XSBRMap['STXS']['WH2HQQ_GE2J_MJJ_120_350'] = {'mode':'WH','factor':0.1392*BR_W_qq}
XSBRMap['STXS']['WH2HQQ_GE2J_MJJ_GT350_PTH_GT200'] = {'mode':'WH','factor':0.0088*BR_W_qq}
XSBRMap['STXS']['WH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'WH','factor':0.0044*BR_W_qq}
XSBRMap['STXS']['WH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'WH','factor':0.0186*BR_W_qq}
XSBRMap['STXS']['WH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'WH','factor':0.0009*BR_W_qq}
XSBRMap['STXS']['WH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'WH','factor':0.0040*BR_W_qq}
XSBRMap['STXS']['ZH2HQQ_FWDH'] = {'mode':'qqZH','factor':0.1143*BR_Z_qq}
XSBRMap['STXS']['ZH2HQQ_0J'] = {'mode':'qqZH','factor':0.0433*BR_Z_qq}
XSBRMap['STXS']['ZH2HQQ_1J'] = {'mode':'qqZH','factor':0.2906*BR_Z_qq}
XSBRMap['STXS']['ZH2HQQ_GE2J_MJJ_0_60'] = {'mode':'qqZH','factor':0.0316*BR_Z_qq}
XSBRMap['STXS']['ZH2HQQ_GE2J_MJJ_60_120'] = {'mode':'qqZH','factor':0.3360*BR_Z_qq}
XSBRMap['STXS']['ZH2HQQ_GE2J_MJJ_120_350'] = {'mode':'qqZH','factor':0.1462*BR_Z_qq}
XSBRMap['STXS']['ZH2HQQ_GE2J_MJJ_GT350_PTH_GT200'] = {'mode':'qqZH','factor':0.0083*BR_Z_qq}
XSBRMap['STXS']['ZH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'qqZH','factor':0.0041*BR_Z_qq}
XSBRMap['STXS']['ZH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'qqZH','factor':0.0202*BR_Z_qq}
XSBRMap['STXS']['ZH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'qqZH','factor':0.0009*BR_Z_qq}
XSBRMap['STXS']['ZH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'qqZH','factor':0.0045*BR_Z_qq}
# WH lep STXS stage 1.2 bins
XSBRMap['STXS']['QQ2HLNU_FWDH'] = {'mode':'WH','factor':0.1213*BR_W_lnu}
XSBRMap['STXS']['QQ2HLNU_PTV_0_75'] = {'mode':'WH','factor':0.4655*BR_W_lnu}
XSBRMap['STXS']['QQ2HLNU_PTV_75_150'] = {'mode':'WH','factor':0.2930*BR_W_lnu}
XSBRMap['STXS']['QQ2HLNU_PTV_150_250_0J'] = {'mode':'WH','factor':0.0510*BR_W_lnu}
XSBRMap['STXS']['QQ2HLNU_PTV_150_250_GE1J'] = {'mode':'WH','factor':0.0397*BR_W_lnu}
XSBRMap['STXS']['QQ2HLNU_PTV_GT250'] = {'mode':'WH','factor':0.0295*BR_W_lnu}
# (qq)ZH lep STXS stage 1.2 bins
XSBRMap['STXS']['QQ2HLL_FWDH'] = {'mode':'qqZH','factor':0.1121*(BR_Z_ll+BR_Z_nunu)}
XSBRMap['STXS']['QQ2HLL_PTV_0_75'] = {'mode':'qqZH','factor':0.4565*(BR_Z_ll+BR_Z_nunu)}
XSBRMap['STXS']['QQ2HLL_PTV_75_150'] = {'mode':'qqZH','factor':0.3070*(BR_Z_ll+BR_Z_nunu)}
XSBRMap['STXS']['QQ2HLL_PTV_150_250_0J'] = {'mode':'qqZH','factor':0.0516*(BR_Z_ll+BR_Z_nunu)}
XSBRMap['STXS']['QQ2HLL_PTV_150_250_GE1J'] = {'mode':'qqZH','factor':0.0427*(BR_Z_ll+BR_Z_nunu)}
XSBRMap['STXS']['QQ2HLL_PTV_GT250'] = {'mode':'qqZH','factor':0.0301*(BR_Z_ll+BR_Z_nunu)}
# gg(ZH) lep STXS stage 1.2 bins: separate processes for ll and nunu decays
XSBRMap['STXS']['GG2HLL_FWDH'] = {'mode':'ggZH','factor':0.0270*BR_Z_ll}
XSBRMap['STXS']['GG2HLL_PTV_0_75'] = {'mode':'ggZH','factor':0.1605*BR_Z_ll}
XSBRMap['STXS']['GG2HLL_PTV_75_150'] = {'mode':'ggZH','factor':0.4325*BR_Z_ll}
XSBRMap['STXS']['GG2HLL_PTV_150_250_0J'] = {'mode':'ggZH','factor':0.0913*BR_Z_ll}
XSBRMap['STXS']['GG2HLL_PTV_150_250_GE1J'] = {'mode':'ggZH','factor':0.2044*BR_Z_ll}
XSBRMap['STXS']['GG2HLL_PTV_GT250'] = {'mode':'ggZH','factor':0.0844*BR_Z_ll}
XSBRMap['STXS']['GG2HNUNU_FWDH'] = {'mode':'ggZH','factor':0.0271*BR_Z_nunu}
XSBRMap['STXS']['GG2HNUNU_PTV_0_75'] = {'mode':'ggZH','factor':0.1591*BR_Z_nunu}
XSBRMap['STXS']['GG2HNUNU_PTV_75_150'] = {'mode':'ggZH','factor':0.4336*BR_Z_nunu}
XSBRMap['STXS']['GG2HNUNU_PTV_150_250_0J'] = {'mode':'ggZH','factor':0.0905*BR_Z_nunu}
XSBRMap['STXS']['GG2HNUNU_PTV_150_250_GE1J'] = {'mode':'ggZH','factor':0.2051*BR_Z_nunu}
XSBRMap['STXS']['GG2HNUNU_PTV_GT250'] = {'mode':'ggZH','factor':0.0845*BR_Z_nunu}
# ttH STXS stage 1.2 bins
XSBRMap['STXS']['TTH_FWDH'] = {'mode':'ttH','factor':0.0135}
XSBRMap['STXS']['TTH_PTH_0_60'] = {'mode':'ttH','factor':0.2250}
XSBRMap['STXS']['TTH_PTH_60_120'] = {'mode':'ttH','factor':0.3473}
XSBRMap['STXS']['TTH_PTH_120_200'] = {'mode':'ttH','factor':0.2569}
XSBRMap['STXS']['TTH_PTH_200_300'] = {'mode':'ttH','factor':0.1076}
XSBRMap['STXS']['TTH_PTH_GT300'] = {'mode':'ttH','factor':0.0533}
# bbH STXS stage 1.2 bins
XSBRMap['STXS']['BBH_FWDH'] = {'mode':'bbH','factor':0.0487}
XSBRMap['STXS']['BBH'] = {'mode':'bbH','factor':0.9513}
# tH STXS stage 1.2 bins: tHq + tHW
XSBRMap['STXS']['THQ_FWDH'] = {'mode':'tHq','factor':0.0279}
XSBRMap['STXS']['THQ'] = {'mode':'tHq','factor':0.9721}
XSBRMap['STXS']['THW_FWDH'] = {'mode':'tHW','factor':0.0106}
XSBRMap['STXS']['THW'] = {'mode':'tHW','factor':0.9894}

XSBRMap['Run3STXS'] = od()
XSBRMap['Run3STXS']['decay'] = {'mode':'hgg'}
XSBRMap['Run3STXS']['GG2H__preEE'] = {'mode':'constant', 'factor':52.277759999999994}
XSBRMap['Run3STXS']['GG2H_FWDH_preEE'] = {'mode':'constant', 'factor':52.277759999999994}
XSBRMap['Run3STXS']['TTH__preEE'] = {'mode':'constant', 'factor':0.57}
XSBRMap['Run3STXS']['TTH_FWDH_preEE'] = {'mode':'constant', 'factor':0.57}
XSBRMap['Run3STXS']['THQ__preEE'] = {'mode':'constant', 'factor':0.086688}
XSBRMap['Run3STXS']['THQ_FWDH_preEE'] = {'mode':'constant', 'factor':0.086688}
XSBRMap['Run3STXS']['THW__preEE'] = {'mode':'constant', 'factor':0.0172}
XSBRMap['Run3STXS']['THW_FWDH_preEE'] = {'mode':'constant', 'factor':0.0172}
XSBRMap['Run3STXS']['WMINUSH2HQQ__preEE'] = {'mode':'constant', 'factor':0.38268657}
XSBRMap['Run3STXS']['WMINUSH2HQQ_FWDH_preEE'] = {'mode':'constant', 'factor':0.38268657}
XSBRMap['Run3STXS']['WMINUSH2HLNU__preEE'] = {'mode':'constant', 'factor':0.18495666}
XSBRMap['Run3STXS']['WMINUSH2HLNU_FWDH_preEE'] = {'mode':'constant', 'factor':0.18495666}
XSBRMap['Run3STXS']['WPLUSH2HQQ__preEE'] = {'mode':'constant', 'factor':0.5992074900000001}
XSBRMap['Run3STXS']['WPLUSH2HQQ__FWDH_preEE'] = {'mode':'constant', 'factor':0.5992074900000001}
XSBRMap['Run3STXS']['WPLUSH2HLNU__preEE'] = {'mode':'constant', 'factor':0.28960362}
XSBRMap['Run3STXS']['WPLUSH2HLNU_FWDH_preEE'] = {'mode':'constant', 'factor':0.28960362}
XSBRMap['Run3STXS']['ZH2HQQ__preEE'] = {'mode':'constant', 'factor':0.6598804899999999}
XSBRMap['Run3STXS']['ZH2HQQ_FWDH_preEE'] = {'mode':'constant', 'factor':0.6598804899999999}
XSBRMap['Run3STXS']['ZH2HLL__preEE'] = {'mode':'constant', 'factor': 0.0953093586}
XSBRMap['Run3STXS']['ZH2HLL_FWDH_preEE'] = {'mode':'constant', 'factor': 0.0953093586}
XSBRMap['Run3STXS']['ZH2HNUNU__preEE'] = {'mode':'constant', 'factor':0.1887}
XSBRMap['Run3STXS']['ZH2HNUNU_FWDH_preEE'] = {'mode':'constant', 'factor':0.1887}
XSBRMap['Run3STXS']['VBF__preEE'] = {'mode':'constant', 'factor':4.078}
XSBRMap['Run3STXS']['VBF_FWDH_preEE'] = {'mode':'constant', 'factor':4.078}
XSBRMap['Run3STXS']['BBH__preEE'] = {'mode':'constant', 'factor':0.5266}
XSBRMap['Run3STXS']['BBH_FWDH_preEE'] = {'mode':'constant', 'factor':0.5266}
XSBRMap['Run3STXS']['GG2HLL__preEE'] = {'mode':'constant', 'factor':0.006838}
XSBRMap['Run3STXS']['GG2HLL_FWDH_preEE'] = {'mode':'constant', 'factor':0.006838}
XSBRMap['Run3STXS']['GG2HNUNU__preEE'] = {'mode':'constant', 'factor':0.01351}
XSBRMap['Run3STXS']['GG2HNUNU_FWDH_preEE'] = {'mode':'constant', 'factor':0.01351}
XSBRMap['Run3STXS']['GG2HQQ__preEE'] = {'mode':'constant', 'factor':0.04776}
XSBRMap['Run3STXS']['GG2HQQ_FWDH_preEE'] = {'mode':'constant', 'factor':0.04776}

XS = {
    "GG2H" : 52.17,
    "GG2HQQ" : 0.09500905,
    "VBF" : 4.075,
    "WPLUSH2HQQ": 0.59789974,
    "WMINUSH2HQQ": 0.3817826,
    "ZH2HQQ" : 0.56369239,
    "WPLUSH2HLNU" : 0.28897157,
    "WMINUSH2HLNU" : 0.18451976,
    "ZH2HLL" : 0.08848336,
    "ZH2HNUNU" : 0.16126,
    "ZH2HLEPLEP" : 0.24974336,
    "GG2HLL" : 0.01491367,
    "GG2HNUNU" : 0.02718,
    "TTH" : 0.5688,
    "THQ" : 0.086594,
    "THQ2HQQ" : 0.05765, # To be updated
    "THQ2HLNU" : 0.029, # To be updated
    "THW" : 0.0172,
    "BBH" : 0.5251
}

XSBRMap['HIG-25-020'] = od()
XSBRMap['HIG-25-020']['decay'] = {'mode':'hgg'}
XSBRMap['HIG-25-020']['GG2H_FWDH'] = {'mode':'constant', 'factor':0.085247062*XS['GG2H']}
XSBRMap['HIG-25-020']['GG2H_PTH_200_300'] = {'mode':'constant', 'factor':0.014211155*XS['GG2H']}
XSBRMap['HIG-25-020']['GG2H_PTH_300_450'] = {'mode':'constant', 'factor':0.004919169*XS['GG2H']}
XSBRMap['HIG-25-020']['GG2H_PTH_450_650'] = {'mode':'constant', 'factor':0.00125562*XS['GG2H']}
XSBRMap['HIG-25-020']['GG2H_PTH_GT650'] = {'mode':'constant', 'factor':0.000333772*XS['GG2H']}
XSBRMap['HIG-25-020']['GG2H_0J_PTH_0_10'] = {'mode':'constant', 'factor':0.137979127*XS['GG2H']}
XSBRMap['HIG-25-020']['GG2H_0J_PTH_GT10'] = {'mode':'constant', 'factor':0.387390556*XS['GG2H']}
XSBRMap['HIG-25-020']['GG2H_1J_PTH_0_60'] = {'mode':'constant', 'factor':0.139387726*XS['GG2H']}
XSBRMap['HIG-25-020']['GG2H_1J_PTH_60_120'] = {'mode':'constant', 'factor':0.100483374*XS['GG2H']}
XSBRMap['HIG-25-020']['GG2H_1J_PTH_120_200'] = {'mode':'constant', 'factor':0.020922364*XS['GG2H']}
XSBRMap['HIG-25-020']['GG2H_GE2J_MJJ_0_350_PTH_0_60'] = {'mode':'constant', 'factor':0.026286564*XS['GG2H']}
XSBRMap['HIG-25-020']['GG2H_GE2J_MJJ_0_350_PTH_60_120'] = {'mode':'constant', 'factor':0.038614288*XS['GG2H']}
XSBRMap['HIG-25-020']['GG2H_GE2J_MJJ_0_350_PTH_120_200'] = {'mode':'constant', 'factor':0.022114408*XS['GG2H']}
XSBRMap['HIG-25-020']['GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.006429092*XS['GG2H']}
XSBRMap['HIG-25-020']['GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.008050272*XS['GG2H']}
XSBRMap['HIG-25-020']['GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.002930442*XS['GG2H']}
XSBRMap['HIG-25-020']['GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.003445008*XS['GG2H']}
XSBRMap['HIG-25-020']['GG2HQQ_FWDH'] = {'mode':'constant', 'factor':0.030261461*XS['GG2HQQ']}
XSBRMap['HIG-25-020']['GG2HQQ_PTH_200_300'] = {'mode':'constant', 'factor':0.137302676*XS['GG2HQQ']}
XSBRMap['HIG-25-020']['GG2HQQ_PTH_300_450'] = {'mode':'constant', 'factor':0.032923158*XS['GG2HQQ']}
XSBRMap['HIG-25-020']['GG2HQQ_PTH_450_650'] = {'mode':'constant', 'factor':0.003664954*XS['GG2HQQ']}
XSBRMap['HIG-25-020']['GG2HQQ_PTH_GT650'] = {'mode':'constant', 'factor':0.000204746*XS['GG2HQQ']}
XSBRMap['HIG-25-020']['GG2HQQ_0J_PTH_0_10'] = {'mode':'constant', 'factor':8.19E-05*XS['GG2HQQ']}
XSBRMap['HIG-25-020']['GG2HQQ_0J_PTH_GT10'] = {'mode':'constant', 'factor':0.00284597*XS['GG2HQQ']}
XSBRMap['HIG-25-020']['GG2HQQ_1J_PTH_0_60'] = {'mode':'constant', 'factor':0.02029033*XS['GG2HQQ']}
XSBRMap['HIG-25-020']['GG2HQQ_1J_PTH_60_120'] = {'mode':'constant', 'factor':0.054237218*XS['GG2HQQ']}
XSBRMap['HIG-25-020']['GG2HQQ_1J_PTH_120_200'] = {'mode':'constant', 'factor':0.037059029*XS['GG2HQQ']}
XSBRMap['HIG-25-020']['GG2HQQ_GE2J_MJJ_0_350_PTH_0_60'] = {'mode':'constant', 'factor':0.058741632*XS['GG2HQQ']}
XSBRMap['HIG-25-020']['GG2HQQ_GE2J_MJJ_0_350_PTH_60_120'] = {'mode':'constant', 'factor':0.201408651*XS['GG2HQQ']}
XSBRMap['HIG-25-020']['GG2HQQ_GE2J_MJJ_0_350_PTH_120_200'] = {'mode':'constant', 'factor':0.300423825*XS['GG2HQQ']}
XSBRMap['HIG-25-020']['GG2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.011977642*XS['GG2HQQ']}
XSBRMap['HIG-25-020']['GG2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.081038472*XS['GG2HQQ']}
XSBRMap['HIG-25-020']['GG2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.003746852*XS['GG2HQQ']}
XSBRMap['HIG-25-020']['GG2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.023791487*XS['GG2HQQ']}
XSBRMap['HIG-25-020']['VBF_FWDH'] = {'mode':'constant', 'factor':0.07578759*XS['VBF']}
XSBRMap['HIG-25-020']['VBF_0J'] = {'mode':'constant', 'factor':0.063805995*XS['VBF']}
XSBRMap['HIG-25-020']['VBF_1J'] = {'mode':'constant', 'factor':0.327773873*XS['VBF']}
XSBRMap['HIG-25-020']['VBF_GE2J_MJJ_0_60'] = {'mode':'constant', 'factor':0.010842014*XS['VBF']}
XSBRMap['HIG-25-020']['VBF_GE2J_MJJ_60_120'] = {'mode':'constant', 'factor':0.018020321*XS['VBF']}
XSBRMap['HIG-25-020']['VBF_GE2J_MJJ_120_350'] = {'mode':'constant', 'factor':0.10769591*XS['VBF']}
XSBRMap['HIG-25-020']['VBF_GE2J_MJJ_GT350_PTH_GT200'] = {'mode':'constant', 'factor':0.043059194*XS['VBF']}
XSBRMap['HIG-25-020']['VBF_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.119847912*XS['VBF']}
XSBRMap['HIG-25-020']['VBF_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.022781008*XS['VBF']}
XSBRMap['HIG-25-020']['VBF_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.165559037*XS['VBF']}
XSBRMap['HIG-25-020']['VBF_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.044827147*XS['VBF']}
XSBRMap['HIG-25-020']['WPLUSH2HQQ_FWDH'] = {'mode':'constant', 'factor':0.151298618*XS['WPLUSH2HQQ']}
XSBRMap['HIG-25-020']['WPLUSH2HQQ_0J'] = {'mode':'constant', 'factor':0.051089435*XS['WPLUSH2HQQ']}
XSBRMap['HIG-25-020']['WPLUSH2HQQ_1J'] = {'mode':'constant', 'factor':0.297227506*XS['WPLUSH2HQQ']}
XSBRMap['HIG-25-020']['WPLUSH2HQQ_GE2J_MJJ_0_60'] = {'mode':'constant', 'factor':0.030924616*XS['WPLUSH2HQQ']}
XSBRMap['HIG-25-020']['WPLUSH2HQQ_GE2J_MJJ_60_120'] = {'mode':'constant', 'factor':0.299082082*XS['WPLUSH2HQQ']}
XSBRMap['HIG-25-020']['WPLUSH2HQQ_GE2J_MJJ_120_350'] = {'mode':'constant', 'factor':0.132109777*XS['WPLUSH2HQQ']}
XSBRMap['HIG-25-020']['WPLUSH2HQQ_GE2J_MJJ_GT350_PTH_GT200'] = {'mode':'constant', 'factor':0.00904939*XS['WPLUSH2HQQ']}
XSBRMap['HIG-25-020']['WPLUSH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.003725287*XS['WPLUSH2HQQ']}
XSBRMap['HIG-25-020']['WPLUSH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.020130107*XS['WPLUSH2HQQ']}
XSBRMap['HIG-25-020']['WPLUSH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.000736183*XS['WPLUSH2HQQ']}
XSBRMap['HIG-25-020']['WPLUSH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.004626999*XS['WPLUSH2HQQ']}
XSBRMap['HIG-25-020']['WMINUSH2HQQ_FWDH'] = {'mode':'constant', 'factor':0.093117961*XS['WMINUSH2HQQ']}
XSBRMap['HIG-25-020']['WMINUSH2HQQ_0J'] = {'mode':'constant', 'factor':0.060332122*XS['WMINUSH2HQQ']}
XSBRMap['HIG-25-020']['WMINUSH2HQQ_1J'] = {'mode':'constant', 'factor':0.324521276*XS['WMINUSH2HQQ']}
XSBRMap['HIG-25-020']['WMINUSH2HQQ_GE2J_MJJ_0_60'] = {'mode':'constant', 'factor':0.032542084*XS['WMINUSH2HQQ']}
XSBRMap['HIG-25-020']['WMINUSH2HQQ_GE2J_MJJ_60_120'] = {'mode':'constant', 'factor':0.309785184*XS['WMINUSH2HQQ']}
XSBRMap['HIG-25-020']['WMINUSH2HQQ_GE2J_MJJ_120_350'] = {'mode':'constant', 'factor':0.142326551*XS['WMINUSH2HQQ']}
XSBRMap['HIG-25-020']['WMINUSH2HQQ_GE2J_MJJ_GT350_PTH_GT200'] = {'mode':'constant', 'factor':0.007524292*XS['WMINUSH2HQQ']}
XSBRMap['HIG-25-020']['WMINUSH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.00414117*XS['WMINUSH2HQQ']}
XSBRMap['HIG-25-020']['WMINUSH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.020211033*XS['WMINUSH2HQQ']}
XSBRMap['HIG-25-020']['WMINUSH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.000555765*XS['WMINUSH2HQQ']}
XSBRMap['HIG-25-020']['WMINUSH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.004942561*XS['WMINUSH2HQQ']}
XSBRMap['HIG-25-020']['ZH2HQQ_FWDH'] = {'mode':'constant', 'factor':0.119478697*XS['ZH2HQQ']}
XSBRMap['HIG-25-020']['ZH2HQQ_0J'] = {'mode':'constant', 'factor':0.042546366*XS['ZH2HQQ']}
XSBRMap['HIG-25-020']['ZH2HQQ_1J'] = {'mode':'constant', 'factor':0.285894738*XS['ZH2HQQ']}
XSBRMap['HIG-25-020']['ZH2HQQ_GE2J_MJJ_0_60'] = {'mode':'constant', 'factor':0.027368421*XS['ZH2HQQ']}
XSBRMap['HIG-25-020']['ZH2HQQ_GE2J_MJJ_60_120'] = {'mode':'constant', 'factor':0.343598999*XS['ZH2HQQ']}
XSBRMap['HIG-25-020']['ZH2HQQ_GE2J_MJJ_120_350'] = {'mode':'constant', 'factor':0.141453632*XS['ZH2HQQ']}
XSBRMap['HIG-25-020']['ZH2HQQ_GE2J_MJJ_GT350_PTH_GT200'] = {'mode':'constant', 'factor':0.008360902*XS['ZH2HQQ']}
XSBRMap['HIG-25-020']['ZH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.003809524*XS['ZH2HQQ']}
XSBRMap['HIG-25-020']['ZH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.021634085*XS['ZH2HQQ']}
XSBRMap['HIG-25-020']['ZH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.000421053*XS['ZH2HQQ']}
XSBRMap['HIG-25-020']['ZH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.005433584*XS['ZH2HQQ']}
XSBRMap['HIG-25-020']['WPLUSH2HLNU_FWDH'] = {'mode':'constant', 'factor':0.155188512*XS['WPLUSH2HLNU']}
XSBRMap['HIG-25-020']['WPLUSH2HLNU_PTV_0_75'] = {'mode':'constant', 'factor':0.431671519*XS['WPLUSH2HLNU']}
XSBRMap['HIG-25-020']['WPLUSH2HLNU_PTV_75_150'] = {'mode':'constant', 'factor':0.287799901*XS['WPLUSH2HLNU']}
XSBRMap['HIG-25-020']['WPLUSH2HLNU_PTV_150_250_0J'] = {'mode':'constant', 'factor':0.051270718*XS['WPLUSH2HLNU']}
XSBRMap['HIG-25-020']['WPLUSH2HLNU_PTV_150_250_GE1J'] = {'mode':'constant', 'factor':0.041543315*XS['WPLUSH2HLNU']}
XSBRMap['HIG-25-020']['WPLUSH2HLNU_PTV_GT250'] = {'mode':'constant', 'factor':0.032526034*XS['WPLUSH2HLNU']}
XSBRMap['HIG-25-020']['WMINUSH2HLNU_FWDH'] = {'mode':'constant', 'factor':0.097063882*XS['WMINUSH2HLNU']}
XSBRMap['HIG-25-020']['WMINUSH2HLNU_PTV_0_75'] = {'mode':'constant', 'factor':0.490122821*XS['WMINUSH2HLNU']}
XSBRMap['HIG-25-020']['WMINUSH2HLNU_PTV_75_150'] = {'mode':'constant', 'factor':0.296397523*XS['WMINUSH2HLNU']}
XSBRMap['HIG-25-020']['WMINUSH2HLNU_PTV_150_250_0J'] = {'mode':'constant', 'factor':0.050060723*XS['WMINUSH2HLNU']}
XSBRMap['HIG-25-020']['WMINUSH2HLNU_PTV_150_250_GE1J'] = {'mode':'constant', 'factor':0.040180898*XS['WMINUSH2HLNU']}
XSBRMap['HIG-25-020']['WMINUSH2HLNU_PTV_GT250'] = {'mode':'constant', 'factor':0.026174153*XS['WMINUSH2HLNU']}
XSBRMap['HIG-25-020']['ZH2HLL_FWDH'] = {'mode':'constant', 'factor':0.119436748*XS['ZH2HLL']}
XSBRMap['HIG-25-020']['ZH2HLL_PTV_0_75'] = {'mode':'constant', 'factor':0.453446194*XS['ZH2HLL']}
XSBRMap['HIG-25-020']['ZH2HLL_PTV_75_150'] = {'mode':'constant', 'factor':0.302843549*XS['ZH2HLL']}
XSBRMap['HIG-25-020']['ZH2HLL_PTV_150_250_0J'] = {'mode':'constant', 'factor':0.052833795*XS['ZH2HLL']}
XSBRMap['HIG-25-020']['ZH2HLL_PTV_150_250_GE1J'] = {'mode':'constant', 'factor':0.041795061*XS['ZH2HLL']}
XSBRMap['HIG-25-020']['ZH2HLL_PTV_GT250'] = {'mode':'constant', 'factor':0.029644654*XS['ZH2HLL']}
XSBRMap['HIG-25-020']['ZH2HNUNU_FWDH'] = {'mode':'constant', 'factor':0.118822109*XS['ZH2HNUNU']}
XSBRMap['HIG-25-020']['ZH2HNUNU_PTV_0_75'] = {'mode':'constant', 'factor':0.457358902*XS['ZH2HNUNU']}
XSBRMap['HIG-25-020']['ZH2HNUNU_PTV_75_150'] = {'mode':'constant', 'factor':0.302931086*XS['ZH2HNUNU']}
XSBRMap['HIG-25-020']['ZH2HNUNU_PTV_150_250_0J'] = {'mode':'constant', 'factor':0.050339103*XS['ZH2HNUNU']}
XSBRMap['HIG-25-020']['ZH2HNUNU_PTV_150_250_GE1J'] = {'mode':'constant', 'factor':0.043829904*XS['ZH2HNUNU']}
XSBRMap['HIG-25-020']['ZH2HNUNU_PTV_GT250'] = {'mode':'constant', 'factor':0.026718897*XS['ZH2HNUNU']}
XSBRMap['HIG-25-020']['ZH2HLEPLEP_FWDH'] = {'mode':'constant', 'factor':0.119028372*XS['ZH2HLEPLEP']}
XSBRMap['HIG-25-020']['ZH2HLEPLEP_PTV_0_75'] = {'mode':'constant', 'factor':0.456045854*XS['ZH2HLEPLEP']}
XSBRMap['HIG-25-020']['ZH2HLEPLEP_PTV_75_150'] = {'mode':'constant', 'factor':0.30290171*XS['ZH2HLEPLEP']}
XSBRMap['HIG-25-020']['ZH2HLEPLEP_PTV_150_250_0J'] = {'mode':'constant', 'factor':0.051176285*XS['ZH2HLEPLEP']}
XSBRMap['HIG-25-020']['ZH2HLEPLEP_PTV_150_250_GE1J'] = {'mode':'constant', 'factor':0.043147041*XS['ZH2HLEPLEP']}
XSBRMap['HIG-25-020']['ZH2HLEPLEP_PTV_GT250'] = {'mode':'constant', 'factor':0.027700738*XS['ZH2HLEPLEP']}
XSBRMap['HIG-25-020']['GG2HLL_FWDH'] = {'mode':'constant', 'factor':0.030792199*XS['GG2HLL']}
XSBRMap['HIG-25-020']['GG2HLL_PTV_0_75'] = {'mode':'constant', 'factor':0.159522254*XS['GG2HLL']}
XSBRMap['HIG-25-020']['GG2HLL_PTV_75_150'] = {'mode':'constant', 'factor':0.439749923*XS['GG2HLL']}
XSBRMap['HIG-25-020']['GG2HLL_PTV_150_250_0J'] = {'mode':'constant', 'factor':0.09267519*XS['GG2HLL']}
XSBRMap['HIG-25-020']['GG2HLL_PTV_150_250_GE1J'] = {'mode':'constant', 'factor':0.205076054*XS['GG2HLL']}
XSBRMap['HIG-25-020']['GG2HLL_PTV_GT250'] = {'mode':'constant', 'factor':0.07218438*XS['GG2HLL']}
XSBRMap['HIG-25-020']['GG2HNUNU_FWDH'] = {'mode':'constant', 'factor':0.030397738*XS['GG2HNUNU']}
XSBRMap['HIG-25-020']['GG2HNUNU_PTV_0_75'] = {'mode':'constant', 'factor':0.161197308*XS['GG2HNUNU']}
XSBRMap['HIG-25-020']['GG2HNUNU_PTV_75_150'] = {'mode':'constant', 'factor':0.440060273*XS['GG2HNUNU']}
XSBRMap['HIG-25-020']['GG2HNUNU_PTV_150_250_0J'] = {'mode':'constant', 'factor':0.094392975*XS['GG2HNUNU']}
XSBRMap['HIG-25-020']['GG2HNUNU_PTV_150_250_GE1J'] = {'mode':'constant', 'factor':0.202701193*XS['GG2HNUNU']}
XSBRMap['HIG-25-020']['GG2HNUNU_PTV_GT250'] = {'mode':'constant', 'factor':0.071250512*XS['GG2HNUNU']}
XSBRMap['HIG-25-020']['TTH_FWDH'] = {'mode':'constant', 'factor':0.014373861*XS['TTH']}
XSBRMap['HIG-25-020']['TTH_PTH_0_60'] = {'mode':'constant', 'factor':0.232810586*XS['TTH']}
XSBRMap['HIG-25-020']['TTH_PTH_60_120'] = {'mode':'constant', 'factor':0.342957155*XS['TTH']}
XSBRMap['HIG-25-020']['TTH_PTH_120_200'] = {'mode':'constant', 'factor':0.254274159*XS['TTH']}
XSBRMap['HIG-25-020']['TTH_PTH_200_300'] = {'mode':'constant', 'factor':0.105868005*XS['TTH']}
XSBRMap['HIG-25-020']['TTH_PTH_GT300'] = {'mode':'constant', 'factor':0.049716234*XS['TTH']}
XSBRMap['HIG-25-020']['THQ_FWDH'] = {'mode':'constant', 'factor':0.110651592*XS['THQ']}
XSBRMap['HIG-25-020']['THQ_FID'] = {'mode':'constant', 'factor':0.889348408*XS['THQ']}
XSBRMap['HIG-25-020']['THQ2HQQ_FWDH'] = {'mode':'constant', 'factor':0.110651592*XS['THQ2HQQ']}
XSBRMap['HIG-25-020']['THQ2HQQ_FID'] = {'mode':'constant', 'factor':0.889348408*XS['THQ2HQQ']}
XSBRMap['HIG-25-020']['THQ2HLNU_FWDH'] = {'mode':'constant', 'factor':0.110651592*XS['THQ2HLNU']}
XSBRMap['HIG-25-020']['THQ2HLNU_FID'] = {'mode':'constant', 'factor':0.889348408*XS['THQ2HLNU']}
XSBRMap['HIG-25-020']['THW_FWDH'] = {'mode':'constant', 'factor':0.008056908*XS['THW']}
XSBRMap['HIG-25-020']['THW_FID'] = {'mode':'constant', 'factor':0.991943092*XS['THW']}
XSBRMap['HIG-25-020']['BBH_FWDH'] = {'mode':'constant', 'factor':0.055177792*XS['BBH']}
XSBRMap['HIG-25-020']['BBH_FID'] = {'mode':'constant', 'factor':0.944822208*XS['BBH']}


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
  #return _SM.modelBuilder.out.function("SM_XS_%s_%s"%(_pm,sqrts__)).getVal()
  # FIXME: added temp fix as no 13.6 TeV splines in combine
  return _SM.modelBuilder.out.function("SM_XS_%s_%s"%(_pm,"13TeV")).getVal()
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
  #for pm in productionModes: SM.makeXS(pm,sqrts__)
  # FIXME: added temp fix as no 13.6 TeV splines in combine
  for pm in productionModes: SM.makeXS(pm,"13TeV")

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
  for proc in d[d['type']=='sig']['proc'].unique():
    fp = XSBRMap[analysis][proc]['factor'] if 'factor' in XSBRMap[analysis][proc] else 1.
    mode = XSBRMap[analysis][proc]['mode']
    xs = fp*xsbr[mode]
    XSBR_for_analysis['XS_%s'%proc] = xs

  # BR
  fd = XSBRMap[analysis]['decay']['factor'] if 'factor' in XSBRMap[analysis]['decay'] else 1.
  mode = XSBRMap[analysis]['decay']['mode']
  br = fd*xsbr[mode]
  XSBR_for_analysis['BR'] = br
  return XSBR_for_analysis


