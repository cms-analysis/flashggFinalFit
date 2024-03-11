def custom_crab(config):
  print '>> Customising the crab config'
  #config.Site.storageSite = 'T2_CH_CERNBOX'
  config.Site.storageSite = 'T3_CH_PSI'
  config.Site.blacklist = ['T3_US_Baylor', 'T3_US_UMiss', 'T2_KR_KISTI', 'T2_EE_Estonia']
  config.JobType.allowUndistributedCMSSW = True
  config.JobType.numCores = 1
  config.Data.outLFNDirBase = '/store/user/niharrin/'
  config.General.transferLogs = True
  config.Data.outputPrimaryDataset = "Combine_HGG_NanoAOD_Test"
  #config.Data.splitting = 'Automatic'
  #config.Data.unitsPerJob = 500