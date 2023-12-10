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
  {'name':'BR_hgg','title':'BR_hgg','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':"0.98/1.021"},
  {'name':'QCDscale_ggH','title':'QCDscale_ggH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'0.931/1.047'},
  {'name':'QCDscale_qqH','title':'QCDscale_qqH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'0.997/1.004'},
  {'name':'QCDscale_VH','title':'QCDscale_VH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'0.993/1.005'},
  {'name':'QCDscale_ttH','title':'QCDscale_ttH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'0.908/1.058'},
  {'name':'pdf_Higgs_ggH','title':'pdf_Higgs_ggH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'1.019'},
  {'name':'pdf_Higgs_qqH','title':'pdf_Higgs_qqH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'1.021'},
  {'name':'pdf_Higgs_VH','title':'pdf_Higgs_VH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'1.017'},
  {'name':'pdf_Higgs_ttH','title':'pdf_Higgs_ttH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'1.030'},
  {'name':'alphaS_ggH','title':'alphaS_ggH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'1.026'},
  {'name':'alphaS_qqH','title':'alphaS_qqH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'1.005'},
  {'name':'alphaS_VH','title':'alphaS_VH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'1.009'},
  {'name':'alphaS_ttH','title':'alphaS_ttH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'1.020'}
               ]
# PDF weight
#for i in range(1,60): theory_systematics.append( {'name':'pdfWeight_%g'%i, 'title':'CMS_hgg_pdfWeight_%g'%i, 'type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']} )

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# EXPERIMENTAL SYSTEMATICS
# correlateAcrossYears = 0 : no correlation
# correlateAcrossYears = 1 : fully correlated
# correlateAcrossYears = -1 : partially correlated

experimental_systematics = [
                # Updated luminosity partial-correlation scheme: 13/5/21 (recommended simplified nuisances)
                {'name':'lumi_13TeV_','title':'lumi_13TeV','type':'constant','prior':'lnN','correlateAcrossYears':0,'value':{'2016':'1.010','2017':'1.020','2018':'1.015'}},
                {'name':'lumi_13TeV_correlated','title':'lumi_13TeV_correlated','type':'constant','prior':'lnN','correlateAcrossYears':-1,'value':{'2016':'1.006','2017':'1.009','2018':'1.020'}},
                {'name':'lumi_13TeV_1718','title':'lumi_13TeV_1718','type':'constant','prior':'lnN','correlateAcrossYears':-1,'value':{'2016':'-','2017':'1.006','2018':'1.002'}},
                {'name':'JER','title':'CMS_res_j','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'JES','title':'CMS_scale_j','type':'factory','prior':'lnN','correlateAcrossYears':0},
                #{'name':'MET_JER','title':'CMS_res_met','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'MET_JES','title':'CMS_scale_met','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'MET_Unclustered','title':'CMS_met_unclustered','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'L1_prefiring_sf','title':'CMS_hgg_L1_prefiring_sf','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'trigger_sf','title':'CMS_hgg_trigger_sf','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'Muon_pt','title':'CMS_scale_m','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'Tau_pt','title':'CMS_scale_t','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'electron_id_sf_SelectedElectron','title':'CMS_electron_id_sf','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'electron_veto_sf_Diphoton_Photon','title':'CMS_hgg_electron_veto_sf','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'muon_id_sfSTAT_SelectedMuon','title':'CMS_muon_id_sfSYS','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'muon_id_sfSYS_SelectedMuon','title':'CMS_muon_iso_sfSTAT','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'muon_iso_sfSTAT_SelectedMuon','title':'CMS_muon_iso_sfSTAT','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'muon_iso_sfSYS_SelectedMuon','title':'CMS_muon_iso_sfSYS','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'photon_id_sf_Diphoton_Photon','title':'CMS_photon_id_sf','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'photon_presel_sf_Diphoton_Photon','title':'CMS_hgg_presel_sf','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'tau_idDeepTauVSe_sf_AnalysisTau','title':'CMS_tau_idDeepTauVSe_sf','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'tau_idDeepTauVSjet_sf_AnalysisTau','title':'CMS_tau_idDeepTauVSjet_sf','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'tau_idDeepTauVSmu_sf_AnalysisTau','title':'CMS_tau_idDeepTauVSmu_sf','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'btag_deepjet_sf_SelectedJet_cferr1','title':'CMS_btag_cferr1_2016_2017_2018','type':'factory','prior':'lnN','correlateAcrossYears':-1},
                {'name':'btag_deepjet_sf_SelectedJet_cferr2','title':'CMS_btag_cferr2_2016_2017_2018','type':'factory','prior':'lnN','correlateAcrossYears':-1},
                {'name':'btag_deepjet_sf_SelectedJet_hf','title':'CMS_btag_HF_2016_2017_2018','type':'factory','prior':'lnN','correlateAcrossYears':-1},
                {'name':'btag_deepjet_sf_SelectedJet_hfstats1','title':'CMS_btag_hfstats1','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'btag_deepjet_sf_SelectedJet_hfstats2','title':'CMS_btag_hfstats2','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'btag_deepjet_sf_SelectedJet_jes','title':'CMS_btag_jes','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'btag_deepjet_sf_SelectedJet_lf','title':'CMS_btag_LF_2016_2017_2018','type':'factory','prior':'lnN','correlateAcrossYears':-1},
                {'name':'btag_deepjet_sf_SelectedJet_lfstats1','title':'CMS_btag_lfstats1','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'btag_deepjet_sf_SelectedJet_lfstats2','title':'CMS_btag_lfstats2','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'puWeight','title':'CMS_pileup','type':'factory','prior':'lnN','correlateAcrossYears':0}
              ]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Shape nuisances: effect encoded in signal model
# mode = (other,scalesGlobal,scales,scalesCorr,smears): match the definition in the signal models

signal_shape_systematics = [
                {'name':'funf','title':'funf','type':'signal_shape','mode':'scalesCorr','mean':'0.0','sigma':'1.0'},
                {'name':'material','title':'material','type':'signal_shape','mode':'scalesCorr','mean':'0.0','sigma':'1.0'},
                {'name':'MCSmear_smear','title':'MCSmear_smear','type':'signal_shape','mode':'smears','mean':'0.0','sigma':'1.0'},
                {'name':'MCScale_scale','title':'MCScale_scale','type':'signal_shape','mode':'scales','mean':'0.0','sigma':'1.0'},
              ]
