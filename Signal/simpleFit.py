# Example script to build fit to RooDataSet

import ROOT
from commonObjects import *
from tools.simultaneousFit import *
from tools.plottingTools import *
from collections import OrderedDict as od

ROOT.gROOT.SetBatch(True)

# Open ROOT file storing datasets
f = ROOT.TFile("/vols/cms/jl2117/hgg/ws/UL/Sept20/MC_final/signal_2016/output_GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8_GG2H_0J_PTH_0_10.root")
ws = f.Get("tagsDumper/cms_hgg_13TeV")
xvar = ws.var("CMS_hgg_mass") # Could also build this manually rather than extracting from workspace (RooRealVar)

processName = "GG2H_0J_PTH_0_10" #these are just used for output plot name
categoryName = "RECO_0J_PTH_0_10_Tag0" # these are just used for output plot names
MHLow = '120'
MHHigh = '130'
massPoints = '125'
nBins = 80 #nBins for fit
MHPolyOrder = 0 # dependence of fit params on MH, set to 0 if using one mass point
minimizerMethod = 'TNC'
minimizerTolerance = 1e-8
nGauss = 3
useDCB = False

# MH var
MH = ROOT.RooRealVar("MH","m_{H}", int(MHLow), int(MHHigh))

# Create dict to store datasets: key=mass point, value = ROOT.RooDataSet()
datasets = od()
datasets['125'] = ws.data("ggh_125_13TeV_RECO_0J_PTH_0_10_Tag0")

# Build ssf object + pdfs
ssf = SimultaneousFit("name",processName,categoryName,datasets,xvar.Clone(),MH,MHLow,MHHigh,massPoints,nBins,MHPolyOrder,minimizerMethod,minimizerTolerance)
if useDCB: ssf.buildDCBplusGaussian()
else: ssf.buildNGaussians(nGauss)

# Run fits and build mean + sigma splines
ssf.runFit()
ssf.buildSplines()

# Plot pdf
plotPdfComponents(ssf,_outdir="./",_extension='total_',_proc=ssf.proc,_cat=ssf.cat)
