import ROOT
import os
import sys
import json
import re
import numpy as np
import pandas
import pickle
from collections import OrderedDict as od
from commonObjects import *
from commonTools import *
from signalTools import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   
# Function to load XS/BR from Combine
from HiggsAnalysis.CombinedLimit.DatacardParser import *
from HiggsAnalysis.CombinedLimit.ModelTools import *
from HiggsAnalysis.CombinedLimit.PhysicsModel import *
from HiggsAnalysis.CombinedLimit.SMHiggsBuilder import *
import HiggsAnalysis.CombinedLimit.PhysicsModel as models
class dummy_options:
  def __init__(self):
    self.physModel = "HiggsAnalysis.CombinedLimit.PhysicsModel:floatingHiggsMass"
    self.physOpt = ["higgsMassRange=90,250"]
    self.bin = True
    self.fileName = "dummy.root"
    self.cexpr = False
    self.out = "wsdefault"
    self.verbose = 0
    self.mass = 125
    self.funcXSext = "dummy"

# Functions to get XS/BR
def getXS(_SM,_MHVar,_mh,_pm):
  _MHVar.setVal(_mh)
  return _SM.modelBuilder.out.function("SM_XS_%s_%s"%(_pm,sqrts__)).getVal()
def getBR(_SM,_MHVar,_mh,_dm):
  _MHVar.setVal(_mh)
  return _SM.modelBuilder.out.function("SM_BR_%s"%_dm).getVal()

