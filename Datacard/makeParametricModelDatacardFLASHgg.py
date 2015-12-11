#!/usr/bin/env python

# Script adapted from original by Matt Kenzie.
# Used for Dry Run of Dec 2015 Hgg analysis.

###############################################################################
## IMPORTS ####################################################################
###############################################################################
import os,sys,copy
###############################################################################

###############################################################################
## OPTION PARSING  ############################################################
###############################################################################
from optparse import OptionParser
parser = OptionParser()
parser.add_option("-i","--infilename", help="Input file (binned signal from flashgg)")
parser.add_option("-o","--outfilename",default="cms_hgg_datacard.txt",help="Name of card to print (default: %default)")
parser.add_option("-p","--procs",default="ggh,vbf,wh,zh,tth",help="String list of procs (default: %default)")
parser.add_option("-c","--cats",default="UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,UntaggedTag_4,VBFTag_0,VBFTag_1,VBFTag_2",help="Flashgg Categories (default: %default)")
parser.add_option("--photonCatScales",default="HighR9EE,LowR9EE,HighR9EB,LowR9EB",help="String list of photon scale nuisance names - WILL NOT correlate across years (default: %default)")
parser.add_option("--photonCatScalesCorr",default="MaterialEBCentral,MaterialEBOuterEE,LightColl",help="String list of photon scale nuisance names - WILL correlate across years (default: %default)")
parser.add_option("--photonCatSmears",default="HighR9EE,LowR9EE,HighR9EBRho,LowR9EBRho,HighR9EBPhi,LowR9EBPhi",help="String list of photon smearing nuisance names - WILL NOT correlate across years (default: %default)")
parser.add_option("--photonCatSmearsCorr",default="",help="String list of photon smearing nuisance names - WILL correlate across years (default: %default)")
parser.add_option("--globalScales",default="NonLinearity:0.001",help="String list of global scale nuisances names with value separated by a \':\' - WILL NOT correlate across years (default: %default)")
parser.add_option("--globalScalesCorr",default="Geant4:0.0005",help="String list of global scale nuisances names with value separated by a \':\' - WILL correlate across years (default: %default)")
parser.add_option("--toSkip",default="",help="proc:cat which are to skipped e.g ggH:11,qqH:12 etc. (default: %default)")
#parser.add_option("--isCutBased",default=False,action="store_true") # hangover from globe, not needd
#parser.add_option("--isSpinModel",default=False,action="store_true")
parser.add_option("--isMultiPdf",default=False,action="store_true")
#parser.add_option("--isBinnedSignal",default=False,action="store_true")
#parser.add_option("--is2011",default=False,action="store_true")
#parser.add_option("--is2012",default=False,action="store_true")
parser.add_option("--simplePdfWeights",default=False,action="store_true",help="Condense pdfWeight systematics into 1 line instead of full shape systematic" )
parser.add_option("--scaleFactors",help="Scale factor for spin model pass as e.g. gg_grav:1.351,qq_grav:1.027")
parser.add_option("--quadInterpolate",type="int",default=0,help="Do a quadratic interpolation of flashgg templates back to 1 sigma from this sigma. 0 means off (default: %default)")
(options,args)=parser.parse_args()
###############################################################################

###############################################################################
## PARSE ROOT MACROS  #########################################################
###############################################################################
import ROOT as r
if options.quadInterpolate:
  r.gROOT.ProcessLine(".L quadInterpolate.C+g")
  from ROOT import quadInterpolate
r.gROOT.ProcessLine(".L $CMSSW_BASE/lib/$SCRAM_ARCH/libHiggsAnalysisCombinedLimit.so")
r.gROOT.ProcessLine(".L ../libLoopAll.so")
###############################################################################

###############################################################################
## FILE I/O ###################################################################
###############################################################################
inFile = r.TFile.Open(options.infilename)
outFile = open(options.outfilename,'w')
###############################################################################

###############################################################################
## PROCS HANDLING & DICT ######################################################
###############################################################################
# convert flashgg style to combine style process
combProc = {'ggH':'ggH','VBF':'qqH','ggh':'ggH','vbf':'qqH','wzh':'VH','wh':'WH','zh':'ZH','tth':'ttH','bkg_mass':'bkg_mass','gg_grav':'ggH_ALT','qq_grav':'qqbarH_ALT'}
flashggProc = {'ggH':'ggh','qqH':'vbf','VH':'wzh','WH':'wh','ZH':'zh','ttH':'tth','bkg_mass':'bkg_mass','ggH_ALT':'gg_grav','qqbarH_ALT':'qq_grav'}
procId = {'ggH':0,'qqH':-1,'VH':-2,'WH':-2,'ZH':-3,'ttH':-4,'ggH_ALT':-5,'qqbarH_ALT':-6,'bkg_mass':1}
bkgProcs = ['bkg_mass'] #what to treat as background
#Determine if VH or WZH
splitVH=False
if 'wzh'in options.procs.split(','):
  splitVH=False
if 'wh' in options.procs.split(',') and 'zh' in options.procs.split(','):
  splitVH=True
#split procs vector
options.procs += ',bkg_mass'
options.procs = [combProc[p] for p in options.procs.split(',')]
options.toSkip = options.toSkip.split(',')
###############################################################################

###############################################################################
## CATEGORISE TAGS FOR CONSIDERATION ##########################################
###############################################################################
#split cats
options.cats = options.cats.split(',')
# cat types
incCats     =[] #Untagged
dijetCats   =[] #VBF 
tthCats  =[]
tthLepCat  =[]
tthHadCat  =[]
vhHadCat    =[]
tightLepCat=[]
looseLepCat=[]
metCat=[]
#fill
for i in range(len(options.cats)):
  if "Untagged" in options.cats[i]:
    incCats.append(options.cats[i])
  if "VBF" in options.cats[i]:
    dijetCats.append(options.cats[i])
  if "TTHLeptonic" in options.cats[i]:
     tthLepCat.append(options.cats[i])
  if "TTHHadronic" in options.cats[i]:
     tthHadCat.append(options.cats[i])
  if "TTH" in options.cats[i]:
     tthCats.append(options.cats[i])
  if "VHHadronic" in options.cats[i]:
     vhHadCat.append(options.cats[i])
  if "VHTight" in options.cats[i]:
     tightLepCat.append(options.cats[i])
  if "VHLoose" in options.cats[i]:
     looseLepCat.append(options.cats[i])
  if "VHEt" in options.cats[i]:
     metCat.append(options.cats[i])
#summary 
print "[INFO] flashgg cats:"
print "--> incCats " , incCats
print "--> dijetCats " , dijetCats
print "--> tthLepCats " , tthCats
print "--> tthLepCats " , tthLepCat
print "--> tthHadCats " , tthHadCat
print "--> vhHadCats " , vhHadCat
print "--> tightLepCats " , tightLepCat
print "--> looseLepCats " , looseLepCat
print "--> metCat " , metCat
###############################################################################

