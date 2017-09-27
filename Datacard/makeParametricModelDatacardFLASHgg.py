#!/usr/bin/env python

# Script adapted from original by Matt Kenzie.
# Used for Dry Run of Dec 2015 Hgg analysis.

###############################################################################
## IMPORTS ####################################################################
###############################################################################
import os,sys,copy,math
###############################################################################

###############################################################################
## PARSE ROOT MACROS  #########################################################
###############################################################################
import ROOT as r
#if options.quadInterpolate:
#  r.gROOT.ProcessLine(".L quadInterpolate.C+g")
#  from ROOT import quadInterpolate
r.gROOT.ProcessLine(".L $CMSSW_BASE/lib/$SCRAM_ARCH/libHiggsAnalysisCombinedLimit.so")
#r.gROOT.ProcessLine(".L ../libLoopAll.so")
###############################################################################

###############################################################################
## WSTFileWrapper  ############################################################
###############################################################################

class WSTFileWrapper:
   #self.fnList = [] # filename list
   #self.fileList = [] #file list
   #self.wsList = [] #workspace list

   def __init__(self, files,wsname):
    self.fnList = files.split(",") # [1]       
    self.fileList = []
    self.wsList = [] #now list of ws names...
    #print files
    for fn in self.fnList: # [2]
        f = r.TFile.Open(fn) 
        self.fileList.append(f)
        thing = f.Get(wsname)
        self.wsList.append(self.fileList[-1].Get(wsname))
        f.Close()

   def convertTemplatedName(self,dataName):
        theProcName = ""
        theDataName = ""
        tpMap = {"GG2H":"ggh","VBF":"vbf","TTH":"tth","QQ2HLNU":"wh","QQ2HLL":"zh","WH2HQQ":"wh","ZH2HQQ":"zh","testBBH":"bbh","testTHQ":"th","testTHW":"th"}
        for stxsProc in tpMap:
          if dataName.startswith(stxsProc):
            theProcName = stxsProc
            theDataName = dataName.replace(stxsProc,tpMap[stxsProc],1)
        return [theDataName,theProcName]

   def data(self,dataName):
        thePair = self.convertTemplatedName(dataName)
        newDataName = thePair[0]
        newProcName = thePair[1]
        result = None
        complained_yet = 0 
        for i in range(len(self.fnList)):
          if self.fnList[i]!="current file":
            if newProcName not in self.fnList[i] and newProcName!="": continue
            this_result_obj = self.wsList[i].data(newDataName);
            if ( result and this_result_obj and (not complained_yet) ):
              complained_yet = True;
            if this_result_obj: # [3]
               result = this_result_obj
        return result 
   
   def var(self,varName):
        result = None
        complained_yet =0 
        for i in range(len(self.fnList)):
          this_result_obj = self.wsList[i].var(varName);
          if this_result_obj: # [3]
             result = this_result_obj
                
        return result 


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
parser.add_option("--uepsfilename",default="",help="input files for calculating UEPS systematics; leave blank to use most recent set")
parser.add_option("--batch",default="LSF",help="Batch system  (default: %default)")
parser.add_option("--photonCatScales",default="HighR9EE,LowR9EE,HighR9EB,LowR9EB",help="String list of photon scale nuisance names - WILL NOT correlate across years (default: %default)")
parser.add_option("--photonCatScalesCorr",default="MaterialCentral,MaterialForward,FNUFEE,FNUFEB,ShowerShapeHighR9EE,ShowerShapeHighR9EB,ShowerShapeLowR9EE,ShowerShapeLowR9EB",help="String list of photon scale nuisance names - WILL correlate across years (default: %default)")
parser.add_option("--photonCatSmears",default="HighR9EE,LowR9EE,HighR9EBRho,LowR9EBRho,HighR9EBPhi,LowR9EBPhi",help="String list of photon smearing nuisance names - WILL NOT correlate across years (default: %default)")
parser.add_option("--photonCatSmearsCorr",default="",help="String list of photon smearing nuisance names - WILL correlate across years (default: %default)")
#parser.add_option("--globalScales",default="NonLinearity:0.001,Geant4:0.0005,LightColl:0.0005,Absolute:0.0001",help="String list of global scale nuisances names with value separated by a \':\' - WILL NOT correlate across years (default: %default)")
parser.add_option("--globalScales",default="NonLinearity:0.001,Geant4:0.0005",help="String list of global scale nuisances names with value separated by a \':\' - WILL NOT correlate across years (default: %default)")
parser.add_option("--globalScalesCorr",default="",help="String list of global scale nuisances names with value separated by a \':\' - WILL correlate across years (default: %default)")
parser.add_option("--toSkip",default="",help="proc:cat which are to skipped e.g ggH_hgg:11,qqH_hgg:12 etc. (default: %default)")
parser.add_option("--isMultiPdf",default=False,action="store_true")
parser.add_option("--submitSelf",default=False,action="store_true",help="Tells script to submit itself to the batch")
parser.add_option("--justThisSyst",default="",help="Only calculate the line corresponding to thsi systematic")
parser.add_option("--simplePdfWeights",default=False,action="store_true",help="Condense pdfWeight systematics into 1 line instead of full shape systematic" )
parser.add_option("--scaleFactors",help="Scale factor for spin model pass as e.g. gg_grav:1.351,qq_grav:1.027")
parser.add_option("--quadInterpolate",type="int",default=0,help="Do a quadratic interpolation of flashgg templates back to 1 sigma from this sigma. 0 means off (default: %default)")
parser.add_option("--mass",type="int",default=125,help="Mass at which to calculate the systematic variations (default: %default)")
parser.add_option("--intLumi",type="float",default=3.71,help="Integrated Lumi (default: %default)")
parser.add_option("--newGghScheme",default=False,action="store_true",help="Use new WG1 scheme for ggH theory uncertainties" )
parser.add_option("--doSTXS",default=False,action="store_true",help="Use STXS Stage 0 processes" )
(options,args)=parser.parse_args()
allSystList=[]
if options.submitSelf :
  options.justThisSyst="batch_split"
###############################################################################


###############################################################################
## FILE I/O ###################################################################
###############################################################################
#inFile = r.TFile.Open(options.infilename)
outFile = open(options.outfilename,'w')
###############################################################################

###############################################################################
## PROCS HANDLING & DICT ######################################################
###############################################################################
# convert flashgg style to combine style process
combProc = {'ggH':'ggH_hgg','VBF':'qqH_hgg','ggh':'ggH_hgg','vbf':'qqH_hgg','wzh':'VH','wh':'WH_hgg','zh':'ZH_hgg','tth':'ttH_hgg','bkg_mass':'bkg_mass','gg_grav':'ggH_hgg_ALT','qq_grav':'qqbarH_ALT'}
if options.doSTXS: 
  combProc = {'GG2H':'ggH_hgg','VBF':'qqH_hgg','TTH':'ttH_hgg','QQ2HLNU':'WH_lep_hgg','QQ2HLL':'ZH_lep_hgg','WH2HQQ':'WH_had_hgg','ZH2HQQ':'ZH_had_hgg','testBBH':'bbH_hgg','testTHQ':'tHq_hgg','testTHW':'tHW_hgg','bkg_mass':'bkg_mass'}
flashggProc = {'ggH_hgg':'ggh','qqH_hgg':'vbf','VH':'wzh','WH_hgg':'wh','ZH_hgg':'zh','ttH_hgg':'tth','bkg_mass':'bkg_mass','ggH_hgg_ALT':'gg_grav','qqbarH_ALT':'qq_grav'}
if options.doSTXS: 
  flashggProc = {'ggH_hgg':'GG2H','qqH_hgg':'VBF','ttH_hgg':'TTH','WH_lep_hgg':'QQ2HLNU','ZH_lep_hgg':'QQ2HLL','WH_had_hgg':'WH2HQQ','ZH_had_hgg':'ZH2HQQ','bbH_hgg':'testBBH','tHq_hgg':'testTHQ','tHW_hgg':'testTHW','bkg_mass':'bkg_mass'}
procId = {'ggH_hgg':0,'qqH_hgg':-1,'ttH_hgg':-2,'WH_lep_hgg':-2,'ZH_lep_hgg':-3,'WH_had_hgg':-4,'ZH_had_hgg':-5,'bbH_hgg':-6,'tHq_hgg':-7,'tHW_hgg':-8,'bkg_mass':1}
bkgProcs = ['bkg_mass','bbH_hgg','tHq_hgg','tHW_hgg'] #what to treat as background
#Determine if VH or WZH_hgg
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
sqrts=13
inWS = WSTFileWrapper(options.infilename,"tagsDumper/cms_hgg_%sTeV"%sqrts)
#inWS = inFile.Get('wsig_13TeV')
#if (inWS==None) : inWS = inFile.Get('tagsDumper/cms_hgg_%sTeV'%sqrts)
#intL = inWS.var('IntLumi').getVal() #FIXME
#intL = 2600
intL = 1000* options.intLumi
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
#sigFile = 'CMS-HGG_%s_%dTeV_sigfit.root'%(file_ext,sqrts)
sigFile = 'CMS-HGG_sigfit_%s_$PROC_$CAT.root'%(file_ext)
#print "making sigfile " ,sigFile
sigWS = 'wsig_%dTeV'%(sqrts)
# file detaisl: for FLashgg always use unbinned signal and multipdf
fileDetails = {}
fileDetails['data_obs'] = [dataFile,dataWS,'roohist_data_mass_$CHANNEL']
fileDetails['bkg_mass']  = [bkgFile,bkgWS,'CMS_hgg_$CHANNEL_%dTeV_bkgshape'%sqrts]

