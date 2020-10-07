print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG SIGNAL FITTER ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
import ROOT
import pandas as pd
import pickle
import math
import os, sys
import json
from optparse import OptionParser
import glob
import re
from collections import OrderedDict as od

from commonTools import *
from commonStrings import *
from replacementMap import globalReplacementMap
from XSBRMap import globalXSBRMap
from simultaneousFit import *

# Constant
MHLow, MHHigh = '115', '135'
MHNominal = '125'

def leave():
  print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG SIGNAL FITTER (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
  sys.exit(1)

def get_options():
  parser = OptionParser()
  parser.add_option("--inputWSDir", dest='inputWSDir', default='', help="Input flashgg WS directory")
  parser.add_option("--ext", dest='ext', default='', help="Extension")
  parser.add_option("--proc", dest='proc', default='', help="Signal process")
  parser.add_option("--cat", dest='cat', default='', help="RECO category")
  parser.add_option("--analysis", dest='analysis', default='STXS', help="Analysis handle: used to specify replacement map and XS*BR normalisations")
  parser.add_option('--massPoints', dest='massPoints', default='120,125,130', help="Mass points to fit")
  parser.add_option('--doEffAccFromJson', dest='doEffAccFromJson', default=False, action="store_true", help="Extract eff x acc from json (produced by getEffAcc). Else, extract from nominal weights in flashgg workspaces")
  parser.add_option('--doBeamspotReweigh', dest='doBeamspotReweigh', default=False, action="store_true", help="Do beamspot reweigh to match beamspot distribution in data")
  parser.add_option('--doPlots', dest='doPlots', default=False, action="store_true", help="Produce Signal Fitting plots")
  parser.add_option("--useDCB", dest='useDCB', default=False, action="store_true", help="Use DCB in signal fitting")
  parser.add_option("--useDiagonalShape", dest='useDiagonalShape', default=False, action="store_true", help="Use shape of diagonal process, keeping normalisation (requires diagonal mapping produced by getDiagonalProc script)")
  parser.add_option('--skipSystematics', dest='skipSystematics', default=False, action="store_true", help="Skip shape systematics in signal model")
  parser.add_option('--skipVertexScenarioSplit', dest='skipVertexScenarioSplit', default=False, action="store_true", help="Skip vertex scenario split")
  # Parameter values
  parser.add_option('--replacementThreshold', dest='replacementThreshold', default=200, type='int', help="Nevent threshold to trigger replacement dataset")
  parser.add_option('--beamspotWidthData', dest='beamspotWidthData', default=3.4, type='float', help="Width of beamspot in data [cm]")
  parser.add_option('--beamspotWidthMC', dest='beamspotWidthMC', default=5.14, type='float', help="Width of beamspot in MC [cm]")
  parser.add_option('--MHPolyOrder', dest='MHPolyOrder', default=1, type='int', help="Order of polynomial for MH dependence")
  parser.add_option('--nBins', dest='nBins', default=80, type='int', help="Number of bins for fit")
  # Minimizer options
  parser.add_option('--minimizerMethod', dest='minimizerMethod', default='L-BFGS-B', help="(Scipy) Minimizer method")
  parser.add_option('--minimizerTolerance', dest='minimizerTolerance', default=1e-6, type='float', help="(Scipy) Minimizer toleranve")
  return parser.parse_args()
(opt,args) = get_options()

ROOT.gStyle.SetOptStat(0)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Functions for signal fitting
def reduceDataset(_d,_argset): return _d.reduce(_argset)

def splitRVWV(_d,_argset,mode="RV"):
  # Split into RV/WV senario at dZ = 1cm
  if mode == "RV": return _d.reduce(_argset,"abs(dZ)<=1.")
  elif mode == "WV": return _d.reduce(_argset,"abs(dZ)>1.")
  else:
    print " --> [ERROR] unrecognised mode (%s) in splitRVWV function"%mode
    return 0

def beamspotReweigh(d,widthData,widthMC,_xvar,_dZ):
  drw = d.emptyClone()
  rw = ROOT.RooRealVar("weight","weight",-100000,1000000)
  for i in range(0,d.numEntries()):
    x, dz = d.get(i).getRealValue("CMS_hgg_mass"), d.get(i).getRealValue("dZ")
    f = 1.
    if abs(dz) < 0.1: f = 1.
    else:
      mcBeamspot = ROOT.TMath.Gaus(dz,0,math.sqrt(2)*widthMC,True)
      dataBeamspot = ROOT.TMath.Gaus(dz,0,math.sqrt(2)*widthData,True)
      f = dataBeamspot/mcBeamspot
    # Set weights and vars
    rw.setVal(f*d.weight())
    _xvar.setVal(x)
    _dZ.setVal(dz)
    # Add point to dataset
    drw.add( ROOT.RooArgSet(_xvar,_dZ), rw.getVal() )
  # Return reweighted dataset
  return drw
    
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SETUP: signal fit
print " --> Running fit for (proc,cat) = (%s,%s)"%(opt.proc,opt.cat)
#if( len(opt.massPoints.split(",")) == 1 )&( opt.MHPolyOrder > 0 ):
#  print " --> [WARNING] Attempting to fit polynomials of O(MH^%g) for single mass point. Setting order to 0"%opt.MHPolyOrder
#  opt.MHPolyOrder=0

# Add stopwatch function

# Load replacement map
if opt.analysis not in globalReplacementMap:
  print " --> [ERROR] replacement map does not exist for analysis (%s). Please add to tools/replacementMap.py"%opt.analysis
  leave()
else: rMap = globalReplacementMap[opt.analysis]

# Load XSBR map
if opt.analysis not in globalXSBRMap:
  print " --> [ERROR] XS * BR map does not exist for analysis (%s). Please add to tools/XSBRMap.py"%opt.analysis
  leave()
else: xsbrMap = globalXSBRMap[opt.analysis]

# Load RooRealVars
nominalWSFileName = glob.glob("%s/output*M%s*%s*"%(opt.inputWSDir,MHNominal,opt.proc))[0]
f0 = ROOT.TFile(nominalWSFileName,"read")
inputWS0 = f0.Get(inputWSName__)
xvar = inputWS0.var("CMS_hgg_mass")
dZ = inputWS0.var("dZ")
aset = ROOT.RooArgSet(xvar,dZ)
f0.Close()

# Create MH var
MH = ROOT.RooRealVar("MH","m_{H}", int(MHLow), int(MHHigh))
MH.setUnit("GeV")
MH.setConstant(True)

# Define proc x cat with which to extract shape: if skipVertexScenarioSplit label all events as "RV"
procRVFit, catRVFit = opt.proc, opt.cat
if opt.skipVertexScenarioSplit: 
  print " --> Skipping vertex scenario split"
else:
  procWVFit, catWVFit = opt.proc, opt.cat

# FIXME: if opt.useDiagonalShape then change to diagonal proc for given cat (lookup json)

# Define process with which to extract normalisation: nominal
procNorm, catNorm = opt.proc, opt.cat

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXTRACT DATASETS TO FIT (for each mass point)
# For RV (or if skipping vertex scenario split)
datasetRVForFit = od()
for mp in opt.massPoints.split(","):
  WSFileName = glob.glob("%s/output*M%s*%s*"%(opt.inputWSDir,mp,procRVFit))[0]
  f = ROOT.TFile(WSFileName,"read")
  inputWS = f.Get(inputWSName__)
  d = reduceDataset(inputWS.data("%s_%s_%s_%s"%(procToData(procRVFit.split("_")[0]),mp,sqrts__,catRVFit)),aset)
  if opt.skipVertexScenarioSplit: datasetRVForFit[mp] = d
  else: datasetRVForFit[mp] = splitRVWV(d,aset,mode="RV")
  inputWS.Delete()
  f.Close()

# Check if nominal yield > threshold (or if +ve sum of weights). If not then use replacement proc x cat
if( datasetRVForFit[MHNominal].numEntries() < opt.replacementThreshold  )|( datasetRVForFit[MHNominal].sumEntries() < 0. ):
  nominal_numEntries = datasetRVForFit[MHNominal].numEntries()
  procReplacementFit, catReplacementFit = rMap['procRVMap'][opt.cat], rMap['catRVMap'][opt.cat]
  for mp in opt.massPoints.split(","):
    WSFileName = glob.glob("%s/output*M%s*%s*"%(opt.inputWSDir,mp,procReplacementFit))[0]
    f = ROOT.TFile(WSFileName,"read")
    inputWS = f.Get(inputWSName__)
    d = reduceDataset(inputWS.data("%s_%s_%s_%s"%(procToData(procReplacementFit.split("_")[0]),mp,sqrts__,catReplacementFit)),aset)
    if opt.skipVertexScenarioSplit: datasetRVForFit[mp] = d
    else: datasetRVForFit[mp] = splitRVWV(d,aset,mode="RV")
    inputWS.Delete()
    f.Close() 

  # Check if replacement dataset has too few entries: if so throw error
  if( datasetRVForFit[MHNominal].numEntries() < opt.replacementThreshold )|( datasetRVForFit[MHNominal].sumEntries() < 0. ):
    print " --> [ERROR] replacement dataset (%s,%s) has too few entries (%g < %g)"%(procReplacementFit,catReplacementFit,datasetRVForFit[MHNominal].numEntries(),opt.replacementThreshold)
    sys.exit(1)

  else:
    procRVFit, catRVFit = procReplacementFit, catReplacementFit
    if opt.skipVertexScenarioSplit: 
      print " --> Too few entries in nominal dataset (%g < %g). Using replacement (proc,cat) = (%s,%s) for extracting shape"%(nominal_numEntries,opt.replacementThreshold,procRVFit,catRVFit)
      print "     * MH = %s: numEntries = %g, sumEntries = %.6f"%(MHNominal,datasetRVForFit[MHNominal].numEntries(),datasetRVForFit[MHNominal].sumEntries())
    else: 
      print " --> RV: Too few entries in nominal dataset (%g < %g). Using replacement (proc,cat) = (%s,%s) for extracting shape"%(nominal_numEntries,opt.replacementThreshold,procRVFit,catRVFit)
      print "     * MH = %s: numEntries = %g, sumEntries = %.6f"%(MHNominal,datasetRVForFit[MHNominal].numEntries(),datasetRVForFit[MHNominal].sumEntries())

else:
  if opt.skipVertexScenarioSplit: 
    print " --> Using (proc,cat) = (%s,%s) for extracting shape"%(procRVFit,catRVFit)
    print "     * MH = %s: numEntries = %g, sumEntries = %.6f"%(MHNominal,datasetRVForFit[MHNominal].numEntries(),datasetRVForFit[MHNominal].sumEntries())
  else: 
    print " --> RV: Using (proc,cat) = (%s,%s) for extracting shape"%(procRVFit,catRVFit)
    print "     * MH = %s: numEntries = %g, sumEntries = %.6f"%(MHNominal,datasetRVForFit[MHNominal].numEntries(),datasetRVForFit[MHNominal].sumEntries())

# Repeat for WV scenario
if not opt.skipVertexScenarioSplit:
  datasetWVForFit = od()
  for mp in opt.massPoints.split(","):
    WSFileName = glob.glob("%s/output*M%s*%s*"%(opt.inputWSDir,mp,procWVFit))[0]
    f = ROOT.TFile(WSFileName,"read")
    inputWS = f.Get(inputWSName__)
    d = reduceDataset(inputWS.data("%s_%s_%s_%s"%(procToData(procWVFit.split("_")[0]),mp,sqrts__,catWVFit)),aset)
    datasetWVForFit[mp] = splitRVWV(d,aset,mode="WV")
    inputWS.Delete()
    f.Close()

  # Check nominal mass dataset
  if( datasetWVForFit[MHNominal].numEntries() < opt.replacementThreshold  )|( datasetWVForFit[MHNominal].sumEntries() < 0. ):
    nominal_numEntries = datasetWVForFit[MHNominal].numEntries()
    procReplacementFit, catReplacementFit = rMap['procWV'], rMap['catWV']
    for mp in opt.massPoints.split(","):
      WSFileName = glob.glob("%s/output*M%s*%s*"%(opt.inputWSDir,mp,procReplacementFit))[0]
      f = ROOT.TFile(WSFileName,"read")
      inputWS = f.Get(inputWSName__)
      d = reduceDataset(inputWS.data("%s_%s_%s_%s"%(procToData(procReplacementFit.split("_")[0]),mp,sqrts__,catReplacementFit)),aset)
      datasetWVForFit[mp] = splitRVWV(d,aset,mode="WV")
      inputWS.Delete()
      f.Close()
    # Check if replacement dataset has too few entries: if so throw error
    if( datasetWVForFit[MHNominal].numEntries() < opt.replacementThreshold )|( datasetWVForFit[MHNominal].sumEntries() < 0. ):
      print " --> [ERROR] replacement dataset (%s,%s) has too few entries (%g < %g)"%(procReplacementFit,catReplacementFit,datasetWVForFit[MHNominal].numEntries,opt.replacementThreshold)
      sys.exit(1)
    else:
      procWVFit, catWVFit = procReplacementFit, catReplacementFit
      print " --> WV: Too few entries in nominal dataset (%g < %g). Using replacement (proc,cat) = (%s,%s) for extracting shape"%(nominal_numEntries,opt.replacementThreshold,procWVFit,catWVFit)
      print "     * MH = %s: numEntries = %g, sumEntries = %.6f"%(MHNominal,datasetWVForFit[MHNominal].numEntries(),datasetWVForFit[MHNominal].sumEntries())
  else:
    print " --> WV: Using (proc,cat) = (%s,%s) for extracting shape"%(procWVFit,catRVFit)
    print "     * MH = %s: numEntries = %g, sumEntries = %.6f"%(MHNominal,datasetWVForFit[MHNominal].numEntries(),datasetWVForFit[MHNominal].sumEntries())

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# BEAMSPOT REWEIGH
# FIXME: normalisation should come first?
if opt.doBeamspotReweigh:
  for mp,d in datasetRVForFit.iteritems(): 
    drw = beamspotReweigh(datasetRVForFit[mp],opt.beamspotWidthData,opt.beamspotWidthMC,xvar,dZ)
    datasetRVForFit[mp] = drw
  if not opt.skipVertexScenarioSplit:
    for mp,d in datasetWVForFit.iteritems(): 
      drw = beamspotReweigh(datasetWVForFit[mp],opt.beamspotWidthData,opt.beamspotWidthMC,xvar,dZ)
      datasetWVForFit[mp] = drw
    print " --> Beamspot reweigh: RV(sumEntries) = %.6f, WV(sumEntries) = %.6f"%(datasetRVForFit[mp].sumEntries(),datasetWVForFit[mp].sumEntries())
  else:
    print " --> Beamspot reweigh: sumEntries = %.6f"%datasetRVForFit[mp].sumEntries()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# If using nGaussian fit then extract nGaussians from fTest json file
if not opt.useDCB:
  with open("%s/outdir_%s/fTest/json/nGauss_%s.json"%(cwd__,opt.ext,opt.ext)) as jf: ngauss = json.load(jf)
  nRV = ngauss["%s__%s"%(procRVFit,catRVFit)]['nRV']
  nWV = ngauss["%s__%s"%(procWVFit,catWVFit)]['nWV']
  if opt.skipVertexScenarioSplit: print " --> Fitting function: convolution of nGaussians (%g)"%nRV
  else: print " --> Fitting function: convolution of nGaussians (RV=%g,WV=%g)"%(nRV,nWV)
else:
  print " --> Fitting function: DCB + 1 Gaussian"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# NORMALISATION


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# FIT: simultaneous signal fit (ssf)
nRV = 4
ssfRV = SimultaneousFit(opt.proc,opt.cat,datasetRVForFit,xvar,MH,MHLow,MHHigh,opt.massPoints,opt.nBins,opt.MHPolyOrder,opt.minimizerMethod,opt.minimizerTolerance,"%s/outdir_%s/signalFit/Plots/rv",_doPlots=opt.doPlots)
if opt.useDCB: ssfRV.buildDCBplusGaussian()
else: ssfRV.buildNGaussians(nRV)
#print " --> Building chi2 function and running fit"
ssfRV.runFit()