###############################################################################
## PHOTON SMEAR/SCALE SYSTEMATICS ## ##########################################
###############################################################################
if options.photonCatScales=='': options.photonCatScales = []
else: options.photonCatScales = options.photonCatScales.split(',')
if options.photonCatScalesCorr=='': options.photonCatScalesCorr = []
else: options.photonCatScalesCorr = options.photonCatScalesCorr.split(',')
if options.photonCatSmears=='': options.photonCatSmears = []
else: options.photonCatSmears = options.photonCatSmears.split(',')
if options.photonCatSmearsCorr=='': options.photonCatSmearsCorr = []
else: options.photonCatSmearsCorr = options.photonCatSmearsCorr.split(',')
if options.globalScales=='': options.globalScales = []
else: options.globalScales = options.globalScales.split(',')
if options.globalScalesCorr=='': options.globalScalesCorr = []
else: options.globalScalesCorr = options.globalScalesCorr.split(',')
###############################################################################

###############################################################################
## OPEN WORKSPACE AND EXTRACT INFO # ##########################################
#inWS = inFile.Get('wsig_13TeV')
sqrts=13
inWS = inFile.Get('tagsDumper/cms_hgg_%sTeV'%sqrts)
intL = inWS.var('IntLumi').getVal() #FIXME
#sqrts = inWS.var('IntLumi').getVal() #FIXME
print "[INFO] Get Intlumi from file, value : ", intL," pb^{-1}", " sqrts ", sqrts
###############################################################################

###############################################################################
## SHAPE SYSTEMATIC SETUP  ####################################################
###############################################################################
file_ext = 'mva'
dataFile = 'CMS-HGG_%s_%dTeV_multipdf.root'%(file_ext,sqrts)
bkgFile = 'CMS-HGG_%s_%dTeV_multipdf.root'%(file_ext,sqrts)
dataWS = 'multipdf'
bkgWS = 'multipdf'
sigFile = 'CMS-HGG_%s_%dTeV_sigfit.root'%(file_ext,sqrts)
sigWS = 'wsig_%dTeV'%(sqrts)
# file detaisl: for FLashgg always use unbinned signal and multipdf
fileDetails = {}
fileDetails['data_obs'] = [dataFile,dataWS,'roohist_data_mass_$CHANNEL']
fileDetails['bkg_mass']  = [bkgFile,bkgWS,'CMS_hgg_$CHANNEL_%dTeV_bkgshape'%sqrts]
fileDetails['ggH']       = [sigFile,sigWS,'hggpdfsmrel_%dTeV_ggh_$CHANNEL'%sqrts]
fileDetails['qqH']       = [sigFile,sigWS,'hggpdfsmrel_%dTeV_vbf_$CHANNEL'%sqrts]
if splitVH:
  fileDetails['WH']       =  [sigFile,sigWS,'hggpdfsmrel_%dTeV_wh_$CHANNEL'%sqrts]
  fileDetails['ZH']       =  [sigFile,sigWS,'hggpdfsmrel_%dTeV_zh_$CHANNEL'%sqrts]
else:
  fileDetails['VH']       =  [sigFile,sigWS,'hggpdfsmrel_%dTeV_wzh_$CHANNEL'%sqrts]
fileDetails['ttH']       = [sigFile,sigWS,'hggpdfsmrel_%dTeV_tth_$CHANNEL'%sqrts]
###############################################################################

###############################################################################
## THEORY SYSTEMATIC SETUP & TOOL #############################################
###############################################################################
# theory systematics arr=[up,down]
# --> globe info these come in specific types (as must be correlated with combination)
# -- globe info  - see https://twiki.cern.ch/twiki/bin/viewauth/CMS/HiggsWG/HiggsCombinationConventions
theorySyst = {}
theorySyst['QCDscale_ggH'] = {}
theorySyst['QCDscale_qqH'] = {}
theorySyst['QCDscale_VH'] = {}
theorySyst['QCDscale_ttH'] = {}
theorySyst['pdf_gg'] = {}
theorySyst['pdf_qqbar'] = {}

# QCD scale and PDF variations on PT-Y (replaced k-Factor PT variation) 
# flashggSysts['pdfWeight_QCDscale'] = 'n_sc' #FIXME
# for pdfi in range(1,27): #FIXME
# flashggSysts['pdfWeight_pdfset%d'%pdfi] = 'n_pdf_%d'%pdfi #FIXME, not currently supported by flashgg 
'''
# 8 TeV  #FIXME FOR 13TEV
# scale
theorySyst['QCDscale_ggH']['ggH'] = [0.072,-0.078]
theorySyst['QCDscale_qqH']['qqH'] = [0.002,-0.002]
if splitVH:
  theorySyst['QCDscale_VH']['WH'] = [0.010,-0.010]
  theorySyst['QCDscale_VH']['ZH'] = [0.031,-0.031]
else:
  theorySyst['QCDscale_VH']['VH'] = [0.031,-0.031] 
theorySyst['QCDscale_ttH']['ttH'] = [0.038,-0.093]
# pdf
theorySyst['pdf_gg']['ggH'] = [0.075,-0.069] 
theorySyst['pdf_qqbar']['qqH'] = [0.026,-0.028]
if splitVH:
  theorySyst['pdf_qqbar']['WH'] = [0.023,-0.023]
  theorySyst['pdf_qqbar']['ZH'] = [0.025,-0.025]
else:
  theorySyst['pdf_qqbar']['VH'] = [0.034,-0.034]
theorySyst['pdf_gg']['ttH'] = [0.081,-0.081]
'''
#printing function
def printTheorySysts():
  # as these are antisymmetric lnN systematics - implement as [1/(1.+err_down)] for the lower and [1.+err_up] for the upper
  print '[INFO] Theory...'
  for systName, systDetails in theorySyst.items():
    outFile.write('%-35s   lnN   '%systName)
    for c in options.cats:
      for p in options.procs:
        if '%s:%s'%(p,c) in options.toSkip: continue
        if p in systDetails.keys():
          outFile.write('%5.3f/%5.3f '%(1./(1.-systDetails[p][1]),1.+systDetails[p][0]))
        else:
          outFile.write('- ')
    outFile.write('\n')
  outFile.write('\n')

## pdf weights printing tool #FIXME NOT USED OR READY
def getFlashggLinePDFWeights(proc,cat,name):
  n = 0
  m = 0
  if ( "pdfset" in name ) : 
    n = int(name[name.find("pdfset")+6:])
    m = n+1
  ws =  inFile.Get("tagsDumper/cms_hgg_13TeV");
