# Python file to store systematics: for STXS analysis

# Comment out all nuisances that you do not want to include

# THEORY SYSTEMATICS:

# For type:constant
#  1) specify same value for all processes
#  2) define process map json in ./theory_uncertainties (add process names where necessary!)

# For type:factory
# Tier system: adds different uncertainties to dataframe
#   1) shape: absolute yield of process kept constant, shape effects i.e. calc migrations across cats
#   2) ishape: as (1) but absolute yield for proc x cat is allowed to vary
#   3) norm: absolute yield of production mode (s0) kept constant but migrations across sub-processes e.g. STXS bins.Same value in each category.
#   4) inorm: as (3) but absolute yield of production mode (s0) can vary
#   5) inc: variations in production mode (s0), same value for each subprocess in each category
# Relations: shape = ishape/inorm
#            norm  = inorm/inc
# Specify as list in dict: e.g. 'tiers'=['inc','inorm','norm','ishape','shape']

theory_systematics = [
                # Normalisation uncertainties: enter interpretations
                {'name':'BR_hgg','title':'BR_hgg','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':"0.98/1.021"},
                # New scheme for ggH stage 1.2 
                {'name':'THU_ggH_stxs_Yield','title':'THU_ggH_stxs_Yield','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                {'name':'THU_ggH_stxs_Res','title':'THU_ggH_stxs_Res','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                {'name':'THU_ggH_stxs_Mig01','title':'THU_ggH_stxs_Mig01','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                {'name':'THU_ggH_stxs_Mig12','title':'THU_ggH_stxs_Mig12','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                {'name':'THU_ggH_stxs_Boosted','title':'THU_ggH_stxs_Boosted','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                {'name':'THU_ggH_stxs_PTH200','title':'THU_ggH_stxs_PTH200','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                {'name':'THU_ggH_stxs_PTH300','title':'THU_ggH_stxs_PTH300','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                {'name':'THU_ggH_stxs_PTH450','title':'THU_ggH_stxs_PTH450','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                {'name':'THU_ggH_stxs_PTH650','title':'THU_ggH_stxs_PTH650','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                {'name':'THU_ggH_stxs_0J_PTH10','title':'THU_ggH_stxs_0J_PTH10','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                {'name':'THU_ggH_stxs_1J_PTH60','title':'THU_ggH_stxs_1J_PTH60','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                {'name':'THU_ggH_stxs_1J_PTH120','title':'THU_ggH_stxs_1J_PTH120','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                {'name':'THU_ggH_stxs_GE2J_PTH60','title':'THU_ggH_stxs_GE2J_PTH60','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                {'name':'THU_ggH_stxs_GE2J_PTH120','title':'THU_ggH_stxs_GE2J_PTH120','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                {'name':'THU_ggH_stxs_GE2J_MJJ350','title':'THU_ggH_stxs_GE2J_MJJ350','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                {'name':'THU_ggH_stxs_GE2J_MJJ700','title':'THU_ggH_stxs_GE2J_MJJ700','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                {'name':'THU_ggH_stxs_GE2J_LOWMJJ_PTHJJ25','title':'THU_ggH_stxs_GE2J_LOWMJJ_PTHJJ25','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                {'name':'THU_ggH_stxs_GE2J_HIGHMJJ_PTHJJ25','title':'THU_ggH_stxs_GE2J_HIGHMJJ_PTHJJ25','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                # WG1 scheme for ggH (includes inclusive N3LO unc so dont have this + QCDscale_ggH)
                {'name':'THU_ggH_Mu','title':'THU_ggH_Mu','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['inorm']},
                {'name':'THU_ggH_Res','title':'THU_ggH_Res','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['inorm']},
                {'name':'THU_ggH_Mig01','title':'THU_ggH_Mig01','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['inorm']},
                {'name':'THU_ggH_Mig12','title':'THU_ggH_Mig12','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['inorm']},
                {'name':'THU_ggH_VBF2j','title':'THU_ggH_VBF2j','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['inorm']},
                {'name':'THU_ggH_VBF3j','title':'THU_ggH_VBF3j','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['inorm']},
                {'name':'THU_ggH_PT60','title':'THU_ggH_PT60','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['inorm']},
                {'name':'THU_ggH_PT120','title':'THU_ggH_PT120','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['inorm']},
                {'name':'THU_ggH_qmtop','title':'THU_ggH_qmtop','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['inorm']},
                #{'name':'QCDscale_ggH','title':'QCDscale_ggH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh.json'},
                # qqH STXS unc scheme (includes inclusive so dont have + QCDscale_qqH)
                {'name':'THU_qqH_Yield','title':'THU_qqH_Yield','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh_stxs.json'},
                {'name':'THU_qqH_PTH200','title':'THU_qqH_PTH200','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh_stxs.json'},
                {'name':'THU_qqH_MJJ60','title':'THU_qqH_MJJ60','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh_stxs.json'},
                {'name':'THU_qqH_MJJ120','title':'THU_qqH_MJJ120','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh_stxs.json'},
                {'name':'THU_qqH_MJJ350','title':'THU_qqH_MJJ350','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh_stxs.json'},
                {'name':'THU_qqH_MJJ700','title':'THU_qqH_MJJ700','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh_stxs.json'},
                {'name':'THU_qqH_MJJ1000','title':'THU_qqH_MJJ1000','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh_stxs.json'},
                {'name':'THU_qqH_MJJ1500','title':'THU_qqH_MJJ1500','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh_stxs.json'},
                {'name':'THU_qqH_PTHJJ25','title':'THU_qqH_PTHJJ25','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh_stxs.json'},
                {'name':'THU_qqH_JET01','title':'THU_qqH_JET01','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh_stxs.json'},
                #{'name':'QCDscale_qqH','title':'QCDscale_qqH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh.json'},
                {'name':'THU_WH_inc','title':'THU_WH_inc','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_whlep_stxs.json'},
                {'name':'THU_WH_mig75','title':'THU_WH_mig75','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_whlep_stxs.json'},
                {'name':'THU_WH_mig150','title':'THU_WH_mig150','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_whlep_stxs.json'},
                {'name':'THU_WH_mig250','title':'THU_WH_mig250','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_whlep_stxs.json'},
                {'name':'THU_WH_mig01','title':'THU_WH_mig01','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_whlep_stxs.json'},
                {'name':'THU_ZH_inc','title':'THU_ZH_inc','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_zhlep_stxs.json'},
                {'name':'THU_ZH_mig75','title':'THU_ZH_mig75','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_zhlep_stxs.json'},
                {'name':'THU_ZH_mig150','title':'THU_ZH_mig150','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_zhlep_stxs.json'},
                {'name':'THU_ZH_mig250','title':'THU_ZH_mig250','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_zhlep_stxs.json'},
                {'name':'THU_ZH_mig01','title':'THU_ZH_mig01','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_zhlep_stxs.json'},
                {'name':'THU_ggZH_inc','title':'THU_ggZH_inc','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggzhlep_stxs.json'},
                {'name':'THU_ggZH_mig75','title':'THU_ggZH_mig75','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggzhlep_stxs.json'},
                {'name':'THU_ggZH_mig150','title':'THU_ggZH_mig150','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggzhlep_stxs.json'},
                {'name':'THU_ggZH_mig250','title':'THU_ggZH_mig250','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggzhlep_stxs.json'},
                {'name':'THU_ggZH_mig01','title':'THU_ggZH_mig01','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggzhlep_stxs.json'},
                #{'name':'QCDscale_VH','title':'QCDscale_VH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_vh.json'}, # Note: VH had components accounted for in THU_qqH_*, set to 1 in json
                {'name':'QCDscale_ggZH','title':'QCDscale_ggZH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggzh.json'}, # Note: ggZH lep components are accounted for in THU_ggZH i.e. this only covers the ggZH had component
                
                {'name':'THU_ttH_Yield','title':'THU_ttH_Yield','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_tth_stxs.json'},
                {'name':'THU_ttH_mig60','title':'THU_ttH_mig60','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_tth_stxs.json'},
                {'name':'THU_ttH_mig120','title':'THU_ttH_mig120','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_tth_stxs.json'},
                {'name':'THU_ttH_mig200','title':'THU_ttH_mig200','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_tth_stxs.json'},
                {'name':'THU_ttH_mig300','title':'THU_ttH_mig300','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_tth_stxs.json'},
                #{'name':'QCDscale_ttH','title':'QCDscale_ttH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_tth.json'},
                {'name':'QCDscale_tHq','title':'QCDscale_tHq','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_thq.json'},
                {'name':'QCDscale_tHW','title':'QCDscale_tHW','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_thw.json'},
                {'name':'QCDscale_bbH','title':'QCDscale_bbH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_bbh.json'},
                {'name':'pdf_Higgs_ggH','title':'pdf_Higgs_ggH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh.json'},
                {'name':'pdf_Higgs_qqH','title':'pdf_Higgs_qqH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh.json'},
                {'name':'pdf_Higgs_VH','title':'pdf_Higgs_VH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_vh.json'},
                {'name':'pdf_Higgs_ggZH','title':'pdf_Higgs_ggZH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggzh.json'},
                {'name':'pdf_Higgs_ttH','title':'pdf_Higgs_ttH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_tth.json'},
                {'name':'pdf_Higgs_tHq','title':'pdf_Higgs_tHq','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_thq.json'},
                {'name':'pdf_Higgs_tHW','title':'pdf_Higgs_tHW','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_thw.json'},
                {'name':'alphaS_ggH','title':'alphaS_ggH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh.json'},
                {'name':'alphaS_qqH','title':'alphaS_qqH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh.json'},
                {'name':'alphaS_VH','title':'alphaS_VH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_vh.json'},
                {'name':'alphaS_ggZH','title':'alphaS_ggZH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggzh.json'},
                {'name':'alphaS_ttH','title':'alphaS_ttH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_tth.json'},
                {'name':'alphaS_tHq','title':'alphaS_tHq','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_thq.json'},
                {'name':'alphaS_tHW','title':'alphaS_tHW','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_thw.json'},

                # Shape uncertainties: enter direct XS measurements
                # Scale weights are grouped: [1,2], [3,6], [4,8]
                #{'name':'scaleWeight_0','title':'CMS_hgg_scaleWeight_0','type':'factory','prior':'lnN','correlateAcrossYears':1}, # nominal weight
                #{'name':'scaleWeight_1','title':'CMS_hgg_scaleWeight_1','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape','mnorm']},
                #{'name':'scaleWeight_2','title':'CMS_hgg_scaleWeight_2','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape','mnorm']},
                #{'name':'scaleWeight_3','title':'CMS_hgg_scaleWeight_3','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape','mnorm']},
                {'name':'scaleWeight_4','title':'CMS_hgg_scaleWeight_4','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape','mnorm']},
                #{'name':'scaleWeight_5','title':'CMS_hgg_scaleWeight_5','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['norm','shape']}, #Unphysical
                #{'name':'scaleWeight_6','title':'CMS_hgg_scaleWeight_6','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape','mnorm']},
                #{'name':'scaleWeight_7','title':'CMS_hgg_scaleWeight_7','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['norm','shape']}, #Unphysical
                {'name':'scaleWeight_8','title':'CMS_hgg_scaleWeight_8','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape','mnorm']},
                {'name':'alphaSWeight_0','title':'CMS_hgg_alphaSWeight_0','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']},
                {'name':'alphaSWeight_1','title':'CMS_hgg_alphaSWeight_1','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']},

                # Theory uncertainties for constrained to SM bins
                {'name':'THU_qqH_Yield_qqH_cnstr','title':'STXS_constrain_THU_qqH_Yield','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh_stxs_constrain.json'},
                {'name':'THU_qqH_PTH200_qqH_cnstr','title':'STXS_constrain_THU_qqH_PTH200','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh_stxs_constrain.json'},
                {'name':'THU_qqH_MJJ60_qqH_cnstr','title':'STXS_constrain_THU_qqH_MJJ60','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh_stxs_constrain.json'},
                {'name':'THU_qqH_MJJ120_qqH_cnstr','title':'STXS_constrain_THU_qqH_MJJ120','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh_stxs_constrain.json'},
                {'name':'THU_qqH_MJJ350_qqH_cnstr','title':'STXS_constrain_THU_qqH_MJJ350','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh_stxs_constrain.json'},
                {'name':'THU_qqH_MJJ700_qqH_cnstr','title':'STXS_constrain_THU_qqH_MJJ700','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh_stxs_constrain.json'},
                {'name':'THU_qqH_MJJ1000_qqH_cnstr','title':'STXS_constrain_THU_qqH_MJJ1000','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh_stxs_constrain.json'},
                {'name':'THU_qqH_MJJ1500_qqH_cnstr','title':'STXS_constrain_THU_qqH_MJJ1500','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh_stxs_constrain.json'},
                {'name':'THU_qqH_PTHJJ25_qqH_cnstr','title':'STXS_constrain_THU_qqH_PTHJJ25','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh_stxs_constrain.json'},
                {'name':'THU_qqH_JET01_qqH_cnstr','title':'STXS_constrain_THU_qqH_JET01','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh_stxs_constrain.json'},
                {'name':'pdf_Higgs_qqH_cnstr','title':'STXS_constrain_pdf_Higgs','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh_stxs_constrain.json'},
                {'name':'alphaS_qqH_cnstr','title':'STXS_constrain_alphaS','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh_stxs_constrain.json'}
              ]
# PDF weight
for i in range(1,60): theory_systematics.append( {'name':'pdfWeight_%g'%i, 'title':'CMS_hgg_pdfWeight_%g'%i, 'type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']} )

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# EXPERIMENTAL SYSTEMATICS
# correlateAcrossYears = 0 : no correlation
# correlateAcrossYears = 1 : fully correlated
# correlateAcrossYears = -1 : partially correlated

experimental_systematics = [
                # Updated luminosity partial-correlation scheme: 13/5/21 (recommended simplified nuisances)
                {'name':'lumi_13TeV_Uncorrelated','title':'lumi_13TeV_Uncorrelated','type':'constant','prior':'lnN','correlateAcrossYears':0,'value':{'2016':'1.010','2017':'1.020','2018':'1.015'}},
                {'name':'lumi_13TeV_Correlated','title':'lumi_13TeV_Correlated','type':'constant','prior':'lnN','correlateAcrossYears':-1,'value':{'2016':'1.006','2017':'1.009','2018':'1.020'}},
                {'name':'lumi_13TeV_Correlated_1718','title':'lumi_13TeV_Correlated_1718','type':'constant','prior':'lnN','correlateAcrossYears':-1,'value':{'2016':'-','2017':'1.006','2018':'1.002'}},
                {'name':'LooseMvaSF','title':'CMS_hgg_LooseMvaSF','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'PreselSF','title':'CMS_hgg_PreselSF','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'electronVetoSF','title':'CMS_hgg_electronVetoSF','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'TriggerWeight','title':'CMS_hgg_TriggerWeight','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'MuonIDWeight','title':'CMS_hgg_MuonID','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'MuonIsoWeight','title':'CMS_hgg_MuonIso','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'ElectronIDWeight','title':'CMS_hgg_ElectronID','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'ElectronRecoWeight','title':'CMS_hgg_ElectronReco','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'JetBTagCutWeight','title':'CMS_hgg_BTagCut','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'JetBTagReshapeWeight','title':'CMS_hgg_BTagReshape','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'prefireWeight','title':'CMS_hgg_prefire','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'SigmaEOverEShift','title':'CMS_hgg_SigmaEOverEShift','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'MvaShift','title':'CMS_hgg_phoIdMva','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'PUJIDShift','title':'CMS_hgg_PUJIDShift','type':'factory','prior':'lnN','correlateAcrossYears':0},
                # New partial correlation scheme for JECs (do not use in addition to nominal 'JEC')
                {'name':'JECAbsolute','title':'CMS_scale_j_Absolute','type':'factory','prior':'lnN','correlateAcrossYears':1},
                {'name':'JECFlavorQCD','title':'CMS_scale_j_FlavorQCD','type':'factory','prior':'lnN','correlateAcrossYears':1},
                {'name':'JECBBEC1','title':'CMS_scale_j_BBEC1','type':'factory','prior':'lnN','correlateAcrossYears':1},
                {'name':'JECHF','title':'CMS_scale_j_HF','type':'factory','prior':'lnN','correlateAcrossYears':1},
                {'name':'JECEC2','title':'CMS_scale_j_EC2','type':'factory','prior':'lnN','correlateAcrossYears':1},
                {'name':'JECRelativeBal','title':'CMS_scale_j_RelativeBal','type':'factory','prior':'lnN','correlateAcrossYears':1},
                {'name':'JECAbsoluteYEAR','title':'CMS_scale_j_Absolute_y','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'JECBBEC1YEAR','title':'CMS_scale_j_BBEC1_y','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'JECHFYEAR','title':'CMS_scale_j_HF_y','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'JECEC2YEAR','title':'CMS_scale_j_EC2_y','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'JECRelativeSampleYEAR','title':'CMS_scale_j_RelativeSample_y','type':'factory','prior':'lnN','correlateAcrossYears':0},
               
                #{'name':'JEC','title':'CMS_scale_j','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'JER','title':'CMS_res_j','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'metJecUncertainty','title':'CMS_hgg_MET_scale_j','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'metJerUncertainty','title':'CMS_hgg_MET_res_j','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'metPhoUncertainty','title':'CMS_hgg_MET_PhotonScale','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'metUncUncertainty','title':'CMS_hgg_MET_Unclustered','type':'factory','prior':'lnN','correlateAcrossYears':0},
                # HEM issue systematic
                {'name':'JetHEM','title':'CMS_hgg_JetHEM','type':'factory','prior':'lnN','correlateAcrossYears':0}
              ]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Shape nuisances: effect encoded in signal model
# mode = (other,scalesGlobal,scales,scalesCorr,smears): match the definition in the signal models

signal_shape_systematics = [
                {'name':'deltafracright','title':'deltafracright','type':'signal_shape','mode':'other','mean':'0.0','sigma':'0.02'},
                {'name':'NonLinearity','title':'NonLinearity','type':'signal_shape','mode':'scalesGlobal','mean':'0.0','sigma':'0.002'},
                {'name':'Geant4','title':'Geant4','type':'signal_shape','mode':'scalesGlobal','mean':'0.0','sigma':'0.0005'},
                {'name':'HighR9EB','title':'HighR9EB','type':'signal_shape','mode':'scales','mean':'0.0','sigma':'1.0'},
                {'name':'HighR9EE','title':'HighR9EE','type':'signal_shape','mode':'scales','mean':'0.0','sigma':'1.0'},
                {'name':'LowR9EB','title':'LowR9EB','type':'signal_shape','mode':'scales','mean':'0.0','sigma':'1.0'},
                {'name':'LowR9EE','title':'LowR9EE','type':'signal_shape','mode':'scales','mean':'0.0','sigma':'1.0'},
                {'name':'ShowerShapeHighR9EB','title':'ShowerShapeHighR9EB','type':'signal_shape','mode':'scalesCorr','mean':'0.0','sigma':'1.0'},
                {'name':'ShowerShapeHighR9EE','title':'ShowerShapeHighR9EE','type':'signal_shape','mode':'scalesCorr','mean':'0.0','sigma':'1.0'},
                {'name':'ShowerShapeLowR9EB','title':'ShowerShapeLowR9EB','type':'signal_shape','mode':'scalesCorr','mean':'0.0','sigma':'1.0'},
                {'name':'ShowerShapeLowR9EE','title':'ShowerShapeLowR9EE','type':'signal_shape','mode':'scalesCorr','mean':'0.0','sigma':'1.0'},
                {'name':'MaterialCentralBarrel','title':'MaterialCentralBarrel','type':'signal_shape','mode':'scalesCorr','mean':'0.0','sigma':'1.0'},
                {'name':'MaterialOuterBarrel','title':'MaterialOuterBarrel','type':'signal_shape','mode':'scalesCorr','mean':'0.0','sigma':'1.0'},
                {'name':'MaterialForward','title':'MaterialForward','type':'signal_shape','mode':'scalesCorr','mean':'0.0','sigma':'1.0'},
                {'name':'FNUFEE','title':'FNUFEE','type':'signal_shape','mode':'scalesCorr','mean':'0.0','sigma':'1.0'},
                {'name':'FNUFEB','title':'FNUFEB','type':'signal_shape','mode':'scalesCorr','mean':'0.0','sigma':'1.0'},
                {'name':'HighR9EBPhi','title':'HighR9EBPhi','type':'signal_shape','mode':'smears','mean':'0.0','sigma':'1.0'},
                {'name':'HighR9EBRho','title':'HighR9EBRho','type':'signal_shape','mode':'smears','mean':'0.0','sigma':'1.0'},
                {'name':'HighR9EEPhi','title':'HighR9EEPhi','type':'signal_shape','mode':'smears','mean':'0.0','sigma':'1.0'},
                {'name':'HighR9EERho','title':'HighR9EERho','type':'signal_shape','mode':'smears','mean':'0.0','sigma':'1.0'},
                {'name':'LowR9EBPhi','title':'LowR9EBPhi','type':'signal_shape','mode':'smears','mean':'0.0','sigma':'1.0'},
                {'name':'LowR9EBRho','title':'LowR9EBRho','type':'signal_shape','mode':'smears','mean':'0.0','sigma':'1.0'},
                {'name':'LowR9EEPhi','title':'LowR9EEPhi','type':'signal_shape','mode':'smears','mean':'0.0','sigma':'1.0'},
                {'name':'LowR9EERho','title':'LowR9EERho','type':'signal_shape','mode':'smears','mean':'0.0','sigma':'1.0'}
              ]
