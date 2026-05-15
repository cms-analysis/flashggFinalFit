# Config file: options for signal fitting

backgroundScriptCfg = {
  
  # Setup
  'inputWS':'/eos/user/j/jlangfor/icrf/hgg/run3hggstxs/May26/samples/split_nlep_merged_GG_GJ_noMET_minimal_xgb_output_htc/nominal/merged/allData.root', # location of 'allData.root' file
  'cats':'RECO_GG2H_0J_PTH_0_10,RECO_GG2H_0J_PTH_GT10,RECO_GG2H_1J_PTH_0_60,RECO_GG2H_1J_PTH_120_200,RECO_GG2H_1J_PTH_60_120,RECO_GG2H_GE2J_MJJ_0_350_PTH_0_60,RECO_GG2H_GE2J_MJJ_0_350_PTH_120_200,RECO_GG2H_GE2J_MJJ_0_350_PTH_60_120,RECO_GG2H_GE2J_MJJ_GT350_PTH_0_200,RECO_GG2H_PTH_200_300,RECO_GG2H_PTH_300_450,RECO_GG2H_PTH_GT450,RECO_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25,RECO_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25,RECO_QQ2HQQ_GE2J_MJJ_60_120,RECO_QQ2HQQ_GE2J_MJJ_GT350_PTH_GT200,RECO_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25,RECO_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25,RECO_QQ2HQQ_REST,RECO_TH_tH_had,RECO_TH_tH_lep,RECO_TTH_PTH_0_60_ttH_had,RECO_TTH_PTH_0_60_ttH_lep,RECO_TTH_PTH_0_60_ttH_semilep,RECO_TTH_PTH_120_200_ttH_had,RECO_TTH_PTH_120_200_ttH_lep,RECO_TTH_PTH_120_200_ttH_semilep,RECO_TTH_PTH_200_300_ttH_had,RECO_TTH_PTH_200_300_ttH_lep,RECO_TTH_PTH_200_300_ttH_semilep,RECO_TTH_PTH_60_120_ttH_had,RECO_TTH_PTH_60_120_ttH_lep,RECO_TTH_PTH_60_120_ttH_semilep,RECO_TTH_PTH_GT300_ttH_had,RECO_TTH_PTH_GT300_ttH_lep,RECO_TTH_PTH_GT300_ttH_semilep,RECO_WH2HLNU_PTV_0_75,RECO_WH2HLNU_PTV_75_150,RECO_WH2HLNU_PTV_GT150,RECO_ZH2HLL_ZH_ll,RECO_ZH2HLL_ZH_nunu',
  'catOffset':0, # add offset to category numbers (useful for categories from different allData.root files)  
  'ext':'split_nlep_merged_GG_GJ_noMET_minimal_xgb_output_htc', # extension to add to output directory
  'year':'combined', # Use combined when merging all years in category (for plots)

  # Job submission options
  'batch':'condor', # [condor,SGE,IC,local]
  'queue':'espresso' # for condor e.g. microcentury
  
}
