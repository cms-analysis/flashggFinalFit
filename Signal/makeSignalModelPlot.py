#!/usr/bin/env python

# Script for making signal model plot
import os, sys
import ROOT
import re, glob
import json
from optparse import OptionParser

lumi = {'2016':'35.9', '2017':'41.5', '2018':'59.8'}

#ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

def get_options():
  parser = OptionParser()
  parser.add_option('--processMap', dest='processMap', default='', help="Signal Process Map. Form: [proc,year] or [all,all]=sum all signal procs from all years falling in category")
  parser.add_option('--cat', dest='cat', default='', help="Analysis category")
  parser.add_option('--ext', dest='ext', default='test', help="Extension: defines output dir where signal models are saved")
  parser.add_option("--mass", dest="mass", default='125', help="Higgs mass")
  parser.add_option("--nBins", dest="nBins", default=160, type='int', help="Number of bins")
  parser.add_option("--pdf_nBins", dest="pdf_nBins", default=3200, type='int', help="Number of bins")
  parser.add_option("--translateCats", dest="translateCats", default=None, help="JSON to store cat translations")
  parser.add_option("--translateProcs", dest="translateProcs", default=None, help="JSON to store proc translations")
  parser.add_option("--doFWHM", dest="doFWHM", default=False, action='store_true', help="Do FWHM")
  return parser.parse_args()
(opt,args) = get_options()

def rooiter(x):
  iter = x.iterator()
  ret = iter.Next()
  while ret:
    yield ret
    ret = iter.Next()

def LoadTranslations(jsonfilename):
    with open(jsonfilename) as jsonfile:
        return json.load(jsonfile)
def Translate(name, ndict):
    return ndict[name] if name in ndict else name

# Function to extract the sigma effective of a histogram
def getEffSigma(_h):
  nbins, binw, xmin = _h.GetXaxis().GetNbins(), _h.GetXaxis().GetBinWidth(1), _h.GetXaxis().GetXmin()
  mu, rms, total = _h.GetMean(), _h.GetRMS(), _h.Integral()
  # Scan round window of mean: window RMS/binWidth (cannot be bigger than 0.1*number of bins)
  nWindow = int(rms/binw) if (rms/binw) < 0.1*nbins else int(0.1*nbins)
  # Determine minimum width of distribution which holds 0.693 of total
  rlim = 0.683*total
  wmin, iscanmin = 9999999, -999
  for iscan in range(-1*nWindow,nWindow+1):
    # Find bin idx in scan: iscan from mean
    i_centre = int((mu-xmin)/binw+1+iscan)
    x_centre = (i_centre-0.5)*binw+xmin # * 0.5 for bin centre
    x_up, x_down = x_centre, x_centre
    i_up, i_down = i_centre, i_centre
    # Define counter for yield in bins: stop when counter > rlim
    y = _h.GetBinContent(i_centre) # Central bin height
    r = y
    reachedLimit = False
    for j in range(1,nbins):
      if reachedLimit: continue
      # Up:
      if(i_up < nbins)&(not reachedLimit):
        i_up+=1
        x_up+=binw
        y = _h.GetBinContent(i_up) # Current bin height
        r+=y
        if r>rlim: reachedLimit = True
      else:
        print " --> Reach nBins in effSigma calc: %s. Returning 0 for effSigma"%_h.GetName()
        return 0
      # Down:
      if( not reachedLimit ):
        if(i_down > 0):
          i_down-=1
          x_down-=binw
          y = _h.GetBinContent(i_down) #Current bin height
          r+=y
          if r>rlim: reachedLimit = True
        else:
          print " --> Reach 0 in effSigma calc: %s. Returning 0 for effSigma"%_h.GetName()
          return 0
    # Calculate fractional width in bin takes above limt (assume linear)
    if y == 0.: dx = 0.
    else: dx = (r-rlim)*(binw/y)
    # Total width: half of peak
    w = (x_up-x_down+binw-dx)*0.5
    if w < wmin:
      wmin = w
      iscanmin = iscan
  # Return effSigma
  return wmin

# Load translations
translateCats = {} if opt.translateCats is None else LoadTranslations(opt.translateCats)
translateProcs = {} if opt.translateProcs is None else LoadTranslations(opt.translateProcs)

# Open signal workspace (output of packageSignal)
fin = ROOT.TFile("outdir_%s/CMS-HGG_sigfit_%s_%s.root"%(opt.ext,opt.ext,opt.cat))
w = fin.Get("wsig_13TeV")
w.var("MH").setVal(float(opt.mass))
mgg = w.var("CMS_hgg_mass")
mgg.setPlotLabel("m_{#gamma#gamma}")
mgg.setUnit("GeV")
mgg_arglist = ROOT.RooArgList(mgg)

# Extract the procs to be plotted
processMap = {'proc':opt.processMap.split(",")[0],'year':opt.processMap.split(",")[1]}
if processMap['proc'] == 'all':
  if processMap['year'] == 'all': allNorms = w.allFunctions().selectByName("*normThisLumi")
  else: allNorms = w.allFunctions().selectByName("*_%s_*normThisLumi"%processMap['year'])