if options.doSTXS:
  fileDetails['ggH_hgg']       = [sigFile.replace('$PROC',"GG2H"),sigWS,'hggpdfsmrel_%dTeV_GG2H_$CHANNEL'%sqrts]
  fileDetails['qqH_hgg']       = [sigFile.replace('$PROC',"VBF"),sigWS,'hggpdfsmrel_%dTeV_VBF_$CHANNEL'%sqrts]
  fileDetails['ttH_hgg']       = [sigFile.replace('$PROC',"TTH"),sigWS,'hggpdfsmrel_%dTeV_TTH_$CHANNEL'%sqrts]
  fileDetails['WH_lep_hgg']    = [sigFile.replace('$PROC',"QQ2HLNU"),sigWS,'hggpdfsmrel_%dTeV_QQ2HLNU_$CHANNEL'%sqrts]
  fileDetails['ZH_lep_hgg']    = [sigFile.replace('$PROC',"QQ2HLL"),sigWS,'hggpdfsmrel_%dTeV_QQ2HLL_$CHANNEL'%sqrts]
  fileDetails['WH_had_hgg']    = [sigFile.replace('$PROC',"WH2HQQ"),sigWS,'hggpdfsmrel_%dTeV_WH2HQQ_$CHANNEL'%sqrts]
  fileDetails['ZH_had_hgg']    = [sigFile.replace('$PROC',"ZH2HQQ"),sigWS,'hggpdfsmrel_%dTeV_ZH2HQQ_$CHANNEL'%sqrts]
  fileDetails['bbH_hgg']       = [sigFile.replace('$PROC',"testBBH"),sigWS,'hggpdfsmrel_%dTeV_testBBH_$CHANNEL'%sqrts]
  fileDetails['tHq_hgg']       = [sigFile.replace('$PROC',"testTHQ"),sigWS,'hggpdfsmrel_%dTeV_testTHQ_$CHANNEL'%sqrts]
  fileDetails['tHW_hgg']       = [sigFile.replace('$PROC',"testTHW"),sigWS,'hggpdfsmrel_%dTeV_testTHW_$CHANNEL'%sqrts]
else:
  fileDetails['ggH_hgg']       = [sigFile.replace('$PROC',"ggh"),sigWS,'hggpdfsmrel_%dTeV_ggh_$CHANNEL'%sqrts]
  fileDetails['qqH_hgg']       = [sigFile.replace('$PROC',"vbf"),sigWS,'hggpdfsmrel_%dTeV_vbf_$CHANNEL'%sqrts]
  fileDetails['ttH_hgg']       = [sigFile.replace('$PROC',"tth"),sigWS,'hggpdfsmrel_%dTeV_tth_$CHANNEL'%sqrts]
  if splitVH:
    fileDetails['WH_hgg']      =  [sigFile.replace('$PROC',"wh"),sigWS,'hggpdfsmrel_%dTeV_wh_$CHANNEL'%sqrts]
    fileDetails['ZH_hgg']      =  [sigFile.replace('$PROC',"zh"),sigWS,'hggpdfsmrel_%dTeV_zh_$CHANNEL'%sqrts]
  else:
    fileDetails['VH']          =  [sigFile.replace('$PROC',"wzh"),sigWS,'hggpdfsmrel_%dTeV_wzh_$CHANNEL'%sqrts]
###############################################################################

###############################################################################
## THEORY SYSTEMATIC SETUP & TOOL #############################################
###############################################################################
# theory systematics arr=[up,down]
# --> globe info these come in specific types (as must be correlated with combination)
# -- globe info  - see https://twiki.cern.ch/twiki/bin/viewauth/CMS/HiggsWG/HiggsCombinationConventions
theorySyst = {}
#theorySyst['scaleWeight'] = [1,2,3,4,6,8,"replicas"] #5,7 unphysical
theorySyst['scaleWeight'] = [[1,2],[3,6],[4,8],"asym"] #5,7 unphysical
theorySyst['alphaSWeight'] = [[0,1],"asym"]
theorySyst['pdfWeight'] = [[0,60],"sym"]

theorySystAbsScale={}
#theorySystAbsScale['names'] = ["QCDscale_qqbar_up","QCDscale_gg_up","QCDscale_qqbar_down","QCDscale_gg_down","pdf_alphaS_qqbar","pdf_alphaS_gg"] #QCD scale up, QCD scale down, PDF+alpha S, PDF, alpha S
#theorySystAbsScale['names_to_consider'] = ["QCDscale_qqbar_up","QCDscale_gg_up","QCDscale_qqbar_down","QCDscale_gg_down","pdf_alphaS_qqbar","pdf_alphaS_gg"]  
#theorySystAbsScale['names'] = ["QCDscale_qqbar_up","QCDscale_gg_up","QCDscale_qqbar_down","QCDscale_gg_down","pdf_alphaS_qqbar","pdf_alphaS_gg"] 
#theorySystAbsScale['names_to_consider'] =   ["QCDscale_ggH_up",  "QCDscale_qqH_up",  "QCDscale_VH_up",  "QCDscale_ttH_up",  "QCDscale_ggH_down",  "QCDscale_qqH_down",  "QCDscale_VH_down",  "QCDscale_ttH_down",  "pdf_Higgs_qqbar",  "pdf_alphaS_gg",  "pdf_alphaS_ttH"] #QCD scale up, QCD scale down, PDF+alpha S, PDF, alpha S 
theorySystAbsScale['names'] =   ["QCDscale_ggH_up",  "QCDscale_qqH_up",  "QCDscale_VH_up",  "QCDscale_ttH_up",  "QCDscale_ggH_down",  "QCDscale_qqH_down",  "QCDscale_VH_down",  "QCDscale_ttH_down",  "pdf_Higgs_qqbar",  "pdf_Higgs_gg",  "pdf_Higgs_ttH"] #QCD scale up, QCD scale down, PDF+alpha S, PDF, alpha S 
theorySystAbsScale['ttH_hgg'] = [0.0,                 0.0,                0.0,               0.058,              0.0,                   0.0,                 0.0,                 -0.092,               0.0,                0.0,              0.036] # ttH is a _qqbar process
theorySystAbsScale['ZH_lep_hgg'] =  [0.0,                 0.0,                0.038,             0.0,                0.0,                   0.0,                 -0.03,               0.0,                  0.016,              0.0,              0.0] # WH is a _qqbar process
theorySystAbsScale['ZH_had_hgg'] =  [0.0,                 0.0,                0.038,             0.0,                0.0,                   0.0,                 -0.03,               0.0,                  0.016,              0.0,              0.0] # WH is a _qqbar process
theorySystAbsScale['WH_lep_hgg'] =  [0.0,                 0.0,                0.005,             0.0,                0.0,                   0.0,                 -0.007,              0.0,                  0.019,              0.0,              0.0] # ZH is a _qqbar process
theorySystAbsScale['WH_had_hgg'] =  [0.0,                 0.0,                0.005,             0.0,                0.0,                   0.0,                 -0.007,              0.0,                  0.019,              0.0,              0.0] # ZH is a _qqbar process
theorySystAbsScale['qqH_hgg'] = [0.0,                 0.004,              0.0,               0.0,                0.0,                   -0.003,              0.0,                 0.0,                  0.021,              0.0,              0.0] # qqH is a _qqbar process
theorySystAbsScale['bbH_hgg'] = [0.0,                 0.0,                0.0,               0.202,              0.0,                   0.0,                 0.0,                 -0.239,               0.0,                0.0,              0.036] # ttH is a _qqbar process
theorySystAbsScale['tHq_hgg'] = [0.0,                 0.0,                0.0,               0.065,              0.0,                   0.0,                 0.0,                 -0.149,               0.0,                0.0,              0.036] # ttH is a _qqbar process
theorySystAbsScale['tHW_hgg'] = [0.0,                 0.0,                0.0,               0.049,              0.0,                   0.0,                 0.0,                 -0.067,               0.0,                0.0,              0.036] # ttH is a _qqbar process
theorySystAbsScale['ggH_hgg'] = [0.039,               0.0,                0.0,               0.0,                -0.039,               0.0,                  0.0,                 0.0,                  0.0,                0.032,            0.0] # GGH is a _gg process