#  if (ws) : print "got ws!"
  data_nominal = ws.data("%s_125_13TeV_%s"%(proc,cat))
  data_nominal_sum = data_nominal.sumEntries()
  data_nominal_num = data_nominal.numEntries()
#  print "LC DEBUG - nominal " , data_nominal , " sumEntries " , data_nominal_sum, " numEntries ", data_nominal_num
  data_up = data_nominal.emptyClone();
  data_down = data_nominal.emptyClone();
  mass = ws.var("CMS_hgg_mass")
  weight = r.RooRealVar("weight","weight",0)
  #weight_up = r.RooRealVar("weight_up","weight_up",0)
  weight_up = ws.var("pdfWeight_1")
  #weight_down = r.RooRealVar("weight_down","weight_down",0)
  weight_down = ws.var("pdfWeight_2")
  for i in range(0,int(data_nominal.numEntries())):
    mass.setVal(data_nominal.get(i).getRealValue("CMS_hgg_mass"))
    centralweight =data_nominal.weight()
    factor_down = data_nominal.get(i).getRealValue("pdfWeight_%d"%n)
    factor_up = data_nominal.get(i).getRealValue("pdfWeight_%d"%(m))
    weight_down.setVal(centralweight*factor_down)
    weight_up.setVal(centralweight*factor_up)
    data_up.add(r.RooArgSet(mass,weight_up),weight_up.getVal())
    data_down.add(r.RooArgSet(mass,weight_down),weight_down.getVal())
  #  print "DEBUG - dataset entry ", i, " central weight ", centralweight, " factor up " , factor_up, " factor down ", factor_down
  #systVals = interp1Sigma(th1f_nom,th1f_dn,th1f_up)
#print "LC DEBUG dataset nominal " , data_nominal.Print()
#  print "LC DEBUG dataset  " , data_up.Print() 
#  print "LC DEBUG dataset down " , data_down.Print() 
  systVals = interp1SigmaDataset(data_nominal,data_down,data_up)
  flashggSystDump.write('%s nominal: %5.3f up: %5.3f down: %5.3f vals: [%5.3f,%5.3f] \n'%(sysr,dataNOMINAL.sumEntries(),dataUP.sumEntries(),dataDOWN.sumEntries(),systVals[0],systVals[1]))
  if systVals[0]==1 and systVals[1]==1:
      line = '- '
  else:
      line = '%5.3f/%5.3f '%(systVals[0],systVals[1])
#      print " [DEBUG] -- ", line
  return line
###############################################################################

###############################################################################
## GENERAL ANALYSIS SYSTEMATIC SETUP  #########################################
###############################################################################
# BR uncertainty
###brSyst = [0.050,-0.049] #8TeV Values
brSyst = [0.,0.] #FIXME FOR 13Tev!!!
# lumi syst
####lumiSyst = 0.026 #8TeV Values
lumiSyst=0.026  #FIXME FOR 13Tev!!!
#trig Eff
####trigEff = 0.01  #8TeV Value
trigEff = 0.0 #FIXME FOR 13Tev!!!

##Printing Functions
def printBRSyst():
  print '[INFO] BR...'
  outFile.write('%-35s   lnN   '%('CMS_hgg_BR'))
  for c in options.cats:
    for p in options.procs:
      if '%s:%s'%(p,c) in options.toSkip: continue
      outFile.write('%5.3f/%5.3f '%(1./(1.-brSyst[1]),1.+brSyst[0]))
  outFile.write('\n')
  outFile.write('\n')

def printLumiSyst():
  print '[INFO] Lumi...'
  outFile.write('%-35s   lnN   '%('lumi_%dTeV'%sqrts))
  for c in options.cats:
    for p in options.procs:
      if '%s:%s'%(p,c) in options.toSkip: continue
      if p in bkgProcs:
        outFile.write('- ')
      else:
        outFile.write('%5.3f '%(1.+lumiSyst))
  outFile.write('\n')
  outFile.write('\n')

def printTrigSyst():
  print '[INFO] Trig...'
  outFile.write('%-35s   lnN   '%'CMS_hgg_n_trig_eff')
  for c in options.cats:
    for p in options.procs:
      if '%s:%s'%(p,c) in options.toSkip: continue
      if p in bkgProcs:
        outFile.write('- ')
      else:
        outFile.write('%5.3f '%(1.+trigEff))
  outFile.write('\n')
  outFile.write('\n')
###############################################################################

###############################################################################
##  FLASHGG-SPECIFIC SYSTEMATIC SETUP  ########################################
###############################################################################
flashggSystDump = open('flashggSystDump.dat','w')
flashggSysts={}


# vtx eff
vtxSyst = 0.030 #FIXME FOR 13Tev!!! #8TeV Values

#photon ID
flashggSysts['MvaShift'] =  'phoIdMva'
flashggSysts['LooseMvaSF'] =  'LooseMvaSF'
flashggSysts['PreselSF']    =  'PreselSF'
flashggSysts['SigmaEOverEShift'] = 'SigmaEOverEShift'
#flashggSysts[''] =  ''

#flashggSysts['regSig'] = 'n_sigmae'
#flashggSysts['idEff'] = 'n_id_eff'
#flashggSysts['triggerEff'] = 'n_trig_eff'

# pu jet eff = [ggEffect,qqEffect,WHeffect,ZHeffect,ttHeffect] - append for each vbf cat and for each VH hadronic cat
puJetIdEff = []
#puJetIdEff.append([0.029,0.029,0.023,0.023,0.009])  ##FIXME 13TeV Flashgg!!
#puJetIdEff.append([0.031,0.035,0.024,0.024,0.010])  ##FIXME 13TeV Flashgg!!
#puJetIdEff.append([0.040,0.040,0.023,0.023,0.009])  ##FIXME 13TeV Flashgg!!
#puJetIdEff.append([0.010,0.010,0.009,0.009,0.009])  ##FIXME 13TeV Flashgg!!

# vbf uncertainties - 
# vbfSysts['name'] = [ggEffect,qqEffect] - append migration effects
# naming is important to correlate with combination
vbfSysts={}
vbfSysts['JEC'] = [] 
vbfSysts['JER'] = [] 
vbfSysts['JetVeto'] =[]
for dijetCat in dijetCats: #each entry will represent a different migration
   vbfSysts['JER'].append([1.,1.])  #value of 1 given gor both ggh and qqh, since vairations are taken from histograms directly
   vbfSysts['JEC'].append([1.,1.]) #value of 1 given gor both ggh and qqh, since vairations are taken from histograms directly
