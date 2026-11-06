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

globalXSBRMap['Run3STXS'] = od()
globalXSBRMap['Run3STXS']['decay'] = {'mode':'hgg'}
globalXSBRMap['Run3STXS']['gghtruth'] = {'mode':'constant', 'factor':52.277759999999994}
globalXSBRMap['Run3STXS']['tthtruth'] = {'mode':'constant', 'factor':0.57}
globalXSBRMap['Run3STXS']['thtruth'] = {'mode':'constant', 'factor':0.10388800000000001}
globalXSBRMap['Run3STXS']['whltruth'] = {'mode':'constant', 'factor':0.47456028}
globalXSBRMap['Run3STXS']['zhltruth'] = {'mode':'constant', 'factor':0.2840093586}
globalXSBRMap['Run3STXS']['vbftruth'] = {'mode':'constant', 'factor':4.078}
globalXSBRMap['Run3STXS']['vhqtruth'] = {'mode':'constant', 'factor':1.64177455}
globalXSBRMap['Run3STXS']['bbhtruth'] = {'mode':'constant', 'factor':0.5266}
globalXSBRMap['Run3STXS']['ggzhtruth'] = {'mode':'constant', 'factor':0.020347999999999998}

globalXSBRMap['Run3STXS0'] = od()
globalXSBRMap['Run3STXS0']['decay'] = {'mode':'hgg'}
globalXSBRMap['Run3STXS0']['GG2H__preEE'] = {'mode':'constant', 'factor':52.277759999999994}
globalXSBRMap['Run3STXS0']['GG2H_FWDH_preEE'] = {'mode':'constant', 'factor':52.277759999999994}
globalXSBRMap['Run3STXS0']['TTH__preEE'] = {'mode':'constant', 'factor':0.57}
globalXSBRMap['Run3STXS0']['TTH_FWDH_preEE'] = {'mode':'constant', 'factor':0.57}
globalXSBRMap['Run3STXS0']['THQ__preEE'] = {'mode':'constant', 'factor':0.086688}
globalXSBRMap['Run3STXS0']['THQ_FWDH_preEE'] = {'mode':'constant', 'factor':0.086688}
globalXSBRMap['Run3STXS0']['THW__preEE'] = {'mode':'constant', 'factor':0.0172}
globalXSBRMap['Run3STXS0']['THW_FWDH_preEE'] = {'mode':'constant', 'factor':0.0172}
globalXSBRMap['Run3STXS0']['WMINUSH2HQQ__preEE'] = {'mode':'constant', 'factor':0.38268657}
globalXSBRMap['Run3STXS0']['WMINUSH2HQQ_FWDH_preEE'] = {'mode':'constant', 'factor':0.38268657}
globalXSBRMap['Run3STXS0']['WMINUSH2HLNU__preEE'] = {'mode':'constant', 'factor':0.18495666}
globalXSBRMap['Run3STXS0']['WMINUSH2HLNU_FWDH_preEE'] = {'mode':'constant', 'factor':0.18495666}
globalXSBRMap['Run3STXS0']['WPLUSH2HQQ__preEE'] = {'mode':'constant', 'factor':0.5992074900000001}
globalXSBRMap['Run3STXS0']['WPLUSH2HQQ__FWDH_preEE'] = {'mode':'constant', 'factor':0.5992074900000001}
globalXSBRMap['Run3STXS0']['WPLUSH2HLNU__preEE'] = {'mode':'constant', 'factor':0.28960362}
globalXSBRMap['Run3STXS0']['WPLUSH2HLNU_FWDH_preEE'] = {'mode':'constant', 'factor':0.28960362}
globalXSBRMap['Run3STXS0']['ZH2HQQ__preEE'] = {'mode':'constant', 'factor':0.6598804899999999}
globalXSBRMap['Run3STXS0']['ZH2HQQ_FWDH_preEE'] = {'mode':'constant', 'factor':0.6598804899999999}
globalXSBRMap['Run3STXS0']['ZH2HLL__preEE'] = {'mode':'constant', 'factor': 0.0953093586}
globalXSBRMap['Run3STXS0']['ZH2HLL_FWDH_preEE'] = {'mode':'constant', 'factor': 0.0953093586}
globalXSBRMap['Run3STXS0']['ZH2HNUNU__preEE'] = {'mode':'constant', 'factor':0.1887}
globalXSBRMap['Run3STXS0']['ZH2HNUNU_FWDH_preEE'] = {'mode':'constant', 'factor':0.1887}
globalXSBRMap['Run3STXS0']['VBF__preEE'] = {'mode':'constant', 'factor':4.078}
globalXSBRMap['Run3STXS0']['VBF_FWDH_preEE'] = {'mode':'constant', 'factor':4.078}
globalXSBRMap['Run3STXS0']['BBH__preEE'] = {'mode':'constant', 'factor':0.5266}
globalXSBRMap['Run3STXS0']['BBH_FWDH_preEE'] = {'mode':'constant', 'factor':0.5266}
globalXSBRMap['Run3STXS0']['GG2HLL__preEE'] = {'mode':'constant', 'factor':0.006838}
globalXSBRMap['Run3STXS0']['GG2HLL_FWDH_preEE'] = {'mode':'constant', 'factor':0.006838}
globalXSBRMap['Run3STXS0']['GG2HNUNU__preEE'] = {'mode':'constant', 'factor':0.01351}
globalXSBRMap['Run3STXS0']['GG2HNUNU_FWDH_preEE'] = {'mode':'constant', 'factor':0.01351}
globalXSBRMap['Run3STXS0']['GG2HQQ__preEE'] = {'mode':'constant', 'factor':0.04776}
globalXSBRMap['Run3STXS0']['GG2HQQ_FWDH_preEE'] = {'mode':'constant', 'factor':0.04776}

