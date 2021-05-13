# Example script to build fit to RooDataSet

import ROOT
import glob
from commonObjects import *
from commonTools import *
from tools.simultaneousFit import *
from tools.plottingTools import *
from collections import OrderedDict as od
from optparse import OptionParser


def get_options():
  parser = OptionParser()
  parser.add_option('--inputFile', dest='inputFile', default = "", help='Input flashgg workspace to fit')
  parser.add_option('--proc', dest='proc', default='GG2H_0J_PTH_0_10', help="Name of signal process")
  parser.add_option('--cat', dest='cat', default='RECO_0J_PTH_0_10_Tag0', help="Name of analysis category")
  parser.add_option('--year', dest='year', default='2016', help="Year")
  parser.add_option('--nGauss', dest='nGauss', default=3, type='int', help="Number of gaussians")
  parser.add_option('--outputDir', dest='outputDir', default='.', help="Plot output directory")
  return parser.parse_args()
(opt,args) = get_options()

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)


# Open ROOT file storing datasets
f = opt.inputFile
fin = ROOT.TFile(f)
ws = fin.Get("tagsDumper/cms_hgg_13TeV")
xvar = ws.var("CMS_hgg_mass") # Could also build this manually rather than extracting from workspace (RooRealVar)

pm,d = signalFromFileName(f)
MHLow = '120'
MHHigh = '130'
massPoints = '125'
nBins = 160 #nBins for fit
MHPolyOrder = 0 # dependence of fit params on MH, set to 0 if using one mass point
minimizerMethod = 'TNC'
minimizerTolerance = 1e-8
nGauss = opt.nGauss
useDCB = False

# MH var
MH = ROOT.RooRealVar("MH","m_{H}", int(MHLow), int(MHHigh))

# Create dict to store datasets: key=mass point, value = ROOT.RooDataSet()
datasets = od()
datasets['125'] = ws.data("%s_125_13TeV_%s"%(pm,opt.cat))

# Build ssf object + pdfs
ssf = SimultaneousFit("name",opt.proc,opt.cat,datasets,xvar.Clone(),MH,MHLow,MHHigh,massPoints,nBins,MHPolyOrder,minimizerMethod,minimizerTolerance)
if useDCB: ssf.buildDCBplusGaussian()
else: ssf.buildNGaussians(nGauss)

# Run fits and build mean + sigma splines
ssf.runFit()
ssf.buildSplines()

# Plot pdf
plotPdfComponents(ssf,_outdir=opt.outputDir,_extension='total_',_proc=ssf.proc,_cat=ssf.cat)
