from collections import OrderedDict as od

# Flashgg STXS dict
flashggSTXSDict = od()
flashggSTXSDict[0] = "UNKNOWN"
flashggSTXSDict[-1] = "GG2H_FWDH"
flashggSTXSDict[1] = "GG2H_PTH_200_300"
flashggSTXSDict[2] = "GG2H_PTH_300_450"
flashggSTXSDict[3] = "GG2H_PTH_450_650"
flashggSTXSDict[4] = "GG2H_PTH_GT650"
flashggSTXSDict[5] = "GG2H_0J_PTH_0_10"
flashggSTXSDict[6] = "GG2H_0J_PTH_GT10"
flashggSTXSDict[7] = "GG2H_1J_PTH_0_60"
flashggSTXSDict[8] = "GG2H_1J_PTH_60_120"
flashggSTXSDict[9] = "GG2H_1J_PTH_120_200"
flashggSTXSDict[10] = "GG2H_GE2J_MJJ_0_350_PTH_0_60"
flashggSTXSDict[11] = "GG2H_GE2J_MJJ_0_350_PTH_60_120"
flashggSTXSDict[12] = "GG2H_GE2J_MJJ_0_350_PTH_120_200"
flashggSTXSDict[13] = "GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25"
flashggSTXSDict[14] = "GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25"
flashggSTXSDict[15] = "GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25"
flashggSTXSDict[16] = "GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25"
flashggSTXSDict[-2] = "QQ2HQQ_FWDH"
flashggSTXSDict[17] = "QQ2HQQ_0J"
flashggSTXSDict[18] = "QQ2HQQ_1J"
flashggSTXSDict[19] = "QQ2HQQ_GE2J_MJJ_0_60"
flashggSTXSDict[20] = "QQ2HQQ_GE2J_MJJ_60_120"
flashggSTXSDict[21] = "QQ2HQQ_GE2J_MJJ_120_350"
flashggSTXSDict[22] = "QQ2HQQ_GE2J_MJJ_GT350_PTH_GT200"
flashggSTXSDict[23] = "QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25"
flashggSTXSDict[24] = "QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25"
flashggSTXSDict[25] = "QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25"
flashggSTXSDict[26] = "QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25"
flashggSTXSDict[-3] = "QQ2HLNU_FWDH"
flashggSTXSDict[27] = "QQ2HLNU_PTV_0_75"
flashggSTXSDict[28] = "QQ2HLNU_PTV_75_150"
flashggSTXSDict[29] = "QQ2HLNU_PTV_150_250_0J"
flashggSTXSDict[30] = "QQ2HLNU_PTV_150_250_GE1J"
flashggSTXSDict[31] = "QQ2HLNU_PTV_GT250"
flashggSTXSDict[-4] = "QQ2HLL_FWDH"
flashggSTXSDict[32] = "QQ2HLL_PTV_0_75"
flashggSTXSDict[33] = "QQ2HLL_PTV_75_150"
flashggSTXSDict[34] = "QQ2HLL_PTV_150_250_0J"
flashggSTXSDict[35] = "QQ2HLL_PTV_150_250_GE1J"
flashggSTXSDict[36] = "QQ2HLL_PTV_GT250"
flashggSTXSDict[-5] = "GG2HLL_FWDH"
flashggSTXSDict[37] = "GG2HLL_PTV_0_75"
flashggSTXSDict[38] = "GG2HLL_PTV_75_150"
flashggSTXSDict[39] = "GG2HLL_PTV_150_250_0J"
flashggSTXSDict[40] = "GG2HLL_PTV_150_250_GE1J"
flashggSTXSDict[41] = "GG2HLL_PTV_GT250"
flashggSTXSDict[-6] = "TTH_FWDH"
flashggSTXSDict[42] = "TTH_PTH_0_60"
flashggSTXSDict[43] = "TTH_PTH_60_120"
flashggSTXSDict[44] = "TTH_PTH_120_200"
flashggSTXSDict[45] = "TTH_PTH_200_300"
flashggSTXSDict[46] = "TTH_PTH_GT300"
flashggSTXSDict[-7] = "BBH_FWDH"
flashggSTXSDict[47] = "BBH"