# Cross sections for each sample according to R5
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
    
globalXSBRMap['HIG-25-020'] = od()
globalXSBRMap['HIG-25-020']['decay'] = {'mode':'hgg'}
globalXSBRMap['HIG-25-020']['GG2H_FWDH'] = {'mode':'constant', 'factor':0.08793496933945123*XS['GG2H']}
globalXSBRMap['HIG-25-020']['GG2H_PTH_200_300'] = {'mode':'constant', 'factor':0.008918359449216368*XS['GG2H']}
globalXSBRMap['HIG-25-020']['GG2H_PTH_300_450'] = {'mode':'constant', 'factor':0.001970527005648357*XS['GG2H']}
globalXSBRMap['HIG-25-020']['GG2H_PTH_450_650'] = {'mode':'constant', 'factor':0.0003327904738421465*XS['GG2H']}
globalXSBRMap['HIG-25-020']['GG2H_PTH_GT650'] = {'mode':'constant', 'factor':3.5413164602218026e-05*XS['GG2H']}
globalXSBRMap['HIG-25-020']['GG2H_0J_PTH_0_10'] = {'mode':'constant', 'factor':0.13466555841051817*XS['GG2H']}
globalXSBRMap['HIG-25-020']['GG2H_0J_PTH_GT10'] = {'mode':'constant', 'factor':0.42304807238946235*XS['GG2H']}
globalXSBRMap['HIG-25-020']['GG2H_1J_PTH_0_60'] = {'mode':'constant', 'factor':0.13871071097321266*XS['GG2H']}
globalXSBRMap['HIG-25-020']['GG2H_1J_PTH_60_120'] = {'mode':'constant', 'factor':0.08858391814636841*XS['GG2H']}
globalXSBRMap['HIG-25-020']['GG2H_1J_PTH_120_200'] = {'mode':'constant', 'factor':0.013898767576163495*XS['GG2H']}
globalXSBRMap['HIG-25-020']['GG2H_GE2J_MJJ_0_350_PTH_0_60'] = {'mode':'constant', 'factor':0.026039602220027526*XS['GG2H']}
globalXSBRMap['HIG-25-020']['GG2H_GE2J_MJJ_0_350_PTH_60_120'] = {'mode':'constant', 'factor':0.03822365023475605*XS['GG2H']}
globalXSBRMap['HIG-25-020']['GG2H_GE2J_MJJ_0_350_PTH_120_200'] = {'mode':'constant', 'factor':0.01883668339397882*XS['GG2H']}
globalXSBRMap['HIG-25-020']['GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.005312410059983659*XS['GG2H']}
globalXSBRMap['HIG-25-020']['GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.007746630993776355*XS['GG2H']}
globalXSBRMap['HIG-25-020']['GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.0022491008044499385*XS['GG2H']}
globalXSBRMap['HIG-25-020']['GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.0034928353645423483*XS['GG2H']}
globalXSBRMap['HIG-25-020']['GG2HQQ_FWDH'] = {'mode':'constant', 'factor':0.030266969104046363*XS['GG2HQQ']}
globalXSBRMap['HIG-25-020']['GG2HQQ_PTH_200_300'] = {'mode':'constant', 'factor':0.1356629925572498*XS['GG2HQQ']}
globalXSBRMap['HIG-25-020']['GG2HQQ_PTH_300_450'] = {'mode':'constant', 'factor':0.03183415497139933*XS['GG2HQQ']}
globalXSBRMap['HIG-25-020']['GG2HQQ_PTH_450_650'] = {'mode':'constant', 'factor':0.003804065743144229*XS['GG2HQQ']}
globalXSBRMap['HIG-25-020']['GG2HQQ_PTH_GT650'] = {'mode':'constant', 'factor':0.00038588362834785953*XS['GG2HQQ']}
globalXSBRMap['HIG-25-020']['GG2HQQ_0J_PTH_0_10'] = {'mode':'constant', 'factor':0.00011327551704337512*XS['GG2HQQ']}
globalXSBRMap['HIG-25-020']['GG2HQQ_0J_PTH_GT10'] = {'mode':'constant', 'factor':0.003130636557521332*XS['GG2HQQ']}
globalXSBRMap['HIG-25-020']['GG2HQQ_1J_PTH_0_60'] = {'mode':'constant', 'factor':0.021923169229449157*XS['GG2HQQ']}
globalXSBRMap['HIG-25-020']['GG2HQQ_1J_PTH_60_120'] = {'mode':'constant', 'factor':0.055785080915722*XS['GG2HQQ']}
globalXSBRMap['HIG-25-020']['GG2HQQ_1J_PTH_120_200'] = {'mode':'constant', 'factor':0.037301254369369596*XS['GG2HQQ']}
globalXSBRMap['HIG-25-020']['GG2HQQ_GE2J_MJJ_0_350_PTH_0_60'] = {'mode':'constant', 'factor':0.058807420409129764*XS['GG2HQQ']}
globalXSBRMap['HIG-25-020']['GG2HQQ_GE2J_MJJ_0_350_PTH_60_120'] = {'mode':'constant', 'factor':0.20039683662539395*XS['GG2HQQ']}
globalXSBRMap['HIG-25-020']['GG2HQQ_GE2J_MJJ_0_350_PTH_120_200'] = {'mode':'constant', 'factor':0.3019576741092278*XS['GG2HQQ']}
globalXSBRMap['HIG-25-020']['GG2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.011444561597170284*XS['GG2HQQ']}
globalXSBRMap['HIG-25-020']['GG2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.07949078319484122*XS['GG2HQQ']}
globalXSBRMap['HIG-25-020']['GG2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.0033422501698133727*XS['GG2HQQ']}
globalXSBRMap['HIG-25-020']['GG2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.024352991301130514*XS['GG2HQQ']}
globalXSBRMap['HIG-25-020']['VBF_FWDH'] = {'mode':'constant', 'factor':0.0722533130749873*XS['VBF']}
globalXSBRMap['HIG-25-020']['VBF_0J'] = {'mode':'constant', 'factor':0.07033905175440057*XS['VBF']}
globalXSBRMap['HIG-25-020']['VBF_1J'] = {'mode':'constant', 'factor':0.33303695754616064*XS['VBF']}
globalXSBRMap['HIG-25-020']['VBF_GE2J_MJJ_0_60'] = {'mode':'constant', 'factor':0.012667952175159083*XS['VBF']}
globalXSBRMap['HIG-25-020']['VBF_GE2J_MJJ_60_120'] = {'mode':'constant', 'factor':0.021875480210705442*XS['VBF']}
globalXSBRMap['HIG-25-020']['VBF_GE2J_MJJ_120_350'] = {'mode':'constant', 'factor':0.11104806117364377*XS['VBF']}
globalXSBRMap['HIG-25-020']['VBF_GE2J_MJJ_GT350_PTH_GT200'] = {'mode':'constant', 'factor':0.039941147587534885*XS['VBF']}
globalXSBRMap['HIG-25-020']['VBF_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.10590618187595*XS['VBF']}
globalXSBRMap['HIG-25-020']['VBF_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.030256852966192693*XS['VBF']}
globalXSBRMap['HIG-25-020']['VBF_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.16691032758976868*XS['VBF']}
globalXSBRMap['HIG-25-020']['VBF_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.035764674045496984*XS['VBF']}
globalXSBRMap['HIG-25-020']['WPLUSH2HQQ_FWDH'] = {'mode':'constant', 'factor':0.1556872883263824*XS['WPLUSH2HQQ']}
globalXSBRMap['HIG-25-020']['WPLUSH2HQQ_0J'] = {'mode':'constant', 'factor':0.05282352199041132*XS['WPLUSH2HQQ']}
globalXSBRMap['HIG-25-020']['WPLUSH2HQQ_1J'] = {'mode':'constant', 'factor':0.2997442561605921*XS['WPLUSH2HQQ']}
globalXSBRMap['HIG-25-020']['WPLUSH2HQQ_GE2J_MJJ_0_60'] = {'mode':'constant', 'factor':0.030702887545768307*XS['WPLUSH2HQQ']}
globalXSBRMap['HIG-25-020']['WPLUSH2HQQ_GE2J_MJJ_60_120'] = {'mode':'constant', 'factor':0.29248133356882217*XS['WPLUSH2HQQ']}
globalXSBRMap['HIG-25-020']['WPLUSH2HQQ_GE2J_MJJ_120_350'] = {'mode':'constant', 'factor':0.12949589254069419*XS['WPLUSH2HQQ']}
globalXSBRMap['HIG-25-020']['WPLUSH2HQQ_GE2J_MJJ_GT350_PTH_GT200'] = {'mode':'constant', 'factor':0.009543195819356077*XS['WPLUSH2HQQ']}
globalXSBRMap['HIG-25-020']['WPLUSH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.003928127041624144*XS['WPLUSH2HQQ']}
globalXSBRMap['HIG-25-020']['WPLUSH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.020003262334377686*XS['WPLUSH2HQQ']}
globalXSBRMap['HIG-25-020']['WPLUSH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.0006824775714926606*XS['WPLUSH2HQQ']}
globalXSBRMap['HIG-25-020']['WPLUSH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.004907757100478961*XS['WPLUSH2HQQ']}
globalXSBRMap['HIG-25-020']['WMINUSH2HQQ_FWDH'] = {'mode':'constant', 'factor':0.09724205269287194*XS['WMINUSH2HQQ']}
globalXSBRMap['HIG-25-020']['WMINUSH2HQQ_0J'] = {'mode':'constant', 'factor':0.05960920478235342*XS['WMINUSH2HQQ']}
globalXSBRMap['HIG-25-020']['WMINUSH2HQQ_1J'] = {'mode':'constant', 'factor':0.3289617488728546*XS['WMINUSH2HQQ']}
globalXSBRMap['HIG-25-020']['WMINUSH2HQQ_GE2J_MJJ_0_60'] = {'mode':'constant', 'factor':0.03287199663390261*XS['WMINUSH2HQQ']}
globalXSBRMap['HIG-25-020']['WMINUSH2HQQ_GE2J_MJJ_60_120'] = {'mode':'constant', 'factor':0.3085342240935115*XS['WMINUSH2HQQ']}
globalXSBRMap['HIG-25-020']['WMINUSH2HQQ_GE2J_MJJ_120_350'] = {'mode':'constant', 'factor':0.1372613243367716*XS['WMINUSH2HQQ']}
globalXSBRMap['HIG-25-020']['WMINUSH2HQQ_GE2J_MJJ_GT350_PTH_GT200'] = {'mode':'constant', 'factor':0.007409614754416615*XS['WMINUSH2HQQ']}
globalXSBRMap['HIG-25-020']['WMINUSH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.003848801477137273*XS['WMINUSH2HQQ']}
globalXSBRMap['HIG-25-020']['WMINUSH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.01924959438595821*XS['WMINUSH2HQQ']}
globalXSBRMap['HIG-25-020']['WMINUSH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.0006214648597517627*XS['WMINUSH2HQQ']}
globalXSBRMap['HIG-25-020']['WMINUSH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.004389973110470433*XS['WMINUSH2HQQ']}
globalXSBRMap['HIG-25-020']['ZH2HQQ_FWDH'] = {'mode':'constant', 'factor':0.12110359986743316*XS['ZH2HQQ']}
globalXSBRMap['HIG-25-020']['ZH2HQQ_0J'] = {'mode':'constant', 'factor':0.04347960812348332*XS['ZH2HQQ']}
globalXSBRMap['HIG-25-020']['ZH2HQQ_1J'] = {'mode':'constant', 'factor':0.2877808073071237*XS['ZH2HQQ']}
globalXSBRMap['HIG-25-020']['ZH2HQQ_GE2J_MJJ_0_60'] = {'mode':'constant', 'factor':0.027289169821139016*XS['ZH2HQQ']}
globalXSBRMap['HIG-25-020']['ZH2HQQ_GE2J_MJJ_60_120'] = {'mode':'constant', 'factor':0.3406705213736634*XS['ZH2HQQ']}
globalXSBRMap['HIG-25-020']['ZH2HQQ_GE2J_MJJ_120_350'] = {'mode':'constant', 'factor':0.14065063717776524*XS['ZH2HQQ']}
globalXSBRMap['HIG-25-020']['ZH2HQQ_GE2J_MJJ_GT350_PTH_GT200'] = {'mode':'constant', 'factor':0.007906087487565565*XS['ZH2HQQ']}
globalXSBRMap['HIG-25-020']['ZH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.0038846206725853915*XS['ZH2HQQ']}
globalXSBRMap['HIG-25-020']['ZH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.021174991521277785*XS['ZH2HQQ']}
globalXSBRMap['HIG-25-020']['ZH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.0006170982720889831*XS['ZH2HQQ']}
globalXSBRMap['HIG-25-020']['ZH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.0054428583758744774*XS['ZH2HQQ']}
globalXSBRMap['HIG-25-020']['WPLUSH2HLNU_FWDH'] = {'mode':'constant', 'factor':0.15271176113315452*XS['WPLUSH2HLNU']}
globalXSBRMap['HIG-25-020']['WPLUSH2HLNU_PTV_0_75'] = {'mode':'constant', 'factor':0.43356786699791927*XS['WPLUSH2HLNU']}
globalXSBRMap['HIG-25-020']['WPLUSH2HLNU_PTV_75_150'] = {'mode':'constant', 'factor':0.28767526534583987*XS['WPLUSH2HLNU']}
globalXSBRMap['HIG-25-020']['WPLUSH2HLNU_PTV_150_250_0J'] = {'mode':'constant', 'factor':0.05318084961358207*XS['WPLUSH2HLNU']}
globalXSBRMap['HIG-25-020']['WPLUSH2HLNU_PTV_150_250_GE1J'] = {'mode':'constant', 'factor':0.0411416402570863*XS['WPLUSH2HLNU']}
globalXSBRMap['HIG-25-020']['WPLUSH2HLNU_PTV_GT250'] = {'mode':'constant', 'factor':0.031722616652417955*XS['WPLUSH2HLNU']}
globalXSBRMap['HIG-25-020']['WMINUSH2HLNU_FWDH'] = {'mode':'constant', 'factor':0.09648710686467347*XS['WMINUSH2HLNU']}
globalXSBRMap['HIG-25-020']['WMINUSH2HLNU_PTV_0_75'] = {'mode':'constant', 'factor':0.4867718359456386*XS['WMINUSH2HLNU']}
globalXSBRMap['HIG-25-020']['WMINUSH2HLNU_PTV_75_150'] = {'mode':'constant', 'factor':0.3013837813167588*XS['WMINUSH2HLNU']}
globalXSBRMap['HIG-25-020']['WMINUSH2HLNU_PTV_150_250_0J'] = {'mode':'constant', 'factor':0.05041842737069779*XS['WMINUSH2HLNU']}
globalXSBRMap['HIG-25-020']['WMINUSH2HLNU_PTV_150_250_GE1J'] = {'mode':'constant', 'factor':0.03911373986842681*XS['WMINUSH2HLNU']}
globalXSBRMap['HIG-25-020']['WMINUSH2HLNU_PTV_GT250'] = {'mode':'constant', 'factor':0.025825108633804533*XS['WMINUSH2HLNU']}
globalXSBRMap['HIG-25-020']['ZH2HLL_FWDH'] = {'mode':'constant', 'factor':0.11820190886407907*XS['ZH2HLL']}
globalXSBRMap['HIG-25-020']['ZH2HLL_PTV_0_75'] = {'mode':'constant', 'factor':0.4552694647142518*XS['ZH2HLL']}
globalXSBRMap['HIG-25-020']['ZH2HLL_PTV_75_150'] = {'mode':'constant', 'factor':0.3016284728356651*XS['ZH2HLL']}
globalXSBRMap['HIG-25-020']['ZH2HLL_PTV_150_250_0J'] = {'mode':'constant', 'factor':0.05298967595175157*XS['ZH2HLL']}
globalXSBRMap['HIG-25-020']['ZH2HLL_PTV_150_250_GE1J'] = {'mode':'constant', 'factor':0.042352236601418666*XS['ZH2HLL']}
globalXSBRMap['HIG-25-020']['ZH2HLL_PTV_GT250'] = {'mode':'constant', 'factor':0.029558241032833794*XS['ZH2HLL']}
globalXSBRMap['HIG-25-020']['ZH2HNUNU_FWDH'] = {'mode':'constant', 'factor':0.11881261579156738*XS['ZH2HNUNU']}
globalXSBRMap['HIG-25-020']['ZH2HNUNU_PTV_0_75'] = {'mode':'constant', 'factor':0.45321104356596154*XS['ZH2HNUNU']}
globalXSBRMap['HIG-25-020']['ZH2HNUNU_PTV_75_150'] = {'mode':'constant', 'factor':0.3023083899029264*XS['ZH2HNUNU']}
globalXSBRMap['HIG-25-020']['ZH2HNUNU_PTV_150_250_0J'] = {'mode':'constant', 'factor':0.05313440620363219*XS['ZH2HNUNU']}
globalXSBRMap['HIG-25-020']['ZH2HNUNU_PTV_150_250_GE1J'] = {'mode':'constant', 'factor':0.043077607875712146*XS['ZH2HNUNU']}
globalXSBRMap['HIG-25-020']['ZH2HNUNU_PTV_GT250'] = {'mode':'constant', 'factor':0.029455936660200358*XS['ZH2HNUNU']}
globalXSBRMap['HIG-25-020']['GG2HLL_FWDH'] = {'mode':'constant', 'factor':0.03053787319098257*XS['GG2HLL']}
globalXSBRMap['HIG-25-020']['GG2HLL_PTV_0_75'] = {'mode':'constant', 'factor':0.15979988436332604*XS['GG2HLL']}
globalXSBRMap['HIG-25-020']['GG2HLL_PTV_75_150'] = {'mode':'constant', 'factor':0.4421118298201533*XS['GG2HLL']}
globalXSBRMap['HIG-25-020']['GG2HLL_PTV_150_250_0J'] = {'mode':'constant', 'factor':0.09450408368635212*XS['GG2HLL']}
globalXSBRMap['HIG-25-020']['GG2HLL_PTV_150_250_GE1J'] = {'mode':'constant', 'factor':0.2014868649920957*XS['GG2HLL']}
globalXSBRMap['HIG-25-020']['GG2HLL_PTV_GT250'] = {'mode':'constant', 'factor':0.07155946394709028*XS['GG2HLL']}
globalXSBRMap['HIG-25-020']['GG2HNUNU_FWDH'] = {'mode':'constant', 'factor':0.0305770161094599*XS['GG2HNUNU']}
globalXSBRMap['HIG-25-020']['GG2HNUNU_PTV_0_75'] = {'mode':'constant', 'factor':0.159868213791565*XS['GG2HNUNU']}
globalXSBRMap['HIG-25-020']['GG2HNUNU_PTV_75_150'] = {'mode':'constant', 'factor':0.44155926164673476*XS['GG2HNUNU']}
globalXSBRMap['HIG-25-020']['GG2HNUNU_PTV_150_250_0J'] = {'mode':'constant', 'factor':0.09352962681858218*XS['GG2HNUNU']}
globalXSBRMap['HIG-25-020']['GG2HNUNU_PTV_150_250_GE1J'] = {'mode':'constant', 'factor':0.203018666016631*XS['GG2HNUNU']}
globalXSBRMap['HIG-25-020']['GG2HNUNU_PTV_GT250'] = {'mode':'constant', 'factor':0.07144721561702723*XS['GG2HNUNU']}
globalXSBRMap['HIG-25-020']['TTH_FWDH'] = {'mode':'constant', 'factor':0.015241625072948543*XS['TTH']}
globalXSBRMap['HIG-25-020']['TTH_PTH_0_60'] = {'mode':'constant', 'factor':0.2326723321900437*XS['TTH']}
globalXSBRMap['HIG-25-020']['TTH_PTH_60_120'] = {'mode':'constant', 'factor':0.35130838206469855*XS['TTH']}
globalXSBRMap['HIG-25-020']['TTH_PTH_120_200'] = {'mode':'constant', 'factor':0.2488938139863567*XS['TTH']}
globalXSBRMap['HIG-25-020']['TTH_PTH_200_300'] = {'mode':'constant', 'factor':0.10345447542821952*XS['TTH']}
globalXSBRMap['HIG-25-020']['TTH_PTH_GT300'] = {'mode':'constant', 'factor':0.04842937125773297*XS['TTH']}
globalXSBRMap['HIG-25-020']['THQ_FWDH'] = {'mode':'constant', 'factor':0.10110201592800672*XS['THQ']}
globalXSBRMap['HIG-25-020']['THQ_FID'] = {'mode':'constant', 'factor':0.8988979840719933*XS['THQ']}
globalXSBRMap['HIG-25-020']['THQ2HQQ_FWDH'] = {'mode':'constant', 'factor':0.10143059712692852*XS['THQ2HQQ']}
globalXSBRMap['HIG-25-020']['THQ2HQQ_FID'] = {'mode':'constant', 'factor':0.8985694028730715*XS['THQ2HQQ']}
globalXSBRMap['HIG-25-020']['THQ2HLNU_FWDH'] = {'mode':'constant', 'factor':0.1004221614584142*XS['THQ2HLNU']}
globalXSBRMap['HIG-25-020']['THQ2HLNU_FID'] = {'mode':'constant', 'factor':0.8995778385415858*XS['THQ2HLNU']}
globalXSBRMap['HIG-25-020']['THW_FWDH'] = {'mode':'constant', 'factor':0.0082992390744502*XS['THW']}
globalXSBRMap['HIG-25-020']['THW_FID'] = {'mode':'constant', 'factor':0.9917007609255498*XS['THW']}
globalXSBRMap['HIG-25-020']['BBH_FWDH'] = {'mode':'constant', 'factor':0.05504122860678072*XS['BBH']}
globalXSBRMap['HIG-25-020']['BBH_FID'] = {'mode':'constant', 'factor':0.9449587713932193*XS['BBH']}

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
