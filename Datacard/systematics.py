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
                {'name':'THU_GG2H_Yield','title':'THU_GG2H_Yield','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                {'name':'THU_GG2H_Res','title':'THU_GG2H_Res','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                {'name':'THU_GG2H_Mig01','title':'THU_GG2H_Mig01','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                {'name':'THU_GG2H_Mig12','title':'THU_GG2H_Mig12','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                {'name':'THU_GG2H_Boosted','title':'THU_GG2H_Boosted','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                {'name':'THU_GG2H_PTH200','title':'THU_GG2H_PTH200','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                {'name':'THU_GG2H_PTH300','title':'THU_GG2H_PTH300','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                {'name':'THU_GG2H_PTH450','title':'THU_GG2H_PTH450','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                {'name':'THU_GG2H_PTH650','title':'THU_GG2H_PTH650','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                {'name':'THU_GG2H_0J_PTH10','title':'THU_GG2H_0J_PTH10','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                {'name':'THU_GG2H_1J_PTH60','title':'THU_GG2H_1J_PTH60','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                {'name':'THU_GG2H_1J_PTH120','title':'THU_GG2H_1J_PTH120','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                {'name':'THU_GG2H_GE2J_PTH60','title':'THU_GG2H_GE2J_PTH60','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                {'name':'THU_GG2H_GE2J_PTH120','title':'THU_GG2H_GE2J_PTH120','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                {'name':'THU_GG2H_GE2J_MJJ350','title':'THU_GG2H_GE2J_MJJ350','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                {'name':'THU_GG2H_GE2J_MJJ700','title':'THU_GG2H_GE2J_MJJ700','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                {'name':'THU_GG2H_GE2J_LOWMJJ_PTHJJ25','title':'THU_GG2H_GE2J_LOWMJJ_PTHJJ25','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                {'name':'THU_GG2H_GE2J_HIGHMJJ_PTHJJ25','title':'THU_GG2H_GE2J_HIGHMJJ_PTHJJ25','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh_stxs.json'},
                {'name':'THU_QQ2HQQ_Yield','title':'THU_QQ2HQQ_Yield','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh_stxs.json'},
                {'name':'THU_QQ2HQQ_PTH200','title':'THU_QQ2HQQ_PTH200','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh_stxs.json'},
                {'name':'THU_QQ2HQQ_MJJ60','title':'THU_QQ2HQQ_MJJ60','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh_stxs.json'},
                {'name':'THU_QQ2HQQ_MJJ120','title':'THU_QQ2HQQ_MJJ120','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh_stxs.json'},
                {'name':'THU_QQ2HQQ_MJJ350','title':'THU_QQ2HQQ_MJJ350','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh_stxs.json'},
                {'name':'THU_QQ2HQQ_MJJ700','title':'THU_QQ2HQQ_MJJ700','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh_stxs.json'},
                {'name':'THU_QQ2HQQ_MJJ1000','title':'THU_QQ2HQQ_MJJ1000','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh_stxs.json'},
                {'name':'THU_QQ2HQQ_MJJ1500','title':'THU_QQ2HQQ_MJJ1500','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh_stxs.json'},
                {'name':'THU_QQ2HQQ_PTHJJ25','title':'THU_QQ2HQQ_PTHJJ25','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh_stxs.json'},
                {'name':'THU_QQ2HQQ_JET01','title':'THU_QQ2HQQ_JET01','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh_stxs.json'},
                {'name':'THU_WHLEP_inc','title':'THU_WHLEP_inc','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_whlep_stxs.json'},
                {'name':'THU_WHLEP_mig75','title':'THU_WHLEP_mig75','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_whlep_stxs.json'},
                {'name':'THU_WHLEP_mig150','title':'THU_WHLEP_mig150','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_whlep_stxs.json'},
                {'name':'THU_WHLEP_mig250','title':'THU_WHLEP_mig250','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_whlep_stxs.json'},
                {'name':'THU_WHLEP_mig01','title':'THU_WHLEP_mig01','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_whlep_stxs.json'},
                {'name':'THU_ZHLEP_inc','title':'THU_ZHLEP_inc','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_zhlep_stxs.json'},
                {'name':'THU_ZHLEP_mig75','title':'THU_ZHLEP_mig75','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_zhlep_stxs.json'},
                {'name':'THU_ZHLEP_mig150','title':'THU_ZHLEP_mig150','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_zhlep_stxs.json'},
                {'name':'THU_ZHLEP_mig250','title':'THU_ZHLEP_mig250','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_zhlep_stxs.json'},
                {'name':'THU_ZHLEP_mig01','title':'THU_ZHLEP_mig01','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_zhlep_stxs.json'},
                {'name':'THU_GGZHLEP_inc','title':'THU_GGZHLEP_inc','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggzhlep_stxs.json'},
                {'name':'THU_GGZHLEP_mig75','title':'THU_GGZHLEP_mig75','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggzhlep_stxs.json'},
                {'name':'THU_GGZHLEP_mig150','title':'THU_GGZHLEP_mig150','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggzhlep_stxs.json'},
                {'name':'THU_GGZHLEP_mig250','title':'THU_GGZHLEP_mig250','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggzhlep_stxs.json'},
                {'name':'THU_GGZHLEP_mig01','title':'THU_GGZHLEP_mig01','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggzhlep_stxs.json'},
                {'name':'THU_TTH_Yield','title':'THU_TTH_Yield','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_tth_stxs.json'},
                {'name':'THU_TTH_mig60','title':'THU_TTH_mig60','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_tth_stxs.json'},
                {'name':'THU_TTH_mig120','title':'THU_TTH_mig120','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_tth_stxs.json'},
                {'name':'THU_TTH_mig200','title':'THU_TTH_mig200','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_tth_stxs.json'},
                {'name':'THU_TTH_mig300','title':'THU_TTH_mig300','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_tth_stxs.json'},                
                {'name':'QCDscale_tHq','title':'QCDscale_tHq','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_thq.json'},
                {'name':'QCDscale_tHW','title':'QCDscale_tHW','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_thw.json'},
                {'name':'QCDscale_bbH','title':'QCDscale_bbH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_bbh.json'},
                #{'name':'QCDscale_ggH','title':'QCDscale_ggH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh.json'},
                #{'name':'QCDscale_qqH','title':'QCDscale_qqH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh.json'},
                #{'name':'QCDscale_VH','title':'QCDscale_VH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_vh.json'}, # Note: VH had components accounted for in THU_QQ2HQQ_*, set to 1 in json
                #{'name':'QCDscale_ggZH','title':'QCDscale_ggZH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggzh.json'}, # Note: ggZH lep components are accounted for in THU_GGZHLEP i.e. this only covers the ggZH had component
                #{'name':'QCDscale_ttH','title':'QCDscale_ttH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_tth.json'},
                #{'name':'QCDscale_tHq','title':'QCDscale_tHq','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_thq.json'},
                #{'name':'QCDscale_tHW','title':'QCDscale_tHW','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_thw.json'},
                #{'name':'QCDscale_bbH','title':'QCDscale_bbH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_bbh.json'},
                #{'name':'pdf_Higgs_ggH','title':'pdf_Higgs_ggH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh.json'},
                #{'name':'pdf_Higgs_qqH','title':'pdf_Higgs_qqH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh.json'},
                #{'name':'pdf_Higgs_VH','title':'pdf_Higgs_VH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_vh.json'},
                #{'name':'pdf_Higgs_ggZH','title':'pdf_Higgs_ggZH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggzh.json'},
                #{'name':'pdf_Higgs_ttH','title':'pdf_Higgs_ttH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_tth.json'},
                #{'name':'pdf_Higgs_tHq','title':'pdf_Higgs_tHq','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_thq.json'},
                #{'name':'pdf_Higgs_tHW','title':'pdf_Higgs_tHW','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_thw.json'},
                #{'name':'alphaS_ggH','title':'alphaS_ggH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh.json'},
                #{'name':'alphaS_qqH','title':'alphaS_qqH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh.json'},
                #{'name':'alphaS_VH','title':'alphaS_VH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_vh.json'},
                #{'name':'alphaS_ggZH','title':'alphaS_ggZH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggzh.json'},
                #{'name':'alphaS_ttH','title':'alphaS_ttH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_tth.json'},
                #{'name':'alphaS_tHq','title':'alphaS_tHq','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_thq.json'},
                #{'name':'alphaS_tHW','title':'alphaS_tHW','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_thw.json'},

                # Shape uncertainties: enter direct XS measurements
                # Shape uncertainties: enter direct XS measurements
                # Scale weights grouping is defined in makeDatacard.py
                # For some reason, the name is saved only as `Scal`, not `Scale`, do not ask me why
                # Comment out the nominal weight here as it does not contain any `tiers`, so it would fail in `makeDatacard.py``
                # The scheme below is valid for v13, you need to explicitly check the nanoAOD documentation to validate your setup
                #{'name':'weight_LHEScal_0','title':'CMS_hgg_scaleWeight_0','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']}, 
                #{'name':'weight_LHEScal_1','title':'CMS_hgg_scaleWeight_1','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']},
                #{'name':'weight_LHEScal_2','title':'CMS_hgg_scaleWeight_2','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']}, #Unphysical
                #{'name':'weight_LHEScal_3','title':'CMS_hgg_scaleWeight_3','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']},
                #{'name':'weight_LHEScal_4','title':'CMS_hgg_scaleWeight_4','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']}, # nominal weight
                #{'name':'weight_LHEScal_5','title':'CMS_hgg_scaleWeight_5','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']}, 
                #{'name':'weight_LHEScal_6','title':'CMS_hgg_scaleWeight_6','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']}, #Unphysical
                #{'name':'weight_LHEScal_7','title':'CMS_hgg_scaleWeight_7','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']},
                #{'name':'weight_LHEScal_8','title':'CMS_hgg_scaleWeight_8','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']},
                {'name':'weight_AlphaS','title':'pdf_alphas','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']}, # DO WE WANT TO FACTOR OUT NORM EFFECTS HERE
                {'name':'weight_PS_ISR','title':'ps_isr','type':'factory','prior':'lnN','correlateAcrossYears':1, 'tiers':['default']},
                {'name':'weight_PS_FSR','title':'ps_fsr','type':'factory','prior':'lnN','correlateAcrossYears':1, 'tiers':['default']}

              ]

# PDF weight
#for i in range(1,101): theory_systematics.append( {'name':'weight_LHEPd_%g'%i, 'title':'CMS_hgg_pdfWeight_%g'%i, 'type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']} )

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# EXPERIMENTAL SYSTEMATICS
# correlateAcrossYears = 0 : no correlation
# correlateAcrossYears = 1 : fully correlated
# correlateAcrossYears = -1 : partially correlated

experimental_systematics = [
                 {'name':'lumi_1','title':'lumi_13p6TeV_222324','type':'constant','prior':'lnN','correlateAcrossYears':-1,'value':{'2022preEE':'1.0138', '2022postEE':'1.0138', '2023preBPix':'1.0017', '2023postBPix':'1.0017', '2024':'1.0020'}},
                 {'name':'lumi_2','title':'lumi_13p6TeV_2324','type':'constant','prior':'lnN','correlateAcrossYears':-1,'value':{'2022preEE':'-', '2022postEE':'-', '2023preBPix':'1.0127', '2023postBPix':'1.0127', '2024':'1.0068'}},
                 {'name':'lumi_3','title':'lumi_13p6TeV_24','type':'constant','prior':'lnN','correlateAcrossYears':-1,'value':{'2022preEE':'-', '2022postEE':'-', '2023preBPix':'-', '2023postBPix':'-', '2024':'1.0144'}},
                 # Shape based
                {'name':'Electron_Scale_EGM','title':'CMS_scale_e_13p6TeV','type':'factory','prior':'lnN','correlateAcrossYears':1},
                {'name':'Electron_Smearing_EGM','title':'CMS_res_e_13p6TeV','type':'factory','prior':'lnN','correlateAcrossYears':1},
                {'name':'energyErrShift','title':'CMS_HIG25020_energyErrShift','type':'factory','prior':'lnN','correlateAcrossYears':1},
                {'name':'jec_syst_Regrouped_Total','title':'CMS_scale_j','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'jer_syst','title':'CMS_res_j_13p6TeV','type':'factory','prior':'lnN','correlateAcrossYears':1},
                {'name':'MET_unclusteredEnergy','title':'CMS_scale_met_unclustered_energy','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'MuonScale','title':'CMS_scale_m_13p6TeV','type':'factory','prior':'lnN','correlateAcrossYears':1},
                {'name':'MuonResolution','title':'CMS_res_m_13p6TeV','type':'factory','prior':'lnN','correlateAcrossYears':1},
                {'name':'PhotonIDMVAShape','title':'CMS_HIG25020_shape_g_id','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'Tau_EnergyScale','title':'CMS_scale_t_13p6TeV','type':'factory','prior':'lnN','correlateAcrossYears':1},
                # Weight based
                {'name':'weight_ElectronIdLooseSF','title':'CMS_eff_e_id_13p6TeV','type':'factory','prior':'lnN','correlateAcrossYears':1},
                {'name':'weight_ElectronIdRecoSF','title':'CMS_eff_e_reco_13p6TeV','type':'factory','prior':'lnN','correlateAcrossYears':1},
                {'name':'weight_ElectronVetoSF','title':'CMS_eff_g_CSEV_13p6TeV','type':'factory','prior':'lnN','correlateAcrossYears':1},
                {'name':'weight_NUM_TightPFIso_DEN_MediumID','title':'CMS_eff_m_13p6TeV','type':'factory','prior':'lnN','correlateAcrossYears':1},
                {'name':'weight_Pileup','title':'CMS_pileup_13p6TeV','type':'factory','prior':'lnN','correlateAcrossYears':1},
                {'name':'weight_PreselSF','title':'CMS_eff_g_PreselSF_13p6TeV','type':'factory','prior':'lnN','correlateAcrossYears':1},
                {'name':'weight_TriggerSF','title':'CMS_eff_g_trigger','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'weight_Tau_ID','title':'CMS_eff_t_13p6TeV','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'weight_bTagSF_sys_cferr1','title':'CMS_btag_fullShape_cferr1','type':'factory','prior':'lnN','correlateAcrossYears':1},
                {'name':'weight_bTagSF_sys_cferr2','title':'CMS_btag_fullShape_cferr2','type':'factory','prior':'lnN','correlateAcrossYears':1},
                {'name':'weight_bTagSF_sys_hf','title':'CMS_btag_fullShape_hf','type':'factory','prior':'lnN','correlateAcrossYears':1},
                {'name':'weight_bTagSF_sys_hfstats1','title':'CMS_btag_fullShape_hfstats1','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'weight_bTagSF_sys_hfstats2','title':'CMS_btag_fullShape_hfstats2','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'weight_bTagSF_sys_jes','title':'CMS_btag_jes','type':'factory','prior':'lnN','correlateAcrossYears':1},
                {'name':'weight_bTagSF_sys_lf','title':'CMS_btag_fullShape_lf','type':'factory','prior':'lnN','correlateAcrossYears':1},
                {'name':'weight_bTagSF_sys_lfstats1','title':'CMS_btag_fullShape_lfstats1','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'weight_bTagSF_sys_lfstats2','title':'CMS_btag_fullShape_lfstats2','type':'factory','prior':'lnN','correlateAcrossYears':0}
              ]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Shape nuisances: effect encoded in signal model
# mode = (other,scalesGlobal,scales,scalesCorr,smears): match the definition in the signal models

signal_shape_systematics = [
                #{'name':'deltafracright','title':'deltafracright','type':'signal_shape','mode':'other','mean':'0.0','sigma':'0.02'},
                # {'name':'ScaleEB_Zee','title':'CMS_HIG25020_scale_g_EB_zee','type':'signal_shape','mode':'scales','mean':'0.0','sigma':'1.0'},
                # {'name':'ScaleEB_Zmmg','title':'CMS_HIG25020_scale_g_EB_zmmg','type':'signal_shape','mode':'scales','mean':'0.0','sigma':'1.0'},
                # {'name':'ScaleEE_Zee','title':'CMS_HIG25020_scale_g_EE_zee','type':'signal_shape','mode':'scales','mean':'0.0','sigma':'1.0'},
                # {'name':'ScaleEE_Zmmg','title':'CMS_HIG25020_scale_g_EE_zmmg','type':'signal_shape','mode':'scales','mean':'0.0','sigma':'1.0'},
                # {'name':'Smearing','title':'CMS_HIG25020_res_g_zmmg','type':'signal_shape','mode':'smears','mean':'0.0','sigma':'1.0'},
                # {'name':'FNUF','title':'CMS_HIG25020_scale_g_fnuf_13p6TeV','type':'signal_shape','mode':'scalesCorr','mean':'0.0','sigma':'1.0'},
                # {'name':'Material','title':'CMS_HIG25020_scale_g_material_13p6TeV','type':'signal_shape','mode':'scalesCorr','mean':'0.0','sigma':'1.0'},
                {'name':'ScaleEB_Zee','title':'ScaleEB_Zee','type':'signal_shape','mode':'scales','mean':'0.0','sigma':'1.0'},
                {'name':'ScaleEB_Zmmg','title':'ScaleEB_Zmmg','type':'signal_shape','mode':'scales','mean':'0.0','sigma':'1.0'},
                {'name':'ScaleEE_Zee','title':'ScaleEE_Zee','type':'signal_shape','mode':'scales','mean':'0.0','sigma':'1.0'},
                {'name':'ScaleEE_Zmmg','title':'ScaleEE_Zmmg','type':'signal_shape','mode':'scales','mean':'0.0','sigma':'1.0'},
                {'name':'Smearing','title':'Smearing','type':'signal_shape','mode':'smears','mean':'0.0','sigma':'1.0'},
                {'name':'FNUF','title':'FNUF','type':'signal_shape','mode':'scalesCorr','mean':'0.0','sigma':'1.0'},
                {'name':'Material','title':'Material','type':'signal_shape','mode':'scalesCorr','mean':'0.0','sigma':'1.0'}
                #{'name':'Smearing','title':'Smearing','type':'signal_shape','mode':'smears','mean':'0.0','sigma':'1.0'},
                #{'name':'NonLinearity','title':'NonLinearity','type':'signal_shape','mode':'scalesGlobal','mean':'0.0','sigma':'0.002'},
                #{'name':'Geant4','title':'Geant4','type':'signal_shape','mode':'scalesGlobal','mean':'0.0','sigma':'0.0005'}
              ]