# Define STXS bin merging scheme: used for calculating "merge" type theory uncertainties
STXSMergingScheme = od()
# Maximal merging scheme
STXSMergingScheme['max_ggH_BSM'] = ['ggH_PTH_200_300', 'ggH_PTH_300_450','ggH_PTH_GT650', 'ggH_PTH_450_650']
STXSMergingScheme['max_ggH_VBFlike'] = ['ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25']
STXSMergingScheme['max_qqH_VBFlike'] = ['qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25', 'qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25', 'ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25', 'ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25', 'WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25', 'ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25', 'ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25']
STXSMergingScheme['max_WH_lep'] = ['WH_lep_PTV_150_250_GE1J', 'WH_lep_PTV_75_150', 'WH_lep_PTV_0_75', 'WH_lep_PTV_150_250_0J','WH_lep_PTV_GT250']
STXSMergingScheme['max_ZH_lep'] = ['ZH_lep_PTV_150_250_0J', 'ZH_lep_PTV_150_250_GE1J', 'ZH_lep_PTV_0_75', 'ZH_lep_PTV_75_150', 'ggZH_ll_PTV_150_250_0J', 'ggZH_ll_PTV_150_250_GE1J', 'ggZH_ll_PTV_0_75', 'ggZH_ll_PTV_75_150', 'ggZH_nunu_PTV_150_250_0J', 'ggZH_nunu_PTV_150_250_GE1J', 'ggZH_nunu_PTV_0_75', 'ggZH_nunu_PTV_75_150','ZH_lep_PTV_GT250','ggZH_ll_PTV_GT250','ggZH_nunu_PTV_GT250']
STXSMergingScheme['max_ttH'] = ['ttH_PTH_200_300', 'ttH_PTH_60_120', 'ttH_PTH_120_200', 'ttH_PTH_0_60','ttH_PTH_GT300']
# Minimal merging scheme
STXSMergingScheme['min_ggH_BSM_high'] = ['ggH_PTH_300_450','ggH_PTH_GT650', 'ggH_PTH_450_650']
STXSMergingScheme['min_VBFlike_low_mjj_low_pthjj'] = ['ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25']
STXSMergingScheme['min_VBFlike_low_mjj_high_pthjj'] = ['ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25']
STXSMergingScheme['min_VBFlike_high_mjj_low_pthjj'] = ['ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25']
STXSMergingScheme['min_VBFlike_high_mjj_high_pthjj'] = ['ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25','ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25']
STXSMergingScheme['min_WH_lep_high'] = ['WH_lep_PTV_150_250_GE1J', 'WH_lep_PTV_75_150', 'WH_lep_PTV_150_250_0J','WH_lep_PTV_GT250']
STXSMergingScheme['min_ZH_lep'] = ['ZH_lep_PTV_150_250_0J', 'ZH_lep_PTV_150_250_GE1J', 'ZH_lep_PTV_0_75', 'ZH_lep_PTV_75_150', 'ggZH_ll_PTV_150_250_0J', 'ggZH_ll_PTV_150_250_GE1J', 'ggZH_ll_PTV_0_75', 'ggZH_ll_PTV_75_150', 'ggZH_nunu_PTV_150_250_0J', 'ggZH_nunu_PTV_150_250_GE1J', 'ggZH_nunu_PTV_0_75', 'ggZH_nunu_PTV_75_150','ZH_lep_PTV_GT250','ggZH_ll_PTV_GT250','ggZH_nunu_PTV_GT250']
STXSMergingScheme['min_ttH_high'] = ['ttH_PTH_200_300', 'ttH_PTH_GT300']