vbfSysts['JetVeto'].append([0.3,0.3]) # adhoc for ggh<->vbf
vbfSysts['JetVeto'].append([0.15,0.15]) # adhoc for vbf0<->vbf1
#vbfSysts['QCDscale_gg2in'] = [] # on the hgg twiki this is referred to JetVeto_QCDscale
#vbfSysts['UEPS'] = []
#vbfSysts['QCDscale_gg2in'].append([0.30,0.]) # All VBF cats -> inclusive
#vbfSysts['QCDscale_gg2in'].append([0.14,0.]) # VBF cat5+cat6 -> VBF loose (cat7)
#vbfSysts['QCDscale_gg2in'].append([0.05,0.]) # VBF cat5 -> VBF cat 6
#vbfSysts['UEPS'].append([0.03,0.01])
#vbfSysts['UEPS'].append([0.01,0.02])
#vbfSysts['UEPS'].append([0.01,0.02])

#lepton, MET tags  ## lepton tags not considered for Dry run...
# [VH tight, VH loose, ttH leptonic]
eleSyst = {}
muonSyst = {}
metSyst = {}
''' 
eleSyst['ggH'] = [0.,0.,0.] ##FIXME 13TeV Flashgg!!
eleSyst['qqH'] = [0.,0.,0.]##FIXME 13TeV Flashgg!!
eleSyst['WH'] = [0.0028,0.0024,0.] ##FIXME 13TeV Flashgg!!
eleSyst['ZH'] = [0.0044,0.0025,0.]##FIXME 13TeV Flashgg!!
eleSyst['ttH'] = [0.0026,0.,0.0022]##FIXME 13TeV Flashgg!!
muonSyst['ggH'] = [0.0,0.0,0.0]##FIXME 13TeV Flashgg!!
muonSyst['qqH'] = [0.0,0.0,0.0]##FIXME 13TeV Flashgg!!
muonSyst['WH'] = [0.0027,0.0034,0.]##FIXME 13TeV Flashgg!!
muonSyst['ZH'] = [0.0054,0.0037,0.]##FIXME 13TeV Flashgg!!
muonSyst['ttH'] = [0.0026,0.,0.0022]##FIXME 13TeV Flashgg!!
metSyst['ggH'] = [0.,0.,0.04] ##FIXME 13TeV Flashgg!!
metSyst['qqH'] = [0.,0.,0.04]##FIXME 13TeV Flashgg!!
metSyst['WH'] = [0.012,0.019,0.026] ##FIXME 13TeV Flashgg!!
metSyst['ZH'] = [0.009,0.015,0.021]##FIXME 13TeV Flashgg!!
metSyst['ttH'] = [0.011,0.012,0.040]##FIXME 13TeV Flashgg!!
'''
#tth tags  ## lepton tags not considered for Dry run...
# syst for tth tags - [ttHlep,tthHad]
###tth tags not considered for dry run
btagSyst={}
ggHforttHSysts = {}
'''
btagSyst['ggH'] = [0.,0.02] ##FIXME 13TeV Flashgg!!
btagSyst['qqH'] = [0.,0.] ##FIXME 13TeV Flashgg!!
btagSyst['WH'] = [0.,0.] ##FIXME 13TeV Flashgg!!
btagSyst['ZH'] = [0.,0.] ##FIXME 13TeV Flashgg!!
btagSyst['ttH'] = [0.01,0.01] ##FIXME 13TeV Flashgg!!
# spec for ggh in tth cats - [MC_low_stat,gluon_splitting,parton_shower]
ggHforttHSysts['CMS_hgg_tth_mc_low_stat'] = 0.25 ##FIXME 13TeV Flashgg!!
ggHforttHSysts['CMS_hgg_tth_gluon_splitting'] = 0.13 ##FIXME 13TeV Flashgg!!
ggHforttHSysts['CMS_hgg_tth_parton_shower'] = 0.30 ##FIXME 13TeV Flashgg!!
'''

# rate adjustments
#looseLepRateScale = 0.9909 ##FIXME 13TeV Flashgg!!
#tightLepRateScale = 0.9886 ##FIXME 13TeV Flashgg!!
#tthLepRateScale = 0.980 ##FIXME 13TeV Flashgg!!
#tthHadRateScale = 0.995 ##FIXME 13TeV Flashgg!!
###############################################################################

###############################################################################
##  INTERPOLATION TOOLS #######################################################
###############################################################################
def interp1Sigma(th1f_nom,th1f_down,th1f_up):
  nomE = th1f_nom.Integral()
  if nomE==0:
    return [1.000,1.000]
  downE = th1f_down.Integral()/nomE
  upE = th1f_up.Integral()/nomE
  if options.quadInterpolate!=0:
    downE = quadInterpolate(-1.,-1.*options.quadInterpolate,0.,1.*options.quadInterpolate,th1f_down.Integral(),th1f_nom.Integral(),th1f_up.Integral())
    upE = quadInterpolate(1.,-1.*options.quadInterpolate,0.,1.*options.quadInterpolate,th1f_down.Integral(),th1f_nom.Integral(),th1f_up.Integral())
    if upE != upE: upE=1.000
    if downE != downE: downE=1.000
  return [downE,upE]

def interp1SigmaDataset(d_nom,d_down,d_up):
  nomE = d_nom.sumEntries()
  if nomE==0:
    return [1.000,1.000]
  downE = d_down.sumEntries()/nomE
  upE = d_up.sumEntries()/nomE
  if options.quadInterpolate!=0:
    downE = quadInterpolate(-1.,-1.*options.quadInterpolate,0.,1.*options.quadInterpolate,d_down.sumEntries(),d_nom.sumEntries(),s_up.sumEntries())
    upE = quadInterpolate(1.,-1.*options.quadInterpolate,0.,1.*options.quadInterpolate,d_down.sumEntries(),d_nom.sumEntries(),d_up.sumEntries())
    if upE != upE: upE=1.000
    if downE != downE: downE=1.000
  return [downE,upE]
###############################################################################

###############################################################################
##  DATACARD PREAMBLE TOOLS ###################################################
###############################################################################
def printPreamble():
  print '[INFO] Making Preamble...'
  outFile.write('CMS-HGG datacard for parametric model - 2015 %dTeV \n'%sqrts)
  outFile.write('Auto-generated by flashggFinalFits/Datacard/makeParametricModelDatacardFLASHgg.py\n')
  outFile.write('Run with: combine\n')
  outFile.write('---------------------------------------------\n')
  outFile.write('imax *\n')
  outFile.write('jmax *\n')
  outFile.write('kmax *\n')
  outFile.write('---------------------------------------------\n')
  outFile.write('\n')
###############################################################################

