# Functions for plotting 
import ROOT
from collections import OrderedDict as od
from commonObjects import *


# Plot final pdf at MH = 125 (with data) + individual Pdf components
def plotPdfComponents(ssf,_outdir='./',_extension='',_proc='',_cat=''):
  canv = ROOT.TCanvas()
  canv.SetLeftMargin(0.15)
  ssf.MH.setVal(125)
  LineColorMap = {0:ROOT.kAzure+1,1:ROOT.kRed-4,2:ROOT.kOrange,3:ROOT.kGreen+2,4:ROOT.kMagenta-9}
  pdfs = od()
  hists = od()
  hmax, hmin = 0, 0
  # Total pdf histogram
  hists['final'] = ssf.Pdfs['final'].createHistogram("h_final%s"%_extension,ssf.xvar,ROOT.RooFit.Binning(1600))
  hists['final'].SetLineWidth(2)
  hists['final'].SetLineColor(1)
  hists['final'].SetTitle("")
  hists['final'].GetXaxis().SetTitle("m_{#gamma#gamma} [GeV]")
  hists['final'].SetMinimum(0)
  if hists['final'].GetMaximum()>hmax: hmax = hists['final'].GetMaximum()
  if hists['final'].GetMinimum()<hmin: hmin = hists['final'].GetMinimum()
  hists['final'].GetXaxis().SetRangeUser(115,140)
  # Create data histogram
  hists['data'] = ssf.xvar.createHistogram("h_data%s"%_extension,ROOT.RooFit.Binning(ssf.nBins))
  ssf.DataHists['125'].fillHistogram(hists['data'],ROOT.RooArgList(ssf.xvar))
  hists['data'].Scale(float(ssf.nBins)/1600)
  hists['data'].SetMarkerStyle(20)
  hists['data'].SetMarkerColor(1)
  hists['data'].SetLineColor(1)
  if hists['data'].GetMaximum()>hmax: hmax = hists['data'].GetMaximum()
  if hists['data'].GetMinimum()<hmin: hmin = hists['data'].GetMinimum()
  # Draw histograms
  hists['final'].SetMaximum(1.2*hmax)
  hists['final'].SetMinimum(1.2*hmin)
  hists['final'].Draw("HIST")
  hists['data'].Draw("Same PE")
  # Individual Gaussian histograms
  for k,v in ssf.Pdfs.iteritems():
    if k == 'final': continue
    pdfs[k] = v
  if len(pdfs.keys())!=1:
    pdfItr = 0
    for k,v in pdfs.iteritems():
      if pdfItr == 0:
	if "gaus" in k: frac = ssf.Pdfs['final'].getComponents().getRealValue("frac_g0_constrained")
	else: frac = ssf.Pdfs['final'].getComponents().getRealValue("frac_constrained")
      else:
	frac = ssf.Pdfs['final'].getComponents().getRealValue("%s_%s_recursive_fraction_%s"%(ssf.proc,ssf.cat,k))
      # Create histogram with 1600 bins
      hists[k] = v.createHistogram("h_%s%s"%(k,_extension),ssf.xvar,ROOT.RooFit.Binning(1600))
      hists[k].Scale(frac)
      hists[k].SetLineColor(LineColorMap[pdfItr])
      hists[k].SetLineWidth(2)
      hists[k].SetLineStyle(2)
      hists[k].Draw("HIST SAME")
      pdfItr += 1
  # Add legend
  leg = ROOT.TLegend(0.58,0.6,0.86,0.8)
  leg.SetFillStyle(0)
  leg.SetLineColor(0)
  leg.SetTextSize(0.04)
  leg.AddEntry(hists['data'],"Simulation","ep")
  leg.AddEntry(hists['final'],"Parametric Model","L")
  leg.Draw("Same")
  if len(pdfs.keys())!=1:
    leg1 = ROOT.TLegend(0.6,0.4,0.86,0.6)
    leg1.SetFillStyle(0)
    leg1.SetLineColor(0)
    leg1.SetTextSize(0.035)
    for k,v in pdfs.iteritems(): leg1.AddEntry(hists[k],k,"L")
    leg1.Draw("Same")
  # Add Latex
  lat = ROOT.TLatex()
  lat.SetTextFont(42)
  lat.SetTextAlign(31)
  lat.SetNDC()
  lat.SetTextSize(0.03)
  lat.DrawLatex(0.9,0.92,"( %s , %s , %s )"%(ssf.name,_proc,_cat))
  lat1 = ROOT.TLatex()
  lat1.SetTextFont(42)
  lat1.SetTextAlign(11)
  lat1.SetNDC()
  lat1.SetTextSize(0.035)
  lat1.DrawLatex(0.65,0.3,"#chi^{2}/n(dof) = %.4f"%(ssf.getChi2()/ssf.Ndof))

  canv.Update()
  canv.SaveAs("%s/%sshape_pdf_components_%s_%s.png"%(_outdir,_extension,_proc,_cat))
  canv.SaveAs("%s/%sshape_pdf_components_%s_%s.pdf"%(_outdir,_extension,_proc,_cat))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Plot final pdf for each mass point
