def custom_crab(config):
  print '>> Customising the crab config'
  #config.Site.storageSite = 'T2_CH_CERNBOX'
  config.Site.storageSite = 'T2_UK_London_IC'
  config.Site.blacklist = ['T3_US_Baylor', 'T3_US_UMiss', 'T2_KR_KISTI', 'T2_DE_RWTH', 'T2_EE_Estonia']
  config.JobType.allowUndistributedCMSSW = True
  config.JobType.numCores = 4
  config.Data.outLFNDirBase = '/store/user/jlangfor/'
  config.General.transferLogs = True
  config.Data.outputPrimaryDataset = "Combine_HGGlegacy_UL_test"