###############################################################################
##  SHAPE SYSTEMATICS TOOLS ###################################################
###############################################################################
def printFileOptions():
  print '[INFO] File opts...'
  for typ, info in fileDetails.items():
    for c in options.cats:
      file = info[0]
      wsname = info[1]
      pdfname = info[2].replace('$CHANNEL','%s'%c)
      if typ not in options.procs and typ!='data_obs': continue
      outFile.write('shapes %-10s %-15s %-30s %-30s\n'%(typ,'%s_%dTeV'%(c,sqrts),file,wsname+':'+pdfname))
  outFile.write('\n')
###############################################################################

###############################################################################
##  PROCESS/BIN LINES TOOLS ###################################################
###############################################################################
def printObsProcBinLines():
  print '[INFO] Rates...'
  outFile.write('%-15s '%'bin')
  for c in options.cats:
    outFile.write('%s_%dTeV '%(c,sqrts))
  outFile.write('\n')
  
  outFile.write('%-15s '%'observation')
  for c in options.cats:
    outFile.write('-1 ')
  outFile.write('\n')
  
  outFile.write('%-15s '%'bin')
  for c in options.cats:
    for p in options.procs:
      if '%s:%s'%(p,c) in options.toSkip: continue
      outFile.write('%s_%dTeV '%(c,sqrts))
  outFile.write('\n')
  
  outFile.write('%-15s '%'process')
  for c in options.cats:
    for p in options.procs:
      if '%s:%s'%(p,c) in options.toSkip: continue
      outFile.write('%s '%p)
  outFile.write('\n')

  outFile.write('%-15s '%'process')
  for c in options.cats:
    for p in options.procs:
      if '%s:%s'%(p,c) in options.toSkip: continue
      outFile.write('%d '%procId[p])
  outFile.write('\n')

  outFile.write('%-15s '%'rate')
  for c in options.cats:
    for p in options.procs:
      if '%s:%s'%(p,c) in options.toSkip: continue
      if p in bkgProcs:
        outFile.write('1.0 ')
      else:
        scale=1.
        if c in looseLepCat: scale *= looseLepRateScale
        if c in tightLepCat: scale *= tightLepRateScale
        if c in tthCats:
          if c in tthLepCat: scale *= tthLepRateScale
          else: scale *= tthHadRateScale
        outFile.write('%7.1f '%(intL*scale))
  outFile.write('\n')
  outFile.write('\n')
###############################################################################

###############################################################################
##  NUISANCE PARAM LINES TOOLS ################################################
###############################################################################
def printNuisParam(name,typ,sqrtS=None):
  val="1.0"
  if ":" in name:
    name,val = name.split(":")
  if sqrtS:
    typ="%dTeV%s" % (sqrtS, typ)
  outFile.write('%-40s param 0.0 %s\n'%('CMS_hgg_nuisance_%s_%s'%(name,typ),val))

def printNuisParams():
    print '[INFO] Nuisances...'
    outFile.write('%-40s param 0.0 %1.4g\n'%('CMS_hgg_nuisance_deltafracright',vtxSyst))
    for phoSyst in options.photonCatScales:
      printNuisParam(phoSyst,"scale",sqrts)
    for phoSyst in options.photonCatScalesCorr:
      printNuisParam(phoSyst,"scale")
    for phoSyst in options.globalScales:
      printNuisParam(phoSyst,"scale",sqrts)      
    for phoSyst in options.globalScalesCorr:
      printNuisParam(phoSyst,"scale")
    for phoSyst in options.photonCatSmears:
      printNuisParam(phoSyst,"smear",sqrts)
    for phoSyst in options.photonCatSmearsCorr:
      printNuisParam(phoSyst,"smear")
    outFile.write('\n')
###############################################################################


###############################################################################
##  LN(N) LINES TOOLS ########################################################
###############################################################################
#individual numbers for each proc/cat
def getFlashggLine(proc,cat,syst):
  asymmetric=False 
  eventweight=False 
  #print "===========> SYST", syst ," PROC ", proc , ", TAG ", cat
  dataSYMMETRIC =  inWS.data("%s_125_13TeV_%s_%s"%(flashggProc[proc],cat,syst)) #Will exist if the systematic is a symmetric uncertainty not stored as event weights
  dataDOWN =  inWS.data("%s_125_13TeV_%s_%sDown01sigma"%(flashggProc[proc],cat,syst)) # will exist if teh systematic is an asymetric uncertainty not strore as event weights
  dataUP =  inWS.data("%s_125_13TeV_%s_%sUp01sigma"%(flashggProc[proc],cat,syst))# will exist if teh systematic is an asymetric uncertainty not strore as event weights
  dataNOMINAL =  inWS.data("%s_125_13TeV_%s"%(flashggProc[proc],cat)) #Nominal RooDataSet,. May contain required weights if UP/DOWN/SYMMETRIC roodatahists do not exist (ie systematic stored as event weigths)
  #print " ", ("%s_125_13TeV_%s_%s"%(flashggProc[proc],cat,syst))," ", dataSYMMETRIC, "data==None" , (dataSYMMETRIC==None), " data is None ", (dataSYMMETRIC is None)
  print " ", ("%s_125_13TeV_%s"%(flashggProc[proc],cat)) ," ",  dataNOMINAL, "data==None" , (dataNOMINAL==None), " data is None ", (dataNOMINAL is None)
  #print "  ", ("%s_125_13TeV_%s_%sDown01sigma"%(flashggProc[proc],cat,syst)), " ", dataDOWN, "data==None" , (dataDOWN==None), " data is None ", (dataDOWN is None)
  #print " ", ("%s_125_13TeV_%s_%sUp01sigma"%(flashggProc[proc],cat,syst)), " ", dataUP, "data==None" , (dataUP==None), " data is None ", (dataUP is None)
  if (dataSYMMETRIC==None):
    if( (dataUP==None) or  (dataDOWN==None)) :
      #print "[INFO] Systematic ", syst," stored as asymmetric event weights in RooDataSet"
      asymmetric=True
      eventweight=True
    else:
      #print "[INFO] Systematic ", syst," stored as asymmetric rooDataHists"
      asymmetric=True
      eventweight=False
  else:
      #print "[INFO] Systematic ", syst," stored as symmetric rooDataHist"
      asymmetric=False
      eventweight=False
  
  if (asymmetric and eventweight) : 
    data_up = dataNOMINAL.emptyClone();
    data_down = dataNOMINAL.emptyClone();
    mass = inWS.var("CMS_hgg_mass")
    weight = r.RooRealVar("weight","weight",0)
    weight_up = inWS.var("%sUp01sigma"%syst)
    #weight_down = inWS.var("%sDown01sigma"%sys)
    weight_down = r.RooRealVar("%sDown01sigma"%syst,"%sDown01sigma"%syst,-1.)
    weight_central = inWS.var("centralObjectWeight")
    for i in range(0,int(dataNOMINAL.numEntries())):
      mass.setVal(dataNOMINAL.get(i).getRealValue("CMS_hgg_mass"))
      w_nominal =dataNOMINAL.weight()
      #print " w_down components dataNOMINAL ", dataNOMINAL , " weight_down ", weight_down , "weight_down.name() ", weight_down.GetName() 
      #w_down = dataNOMINAL.get(i).getRealValue(("%sDown01sigma"%syst))
      #print " mass, ", mass, " w_nominal " , w_nominal , " w down ", w_down , "test ", (("%sDown01sigma"%syst))
      #sys.exit(1) 
      w_down = dataNOMINAL.get(i).getRealValue(weight_down.GetName())
      w_up = dataNOMINAL.get(i).getRealValue(weight_up.GetName())
      w_central = dataNOMINAL.get(i).getRealValue(weight_central.GetName())
      #print " syst " , syst , " w_nom ", w_nominal , "  w_up " , w_up , " w_ down " , w_down 
      weight_down.setVal(w_nominal*(w_down/w_central))
      weight_up.setVal(w_nominal*(w_up/w_central))
      data_up.add(r.RooArgSet(mass,weight_up),weight_up.getVal())
      data_down.add(r.RooArgSet(mass,weight_down),weight_down.getVal())
    #print "dataNOMINAL " , dataNOMINAL.sumEntries()
    #print "data_up ", data_up.sumEntries()
    #print "data_down ", data_down.sumEntries()
    dataUP =  data_up  #repalce UP/DOwn histograms defined outside scope of this "if"
    dataDOWN =  data_down  #repalce UP/DOwn histograms defined outside scope of this "if"

  systVals = interp1SigmaDataset(dataNOMINAL,dataDOWN,dataUP)
  flashggSystDump.write('%s nominal: %5.3f up: %5.3f down: %5.3f vals: [%5.3f,%5.3f] \n'%(syst,dataNOMINAL.sumEntries(),dataUP.sumEntries(),dataDOWN.sumEntries(),systVals[0],systVals[1]))
  print "systvals ", systVals 
  if systVals[0]==1 and systVals[1]==1:
      line = '- '
  else:
      line = '%5.3f/%5.3f '%(systVals[0],systVals[1])
  print " [DEBUG] proc ", proc, " tag " , cat,  "  syst ", syst ," --> ", line
  return line

