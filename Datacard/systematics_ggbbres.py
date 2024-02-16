# Python file to store systematics: for STXS analysis

# Comment out all nuisances that you do not want to include

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

# correlateAcrossYears = 0 : no correlation
# correlateAcrossYears = 1 : fully correlated
# correlateAcrossYears = -1 : partially correlated

# THEORY SYSTEMATICS:

theory_systematics = [
  #{'name':'BR_hgg','title':'BR_hgg','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':"0.98/1.021"},
  #{'name':'QCDscale_ggH','title':'QCDscale_ggH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'0.931/1.047'},
  #{'name':'QCDscale_qqH','title':'QCDscale_qqH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'0.997/1.004'},
  #{'name':'QCDscale_VH','title':'QCDscale_VH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'0.993/1.005'},
  #{'name':'QCDscale_ttH','title':'QCDscale_ttH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'0.908/1.058'},
  #{'name':'pdf_Higgs_ggH','title':'pdf_Higgs_ggH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'1.019'},
  #{'name':'pdf_Higgs_qqH','title':'pdf_Higgs_qqH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'1.021'},
  #{'name':'pdf_Higgs_VH','title':'pdf_Higgs_VH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'1.017'},
  #{'name':'pdf_Higgs_ttH','title':'pdf_Higgs_ttH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'1.030'},
  #{'name':'alphaS_ggH','title':'alphaS_ggH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'1.026'},
  #{'name':'alphaS_qqH','title':'alphaS_qqH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'1.005'},
  #{'name':'alphaS_VH','title':'alphaS_VH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'1.009'},
  #{'name':'alphaS_ttH','title':'alphaS_ttH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'1.020'}
]
# PDF weight
#for i in range(1,60): theory_systematics.append( {'name':'pdfWeight_%g'%i, 'title':'CMS_hgg_pdfWeight_%g'%i, 'type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']} )

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# EXPERIMENTAL SYSTEMATICS

experimental_systematics = [
                {'name':'lumi_13TeV_','title':'lumi_13TeV','type':'constant','prior':'lnN','correlateAcrossYears':0,'value':{'2016':'1.010','2017':'1.020','2018':'1.015'}},
                {'name':'lumi_13TeV_correlated','title':'lumi_13TeV_correlated','type':'constant','prior':'lnN','correlateAcrossYears':-1,'value':{'2016':'1.006','2017':'1.009','2018':'1.020'}},
                {'name':'lumi_13TeV_1718','title':'lumi_13TeV_1718','type':'constant','prior':'lnN','correlateAcrossYears':-1,'value':{'2016':'-','2017':'1.006','2018':'1.002'}},
                {'name':'L1pref','title':'CMS_hgg_L1_prefiring_sf','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'electronVetoSF','title':'CMS_hgg_electron_veto_sf','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'triggerSF','title':'CMS_hgg_trigger_sf','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'phoMVAIDWP90SF','title':'CMS_photon_id_sf','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'JESUnc7','title':'CMS_scale_j_EC2_2016_2017_2018','type':'factory','prior':'lnN','correlateAcrossYears':1},
                {'name':'JESUnc8','title':'CMS_scale_j_EC2','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'JESUnc9','title':'CMS_scale_j_HF_2016_2017_2018','type':'factory','prior':'lnN','correlateAcrossYears':1},
                {'name':'JESUnc10','title':'CMS_scale_j_HF','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'bTagSF2','title':'CMS_btag_hf_2016_2017_2018','type':'factory','prior':'lnN','correlateAcrossYears':1},
                {'name':'bTagSF3','title':'CMS_btag_hfstats1','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'bTagSF4','title':'CMS_btag_hfstats2','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'bTagSF5','title':'CMS_btag_lf_2016_2017_2018','type':'factory','prior':'lnN','correlateAcrossYears':1},
                {'name':'bTagSF6','title':'CMS_btag_lfstats1','type':'factory','prior':'lnN','correlateAcrossYears':0},
                {'name':'bTagSF7','title':'CMS_btag_lfstats2','type':'factory','prior':'lnN','correlateAcrossYears':0}
                {'name':'photon_presel_sf_Diphoton_Photon','title':'CMS_hgg_presel_sf','type':'factory','prior':'lnN','correlateAcrossYears':0}
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Shape nuisances: effect encoded in signal model
# mode = (other,scalesGlobal,scales,scalesCorr,smears): match the definition in the signal models

signal_shape_systematics = [
                {'name':'fnufUnc','title':'funf','type':'signal_shape','mode':'scalesCorr','mean':'0.0','sigma':'1.0'},
                {'name':'materialUnc','title':'material','type':'signal_shape','mode':'scalesCorr','mean':'0.0','sigma':'1.0'},
                {'name':'PhoScaleUnc','title':'MCSmear','type':'signal_shape','mode':'smears','mean':'0.0','sigma':'1.0'},
                {'name':'PhoSmearUnc','title':'MCScale','type':'signal_shape','mode':'scales','mean':'0.0','sigma':'1.0'},
                {'name':'PUWeight','title':'pileup','type':'signal_shape','mode':'scales','mean':'0.0','sigma':'1.0'},
                {'name':'JESUnc2','title':'scale_j_absolute','type':'signal_shape','mode':'scalesCorr','mean':'0.0','sigma':'1.0'},
                {'name':'JESUnc3','title':'scale_j_absolute','type':'signal_shape','mode':'scales','mean':'0.0','sigma':'1.0'},
                {'name':'JESUnc4','title':'scale_j_flavorQCD','type':'signal_shape','mode':'scalesCorr','mean':'0.0','sigma':'1.0'},
                {'name':'JESUnc5','title':'scale_j_BBEC1','type':'signal_shape','mode':'scalesCorr','mean':'0.0','sigma':'1.0'},
                {'name':'JESUnc6','title':'scale_j_BBEC1','type':'signal_shape','mode':'scales','mean':'0.0','sigma':'1.0'},
                {'name':'JESUnc11','title':'scale_j_relativeBal','type':'signal_shape','mode':'scalesCorr','mean':'0.0','sigma':'1.0'},
                {'name':'JESUnc12','title':'scale_j_relativeSample','type':'signal_shape','mode':'scales','mean':'0.0','sigma':'1.0'},
                {'name':'bTagSF8','title':'btag_cferr1','type':'signal_shape','mode':'scalesCorr','mean':'0.0','sigma':'1.0'},
                {'name':'bTagSF9','title':'btag_cferr2','type':'signal_shape','mode':'scalesCorr','mean':'0.0','sigma':'1.0'},
                {'name':'JERUnc','title':'res_j','type':'signal_shape','mode':'scales','mean':'0.0','sigma':'1.0'},
]
