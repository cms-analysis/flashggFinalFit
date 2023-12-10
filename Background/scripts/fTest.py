print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG BACKGROUND FITTER ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
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
from scipy import linalg

from commonTools import *
from commonObjects import *
from backgroundFunctions import *
from modelBuilder_v2 import *
from plottingTools import *

import control_regions

def tryMake(directory):
  try:
    os.mkdir(directory)
  except:
    pass

def leave():
  print "\n ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG BACKGROUND FITTER (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
  sys.exit(0)

def get_options():
  parser = OptionParser()
  parser.add_option("--xvar", dest='xvar', default='CMS_hgg_mass', help="Observable to fit")
  parser.add_option("--inputWSFile", dest='inputWSFile', default='', help="Input flashgg WS file: usually path to allData.root")
  parser.add_option("--ext", dest='ext', default='', help="Extension")
  parser.add_option("--cat", dest='cat', default='', help="RECO category")
  parser.add_option("--year", dest='year', default='2016', help="Year. Use 'merged' for year-merged cat")
  parser.add_option("--blindingRegion", dest='blindingRegion', default='115,135', help="Only fit function outside this region (unless running with --fitFullRange)")
  parser.add_option("--plotBlindingRegion", dest='plotBlindingRegion', default=None, help="Region to blind in plot. If None, will default to --blindingRegion")
  parser.add_option("--fitFullRange", dest='fitFullRange', default=False, action="store_true", help="Fit background pdfs over full range, including the blinding region")
  parser.add_option("--maxOrder", dest='maxOrder', default=6, type='int', help="Max order of functions")
  parser.add_option("--pvalFTest", dest='pvalFTest', default=0.05, type='float', help="p-value threshold to include higher order function in envelope")
  #parser.add_option("--pvalFTest", dest='pvalFTest', default=0.65, type='float', help="p-value threshold to include higher order function in envelope")
  parser.add_option("--gofCriteria", dest='gofCriteria', default=0.01, type='float', help="goodness-of-fit threshold to include function in envelope")
  parser.add_option('--doPlots', dest='doPlots', default=False, action="store_true", help="Produce bkg fitting plots")
  #parser.add_option('--nBins', dest='nBins', default=80, type='int', help="Number of bins for fit")
  #parser.add_option('--nBinsOutput', dest='nBinsOutput', default=320, type='int', help="Number of bins for ouptut WS")
  # Minimizer options
  parser.add_option('--minimizerMethod', dest='minimizerMethod', default='TNC', help="(Scipy) Minimizer method")
  parser.add_option('--minimizerTolerance', dest='minimizerTolerance', default=1e-8, type='float', help="(Scipy) Minimizer tolerance")
  return parser.parse_args()
(opt,args) = get_options()

if opt.cat[-2:] == "cr":
  foutDir = "%s/outdir_%s/fTest/output"%(bwd__,opt.ext)
  if not os.path.isdir(foutDir): os.system("mkdir %s"%foutDir)
  foutName = "%s/outdir_%s/fTest/output/CMS-HGG_ws_%s.root"%(bwd__,opt.ext,opt.cat)
  control_regions.main(opt.inputWSFile, opt.cat, foutName)
  exit()

print(opt.blindingRegion)
if opt.plotBlindingRegion is not None:
  cat_num = int(opt.cat.split("cat")[1].split("cr")[0])
  if cat_num < 3:
    opt.plotBlindingRegion = (float(opt.plotBlindingRegion.split(",")[0]), float(opt.plotBlindingRegion.split(",")[1]))
  else:
    opt.plotBlindingRegion = None

ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(True)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SETUP
f = ROOT.TFile(opt.inputWSFile,"read")
inputWS = f.Get(inputWSName__)
xvar = inputWS.var(opt.xvar)
xvarFit = xvar.Clone()

data = inputWS.data("Data_%s_%s"%(sqrts__,opt.cat))

if( data.numEntries == 0 )|( data.sumEntries() <= 0. ):
  print " --> [ERROR] Attempting to running bkg modelling for category (%s) with zero/negative events"%opt.cat
  sys.exit(1)

