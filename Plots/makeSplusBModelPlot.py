# Script to make migration + purity matrices and output yields table
#  * Read in PANDAS dataframe

import os, sys
import re
from optparse import OptionParser
import ROOT
import pandas as pd
import glob
import pickle
import math
import json
# Scripts for plotting
from usefulStyle import setCanvas, drawCMS, drawEnPu, drawEnYear, formatHisto
from shanePalette import set_color_palette

print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG MODEL PLOTTER RUN II ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
def leave():
  print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG MODEL PLOTTER RUN II (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
  sys.exit(1)

#ROOT.gROOT.SetBatch(True)

def get_options():
  parser = OptionParser()
  parser.add_option("--inputWSFile", dest="inputWSFile", default=None, help="Input RooWorkspace file. If loading snapshot then use a post-fit workspace where the option --saveWorkspace was set")
  parser.add_option("--cat", dest="cat", default=None, help="Analysis category. all = loop over cats and plot sum")
  parser.add_option("--unblind", dest="unblind", default=False, action="store_true", help="Unblind signal region")
  parser.add_option("--doBkgRenormalization", dest="doBkgRenormalization", default=False, action="store_true", help="Do Bkg renormalization")
  parser.add_option("--doBands", dest="doBands", default=False, action="store_true", help="Do +-1/2sigma bands for bkg model")
  parser.add_option("--doZeroes", dest="doZeroes", default=False, action="store_true", help="Add error of unity to zero bins to show on plot")
  parser.add_option("--skipIndividualCatPlots", dest="skipIndividualCatPlots", default=False, action="store_true", help="Skip plotting of individual categories")
  parser.add_option("--loadSnapshot", dest="loadSnapshot", default=None, help="Load best-fit snapshot name")
  parser.add_option("--parameterMap", dest="parameterMap", default=None, help="Comma separated pairs of model parameters:values,...")
  parser.add_option("--ext", dest="ext", default='', help="Extension for saving")
  parser.add_option("--mass", dest="mass", default=None, help="Higgs mass")
  parser.add_option("--xvar", dest="xvar", default="CMS_hgg_mass,m_{#gamma#gamma},GeV", help="X-variable: name,title,units")
  parser.add_option("--nBins", dest="nBins", default=80, type='int', help="Number of bins")
  parser.add_option("--pdfNBins", dest="pdfNBins", default=3200, type='int', help="Number of bins")
  parser.add_option("--translateCats", dest="translateCats", default=None, help="JSON to store cat translations")
  parser.add_option("--translatePOIs", dest="translatePOIs", default=None, help="JSON to store poi translations")
  return parser.parse_args()
(opt,args) = get_options()

#if opt.loadSnapshot is not None:
  # Load workspaces from snapshot

# Load translations from json
def LoadTranslations(jsonfilename):
    with open(jsonfilename) as jsonfile:
        return json.load(jsonfile)
def Translate(name, ndict):
    return ndict[name] if name in ndict else name
translateCats = {} if opt.translateCats is None else LoadTranslations(opt.translateCats)
translatePOIs = {} if opt.translatePOIs is None else LoadTranslations(opt.translatePOIs)

blindingRegion = [116.,134.]
  
# Open WS
if opt.inputWSFile is not None:
  print " --> Loading workspace"
  f = ROOT.TFile(opt.inputWSFile)
  w = f.Get("w")
  # If required loadSnapshot
  if opt.loadSnapshot is not None: w.loadSnapshot(opt.loadSnapshot)
  # Also loop over parameters in map and set
  if opt.parameterMap is not None:
    if opt.loadSnapshot is not None:
      print " --> [WARNING] Already loaded snapshot. Will not set parameters from opt.parameterMap"
      opt.parameterMap = None
    else:
      for kv in opt.parameterMap.split(","):
	k, v = kv.split(":")[0], kv.split(":")[1]
	w.var(k).setVal(float(v))

if opt.mass is not None: w.var("MH").setVal(float(opt.mass))
xvar = w.var(opt.xvar.split(",")[0]) 
xvar.SetTitle(opt.xvar.split(",")[1])
xvar.setPlotLabel(opt.xvar.split(",")[1])
xvar.setUnit(opt.xvar.split(",")[2])
xvar_arglist, xvar_argset = ROOT.RooArgList(xvar), ROOT.RooArgSet(xvar)
chan = w.cat("CMS_channel")

# Extract the total SB/B models
sb_model, b_model = w.pdf("model_s"), w.pdf("model_b")

# Extract dataasets and fill histograms
d_obs = w.data("data_obs")
data_cats = {}
print " --> Extracting data histograms"
for cidx in range(chan.numTypes()):
  chan.setIndex(cidx)
  if(opt.cat!='all')&(chan.getLabel()!=opt.cat): continue
  data_cats[chan.getLabel()] = ROOT.RooDataSet("d_%s"%chan.getLabel(),"d_%s"%chan.getLabel(),xvar_argset)
# Loop over bins and add entry for each "weight" to cat datasets 
for i in range(d_obs.numEntries()):
  p = d_obs.get(i)
  if(opt.cat!='all')&(p.getCatLabel("CMS_channel")!=opt.cat): continue
  nent = int(d_obs.weight())
  for ient in range(nent): data_cats[p.getCatLabel("CMS_channel")].add(p)
h_data = {}
for k, v in data_cats.iteritems(): 
  h_data[k] = xvar.createHistogram("h_data_%s"%k, ROOT.RooFit.Binning(opt.nBins))
  h_data[k].SetBinErrorOption(ROOT.TH1.kPoisson)
  if opt.unblind: v.fillHistogram(h_data[k],xvar_arglist)
  else: v.reduce("%s<%f|%s>%f"%(xvar.GetName(),blindingRegion[0],xvar.GetName(),blindingRegion[1])).fillHistogram(h_data[k],xvar_arglist)
    
# If option doZeroes: add error of +-unity for zeroth bins
if opt.doZeroes:
  print " --> Adding zeroes to data histograms"
  for c, h in h_data.iteritems():
    # Loop over bins
    for ibin in range(1,h.GetNbinsX()+1):
      bcenter = h.GetBinCenter(ibin)
      if( not opt.unblind )&(bcenter > blindingRegion[0])&(bcenter < blindingRegion[1]): continue
      if h.GetBinContent(ibin)==0.: h.SetBinError(ibin,1)

# PDFs: extract pdfs and make histograms
bpdfs, sbpdfs = {}, {}
h_spdfs, h_bpdfs, h_sbpdfs = {}, {}, {} # Dict: {pdfNBins,nBins}
print " --> Extracting PDF histograms"
for cidx in range(chan.numTypes()):
  chan.setIndex(cidx)
  c = chan.getLabel()
  print "   * Category: %s"%c
  if(opt.cat!='all')&(c!=opt.cat): continue
  sbpdfs[c], bpdfs[c] = sb_model.getPdf(c),b_model.getPdf(c)
  h_sbpdfs[c] = {"pdfNBins":sbpdfs[c].createHistogram("h_sb_pdfNBins_%s"%c,xvar,ROOT.RooFit.Binning(opt.pdfNBins)),
                "nBins":sbpdfs[c].createHistogram("h_sb_nBins_%s"%c,xvar,ROOT.RooFit.Binning(opt.nBins))
               }
  h_bpdfs[c] = {"pdfNBins":bpdfs[c].createHistogram("h_b_pdfNBins_%s"%c,xvar,ROOT.RooFit.Binning(opt.pdfNBins)),
                "nBins":bpdfs[c].createHistogram("h_b_nBins_%s"%c,xvar,ROOT.RooFit.Binning(opt.nBins))
               }

# Renormalize bpdf to be bpdf-spdf: initial B normalisation is sum S+B
if opt.doBkgRenormalization:
  print " --> Adjusting background normalization"
  for c in h_data:
    SB = sbpdfs[c].expectedEvents(xvar_argset)
    B = bpdfs[c].expectedEvents(xvar_argset)
    S = SB-B
    Bcorr = B-S
    SBcorr = B
    nf_b, nf_sb = Bcorr/B, SBcorr/SB
    for h in h_sbpdfs[c].itervalues(): h.Scale(nf_sb)
    for h in h_bpdfs[c].itervalues(): h.Scale(nf_b)

# Extract signal pdfs
for c in h_data:
  h_spdfs[c] = {"pdfNBins":h_sbpdfs[c]['pdfNBins']-h_bpdfs[c]['pdfNBins'],
                "nBins":h_sbpdfs[c]['nBins']-h_bpdfs[c]['nBins']
               }

# If using different number of bins then scale pdfs histograms accordingly
print " --> Scaling pdf histograms to match binning"
for c in h_data:
  xvar_range = int(xvar.getBinning().highBound()-xvar.getBinning().lowBound())
  if opt.nBins != xvar_range:
    for hists in [h_sbpdfs[c],h_bpdfs[c],h_spdfs[c]]:
      for h in hists.itervalues(): h.Scale(xvar_range/opt.nBins)

# Extract sum of data and pdfs
if opt.cat == 'all':
  print " --> Summing datasets and pdfs"
  cats = h_data.keys()
  for cidx in range(len(cats)):
    c = cats[cidx]
    if cidx == 0: 
      h_data['all'] = h_data[c].Clone()
      h_sbpdfs['all'] = {'pdfNBins':h_sbpdfs[c]['pdfNBins'].Clone(),'nBins':h_sbpdfs[c]['nBins'].Clone()}
      h_bpdfs['all'] = {'pdfNBins':h_bpdfs[c]['pdfNBins'].Clone(),'nBins':h_bpdfs[c]['nBins'].Clone()}
      h_spdfs['all'] = {'pdfNBins':h_spdfs[c]['pdfNBins'].Clone(),'nBins':h_spdfs[c]['nBins'].Clone()}
    else:
      h_data['all'] += h_data[c]
      h_sbpdfs['all']['pdfnbins'] += h_sbpdfs[c]['pdfnbins']
      h_sbpdfs['all']['nbins'] += h_sbpdfs[c]['nbins']
      h_bpdfs['all']['pdfnbins'] += h_bpdfs[c]['pdfnbins']
      h_bpdfs['all']['nbins'] += h_bpdfs[c]['nbins']
      h_spdfs['all']['pdfnbins'] += h_spdfs[c]['pdfnbins']
      h_spdfs['all']['nbins'] += h_spdfs[c]['nbins'] 

# Extract histograms for ratio plot
h_bpdfs_ratio = {} # Straight lines
h_spdfs_ratio = {} # Straight lines
h_data_ratio = {}
print " --> Making ratio histograms"
for c in h_data:
  h_bpdfs_ratio[c] = h_bpdfs[c]['pdfNBins']-h_bpdfs[c]['pdfNBins']
  h_spdfs_ratio[c] = h_spdfs[c]['pdfNBins'].Clone()
  h_data_ratio[c] = h_data[c].Clone()
  h_data_ratio[c].Reset()
  for ibin in range(1,h_data[c].GetNbinsX()+1):
    bcenter = h_data[c].GetBinCenter(ibin)
    if(not opt.unblind)&(bcenter>blindingRegion[0])&(bcenter<blindingRegion[1]): continue
    bval, berr = h_data[c].GetBinContent(ibin), h_data[c].GetBinError(ibin)
    bkgval = h_bpdfs[c]['nBins'].GetBinContent(ibin)
    h_data_ratio[c].SetBinContent(ibin,bval-bkgval)
    h_data_ratio[c].SetBinError(ibin,berr)
 


# Make individual category plots: for each cat
print " --> Making plots..."
for c in h_data:
  if(opt.skipIndividualCatPlots)&(c!='all'): continue
  canv = ROOT.TCanvas("canv_%s"%c,"canv_%s"%c,700,700)
  pad1 = ROOT.TPad("pad1_%s"%c,"pad1_%s"%c,0,0.25,1,1)
  pad1.SetTickx()
  pad1.SetTicky()
  pad1.SetBottomMargin(0.18)
  pad1.Draw()
  pad2 = ROOT.TPad("pad2_%s"%c,"pad2_%s"%c,0,0,1,0.35)
  pad2.SetTickx()
  pad2.SetTicky()
  pad2.SetTopMargin(0.000001)
  pad2.SetBottomMargin(0.25)
  pad2.Draw()
  
  padSizeRatio = 0.75/0.35

  # Nominal plot
  pad1.cd()
  h_axes = h_data[c].Clone()
  h_axes.Reset()
  h_axes.SetMaximum((h_data[c].GetMaximum()+h_data[c].GetBinError(h_data[c].GetMaximumBin()))*1.3)
  h_axes.SetMinimum(0.)
  h_axes.SetTitle("")
  h_axes.GetXaxis().SetTitle("")
  h_axes.GetXaxis().SetLabelSize(0)
  h_axes.GetYaxis().SetTitleSize(0.05)
  h_axes.GetYaxis().SetTitleOffset(0.9)
  h_axes.GetYaxis().SetLabelSize(0.035)
  h_axes.GetYaxis().SetLabelOffset(0.007)
  h_axes.Draw()
  # Add legend
  if opt.doBands: leg = ROOT.TLegend(0.58,0.36,0.86,0.76)
  else: leg = ROOT.TLegend(0.58,0.52,0.86,0.76)
  leg.SetFillStyle(0)
  leg.SetLineColor(0)
  leg.SetTextSize(0.045)
  leg.AddEntry(h_data[c],"Data","ep")
  if opt.unblind:
    leg.AddEntry(h_sbpdfs[c]['pdfNBins'],"S+B fit","l")
    leg.AddEntry(h_bpdfs[c]['pdfNBins'],"B component","l")
  else:
    leg.AddEntry(h_bpdfs[c]['pdfNBins'],"B fit","l")
    leg.AddEntry(h_spdfs[c]['pdfNBins'],"S model","fl")
  leg.Draw("Same")
  # Set pdf style
  if opt.unblind:
    h_sbpdfs[c]['pdfNBins'].SetLineWidth(3)
    h_sbpdfs[c]['pdfNBins'].SetLineColor(2)
    h_sbpdfs[c]['pdfNBins'].Draw("Hist same c")
    h_bpdfs[c]['pdfNBins'].SetLineWidth(3)
    h_bpdfs[c]['pdfNBins'].SetLineColor(2)
    h_bpdfs[c]['pdfNBins'].SetLineStyle(2)
    h_bpdfs[c]['pdfNBins'].Draw("Hist same c") 
  else:
    h_spdfs[c]['pdfNBins'].SetLineWidth(3)
    h_spdfs[c]['pdfNBins'].SetLineColor(9)
    h_spdfs[c]['pdfNBins'].SetFillColor(38)
    h_spdfs[c]['pdfNBins'].SetFillStyle(1001)
    h_spdfs[c]['pdfNBins'].GetXaxis().SetRangeUser(blindingRegion[0],blindingRegion[1])
    h_spdfs[c]['pdfNBins'].Draw("Hist same cf")
    h_bpdfs[c]['pdfNBins'].SetLineWidth(3)
    h_bpdfs[c]['pdfNBins'].SetLineColor(2)
    h_bpdfs[c]['pdfNBins'].Draw("Hist same c")
  # Set data style
  h_data[c].SetMarkerStyle(20)
  h_data[c].SetMarkerColor(1)
  h_data[c].SetLineColor(1)
  h_data[c].Draw("Same PE")
  # Add TLatex to plot
  lat0 = ROOT.TLatex()
  lat0.SetTextFont(42)
  lat0.SetTextAlign(11)
  lat0.SetNDC()
  lat0.SetTextSize(0.06)
  lat0.DrawLatex(0.1,0.92,"#bf{CMS} #it{Preliminary}")
  lat0.DrawLatex(0.6,0.92,"137 fb^{-1} (13 TeV)")
  lat0.DrawLatex(0.6,0.8,"#scale[0.75]{%s}"%Translate(c,translateCats))
  lat0.DrawLatex(0.13,0.83,"#scale[0.75]{H#rightarrow#gamma#gamma}")
  if(opt.loadSnapshot is not None): 
    muhat, mhhat = w.var("r").getVal(), w.var("MH").getVal()
    lat0.DrawLatex(0.13,0.77,"#scale[0.75]{#hat{m}_{H} = %.1f GeV, #hat{#mu} = %.2f}"%(mhhat,muhat))
  elif opt.parameterMap is not None:
    poiStr = ''
    for kv in opt.parameterMap.split(","):
      [k,v] = kv.split(":")
      poiStr += ' %s = %.1f,'%(Translate(k,translatePOIs),float(v))
    poiStr = poiStr[:-1]
    lat0.DrawLatex(0.13,0.77,"#scale[0.75]{%s}"%poiStr)
  # Ratio plot
  pad2.cd()
  h_axes_ratio = h_data_ratio[c].Clone()
  h_axes_ratio.Reset()
  h_axes_ratio.SetMaximum(max((h_data_ratio[c].GetMaximum()+h_data_ratio[c].GetBinError(h_data_ratio[c].GetMaximumBin()))*1.5,h_spdfs[c]['pdfNBins'].GetMaximum()*1.2))
  h_axes_ratio.SetMinimum((h_data_ratio[c].GetMinimum()-h_data_ratio[c].GetBinError(h_data_ratio[c].GetMinimumBin()))*1.2)
  h_axes_ratio.SetTitle("")
  h_axes_ratio.GetXaxis().SetTitleSize(0.05*padSizeRatio)
  h_axes_ratio.GetXaxis().SetLabelSize(0.035*padSizeRatio)
  h_axes_ratio.GetXaxis().SetLabelOffset(0.007)
  h_axes_ratio.GetXaxis().SetTickLength(0.03*padSizeRatio)
  h_axes_ratio.GetYaxis().SetLabelSize(0.035*padSizeRatio)
  h_axes_ratio.GetYaxis().SetLabelOffset(0.007)
  h_axes_ratio.GetYaxis().SetTitle("")
  h_axes_ratio.Draw()
  # Set pdf style
  if opt.unblind:
    h_spdfs_ratio[c].SetLineWidth(3)
    h_spdfs_ratio[c].SetLineColor(2)
    h_spdfs_ratio[c].Draw("Hist same c")
    h_bpdfs_ratio[c].SetLineWidth(3)
    h_bpdfs_ratio[c].SetLineStyle(2)
    h_bpdfs_ratio[c].SetLineColor(2)
    h_bpdfs_ratio[c].Draw("Hist same c")
  else:
    h_spdfs_ratio[c].SetLineWidth(3)
    h_spdfs_ratio[c].SetLineColor(9)
    h_spdfs_ratio[c].SetFillColor(38)
    h_spdfs_ratio[c].SetFillStyle(1001)
    h_spdfs_ratio[c].GetXaxis().SetRangeUser(blindingRegion[0],blindingRegion[1])
    h_spdfs_ratio[c].Draw("Hist same cf")
    h_bpdfs_ratio[c].SetLineWidth(3)
    h_bpdfs_ratio[c].SetLineColor(2)
    h_bpdfs_ratio[c].Draw("Hist same c")
  # Set data style
  h_data_ratio[c].SetMarkerStyle(20)
  h_data_ratio[c].SetMarkerColor(1)
  h_data_ratio[c].SetLineColor(1)
  h_data_ratio[c].Draw("Same PE")
  # Add TLatex to ratio plot
  lat1 = ROOT.TLatex()
  lat1.SetTextFont(42)
  lat1.SetTextAlign(33)
  lat1.SetNDC(1)
  lat1.SetTextSize(0.045*padSizeRatio)
  lat1.DrawLatex(0.87,0.93,"B component subtracted")

    