# printing whole lines 
def printFlashggSysts():
  print '[INFO] lnN lines...'
  for flashggSyst, paramSyst in flashggSysts.items():
    #Not considering QCD scale and PDF weight right now, #FIXME more to another section later
    #if 'pdfWeight' and 'QCDscale' in flashggSyst: # special case
    #  outFile.write('%-35s   lnN   '%('CMS_hgg_%s_ggH'%paramSyst))
    #  for c in options.cats:
    #    for p in options.procs:
    #      if '%s:%s'%(p,c) in options.toSkip: continue
    #      #if p=='ggH': outFile.write(getFlashggLine(flashggProc[p],c,flashggSyst))
    #      if p=='ggH': outFile.write(getFlashggLine(p,c,flashggSyst))
    #      else: outFile.write('- ')
    #  outFile.write('\n')
    #  outFile.write('%-35s   lnN   '%('CMS_hgg_%s_qqH'%paramSyst))
    #  for c in options.cats:
    #    for p in options.procs:
    #      if '%s:%s'%(p,c) in options.toSkip: continue
    #      #if p=='qqH': outFile.write(getFlashggLine(flashggProc[p],c,flashggSyst))
    #      if p=='qqH': outFile.write(getFlashggLine(p,c,flashggSyst))
    #      else: outFile.write('- ')
    #else:    
#     print " [DEBUG] pdfWeight and QCDScale NOT in flashggSyst"
#     print " [DEBUG] pdfWeight and QCDScale NOT  in flashggSyst --- UNbinned Signal"
      outFile.write('%-35s   lnN   '%('CMS_hgg_%s'%paramSyst))
      for c in options.cats:
        for p in options.procs:
          if '%s:%s'%(p,c) in options.toSkip: continue
          if p in bkgProcs or ('pdfWeight' in flashggSyst and (p!='ggH' and p!='qqH')):
            outFile.write('- ')
          else:
            outFile.write(getFlashggLine(p,c,flashggSyst))
      outFile.write('\n')
  outFile.write('\n')
###############################################################################

