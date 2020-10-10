import ROOT
import os
import sys
import json
import numpy as np
from collections import OrderedDict as od
from commonObjects import *

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
  return xsbr


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   
class FinalModel:
  # Constructor
  def __init__(self,_ssfMap,_proc,_cat,_ext,_year,_sqrts,_datasets,_xvar,_MH,_MHLow,_MHHigh,_massPoints,_xsbrMap,_skipSystematics,_doEffAccFromJson):
    self.ssfMap = _ssfMap
    self.proc = _proc
    self.cat = _cat
    self.ext = _ext
    self.year = _year
    self.sqrts = _sqrts
    self.datasets = _datasets
    self.xvar = _xvar
    self.MH = _MH
    self.MHLow = _MHLow
    self.MHHigh = _MHHigh
    self.massPoints = _massPoints
    self.xsbrMap = _xsbrMap
    self.skipSystematics = _skipSystematics
    self.doEffAccFromJson = _doEffAccFromJson
    self.verbose = True
    # Dict to store objects
    self.Splines = od()
    self.Nuisances = od()
    # Build XS/BR/EA splines
    self.XSBR = initialiseXSBR() 
    self.buildXSBRSplines()
    self.buildEffAccSpline()

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
        jfname = "%s/outdir_%s/getEffAcc/json/effAcc_M%s_%s.json"%(cwd__,self.ext,mp,self.ext)
        if not os.path.exists(jfname):
          print " --> [ERROR] effAcc json file (%s) does not exist for mass point = %s. Run getEffAcc first."%(jfname,mp)
          sys.exit(1)
        with open(jfname,'r') as jf: ea_data = json.load(jf)
        ea.append(float(ea_data['%s__%s'%(self.proc,self.cat)]))
      else:
        sumw = self.datasets[mp].sumEntries()
        self.MH.setVal(float(mp))
        xs,br = self.Splines['xs'].getVal(), self.Splines['br'].getVal()
        ea.append(sumw/(lumiScaleFactor*xs*br)) 
    # If single mass point then add MHLow and MHHigh dummy points for constant ea
    if len(ea) == 1: ea, mh = [ea[0],ea[0],ea[0]], [float(self.MHLow),mh[0],float(self.MHHigh)]
    # Convert to numpy arrays and make spline
    ea, mh = np.asarray(ea), np.asarray(mh)
    self.Splines['ea'] = ROOT.RooSpline1D("fea_%s_%s_%s_%s"%(self.proc,self.year,self.cat,self.sqrts),"fea_%s_%s_%s_%s"%(self.proc,self.year,self.cat,self.sqrts),self.MH,len(mh),mh,ea)

  