def plotInterpolation(_finalModel,_outdir='./',_massPoints='120,121,122,123,124,125,126,127,128,129,130'):

  canv = ROOT.TCanvas()
  colors = [ROOT.kRed,ROOT.kCyan,ROOT.kBlue+1,ROOT.kOrange-3,ROOT.kMagenta-7,ROOT.kGreen+1,ROOT.kYellow-7,ROOT.kViolet+6,ROOT.kTeal+1,ROOT.kPink+1,ROOT.kAzure+1]
  colorMap = {}
  for i, mp in enumerate(_massPoints.split(",")): colorMap[mp] = colors[i]
  # Set luminosity
  _finalModel.intLumi.setVal(float(lumiMap[_finalModel.year]))
  # Total pdf histograms
  dh = od()
  hists = od()
  hmax = 0.1 
  for mp in _massPoints.split(","):
    _finalModel.MH.setVal(int(mp))
    hists[mp] = _finalModel.Pdfs['final'].createHistogram("h_%s"%mp,_finalModel.xvar,ROOT.RooFit.Binning(3200))
    norm = _finalModel.Functions['final_normThisLumi'].getVal()
    if norm == 0.: hists[mp].Scale(0.)
    else: hists[mp].Scale((norm*3200)/(hists[mp].Integral()*_finalModel.xvar.getBins()))
    if mp in _finalModel.Datasets:
      hists[mp].SetLineWidth(2)
    else:
      hists[mp].SetLineWidth(1)
      hists[mp].SetLineStyle(2)
    hists[mp].SetLineColor(colorMap[mp])
    hists[mp].SetTitle("")
    if hists[mp].GetMaximum() > hmax: hmax = hists[mp].GetMaximum()

    # Create ROOT datahists and then histograms
    if mp in _finalModel.Datasets:
      dh[mp] = ROOT.RooDataHist("dh_%s"%mp,"dh_%s"%mp,ROOT.RooArgSet(_finalModel.xvar),_finalModel.Datasets[mp])
      hists['data_%s'%mp] = _finalModel.xvar.createHistogram("h_data_%s"%mp,ROOT.RooFit.Binning(_finalModel.xvar.getBins()))
      dh[mp].fillHistogram(hists['data_%s'%mp],ROOT.RooArgList(_finalModel.xvar))
      if norm == 0.: hists['data_%s'%mp].Scale(0)
      else: hists['data_%s'%mp].Scale(norm/(hists['data_%s'%mp].Integral()))
      hists['data_%s'%mp].SetMarkerStyle(20)
      hists['data_%s'%mp].SetMarkerColor(colorMap[mp])
      hists['data_%s'%mp].SetLineColor(colorMap[mp])

  # Extract first hist and clone for axes
  haxes = hists[hists.keys()[0]].Clone()
  haxes.GetXaxis().SetTitle("m_{#gamma#gamma} [GeV]")
  haxes.GetYaxis().SetTitle("Events / %.2f GeV"%((_finalModel.xvar.getMax()-_finalModel.xvar.getMin())/_finalModel.xvar.getBins()))
  haxes.SetMinimum(0)
  haxes.SetMaximum(hmax*1.2)
  haxes.GetXaxis().SetRangeUser(100,150)
  haxes.Draw("AXIS")

  # Draw rest of histograms
  for k,h in hists.iteritems(): 
    if "data" in k: h.Draw("Same EP")
    else: 
      h.Draw("Same HIST")

  # Add Latex
  lat = ROOT.TLatex()
  lat.SetTextFont(42)
  lat.SetTextAlign(31)
  lat.SetNDC()
  lat.SetTextSize(0.03)
  lat.DrawLatex(0.9,0.92,"%s"%(_finalModel.name))


  canv.Update()
  canv.SaveAs("%s/%s_model_vs_mH.png"%(_outdir,_finalModel.name))
  canv.SaveAs("%s/%s_model_vs_mH.pdf"%(_outdir,_finalModel.name))





# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Plot splines
def plotSplines(_finalModel,_outdir="./",_nominalMass='125',splinesToPlot=['xs','br','ea','fracRV']):
  canv = ROOT.TCanvas()
  colorMap = {'xs':ROOT.kRed-4,'br':ROOT.kAzure+1,'ea':ROOT.kGreen+1,'fracRV':ROOT.kMagenta-7,'norm':ROOT.kBlack}
  grs = od()
  grs['norm'] = ROOT.TGraph()
  for sp in splinesToPlot: grs[sp] = ROOT.TGraph()
  # Get value at nominal mass
  xnom = od()
  _finalModel.MH.setVal(float(_nominalMass))
  for sp in splinesToPlot: xnom[sp] = _finalModel.Splines[sp].getVal()
  _finalModel.intLumi.setVal(float(lumiMap[_finalModel.year]))
  xnom['norm'] = _finalModel.Functions['final_normThisLumi'].getVal()
  # Loop over mass points
  p = 0
  xmax, xmin = 0,0.5
  for mh in range(int(_finalModel.MHLow),int(_finalModel.MHHigh)+1):
    _finalModel.MH.setVal(float(mh))
    for sp in splinesToPlot:
      x = _finalModel.Splines[sp].getVal()
      if xnom[sp] == 0.: r = 1.
      else: r = x/xnom[sp]
      grs[sp].SetPoint(p,int(mh),r)
      if r > xmax: xmax = r
      if r < xmin: xmin = r
    # Overall norm
    x = _finalModel.Functions['final_normThisLumi'].getVal()
    if xnom['norm'] == 0.: r = 1.
    else: r = x/xnom['norm']
    grs['norm'].SetPoint(p,int(mh),r)
    if r > xmax: xmax = r
    if r < xmin: xmin = r
    p += 1
  # Draw axes
  haxes = ROOT.TH1F("h_axes_spl","h_axes_spl",int(_finalModel.MHHigh)-int(_finalModel.MHLow),int(_finalModel.MHLow),int(_finalModel.MHHigh))
  haxes.SetTitle("")
  haxes.GetXaxis().SetTitle("m_{H} [GeV]")
  haxes.GetXaxis().SetTitleSize(0.05)
  haxes.GetXaxis().SetTitleOffset(0.85)
  haxes.GetXaxis().SetLabelSize(0.035)
  haxes.GetYaxis().SetTitle("X/X(m_{H}=125)")
  haxes.GetYaxis().SetTitleOffset(0.85)
  haxes.GetYaxis().SetTitleSize(0.05)
  haxes.SetMaximum(1.2*xmax)
  haxes.SetMinimum(xmin)
  haxes.Draw()
  # Define legend
  leg = ROOT.TLegend(0.15,0.15,0.4,0.4)
  leg.SetFillStyle(0)
  leg.SetLineColor(0)
  leg.SetTextSize(0.04)
  # Draw graphs
  for x, gr in grs.iteritems(): 
    gr.SetLineColor(colorMap[x])
    gr.SetMarkerColor(colorMap[x])
    gr.SetMarkerStyle(20)
    gr.Draw("Same PL")
    if x == "norm": leg.AddEntry(gr,"N_{exp}: @%s = %.2f"%(_nominalMass,xnom['norm']))
    if x == "xs": leg.AddEntry(gr,"#sigma: @%s = %.2f pb"%(_nominalMass,xnom['xs']))
    if x == "br": leg.AddEntry(gr,"#bf{#it{#Beta}}: @%s = %.2f%%"%(_nominalMass,100*xnom['br']))
    if x == "ea": leg.AddEntry(gr,"#epsilon x #it{#Alpha}: @%s = %.2f%%"%(_nominalMass,100*xnom['ea']))
    if x == "fracRV": leg.AddEntry(gr,"RV fraction: @%s = %.2f%%"%(_nominalMass,100*xnom['fracRV']))
  leg.Draw("Same")
  grs['norm'].Draw("Same PL")
  # Add Latex
  lat = ROOT.TLatex()
  lat.SetTextFont(42)
  lat.SetTextAlign(31)
  lat.SetNDC()
  lat.SetTextSize(0.03)
  lat.DrawLatex(0.9,0.92,"%s"%(_finalModel.name))
  canv.Update()
  canv.SaveAs("%s/%s_splines.png"%(_outdir,_finalModel.name))
  canv.SaveAs("%s/%s_splines.pdf"%(_outdir,_finalModel.name))


  
