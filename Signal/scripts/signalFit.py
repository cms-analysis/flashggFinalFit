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
from commonObjects import *
from signalTools import *
from replacementMap import globalReplacementMap
from XSBRMap import *
from simultaneousFit import *
from finalModel import *
from plottingTools import *

# Constant
MHLow, MHHigh = '120', '130'
MHNominal = '125'

print(" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG SIGNAL FITTER ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ")
def leave():
  print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG SIGNAL FITTER (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ")
  exit()

def get_options():
  parser = OptionParser()
  parser.add_option("--xvar", dest='xvar', default='CMS_hgg_mass', help="Observable to fit")
  parser.add_option("--inputWSDir", dest='inputWSDir', default='', help="Input flashgg WS directory")
  parser.add_option("--ext", dest='ext', default='', help="Extension")
  parser.add_option("--proc", dest='proc', default='', help="Signal process")
  parser.add_option("--cat", dest='cat', default='', help="RECO category")
  parser.add_option("--year", dest='year', default='2016', help="Year")
  parser.add_option("--analysis", dest='analysis', default='STXS', help="Analysis handle: used to specify replacement map and XS*BR normalisations")
  parser.add_option('--massPoints', dest='massPoints', default='120,125,130', help="Mass points to fit")
  parser.add_option('--skipBeamspotReweigh', dest='skipBeamspotReweigh', default=False, action="store_true", help="Skip beamspot reweigh to match beamspot distribution in data")
  parser.add_option('--doPlots', dest='doPlots', default=False, action="store_true", help="Produce Signal Fitting plots")
  parser.add_option("--doVoigtian", dest='doVoigtian', default=False, action="store_true", help="Use Voigtians instead of Gaussians for signal models with Higgs width as parameter")
  parser.add_option("--useDCB", dest='useDCB', default=False, action="store_true", help="Use DCB in signal fitting")
  parser.add_option("--useDiagonalProcForShape", dest='useDiagonalProcForShape', default=False, action="store_true", help="Use shape of diagonal process, keeping normalisation (requires diagonal mapping produced by getDiagProc script)")
  parser.add_option('--skipVertexScenarioSplit', dest='skipVertexScenarioSplit', default=False, action="store_true", help="Skip vertex scenario split")
  parser.add_option('--skipZeroes', dest='skipZeroes', default=False, action="store_true", help="Skip proc x cat is numEntries = 0., or sumEntries < 0.")
  # For systematics
  parser.add_option('--skipSystematics', dest='skipSystematics', default=False, action="store_true", help="Skip shape systematics in signal model")
  parser.add_option('--useDiagonalProcForSyst', dest='useDiagonalProcForSyst', default=False, action="store_true", help="Use diagonal process for systematics (requires diagonal mapping produced by getDiagProc script)")
  parser.add_option("--scales", dest='scales', default='', help="Photon shape systematics: scales")
  parser.add_option("--scalesCorr", dest='scalesCorr', default='', help='Photon shape systematics: scalesCorr')
  parser.add_option("--scalesGlobal", dest='scalesGlobal', default='', help='Photon shape systematics: scalesGlobal')
  parser.add_option("--smears", dest='smears', default='', help='Photon shape systematics: smears')
  # Parameter values
  parser.add_option('--replacementThreshold', dest='replacementThreshold', default=100, type='int', help="Nevent threshold to trigger replacement dataset")
  parser.add_option('--beamspotWidthData', dest='beamspotWidthData', default=3.5, type='float', help="Width of beamspot in data [cm]")
  parser.add_option('--beamspotWidthMC', dest='beamspotWidthMC', default=3.7, type='float', help="Width of beamspot in MC [cm]")
  parser.add_option('--MHPolyOrder', dest='MHPolyOrder', default=1, type='int', help="Order of polynomial for MH dependence")
  parser.add_option('--nBins', dest='nBins', default=80, type='int', help="Number of bins for fit")
  # Minimizer options
  parser.add_option('--minimizerMethod', dest='minimizerMethod', default='TNC', help="(Scipy) Minimizer method")
  parser.add_option('--minimizerTolerance', dest='minimizerTolerance', default=1e-8, type='float', help="(Scipy) Minimizer toleranve")
  return parser.parse_args()
(opt,args) = get_options()

ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(True)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SETUP: signal fit
print(" --> Running fit for (proc,cat) = (%s,%s)"%(opt.proc,opt.cat))
if( len(opt.massPoints.split(",")) == 1 )&( opt.MHPolyOrder > 0 ):
  print(" --> [WARNING] Attempting to fit polynomials of O(MH^%g) for single mass point. Setting order to 0"%opt.MHPolyOrder)
  opt.MHPolyOrder=0

# Add stopwatch function

# Load replacement map
if opt.analysis not in globalReplacementMap:
  print(" --> [ERROR] replacement map does not exist for analysis (%s). Please add to tools/replacementMap.py"%opt.analysis)
  leave()
else: rMap = globalReplacementMap[opt.analysis]

# Load XSBR map
if opt.analysis not in globalXSBRMap:
  print(" --> [ERROR] XS * BR map does not exist for analysis (%s). Please add to tools/XSBRMap.py"%opt.analysis)
  leave()
else: xsbrMap = globalXSBRMap[opt.analysis]

# Load RooRealVars
nominalWSFileName = glob.glob("%s/output*M%s*%s.root"%(opt.inputWSDir,MHNominal,opt.proc))[0]
f0 = ROOT.TFile(nominalWSFileName,"read")
inputWS0 = f0.Get(inputWSName__)
xvar = inputWS0.var(opt.xvar)
xvarFit = xvar.Clone()
dZ = inputWS0.var("dZ")
aset = ROOT.RooArgSet(xvar,dZ)
f0.Close()

# Create MH var
MH = ROOT.RooRealVar("MH","m_{H}", int(MHLow), int(MHHigh))
MH.setUnit("GeV")
MH.setConstant(True)

if opt.skipZeroes:
  # Extract nominal mass dataset and see if entries == 0
  WSFileName = glob.glob("%s/output*M%s*%s.root"%(opt.inputWSDir,MHNominal,opt.proc))[0]
  f = ROOT.TFile(WSFileName,"read")
  inputWS = f.Get(inputWSName__)
  d = reduceDataset(inputWS.data("%s_%s_%s_%s"%(procToData(opt.proc.split("_")[0]),MHNominal,sqrts__,opt.cat)),aset)
  if( d.numEntries() == 0. )|( d.sumEntries <= 0. ):
    print(" --> (%s,%s) has zero events. Will not construct signal model"%(opt.proc,opt.cat))
    exit()
  inputWS.Delete()
  f.Close()
 
# Define proc x cat with which to extract shape: if skipVertexScenarioSplit label all events as "RV"
procRVFit, catRVFit = opt.proc, opt.cat
if opt.skipVertexScenarioSplit: 
  print(" --> Skipping vertex scenario split")
else:
  procWVFit, catWVFit = opt.proc, opt.cat

# Options for using diagonal process from getDiagProc output json
if opt.useDiagonalProcForShape:
  if not os.path.exists("%s/outdir_%s/getDiagProc/json/diagonal_process.json"%(swd__,opt.ext)):
    print(" --> [ERROR] Diagonal process json from getDiagProc does not exist. Using nominal proc x cat for shape")
  else:
    with open("%s/outdir_%s/getDiagProc/json/diagonal_process.json"%(swd__,opt.ext),"r") as jf: dproc = json.load(jf)
    procRVFit = dproc[opt.cat]
    print(" --> Using diagonal proc (%s,%s) for shape"%(procRVFit,opt.cat))
    if not opt.skipVertexScenarioSplit: procWVFit = dproc[opt.cat]

# Process for syst
procSyst = opt.proc
if opt.useDiagonalProcForSyst:
  if not os.path.exists("%s/outdir_%s/getDiagProc/json/diagonal_process.json"%(swd__,opt.ext)):
    print(" --> [ERROR] Diagonal process json from getDiagProc does not exist. Using nominal proc x cat for systematics")
  else:
    with open("%s/outdir_%s/getDiagProc/json/diagonal_process.json"%(swd__,opt.ext),"r") as jf: dproc = json.load(jf)
    procSyst = dproc[opt.cat]
    print(" --> Using diagonal proc (%s,%s) for systematics"%(procSyst,opt.cat))

# Define process with which to extract normalisation: nominal
procNorm, catNorm = opt.proc, opt.cat

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXTRACT DATASETS TO FIT (for each mass point)
nominalDatasets = od()
# For RV (or if skipping vertex scenario split)
datasetRVForFit = od()
for mp in opt.massPoints.split(","):
  WSFileName = glob.glob("%s/output*M%s*%s.root"%(opt.inputWSDir,mp,procRVFit))[0]
  f = ROOT.TFile(WSFileName,"read")
  inputWS = f.Get(inputWSName__)
  d = reduceDataset(inputWS.data("%s_%s_%s_%s"%(procToData(procRVFit.split("_")[0]),mp,sqrts__,catRVFit)),aset)
  nominalDatasets[mp] = d.Clone()
  if opt.skipVertexScenarioSplit: datasetRVForFit[mp] = d
  else: datasetRVForFit[mp] = splitRVWV(d,aset,mode="RV")
  inputWS.Delete()
  f.Close()

# Check if nominal yield > threshold (or if +ve sum of weights). If not then use replacement proc x cat
if( datasetRVForFit[MHNominal].numEntries() < opt.replacementThreshold  )|( datasetRVForFit[MHNominal].sumEntries() < 0. ):
  nominal_numEntries = datasetRVForFit[MHNominal].numEntries()
  procReplacementFit, catReplacementFit = rMap['procRVMap'][opt.cat], rMap['catRVMap'][opt.cat]
  for mp in opt.massPoints.split(","):
    WSFileName = glob.glob("%s/output*M%s*%s.root"%(opt.inputWSDir,mp,procReplacementFit))[0]
    f = ROOT.TFile(WSFileName,"read")
    inputWS = f.Get(inputWSName__)
    d = reduceDataset(inputWS.data("%s_%s_%s_%s"%(procToData(procReplacementFit.split("_")[0]),mp,sqrts__,catReplacementFit)),aset)
    if opt.skipVertexScenarioSplit: datasetRVForFit[mp] = d
    else: datasetRVForFit[mp] = splitRVWV(d,aset,mode="RV")
    inputWS.Delete()
    f.Close() 

  # Check if replacement dataset has too few entries: if so throw error
  if( datasetRVForFit[MHNominal].numEntries() < opt.replacementThreshold )|( datasetRVForFit[MHNominal].sumEntries() < 0. ):
    print(" --> [ERROR] replacement dataset (%s,%s) has too few entries (%g < %g)"%(procReplacementFit,catReplacementFit,datasetRVForFit[MHNominal].numEntries(),opt.replacementThreshold))
    sys.exit(1)

  else:
    procRVFit, catRVFit = procReplacementFit, catReplacementFit
    if opt.skipVertexScenarioSplit: 
      print(" --> Too few entries in nominal dataset (%g < %g). Using replacement (proc,cat) = (%s,%s) for extracting shape"%(nominal_numEntries,opt.replacementThreshold,procRVFit,catRVFit))
      for mp in opt.massPoints.split(","):
        print("     * MH = %s GeV: numEntries = %g, sumEntries = %.6f"%(mp,datasetRVForFit[mp].numEntries(),datasetRVForFit[mp].sumEntries()))
    else: 
      print(" --> RV: Too few entries in nominal dataset (%g < %g). Using replacement (proc,cat) = (%s,%s) for extracting shape"%(nominal_numEntries,opt.replacementThreshold,procRVFit,catRVFit))
      for mp in opt.massPoints.split(","):
        print("     * MH = %s: numEntries = %g, sumEntries = %.6f"%(mp,datasetRVForFit[mp].numEntries(),datasetRVForFit[mp].sumEntries()))

else:
  if opt.skipVertexScenarioSplit: 
    print(" --> Using (proc,cat) = (%s,%s) for extracting shape"%(procRVFit,catRVFit))
    for mp in opt.massPoints.split(","):
      print("     * MH = %s: numEntries = %g, sumEntries = %.6f"%(mp,datasetRVForFit[mp].numEntries(),datasetRVForFit[mp].sumEntries()))
  else: 
    print(" --> RV: Using (proc,cat) = (%s,%s) for extracting shape"%(procRVFit,catRVFit))
    for mp in opt.massPoints.split(","):
      print("     * MH = %s: numEntries = %g, sumEntries = %.6f"%(mp,datasetRVForFit[mp].numEntries(),datasetRVForFit[mp].sumEntries()))

# Repeat for WV scenario
if not opt.skipVertexScenarioSplit:
  datasetWVForFit = od()
  for mp in opt.massPoints.split(","):
    WSFileName = glob.glob("%s/output*M%s*%s.root"%(opt.inputWSDir,mp,procWVFit))[0]
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
      WSFileName = glob.glob("%s/output*M%s*%s.root"%(opt.inputWSDir,mp,procReplacementFit))[0]
      f = ROOT.TFile(WSFileName,"read")
      inputWS = f.Get(inputWSName__)
      d = reduceDataset(inputWS.data("%s_%s_%s_%s"%(procToData(procReplacementFit.split("_")[0]),mp,sqrts__,catReplacementFit)),aset)
      datasetWVForFit[mp] = splitRVWV(d,aset,mode="WV")
      inputWS.Delete()
      f.Close()
    # Check if replacement dataset has too few entries: if so throw error
    if( datasetWVForFit[MHNominal].numEntries() < opt.replacementThreshold )|( datasetWVForFit[MHNominal].sumEntries() < 0. ):
      print(" --> [ERROR] replacement dataset (%s,%s) has too few entries (%g < %g)"%(procReplacementFit,catReplacementFit,datasetWVForFit[MHNominal].numEntries,opt.replacementThreshold))
      sys.exit(1)
    else:
      procWVFit, catWVFit = procReplacementFit, catReplacementFit
      print(" --> WV: Too few entries in nominal dataset (%g < %g). Using replacement (proc,cat) = (%s,%s) for extracting shape"%(nominal_numEntries,opt.replacementThreshold,procWVFit,catWVFit))
      for mp in opt.massPoints.split(","):
        print("     * MH = %s: numEntries = %g, sumEntries = %.6f"%(mp,datasetWVForFit[mp].numEntries(),datasetWVForFit[mp].sumEntries()))
  else:
    print(" --> WV: Using (proc,cat) = (%s,%s) for extracting shape"%(procWVFit,catRVFit))
    for mp in opt.massPoints.split(","):
      print("     * MH = %s: numEntries = %g, sumEntries = %.6f"%(mp,datasetWVForFit[mp].numEntries(),datasetWVForFit[mp].sumEntries()))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# BEAMSPOT REWEIGH
if not opt.skipBeamspotReweigh:
  # Datasets for fit
  for mp,d in datasetRVForFit.items(): 
    drw = beamspotReweigh(datasetRVForFit[mp],opt.beamspotWidthData,opt.beamspotWidthMC,xvar,dZ,_x=opt.xvar)
    datasetRVForFit[mp] = drw
  if not opt.skipVertexScenarioSplit:
    for mp,d in datasetWVForFit.items(): 
      drw = beamspotReweigh(datasetWVForFit[mp],opt.beamspotWidthData,opt.beamspotWidthMC,xvar,dZ,_x=opt.xvar)
      datasetWVForFit[mp] = drw
    print(" --> Beamspot reweigh: RV(sumEntries) = %.6f, WV(sumEntries) = %.6f"%(datasetRVForFit[mp].sumEntries(),datasetWVForFit[mp].sumEntries()))
  else:
    print(" --> Beamspot reweigh: sumEntries = %.6f"%datasetRVForFit[mp].sumEntries())

  # Nominal datasets for saving to output Workspace: preserve norm for eff * acc calculation
  for mp,d in nominalDatasets.items():
    drw = beamspotReweigh(d,opt.beamspotWidthData,opt.beamspotWidthMC,xvar,dZ,_x=opt.xvar,preserveNorm=True)
    nominalDatasets[mp] = drw

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# If using nGaussian fit then extract nGaussians from fTest json file
if not opt.useDCB:
  with open("%s/outdir_%s/fTest/json/nGauss_%s.json"%(swd__,opt.ext,catRVFit)) as jf: ngauss = json.load(jf)
  nRV = int(ngauss["%s__%s"%(procRVFit,catRVFit)]['nRV'])
  if opt.skipVertexScenarioSplit: print(" --> Fitting function: convolution of nGaussians (%g)"%nRV)
  else: 
    with open("%s/outdir_%s/fTest/json/nGauss_%s.json"%(swd__,opt.ext,catWVFit)) as jf: ngauss = json.load(jf)
    nWV = int(ngauss["%s__%s"%(procWVFit,catWVFit)]['nWV'])
    print(" --> Fitting function: convolution of nGaussians (RV=%g,WV=%g)"%(nRV,nWV))
else:
  print(" --> Fitting function: DCB + 1 Gaussian")

if opt.doVoigtian:
  print(" --> Will add natural Higgs width as parameter in Pdf (Gaussians -> Voigtians)")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# FIT: simultaneous signal fit (ssf)
ssfMap = od()
name = "Total" if opt.skipVertexScenarioSplit else "RV"
ssfRV = SimultaneousFit(name,opt.proc,opt.cat,datasetRVForFit,xvar.Clone(),MH,MHLow,MHHigh,opt.massPoints,opt.nBins,opt.MHPolyOrder,opt.minimizerMethod,opt.minimizerTolerance)
if opt.useDCB: ssfRV.buildDCBplusGaussian()
else: ssfRV.buildNGaussians(nRV)
ssfRV.runFit()
ssfRV.buildSplines()
ssfMap[name] = ssfRV

if not opt.skipVertexScenarioSplit:
  name = "WV"
  ssfWV = SimultaneousFit(name,opt.proc,opt.cat,datasetWVForFit,xvar.Clone(),MH,MHLow,MHHigh,opt.massPoints,opt.nBins,opt.MHPolyOrder,opt.minimizerMethod,opt.minimizerTolerance)
  if opt.useDCB: ssfWV.buildDCBplusGaussian()
  else: ssfWV.buildNGaussians(nWV)
  ssfWV.runFit()
  ssfWV.buildSplines()
  ssfMap[name] = ssfWV

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# FINAL MODEL: construction
print("\n --> Constructing final model")
fm = FinalModel(ssfMap,opt.proc,opt.cat,opt.ext,opt.year,sqrts__,nominalDatasets,xvar,MH,MHLow,MHHigh,opt.massPoints,xsbrMap,procSyst,opt.scales,opt.scalesCorr,opt.scalesGlobal,opt.smears,opt.doVoigtian,opt.useDCB,opt.skipVertexScenarioSplit,opt.skipSystematics)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SAVE: to output workspace
foutDir = "%s/outdir_%s/signalFit/output"%(swd__,opt.ext)
foutName = "%s/outdir_%s/signalFit/output/CMS-HGG_sigfit_%s_%s_%s_%s.root"%(swd__,opt.ext,opt.ext,opt.proc,opt.year,opt.cat)
print("\n --> Saving output workspace to file: %s"%foutName)
if not os.path.isdir(foutDir): os.system("mkdir %s"%foutDir)
fout = ROOT.TFile(foutName,"RECREATE")
outWS = ROOT.RooWorkspace("%s_%s"%(outputWSName__,sqrts__),"%s_%s"%(outputWSName__,sqrts__))
fm.save(outWS)
outWS.Write()
fout.Close()
  
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# PLOTTING
if opt.doPlots:
  print("\n --> Making plots...")
  if not os.path.isdir("%s/outdir_%s/signalFit/Plots"%(swd__,opt.ext)): os.system("mkdir %s/outdir_%s/signalFit/Plots"%(swd__,opt.ext))
  if opt.skipVertexScenarioSplit:
    plotPdfComponents(ssfRV,_outdir="%s/outdir_%s/signalFit/Plots"%(swd__,opt.ext),_extension="total_",_proc=procRVFit,_cat=catRVFit) 
  if not opt.skipVertexScenarioSplit:
    plotPdfComponents(ssfRV,_outdir="%s/outdir_%s/signalFit/Plots"%(swd__,opt.ext),_extension="RV_",_proc=procRVFit,_cat=catRVFit) 
    plotPdfComponents(ssfWV,_outdir="%s/outdir_%s/signalFit/Plots"%(swd__,opt.ext),_extension="WV_",_proc=procWVFit,_cat=catRVFit) 
  # Plot interpolation
  plotInterpolation(fm,_outdir="%s/outdir_%s/signalFit/Plots"%(swd__,opt.ext)) 
  plotSplines(fm,_outdir="%s/outdir_%s/signalFit/Plots"%(swd__,opt.ext),_nominalMass=MHNominal) 