##############################################################################
## Calculate overall effect of theory systematics
##############################################################################
result ={}
mass = inWS.var("CMS_hgg_mass")
norm_factors_file = open('norm_factors_new.py','w')
inclusiveCats = list(options.cats) #need the list() otherwise NoTag will also be appended to options.cats
inclusiveCats.append("NoTag")
for proc in options.procs:
  if proc in bkgProcs: continue
  for name in theorySyst.keys(): #wh_130_13TeV_UntaggedTag_1_pdfWeights
    norm_factors_file.write("%s_%s = ["%(proc,name.replace("Weight",""))) 
    result["%s_%s"%(proc,name)] = []
    n=-1
    while (n>=-1): 
      n=n+1
      runningTotal_nom=0
      runningTotal_up=0
      weight = r.RooRealVar("weight","weight",0)
      weight_up = inWS.var("%s_%d"%(name,n)) # eg pdfWeight_1
      if (weight_up==None) : 
        n=-999
        continue # this will break the while loop, so we just stop when we are out of pdfWeights, scaleWeights or alphaSWeights 
      weight_central = inWS.var("centralObjectWeight") 
      weight_sumW = inWS.var("sumW")
      for cat in inclusiveCats:
        #print "---> this is proc ", proc, "look for", "%s_%d_13TeV_%s_pdfWeights"%(combProc.keys()[combProc.values().index(proc)],options.mass,cat) 
        data_nominal= inWS.data("%s_%d_13TeV_%s_pdfWeights"%(combProc.keys()[combProc.values().index(proc)],options.mass,cat))
        data_nominal_sum = data_nominal.sumEntries()
        data_up = data_nominal.emptyClone();
        data_nominal_new = data_nominal.emptyClone();
        zeroWeightEvents=0.
        for i in range(0,int(data_nominal.numEntries())):
           mass.setVal(data_nominal.get(i).getRealValue("CMS_hgg_mass"))
           w_nominal =data_nominal.weight()
           w_up = data_nominal.get(i).getRealValue("%s_%d"%(name,n))
           w_central = data_nominal.get(i).getRealValue("scaleWeight_0") #sneaky fix as it doesn't look like central weight is beign propagated correctly in these cases.
           sumW = data_nominal.get(i).getRealValue("sumW")
           if (w_central) : print name, n, proc, cat, "entry ", i, " w_nominal ", w_nominal, " w_central " , w_central, " w_up ", w_up , " w_nominal*(w_up/w_central) ", w_nominal*(w_up/w_central)
           if (abs(w_central)<1E-4 or abs(w_nominal)<1E-4 or w_nominal<=0. or math.isnan(w_up) or w_central<=0. or w_up<=0. or w_up>10.0): continue
           weight_up.setVal(w_nominal*(w_up/w_central))
           data_up.add(r.RooArgSet(mass,weight_up),weight_up.getVal())
           data_nominal_new.add(r.RooArgSet(mass,weight),w_nominal)
        runningTotal_nom_old = runningTotal_nom
        runningTotal_up_old = runningTotal_up
        runningTotal_nom =runningTotal_nom + data_nominal.sumEntries() 
        runningTotal_up =runningTotal_up + data_up.sumEntries()
        if (runningTotal_nom): effect =runningTotal_up/runningTotal_nom
        else: effect =-1
        print name, n, proc, cat, " runningTotal_up ", runningTotal_up, " runningTotal_up_old ", runningTotal_up_old, " data_up.sumEntries() ", data_up.sumEntries() , "runningTotal_nom", runningTotal_nom, " runningTotal_nom_old ", runningTotal_nom_old , " data_nominal.sumEntries() ",  data_nominal.sumEntries(), " effect ", effect
      effect=-1
      if (runningTotal_nom==runningTotal_up): effect=1
      else: effect = runningTotal_up/runningTotal_nom
      print " effect of %s_%d "%(name,n), "on %s"%(proc) ," is %.3f"%( effect)
      if (effect <0.5 or effect > 2.0) : 
        #exit ("effect is greater than a factor of two - shouldn't happen, exiting...")
        print "effect is greater than a factor of two - shouldn't happen, exiting...\n"
      if (n==0) :norm_factors_file.write(" %.3f"%effect)
      else: norm_factors_file.write(", %.3f"%effect)
      result["%s_%s"%(proc,name)].append(effect)
    norm_factors_file.write("]\n")
    #print result
#exit(1)
norm_factors_file.close()
theoryNormFactors=result
  
#yprinting function
def printTheorySysts():
  # as these are antisymmetric lnN systematics - implement as [1/(1.+err_down)] for the lower and [1.+err_up] for the upper
  print '[INFO] Theory...'
  for systName, systDetails in theorySyst.items():
    print "[INFO] processing ", systName ," from list ",theorySyst
    if "replicas" in systDetails[-1] :
        name="CMS_hgg_"+systName
        if (not "Theory" in allSystList ) :allSystList.append("Theory")
        if (not options.justThisSyst=="") :
          if (not options.justThisSyst=="Theory"): continue
        outFile.write('%-35s  lnN   '%(name))
        for c in options.cats:
          for p in options.procs:
            if "bkg" in flashggProc[p] or "BBH" in flashggProc[p] or "THQ" in flashggProc[p] or "THW" in flashggProc[p] or (('QCDscale' in systName or 'scaleWeight' in systName) and options.newGghScheme):
              outFile.write('- ')
              continue
            else:
              outFile.write(getFlashggLineTheoryEnvelope(flashggProc[p],c,systName,systDetails))
        outFile.write('\n')
    else: #sym or asym uncertainties
      #print "consider ", systName
      asymmetric=("asym" in systDetails[-1])
      if asymmetric:
        iteration_list=systDetails[:-1]
      else:
        iteration_list=[]
        for a in range(systDetails[0][0],systDetails[0][1]):
          iteration_list.append([a,0])

      #print "THIS SYST: ", systName ," is assymetric ? ", asymmetric, " and we will iterate over ", iteration_list 
      factor=1.0
      if "alphaS" in systName: factor=1.5
      for it in iteration_list:
        i=it[0]
        j=it[1]
        name="CMS_hgg_"+systName+"_"+str(iteration_list.index(it))
        if (not "Theory" in allSystList ) :allSystList.append("Theory")
        if (not options.justThisSyst=="") :
          if (not options.justThisSyst=="Theory"): continue
        if (i%1==0) : print "[INFO] processing ", name
        outFile.write('%-35s  lnN   '%(name))
        for c in options.cats:
          for p in options.procs:
            #with new WG1 prescription, specific other nuisances deal with ggH theory uncerts
            if "bkg" in flashggProc[p] or "BBH" in flashggProc[p] or "THQ" in flashggProc[p] or "THW" in flashggProc[p] or ('scaleWeight' in systName and options.newGghScheme and 'ggH' in p):
              outFile.write('- ')
              continue
            else:
              outFile.write(getFlashggLineTheoryWeights(flashggProc[p],c,systName,i,asymmetric,j,factor))
        if '%s:%s'%(p,c) in options.toSkip: continue
        outFile.write('\n')
      outFile.write('\n')
  
  #absolute scales for theory uncertainties.
  for syst in theorySystAbsScale['names'] :
    #with new WG1 prescription, specific other nuisances deal with ggH theory uncerts
    if 'QCDscale_ggH' in syst and options.newGghScheme: continue
    if (not "Theory" in allSystList ) :allSystList.append("Theory")
    if (not options.justThisSyst=="") :
      if (not options.justThisSyst=="Theory"): continue
    #print  "DEBUG consider name ", syst
    asymmetric= False
    if "_up" in syst : asymmetric= True
    if "_down" in syst : continue #already considered as part of "_up"
    outFile.write('%-35s  lnN   '%(syst.replace("_up",""))) # if it doesn;t contain "_up", the replace has no effect anyway 
    for c in options.cats:
      for p in options.procs:
            #if "bkg" in flashggProc[p] or "BBH" in flashggProc[p] or "THQ" in flashggProc[p] or "THW" in flashggProc[p]:
            if "bkg" in flashggProc[p]:
              outFile.write('- ')
              continue
            else:
              value = 1+theorySystAbsScale[p][theorySystAbsScale['names'].index(syst)] 
              if asymmetric :
                valueDown = 1+theorySystAbsScale[p][theorySystAbsScale['names'].index(syst.replace("_up","_down"))]
                if value==1.0 and valueDown==1.0 :
                  outFile.write("- ")
                else:
                  outFile.write("%1.3f/%1.3f "%(value,valueDown))
              else :
                if value==1.0 :
                  outFile.write("- ")
                else:
                  outFile.write("%1.3f "%(value))
    outFile.write('\n')


