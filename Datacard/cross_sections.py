from collections import OrderedDict as od

# Define values (mh = 125)
BR_hgg = 0.002270
W_BR_had = 0.6741
W_BR_lep = 0.3259
Z_BR_had = 0.6991
Z_BR_lep = 0.3009
Z_BR_ll = 0.100974
Z_BR_nunu = 0.200

# XS in pb
XS_ggh = 48.58
XS_vbf = 3.782
XS_wh = 1.373
XS_zh = 0.8839
XS_ggzh = 0.1227
XS_qqzh = XS_zh-XS_ggzh
XS_tth = 0.5071
XS_bbh = 0.4880
XS_thq = 0.07713
XS_thw = 0.01517

stxs_xs = od()
# GGH
stxs_xs["ggH_FWDH"] = 0.0809 * XS_ggh*BR_hgg
stxs_xs["ggH_PTH_200_300"] = 0.0098 * XS_ggh*BR_hgg
stxs_xs["ggH_PTH_300_450"] = 0.0025 * XS_ggh*BR_hgg
stxs_xs["ggH_PTH_450_650"] = 0.0003 * XS_ggh*BR_hgg
stxs_xs["ggH_PTH_GT650"] = 0.0001 * XS_ggh*BR_hgg
stxs_xs["ggH_0J_PTH_0_10"] = 0.1387 * XS_ggh*BR_hgg
stxs_xs["ggH_0J_PTH_GT10"] = 0.3940 * XS_ggh*BR_hgg
stxs_xs["ggH_1J_PTH_0_60"] = 0.1477 * XS_ggh*BR_hgg
stxs_xs["ggH_1J_PTH_60_120"] = 0.1023 * XS_ggh*BR_hgg
stxs_xs["ggH_1J_PTH_120_200"] = 0.0182 * XS_ggh*BR_hgg
stxs_xs["ggH_GE2J_MJJ_0_350_PTH_0_60"] = 0.0256 * XS_ggh*BR_hgg
stxs_xs["ggH_GE2J_MJJ_0_350_PTH_60_120"] = 0.0410 * XS_ggh*BR_hgg
stxs_xs["ggH_GE2J_MJJ_0_350_PTH_120_200"] = 0.0188 * XS_ggh*BR_hgg
stxs_xs["ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25"] = 0.0063 * XS_ggh*BR_hgg
stxs_xs["ggH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25"] = 0.0077 * XS_ggh*BR_hgg
stxs_xs["ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25"] = 0.0028 * XS_ggh*BR_hgg
stxs_xs["ggH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25"] = 0.0032 * XS_ggh*BR_hgg
# VBF
stxs_xs["qqH_FWDH"] = 0.0669 * XS_vbf*BR_hgg
stxs_xs["qqH_0J"] = 0.0695 * XS_vbf*BR_hgg
stxs_xs["qqH_1J"] = 0.3283 * XS_vbf*BR_hgg
stxs_xs["qqH_GE2J_MJJ_0_60"] = 0.0136 * XS_vbf*BR_hgg
stxs_xs["qqH_GE2J_MJJ_60_120"] = 0.0240 * XS_vbf*BR_hgg
stxs_xs["qqH_GE2J_MJJ_120_350"] = 0.1234 * XS_vbf*BR_hgg
stxs_xs["qqH_GE2J_MJJ_GT350_PTH_GT200"] = 0.0398 * XS_vbf*BR_hgg
stxs_xs["qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25"] = 0.1026 * XS_vbf*BR_hgg
stxs_xs["qqH_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25"] = 0.0385 * XS_vbf*BR_hgg
stxs_xs["qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25"] = 0.1509 * XS_vbf*BR_hgg
stxs_xs["qqH_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25"] = 0.0425 * XS_vbf*BR_hgg
# WH had
stxs_xs["WH_had_FWDH"] = 0.1257 * XS_wh*W_BR_had*BR_hgg
stxs_xs["WH_had_0J"] = 0.0570 * XS_wh*W_BR_had*BR_hgg
stxs_xs["WH_had_1J"] = 0.3113 * XS_wh*W_BR_had*BR_hgg
stxs_xs["WH_had_GE2J_MJJ_0_60"] = 0.0358 * XS_wh*W_BR_had*BR_hgg
stxs_xs["WH_had_GE2J_MJJ_60_120"] = 0.2943 * XS_wh*W_BR_had*BR_hgg
stxs_xs["WH_had_GE2J_MJJ_120_350"] = 0.1392 * XS_wh*W_BR_had*BR_hgg
stxs_xs["WH_had_GE2J_MJJ_GT350_PTH_GT200"] = 0.0088 * XS_wh*W_BR_had*BR_hgg
stxs_xs["WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25"] = 0.0044 * XS_wh*W_BR_had*BR_hgg
stxs_xs["WH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25"] = 0.0186 * XS_wh*W_BR_had*BR_hgg
stxs_xs["WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25"] = 0.0009 * XS_wh*W_BR_had*BR_hgg
stxs_xs["WH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25"] = 0.0040 * XS_wh*W_BR_had*BR_hgg
# ZH had
stxs_xs["ZH_had_FWDH"] = 0.1143 * XS_qqzh*Z_BR_had*BR_hgg
stxs_xs["ZH_had_0J"] = 0.0433 * XS_qqzh*Z_BR_had*BR_hgg
stxs_xs["ZH_had_1J"] = 0.2906 * XS_qqzh*Z_BR_had*BR_hgg
stxs_xs["ZH_had_GE2J_MJJ_0_60"] = 0.0316 * XS_qqzh*Z_BR_had*BR_hgg
stxs_xs["ZH_had_GE2J_MJJ_60_120"] = 0.3360 * XS_qqzh*Z_BR_had*BR_hgg
stxs_xs["ZH_had_GE2J_MJJ_120_350"] = 0.1462 * XS_qqzh*Z_BR_had*BR_hgg
stxs_xs["ZH_had_GE2J_MJJ_GT350_PTH_GT200"] = 0.0083 * XS_qqzh*Z_BR_had*BR_hgg
stxs_xs["ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25"] = 0.0041 * XS_qqzh*Z_BR_had*BR_hgg
stxs_xs["ZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25"] = 0.0202 * XS_qqzh*Z_BR_had*BR_hgg
stxs_xs["ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25"] = 0.0009 * XS_qqzh*Z_BR_had*BR_hgg
stxs_xs["ZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25"] = 0.0045 * XS_qqzh*Z_BR_had*BR_hgg
# WH lep
stxs_xs["WH_lep_FWDH"] = 0.1213 * XS_wh*W_BR_lep*BR_hgg
stxs_xs["WH_lep_PTV_0_75"] = 0.4655 * XS_wh*W_BR_lep*BR_hgg
stxs_xs["WH_lep_PTV_75_150"] = 0.2930 * XS_wh*W_BR_lep*BR_hgg
stxs_xs["WH_lep_PTV_150_250_0J"] = 0.0510 * XS_wh*W_BR_lep*BR_hgg
stxs_xs["WH_lep_PTV_150_250_GE1J"] = 0.0397 * XS_wh*W_BR_lep*BR_hgg
stxs_xs["WH_lep_PTV_GT250"] = 0.0295 * XS_wh*W_BR_lep*BR_hgg
# ZH lep
stxs_xs["ZH_lep_FWDH"] = 0.1121 * XS_qqzh*Z_BR_lep*BR_hgg
stxs_xs["ZH_lep_PTV_0_75"] = 0.4565 * XS_qqzh*Z_BR_lep*BR_hgg
stxs_xs["ZH_lep_PTV_75_150"] = 0.3070 * XS_qqzh*Z_BR_lep*BR_hgg
stxs_xs["ZH_lep_PTV_150_250_0J"] = 0.0516 * XS_qqzh*Z_BR_lep*BR_hgg
stxs_xs["ZH_lep_PTV_150_250_GE1J"] = 0.0427 * XS_qqzh*Z_BR_lep*BR_hgg
stxs_xs["ZH_lep_PTV_GT250"] = 0.0301 * XS_qqzh*Z_BR_lep*BR_hgg
# ggZH had
stxs_xs["ggZH_had_FWDH"] = 0.0273 * XS_ggzh*Z_BR_had*BR_hgg
stxs_xs["ggZH_had_PTH_200_300"] = 0.1393 * XS_ggzh*Z_BR_had*BR_hgg
stxs_xs["ggZH_had_PTH_300_450"] = 0.0386 * XS_ggzh*Z_BR_had*BR_hgg
stxs_xs["ggZH_had_PTH_450_650"] = 0.0077 * XS_ggzh*Z_BR_had*BR_hgg
stxs_xs["ggZH_had_PTH_GT650"] = 0.0020 * XS_ggzh*Z_BR_had*BR_hgg
stxs_xs["ggZH_had_0J_PTH_0_10"] = 0.0001 * XS_ggzh*Z_BR_had*BR_hgg
stxs_xs["ggZH_had_0J_PTH_GT10"] = 0.0029 * XS_ggzh*Z_BR_had*BR_hgg
stxs_xs["ggZH_had_1J_PTH_0_60"] = 0.0200 * XS_ggzh*Z_BR_had*BR_hgg
stxs_xs["ggZH_had_1J_PTH_60_120"] = 0.0534 * XS_ggzh*Z_BR_had*BR_hgg
stxs_xs["ggZH_had_1J_PTH_120_200"] = 0.0353 * XS_ggzh*Z_BR_had*BR_hgg
stxs_xs["ggZH_had_GE2J_MJJ_0_350_PTH_0_60"] = 0.0574 * XS_ggzh*Z_BR_had*BR_hgg
stxs_xs["ggZH_had_GE2J_MJJ_0_350_PTH_60_120"] = 0.1963 * XS_ggzh*Z_BR_had*BR_hgg
stxs_xs["ggZH_had_GE2J_MJJ_0_350_PTH_120_200"] = 0.2954 * XS_ggzh*Z_BR_had*BR_hgg
stxs_xs["ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25"] = 0.0114 * XS_ggzh*Z_BR_had*BR_hgg
stxs_xs["ggZH_had_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25"] = 0.0806 * XS_ggzh*Z_BR_had*BR_hgg
stxs_xs["ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25"] = 0.0036 * XS_ggzh*Z_BR_had*BR_hgg
stxs_xs["ggZH_had_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25"] = 0.0285 * XS_ggzh*Z_BR_had*BR_hgg
# ggZH, Z->ll
stxs_xs["ggZH_ll_FWDH"] = 0.0270 * XS_ggzh*Z_BR_ll*BR_hgg
stxs_xs["ggZH_ll_PTV_0_75"] = 0.1605 * XS_ggzh*Z_BR_ll*BR_hgg
stxs_xs["ggZH_ll_PTV_75_150"] = 0.4325 * XS_ggzh*Z_BR_ll*BR_hgg
stxs_xs["ggZH_ll_PTV_150_250_0J"] = 0.0913 * XS_ggzh*Z_BR_ll*BR_hgg
stxs_xs["ggZH_ll_PTV_150_250_GE1J"] = 0.2044 * XS_ggzh*Z_BR_ll*BR_hgg
stxs_xs["ggZH_ll_PTV_GT250"] = 0.0844 * XS_ggzh*Z_BR_ll*BR_hgg
# ggZH, Z->nunu
stxs_xs["ggZH_nunu_FWDH"] = 0.0271 * XS_ggzh*Z_BR_nunu*BR_hgg
stxs_xs["ggZH_nunu_PTV_0_75"] = 0.1591 * XS_ggzh*Z_BR_nunu*BR_hgg
stxs_xs["ggZH_nunu_PTV_75_150"] = 0.4336 * XS_ggzh*Z_BR_nunu*BR_hgg
stxs_xs["ggZH_nunu_PTV_150_250_0J"] = 0.0905 * XS_ggzh*Z_BR_nunu*BR_hgg
stxs_xs["ggZH_nunu_PTV_150_250_GE1J"] = 0.2051 * XS_ggzh*Z_BR_nunu*BR_hgg
stxs_xs["ggZH_nunu_PTV_GT250"] = 0.0845 * XS_ggzh*Z_BR_nunu*BR_hgg
# ttH
stxs_xs["ttH_FWDH"] = 0.0135 * XS_tth*BR_hgg
stxs_xs["ttH_PTH_0_60"] = 0.2250 * XS_tth*BR_hgg
stxs_xs["ttH_PTH_60_120"] = 0.3473 * XS_tth*BR_hgg
stxs_xs["ttH_PTH_120_200"] = 0.2569 * XS_tth*BR_hgg
stxs_xs["ttH_PTH_200_300"] = 0.1076 * XS_tth*BR_hgg
stxs_xs["ttH_PTH_GT300"] = 0.0533 * XS_tth*BR_hgg
# bbH
stxs_xs["bbH_FWDH"] = 0.0487* XS_bbh*BR_hgg
stxs_xs["bbH"] = 0.9513* XS_bbh*BR_hgg
# tHq
stxs_xs["tHq_FWDH"] = 0.0279 * XS_thq*BR_hgg
stxs_xs["tHq"] = 0.9721 * XS_thq*BR_hgg
# tHW
stxs_xs["tHW_FWDH"] = 0.0106 * XS_thw*BR_hgg
stxs_xs["tHW"] = 0.9894 * XS_thw*BR_hgg