# Function to initialise XS values from combine
def initialiseXSBR():
  options=dummy_options()
  DC = Datacard()
  MB = ModelBuilder(DC, options)
  physics = models.floatingHiggsMass
  physics.setPhysicsOptions(options.physOpt)
  MB.setPhysics(physics)
  MB.physics.doParametersOfInterest()
  SM = SMHiggsBuilder(MB)
  MHVar = SM.modelBuilder.out.var("MH")

  # Make XS and BR
  SM.makeBR(decayMode)
  for pm in productionModes: SM.makeXS(pm,sqrts__)

  # Store numpy arrays for each production mode in ordered dict
  xsbr = od()
  for pm in productionModes: xsbr[pm] = []
  xsbr[decayMode] = []
  xsbr['constant'] = []
  mh = 120.
  while( mh < 130.05 ):
    for pm in productionModes: xsbr[pm].append(getXS(SM,MHVar,mh,pm))
    xsbr[decayMode].append(getBR(SM,MHVar,mh,decayMode))
    xsbr['constant'].append(1.)
    mh += 0.1
  for pm in productionModes: xsbr[pm] = np.asarray(xsbr[pm])
  xsbr[decayMode] = np.asarray(xsbr[decayMode])
  xsbr['constant'] = np.asarray(xsbr['constant'])
  # If ggZH and ZH in production modes then make qqZH numpy array
  if('ggZH' in productionModes)&('ZH' in productionModes): xsbr['qqZH'] = xsbr['ZH']-xsbr['ggZH']
  return xsbr

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   
class FinalModel:
  # Constructor
  def __init__(self,_ssfMap,_proc,_cat,_ext,_year,_sqrts,_datasets,_xvar,_MH,_MHLow,_MHHigh,_massPoints,_xsbrMap,_procSyst,_scales,_scalesCorr,_scalesGlobal,_smears,_doVoigtian,_useDCB,_skipVertexScenarioSplit,_skipSystematics,_doEffAccFromJson):
    self.ssfMap = _ssfMap
    self.proc = _proc
    self.procSyst = _procSyst # Signal process used for systematics (useful for low stat cases)
    self.cat = _cat
    self.ext = _ext
    self.year = _year
    self.sqrts = _sqrts
    self.name = "%s_%s_%s_%s"%(self.proc,self.year,self.cat,self.sqrts)
    self.datasets = _datasets
    self.xvar = _xvar
    self.aset = ROOT.RooArgSet(self.xvar)
    self.MH = _MH
    self.MHLow = _MHLow
    self.MHHigh = _MHHigh
    self.massPoints = _massPoints
    self.intLumi = ROOT.RooRealVar("IntLumi","IntLumi",1.,0.,999999999.) # in pb^-1
    self.xsbrMap = _xsbrMap
    # Systematics
    self.skipSystematics = _skipSystematics
    self.scales = _scales
    self.scalesCorr = _scalesCorr
    self.scalesGlobal = _scalesGlobal
    self.smears = _smears
    # Options:
    self.useDCB = _useDCB
    self.doVoigtian = _doVoigtian
    if self.doVoigtian: self.GammaH = ROOT.RooRealVar("GammaH","GammaH",0.004,0.,5.)
    self.skipVertexScenarioSplit = _skipVertexScenarioSplit
    self.doEffAccFromJson = _doEffAccFromJson
    self.verbose = True
    # Dict to store objects
    self.Splines = od()
    self.Functions = od()
    self.NuisanceMap = od()
    self.Pdfs = od()
    self.Datasets = od()
    # Build XS/BR/EA splines
    self.XSBR = initialiseXSBR() 
    self.buildXSBRSplines()
    self.buildEffAccSpline()
    # If not skip systematics: add nuisance params to dict
    if not self.skipSystematics: self.buildNuisanceMap()
    # Build final pdfs
    if not self.skipVertexScenarioSplit: 
      self.buildRVFracFunction()
      self.buildPdf(self.ssfMap['RV'],ext="rv",useDCB=self.useDCB)
      self.buildPdf(self.ssfMap['WV'],ext="wv",useDCB=self.useDCB)
      self.Pdfs['final'] = ROOT.RooAddPdf("%s_%s"%(outputWSObjectTitle__,self.name),"%s_%s"%(outputWSObjectTitle__,self.name),ROOT.RooArgList(self.Pdfs['rv'],self.Pdfs['wv']),ROOT.RooArgList(self.Functions['fracRV']))
    else:
      self.buildPdf(self.ssfMap['Total'],ext='total',useDCB=self.useDCB)
      self.Pdfs['final'] = self.Pdfs['total']
    # Build final normalisation, datasets and extended Pdfs
    self.buildNorm()
    self.buildDatasets()
    self.buildExtended() 

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # Functions to get XS, BR and EA splines for given proc/decay from map
  def buildXSBRSplines(self):
    mh = np.linspace(120.,130.,101)
    # XS
    fp = self.xsbrMap[self.proc]['factor'] if 'factor' in self.xsbrMap[self.proc] else 1.
    mp = self.xsbrMap[self.proc]['mode']
    xs = fp*self.XSBR[mp]
    self.Splines['xs'] = ROOT.RooSpline1D("fxs_%s_%s"%(self.proc,self.sqrts),"fxs_%s_%s"%(self.proc,self.sqrts),self.MH,len(mh),mh,xs)
    # BR
    fd = self.xsbrMap['decay']['factor'] if 'factor' in self.xsbrMap['decay'] else 1.
    md = self.xsbrMap['decay']['mode']
    br = fd*self.XSBR[md]
    self.Splines['br'] = ROOT.RooSpline1D("fbr_%s"%self.sqrts,"fbr_%s"%self.sqrts,self.MH,len(mh),mh,br)

  def buildEffAccSpline(self):
    # Two treatments: load from json created with getEffAcc.py script or calc from sum of weights
    # Loop over mass points  
    ea, mh = [], []
    for mp in self.massPoints.split(","):
      mh.append(float(mp))
      if self.doEffAccFromJson:
        jfname = "%s/outdir_%s/getEffAcc/json/effAcc_M%s_%s.json"%(swd__,self.ext,mp,self.ext)
        if not os.path.exists(jfname):
          print " --> [ERROR] effAcc json file (%s) does not exist for mass point = %s. Run getEffAcc first."%(jfname,mp)
          sys.exit(1)
        with open(jfname,'r') as jf: ea_data = json.load(jf)
        ea.append(float(ea_data['%s__%s'%(self.proc,self.cat)]))
      else:
        sumw = self.datasets[mp].sumEntries()
        ea.append(sumw) 
    # If single mass point then add MHLow and MHHigh dummy points for constant ea
    if len(ea) == 1: ea, mh = [ea[0],ea[0],ea[0]], [float(self.MHLow),mh[0],float(self.MHHigh)]
    # Convert to numpy arrays and make spline
    ea, mh = np.asarray(ea), np.asarray(mh)
    self.Splines['ea'] = ROOT.RooSpline1D("fea_%s"%(self.name),"fea_%s"%(self.name),self.MH,len(mh),mh,ea)

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # Function to build final normalisation: XS * BR * eff * acc * rate
  def buildNorm(self):
    # Build rate function: encode affect of nuisances on signal rate
    self.buildRate("rate_%s"%self.name,skipSystematics=self.skipSystematics)
    finalPdfName = self.Pdfs['final'].GetName()
    self.Functions['final_norm'] = ROOT.RooFormulaVar("%s_norm"%finalPdfName,"%s_norm"%finalPdfName,"@0*@1*@2*@3",ROOT.RooArgList(self.Splines['xs'],self.Splines['br'],self.Splines['ea'],self.Functions['rate_%s'%self.name]))

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # Function for making nuisance param w/ info to add to Nuisance dict
  def makeNuisance(self,nuisanceName,nuisanceMeanConst,nuisanceSigmaConst,nuisanceRateConst,nuisanceType,nuisanceOpts=[]):
    self.NuisanceMap[nuisanceType][nuisanceName] = {
      'name':nuisanceName,
      'param':ROOT.RooRealVar("%s_%s"%(outputWSNuisanceTitle__,nuisanceName),"%s_%s"%(outputWSNuisanceTitle__,nuisanceName),0.,-5.,5.),
      'meanConst':ROOT.RooConstVar("const_%s_mean_%s"%(self.name,nuisanceName),"const_%s_mean_%s"%(self.name,nuisanceName),nuisanceMeanConst),
      'sigmaConst':ROOT.RooConstVar("const_%s_sigma_%s"%(self.name,nuisanceName),"const_%s_sigma_%s"%(self.name,nuisanceName),nuisanceSigmaConst),
      'rateConst':ROOT.RooConstVar("const_%s_rate_%s"%(self.name,nuisanceName),"const_%s_rate_%s"%(self.name,nuisanceName),nuisanceRateConst),
      'opts':nuisanceOpts}
    self.NuisanceMap[nuisanceType][nuisanceName]['param'].setConstant(True)
  
  # Function for building Nuisance param map:
  def buildNuisanceMap(self):
    # Dict to store nuisances of different type in map
    for sType in ['scales','scalesCorr','scalesGlobal','smears']:
      if getattr(self,sType) != '': self.NuisanceMap[sType] = od()

    # Extract calcPhotonSyst output
    psname = "%s/outdir_%s/calcPhotonSyst/pkl/%s.pkl"%(swd__,self.ext,self.cat)
    if not os.path.exists(psname):
      print " --> [ERROR] Photon systematics do not exist (%s). Please run calcPhotonSyst mode first or skip systematics (--skipSystematics)"%psname
      sys.exit(1)
    with open(psname,"r") as fpkl: psdata = pickle.load(fpkl)
    
    # Get row for proc: option to use diagonal process
    r = psdata[psdata['proc']==self.procSyst]
    if len(r) == 0:
      print " --> [WARNING] Process %s is not in systematics pkl (%s). Skipping systematics."%(self.proc,psname)
      self.skipSystematics = True

    else:
      # Add scales, scalesCorr, scalesGlobal, smears
      for sType in ['scales','scalesCorr','scalesGlobal','smears']:
	for syst in getattr(self,sType).split(","):
          if syst == '': continue

          # If corr/global nor in sType then build separate nuisance per year i.e. de-correlate
          if('Corr' in sType)|('Global' in sType): sExt = ""
          else: sExt = "_%s"%self.year

          # Extract info
	  systOpts = syst.split(":")
	  sName = "%s_%s"%(systOpts[0],outputNuisanceExtMap[sType])

          # Extract constant values and make nuisance
          if sType == 'scalesGlobal': cMean, cSigma, cRate = 0.,0.,0.
	  else: cMean, cSigma, cRate = r["%s_mean"%sName].values[0], r["%s_sigma"%sName].values[0], r["%s_rate"%sName].values[0]
	  sOpts = systOpts[1:] if len(systOpts) > 1 else []
	  self.makeNuisance("%s%s"%(sName,sExt),cMean,cSigma,cRate,sType,sOpts)

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # Function to get RV fraction func
  def buildRVFracFunction(self):
    # Loop over mass points
    frv, mh = [], []
    for mp in self.massPoints.split(","):
      mh.append(float(mp))
      dRV = splitRVWV(self.datasets[mp],self.aset,mode="RV")
      dWV = splitRVWV(self.datasets[mp],self.aset,mode="WV")
      # Do not allow negative values (caused by negative weights)
      nRV, nWV = max(0.,dRV.sumEntries()), max(0.,dWV.sumEntries())
      # If sum = 0, then set frv = 1.
      if nRV+nWV == 0.: fRV = 1.
      else: fRV = nRV/(nRV+nWV)
      # If nan then set to 1.
      if fRV != fRV: fRV = 1.
      frv.append(fRV)
    # If single mass point then add MHLow and MHHigh dummy points for constant rv frac
    if len(frv) == 1: frv, mh = [frv[0],frv[0],frv[0]], [float(self.MHLow),mh[0],float(self.MHHigh)]
    # Convert to numpy arrays and make spline
    frv, mh = np.asarray(frv), np.asarray(mh)
    self.Splines['fracRV'] = ROOT.RooSpline1D("%s_%s_rvFracSpline"%(outputWSObjectTitle__,self.name),"%s_%s_rvFracSpline"%(outputWSObjectTitle__,self.name),self.MH,len(mh),mh,frv)
    # Create function: if not skip systematics then add nuisance for RV fraction
    if self.skipSystematics:
      self.Functions['fracRV'] = ROOT.RooFormulaVar("%s_%s_rvFrac"%(outputWSObjectTitle__,self.name),"%s_%s_rvFrac"%(outputWSObjectTitle__,self.name),"TMath::Min(@0,1.0)",ROOT.RooArgList(self.Splines['fracRV']))
    else:
      self.NuisanceMap['other'] = od()
      self.makeNuisance('deltafracright',1.,1.,1.,'other')
      self.Functions['fracRV'] = ROOT.RooFormulaVar("%s_%s_rvFrac"%(outputWSObjectTitle__,self.name),"%s_%s_rvFrac"%(outputWSObjectTitle__,self.name),"TMath::Min(@0+@1,1.0)",ROOT.RooArgList(self.Splines['fracRV'],self.NuisanceMap['other']['deltafracright']['param']))

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # Function to build final PDFs from input SimultaneousFit object splines
  def buildPdf(self,ssf,ext='',useDCB=False,_recursive=True):
    extStr = "%s_%s"%(self.name,ext) if ext!='total' else '%s'%self.name
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # For double CB + Gaussian
    if useDCB:
      # Extract splines
      for f in ['dm','sigma','n1','n2','a1','a2']:
        k = "%s_dcb"%f
        self.Splines["%s_%s"%(k,extStr)] = ssf.Splines[k].Clone()
        self.Splines["%s_%s"%(k,extStr)].SetName("%s_%s"%(re.sub("sigma","sigma_fit",k),extStr))
      # Build mean and sigma functions: including systematics
      self.buildMean('dm_dcb_%s'%extStr,skipSystematics=self.skipSystematics)
      self.buildSigma('sigma_dcb_%s'%extStr,skipSystematics=self.skipSystematics)
      # Build DCB pdf
      self.Pdfs['dcb_%s'%extStr] = ROOT.RooDoubleCBFast("dcb_%s"%extStr,"dcb_%s"%extStr,self.xvar,self.Functions["mean_dcb_%s"%extStr],self.Functions["sigma_dcb_%s"%extStr],self.Splines['a1_dcb_%s'%extStr],self.Splines['n1_dcb_%s'%extStr],self.Splines['a2_dcb_%s'%extStr],self.Splines['n2_dcb_%s'%extStr])
      
      # + Gaussian: shares mean with DCB
      self.Splines['sigma_gaus_%s'%extStr] = ssf.Splines['sigma_gaus'].Clone()
      self.Splines['sigma_gaus_%s'%extStr].SetName("sigma_fit_gaus_%s"%extStr)
      self.buildSigma('sigma_gaus_%s'%extStr,skipSystematics=self.skipSystematics)
      if self.doVoigtian:
        self.Pdfs['gaus_%s'%extStr] = ROOT.RooVoigtian("gaus_%s"%extStr,"gaus_%s"%extStr,self.xvar,self.Functions["mean_dcb_%s"%extStr],self.GammaH,self.Functions["sigma_gaus_%s"%extStr])
      else:
        self.Pdfs['gaus_%s'%extStr] = ROOT.RooGaussian("gaus_%s"%extStr,"gaus_%s"%extStr,self.xvar,self.Functions["mean_dcb_%s"%extStr],self.Functions["sigma_gaus_%s"%extStr])

      # Fraction
      self.Splines['frac_%s'%extStr] = ssf.Splines['frac_constrained'].Clone()
      self.Splines['frac_%s'%extStr].SetName("frac_%s"%extStr)

      # Define total pdf
      _pdfs, _coeffs = ROOT.RooArgList(), ROOT.RooArgList()
      for pdf in ['dcb','gaus']: _pdfs.add(self.Pdfs['%s_%s'%(pdf,extStr)])
      _coeffs.add(self.Splines['frac_%s'%extStr])
      self.Pdfs[ext] = ROOT.RooAddPdf("%s_%s"%(outputWSObjectTitle__,extStr),"%s_%s"%(outputWSObjectTitle__,extStr),_pdfs,_coeffs,_recursive)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # For nGaussians:
    else:
      # For total pdf
      _pdfs, _coeffs = ROOT.RooArgList(), ROOT.RooArgList()

      for g in range(0,ssf.nGaussians):
        # Extract splines
        for f in ['dm','sigma']:
          k = "%s_g%g"%(f,g)
          self.Splines["%s_%s"%(k,extStr)] = ssf.Splines[k].Clone()
          self.Splines["%s_%s"%(k,extStr)].SetName("%s_%s"%(re.sub("sigma","sigma_fit",k),extStr))
        # Build mean and sigma functions for gaussian, g: including systematics
        self.buildMean('dm_g%g_%s'%(g,extStr),skipSystematics=self.skipSystematics)
        self.buildSigma('sigma_g%g_%s'%(g,extStr),skipSystematics=self.skipSystematics)
        # Build Gaussian
        if self.doVoigtian: 
          self.Pdfs['gaus_g%g_%s'%(g,extStr)] = ROOT.RooVoigtian("gaus_g%g_%s"%(g,extStr),"gaus_g%g_%s"%(g,extStr),self.xvar,self.Functions["mean_g%g_%s"%(g,extStr)],self.GammaH,self.Functions["sigma_g%g_%s"%(g,extStr)])
        else: 
          self.Pdfs['gaus_g%g_%s'%(g,extStr)] = ROOT.RooGaussian("gaus_g%g_%s"%(g,extStr),"gaus_g%g_%s"%(g,extStr),self.xvar,self.Functions["mean_g%g_%s"%(g,extStr)],self.Functions["sigma_g%g_%s"%(g,extStr)])
        _pdfs.add(self.Pdfs['gaus_g%g_%s'%(g,extStr)])
        
        # Fractions
        if g < ssf.nGaussians-1:
          self.Splines['frac_g%g_%s'%(g,extStr)] = ssf.Splines['frac_g%g_constrained'%g]
          self.Splines['frac_g%g_%s'%(g,extStr)].SetName("frac_g%g_%s"%(g,extStr))
          _coeffs.add(self.Splines['frac_g%g_%s'%(g,extStr)])

        # Define total pdf
        self.Pdfs[ext] = ROOT.RooAddPdf("%s_%s"%(outputWSObjectTitle__,extStr),"%s_%s"%(outputWSObjectTitle__,extStr),_pdfs,_coeffs,_recursive)

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # Functions to build mean, sigma and rate functions with systematics
  def buildMean(self,dmSplineName="",skipSystematics=False):
    meanName = re.sub("dm","mean",dmSplineName) 
    # Build formula string and dependents list
    dependents = ROOT.RooArgList()
    formula = "(@0+@1)"
    dependents.add(self.MH)
    dependents.add(self.Splines[dmSplineName])
    if not skipSystematics:
      # Add systematics
      formula += "*(1."
      # Global
      if 'scalesGlobal' in self.NuisanceMap:
        for sName, sInfo in self.NuisanceMap['scalesGlobal'].iteritems():
          formula += "+@%g"%dependents.getSize()
          # For adding additional factor
          for so in sInfo['opts']: 
            if "factor_%s"%self.cat in so:
              additionalFactor = float(so.split("=")[-1])
              formula += "*%3.1f"%additionalFactor
          dependents.add(sInfo['param'])
      # Other systs: scales, scalesCorr, smears
      for sType in ['scales','scalesCorr','smears']:
        if sType in self.NuisanceMap:
          for sName, sInfo in self.NuisanceMap[sType].iteritems():
            c = sInfo['meanConst'].getVal()
            if abs(c)>=5.e-5:
              formula += "+@%g*@%g"%(dependents.getSize(),dependents.getSize()+1)
              dependents.add(sInfo['meanConst'])
              dependents.add(sInfo['param'])
      formula += ")"
    self.Functions[meanName] = ROOT.RooFormulaVar(meanName,meanName,formula,dependents)

  def buildSigma(self,sigmaSplineName="",skipSystematics=False):
    sigmaName = sigmaSplineName
    # Build formula string and dependents list
    dependents = ROOT.RooArgList()
    formula = "@0"
    dependents.add(self.Splines[sigmaSplineName])
    if not skipSystematics:
      # Add systematics
      formula += "*TMath::Max(1.e-2,(1."
      for sType in ['scales','scalesCorr','smears']:
        if sType in self.NuisanceMap:
          for sName, sInfo in self.NuisanceMap[sType].iteritems():
            c = sInfo['sigmaConst'].getVal()
            if c>=1e-4:
              formula += "+@%g*@%g"%(dependents.getSize(),dependents.getSize()+1)
              dependents.add(sInfo['sigmaConst'])
              dependents.add(sInfo['param'])
      formula += "))"
    self.Functions[sigmaName] = ROOT.RooFormulaVar(sigmaName,sigmaName,formula,dependents)

  def buildRate(self,rateName,skipSystematics=False):
    # Build formula string and dependents list
    dependents = ROOT.RooArgList()
    formula = "(1."
    if not skipSystematics:
      # Add systematics
      for sType in ['scales','scalesCorr','smears']:
        if sType in self.NuisanceMap:
          for sName, sInfo in self.NuisanceMap[sType].iteritems():
            c = sInfo['rateConst'].getVal()
            if c>=5.e-4:
              formula += "+@%g*@%g"%(dependents.getSize(),dependents.getSize()+1)
              dependents.add(sInfo['rateConst'])
              dependents.add(sInfo['param'])
    formula += ")"
    self.Functions[rateName] = ROOT.RooFormulaVar(rateName,rateName,formula,dependents)

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # Function to build datasets to add to workspace
  def buildDatasets(self):
    for mp, d in self.datasets.iteritems(): 
      self.Datasets[mp] = d.Clone("sig_mass_m%s_%s"%(mp,self.name))
      self.Datasets['%s_copy'%mp] = d.Clone("sig_mass_m%s_%s"%(mp,self.cat))

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # Function to build extended Pdfs and normalisation with luminosity
  def buildExtended(self):
    finalPdfName = self.Pdfs['final'].GetName()
    self.Functions['final_normThisLumi'] = ROOT.RooFormulaVar("%s_normThisLumi"%finalPdfName,"%s_normThisLumi"%finalPdfName,"@0*@1*@2*@3*@4",ROOT.RooArgList(self.Splines['xs'],self.Splines['br'],self.Splines['ea'],self.Functions['rate_%s'%self.name],self.intLumi))
    self.Pdfs['final_extend'] = ROOT.RooExtendPdf("extend%s"%finalPdfName,"extend%s"%finalPdfName,self.Pdfs['final'],self.Functions['final_norm'])
    self.Pdfs['final_extendThisLumi'] = ROOT.RooExtendPdf("extend%sThisLumi"%finalPdfName,"extend%sThisLumi"%finalPdfName,self.Pdfs['final'],self.Functions['final_normThisLumi'])
 
  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # Function for saving to output workspace
  def save(self,wsout):
    wsout.imp = getattr(wsout,"import")
    wsout.imp(self.Pdfs['final'],ROOT.RooFit.RecycleConflictNodes())
    wsout.imp(self.Functions['final_norm'],ROOT.RooFit.RecycleConflictNodes())
    wsout.imp(self.Functions['final_normThisLumi'],ROOT.RooFit.RecycleConflictNodes())
    wsout.imp(self.Pdfs['final_extend'],ROOT.RooFit.RecycleConflictNodes())
    wsout.imp(self.Pdfs['final_extendThisLumi'],ROOT.RooFit.RecycleConflictNodes())
    for d in self.Datasets.itervalues(): wsout.imp(d) 