## pdf weights printing tool 
def getFlashggLineTheoryWeights(proc,cat,name,i,asymmetric,j=0,factor=1):
  n = i
  m = i
  ad_hoc_factor =1.
  #theoryNormFactor_n=1. #up
  #theoryNormFactor_m=1. #down
  if ( asymmetric ) :
    "SINCE WE are looking at syst ", name , " we apply an ad-hoc factor of ", factor
    ad_hoc_factor=factor
    m = j
  theoryNormFactor_n= 1/theoryNormFactors["%s_%s"%(combProc[proc],name)][n] #up
  theoryNormFactor_m= 1/theoryNormFactors["%s_%s"%(combProc[proc],name)][m] #up
  
  mass = inWS.var("CMS_hgg_mass")
  weight = r.RooRealVar("weight","weight",0)
  weight_up = inWS.var("%s_%d"%(name,n))
  weight_down = inWS.var("%s_%d"%(name,m))
  weight_central = inWS.var("centralObjectWeight") 
  weight_sumW = inWS.var("sumW") 
  #data_nominal = inWS.data("%s_%d_13TeV_%s"%(proc,options.mass,cat))
  data_nominal= inWS.data("%s_%d_13TeV_%s_pdfWeights"%(proc,options.mass,cat))
  data_nominal_sum = data_nominal.sumEntries()
  if (data_nominal_sum <= 0.):
      print "[WARNING] This dataset has 0 or negative sum of weight. Systematic calulcxation meaningless, so list as '- '"
      line = '- '
      return line
  #data_nominal_num = data_nominal.numEntries()
  data_up = data_nominal.emptyClone();
  data_down = data_nominal.emptyClone();
  data_nominal_new = data_nominal.emptyClone();
  zeroWeightEvents=0.
  for i in range(0,int(data_nominal.numEntries())):
    
    mass.setVal(data_nominal.get(i).getRealValue("CMS_hgg_mass"))
    w_nominal =data_nominal.weight()
    w_up = theoryNormFactor_n*data_nominal.get(i).getRealValue("%s_%d"%(name,n))
    w_down = theoryNormFactor_m*data_nominal.get(i).getRealValue("%s_%d"%(name,m))
    #w_central = data_nominal.get(i).getRealValue(weight_central.GetName())
    w_central = data_nominal.get(i).getRealValue("scaleWeight_0") #sneaky fix as it doesn't look like central weight is beign propagated correctly in these cases.
    sumW = data_nominal.get(i).getRealValue("sumW")
    if (w_central<=0. or w_nominal<=0. or math.isnan(w_down) or math.isnan(w_up) or w_down<=0. or w_up<=0.): 
        zeroWeightEvents=zeroWeightEvents+1.0
        if (zeroWeightEvents%1==0):
          print "[WARNING] skipping one event where weight is identically 0 or nan, causing  a seg fault, occured in ",(zeroWeightEvents/data_nominal.numEntries())*100 , " percent of events"
          #print " WARNING] syst ", name,n, " ","procs/cat  " , proc,",",cat , " entry " , i, " w_nom ", w_nominal , "  w_up " , w_up , " w_down ", w_down ,"w_central ", w_central
          #exit(1)
        continue
    elif ( abs(w_central/w_down) <0.01 or abs(w_central/w_down) >100 ) :
        zeroWeightEvents=zeroWeightEvents+1.0
        #if (zeroWeightEvents%1000==0):
          #print "[WARNING] skipping one event where weight is identically 0 or nan, causing  a seg fault, occured in ",(zeroWeightEvents/data_nominal.numEntries())*100 , " percent of events"
          #print " WARNING] syst ", name,n, " ","procs/cat  " , proc,",",cat , " entry " , i, " w_nom ", w_nominal , "  w_up " , w_up , " w_down ", w_down ,"w_central ", w_central
          #exit(1)
        continue
    print " WARNING] syst ", name,n, " ","procs/cat  " , proc,",",cat , " entry " , i, " w_nom ", w_nominal , "  w_up " , w_up , " w_down ", w_down ,"w_central ", w_central, " theoryNormFactor_m ", theoryNormFactor_m , " theoryNormFactor_n ", theoryNormFactor_n, " w_nominal*(w_down/w_central) " , w_nominal*(w_down/w_central) , " w_nominal*(w_up/w_central) " , w_nominal*(w_up/w_central)
    weight_down.setVal(w_nominal*(w_down/w_central))
    weight_up.setVal(w_nominal*(w_up/w_central))
    data_up.add(r.RooArgSet(mass,weight_up),weight_up.getVal())
    data_down.add(r.RooArgSet(mass,weight_down),weight_down.getVal())
    data_nominal_new.add(r.RooArgSet(mass,weight),w_nominal)
  if (data_up.sumEntries() <= 0. or data_down.sumEntries() <= 0. ):
      print "[WARNING] This dataset has 0 or negative sum of weight. Systematic calulcxation meaningless, so list as '- '"
      line = '- '
      return line
  systVals = interp1SigmaDataset(data_nominal_new,data_down,data_up,ad_hoc_factor)
  if (math.isnan(systVals[0]) or math.isnan(systVals[1]) or systVals[0]<0.6 or systVals[1]<0.6 ): 
    print "ERROR look at the value of these uncertainties!! systVals[0] ", systVals[0], " systVals[1] ", systVals[1]
    #print "data Nominal"
    #data_nominal_new.Print()
    #print "data down "
    #data_down.Print()
    #print "data up "
    #data_up.Print()
    #exit (1)
  if (systVals[0] >10) : 
    print "ERROR look at the value of these uncertainties!! systVals[0] ", systVals[0], " systVals[1] ", systVals[1]
    #print "data_nominal_new"
    #data_nominal_new.Print()
    #print "data_down"
    #data_down.Print()
    #print "data_up"
    #data_up.Print()
    #print "ad_hoc_factor"
    #ad_hoc_factor
    #exit (1)
  if ((systVals[1] >10)) : 
    #print "data_nominal_new"
    #data_nominal_new.Print()
    #print "data_down"
    d#ata_down.Print()
    #print "data_up"
    #data_up.Print()
    #print "ad_hoc_factor"
    #ad_hoc_factor
    print "ERROR look at the value of these uncertainties!! systVals[0] ", systVals[0], " systVals[1] ", systVals[1]
    #exit (1)
  if systVals[0]==1 and systVals[1]==1:
      line = '- '
  elif (asymmetric):
      if systVals[0] < 1 and systVals[1] <1 :
        print "alpha S --- both systVals[0] ", systVals[0] , " and systVals[1] ", systVals[1] , " are less than 1 !"
        #print "data_nominal_new"
        #data_nominal_new.Print()
        #print "data_down"
        #data_down.Print()
        #print "data_up"
        #data_up.Print()
        #print "ad_hoc_factor", ad_hoc_factor
        #exit(1)
      line = '%5.3f/%5.3f '%(systVals[0],systVals[1])
  else : #symmetric
      line = '%5.3f '%(systVals[0])
  #print " summary tag " , cat , "  proc ", proc, " value ", line 
  return line

## envelope computation, for Theory scale weights
def getFlashggLineTheoryEnvelope(proc,cat,name,details):
  
  #print "consider proc ", proc, " cat ", cat , " name ", name , " detail ", details
  #print "DEBug cat ", cat
  #if "Untagged" in cat : return " - "
  indices=details[0:-1] # skip last entry whcuh is text specifying the treatment of uncertainty eg "replicas"
  histograms=[]
  h_nominal =None
  nBins=80
  
  for iReplica in indices:
    data_nominal = inWS.data("%s_%d_13TeV_%s"%(proc,options.mass,cat)) #FIXME
    data_nominal_num = data_nominal.numEntries()
    data_new_h = r.TH1F("h_%d"%iReplica,"h_%d"%iReplica,nBins,100,180);
    data_nom_h = r.TH1F("h_nom_%d"%iReplica,"h_nom_%d"%iReplica,nBins,100,180);
    mass = inWS.var("CMS_hgg_mass")
    weight = r.RooRealVar("weight","weight",0)
    weight_new = inWS.var("%s_%d"%(name,iReplica))
    theoryNormFactor=1.0
    if (options.theoryNormFactors != ""):
       values = eval("th_norm.%s_%s"%(proc,name.replace("Weight","")))
       theoryNormFactor= 1/values[iReplica]

    weight_central = inWS.var("centralObjectWeight")
    zeroWeightEvents=0.;
    for i in range(0,int(data_nominal.numEntries())):
      mass.setVal(data_nominal.get(i).getRealValue("CMS_hgg_mass"))
      mass.setBins(100)
      w_nominal =data_nominal.weight()
      w_new = theoryNormFactor*data_nominal.get(i).getRealValue("%s_%d"%(name,iReplica))
      w_central = data_nominal.get(i).getRealValue("scaleWeight_0")
      if (w_central==0. or w_nominal==0. or math.isnan(w_new) or w_new==0.):
        zeroWeightEvents=zeroWeightEvents+1.0
        if (zeroWeightEvents%1000==0):
          print "[WARNING] skipping one event where weight is identically 0, causing  a seg fault, occured in ",(zeroWeightEvents/data_nominal.numEntries())*100 , " percent of events"
          #print " [WARNING] procs/cat  " , proc,",",cat , " entry " , i, " w_nom ", w_nominal , "  w_new " , w_new , "w_central ", w_central
        #exit(1)
        continue
      elif( abs(w_central/w_new) >100 or  abs(w_central/w_new) <0.01) :
        zeroWeightEvents=zeroWeightEvents+1.0
        if (zeroWeightEvents%1000==0):
          print "[WARNING] skipping one event where weight is identically 0, causing  a seg fault, occured in ",(zeroWeightEvents/data_nominal.numEntries())*100 , " percent of events"
          #print " [WARNING] procs/cat  " , proc,",",cat , " entry " , i, " w_nom ", w_nominal , "  w_new " , w_new , "w_central ", w_central
        exit(1)
        continue
      weight_new.setVal(w_nominal*(w_new/w_central))
      data_new_h.Fill(mass.getVal(),weight_new.getVal())
      data_nom_h.Fill(mass.getVal(),w_nominal)
    histograms.append(data_new_h)
    if (h_nominal==None) : h_nominal=data_nom_h
  
  h_min = r.TH1F("h_min","h_min",nBins,100,180);
  h_max = r.TH1F("h_max","h_max",nBins,100,180);
  array ={}
  for iBin in range(0, h_min.GetNbinsX()): 
    array[iBin]=[]
    for iRep in range(0,len(indices)):
      content=histograms[iRep].GetBinContent(iRep)
      array[iBin].append(histograms[iRep].GetBinContent(iBin))
    h_min.SetBinContent(iBin,min(array[iBin]))
    h_max.SetBinContent(iBin,max(array[iBin]))

  systVals = interp1Sigma(h_nominal,h_min,h_max)
  if (systVals[0]<0.2 or  systVals[1]<0.2):
    print "[ERROR] Look at these histograms because systVals[0]= ", systVals[0], " or systVals[1]= ",systVals[1]," :"
    print "h_nominal ", h_nominal.GetEntries(), " (", h_nominal.Integral(),")";
    print "h_min ", h_min.GetEntries(), " (", h_min.Integral(),")";
    print "h_max ", h_max.GetEntries(), " (", h_max.Integral(),")";
    exit(1)
  if (systVals[0]>2. or  systVals[1]>2.):
    print "[ERROR] Look at these histograms because systVals[0]= ", systVals[0], " or systVals[1]= ",systVals[1]," :"
    print "h_nominal ", h_nominal.GetEntries(), " (", h_nominal.Integral(),")";
    print "h_min ", h_min.GetEntries(), " (", h_min.Integral(),")";
    print "h_max ", h_max.GetEntries(), " (", h_max.Integral(),")";
    if(h_nominal.Integral() <0. or  h_min.Integral() <0. or  h_max.Integral()<0.): 
        line = '- '
    else :
      print "ERROR large weight"
      exit(1)
    return line

  if systVals[0]==1 and systVals[1]==1:
        line = '- '
  else:
        line = '%5.3f/%5.3f '%(systVals[0],systVals[1])
  return line
