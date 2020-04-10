models = {
  "mu_inclusive":"",

  "mu":"-P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
--PO \"map=.*/ggH.*:r_ggH[1,0,2]\" \
--PO \"map=.*/qqH.*:r_VBF[1,0,3]\" \
--PO \"map=.*/WH_had.*:r_VH[1,0,3]\" \
--PO \"map=.*/ZH_had.*:r_VH[1,0,3]\" \
--PO \"map=.*/WH_lep.*:r_VH[1,0,3]\" \
--PO \"map=.*/ZH_lep.*:r_VH[1,0,3]\" \
--PO \"map=.*/ttH.*:r_top[1,0,3]\" \
--PO \"map=.*/tHq.*:r_top[1,0,3]\"",

  "stage0":"-P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
--PO \"map=.*/ggH_.*:r_ggH[1,0,2]\" \
--PO \"map=.*/qqH_.*:r_VBF[1,0,3]\" \
--PO \"map=.*/WH_had_.*:r_VH_had[1,0,6]\" \
--PO \"map=.*/ZH_had_.*:r_VH_had[1,0,6]\" \
--PO \"map=.*/WH_lep.*:r_WH_lep[1,0,6]\" \
--PO \"map=.*/ZH_lep.*:r_ZH_lep[1,0,6]\" \
--PO \"map=.*/ttH.*:r_ttH[1,0,2]\" \
--PO \"map=.*/tHq.*:r_tHq[1,0,8]\"",

  "stage1p2_maximal":"-P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
--PO \"map=.*/ggH_0J_PTH_0_10.*:r_ggH_0J_low[1,0,4]\" \
--PO \"map=.*/ggH_0J_PTH_GT10.*:r_ggH_0J_high[1,0,2]\" \
--PO \"map=.*/ggH_1J_PTH_0_60.*:r_ggH_1J_low[1,0,4]\" \
--PO \"map=.*/ggH_1J_PTH_60_120.*:r_ggH_1J_med[1,0,4]\" \
--PO \"map=.*/ggH_1J_PTH_120_200.*:r_ggH_1J_high[1,0,4]\" \
--PO \"map=.*/ggH_GE2J_MJJ_0_350_PTH_0_60.*:r_ggH_2J_low[1,0,4]\" \
--PO \"map=.*/ggH_GE2J_MJJ_0_350_PTH_60_120.*:r_ggH_2J_med[1,0,4]\" \
--PO \"map=.*/ggH_GE2J_MJJ_0_350_PTH_120_200.*:r_ggH_2J_high[1,0,4]\" \
--PO \"map=.*/ggH_PTH_.*:r_ggH_BSM[1,0,4]\" \
--PO \"map=.*/ggH_GE2J_MJJ_350_700_.*.*:r_ggH_VBFlike[1,0,6]\" \
--PO \"map=.*/ggH_GE2J_MJJ_GT700_.*.*:r_ggH_VBFlike[1,0,6]\" \
--PO \"map=.*/qqH_GE2J_MJJ_350_700_PTH_0_200_.*:r_qqH_low_mjj[1,0,4]\" \
--PO \"map=.*/qqH_GE2J_MJJ_GT700_PTH_0_200_.*:r_qqH_high_mjj[1,0,4]\" \
--PO \"map=.*/qqH_GE2J_.*_PTH_GT200.*:r_qqH_BSM[1,0,4]\" \
--PO \"map=.*/WH_had_GE2J_MJJ_350_700_PTH_0_200_.*:r_qqH_low_mjj[1,0,4]\" \
--PO \"map=.*/WH_had_GE2J_MJJ_GT700_PTH_0_200_.*:r_qqH_high_mjj[1,0,4]\" \
--PO \"map=.*/WH_had_GE2J_.*_PTH_GT200.*:r_qqH_BSM[1,0,4]\" \
--PO \"map=.*/ZH_had_GE2J_MJJ_350_700_PTH_0_200_.*:r_qqH_low_mjj[1,0,4]\" \
--PO \"map=.*/ZH_had_GE2J_MJJ_GT700_PTH_0_200_.*:r_qqH_high_mjj[1,0,4]\" \
--PO \"map=.*/ZH_had_GE2J_.*_PTH_GT200.*:r_qqH_BSM[1,0,4]\" \
--PO \"map=.*/qqH_GE2J_MJJ_60_120.*:r_qqH_VHhad[1,0,6]\" \
--PO \"map=.*/WH_had_GE2J_MJJ_60_120.*:r_qqH_VHhad[1,0,6]\" \
--PO \"map=.*/ZH_had_GE2J_MJJ_60_120.*:r_qqH_VHhad[1,0,6]\" \
--PO \"map=.*/WH_lep.*hgg:r_WH_lep[1,0,6]\" \
--PO \"map=.*/ZH_lep.*hgg:r_ZH_lep[1,0,6]\" \
--PO \"map=.*/ttH.*hgg:r_ttH[1,0,2]\" \
--PO \"map=.*/tHq.*hgg:r_tHq[1,0,8]\"",

  "stage1p2_intermediate":"-P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
--PO \"map=.*/ggH_0J_PTH_0_10.*:r_ggH_0J_low[1,0,4]\" \
--PO \"map=.*/ggH_0J_PTH_GT10.*:r_ggH_0J_high[1,0,2]\" \
--PO \"map=.*/ggH_1J_PTH_0_60.*:r_ggH_1J_low[1,0,4]\" \
--PO \"map=.*/ggH_1J_PTH_60_120.*:r_ggH_1J_med[1,0,4]\" \
--PO \"map=.*/ggH_1J_PTH_120_200.*:r_ggH_1J_high[1,0,4]\" \
--PO \"map=.*/ggH_GE2J_MJJ_0_350_PTH_0_60.*:r_ggH_2J_low[1,0,4]\" \
--PO \"map=.*/ggH_GE2J_MJJ_0_350_PTH_60_120.*:r_ggH_2J_med[1,0,4]\" \
--PO \"map=.*/ggH_GE2J_MJJ_0_350_PTH_120_200.*:r_ggH_2J_high[1,0,4]\" \
--PO \"map=.*/ggH_PTH_200_300.*:r_ggH_BSM_low[1,0,4]\" \
--PO \"map=.*/ggH_PTH_300_450.*:r_ggH_BSM_high[1,0,4]\" \
--PO \"map=.*/ggH_PTH_450_650.*:r_ggH_BSM_high[1,0,4]\" \
--PO \"map=.*/ggH_PTH_GT650.*:r_ggH_BSM_high[1,0,4]\" \
--PO \"map=.*/ggH_GE2J_MJJ_350_700_.*.*:r_ggH_VBFlike[1,0,6]\" \
--PO \"map=.*/ggH_GE2J_MJJ_GT700_.*.*:r_ggH_VBFlike[1,0,6]\" \
--PO \"map=.*/qqH_GE2J_MJJ_350_700_PTH_0_200_.*:r_qqH_low_mjj[1,0,4]\" \
--PO \"map=.*/qqH_GE2J_MJJ_GT700_PTH_0_200_.*:r_qqH_high_mjj[1,0,4]\" \
--PO \"map=.*/qqH_GE2J_.*_PTH_GT200.*:r_qqH_BSM[1,0,4]\" \
--PO \"map=.*/WH_had_GE2J_MJJ_350_700_PTH_0_200_.*:r_qqH_low_mjj[1,0,4]\" \
--PO \"map=.*/WH_had_GE2J_MJJ_GT700_PTH_0_200_.*:r_qqH_high_mjj[1,0,4]\" \
--PO \"map=.*/WH_had_GE2J_.*_PTH_GT200.*:r_qqH_BSM[1,0,4]\" \
--PO \"map=.*/ZH_had_GE2J_MJJ_350_700_PTH_0_200_.*:r_qqH_low_mjj[1,0,4]\" \
--PO \"map=.*/ZH_had_GE2J_MJJ_GT700_PTH_0_200_.*:r_qqH_high_mjj[1,0,4]\" \
--PO \"map=.*/ZH_had_GE2J_.*_PTH_GT200.*:r_qqH_BSM[1,0,4]\" \
--PO \"map=.*/qqH_GE2J_MJJ_60_120.*:r_qqH_VHhad[1,0,6]\" \
--PO \"map=.*/WH_had_GE2J_MJJ_60_120.*:r_qqH_VHhad[1,0,6]\" \
--PO \"map=.*/ZH_had_GE2J_MJJ_60_120.*:r_qqH_VHhad[1,0,6]\" \
--PO \"map=.*/WH_lep_PTV_0_75.*hgg:r_WH_lep_low[1,0,6]\" \
--PO \"map=.*/WH_lep_PTV_75_150.*hgg:r_WH_lep_high[1,0,6]\" \
--PO \"map=.*/WH_lep_PTV_150_250.*hgg:r_WH_lep_high[1,0,6]\" \
--PO \"map=.*/WH_lep_PTV_GT250.*hgg:r_WH_lep_high[1,0,6]\" \
--PO \"map=.*/ZH_lep.*hgg:r_ZH_lep[1,0,6]\" \
--PO \"map=.*/ttH_PTH_0_60.*hgg:r_ttH_low[1,0,3]\" \
--PO \"map=.*/ttH_PTH_60_120.*hgg:r_ttH_low[1,0,3]\" \
--PO \"map=.*/ttH_PTH_120_200.*hgg:r_ttH_high[1,0,3]\" \
--PO \"map=.*/ttH_PTH_200_300.*hgg:r_ttH_high[1,0,3]\" \
--PO \"map=.*/ttH_PTH_GT300.*hgg:r_ttH_high[1,0,3]\" \
--PO \"map=.*/tHq.*hgg:r_tHq[1,0,8]\"",

  "stage1p2_minimal":"-P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel \
--PO \"map=.*/ggH_0J_PTH_0_10.*:r_ggH_0J_low[1,0,4]\" \
--PO \"map=.*/ggH_0J_PTH_GT10.*:r_ggH_0J_high[1,0,2]\" \
--PO \"map=.*/ggH_1J_PTH_0_60.*:r_ggH_1J_low[1,0,4]\" \
--PO \"map=.*/ggH_1J_PTH_60_120.*:r_ggH_1J_med[1,0,4]\" \
--PO \"map=.*/ggH_1J_PTH_120_200.*:r_ggH_1J_high[1,0,4]\" \
--PO \"map=.*/ggH_GE2J_MJJ_0_350_PTH_0_60.*:r_ggH_2J_low[1,0,4]\" \
--PO \"map=.*/ggH_GE2J_MJJ_0_350_PTH_60_120.*:r_ggH_2J_med[1,0,4]\" \
--PO \"map=.*/ggH_GE2J_MJJ_0_350_PTH_120_200.*:r_ggH_2J_high[1,0,4]\" \
--PO \"map=.*/ggH_PTH_200_300.*:r_ggH_BSM_low[1,0,4]\" \
--PO \"map=.*/ggH_PTH_300_450.*:r_ggH_BSM_high[1,0,4]\" \
--PO \"map=.*/ggH_PTH_450_650.*:r_ggH_BSM_high[1,0,4]\" \
--PO \"map=.*/ggH_PTH_GT650.*:r_ggH_BSM_high[1,0,4]\" \
--PO \"map=.*/ggH_GE2J_MJJ_350_700_.*.*:r_ggH_VBFlike[1,0,6]\" \
--PO \"map=.*/ggH_GE2J_MJJ_GT700_.*.*:r_ggH_VBFlike[1,0,6]\" \
--PO \"map=.*/qqH_GE2J_MJJ_350_700_PTH_0_200_.*:r_qqH_low_mjj[1,0,4]\" \
--PO \"map=.*/qqH_GE2J_MJJ_GT700_PTH_0_200_.*:r_qqH_high_mjj[1,0,4]\" \
--PO \"map=.*/qqH_GE2J_.*_PTH_GT200.*:r_qqH_BSM[1,0,4]\" \
--PO \"map=.*/WH_had_GE2J_MJJ_350_700_PTH_0_200_.*:r_qqH_low_mjj[1,0,4]\" \
--PO \"map=.*/WH_had_GE2J_MJJ_GT700_PTH_0_200_.*:r_qqH_high_mjj[1,0,4]\" \
--PO \"map=.*/WH_had_GE2J_.*_PTH_GT200.*:r_qqH_BSM[1,0,4]\" \
--PO \"map=.*/ZH_had_GE2J_MJJ_350_700_PTH_0_200_.*:r_qqH_low_mjj[1,0,4]\" \
--PO \"map=.*/ZH_had_GE2J_MJJ_GT700_PTH_0_200_.*:r_qqH_high_mjj[1,0,4]\" \
--PO \"map=.*/ZH_had_GE2J_.*_PTH_GT200.*:r_qqH_BSM[1,0,4]\" \
--PO \"map=.*/qqH_GE2J_MJJ_60_120.*:r_qqH_VHhad[1,0,6]\" \
--PO \"map=.*/WH_had_GE2J_MJJ_60_120.*:r_qqH_VHhad[1,0,6]\" \
--PO \"map=.*/ZH_had_GE2J_MJJ_60_120.*:r_qqH_VHhad[1,0,6]\" \
--PO \"map=.*/WH_lep_PTV_0_75.*hgg:r_WH_lep_low[1,0,6]\" \
--PO \"map=.*/WH_lep_PTV_75_150.*hgg:r_WH_lep_high[1,0,6]\" \
--PO \"map=.*/WH_lep_PTV_150_250.*hgg:r_WH_lep_high[1,0,6]\" \
--PO \"map=.*/WH_lep_PTV_GT250.*hgg:r_WH_lep_high[1,0,6]\" \
--PO \"map=.*/ZH_lep.*hgg:r_ZH_lep[1,0,6]\" \
--PO \"map=.*/ttH_PTH_0_60.*hgg:r_ttH_low[1,0,5]\" \
--PO \"map=.*/ttH_PTH_60_120.*hgg:r_ttH_medlow[1,0,3]\" \
--PO \"map=.*/ttH_PTH_120_200.*hgg:r_ttH_medhigh[1,0,4]\" \
--PO \"map=.*/ttH_PTH_200_300.*hgg:r_ttH_high[1,0,5]\" \
--PO \"map=.*/ttH_PTH_GT300.*hgg:r_ttH_high[1,0,5]\" \
--PO \"map=.*/tHq.*hgg:r_tHq[1,0,8]\"",

  "kappas_resolved":"-P HiggsAnalysis.CombinedLimit.LHCHCGModels:K1 --PO BRU=0",

  "kappas":"-P HiggsAnalysis.CombinedLimit.LHCHCGModels:K2 --PO BRU=0",

  "kVkF":"-P HiggsAnalysis.CombinedLimit.LHCHCGModels:K3 --PO BRU=0"
}