# Define STXS scale correlation scheme: for correlating acceptance uncertainties
STXSScaleCorrelationScheme = od()
STXSScaleCorrelationScheme['ggH_scale_0jet'] = ['ggH_0J_PTH_0_10','ggH_0J_PTH_GT10','ggZH_had_0J_PTH_0_10','ggZH_had_0J_PTH_GT10']
STXSScaleCorrelationScheme['ggH_scale_1jet_lowpt'] = ['ggH_1J_PTH_60_120', 'ggH_1J_PTH_120_200', 'ggH_1J_PTH_0_60','ggZH_had_1J_PTH_60_120', 'ggZH_had_1J_PTH_120_200', 'ggZH_had_1J_PTH_0_60']
STXSScaleCorrelationScheme['ggH_scale_2jet_lowpt'] = ['ggH_GE2J_MJJ_0_350_PTH_120_200', 'ggH_GE2J_MJJ_0_350_PTH_60_120', 'ggH_GE2J_MJJ_0_350_PTH_0_60','ggZH_had_GE2J_MJJ_0_350_PTH_120_200', 'ggZH_had_GE2J_MJJ_0_350_PTH_60_120', 'ggZH_had_GE2J_MJJ_0_350_PTH_0_60']
STXSScaleCorrelationScheme['ggH_scale_highpt'] = ['ggH_PTH_200_300', 'ggH_PTH_300_450','ggZH_had_PTH_200_300', 'ggZH_had_PTH_300_450']
STXSScaleCorrelationScheme['ggH_scale_veryhighpt'] = ['ggH_PTH_GT650', 'ggH_PTH_450_650','ggZH_had_PTH_GT650', 'ggZH_had_PTH_450_650']
STXSScaleCorrelationScheme['ggH_scale_vbf'] = ['ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25', 'ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25', 'ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25', 'ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25', 'ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25', 'ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25', 'ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25']
STXSScaleCorrelationScheme['vbf_scale_0jet'] = ['qqH_0J']
STXSScaleCorrelationScheme['vbf_scale_1jet'] = ['qqH_1J']
STXSScaleCorrelationScheme['vbf_scale_lowmjj'] = ['qqH_GE2J_MJJ_0_60','qqH_GE2J_MJJ_60_120','qqH_GE2J_MJJ_120_350']
STXSScaleCorrelationScheme['vbf_scale_highmjj_lowpt'] = ['qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25', 'qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25']
STXSScaleCorrelationScheme['vbf_scale_highmjj_highpt'] = ['qqH_GE2J_MJJ_GT350_PTH_GT200']
STXSScaleCorrelationScheme['VH_scale_0jet'] = ['WH_had_0J','ZH_had_0J']
STXSScaleCorrelationScheme['VH_scale_1jet'] = ['WH_had_1J','ZH_had_1J']
STXSScaleCorrelationScheme['VH_scale_lowmjj'] = ['WH_had_GE2J_MJJ_0_60','ZH_had_GE2J_MJJ_0_60','WH_had_GE2J_MJJ_60_120', 'ZH_had_GE2J_MJJ_60_120','ZH_had_GE2J_MJJ_120_350', 'WH_had_GE2J_MJJ_120_350']
STXSScaleCorrelationScheme['VH_scale_highmjj_lowpt'] = ['WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25', 'ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25','WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25', 'ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25', 'WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25','WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25', 'ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25', 'ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25']
STXSScaleCorrelationScheme['VH_scale_highmjj_highpt'] = ['WH_had_GE2J_MJJ_GT350_PTH_GT200', 'ZH_had_GE2J_MJJ_GT350_PTH_GT200']
STXSScaleCorrelationScheme['WH_scale_lowpt'] = ['WH_lep_PTV_150_250_GE1J', 'WH_lep_PTV_75_150', 'WH_lep_PTV_0_75', 'WH_lep_PTV_150_250_0J']
STXSScaleCorrelationScheme['WH_scale_highpt'] = ['WH_lep_PTV_GT250']
STXSScaleCorrelationScheme['ZH_scale_lowpt'] = ['ZH_lep_PTV_150_250_0J', 'ZH_lep_PTV_150_250_GE1J', 'ZH_lep_PTV_0_75', 'ZH_lep_PTV_75_150', 'ggZH_ll_PTV_150_250_0J', 'ggZH_ll_PTV_150_250_GE1J', 'ggZH_ll_PTV_0_75', 'ggZH_ll_PTV_75_150', 'ggZH_nunu_PTV_150_250_0J', 'ggZH_nunu_PTV_150_250_GE1J', 'ggZH_nunu_PTV_0_75', 'ggZH_nunu_PTV_75_150']
STXSScaleCorrelationScheme['ZH_scale_highpt'] = ['ZH_lep_PTV_GT250','ggZH_ll_PTV_GT250','ggZH_nunu_PTV_GT250']
STXSScaleCorrelationScheme['ttH_scale_lowpt'] = ['ttH_PTH_200_300', 'ttH_PTH_60_120', 'ttH_PTH_120_200', 'ttH_PTH_0_60']
STXSScaleCorrelationScheme['ttH_scale_highpt'] = ['ttH_PTH_GT300']
STXSScaleCorrelationScheme['tH_scale'] = ['tHq','tHW']
STXSScaleCorrelationScheme['bbH_scale'] = ['bbH']