###############################################################################

###############################################################################
## GENERAL ANALYSIS SYSTEMATIC SETUP  #########################################
###############################################################################
# BR uncertainty
brSyst = [0.0206,-0.0208] #13TeV Values, from YR4 taking  in quadrature THU (+1.73 -1.72), PU(mq) (+0.93,-0.99) , PU(as) (+0.61 -0.62)
# lumi syst
####lumiSyst = 0.026 #8TeV Values
#lumiSyst=0.062  #Correct for ICHEP 
lumiSyst=0.025  #Correct for Moriond17

##Printing Functions
def printBRSyst():
  print '[INFO] BR...'
  #outFile.write('%-35s   lnN   '%('CMS_hgg_BR'))
  outFile.write('%-35s   lnN   '%('BR_hgg'))
  for c in options.cats:
    for p in options.procs:
      if '%s:%s'%(p,c) in options.toSkip: continue
      if p in bkgProcs:
        outFile.write('- ')
      else:
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

def printUEPSSyst():
  print '[INFO] UEPS...'
  if options.uepsfilename=="none": options.uepsfilename=""
  if options.uepsfilename=="" and not os.path.isfile('ueps_lines.dat'): exit("ueps_lines.dat doesn't exist - you need to either get it somehow or generate from UEPS MC files")
  elif options.uepsfilename=="" and os.path.isfile('ueps_lines.dat'):
    for line in open('ueps_lines.dat', 'r').readlines():
      outFile.write(line)
  else:
    uepsOutFile = open('ueps_lines.dat','w')
    uncertainties = ['UE','PS']
    uepsFiles = {}
    uepsFiles['UE'] = options.uepsfilename.split(',UEPS,')[0].split(',')
    print uepsFiles['UE']
    uepsFiles['PS'] = options.uepsfilename.split(',UEPS,')[1].split(',')
    print uepsFiles['PS']
    
    tpMap = {'GG2H':'ggh','VBF':'vbf','TTH':'tth','QQ2HLNU':'wh','QQ2HLL':'zh','WH2HQQ':'wh','ZH2HQQ':'zh','bkg_mass':'bkg_mass'}
    
    lines = {}

    for uncertainty in uncertainties:
      lines[uncertainty] = ''
      allValues = {}
      for proc in options.procs:
        proc = flashggProc[proc]
        procValues = {}
        for filename in uepsFiles[uncertainty]:
          if proc in filename and 'Up' in filename: 
            wsUp = (r.TFile(filename)).Get("tagsDumper/cms_hgg_13TeV")
            continue
          elif proc in filename and 'Down' in filename: 
            wsDown = (r.TFile(filename)).Get("tagsDumper/cms_hgg_13TeV")
            continue
          else: continue
        for cat in options.cats:
          if not ('GG2H' in proc or 'VBF' in proc): 
            continue
          elif not ('Untagged' in cat or 'VBF' in cat): 
            continue
          dataUp = "%s_%sUp_13TeV_%s" % (tpMap[proc],uncertainty,cat) 
          dataDown = "%s_%sDown_13TeV_%s" % (tpMap[proc],uncertainty,cat) 
          weightUp = wsUp.data(dataUp).sumEntries()
          weightDown = wsDown.data(dataDown).sumEntries()
          delta = weightUp - weightDown
          sumBoth = weightUp + weightDown
          value = 1. + (delta / sumBoth)
          procValues[cat] = value
        allValues[proc] = procValues
      for cat in options.cats:
        for proc in options.procs:
          proc = flashggProc[proc]
          if not ('GG2H' in proc or 'VBF' in proc): 
            lines[uncertainty] += '- '
            continue
          elif not ('Untagged' in cat or 'VBF' in cat): 
            lines[uncertainty] += '- '
            continue
          value = (allValues[proc])[cat]
          lines[uncertainty] += '%5.3f ' % value
      uncName = 'CMS_hgg_'+uncertainty
      print '%-35s   lnN   '%(uncName)+lines[uncertainty]
      uepsOutFile.write('%-35s   lnN   '%(uncName)+lines[uncertainty]+'\n')
      outFile.write('%-35s   lnN   '%(uncName)+lines[uncertainty]+'\n')
    uepsOutFile.write('\n')
    uepsOutFile.close()
    outFile.write('\n')
    

###############################################################################

###############################################################################
##  FLASHGG-SPECIFIC SYSTEMATIC SETUP  ########################################
###############################################################################
flashggSystDump = open('flashggSystDump.dat','w')
flashggSysts={}

# vtx eff
#vtxSyst = 0.015 
vtxSyst = 0.02 #updated for Moriond17

#photon ID
flashggSysts['MvaShift'] =  'phoIdMva'
flashggSysts['LooseMvaSF'] =  'LooseMvaSF'
flashggSysts['PreselSF']    =  'PreselSF'
flashggSysts['SigmaEOverEShift'] = 'SigmaEOverEShift'
flashggSysts['ElectronWeight'] = 'eff_e'
flashggSysts['electronVetoSF'] = 'electronVetoSF'
flashggSysts['MuonWeight'] = 'eff_m'
flashggSysts['MuonMiniIsoWeight'] = 'eff_m_MiniIso'
flashggSysts['TriggerWeight'] = 'TriggerWeight'
#flashggSysts['JetBTagWeight'] = 'eff_b'
flashggSysts['JetBTagCutWeight'] = 'eff_b'
#flashggSysts['MvaLinearSyst'] = 'MvaLinearSyst'
#flashggSysts[''] =  ''
flashggSysts['metPhoUncertainty'] = 'MET_PhotonScale'
flashggSysts['metUncUncertainty'] = 'MET_Unclustered'
flashggSysts['metJecUncertainty'] = 'MET_JEC'
flashggSysts['metJerUncertainty'] = 'MET_JER'

#new ggH uncert prescription (replaces theory, JetVeto)
if options.newGghScheme:
  flashggSysts['THU_ggH_Mu'] = 'THU_ggH_Mu'
  flashggSysts['THU_ggH_Res'] = 'THU_ggH_Res'
  flashggSysts['THU_ggH_Mig01'] = 'THU_ggH_Mig01'
  flashggSysts['THU_ggH_Mig12'] = 'THU_ggH_Mig12'
  flashggSysts['THU_ggH_VBF2j'] = 'THU_ggH_VBF2j'
  flashggSysts['THU_ggH_VBF3j'] = 'THU_ggH_VBF3j'
  flashggSysts['THU_ggH_PT60'] = 'THU_ggH_PT60'
  flashggSysts['THU_ggH_PT120'] = 'THU_ggH_PT120'
  flashggSysts['THU_ggH_qmtop'] = 'THU_ggH_qmtop'

