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

xsbr = {}
xsbr['decay'] = {'mode':'constant', 'factor':0.00227}
xsbr['GG2H_FWDH'] = {'mode':'constant', 'factor':0.085247062*XS['GG2H']}
xsbr['GG2H_PTH_200_300'] = {'mode':'constant', 'factor':0.014211155*XS['GG2H']}
xsbr['GG2H_PTH_300_450'] = {'mode':'constant', 'factor':0.004919169*XS['GG2H']}
xsbr['GG2H_PTH_450_650'] = {'mode':'constant', 'factor':0.00125562*XS['GG2H']}
xsbr['GG2H_PTH_GT650'] = {'mode':'constant', 'factor':0.000333772*XS['GG2H']}
xsbr['GG2H_0J_PTH_0_10'] = {'mode':'constant', 'factor':0.137979127*XS['GG2H']}
xsbr['GG2H_0J_PTH_GT10'] = {'mode':'constant', 'factor':0.387390556*XS['GG2H']}
xsbr['GG2H_1J_PTH_0_60'] = {'mode':'constant', 'factor':0.139387726*XS['GG2H']}
xsbr['GG2H_1J_PTH_60_120'] = {'mode':'constant', 'factor':0.100483374*XS['GG2H']}
xsbr['GG2H_1J_PTH_120_200'] = {'mode':'constant', 'factor':0.020922364*XS['GG2H']}
xsbr['GG2H_GE2J_MJJ_0_350_PTH_0_60'] = {'mode':'constant', 'factor':0.026286564*XS['GG2H']}
xsbr['GG2H_GE2J_MJJ_0_350_PTH_60_120'] = {'mode':'constant', 'factor':0.038614288*XS['GG2H']}
xsbr['GG2H_GE2J_MJJ_0_350_PTH_120_200'] = {'mode':'constant', 'factor':0.022114408*XS['GG2H']}
xsbr['GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.006429092*XS['GG2H']}
xsbr['GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.008050272*XS['GG2H']}
xsbr['GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.002930442*XS['GG2H']}
xsbr['GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.003445008*XS['GG2H']}
xsbr['GG2HQQ_FWDH'] = {'mode':'constant', 'factor':0.030261461*XS['GG2HQQ']}
xsbr['GG2HQQ_PTH_200_300'] = {'mode':'constant', 'factor':0.137302676*XS['GG2HQQ']}
xsbr['GG2HQQ_PTH_300_450'] = {'mode':'constant', 'factor':0.032923158*XS['GG2HQQ']}
xsbr['GG2HQQ_PTH_450_650'] = {'mode':'constant', 'factor':0.003664954*XS['GG2HQQ']}
xsbr['GG2HQQ_PTH_GT650'] = {'mode':'constant', 'factor':0.000204746*XS['GG2HQQ']}
xsbr['GG2HQQ_0J_PTH_0_10'] = {'mode':'constant', 'factor':8.19E-05*XS['GG2HQQ']}
xsbr['GG2HQQ_0J_PTH_GT10'] = {'mode':'constant', 'factor':0.00284597*XS['GG2HQQ']}
xsbr['GG2HQQ_1J_PTH_0_60'] = {'mode':'constant', 'factor':0.02029033*XS['GG2HQQ']}
xsbr['GG2HQQ_1J_PTH_60_120'] = {'mode':'constant', 'factor':0.054237218*XS['GG2HQQ']}
xsbr['GG2HQQ_1J_PTH_120_200'] = {'mode':'constant', 'factor':0.037059029*XS['GG2HQQ']}
xsbr['GG2HQQ_GE2J_MJJ_0_350_PTH_0_60'] = {'mode':'constant', 'factor':0.058741632*XS['GG2HQQ']}
xsbr['GG2HQQ_GE2J_MJJ_0_350_PTH_60_120'] = {'mode':'constant', 'factor':0.201408651*XS['GG2HQQ']}
xsbr['GG2HQQ_GE2J_MJJ_0_350_PTH_120_200'] = {'mode':'constant', 'factor':0.300423825*XS['GG2HQQ']}
xsbr['GG2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.011977642*XS['GG2HQQ']}
xsbr['GG2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.081038472*XS['GG2HQQ']}
xsbr['GG2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.003746852*XS['GG2HQQ']}
xsbr['GG2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.023791487*XS['GG2HQQ']}
xsbr['VBF_FWDH'] = {'mode':'constant', 'factor':0.07578759*XS['VBF']}
xsbr['VBF_0J'] = {'mode':'constant', 'factor':0.063805995*XS['VBF']}
xsbr['VBF_1J'] = {'mode':'constant', 'factor':0.327773873*XS['VBF']}
xsbr['VBF_GE2J_MJJ_0_60'] = {'mode':'constant', 'factor':0.010842014*XS['VBF']}
xsbr['VBF_GE2J_MJJ_60_120'] = {'mode':'constant', 'factor':0.018020321*XS['VBF']}
xsbr['VBF_GE2J_MJJ_120_350'] = {'mode':'constant', 'factor':0.10769591*XS['VBF']}
xsbr['VBF_GE2J_MJJ_GT350_PTH_GT200'] = {'mode':'constant', 'factor':0.043059194*XS['VBF']}
xsbr['VBF_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.119847912*XS['VBF']}
xsbr['VBF_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.022781008*XS['VBF']}
xsbr['VBF_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.165559037*XS['VBF']}
xsbr['VBF_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.044827147*XS['VBF']}
xsbr['WPLUSH2HQQ_FWDH'] = {'mode':'constant', 'factor':0.151298618*XS['WPLUSH2HQQ']}
xsbr['WPLUSH2HQQ_0J'] = {'mode':'constant', 'factor':0.051089435*XS['WPLUSH2HQQ']}
xsbr['WPLUSH2HQQ_1J'] = {'mode':'constant', 'factor':0.297227506*XS['WPLUSH2HQQ']}
xsbr['WPLUSH2HQQ_GE2J_MJJ_0_60'] = {'mode':'constant', 'factor':0.030924616*XS['WPLUSH2HQQ']}
xsbr['WPLUSH2HQQ_GE2J_MJJ_60_120'] = {'mode':'constant', 'factor':0.299082082*XS['WPLUSH2HQQ']}
xsbr['WPLUSH2HQQ_GE2J_MJJ_120_350'] = {'mode':'constant', 'factor':0.132109777*XS['WPLUSH2HQQ']}
xsbr['WPLUSH2HQQ_GE2J_MJJ_GT350_PTH_GT200'] = {'mode':'constant', 'factor':0.00904939*XS['WPLUSH2HQQ']}
xsbr['WPLUSH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.003725287*XS['WPLUSH2HQQ']}
xsbr['WPLUSH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.020130107*XS['WPLUSH2HQQ']}
xsbr['WPLUSH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.000736183*XS['WPLUSH2HQQ']}
xsbr['WPLUSH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.004626999*XS['WPLUSH2HQQ']}
xsbr['WMINUSH2HQQ_FWDH'] = {'mode':'constant', 'factor':0.093117961*XS['WMINUSH2HQQ']}
xsbr['WMINUSH2HQQ_0J'] = {'mode':'constant', 'factor':0.060332122*XS['WMINUSH2HQQ']}
xsbr['WMINUSH2HQQ_1J'] = {'mode':'constant', 'factor':0.324521276*XS['WMINUSH2HQQ']}
xsbr['WMINUSH2HQQ_GE2J_MJJ_0_60'] = {'mode':'constant', 'factor':0.032542084*XS['WMINUSH2HQQ']}
xsbr['WMINUSH2HQQ_GE2J_MJJ_60_120'] = {'mode':'constant', 'factor':0.309785184*XS['WMINUSH2HQQ']}
xsbr['WMINUSH2HQQ_GE2J_MJJ_120_350'] = {'mode':'constant', 'factor':0.142326551*XS['WMINUSH2HQQ']}
xsbr['WMINUSH2HQQ_GE2J_MJJ_GT350_PTH_GT200'] = {'mode':'constant', 'factor':0.007524292*XS['WMINUSH2HQQ']}
xsbr['WMINUSH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.00414117*XS['WMINUSH2HQQ']}
xsbr['WMINUSH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.020211033*XS['WMINUSH2HQQ']}
xsbr['WMINUSH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.000555765*XS['WMINUSH2HQQ']}
xsbr['WMINUSH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.004942561*XS['WMINUSH2HQQ']}
xsbr['ZH2HQQ_FWDH'] = {'mode':'constant', 'factor':0.119478697*XS['ZH2HQQ']}
xsbr['ZH2HQQ_0J'] = {'mode':'constant', 'factor':0.042546366*XS['ZH2HQQ']}
xsbr['ZH2HQQ_1J'] = {'mode':'constant', 'factor':0.285894738*XS['ZH2HQQ']}
xsbr['ZH2HQQ_GE2J_MJJ_0_60'] = {'mode':'constant', 'factor':0.027368421*XS['ZH2HQQ']}
xsbr['ZH2HQQ_GE2J_MJJ_60_120'] = {'mode':'constant', 'factor':0.343598999*XS['ZH2HQQ']}
xsbr['ZH2HQQ_GE2J_MJJ_120_350'] = {'mode':'constant', 'factor':0.141453632*XS['ZH2HQQ']}
xsbr['ZH2HQQ_GE2J_MJJ_GT350_PTH_GT200'] = {'mode':'constant', 'factor':0.008360902*XS['ZH2HQQ']}
xsbr['ZH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.003809524*XS['ZH2HQQ']}
xsbr['ZH2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.021634085*XS['ZH2HQQ']}
xsbr['ZH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25'] = {'mode':'constant', 'factor':0.000421053*XS['ZH2HQQ']}
xsbr['ZH2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25'] = {'mode':'constant', 'factor':0.005433584*XS['ZH2HQQ']}
xsbr['WPLUSH2HLNU_FWDH'] = {'mode':'constant', 'factor':0.155188512*XS['WPLUSH2HLNU']}
xsbr['WPLUSH2HLNU_PTV_0_75'] = {'mode':'constant', 'factor':0.431671519*XS['WPLUSH2HLNU']}
xsbr['WPLUSH2HLNU_PTV_75_150'] = {'mode':'constant', 'factor':0.287799901*XS['WPLUSH2HLNU']}
xsbr['WPLUSH2HLNU_PTV_150_250_0J'] = {'mode':'constant', 'factor':0.051270718*XS['WPLUSH2HLNU']}
xsbr['WPLUSH2HLNU_PTV_150_250_GE1J'] = {'mode':'constant', 'factor':0.041543315*XS['WPLUSH2HLNU']}
xsbr['WPLUSH2HLNU_PTV_GT250'] = {'mode':'constant', 'factor':0.032526034*XS['WPLUSH2HLNU']}
xsbr['WMINUSH2HLNU_FWDH'] = {'mode':'constant', 'factor':0.097063882*XS['WMINUSH2HLNU']}
xsbr['WMINUSH2HLNU_PTV_0_75'] = {'mode':'constant', 'factor':0.490122821*XS['WMINUSH2HLNU']}
xsbr['WMINUSH2HLNU_PTV_75_150'] = {'mode':'constant', 'factor':0.296397523*XS['WMINUSH2HLNU']}
xsbr['WMINUSH2HLNU_PTV_150_250_0J'] = {'mode':'constant', 'factor':0.050060723*XS['WMINUSH2HLNU']}
xsbr['WMINUSH2HLNU_PTV_150_250_GE1J'] = {'mode':'constant', 'factor':0.040180898*XS['WMINUSH2HLNU']}
xsbr['WMINUSH2HLNU_PTV_GT250'] = {'mode':'constant', 'factor':0.026174153*XS['WMINUSH2HLNU']}
xsbr['ZH2HLL_FWDH'] = {'mode':'constant', 'factor':0.119436748*XS['ZH2HLL']}
xsbr['ZH2HLL_PTV_0_75'] = {'mode':'constant', 'factor':0.453446194*XS['ZH2HLL']}
xsbr['ZH2HLL_PTV_75_150'] = {'mode':'constant', 'factor':0.302843549*XS['ZH2HLL']}
xsbr['ZH2HLL_PTV_150_250_0J'] = {'mode':'constant', 'factor':0.052833795*XS['ZH2HLL']}
xsbr['ZH2HLL_PTV_150_250_GE1J'] = {'mode':'constant', 'factor':0.041795061*XS['ZH2HLL']}
xsbr['ZH2HLL_PTV_GT250'] = {'mode':'constant', 'factor':0.029644654*XS['ZH2HLL']}
xsbr['ZH2HNUNU_FWDH'] = {'mode':'constant', 'factor':0.118822109*XS['ZH2HNUNU']}
xsbr['ZH2HNUNU_PTV_0_75'] = {'mode':'constant', 'factor':0.457358902*XS['ZH2HNUNU']}
xsbr['ZH2HNUNU_PTV_75_150'] = {'mode':'constant', 'factor':0.302931086*XS['ZH2HNUNU']}
xsbr['ZH2HNUNU_PTV_150_250_0J'] = {'mode':'constant', 'factor':0.050339103*XS['ZH2HNUNU']}
xsbr['ZH2HNUNU_PTV_150_250_GE1J'] = {'mode':'constant', 'factor':0.043829904*XS['ZH2HNUNU']}
xsbr['ZH2HNUNU_PTV_GT250'] = {'mode':'constant', 'factor':0.026718897*XS['ZH2HNUNU']}
xsbr['ZH2HLEPLEP_FWDH'] = {'mode':'constant', 'factor':0.119028372*XS['ZH2HLEPLEP']}
xsbr['ZH2HLEPLEP_PTV_0_75'] = {'mode':'constant', 'factor':0.456045854*XS['ZH2HLEPLEP']}
xsbr['ZH2HLEPLEP_PTV_75_150'] = {'mode':'constant', 'factor':0.30290171*XS['ZH2HLEPLEP']}
xsbr['ZH2HLEPLEP_PTV_150_250_0J'] = {'mode':'constant', 'factor':0.051176285*XS['ZH2HLEPLEP']}
xsbr['ZH2HLEPLEP_PTV_150_250_GE1J'] = {'mode':'constant', 'factor':0.043147041*XS['ZH2HLEPLEP']}
xsbr['ZH2HLEPLEP_PTV_GT250'] = {'mode':'constant', 'factor':0.027700738*XS['ZH2HLEPLEP']}
xsbr['GG2HLL_FWDH'] = {'mode':'constant', 'factor':0.030792199*XS['GG2HLL']}
xsbr['GG2HLL_PTV_0_75'] = {'mode':'constant', 'factor':0.159522254*XS['GG2HLL']}
xsbr['GG2HLL_PTV_75_150'] = {'mode':'constant', 'factor':0.439749923*XS['GG2HLL']}
xsbr['GG2HLL_PTV_150_250_0J'] = {'mode':'constant', 'factor':0.09267519*XS['GG2HLL']}
xsbr['GG2HLL_PTV_150_250_GE1J'] = {'mode':'constant', 'factor':0.205076054*XS['GG2HLL']}
xsbr['GG2HLL_PTV_GT250'] = {'mode':'constant', 'factor':0.07218438*XS['GG2HLL']}
xsbr['GG2HNUNU_FWDH'] = {'mode':'constant', 'factor':0.030397738*XS['GG2HNUNU']}
xsbr['GG2HNUNU_PTV_0_75'] = {'mode':'constant', 'factor':0.161197308*XS['GG2HNUNU']}
xsbr['GG2HNUNU_PTV_75_150'] = {'mode':'constant', 'factor':0.440060273*XS['GG2HNUNU']}
xsbr['GG2HNUNU_PTV_150_250_0J'] = {'mode':'constant', 'factor':0.094392975*XS['GG2HNUNU']}
xsbr['GG2HNUNU_PTV_150_250_GE1J'] = {'mode':'constant', 'factor':0.202701193*XS['GG2HNUNU']}
xsbr['GG2HNUNU_PTV_GT250'] = {'mode':'constant', 'factor':0.071250512*XS['GG2HNUNU']}
xsbr['TTH_FWDH'] = {'mode':'constant', 'factor':0.014373861*XS['TTH']}
xsbr['TTH_PTH_0_60'] = {'mode':'constant', 'factor':0.232810586*XS['TTH']}
xsbr['TTH_PTH_60_120'] = {'mode':'constant', 'factor':0.342957155*XS['TTH']}
xsbr['TTH_PTH_120_200'] = {'mode':'constant', 'factor':0.254274159*XS['TTH']}
xsbr['TTH_PTH_200_300'] = {'mode':'constant', 'factor':0.105868005*XS['TTH']}
xsbr['TTH_PTH_GT300'] = {'mode':'constant', 'factor':0.049716234*XS['TTH']}
xsbr['THQ_FWDH'] = {'mode':'constant', 'factor':0.110651592*XS['THQ']}
xsbr['THQ_FID'] = {'mode':'constant', 'factor':0.889348408*XS['THQ']}
xsbr['THQ2HQQ_FWDH'] = {'mode':'constant', 'factor':0.110651592*XS['THQ2HQQ']}
xsbr['THQ2HQQ_FID'] = {'mode':'constant', 'factor':0.889348408*XS['THQ2HQQ']}
xsbr['THQ2HLNU_FWDH'] = {'mode':'constant', 'factor':0.110651592*XS['THQ2HLNU']}
xsbr['THQ2HLNU_FID'] = {'mode':'constant', 'factor':0.889348408*XS['THQ2HLNU']}
xsbr['THW_FWDH'] = {'mode':'constant', 'factor':0.008056908*XS['THW']}
xsbr['THW_FID'] = {'mode':'constant', 'factor':0.991943092*XS['THW']}
xsbr['BBH_FWDH'] = {'mode':'constant', 'factor':0.055177792*XS['BBH']}
xsbr['BBH_FID'] = {'mode':'constant', 'factor':0.944822208*XS['BBH']}