###############################################################################
##  VBF CATEGORY MIGRATION LINES TOOLS ########################################
###############################################################################
def printVbfSysts():
  # we first figure out what migrations are needed
  # e.g. for 5 inc cats and 3 vbf cats we need:
  # cat5 -> cat6, cat5+cat6 -> cat7, cat5+cat6+cat7 -> incCats
  # the other important thing is to adjust the name of the VBFtot -> incCats mig to 
  # correlate with combination for the QCDscale and UEPS
  print "[INFO] considering VBF catgeory migrations"
  # now print relevant numbers
  for vbfSystName, vbfSystValArray in vbfSysts.items():
    asymmetric=False
    adhoc=False
    print "vbfSystName, vbfSystValArray ", vbfSystName,", ", vbfSystValArray
    
    # work out which cats we are migrating to and from
    syst=vbfSystName
    if (len(vbfSystValArray)==0) : continue
    vbfMigrateFromCats=[]
    vbfMigrateToCats=[]
    vbfMigrateFromEvCount={}
    vbfMigrateToEvCount={}
    vbfMigrateFromEvCountUP={}
    vbfMigrateToEvCountUP={}
    vbfMigrateFromEvCountDOWN={}
    vbfMigrateToEvCountDOWN={}
    vbfMigrateFromEvCountNOMINAL={}
    vbfMigrateToEvCountNOMINAL={}
    temp = []
    for c in dijetCats:
      temp.append(c)
      vbfMigrateFromCats.append(copy.copy(temp))
      if c==options.cats[len(incCats)+len(dijetCats)-1]: # i.e. last vbf cat
        vbfMigrateToCats.append(incCats)
      else:
        index=options.cats.index(c)
        dummy=[]
        dummy.append(options.cats[index+1])
        vbfMigrateToCats.append(dummy)
    # reverse
    vbfMigrateToCats.reverse()
    vbfMigrateFromCats.reverse()
    #summary
    print "--> cats To " , vbfMigrateToCats 
    print "--> cats From " , vbfMigrateFromCats 
      
    # now get relevant event counts
    for p in options.procs:
      if p in bkgProcs: continue
      vbfMigrateToEvCount[p] = []
      vbfMigrateToEvCountNOMINAL[p] = []
      vbfMigrateToEvCountUP[p] = []
      vbfMigrateToEvCountDOWN[p] = []
      for cats in vbfMigrateToCats:
        sum=0
        sumUP=0
        sumNOMINAL=0
        sumDOWN=0
        for c in cats:
          print "looking at c ", c , " proc ", p , " syst ", syst
          data =  inWS.data("%s_125_13TeV_%s_%s"%(flashggProc[p],c,syst))
          dataDOWN =  inWS.data("%s_125_13TeV_%s_%sDown01sigma"%(flashggProc[p],c,syst))
          dataNOMINAL =  inWS.data("%s_125_13TeV_%s"%(flashggProc[p],c))
          mass = inWS.var("CMS_hgg_mass")
          dataUP =  inWS.data("%s_125_13TeV_%s_%sUp01sigma"%(flashggProc[p],c,syst))
          
          if (data==None):
            if( (dataUP==None) or  (dataDOWN==None)) :
              print "[INFO] VBF Systematic ", syst," could not be found either as symmetric (",syst,") or asymmetric (",syst,"Down01sigma,",syst,"Up01sigma). Consider as adhoc variation..."
              adhoc=True
              asymmetric=False
            else:
              asymmetric=True
              print "[INFO] VBF Systematic ", syst," will be treated as asymmetric"
          else:
              asymmetric=False
              print "[INFO] VBF Systematic ", syst," wil be treated as symmetric"


          if (asymmetric) :
            sumUP += dataUP.sumEntries()
            sumDOWN += dataDOWN.sumEntries()
            sumNOMINAL += dataNOMINAL.sumEntries()
          elif (adhoc) : 
            sumNOMINAL += dataNOMINAL.sumEntries()
          else : 
            sum += data.sumEntries()
            sumNOMINAL += dataNOMINAL.sumEntries()
        vbfMigrateToEvCount[p].append(sum)
        vbfMigrateToEvCountNOMINAL[p].append(sumNOMINAL)
        vbfMigrateToEvCountUP[p].append(sumUP)
        vbfMigrateToEvCountDOWN[p].append(sumDOWN)
    for p in options.procs:
      if p in bkgProcs: continue
      vbfMigrateFromEvCount[p] = []
      vbfMigrateFromEvCountNOMINAL[p] = []
      vbfMigrateFromEvCountUP[p] = []
      vbfMigrateFromEvCountDOWN[p] = []
      for cats in vbfMigrateFromCats:
        sum=0
        sumUP=0
        sumNOMINAL=0
        sumDOWN=0
        for c in cats:
          data =  inWS.data("%s_125_13TeV_%s_%s"%(flashggProc[p],c,syst))
          dataDOWN =  inWS.data("%s_125_13TeV_%s_%sDown01sigma"%(flashggProc[p],c,syst))
          dataNOMINAL =  inWS.data("%s_125_13TeV_%s"%(flashggProc[p],c))
          dataUP =  inWS.data("%s_125_13TeV_%s_%sUp01sigma"%(flashggProc[p],c,syst))
          if (asymmetric) :
            sumUP += dataUP.sumEntries()
            sumDOWN += dataDOWN.sumEntries()
            sumNOMINAL += dataNOMINAL.sumEntries()
          elif (adhoc) :
            sumNOMINAL += dataNOMINAL.sumEntries()
          else : 
            sum += data.sumEntries()
            sumNOMINAL += dataNOMINAL.sumEntries()
        vbfMigrateFromEvCount[p].append(sum)
        vbfMigrateFromEvCountUP[p].append(sumUP)
        vbfMigrateFromEvCountNOMINAL[p].append(sumNOMINAL)
        vbfMigrateFromEvCountDOWN[p].append(sumDOWN)
    
    for migIt, vbfSystVal in (enumerate(vbfSystValArray)):
      name = vbfSystName
      name += '_migration%d'%(migIt)
      outFile.write('%-35s   lnN   '%name)
      for c in options.cats:
        for p in options.procs:
          if '%s:%s'%(p,c) in options.toSkip: continue
          if p=='ggH': thisUncert = vbfSystVal[0]
          elif p=='qqH': thisUncert = vbfSystVal[1]
          else:
            outFile.write('- ')
            continue
          if thisUncert==0:
            outFile.write('- ')
          else:
            print "DEBUG ------> for migration of " ,vbfMigrateFromCats[migIt] ," to ",  vbfMigrateToCats[migIt] , " cat ", c ,", proc ", p
            if c in vbfMigrateToCats[migIt]:
              if (asymmetric) : 
                #print "DEBUG --------> (To) NOMINAL: ",vbfMigrateToEvCountNOMINAL[p][migIt] , ", UP: ", vbfMigrateToEvCountUP[p][migIt] , " difference (", vbfMigrateToEvCountUP[p][migIt] -  vbfMigrateToEvCountNOMINAL[p][migIt]
                #print "DEBUG --------> ===================" 
                #print "DEBUG --------> (To) NOMINAL: ",vbfMigrateToEvCountNOMINAL[p][migIt] , ", DOWN: ", vbfMigrateToEvCountDOWN[p][migIt] , " difference (", vbfMigrateToEvCountDOWN[p][migIt] -  vbfMigrateToEvCountNOMINAL[p][migIt]
                UP=vbfMigrateToEvCountUP[p][migIt]/vbfMigrateToEvCountNOMINAL[p][migIt]
                DOWN=vbfMigrateToEvCountDOWN[p][migIt]/vbfMigrateToEvCountNOMINAL[p][migIt]
                #print "DEBUG --------> ===================" 
                #print "DEBUG --------> TO DOWN ", DOWN, " UP ",UP 
                outFile.write('%1.4g/%1.4g '%(DOWN,UP))
              elif (adhoc) : 
                VAR=((vbfMigrateToEvCountNOMINAL[p][migIt]-thisUncert*vbfMigrateFromEvCountNOMINAL[p][migIt])/vbfMigrateToEvCountNOMINAL[p][migIt]) 
                print " TO categories : " , VAR
                outFile.write('%1.4g '%VAR)
              else : outFile.write('%1.4g '%(vbfMigrateToEvCount[p][migIt]/vbfMigrateToEvCountNOMINAL[p][migIt]))
            elif c in vbfMigrateFromCats[migIt]:
              if (asymmetric):
                #print "DEBUG --------> (From) NOMINAL: ",vbfMigrateFromEvCountNOMINAL[p][migIt] , ", UP: ", vbfMigrateFromEvCountUP[p][migIt], " difference (", vbfMigrateFromEvCountUP[p][migIt] -  vbfMigrateFromEvCountNOMINAL[p][migIt] 
                #print "DEBUG --------> (From) NOMINAL: ",vbfMigrateFromEvCountNOMINAL[p][migIt] , ", DOWN: ", vbfMigrateFromEvCountDOWN[p][migIt], " difference (", vbfMigrateFromEvCountDOWN[p][migIt] -  vbfMigrateFromEvCountNOMINAL[p][migIt] 
                UP=vbfMigrateFromEvCountUP[p][migIt]/vbfMigrateFromEvCountNOMINAL[p][migIt]
                DOWN=vbfMigrateFromEvCountDOWN[p][migIt]/vbfMigrateFromEvCountNOMINAL[p][migIt]
                outFile.write('%1.4g/%1.4g '%(DOWN,UP))
                #print "DEBUG --------> ===================" 
                #print "DEBUG --------> FROM DOWN ", DOWN, " UP ",UP 
              elif (adhoc) :
                VAR=(1.+thisUncert)
                print " FROM categories : " , VAR
                outFile.write('%1.4g '%VAR)
              else:
                VAR=vbfMigrateFromEvCount[p][migIt]/vbfMigrateFromEvCountNOMINAL[p][migIt]
                outFile.write('%1.4g '%(VAR))
            else:
              outFile.write('- ')
      outFile.write('\n')
    outFile.write('\n')
  '''
  # pu id eff  -- NOTE to correlate with combination change to CMS_eff_j
  # only in 2012  #FIXME FLASHgg??
  outFile.write('%-35s   lnN   '%('CMS_eff_j'))
  vbfCatCounter=0
  for c in options.cats:
    for i,p in enumerate(options.procs):
      if '%s:%s'%(p,c) in options.toSkip: continue
      if p in bkgProcs:
        outFile.write('- ')
        continue
      if c in dijetCats or c in vhHadCat:
        outFile.write('%6.4f/%6.4f '%(1.-puJetIdEff[vbfCatCounter][i],1.+puJetIdEff[vbfCatCounter][i]))
        if i==len(options.procs)-2: 
          vbfCatCounter += 1
      else:
        outFile.write('- ')
        continue
  outFile.write('\n')
  '''