#tth Tags
tthSysts={}
tthSysts['JEC'] = 'JEC_TTH'
tthSysts['JER'] = 'JER_TTH'
tthSysts['JetBTagReshapeWeight'] = 'BTagReshape_TTH'
btagReshapeSyst = 1.042 #ad hoc from Saranya for Moriond17, combination of various sources
#flashggSysts['regSig'] = 'n_sigmae'
#flashggSysts['idEff'] = 'n_id_eff'
#flashggSysts['triggerEff'] = 'n_trig_eff'

# pu jet eff = [ggEffect,qqEffect,WH_hggeffect,ZH_hggeffect,ttHeffect] - append for each vbf cat and for each VH hadronic cat
puJetIdEff = []

# naming is important to correlate with combination
vbfSysts={}
vbfSysts['JEC'] = [] 
#vbfSysts['UnmatchedPUWeight'] = [] #removed for Moriond17
vbfSysts['JER'] = [] 
#vbfSysts['UEPS'] =[] #superseded by new method, no longer a bin migration
#vbfSysts['RMSShift'] =[]
vbfSysts['PUJIDShift'] =[]
for dijetCat in dijetCats: #each entry will represent a different migration
   vbfSysts['JER'].append([1.,1.,1.])  #value of 1 given gor both ggh and qqh, since vairations are taken from histograms directly
   vbfSysts['JEC'].append([1.,1.,1.]) #value of 1 given gor both ggh and qqh, since vairations are taken from histograms directly
#vbfSysts['UnmatchedPUWeight'].append([1.,1.]) #should only apply to ggh<->vbf
#vbfSysts['RMSShift'].append([1.,1.]) #should only apply to ggh<->vbf
vbfSysts['PUJIDShift'].append([1.,1.]) #should only apply to ggh<->vbf
#UEPS method no longer needs these
#vbfSysts['UEPS'].append([0.077,0.071]) # adhoc for ggh<->vbf # UPDATED FOR ICHEP16
#vbfSysts['UEPS'].append([0.042,0.092]) # adhoc for vbf0<->vbf1# UPDATED FOR ICHEP16
#vbfSysts['UEPS'].append([0.042,0.092]) # adhoc by Ed in attempt to fix negative value
#still waiting for new recipe here
if not options.newGghScheme: 
  vbfSysts['JetVeto'] =[]
  vbfSysts['JetVeto'].append([0.289,0.0]) # Untagged <-> VBF, updated for (post)Moriond17
  vbfSysts['JetVeto'].append([0.077,0.0]) # VBF 0,1 <-> VBF 2, updated for (post)Moriond17
  vbfSysts['JetVeto'].append([0.031,0.0]) # VBF 0 <-> VBF 1, updated for (post)Moriond17

#lepton, MET tags  ## lepton tags not considered for Dry run...
# [VH tight, VH loose, ttH leptonic]
eleSyst = {}
muonSyst = {}
metSyst = {}
metSyst['ggH_hgg'] = [0.,0.,0.04] #not used for ICHEP16
metSyst['qqH_hgg'] = [0.,0.,0.04]#not used for ICHEP16
#metSyst['VH'] = [0.012,0.019,0.026] #not used for ICHEP16
metSyst['ZH_hgg'] = [0.012,0.019,0.026] #not used for ICHEP16
metSyst['WH_hgg_hgg'] = [0.012,0.019,0.026] #not used for ICHEP16
metSyst['ttH_hgg'] = [0.011,0.012,0.040]#not used for ICHEP16
#tth tags  ## lepton tags not considered for Dry run...
# syst for tth tags - [ttHlep,tthHad]
###tth tags not considered for dry run
#btagSyst={}
ggHforttHSysts = {}

# spec for ggh in tth cats - [MC_low_stat,gluon_splitting,parton_shower]
ggHforttHSysts['CMS_hgg_tth_mc_low_stat'] = 0.10 ##FIXME needs double checking for Moriond17
ggHforttHSysts['CMS_hgg_tth_gluon_splitting'] = 0.52 #re-evaluated for Moriond17, using TOP-16-010
ggHforttHSysts['CMS_hgg_tth_parton_shower'] = 0.35 #updated for Moriond17

# rate adjustments
tthLepRateScale = 1.0 #not used for ICHEP16
tthHadRateScale = 1.0 #not used for ICHEP16
###############################################################################

###############################################################################
##  INTERPOLATION TOOLS #######################################################
###############################################################################
def interp1Sigma(th1f_nom,th1f_down,th1f_up,factor=1.):
  nomE = th1f_nom.Integral()
  if th1f_down.Integral()<0 or nomE-th1f_up.Integral()<0  :
    return [1.000,1.000]
  if abs(nomE)< 1.e-6 or abs(nomE-th1f_down.Integral())<1.e-6 or abs(nomE-th1f_up.Integral())<1.e-6  :
    return [1.000,1.000]
  downE = 1+ factor*((th1f_down.Integral() - nomE) /nomE)
  upE = 1+ factor*((th1f_up.Integral() - nomE) /nomE)
  if options.quadInterpolate!=0:
    downE = quadInterpolate(-1.,-1.*options.quadInterpolate,0.,1.*options.quadInterpolate,th1f_down.Integral(),th1f_nom.Integral(),th1f_up.Integral())
    upE = quadInterpolate(1.,-1.*options.quadInterpolate,0.,1.*options.quadInterpolate,th1f_down.Integral(),th1f_nom.Integral(),th1f_up.Integral())
    if upE != upE: upE=1.000
    if downE != downE: downE=1.000
  return [downE,upE]

