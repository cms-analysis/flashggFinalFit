# Config file: options for signal fitting

_year = '2023preBPix'

signalScriptCfg = {
  
  # Setup
  'inputWSDir':'/vols/cms/jl2117/icrf/hgg/stxs/May26/samples/split_nlep_merged_GG_GJ_noMET_minimal_xgb_output_htc/nominal/%s'%_year,
  'procs':'auto', # if auto: inferred automatically from filenames
  'cats':'RECO_GG2H_0J_PTH_0_10,RECO_GG2H_0J_PTH_GT10,RECO_GG2H_1J_PTH_0_60,RECO_GG2H_1J_PTH_120_200,RECO_GG2H_1J_PTH_60_120,RECO_GG2H_GE2J_MJJ_0_350_PTH_0_60,RECO_GG2H_GE2J_MJJ_0_350_PTH_120_200,RECO_GG2H_GE2J_MJJ_0_350_PTH_60_120,RECO_GG2H_GE2J_MJJ_GT350_PTH_0_200,RECO_GG2H_PTH_200_300,RECO_GG2H_PTH_300_450,RECO_GG2H_PTH_GT450,RECO_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25,RECO_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25,RECO_QQ2HQQ_GE2J_MJJ_60_120,RECO_QQ2HQQ_GE2J_MJJ_GT350_PTH_GT200,RECO_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25,RECO_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25,RECO_QQ2HQQ_REST,RECO_TH_tH_had,RECO_TH_tH_lep,RECO_TTH_PTH_0_60_ttH_had,RECO_TTH_PTH_0_60_ttH_lep,RECO_TTH_PTH_0_60_ttH_semilep,RECO_TTH_PTH_120_200_ttH_had,RECO_TTH_PTH_120_200_ttH_lep,RECO_TTH_PTH_120_200_ttH_semilep,RECO_TTH_PTH_200_300_ttH_had,RECO_TTH_PTH_200_300_ttH_lep,RECO_TTH_PTH_200_300_ttH_semilep,RECO_TTH_PTH_60_120_ttH_had,RECO_TTH_PTH_60_120_ttH_lep,RECO_TTH_PTH_60_120_ttH_semilep,RECO_TTH_PTH_GT300_ttH_had,RECO_TTH_PTH_GT300_ttH_lep,RECO_TTH_PTH_GT300_ttH_semilep,RECO_WH2HLNU_PTV_0_75,RECO_WH2HLNU_PTV_75_150,RECO_WH2HLNU_PTV_GT150,RECO_ZH2HLL_ZH_ll,RECO_ZH2HLL_ZH_nunu', # if auto: inferred automatically from (0) workspace
  'ext':'split_nlep_merged_GG_GJ_noMET_minimal_xgb_output_htc_%s'%_year,
  'analysis':"HIG-25-020", #'tutorial', # To specify which replacement dataset mapping (defined in ./python/replacementMap.py)
  'year':'%s'%_year, # Use 'combined' if merging all years: not recommended
  'massPoints':'125',

  #Photon shape systematics  
  'scales':'', # separate nuisance per year
  'scalesCorr':'', # correlated across years
  'scalesGlobal':'', # affect all processes equally, correlated across years
  'smears':'', # separate nuisance per year

  # Job submission options
  'batch':'condor', # ['condor','SGE','IC','local']
  'queue':'3600',

}
