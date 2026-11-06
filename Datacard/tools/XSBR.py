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
    "GG2H" : 51.673603,
    "GG2HQQ" : 0.09118151569999998,
    "VBF" : 4.109760,
    "WPLUSH2HQQ": 0.6053101173,
    "WMINUSH2HQQ": 0.38231514089999996,
    "ZH2HQQ" : 0.5710115970999999,
    "WPLUSH2HLNU" : 0.29255308739999997,
    "WMINUSH2HLNU" : 0.1847771442,
    "ZH2HLL" : 0.08247364469400001,
    "ZH2HNUNU" : 0.16335619999999998,
    "ZH2HLEPLEP" : 0.24582984469400002,
    "GG2HLL" : 0.013169735898000001,
    "GG2HNUNU" : 0.026085399999999998,
    "TTH" : 0.592161,
    "THQ" : 0.088481,
    "THQ2HQQ" : 0.059645042100000004,
    "THQ2HLNU" : 0.028827109799999997,
    "THW" : 0.017376,
    "BBH" : 0.568281
}

XSBRMap['HIG-25-020'] = od()
XSBRMap['HIG-25-020']['decay'] = {'mode':'hgg'}
XSBRMap['HIG-25-020']['GG2H_FWDH'] = {'mode':'constant', 'factor':0.08793496933945123*XS['GG2H']}
XSBRMap['HIG-25-020']['GG2H_PTH_200_300'] = {'mode':'constant', 'factor':0.008918359449216368*XS['GG2H']}
XSBRMap['HIG-25-020']['GG2H_PTH_300_450'] = {'mode':'constant', 'factor':0.001970527005648357*XS['GG2H']}
XSBRMap['HIG-25-020']['GG2H_PTH_450_650'] = {'mode':'constant', 'factor':0.0003327904738421465*XS['GG2H']}
XSBRMap['HIG-25-020']['GG2H_PTH_GT650'] = {'mode':'constant', 'factor':3.5413164602218026e-05*XS['GG2H']}
XSBRMap['HIG-25-020']['GG2H_0J_PTH_0_10'] = {'mode':'constant', 'factor':0.13466555841051817*XS['GG2H']}
XSBRMap['HIG-25-020']['GG2H_0J_PTH_GT10'] = {'mode':'constant', 'factor':0.42304807238946235*XS['GG2H']}
XSBRMap['HIG-25-020']['GG2H_1J_PTH_0_60'] = {'mode':'constant', 'factor':0.13871071097321266*XS['GG2H']}
XSBRMap['HIG-25-020']['GG2H_1J_PTH_60_120'] = {'mode':'constant', 'factor':0.08858391814636841*XS['GG2H']}
XSBRMap['HIG-25-020']['GG2H_1J_PTH_120_200'] = {'mode':'constant', 'factor':0.013898767576163495*XS['GG2H']}
XSBRMap['HIG-25-020']['GG2H_GE2J_MJJ_0_350_PTH_0_60'] = {'mode':'constant', 'factor':0.026039602220027526*XS['GG2H']}
XSBRMap['HIG-25-020']['GG2H_GE2J_MJJ_0_350_PTH_60_120'] = {'mode':'constant', 'factor':0.03822365023475605*XS['GG2H']}
XSBRMap['HIG-25-020']['GG2H_GE2J_MJJ_0_350_PTH_120_200'] = {'mode':'constant', 'factor':0.01883668339397882*XS['GG2H']}
XSBRMap['HIG-25-020']['GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.005312410059983659*XS['GG2H']}
XSBRMap['HIG-25-020']['GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.007746630993776355*XS['GG2H']}
XSBRMap['HIG-25-020']['GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.0022491008044499385*XS['GG2H']}
XSBRMap['HIG-25-020']['GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.0034928353645423483*XS['GG2H']}
XSBRMap['HIG-25-020']['GG2HQQ_FWDH'] = {'mode':'constant', 'factor':0.030266969104046363*XS['GG2HQQ']}
XSBRMap['HIG-25-020']['GG2HQQ_PTH_200_300'] = {'mode':'constant', 'factor':0.1356629925572498*XS['GG2HQQ']}
XSBRMap['HIG-25-020']['GG2HQQ_PTH_300_450'] = {'mode':'constant', 'factor':0.03183415497139933*XS['GG2HQQ']}
XSBRMap['HIG-25-020']['GG2HQQ_PTH_450_650'] = {'mode':'constant', 'factor':0.003804065743144229*XS['GG2HQQ']}
XSBRMap['HIG-25-020']['GG2HQQ_PTH_GT650'] = {'mode':'constant', 'factor':0.00038588362834785953*XS['GG2HQQ']}
XSBRMap['HIG-25-020']['GG2HQQ_0J_PTH_0_10'] = {'mode':'constant', 'factor':0.00011327551704337512*XS['GG2HQQ']}
XSBRMap['HIG-25-020']['GG2HQQ_0J_PTH_GT10'] = {'mode':'constant', 'factor':0.003130636557521332*XS['GG2HQQ']}
XSBRMap['HIG-25-020']['GG2HQQ_1J_PTH_0_60'] = {'mode':'constant', 'factor':0.021923169229449157*XS['GG2HQQ']}
XSBRMap['HIG-25-020']['GG2HQQ_1J_PTH_60_120'] = {'mode':'constant', 'factor':0.055785080915722*XS['GG2HQQ']}
XSBRMap['HIG-25-020']['GG2HQQ_1J_PTH_120_200'] = {'mode':'constant', 'factor':0.037301254369369596*XS['GG2HQQ']}
XSBRMap['HIG-25-020']['GG2HQQ_GE2J_MJJ_0_350_PTH_0_60'] = {'mode':'constant', 'factor':0.058807420409129764*XS['GG2HQQ']}
XSBRMap['HIG-25-020']['GG2HQQ_GE2J_MJJ_0_350_PTH_60_120'] = {'mode':'constant', 'factor':0.20039683662539395*XS['GG2HQQ']}
XSBRMap['HIG-25-020']['GG2HQQ_GE2J_MJJ_0_350_PTH_120_200'] = {'mode':'constant', 'factor':0.3019576741092278*XS['GG2HQQ']}
XSBRMap['HIG-25-020']['GG2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.011444561597170284*XS['GG2HQQ']}
XSBRMap['HIG-25-020']['GG2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.07949078319484122*XS['GG2HQQ']}
XSBRMap['HIG-25-020']['GG2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.0033422501698133727*XS['GG2HQQ']}
XSBRMap['HIG-25-020']['GG2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.024352991301130514*XS['GG2HQQ']}
XSBRMap['HIG-25-020']['VBF_FWDH'] = {'mode':'constant', 'factor':0.0722533130749873*XS['VBF']}
XSBRMap['HIG-25-020']['VBF_0J'] = {'mode':'constant', 'factor':0.07033905175440057*XS['VBF']}
XSBRMap['HIG-25-020']['VBF_1J'] = {'mode':'constant', 'factor':0.33303695754616064*XS['VBF']}
XSBRMap['HIG-25-020']['VBF_GE2J_MJJ_0_60'] = {'mode':'constant', 'factor':0.012667952175159083*XS['VBF']}
XSBRMap['HIG-25-020']['VBF_GE2J_MJJ_60_120'] = {'mode':'constant', 'factor':0.021875480210705442*XS['VBF']}
XSBRMap['HIG-25-020']['VBF_GE2J_MJJ_120_350'] = {'mode':'constant', 'factor':0.11104806117364377*XS['VBF']}
XSBRMap['HIG-25-020']['VBF_GE2J_MJJ_GT350_PTH_GT200'] = {'mode':'constant', 'factor':0.039941147587534885*XS['VBF']}
XSBRMap['HIG-25-020']['VBF_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.10590618187595*XS['VBF']}
XSBRMap['HIG-25-020']['VBF_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.030256852966192693*XS['VBF']}
XSBRMap['HIG-25-020']['VBF_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.16691032758976868*XS['VBF']}
XSBRMap['HIG-25-020']['VBF_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.035764674045496984*XS['VBF']}
XSBRMap['HIG-25-020']['WPLUSH2HQQ_FWDH'] = {'mode':'constant', 'factor':0.1556872883263824*XS['WPLUSH2HQQ']}
XSBRMap['HIG-25-020']['WPLUSH2HQQ_0J'] = {'mode':'constant', 'factor':0.05282352199041132*XS['WPLUSH2HQQ']}
XSBRMap['HIG-25-020']['WPLUSH2HQQ_1J'] = {'mode':'constant', 'factor':0.2997442561605921*XS['WPLUSH2HQQ']}
XSBRMap['HIG-25-020']['WPLUSH2HQQ_GE2J_MJJ_0_60'] = {'mode':'constant', 'factor':0.030702887545768307*XS['WPLUSH2HQQ']}
XSBRMap['HIG-25-020']['WPLUSH2HQQ_GE2J_MJJ_60_120'] = {'mode':'constant', 'factor':0.29248133356882217*XS['WPLUSH2HQQ']}
XSBRMap['HIG-25-020']['WPLUSH2HQQ_GE2J_MJJ_120_350'] = {'mode':'constant', 'factor':0.12949589254069419*XS['WPLUSH2HQQ']}
XSBRMap['HIG-25-020']['WPLUSH2HQQ_GE2J_MJJ_GT350_PTH_GT200'] = {'mode':'constant', 'factor':0.009543195819356077*XS['WPLUSH2HQQ']}
XSBRMap['HIG-25-020']['WPLUSH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.003928127041624144*XS['WPLUSH2HQQ']}
XSBRMap['HIG-25-020']['WPLUSH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.020003262334377686*XS['WPLUSH2HQQ']}
XSBRMap['HIG-25-020']['WPLUSH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.0006824775714926606*XS['WPLUSH2HQQ']}
XSBRMap['HIG-25-020']['WPLUSH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.004907757100478961*XS['WPLUSH2HQQ']}
XSBRMap['HIG-25-020']['WMINUSH2HQQ_FWDH'] = {'mode':'constant', 'factor':0.09724205269287194*XS['WMINUSH2HQQ']}
XSBRMap['HIG-25-020']['WMINUSH2HQQ_0J'] = {'mode':'constant', 'factor':0.05960920478235342*XS['WMINUSH2HQQ']}
XSBRMap['HIG-25-020']['WMINUSH2HQQ_1J'] = {'mode':'constant', 'factor':0.3289617488728546*XS['WMINUSH2HQQ']}
XSBRMap['HIG-25-020']['WMINUSH2HQQ_GE2J_MJJ_0_60'] = {'mode':'constant', 'factor':0.03287199663390261*XS['WMINUSH2HQQ']}
XSBRMap['HIG-25-020']['WMINUSH2HQQ_GE2J_MJJ_60_120'] = {'mode':'constant', 'factor':0.3085342240935115*XS['WMINUSH2HQQ']}
XSBRMap['HIG-25-020']['WMINUSH2HQQ_GE2J_MJJ_120_350'] = {'mode':'constant', 'factor':0.1372613243367716*XS['WMINUSH2HQQ']}
XSBRMap['HIG-25-020']['WMINUSH2HQQ_GE2J_MJJ_GT350_PTH_GT200'] = {'mode':'constant', 'factor':0.007409614754416615*XS['WMINUSH2HQQ']}
XSBRMap['HIG-25-020']['WMINUSH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.003848801477137273*XS['WMINUSH2HQQ']}
XSBRMap['HIG-25-020']['WMINUSH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.01924959438595821*XS['WMINUSH2HQQ']}
XSBRMap['HIG-25-020']['WMINUSH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.0006214648597517627*XS['WMINUSH2HQQ']}
XSBRMap['HIG-25-020']['WMINUSH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.004389973110470433*XS['WMINUSH2HQQ']}
XSBRMap['HIG-25-020']['ZH2HQQ_FWDH'] = {'mode':'constant', 'factor':0.12110359986743316*XS['ZH2HQQ']}
XSBRMap['HIG-25-020']['ZH2HQQ_0J'] = {'mode':'constant', 'factor':0.04347960812348332*XS['ZH2HQQ']}
XSBRMap['HIG-25-020']['ZH2HQQ_1J'] = {'mode':'constant', 'factor':0.2877808073071237*XS['ZH2HQQ']}
XSBRMap['HIG-25-020']['ZH2HQQ_GE2J_MJJ_0_60'] = {'mode':'constant', 'factor':0.027289169821139016*XS['ZH2HQQ']}
XSBRMap['HIG-25-020']['ZH2HQQ_GE2J_MJJ_60_120'] = {'mode':'constant', 'factor':0.3406705213736634*XS['ZH2HQQ']}
XSBRMap['HIG-25-020']['ZH2HQQ_GE2J_MJJ_120_350'] = {'mode':'constant', 'factor':0.14065063717776524*XS['ZH2HQQ']}
XSBRMap['HIG-25-020']['ZH2HQQ_GE2J_MJJ_GT350_PTH_GT200'] = {'mode':'constant', 'factor':0.007906087487565565*XS['ZH2HQQ']}
XSBRMap['HIG-25-020']['ZH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.0038846206725853915*XS['ZH2HQQ']}
XSBRMap['HIG-25-020']['ZH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.021174991521277785*XS['ZH2HQQ']}
XSBRMap['HIG-25-020']['ZH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.0006170982720889831*XS['ZH2HQQ']}
XSBRMap['HIG-25-020']['ZH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.0054428583758744774*XS['ZH2HQQ']}
XSBRMap['HIG-25-020']['WPLUSH2HLNU_FWDH'] = {'mode':'constant', 'factor':0.15271176113315452*XS['WPLUSH2HLNU']}
XSBRMap['HIG-25-020']['WPLUSH2HLNU_PTV_0_75'] = {'mode':'constant', 'factor':0.43356786699791927*XS['WPLUSH2HLNU']}
XSBRMap['HIG-25-020']['WPLUSH2HLNU_PTV_75_150'] = {'mode':'constant', 'factor':0.28767526534583987*XS['WPLUSH2HLNU']}
XSBRMap['HIG-25-020']['WPLUSH2HLNU_PTV_150_250_0J'] = {'mode':'constant', 'factor':0.05318084961358207*XS['WPLUSH2HLNU']}
XSBRMap['HIG-25-020']['WPLUSH2HLNU_PTV_150_250_GE1J'] = {'mode':'constant', 'factor':0.0411416402570863*XS['WPLUSH2HLNU']}
XSBRMap['HIG-25-020']['WPLUSH2HLNU_PTV_GT250'] = {'mode':'constant', 'factor':0.031722616652417955*XS['WPLUSH2HLNU']}
XSBRMap['HIG-25-020']['WMINUSH2HLNU_FWDH'] = {'mode':'constant', 'factor':0.09648710686467347*XS['WMINUSH2HLNU']}
XSBRMap['HIG-25-020']['WMINUSH2HLNU_PTV_0_75'] = {'mode':'constant', 'factor':0.4867718359456386*XS['WMINUSH2HLNU']}
XSBRMap['HIG-25-020']['WMINUSH2HLNU_PTV_75_150'] = {'mode':'constant', 'factor':0.3013837813167588*XS['WMINUSH2HLNU']}
XSBRMap['HIG-25-020']['WMINUSH2HLNU_PTV_150_250_0J'] = {'mode':'constant', 'factor':0.05041842737069779*XS['WMINUSH2HLNU']}
XSBRMap['HIG-25-020']['WMINUSH2HLNU_PTV_150_250_GE1J'] = {'mode':'constant', 'factor':0.03911373986842681*XS['WMINUSH2HLNU']}
XSBRMap['HIG-25-020']['WMINUSH2HLNU_PTV_GT250'] = {'mode':'constant', 'factor':0.025825108633804533*XS['WMINUSH2HLNU']}
XSBRMap['HIG-25-020']['ZH2HLL_FWDH'] = {'mode':'constant', 'factor':0.11820190886407907*XS['ZH2HLL']}
XSBRMap['HIG-25-020']['ZH2HLL_PTV_0_75'] = {'mode':'constant', 'factor':0.4552694647142518*XS['ZH2HLL']}
XSBRMap['HIG-25-020']['ZH2HLL_PTV_75_150'] = {'mode':'constant', 'factor':0.3016284728356651*XS['ZH2HLL']}
XSBRMap['HIG-25-020']['ZH2HLL_PTV_150_250_0J'] = {'mode':'constant', 'factor':0.05298967595175157*XS['ZH2HLL']}
XSBRMap['HIG-25-020']['ZH2HLL_PTV_150_250_GE1J'] = {'mode':'constant', 'factor':0.042352236601418666*XS['ZH2HLL']}
XSBRMap['HIG-25-020']['ZH2HLL_PTV_GT250'] = {'mode':'constant', 'factor':0.029558241032833794*XS['ZH2HLL']}
XSBRMap['HIG-25-020']['ZH2HNUNU_FWDH'] = {'mode':'constant', 'factor':0.11881261579156738*XS['ZH2HNUNU']}
XSBRMap['HIG-25-020']['ZH2HNUNU_PTV_0_75'] = {'mode':'constant', 'factor':0.45321104356596154*XS['ZH2HNUNU']}
XSBRMap['HIG-25-020']['ZH2HNUNU_PTV_75_150'] = {'mode':'constant', 'factor':0.3023083899029264*XS['ZH2HNUNU']}
XSBRMap['HIG-25-020']['ZH2HNUNU_PTV_150_250_0J'] = {'mode':'constant', 'factor':0.05313440620363219*XS['ZH2HNUNU']}
XSBRMap['HIG-25-020']['ZH2HNUNU_PTV_150_250_GE1J'] = {'mode':'constant', 'factor':0.043077607875712146*XS['ZH2HNUNU']}
XSBRMap['HIG-25-020']['ZH2HNUNU_PTV_GT250'] = {'mode':'constant', 'factor':0.029455936660200358*XS['ZH2HNUNU']}
XSBRMap['HIG-25-020']['GG2HLL_FWDH'] = {'mode':'constant', 'factor':0.03053787319098257*XS['GG2HLL']}
XSBRMap['HIG-25-020']['GG2HLL_PTV_0_75'] = {'mode':'constant', 'factor':0.15979988436332604*XS['GG2HLL']}
XSBRMap['HIG-25-020']['GG2HLL_PTV_75_150'] = {'mode':'constant', 'factor':0.4421118298201533*XS['GG2HLL']}
XSBRMap['HIG-25-020']['GG2HLL_PTV_150_250_0J'] = {'mode':'constant', 'factor':0.09450408368635212*XS['GG2HLL']}
XSBRMap['HIG-25-020']['GG2HLL_PTV_150_250_GE1J'] = {'mode':'constant', 'factor':0.2014868649920957*XS['GG2HLL']}
XSBRMap['HIG-25-020']['GG2HLL_PTV_GT250'] = {'mode':'constant', 'factor':0.07155946394709028*XS['GG2HLL']}
XSBRMap['HIG-25-020']['GG2HNUNU_FWDH'] = {'mode':'constant', 'factor':0.0305770161094599*XS['GG2HNUNU']}
XSBRMap['HIG-25-020']['GG2HNUNU_PTV_0_75'] = {'mode':'constant', 'factor':0.159868213791565*XS['GG2HNUNU']}
XSBRMap['HIG-25-020']['GG2HNUNU_PTV_75_150'] = {'mode':'constant', 'factor':0.44155926164673476*XS['GG2HNUNU']}
XSBRMap['HIG-25-020']['GG2HNUNU_PTV_150_250_0J'] = {'mode':'constant', 'factor':0.09352962681858218*XS['GG2HNUNU']}
XSBRMap['HIG-25-020']['GG2HNUNU_PTV_150_250_GE1J'] = {'mode':'constant', 'factor':0.203018666016631*XS['GG2HNUNU']}
XSBRMap['HIG-25-020']['GG2HNUNU_PTV_GT250'] = {'mode':'constant', 'factor':0.07144721561702723*XS['GG2HNUNU']}
XSBRMap['HIG-25-020']['TTH_FWDH'] = {'mode':'constant', 'factor':0.015241625072948543*XS['TTH']}
XSBRMap['HIG-25-020']['TTH_PTH_0_60'] = {'mode':'constant', 'factor':0.2326723321900437*XS['TTH']}
XSBRMap['HIG-25-020']['TTH_PTH_60_120'] = {'mode':'constant', 'factor':0.35130838206469855*XS['TTH']}
XSBRMap['HIG-25-020']['TTH_PTH_120_200'] = {'mode':'constant', 'factor':0.2488938139863567*XS['TTH']}
XSBRMap['HIG-25-020']['TTH_PTH_200_300'] = {'mode':'constant', 'factor':0.10345447542821952*XS['TTH']}
XSBRMap['HIG-25-020']['TTH_PTH_GT300'] = {'mode':'constant', 'factor':0.04842937125773297*XS['TTH']}
XSBRMap['HIG-25-020']['THQ_FWDH'] = {'mode':'constant', 'factor':0.10110201592800672*XS['THQ']}
XSBRMap['HIG-25-020']['THQ_FID'] = {'mode':'constant', 'factor':0.8988979840719933*XS['THQ']}
XSBRMap['HIG-25-020']['THQ2HQQ_FWDH'] = {'mode':'constant', 'factor':0.10143059712692852*XS['THQ2HQQ']}
XSBRMap['HIG-25-020']['THQ2HQQ_FID'] = {'mode':'constant', 'factor':0.8985694028730715*XS['THQ2HQQ']}
XSBRMap['HIG-25-020']['THQ2HLNU_FWDH'] = {'mode':'constant', 'factor':0.1004221614584142*XS['THQ2HLNU']}
XSBRMap['HIG-25-020']['THQ2HLNU_FID'] = {'mode':'constant', 'factor':0.8995778385415858*XS['THQ2HLNU']}
XSBRMap['HIG-25-020']['THW_FWDH'] = {'mode':'constant', 'factor':0.0082992390744502*XS['THW']}
XSBRMap['HIG-25-020']['THW_FID'] = {'mode':'constant', 'factor':0.9917007609255498*XS['THW']}
XSBRMap['HIG-25-020']['BBH_FWDH'] = {'mode':'constant', 'factor':0.05504122860678072*XS['BBH']}
XSBRMap['HIG-25-020']['BBH_FID'] = {'mode':'constant', 'factor':0.9449587713932193*XS['BBH']}

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