###############################################################################

###############################################################################
##  LEPTON SYST LINES TOOLS ###################################################
###############################################################################
def printLepSysts():
  print '[INFO] Lep...'
  # electron efficiency -- NOTE to correlate with combination change to CMS_eff_e
  outFile.write('%-35s   lnN   '%('CMS_eff_e'))
  for c in options.cats:
    for p in options.procs:
      if '%s:%s'%(p,c) in options.toSkip: 
        outFile.write('- ')
        continue
      if p in bkgProcs or p=='ggH' or p=='qqH': 
        outFile.write('- ')
        continue
      else:
        if c in tightLepCat: thisUncert = eleSyst[p][0]
        elif c in looseLepCat: thisUncert = eleSyst[p][1]
        elif c in tthLepCat: thisUncert = eleSyst[p][2]
        else: thisUncert = 0.
        if thisUncert==0:
          outFile.write('- ')
        else:
          outFile.write('%6.4f/%6.4f '%(1.-thisUncert,1+thisUncert))
  outFile.write('\n')
  
  # muon efficiency -- NOTE to correlate with combination change to CMS_eff_m
  outFile.write('%-35s   lnN   '%('CMS_eff_m'))
  for c in options.cats:
    for p in options.procs:
      if '%s:%s'%(p,c) in options.toSkip: 
        outFile.write('- ')
        continue
      if p in bkgProcs or p=='ggH' or p=='qqH': 
        outFile.write('- ')
        continue
      else:
        if c in tightLepCat: thisUncert = muonSyst[p][0]
        elif c in looseLepCat: thisUncert = muonSyst[p][1]
        elif c in tthLepCat: thisUncert = muonSyst[p][2]
        else: thisUncert = 0.
        if thisUncert==0:
          outFile.write('- ')
        else:
          outFile.write('%6.4f/%6.4f '%(1.-thisUncert,1+thisUncert))
  outFile.write('\n')

  # met efficiency -- NOTE to correlate with combination change to CMS_scale_met
  outFile.write('%-35s   lnN   '%('CMS_scale_met'))
  for c in options.cats:
    for p in options.procs:
      if '%s:%s'%(p,c) in options.toSkip: 
        outFile.write('- ')
        continue
      if p in bkgProcs or p=='ggH' or p=='qqH': 
        outFile.write('- ')
        continue
      else:
        if c in tightLepCat: thisUncert = metSyst[p][0]
        elif c in looseLepCat: thisUncert = metSyst[p][1]
        elif c in tthLepCat: thisUncert = metSyst[p][2]
        else: thisUncert = 0.
        if thisUncert==0:
          outFile.write('- ')
        else:
          outFile.write('%6.4f/%6.4f '%(1.-thisUncert,1+thisUncert))
  outFile.write('\n')
###############################################################################

###############################################################################
##  TTH SYST LINES TOOLS ######################################################
###############################################################################
def printTTHSysts():
  print '[INFO] tth...'
  # b tag efficiency
  outFile.write('%-35s   lnN   '%('CMS_eff_b'))
  for c in options.cats:
    for p in options.procs:
      if '%s:%s'%(p,c) in options.toSkip: 
        outFile.write('- ')
        continue
      if p in bkgProcs: 
        outFile.write('- ')
        continue
      if c in tthCats:
        #FIXME flashgg??
        #if c in tthLepCat: 
        #    thisUncert = btagSyst[p][0]
        #if c in tthHadCat:
        #    thisUncert = btagSyst[p][1]
        if thisUncert==0:
          outFile.write('- ')
        else:
          outFile.write('%6.4f/%6.4f '%(1.-thisUncert,1.+thisUncert))
      else:
        outFile.write('- ')
  outFile.write('\n')

  # ggh uncerts on tth
  for systName, systVal in ggHforttHSysts.items():
    outFile.write('%-35s   lnN   '%systName)
    for c in options.cats:
      for p in options.procs:
        if '%s:%s'%(p,c) in options.toSkip: 
          outFile.write('- ')
          continue
        if p=='ggH' and c in tthCats:
          outFile.write('%6.4f/%6.4f '%(1.-systVal,1.+systVal))
        else:
          outFile.write('- ')
          continue
    outFile.write('\n')
###############################################################################

###############################################################################
##  DISCRETE SYST LINES TOOLS #################################################
###############################################################################
def printMultiPdf():
  if options.isMultiPdf:
    for c in options.cats:
      outFile.write('pdfindex_%s_%dTeV  discrete\n'%(c,sqrts))
###############################################################################

###############################################################################
## MAIN #######################################################################
###############################################################################
# __main__ here
#preamble
printPreamble()
#shape systematic files
printFileOptions()
#obs proc/tag bins
printObsProcBinLines()
#nuisance param systematics
printNuisParams()
# lnN systematics
printTheorySysts()
printBRSyst()
printLumiSyst()
printTrigSyst()
printFlashggSysts()
#catgeory migrations
if len(dijetCats) > 0 :  printVbfSysts()
#other 
#printLepSysts()
#printTTHSysts()
printMultiPdf()
###############################################################################