def interp1SigmaDataset(d_nom,d_down,d_up,factor=1.):
  nomE = d_nom.sumEntries()
  #if abs(nomE)< 1.e-6 or d_down.sumEntries()<0 or d_up.sumEntries()<0 or abs(nomE -d_down.sumEntries())<1.e-6 or abs(nomE -d_up.sumEntries())<1.e-6:
  if nomE<1.e-6 or d_down.sumEntries()<0 or d_up.sumEntries()<0 or abs(nomE -d_down.sumEntries())<1.e-6 or abs(nomE -d_up.sumEntries())<1.e-6:
    return [1.000,1.000]
  downE = 1+ factor*((d_down.sumEntries() - nomE) /nomE)
  upE = 1+ factor*((d_up.sumEntries() - nomE) /nomE)
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
      file = info[0].replace('$CAT','%s'%c)
      wsname = info[1]
      pdfname = info[2].replace('$CHANNEL','%s'%c)
      if typ not in options.procs and typ!='data_obs': continue
      #outFile.write('shapes %-10s %-15s %-30s %-30s\n'%(typ,'%s_%dTeV'%(c,sqrts),file.replace(".root","_%s_%s.root"%(typ,c)),wsname+':'+pdfname))
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
def getReweightedDataset(dataNOMINAL,syst):
  asymmetric=True 
  eventweight=True
  #could expand this to make it more general, eg no asym or not eventweight
  
  if (asymmetric and eventweight) : 
    data_up = dataNOMINAL.emptyClone();
    data_down = dataNOMINAL.emptyClone();
    data_nominal = dataNOMINAL.emptyClone();
    mass = inWS.var("CMS_hgg_mass")
    weight = r.RooRealVar("weight","weight",0)
    weight_up = inWS.var("%sUp01sigma"%syst)
    #weight_down = inWS.var("%sDown01sigma"%sys)
    weight_down = r.RooRealVar("%sDown01sigma"%syst,"%sDown01sigma"%syst,-1.)
    weight_central = inWS.var("centralObjectWeight")
    zeroWeightEvents=0.
    for i in range(0,int(dataNOMINAL.numEntries())):
      mass.setVal(dataNOMINAL.get(i).getRealValue("CMS_hgg_mass"))
      w_nominal =dataNOMINAL.weight()
      w_down = dataNOMINAL.get(i).getRealValue(weight_down.GetName())
      w_up = dataNOMINAL.get(i).getRealValue(weight_up.GetName())
      w_central = dataNOMINAL.get(i).getRealValue(weight_central.GetName())
      if (w_central==0.) :
        zeroWeightEvents=zeroWeightEvents+1.0
        if (zeroWeightEvents%1==0):
          print "[WARNING] skipping one event where weight is identically 0, causing  a seg fault, occured in ",(zeroWeightEvents/dataNOMINAL.numEntries())*100 , " percent of events"
          #print "[WARNING]  syst " , syst , " w_nom ", w_nominal , "  w_up " , w_up , " w_ down " , w_down, "w_central ", w_central
          #exit(1)
        continue
      if (w_up==w_down):
        weight_down.setVal(w_nominal)
        weight_up.setVal(w_nominal)
      else :
        weight_down.setVal(w_nominal*(w_down/w_central))
        weight_up.setVal(w_nominal*(w_up/w_central))

      data_up.add(r.RooArgSet(mass,weight_up),weight_up.getVal())
      data_down.add(r.RooArgSet(mass,weight_down),weight_down.getVal())
      data_nominal.add(r.RooArgSet(mass,weight),w_nominal)
    dataUP =  data_up  #repalce UP/DOwn histograms defined outside scope of this "if"
    dataDOWN =  data_down  #repalce UP/DOwn histograms defined outside scope of this "if"
    dataNOMINAL =  data_nominal  #repalce UP/DOwn histograms defined outside scope of this "if"
    return [dataDOWN,dataNOMINAL,dataUP]

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
  dataSYMMETRIC =  inWS.data("%s_%d_13TeV_%s_%s"%(flashggProc[proc],options.mass,cat,syst)) #Will exist if the systematic is a symmetric uncertainty not stored as event weights
  dataDOWN =  inWS.data("%s_%d_13TeV_%s_%sDown01sigma"%(flashggProc[proc],options.mass,cat,syst)) # will exist if teh systematic is an asymetric uncertainty not strore as event weights
  dataUP =  inWS.data("%s_%d_13TeV_%s_%sUp01sigma"%(flashggProc[proc],options.mass,cat,syst))# will exist if teh systematic is an asymetric uncertainty not strore as event weights
  dataNOMINAL =  inWS.data("%s_%d_13TeV_%s"%(flashggProc[proc],options.mass,cat)) #Nominal RooDataSet,. May contain required weights if UP/DOWN/SYMMETRIC roodatahists do not exist (ie systematic stored as event weigths)
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
    data_nominal = dataNOMINAL.emptyClone();
    mass = inWS.var("CMS_hgg_mass")
    weight = r.RooRealVar("weight","weight",0)
    weight_up = inWS.var("%sUp01sigma"%syst)
    #weight_down = inWS.var("%sDown01sigma"%sys)
    weight_down = r.RooRealVar("%sDown01sigma"%syst,"%sDown01sigma"%syst,-1.)
    weight_central = inWS.var("centralObjectWeight")
    zeroWeightEvents=0.
    for i in range(0,int(dataNOMINAL.numEntries())):
      mass.setVal(dataNOMINAL.get(i).getRealValue("CMS_hgg_mass"))
      w_nominal =dataNOMINAL.weight()
      w_down = dataNOMINAL.get(i).getRealValue(weight_down.GetName())
      w_up = dataNOMINAL.get(i).getRealValue(weight_up.GetName())
      w_central = dataNOMINAL.get(i).getRealValue(weight_central.GetName())
      #print "[WARNING]  syst " , syst , " w_nom ", w_nominal , "  w_up " , w_up , " w_ down " , w_down, "w_central ", w_central
      if (w_central==0.) :
        zeroWeightEvents=zeroWeightEvents+1.0
        if (zeroWeightEvents%1==0):
          print "[WARNING] skipping one event where weight is identically 0, causing  a seg fault, occured in ",(zeroWeightEvents/dataNOMINAL.numEntries())*100 , " percent of events"
          #print "[WARNING]  syst " , syst , " w_nom ", w_nominal , "  w_up " , w_up , " w_ down " , w_down, "w_central ", w_central
          #exit(1)
        continue
      if (w_up==w_down):
        weight_down.setVal(w_nominal)
        weight_up.setVal(w_nominal)
      else :
        weight_down.setVal(w_nominal*(w_down/w_central))
        weight_up.setVal(w_nominal*(w_up/w_central))

      data_up.add(r.RooArgSet(mass,weight_up),weight_up.getVal())
      data_down.add(r.RooArgSet(mass,weight_down),weight_down.getVal())
      data_nominal.add(r.RooArgSet(mass,weight),w_nominal)
    dataUP =  data_up  #repalce UP/DOwn histograms defined outside scope of this "if"
    dataDOWN =  data_down  #repalce UP/DOwn histograms defined outside scope of this "if"
    dataNOMINAL =  data_nominal  #repalce UP/DOwn histograms defined outside scope of this "if"

  systVals = interp1SigmaDataset(dataNOMINAL,dataDOWN,dataUP)
  flashggSystDump.write('%s nominal: %5.3f up: %5.3f down: %5.3f vals: [%5.3f,%5.3f] \n'%(syst,dataNOMINAL.sumEntries(),dataUP.sumEntries(),dataDOWN.sumEntries(),systVals[0],systVals[1]))
  #print "systvals ", systVals 
  if systVals[0]<0.0 or systVals[1]<0.0:
    print "[ERROR] YOU HAVE A NEGATIVE SYSTEMATIC... systVals[0]= ",systVals[0], " systVals[1]= ", systVals[1]
    print "syst ", syst, " for ", dataNOMINAL.GetName()
    print "NOMINAL"
    dataNOMINAL.Print()
    print" dataUP"
    dataUP.Print()
    print "dataDOWN"
    dataDOWN.Print()
    exit(1)
  if systVals[0]==1 and systVals[1]==1:
      line = '- '
  else:
      line = '%5.3f/%5.3f '%(systVals[0],systVals[1])
  return line

# printing whole lines 
def printFlashggSysts():
  print '[INFO] lnN lines...'
  for flashggSyst, paramSyst in flashggSysts.items():
      
      name='CMS_hgg_%s'%paramSyst
      if 'eff' in paramSyst:
        name='CMS_%s'%paramSyst
      print "[INFO] processing " ,name
      allSystList.append(name)
      if (not options.justThisSyst=="") :
          if (not options.justThisSyst==name): continue
      outFile.write('%-35s   lnN   '%(name))
      for c in options.cats:
        for p in options.procs:
          if '%s:%s'%(p,c) in options.toSkip: continue
          #print "p,c is",p,c
          if p in bkgProcs or ('pdfWeight' in flashggSyst and (p!='ggH_hgg' and p!='qqH_hgg')) or ('THU_ggH' in flashggSyst and p!='ggH_hgg'):
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
    asymweight=False
    affectsTTH=None
    if (len(vbfSystValArray)>(len(dijetCats))) : affectsTTH=True
    #print "vbfSystName, vbfSystValArray ", vbfSystName,", ", vbfSystValArray, " affects tth ? ", affectsTTH
    print "[INFO] considering: ", vbfSystName
    for migIt, vbfSystVal in (enumerate(vbfSystValArray)):
      name = "CMS_hgg_"+vbfSystName
      name += '_migration%d'%(migIt)
      allSystList.append(name)
      if (not options.justThisSyst=="") :
          if (not options.justThisSyst==name):
            print "DANGER SKIPPING 0 ", name
            continue
    
    # work out which cats we are migrating to and from
    syst=vbfSystName
    if ((not syst in options.justThisSyst) and (not options.justThisSyst=="")): 
         continue
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
    if (affectsTTH):
     vbfMigrateToCats.append(incCats)
     vbfMigrateFromCats.append(tthHadCat)
     vbfMigrateToCats.append(incCats) 
     vbfMigrateFromCats.append(tthLepCat)
    
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
          data =  inWS.data("%s_%d_13TeV_%s_%s"%(flashggProc[p],options.mass,c,syst))
          dataDOWN =  inWS.data("%s_%d_13TeV_%s_%sDown01sigma"%(flashggProc[p],options.mass,c,syst))
          dataNOMINAL =  inWS.data("%s_%d_13TeV_%s"%(flashggProc[p],options.mass,c))
          mass = inWS.var("CMS_hgg_mass")
          dataUP =  inWS.data("%s_%d_13TeV_%s_%sUp01sigma"%(flashggProc[p],options.mass,c,syst))
          
          if (data==None):
            if( (dataUP==None) or  (dataDOWN==None)) :
             if (dataNOMINAL.get().find("%sDown01sigma"%syst)):
              print "[INFO] VBF Systematic ", syst," is stored as up/down weights in nominal dataset"
              asymmetric=False
              adhoc=False
              asymweight=True
             else:
              print "[INFO] VBF Systematic ", syst," could not be found either as symmetric (",syst,") or asymmetric (",syst,"Down01sigma,",syst,"Up01sigma). Consider as adhoc variation..."
              adhoc=True
              asymmetric=False
            else:
              asymmetric=True
              print "[INFO] VBF Systematic ", syst," will be treated as asymmetric"
          else:
              asymmetric=False
              print "[INFO] VBF Systematic ", syst," wil be treated as symmetric"


          if (asymweight): 
            [DOWN,NOMINAL,UP] = getReweightedDataset(dataNOMINAL,syst)
            sumUP += UP.sumEntries()
            sumNOMINAL += NOMINAL.sumEntries()
            sumDOWN += DOWN.sumEntries()
          elif (asymmetric) :
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
          data =  inWS.data("%s_%d_13TeV_%s_%s"%(flashggProc[p],options.mass,c,syst))
          dataDOWN =  inWS.data("%s_%d_13TeV_%s_%sDown01sigma"%(flashggProc[p],options.mass,c,syst))
          dataNOMINAL =  inWS.data("%s_%d_13TeV_%s"%(flashggProc[p],options.mass,c))
          dataUP =  inWS.data("%s_%d_13TeV_%s_%sUp01sigma"%(flashggProc[p],options.mass,c,syst))
          if (asymweight): 
            [DOWN,NOMINAL,UP] = getReweightedDataset(dataNOMINAL,syst)
            sumUP += UP.sumEntries()
            sumNOMINAL += NOMINAL.sumEntries()
            sumDOWN += DOWN.sumEntries()
          elif (asymmetric) :
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
      name = "CMS_hgg_"+vbfSystName
      name += '_migration%d'%(migIt)
      allSystList.append(name)
      if (not options.justThisSyst=="") :
          if (not options.justThisSyst==name): 
            print "DANGER SKIPPING 1 ", name
            continue
      outFile.write('%-35s   lnN   '%name)
      for c in options.cats:
        for p in options.procs:
          if '%s:%s'%(p,c) in options.toSkip: continue
          if p=='ggH_hgg': thisUncert = vbfSystVal[0]
          elif p=='qqH_hgg': thisUncert = vbfSystVal[1]
          elif (p=='ttH_hgg' and affectsTTH): thisUncert = vbfSystVal[2]
          else:
            outFile.write('- ')
            continue
          if thisUncert==0:
            outFile.write('- ')
          else:
            if c in vbfMigrateToCats[migIt]:
              if (asymmetric or asymweight) : 
                UP=vbfMigrateToEvCountUP[p][migIt]/vbfMigrateToEvCountNOMINAL[p][migIt]
                DOWN=vbfMigrateToEvCountDOWN[p][migIt]/vbfMigrateToEvCountNOMINAL[p][migIt]
                outFile.write('%1.4g/%1.4g '%(DOWN,UP))
              elif (adhoc) : 
                VAR=((vbfMigrateToEvCountNOMINAL[p][migIt]-thisUncert*vbfMigrateFromEvCountNOMINAL[p][migIt])/vbfMigrateToEvCountNOMINAL[p][migIt]) 
                #print " TO categories : " , VAR
                outFile.write('%1.4g '%VAR)
              else : outFile.write('%1.4g '%(vbfMigrateToEvCount[p][migIt]/vbfMigrateToEvCountNOMINAL[p][migIt]))
            elif c in vbfMigrateFromCats[migIt]:
              if (asymmetric or asymweight):
                UP=vbfMigrateFromEvCountUP[p][migIt]/vbfMigrateFromEvCountNOMINAL[p][migIt]
                DOWN=vbfMigrateFromEvCountDOWN[p][migIt]/vbfMigrateFromEvCountNOMINAL[p][migIt]
                outFile.write('%1.4g/%1.4g '%(DOWN,UP))
              elif (adhoc) :
                VAR=(1.+thisUncert)
                #print " FROM categories : " , VAR
                outFile.write('%1.4g '%VAR)
              else:
                outFile.write('%1.4g '%(VAR))
                VAR=vbfMigrateFromEvCount[p][migIt]/vbfMigrateFromEvCountNOMINAL[p][migIt]
            else:
              outFile.write('- ')
      outFile.write('\n')
    outFile.write('\n')