elif processMap['year'] == 'all': allNorms = w.allFunctions().selectByName("*_%s_*normThisLumi"%processMap['proc'])
else: allNorms = w.allFunctions().selectByName("*_%s_*_%s_*normThisLumi"%(processMap['year'],processMap['proc']))

# Iterate over norms: re-weight dataset and create Histogram from pdf
data_rwgt = {}
pdf_hists = {}
for norm in rooiter(allNorms):
  nnorm = norm.GetName()
  # Extract year and proc from n
  year = nnorm.split("_")[1]
  proc = nnorm.split("13TeV_")[-1].split("_RECO")[0]
  # Set luminosity value depending on year
  w.var("IntLumi").setVal(float(lumi[year])*1000)
  nval = norm.getVal()
  # Make empty copy of dataset:
  d = w.data("sig_%s_%s_mass_m%s_%s"%(proc,year,opt.mass,opt.cat))
  d_rwgt = d.emptyClone("proc_%s_year_%s_cat_%s"%(proc,year,opt.cat))
  # Determine normFactor
  nf = nval/d.sumEntries()
  for i in range(d.numEntries()):
    p = d.get(i)
    rw, rwe = d.weight()*nf, d.weightError()*nf
    d_rwgt.add(p,rw,rwe)
  # Add dataset to rwgt dataset 
  data_rwgt[d_rwgt.GetName()] = d_rwgt

  # Extract pdf and create histogram from pdf
  pdf = w.pdf("extendhggpdfsmrel_%s_13TeV_%s_%sThisLumi"%(year,proc,opt.cat))
  pdf_hists["proc_%s_year_%s_cat_%s"%(proc,year,opt.cat)] = pdf.createHistogram("hpdf_proc_%s_year_%s_cat_%s"%(proc,year,opt.cat),mgg,ROOT.RooFit.Binning(opt.pdf_nBins))
  # Scale by factor to match binning
  pdf_hists["proc_%s_year_%s_cat_%s"%(proc,year,opt.cat)].Scale(float(opt.nBins)/320)
  

# Define data histogram and fill with all datasets
h_data = mgg.createHistogram("h_data", ROOT.RooFit.Binning(opt.nBins))
for k, v in data_rwgt.iteritems(): v.fillHistogram(h_data,mgg_arglist)
# Sum pdf histograms:
pdfitr = 0
for k, v in pdf_hists.iteritems():
  if pdfitr == 0: h_pdf = v.Clone("h_pdf")
  else: h_pdf += v
  pdfitr += 1
# Make individual year histograms
if processMap['year'] == 'all':
  h_pdf_splitByYear = {}
  for y in lumi: 
    h_pdf_splitByYear[y] = h_pdf.Clone("h_pdf_%s"%y)
    h_pdf_splitByYear[y].Reset()
  for k, v in pdf_hists.iteritems():
    for y in lumi:
      if y in k: h_pdf_splitByYear[y] += v 
# Extract and make eff sigma 
effSigma = getEffSigma(h_pdf)
effSigma_low, effSigma_high = h_pdf.GetMean()-effSigma, h_pdf.GetMean()+effSigma
h_effSigma = h_pdf.Clone()
h_effSigma.GetXaxis().SetRangeUser(effSigma_low,effSigma_high)

# Make plot
canv = ROOT.TCanvas("c","c",650,600)
canv.SetBottomMargin(0.12)
canv.SetLeftMargin(0.15)
canv.SetTickx()
canv.SetTicky()
h_axes = h_data.Clone()
h_axes.Reset()
h_axes.SetMaximum(h_data.GetMaximum()*1.2)
h_axes.SetMinimum(0.)
h_axes.GetXaxis().SetRangeUser(105,140)
h_axes.SetTitle("")
h_axes.GetXaxis().SetTitleSize(0.05)
h_axes.GetXaxis().SetTitleOffset(1.)
h_axes.GetYaxis().SetTitleSize(0.05)
h_axes.GetYaxis().SetTitleOffset(1.2)
h_axes.Draw()
# Legend
offset = 0.02
if processMap['year'] == 'all':
  leg0 = ROOT.TLegend(0.15+offset,0.6,0.5+offset,0.82)
  leg0.SetFillStyle(0)
  leg0.SetLineColor(0)
  leg0.SetTextSize(0.03)
  leg0.AddEntry(h_data,"Simulation","lep")
  leg0.AddEntry(h_pdf,"#splitline{Parametric}{model}","l")
  leg0.Draw("Same")

  leg1 = ROOT.TLegend(0.17+offset,0.45,0.4+offset,0.61)
  leg1.SetFillStyle(0)
  leg1.SetLineColor(0)
  leg1.SetTextSize(0.03)
  leg1.AddEntry(h_pdf_splitByYear['2016'],"2016: #scale[0.8]{#sigma_{eff} = %1.2f GeV}"%getEffSigma(h_pdf_splitByYear['2016']),"l")
  leg1.AddEntry(h_pdf_splitByYear['2017'],"2017: #scale[0.8]{#sigma_{eff} = %1.2f GeV}"%getEffSigma(h_pdf_splitByYear['2017']),"l")
  leg1.AddEntry(h_pdf_splitByYear['2018'],"2018: #scale[0.8]{#sigma_{eff} = %1.2f GeV}"%getEffSigma(h_pdf_splitByYear['2018']),"l")
  leg1.Draw("Same")
 
  leg2 = ROOT.TLegend(0.15+offset,0.3,0.5+offset,0.45)
  leg2.SetFillStyle(0)
  leg2.SetLineColor(0)
  leg2.SetTextSize(0.03)
  leg2.AddEntry(h_effSigma,"#sigma_{eff} = %1.2f GeV"%(0.5*(effSigma_high-effSigma_low)),"fl")
  leg2.Draw("Same")
