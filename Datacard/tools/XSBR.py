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

XSBRMap['Run3STXS12'] = od()
XSBRMap['Run3STXS12']['decay'] = {'mode':'hgg'}
XSBRMap['Run3STXS12'][f'GG2H_FWDH'] = {'mode':'constant', 'factor':4.452454062335999}
XSBRMap['Run3STXS12'][f'GG2H_PTH_200_300'] = {'mode':'constant', 'factor':0.742248611739905}
XSBRMap['Run3STXS12'][f'GG2H_PTH_300_450'] = {'mode':'constant', 'factor':0.2569282211079247}
XSBRMap['Run3STXS12'][f'GG2H_PTH_450_650'] = {'mode':'constant', 'factor':0.06558103324171183}
XSBRMap['Run3STXS12'][f'GG2H_PTH_GT650'] = {'mode':'constant', 'factor':0.01743293292022304}
XSBRMap['Run3STXS12'][f'GG2H_0J_PTH_0_10'] = {'mode':'constant', 'factor':7.206649791438642}
XSBRMap['Run3STXS12'][f'GG2H_0J_PTH_GT10'] = {'mode':'constant', 'factor':20.233408719041858}
XSBRMap['Run3STXS12'][f'GG2H_1J_PTH_0_60'] = {'mode':'constant', 'factor':7.280220917066073}
XSBRMap['Run3STXS12'][f'GG2H_1J_PTH_60_120'] = {'mode':'constant', 'factor':5.2482466089417406}
XSBRMap['Run3STXS12'][f'GG2H_1J_PTH_120_200'] = {'mode':'constant', 'factor':1.0927750903729103}
XSBRMap['Run3STXS12'][f'GG2H_GE2J_MJJ_0_350_PTH_0_60'] = {'mode':'constant', 'factor':1.3729472392221491}
XSBRMap['Run3STXS12'][f'GG2H_GE2J_MJJ_0_350_PTH_60_120'] = {'mode':'constant', 'factor':2.0168242375363197}
XSBRMap['Run3STXS12'][f'GG2H_GE2J_MJJ_0_350_PTH_120_200'] = {'mode':'constant', 'factor':1.1550355486583803}
XSBRMap['Run3STXS12'][f'GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.3357914908587647}
XSBRMap['Run3STXS12'][f'GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.4204657285709297}
XSBRMap['Run3STXS12'][f'GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.15305699585548868}
XSBRMap['Run3STXS12'][f'GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.17993277109097414}
XSBRMap['Run3STXS12'][f'VBF_FWDH'] = {'mode':'constant', 'factor':0.30906179249042953}
XSBRMap['Run3STXS12'][f'VBF_0J'] = {'mode':'constant', 'factor':0.26020084849442665}
XSBRMap['Run3STXS12'][f'VBF_1J'] = {'mode':'constant', 'factor':1.3366618521641214}
XSBRMap['Run3STXS12'][f'VBF_GE2J_MJJ_0_60'] = {'mode':'constant', 'factor':0.04421373111576067}
XSBRMap['Run3STXS12'][f'VBF_GE2J_MJJ_60_120'] = {'mode':'constant', 'factor':0.07348686900193459}
XSBRMap['Run3STXS12'][f'VBF_GE2J_MJJ_120_350'] = {'mode':'constant', 'factor':0.4391839200979416}
XSBRMap['Run3STXS12'][f'VBF_GE2J_MJJ_GT350_PTH_GT200'] = {'mode':'constant', 'factor':0.17559539236044044}
XSBRMap['Run3STXS12'][f'VBF_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.48873978595619433}
XSBRMap['Run3STXS12'][f'VBF_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.09290095216557219}
XSBRMap['Run3STXS12'][f'VBF_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.6751497526714281}
XSBRMap['Run3STXS12'][f'VBF_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.18280510348175089}
XSBRMap['Run3STXS12'][f'TTH_FWDH'] = {'mode':'constant', 'factor':0.008193101006813874}
XSBRMap['Run3STXS12'][f'TTH_PTH_0_60'] = {'mode':'constant', 'factor':0.13270203375560813}
XSBRMap['Run3STXS12'][f'TTH_PTH_60_120'] = {'mode':'constant', 'factor':0.19548557858751595}
XSBRMap['Run3STXS12'][f'TTH_PTH_120_200'] = {'mode':'constant', 'factor':0.14493627062366152}
XSBRMap['Run3STXS12'][f'TTH_PTH_200_300'] = {'mode':'constant', 'factor':0.060344762800465024}
XSBRMap['Run3STXS12'][f'TTH_PTH_GT300'] = {'mode':'constant', 'factor':0.028338253225935466}
XSBRMap['Run3STXS12'][f'THQ_FWDH'] = {'mode':'constant', 'factor':0.009592165219271682}
XSBRMap['Run3STXS12'][f'THQ_FID'] = {'mode':'constant', 'factor':0.07709583478072832}
XSBRMap['Run3STXS12'][f'THW_FWDH'] = {'mode':'constant', 'factor':0.00013857882426542638}
XSBRMap['Run3STXS12'][f'THW_FID'] = {'mode':'constant', 'factor':0.017061421175734573}
XSBRMap['Run3STXS12'][f'WMINUSH2HQQ_FWDH'] = {'mode':'constant', 'factor':0.035634993187838505}
XSBRMap['Run3STXS12'][f'WMINUSH2HQQ_0J'] = {'mode':'constant', 'factor':0.0230882929447906}
XSBRMap['Run3STXS12'][f'WMINUSH2HQQ_1J'] = {'mode':'constant', 'factor':0.12418993397250003}
XSBRMap['Run3STXS12'][f'WMINUSH2HQQ_GE2J_MJJ_0_60'] = {'mode':'constant', 'factor':0.012453418359100773}
XSBRMap['Run3STXS12'][f'WMINUSH2HQQ_GE2J_MJJ_60_120'] = {'mode':'constant', 'factor':0.11855062961509753}
XSBRMap['Run3STXS12'][f'WMINUSH2HQQ_GE2J_MJJ_120_350'] = {'mode':'constant', 'factor':0.05446645981119059}
XSBRMap['Run3STXS12'][f'WMINUSH2HQQ_GE2J_MJJ_GT350_PTH_GT200'] = {'mode':'constant', 'factor':0.0028794456254774355}
XSBRMap['Run3STXS12'][f'WMINUSH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.0015847700440967524}
XSBRMap['Run3STXS12'][f'WMINUSH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.007734490737356786}
XSBRMap['Run3STXS12'][f'WMINUSH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.00021268388547402065}
XSBRMap['Run3STXS12'][f'WMINUSH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.0018914518170770201}
XSBRMap['Run3STXS12'][f'WMINUSH2HLNU_FWDH'] = {'mode':'constant', 'factor':0.01795261149324277}
XSBRMap['Run3STXS12'][f'WMINUSH2HLNU_PTV_0_75'] = {'mode':'constant', 'factor':0.09065147992552919}
XSBRMap['Run3STXS12'][f'WMINUSH2HLNU_PTV_75_150'] = {'mode':'constant', 'factor':0.05482069590239782}
XSBRMap['Run3STXS12'][f'WMINUSH2HLNU_PTV_150_250_0J'] = {'mode':'constant', 'factor':0.009259064032410894}
XSBRMap['Run3STXS12'][f'WMINUSH2HLNU_PTV_150_250_GE1J'] = {'mode':'constant', 'factor':0.007431724739152518}
XSBRMap['Run3STXS12'][f'WMINUSH2HLNU_PTV_GT250'] = {'mode':'constant', 'factor':0.00484108390726685}
XSBRMap['Run3STXS12'][f'WPLUSH2HQQ_FWDH'] = {'mode':'constant', 'factor':0.0906592652504524}
XSBRMap['Run3STXS12'][f'WPLUSH2HQQ_0J'] = {'mode':'constant', 'factor':0.030613171988068913}
XSBRMap['Run3STXS12'][f'WPLUSH2HQQ_1J'] = {'mode':'constant', 'factor':0.17810094812040317}
XSBRMap['Run3STXS12'][f'WPLUSH2HQQ_GE2J_MJJ_0_60'] = {'mode':'constant', 'factor':0.01853026125408403}
XSBRMap['Run3STXS12'][f'WPLUSH2HQQ_GE2J_MJJ_60_120'] = {'mode':'constant', 'factor':0.1792122237603338}
XSBRMap['Run3STXS12'][f'WPLUSH2HQQ_GE2J_MJJ_120_350'] = {'mode':'constant', 'factor':0.0791611678989454}
XSBRMap['Run3STXS12'][f'WPLUSH2HQQ_GE2J_MJJ_GT350_PTH_GT200'] = {'mode':'constant', 'factor':0.005422462430148131}
XSBRMap['Run3STXS12'][f'WPLUSH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.0022322199352340943}
XSBRMap['Run3STXS12'][f'WPLUSH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.012062111003472974}
XSBRMap['Run3STXS12'][f'WPLUSH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.00044112610965828334}
XSBRMap['Run3STXS12'][f'WPLUSH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.0027725322491988997}
XSBRMap['Run3STXS12'][f'WPLUSH2HLNU_FWDH'] = {'mode':'constant', 'factor':0.04494315480687072}
XSBRMap['Run3STXS12'][f'WPLUSH2HLNU_PTV_0_75'] = {'mode':'constant', 'factor':0.12501363463592902}
XSBRMap['Run3STXS12'][f'WPLUSH2HLNU_PTV_75_150'] = {'mode':'constant', 'factor':0.08334789328833658}
XSBRMap['Run3STXS12'][f'WPLUSH2HLNU_PTV_150_250_0J'] = {'mode':'constant', 'factor':0.014848185489994519}
XSBRMap['Run3STXS12'][f'WPLUSH2HLNU_PTV_150_250_GE1J'] = {'mode':'constant', 'factor':0.012031094523527507}
XSBRMap['Run3STXS12'][f'WPLUSH2HLNU_PTV_GT250'] = {'mode':'constant', 'factor':0.009419657255341643}
XSBRMap['Run3STXS12'][f'ZH2HLL_FWDH'] = {'mode':'constant', 'factor':0.01138343980399486}
XSBRMap['Run3STXS12'][f'ZH2HLL_PTV_0_75'] = {'mode':'constant', 'factor':0.04321766588424201}
XSBRMap['Run3STXS12'][f'ZH2HLL_PTV_75_150'] = {'mode':'constant', 'factor':0.02886382437553178}
XSBRMap['Run3STXS12'][f'ZH2HLL_PTV_150_250_0J'] = {'mode':'constant', 'factor':0.005035555083396863}
XSBRMap['Run3STXS12'][f'ZH2HLL_PTV_150_250_GE1J'] = {'mode':'constant', 'factor':0.003983460461075898}
XSBRMap['Run3STXS12'][f'ZH2HLL_PTV_GT250'] = {'mode':'constant', 'factor':0.0028254129917586047}
XSBRMap['Run3STXS12'][f'ZH2HNUNU_FWDH'] = {'mode':'constant', 'factor':0.02242173191744918}
XSBRMap['Run3STXS12'][f'ZH2HNUNU_PTV_0_75'] = {'mode':'constant', 'factor':0.08630362472185986}
XSBRMap['Run3STXS12'][f'ZH2HNUNU_PTV_75_150'] = {'mode':'constant', 'factor':0.05716309595379858}
XSBRMap['Run3STXS12'][f'ZH2HNUNU_PTV_150_250_0J'] = {'mode':'constant', 'factor':0.00949898877893254}
XSBRMap['Run3STXS12'][f'ZH2HNUNU_PTV_150_250_GE1J'] = {'mode':'constant', 'factor':0.00827070284676212}
XSBRMap['Run3STXS12'][f'ZH2HNUNU_PTV_GT250'] = {'mode':'constant', 'factor':0.005041855781197736}
XSBRMap['Run3STXS12'][f'ZH2HQQ_FWDH'] = {'mode':'constant', 'factor':0.0788416608697549}
XSBRMap['Run3STXS12'][f'ZH2HQQ_0J'] = {'mode':'constant', 'factor':0.028075516770689216}
XSBRMap['Run3STXS12'][f'ZH2HQQ_1J'] = {'mode':'constant', 'factor':0.1886563596888995}
XSBRMap['Run3STXS12'][f'ZH2HQQ_GE2J_MJJ_0_60'] = {'mode':'constant', 'factor':0.01805988693533062}
XSBRMap['Run3STXS12'][f'ZH2HQQ_GE2J_MJJ_60_120'] = {'mode':'constant', 'factor':0.226734275909364}
XSBRMap['Run3STXS12'][f'ZH2HQQ_GE2J_MJJ_120_350'] = {'mode':'constant', 'factor':0.0933424920454782}
XSBRMap['Run3STXS12'][f'ZH2HQQ_GE2J_MJJ_GT350_PTH_GT200'] = {'mode':'constant', 'factor':0.005517196244158761}
XSBRMap['Run3STXS12'][f'ZH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.002513830395119137}
XSBRMap['Run3STXS12'][f'ZH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.014275910673316648}
XSBRMap['Run3STXS12'][f'ZH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.003585516057158526}
XSBRMap['Run3STXS12'][f'ZH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.0002778444107304571}
XSBRMap['Run3STXS12'][f'BBH_FWDH'] = {'mode':'constant', 'factor':0.029056625407216003}
XSBRMap['Run3STXS12'][f'BBH_FID'] = {'mode':'constant', 'factor':0.49754337459278397}
XSBRMap['Run3STXS12'][f'GG2HLL_FWDH'] = {'mode':'constant', 'factor':0.00021055705991034662}
XSBRMap['Run3STXS12'][f'GG2HLL_PTV_0_75'] = {'mode':'constant', 'factor':0.0010908131720775646}
XSBRMap['Run3STXS12'][f'GG2HLL_PTV_75_150'] = {'mode':'constant', 'factor':0.003007009971313092}
XSBRMap['Run3STXS12'][f'GG2HLL_PTV_150_250_0J'] = {'mode':'constant', 'factor':0.0006337129488545543}
XSBRMap['Run3STXS12'][f'GG2HLL_PTV_150_250_GE1J'] = {'mode':'constant', 'factor':0.0014023100563868667}
XSBRMap['Run3STXS12'][f'GG2HLL_PTV_GT250'] = {'mode':'constant', 'factor':0.0004935967914575765}
XSBRMap['Run3STXS12'][f'GG2HNUNU_FWDH'] = {'mode':'constant', 'factor':0.000410673439433009}
XSBRMap['Run3STXS12'][f'GG2HNUNU_PTV_0_75'] = {'mode':'constant', 'factor':0.0021777756372606716}
XSBRMap['Run3STXS12'][f'GG2HNUNU_PTV_75_150'] = {'mode':'constant', 'factor':0.005945214287566574}
XSBRMap['Run3STXS12'][f'GG2HNUNU_PTV_150_250_0J'] = {'mode':'constant', 'factor':0.0012752490973046416}
XSBRMap['Run3STXS12'][f'GG2HNUNU_PTV_150_250_GE1J'] = {'mode':'constant', 'factor':0.002738493115937783}
XSBRMap['Run3STXS12'][f'GG2HNUNU_PTV_GT250'] = {'mode':'constant', 'factor':0.0009625944224973184}
XSBRMap['Run3STXS12'][f'GG2HQQ_FWDH'] = {'mode':'constant', 'factor':0.0014452873646897814}
XSBRMap['Run3STXS12'][f'GG2HQQ_PTH_200_300'] = {'mode':'constant', 'factor':0.006557575799101074}
XSBRMap['Run3STXS12'][f'GG2HQQ_PTH_300_450'] = {'mode':'constant', 'factor':0.0015724100341308021}
XSBRMap['Run3STXS12'][f'GG2HQQ_PTH_450_650'] = {'mode':'constant', 'factor':0.0001750381871262402}
XSBRMap['Run3STXS12'][f'GG2HQQ_PTH_GT650'] = {'mode':'constant', 'factor':9.778669557475902e-06}
XSBRMap['Run3STXS12'][f'GG2HQQ_0J_PTH_0_10'] = {'mode':'constant', 'factor':3.911467822990361e-06}
XSBRMap['Run3STXS12'][f'GG2HQQ_0J_PTH_GT10'] = {'mode':'constant', 'factor':0.00013592350684891506}
XSBRMap['Run3STXS12'][f'GG2HQQ_1J_PTH_0_60'] = {'mode':'constant', 'factor':0.0009690661490510189}
XSBRMap['Run3STXS12'][f'GG2HQQ_1J_PTH_60_120'] = {'mode':'constant', 'factor':0.002590369528921779}
XSBRMap['Run3STXS12'][f'GG2HQQ_1J_PTH_120_200'] = {'mode':'constant', 'factor':0.001769939204235089}
XSBRMap['Run3STXS12'][f'GG2HQQ_GE2J_MJJ_0_350_PTH_0_60'] = {'mode':'constant', 'factor':0.002805500355415061}
XSBRMap['Run3STXS12'][f'GG2HQQ_GE2J_MJJ_0_350_PTH_60_120'] = {'mode':'constant', 'factor':0.009619277192503507}
XSBRMap['Run3STXS12'][f'GG2HQQ_GE2J_MJJ_0_350_PTH_120_200'] = {'mode':'constant', 'factor':0.01434824186830087}
XSBRMap['Run3STXS12'][f'GG2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.0005720521773020264}
XSBRMap['Run3STXS12'][f'GG2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.003870397437465442}
XSBRMap['Run3STXS12'][f'GG2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.00017894965699665207}
XSBRMap['Run3STXS12'][f'GG2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.0011362814005312783}

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
    print(proc)
    print(analysis)
    print(XSBRMap[analysis])
    print(XSBRMap[analysis][proc])
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


