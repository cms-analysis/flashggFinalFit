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
                {'name':'THU_ttH_Yield','title':'THU_ttH_Yield','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_tth_stxs.json'},
                {'name':'THU_ttH_mig60','title':'THU_ttH_mig60','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_tth_stxs.json'},
                {'name':'THU_ttH_mig120','title':'THU_ttH_mig120','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_tth_stxs.json'},
                {'name':'THU_ttH_mig200','title':'THU_ttH_mig200','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_tth_stxs.json'},
                {'name':'THU_ttH_mig300','title':'THU_ttH_mig300','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_tth_stxs.json'},
                
                {'name':'QCDscale_ggZH','title':'QCDscale_ggZH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggzh.json'}, # Note: ggZH lep components are accounted for in THU_ggZH i.e. this only covers the ggZH had component
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

                # # Shape uncertainties: enter direct XS measurements
                # # Shape uncertainties: enter direct XS measurements
                # # Scale weights grouping is defined in makeDatacard.py
                # # For some reason, the name is saved only as `Scal`, not `Scale`, do not ask me why
                # # Comment out the nominal weight here as it does not contain any `tiers`, so it would fail in `makeDatacard.py``
                # # The scheme below is valid for v13, you need to explicitly check the nanoAOD documentation to validate your setup
                # #{'name':'weight_LHEScal_0','title':'CMS_hgg_scaleWeight_0','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']}, 
                # #{'name':'weight_LHEScal_1','title':'CMS_hgg_scaleWeight_1','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']},
                # #{'name':'weight_LHEScal_2','title':'CMS_hgg_scaleWeight_2','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']}, #Unphysical
                # #{'name':'weight_LHEScal_3','title':'CMS_hgg_scaleWeight_3','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']},
                # #{'name':'weight_LHEScal_4','title':'CMS_hgg_scaleWeight_4','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']}, # nominal weight
                # #{'name':'weight_LHEScal_5','title':'CMS_hgg_scaleWeight_5','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']}, 
                # #{'name':'weight_LHEScal_6','title':'CMS_hgg_scaleWeight_6','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']}, #Unphysical
                # #{'name':'weight_LHEScal_7','title':'CMS_hgg_scaleWeight_7','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']},
                # #{'name':'weight_LHEScal_8','title':'CMS_hgg_scaleWeight_8','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']},
                # {'name':'weight_AlphaS','title':'CMS_hgg_AlphaS','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']},
                {'name':'weight_PS_ISR','title':'CMS_hgg_PS_ISR','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']},
                {'name':'weight_PS_FSR','title':'CMS_hgg_PS_FSR','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']}

              ]

# PDF weight
#for i in range(1,101): theory_systematics.append( {'name':'weight_LHEPd_%g'%i, 'title':'CMS_hgg_pdfWeight_%g'%i, 'type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']} )

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# EXPERIMENTAL SYSTEMATICS
# correlateAcrossYears = 0 : no correlation
# correlateAcrossYears = 1 : fully correlated
# correlateAcrossYears = -1 : partially correlated

experimental_systematics = [
                {'name':'lumi_13p6TeV_2022','title':'lumi_13p6TeV_2022','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':"1.014"},
                #  {'name':'weight_Dummy','title':'CMS_hgg_DummyWeight','type':'factory','prior':'lnN','correlateAcrossYears':1},
               
                {'name':'weight_Pileup','title':'CMS_hgg_PileupWeight','type':'factory','prior':'lnN','correlateAcrossYears':1},
                {'name':'weight_TriggerSF','title':'CMS_hgg_TriggerWeight','type':'factory','prior':'lnN','correlateAcrossYears':1},
                {'name':'weight_ElectronVetoSF','title':'CMS_hgg_ElectronVetoSF','type':'factory','prior':'lnN','correlateAcrossYears':1},
                {'name':'weight_PreselSF','title':'CMS_hgg_PreselSF','type':'factory','prior':'lnN','correlateAcrossYears':1},
                
                {'name':'weight_SF_photon_ID','title':'CMS_hgg_phoIdMva','type':'factory','prior':'lnN','correlateAcrossYears':1},
                 {'name':'energyErrShift','title':'CMS_hgg_SigmaEOverEShift','type':'factory','prior':'lnN','correlateAcrossYears':1},
                {'name':'jec_syst_Total','title':'CMS_jec','type':'factory','prior':'lnN','correlateAcrossYears':0} ]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Shape nuisances: effect encoded in signal model
# mode = (other,scalesGlobal,scales,scalesCorr,smears): match the definition in the signal models

signal_shape_systematics = [
#                 # {'name':'deltafracright','title':'deltafracright','type':'signal_shape','mode':'other','mean':'0.0','sigma':'0.02'},
#                 # {'name':'Scale','title':'Scale','type':'signal_shape','mode':'scales','mean':'0.0','sigma':'1.0'},
#                 # {'name':'Smearing','title':'Smearing','type':'signal_shape','mode':'smears','mean':'0.0','sigma':'1.0'},
#                 # #{'name':'NonLinearity','title':'NonLinearity','type':'signal_shape','mode':'scalesGlobal','mean':'0.0','sigma':'0.002'},
#                 #{'name':'Geant4','title':'Geant4','type':'signal_shape','mode':'scalesGlobal','mean':'0.0','sigma':'0.0005'}
#               ]

# signal_shape_systematics = [

                {'name':'Material','title':'Material','type':'signal_shape','mode':'scalesCorr','mean':'0.0','sigma':'1.0','correlateAcrossYears':1},
                {'name':'FNUF','title':'FNUF','type':'signal_shape','mode':'scalesCorr','mean':'0.0','sigma':'1.0','correlateAcrossYears':1},
                {'name':'ScaleEB2G_IJazZ','title':'ScaleEB2G_IJazZ','type':'signal_shape','mode':'scales','mean':'0.0','sigma':'1.0','correlateAcrossYears':0},
                {'name':'ScaleEE2G_IJazZ','title':'ScaleEE2G_IJazZ','type':'signal_shape','mode':'scales','mean':'0.0','sigma':'1.0','correlateAcrossYears':0},
                {'name':'Smearing2G_IJazZ','title':'Smearing2G_IJazZ','type':'signal_shape','mode':'scales','mean':'0.0','sigma':'1.0','correlateAcrossYears':0},

  
]