# Extract blinding region in list
blindingRegion = [float(opt.blindingRegion.split(",")[0]),float(opt.blindingRegion.split(",")[1])]
print(blindingRegion)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CONSTRUCT MODEL
nBinsOutput = inputWS.var("CMS_hgg_mass").getBins()
nBins = int(nBinsOutput/4) #set as 1GeV intervals assuming it is originally 0.25 GeV intervals (see trees2ws_data.py)
print(nBinsOutput, nBins)

if xvar.getMax() > 180: # if high mass
  functionFamilies['HighMassDijet'] = od()
  functionFamilies['HighMassDijet']['name'] = ['HighMassDijet','hmdijet']
  fitHistType = "variable"
else:
  fitHistType = "fixed"

# if high mass or low stats, remove Bernstein
if (xvar.getMax() > 180) or (data.numEntries() < 100):
  del functionFamilies['Bernstein']

model = modelBuilder("model_%s_%s"%(opt.cat,opt.year),opt.cat,xvarFit,data,functionFamilies,nBins,blindingRegion,opt.minimizerMethod,opt.minimizerTolerance,fitHistType=fitHistType)
if opt.fitFullRange: model.setBlind(False)

# Perform fTest to determine if higher orders provide sufficient improvement in fit
model.fTest(_maxOrder = opt.maxOrder, _pvalFTest = opt.pvalFTest)

# Require each function to pass some minimum GOF criteria
model.goodnessOfFit(_gofCriteria = opt.gofCriteria)

for k in model.pdfs: print "%s --> Success: %s, Evals = %g, NLL = %.3f"%(k,model.pdfs[k]['status']['success'],model.pdfs[k]['status']['nfev'],model.pdfs[k]['NLL'])

#pdf_null = model.pdfs[('Exponential',1)]
#pdf_test = model.pdfs[('Exponential',1)]
#model.getProbabilityFTestFromToys(pdf_null,pdf_test,_outDir="/home/hep/mdk16/PhD/ggtt/finalfits_try2/CMSSW_10_2_13/src/flashggFinalFit/Background/fTest_with_toys",nToys=10)

#sys.exit(1)

# Build envelope
if opt.year == "merged": model.buildEnvelope(_extension="_%s"%sqrts__)
else: model.buildEnvelope(_extension="_%s_%s"%(opt.year,sqrts__))

# Find best-fit function and extract normalisation
model.getBestfit()
norm = model.getNorm( model.envelopePdfs[model.bestfitPdf]['pdf'])
print "\n --> Model normalisation: %.2f"%norm
if opt.year == "merged": model.buildNorm( norm, _extension="_%s"%sqrts__)
else: model.buildNorm( norm, _extension="_%s_%s"%(opt.year,sqrts__)) 

# Plotting
print "\n --> Plotting envelope"
tryMake("%s/plots"%bwd__)
tryMake("%s/plots/%s"%(bwd__,opt.year))
plotPdfMap(model,model.envelopePdfs,opt.plotBlindingRegion,_outdir="%s/plots/%s"%(bwd__,opt.year),_cat=opt.cat)
if model.xvar.getMax() > 180: #if high mass
  plotPdfMap(model,model.envelopePdfs,opt.plotBlindingRegion,_outdir="%s/plots/%s"%(bwd__,opt.year),_cat=opt.cat,setLogY=True)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SAVE: to output workspace

# Set nBins for output
model.setNBins(nBinsOutput)

# Create output file and save model contents
foutDir = "%s/outdir_%s/fTest/output"%(bwd__,opt.ext)
foutName = "%s/outdir_%s/fTest/output/CMS-HGG_multipdf_%s.root"%(bwd__,opt.ext,opt.cat)
print "\n --> Saving output multipdf to file: %s"%foutName
if not os.path.isdir(foutDir): os.system("mkdir %s"%foutDir)
fout = ROOT.TFile(foutName,"RECREATE")
outWS = ROOT.RooWorkspace(bkgWSName__,bkgWSName__)
model.save(outWS)
outWS.Write()
fout.Close()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
leave()