###############################################################################

###############################################################################
##  LEPTON SYST LINES TOOLS ###################################################
###############################################################################
def printLepSysts():
  print '[INFO] Lep...'
  # electron efficiency -- NOTE to correlate with combination change to CMS_eff_e

  # met efficiency -- NOTE to correlate with combination change to CMS_scale_met
  outFile.write('%-35s   lnN   '%('CMS_scale_met_old'))
  for c in options.cats:
    for p in options.procs:
      if '%s:%s'%(p,c) in options.toSkip: 
        outFile.write('- ')
        continue
      if p in bkgProcs or p=='ggH_hgg' or p=='qqH_hgg': 
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
  print '[INFO] TTH lnN lines...'
  for tthSyst, paramSyst in tthSysts.items():
      name='CMS_hgg_%s'%paramSyst
      allSystList.append(name)
      if (not options.justThisSyst=="") :
          if (not options.justThisSyst==name): continue
      outFile.write('%-35s   lnN   '%(name))
      for c in options.cats:
        for p in options.procs:
          if '%s:%s'%(p,c) in options.toSkip: continue
          if p in bkgProcs or ('pdfWeight' in tthSyst and (p!='ggH_hgg' and p!='qqH_hgg')):
            outFile.write('- ')
          elif c not in tthCats:
            outFile.write('- ')
          elif 'Reshape' in tthSyst:
            if 'ttH' in p and 'Hadronic' in c:
              outFile.write('%1.4g '%(btagReshapeSyst))
            else:
              outFile.write('- ')
          else:
            outFile.write(getFlashggLine(p,c,tthSyst))
      outFile.write('\n')
  outFile.write('\n')

def printSimpleTTHSysts():
  for systName, systVal in ggHforttHSysts.items():
    outFile.write('%-35s   lnN   '%systName)
    for c in options.cats:
      for p in options.procs:
        if '%s:%s'%(p,c) in options.toSkip: 
          outFile.write('- ')
          continue
        if p=='ggH_hgg' and c in tthCats:
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

print "JustThisSyst == " , options.justThisSyst
if ((options.justThisSyst== "batch_split") or options.justThisSyst==""):
  printPreamble()
  #shape systematic files
  printFileOptions()
  #obs proc/tag bins
  printObsProcBinLines()
  #nuisance param systematics
  printNuisParams()
  printMultiPdf()
  printBRSyst()
  printLumiSyst()
  #printTrigSyst() # now a weight in the main roodataset!
  printSimpleTTHSysts()

if (len(tthCats) > 0 ):  printTTHSysts()
printTheorySysts()
# lnN systematics
printFlashggSysts()
printUEPSSyst()
#catgeory migrations
#if (len(dijetCats) > 0 and len(tthCats)>0):  printVbfSysts()
if (len(dijetCats) > 0 ):  printVbfSysts()
#other 
#printLepSysts() #obsolete

print "################## all sys list #######################"
print allSystList
print "procs :" , ",".join(flashggProc[p] for p in options.procs).replace("bkg_mass","")
print "tags : " , ",".join(options.cats)
print "smears ", ",".join(options.photonCatSmears)
if options.submitSelf:
  counter=0
  os.system('mkdir -p jobs ')
  os.system('rm jobs/* ')
  for syst in allSystList:
    fname='%s/sub%d.sh'%("jobs",counter)
    f = open(fname ,'w')
    os.system('chmod +x %s'%f.name)
    counter=counter+1
    f.write('\#!/bin/bash\n')
    f.write('touch %s.run\n'%os.path.abspath(f.name))
    f.write('cd %s\n'%os.getcwd())
    f.write('eval `scramv1 runtime -sh`\n')
    execLine = '$CMSSW_BASE/src/flashggFinalFit/Datacard/makeParametricModelDatacardFLASHgg.py -i %s -o %s -p %s -c %s --photonCatScales %s --photonCatSmears %s --isMultiPdf --mass %d --justThisSyst %s'%(options.infilename,"jobs/"+options.outfilename+"."+syst,",".join(flashggProc[p] for p in options.procs).replace(",bkg_mass",""),",".join(options.cats),",".join(options.photonCatScales),",".join(options.photonCatSmears),options.mass,syst )
    f.write('if (%s) then \n'%execLine);
    f.write('\t touch %s.done\n'%os.path.abspath(f.name))
    f.write('else\n')
    f.write('\t touch %s.fail\n'%os.path.abspath(f.name))
    f.write('fi\n')
    f.write('rm -f %s.run\n'%os.path.abspath(f.name))
    print "[SUBMITTING] ",execLine
    f.close()
    os.system('rm -f %s.done'%os.path.abspath(f.name))
    os.system('rm -f %s.fail'%os.path.abspath(f.name))
    os.system('rm -f %s.log'%os.path.abspath(f.name))
    os.system('rm -f %s.err'%os.path.abspath(f.name))
    if (options.batch=="IC"):
      os.system('qsub -q %s -o %s.log %s'%("hep.q",os.path.abspath(f.name),os.path.abspath(f.name)))
    else:
      os.system('bsub -q %s -o %s.log %s'%("1nh",os.path.abspath(f.name),os.path.abspath(f.name)))
  continueLoop=1;
  while( continueLoop):
    if (options.batch=="IC"): qstat="qstat"
    else: qstat="bjobs"
    os.system('sleep 10') 
    os.system('%s'%qstat) 
    os.system('%s >out.txt'%qstat) 
    if( os.stat('out.txt').st_size==0) :continueLoop=0;
  
  print "All done, now just do :"
  print ('cat jobs/%s* >> %s'%(options.outfilename,options.outfilename)) 
  # os.system("cat jobs/%s* >> %s"%(options.outfilename,options.outfilename)) 
  #print ('mv %s.tmp %s'%(options.outfilename,options.outfilename)) 
  #os.system('mv %s.tmp %s'%(options.outfilename,options.outfilename)) 
###############################################################################
#import time
#if options.submitSelf:
#   
#  BJOBS= len([name for name in os.listdir('.') if (os.path.isfile(name)] and (not ".run" in name) and ))
#  RUN= len([name for name in os.listdir('.') if (os.path.isfile(name)] and ".run" in name))
#  while RUN :
#  
#  RUN= len([name for name in os.listdir('.') if (os.path.isfile(name)] and ".run" in name))
#  DONE= len([name for name in os.listdir('.') if (os.path.isfile(name)] and ".done" in name))
#  FAIL= len([name for name in os.listdir('.') if (os.path.isfile(name)] and ".fail" in name))
#  time.sleep(10s)