else: 
  leg = ROOT.TLegend(0.15+offset,0.4,0.5+offset,0.82)
  leg.SetFillStyle(0)
  leg.SetLineColor(0)
  leg.SetTextSize(0.03)
  leg.AddEntry(h_data,"Simulation","lep")
  leg.AddEntry(h_pdf,"#splitline{Parametric}{model}","l")
  leg.AddEntry(h_effSigma,"#sigma_{eff} = %1.2f GeV"%(0.5*(effSigma_high-effSigma_low)),"fl")
  leg.Draw("Same")
# Set style effSigma
h_effSigma.SetLineColor(15)
h_effSigma.SetFillStyle(1001)
h_effSigma.SetFillColor(19)
h_effSigma.Draw("Same Hist F")
vline_effSigma_low = ROOT.TLine(effSigma_low,0,effSigma_low,h_pdf.GetBinContent(h_pdf.FindBin(effSigma_low)))
vline_effSigma_high = ROOT.TLine(effSigma_high,0,effSigma_high,h_pdf.GetBinContent(h_pdf.FindBin(effSigma_high)))
vline_effSigma_low.SetLineColor(15)
vline_effSigma_high.SetLineColor(15)
vline_effSigma_low.SetLineWidth(2)
vline_effSigma_high.SetLineWidth(2)
vline_effSigma_low.Draw("Same")
vline_effSigma_high.Draw("Same")
# Extract FWHM and set style
if opt.doFWHM:
  fwhm_low = h_pdf.GetBinCenter(h_pdf.FindFirstBinAbove(0.5*h_pdf.GetMaximum()))
  fwhm_high = h_pdf.GetBinCenter(h_pdf.FindLastBinAbove(0.5*h_pdf.GetMaximum()))
  fwhmArrow = ROOT.TArrow(fwhm_low,0.5*h_pdf.GetMaximum(),fwhm_high,0.5*h_pdf.GetMaximum(),0.02,"<>")
  fwhmArrow.SetLineWidth(2)
  fwhmArrow.Draw("Same <>")
  fwhmText = ROOT.TLatex()
  fwhmText.SetTextFont(42)
  fwhmText.SetTextAlign(11)
  fwhmText.SetNDC()
  fwhmText.SetTextSize(0.03)
  if processMap['year'] == 'all': fwhmText.DrawLatex(0.17+offset,0.25,"FWHM = %1.2f GeV"%(fwhm_high-fwhm_low))
  else: fwhmText.DrawLatex(0.17+offset,0.35,"FWHM = %1.2f GeV"%(fwhm_high-fwhm_low))

# Set style pdf
h_pdf.SetLineColor(4)
h_pdf.SetLineWidth(2)
h_pdf.Draw("Same Hist C")
if processMap['year'] == 'all':
  colorMap = {'2016':38,'2017':30,'2018':46}
  for k, v in h_pdf_splitByYear.iteritems():
    v.SetLineColor( colorMap[k] )
    v.SetLineStyle(2)
    v.SetLineWidth(2)
    v.Draw("Same Hist C")
# Set style: data
h_data.SetMarkerStyle(25)
h_data.SetMarkerColor(1)
h_data.SetLineColor(1)
h_data.SetLineWidth(2)
h_data.Draw("Same PE")

# Add TLatex to plot
lat0 = ROOT.TLatex()
lat0.SetTextFont(42)
lat0.SetTextAlign(11)
lat0.SetNDC()
lat0.SetTextSize(0.045)
lat0.DrawLatex(0.15,0.92,"#bf{CMS} #it{Simulation}")
lat0.DrawLatex(0.77,0.92,"13 TeV")
lat0.DrawLatex(0.16+offset,0.83,"H#rightarrow#gamma#gamma")
lat1 = ROOT.TLatex()
lat1.SetTextFont(42)
lat1.SetTextAlign(33)
lat1.SetNDC(1)
lat1.SetTextSize(0.035)
procStr = Translate(processMap['proc'],translateProcs) if processMap['proc']!='all' else ''
yearStr = processMap['year'] if processMap['year']!='all' else ''
lat1.DrawLatex(0.87,0.86,"%s"%Translate(opt.cat,translateCats))
lat1.DrawLatex(0.87,0.8,"%s %s"%(procStr,yearStr))

canv.Update()
