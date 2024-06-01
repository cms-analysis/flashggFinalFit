import ROOT
import json
import math
import pandas
import numpy as np
import re

def Translate(name, ndict):
    return ndict[name] if name in ndict else name

def LoadTranslations(jsonfilename):
    with open(jsonfilename) as jsonfile:
        return json.load(jsonfile)

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
        print(" --> Reach nBins in effSigma calc: %s. Returning 0 for effSigma"%_h.GetName())
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
          print(" --> Reach 0 in effSigma calc: %s. Returning 0 for effSigma"%_h.GetName())
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

def extractBandProperties(data,category,bidx):
  props = {}
  if category == 'all': c = 'sum'
  elif category == 'wall': c = 'wsum'
  else: c = category
  props['median'] = np.median(data['%s_%g'%(c,bidx)].values)
  props['up1sigma'] = np.percentile(data['%s_%g'%(c,bidx)].values,50*(1+math.erf(1./math.sqrt(2))))
  props['down1sigma'] = np.percentile(data['%s_%g'%(c,bidx)].values,50*(1+math.erf(-1./math.sqrt(2))))
  props['up2sigma'] = np.percentile(data['%s_%g'%(c,bidx)].values,50*(1+math.erf(2./math.sqrt(2))))
  props['down2sigma'] = np.percentile(data['%s_%g'%(c,bidx)].values,50*(1+math.erf(-2./math.sqrt(2))))
  return props

def makeSplusBPlot(workspace,hD,hSB,hB,hS,hDr,hBr,hSr,cat,options,dB=None,reduceRange=None):
  translateCats = {} if options.translateCats is None else LoadTranslations(options.translateCats)
  translatePOIs = {} if options.translatePOIs is None else LoadTranslations(options.translatePOIs)
  blindingRegion = [float(options.blindingRegion.split(",")[0]),float(options.blindingRegion.split(",")[1])]
  if reduceRange is not None:
    for h in [hD,hDr,hBr,hSr]: h.GetXaxis().SetRangeUser(reduceRange[0],reduceRange[1])
    for h_ipdf in [hSB,hB,hS]:
      for h in h_ipdf.values(): h.GetXaxis().SetRangeUser(reduceRange[0],reduceRange[1])
  
  canv = ROOT.TCanvas("canv_%s"%cat,"canv_%s"%cat,700,700)
  pad1 = ROOT.TPad("pad1_%s"%cat,"pad1_%s"%cat,0,0.25,1,1)
  pad1.SetTickx()
  pad1.SetTicky()
  pad1.SetBottomMargin(0.18)
  pad1.SetLeftMargin(0.12)
  pad1.Draw()
  pad2 = ROOT.TPad("pad2_%s"%cat,"pad2_%s"%cat,0,0,1,0.35)
  pad2.SetTickx()
  pad2.SetTicky()
  pad2.SetTopMargin(0.03)
  pad2.SetBottomMargin(0.25)
  pad2.SetLeftMargin(0.12)
  pad2.Draw()
  padSizeRatio = 0.75/0.35

  # Axis options 
  ROOT.TGaxis.SetMaxDigits(4)
  ROOT.TGaxis.SetExponentOffset(-0.05,0.00,"y")

  # Nominal plot
  pad1.cd()
  h_axes = hD.Clone()
  h_axes.Reset()
  if options.doBands: h_axes.SetMaximum((hD.GetMaximum()+hD.GetBinError(hD.GetMaximumBin()))*1.4)
  else: h_axes.SetMaximum((hD.GetMaximum()+hD.GetBinError(hD.GetMaximumBin()))*1.3)
  h_axes.SetMinimum(0.)
  h_axes.SetTitle("")
  h_axes.GetXaxis().SetTitle("")
  h_axes.GetXaxis().SetLabelSize(0)
  h_axes.GetYaxis().SetTitleSize(0.05)
  h_axes.GetYaxis().SetTitle("Events / GeV")
  h_axes.GetYaxis().SetTitleOffset(1.1)
  h_axes.GetYaxis().SetLabelSize(0.035)
  h_axes.GetYaxis().SetLabelOffset(0.007)
  #if cat == "wall": h_axes.GetYaxis().SetTitle("S/(S+B) Weighted %s"%h_axes.GetYaxis().GetTitle())
  if cat == "wall": h_axes.GetYaxis().SetTitle("S/(S+B) Weighted Events / GeV")
  h_axes.Draw()
  # Add bands
  if options.doBands:
    gr_1sig, gr_1sig_r = ROOT.TGraphAsymmErrors(), ROOT.TGraphAsymmErrors()
    gr_2sig, gr_2sig_r = ROOT.TGraphAsymmErrors(), ROOT.TGraphAsymmErrors()
    gr_i = 0
    # Loop over bins and extract median and +-1/2sigma bands
    for ibin in range(h_axes.GetXaxis().GetFirst(),h_axes.GetNbinsX()+1):
      xval = h_axes.GetXaxis().GetBinCenter(ibin)
      xerr = 0.5*(h_axes.GetXaxis().GetBinWidth(ibin))
      bkgval = hB['nBins'].GetBinContent(ibin)
      properties = extractBandProperties(dB,cat,ibin)
      gr_1sig.SetPoint(gr_i,xval,properties['median'])
      gr_2sig.SetPoint(gr_i,xval,properties['median'])
      gr_1sig_r.SetPoint(gr_i,xval,properties['median']-bkgval)
      gr_2sig_r.SetPoint(gr_i,xval,properties['median']-bkgval)
      gr_1sig.SetPointError(gr_i,xerr,xerr,properties['median']-properties['down1sigma'],properties['up1sigma']-properties['median'])
      gr_2sig.SetPointError(gr_i,xerr,xerr,properties['median']-properties['down2sigma'],properties['up2sigma']-properties['median'])
      gr_1sig_r.SetPointError(gr_i,xerr,xerr,properties['median']-properties['down1sigma'],properties['up1sigma']-properties['median'])
      gr_2sig_r.SetPointError(gr_i,xerr,xerr,properties['median']-properties['down2sigma'],properties['up2sigma']-properties['median'])
      gr_i += 1
    gr_1sig.SetFillColor(ROOT.kGreen)
    gr_1sig.SetFillStyle(1001)
    gr_2sig.SetFillColor(ROOT.kYellow)
    gr_2sig.SetFillStyle(1001)
    gr_1sig_r.SetFillColor(ROOT.kGreen)
    gr_1sig_r.SetFillStyle(1001)
    gr_2sig_r.SetFillColor(ROOT.kYellow)
    gr_2sig_r.SetFillStyle(1001)
    gr_2sig.Draw("LE3SAME")
    gr_1sig.Draw("LE3SAME")
  # Add legend
  if options.doBands: leg = ROOT.TLegend(0.58,0.46,0.86,0.76)
  else: leg = ROOT.TLegend(0.58,0.52,0.86,0.76)
  leg.SetFillStyle(0)
  leg.SetLineColor(0)
  leg.SetTextSize(0.045)
  leg.AddEntry(hD,"Data","ep")
  if options.unblind:
    leg.AddEntry(hSB['pdfNBins'],"S+B fit","l")
    leg.AddEntry(hB['pdfNBins'],"B component","l")
  else:
    leg.AddEntry(hB['pdfNBins'],"B fit","l")
    leg.AddEntry(hS['pdfNBins'],"S model","fl")
  if options.doBands:
    leg.AddEntry(gr_1sig,"#pm1 #sigma","F")
    leg.AddEntry(gr_2sig,"#pm2 #sigma","F")
  leg.Draw("Same")
  # Set pdf style
  if options.unblind:
    hSB['pdfNBins'].SetLineWidth(3)
    hSB['pdfNBins'].SetLineColor(2)
    hSB['pdfNBins'].Draw("Hist same c")
    hB['pdfNBins'].SetLineWidth(3)
    hB['pdfNBins'].SetLineColor(2)
    hB['pdfNBins'].SetLineStyle(2)
    hB['pdfNBins'].Draw("Hist same c")
  else:
    hS['pdfNBins'].SetLineWidth(3)
    hS['pdfNBins'].SetLineColor(9)
    hS['pdfNBins'].SetFillColor(38)
    hS['pdfNBins'].SetFillStyle(1001)
    hS['pdfNBins'].GetXaxis().SetRangeUser(blindingRegion[0],blindingRegion[1])
    hS['pdfNBins'].Draw("Hist same cf")
    hB['pdfNBins'].SetLineWidth(3)
    hB['pdfNBins'].SetLineColor(2)
    hB['pdfNBins'].Draw("Hist same c")
  # Set data style
  hD.SetMarkerStyle(20)
  hD.SetMarkerColor(1)
  hD.SetLineColor(1)
  hD.Draw("Same PE")
  # Add TLatex to plot
  lat0 = ROOT.TLatex()
  lat0.SetTextFont(42)
  lat0.SetTextAlign(11)
  lat0.SetNDC()
  lat0.SetTextSize(0.06)
  #lat0.DrawLatex(0.12,0.92,"#bf{CMS} #it{Preliminary}")
  #lat0.DrawLatex(0.12,0.92,"#bf{CMS}")
  lat0.DrawLatex(0.6,0.92,"137 fb^{-1} (13 TeV)")
  lat0.DrawLatex(0.6,0.8,"#scale[0.6]{%s}"%Translate(cat,translateCats))
  #lat0.DrawLatex(0.15,0.83,"#scale[0.75]{H#rightarrow#gamma#gamma}")
  lat0.DrawLatex(0.15,0.83,"#scale[0.75]{H #rightarrow #gamma#gamma, m_{H} = 125.38 GeV}")
  if(options.loadSnapshot is not None):
    #lat0.DrawLatex(0.15,0.77,"#scale[0.6]{#vec{#alpha} = STXS stage 1.2 minimal}")
    lat0.DrawLatex(0.15,0.77,"#scale[0.6]{#vec{#alpha} = (#mu_{ggH}, #mu_{VBF}, #mu_{VH}, #mu_{top})}")
    #lat0.DrawLatex(0.15,0.77,"#scale[0.5]{(#hat{#mu}_{ggH},#hat{#mu}_{VBF},#hat{#mu}_{VH},#hat{#mu}_{top}) = (1.07,1.04,1.34,1.35)}")
    #lat0.DrawLatex(0.15,0.77,"#scale[0.75]{#hat{#mu} = 1.03}")
    #muhat_ggh, muhat_vbf, muhat_vh, muhat_top, mhhat = workspace.var("r_ggH").getVal(), workspace.var("r_VBF").getVal(), workspace.var("r_VH").getVal(), workspace.var("r_top").getVal(), workspace.var("MH").getVal()
    #lat0.DrawLatex(0.13,0.77,"#scale[0.6]{(#hat{#mu}_{ggH},#hat{#mu}_{VBF},#hat{#mu}_{VH},#hat{#mu}_{top}) = (%.2f,%.2f,%.2f,%.2f)}"%(muhat_ggh,muhat_vbf,muhat_vh,muhat_top))
    #muhat, mhhat = workspace.var("r").getVal(), workspace.var("MH").getVal()
    #lat0.DrawLatex(0.13,0.77,"#scale[0.75]{#hat{m}_{H} = %.1f GeV, #hat{#mu} = %.2f}"%(mhhat,muhat))
  #elif options.parameterMap is not None:
  #  poiStr = ''
  #  for kv in options.parameterMap.split(","):
  #    [k,v] = kv.split(":")
  #    poiStr += ' %s = %.1f,'%(Translate(k,translatePOIs),float(v))
  #  poiStr = poiStr[:-1]
  #  lat0.DrawLatex(0.13,0.77,"#scale[0.75]{%s}"%poiStr)
  else: lat0.DrawLatex(0.15,0.77,"#scale[0.75]{#mu = 1.0}")
  # Ratio plot
  pad2.cd()
  h_axes_ratio = hDr.Clone()
  h_axes_ratio.Reset()
  h_axes_ratio.SetMaximum(max((hDr.GetMaximum()+hDr.GetBinError(hDr.GetMaximumBin()))*1.5,hSr.GetMaximum()*1.2))
  h_axes_ratio.SetMinimum((hDr.GetMinimum()-hDr.GetBinError(hDr.GetMinimumBin()))*1.3)
  h_axes_ratio.SetTitle("")
  h_axes_ratio.GetXaxis().SetTitleSize(0.05*padSizeRatio)
  h_axes_ratio.GetXaxis().SetLabelSize(0.035*padSizeRatio)
  h_axes_ratio.GetXaxis().SetLabelOffset(0.007)
  h_axes_ratio.GetXaxis().SetTickLength(0.03*padSizeRatio)
  h_axes_ratio.GetYaxis().SetLabelSize(0.035*padSizeRatio)
  h_axes_ratio.GetYaxis().SetLabelOffset(0.007)
  h_axes_ratio.GetYaxis().SetTitle("")
  h_axes_ratio.Draw()
  # Draw bands 
  if options.doBands:
    gr_2sig_r.Draw("LE3SAME")
    gr_1sig_r.Draw("LE3SAME")
  # Set pdf style
  if options.unblind:
    hSr.SetLineWidth(3)
    hSr.SetLineColor(2)
    hSr.Draw("Hist same c")
    hBr.SetLineWidth(3)
    hBr.SetLineStyle(2)
    hBr.SetLineColor(2)
    hBr.Draw("Hist same c")
  else:
    hSr.SetLineWidth(3)
    hSr.SetLineColor(9)
    hSr.SetFillColor(38)
    hSr.SetFillStyle(1001)
    hSr.GetXaxis().SetRangeUser(blindingRegion[0],blindingRegion[1])
    hSr.Draw("Hist same cf")
    hBr.SetLineWidth(3)
    hBr.SetLineColor(2)
    hBr.Draw("Hist same c")
  # Set data style
  hDr.SetMarkerStyle(20)
  hDr.SetMarkerColor(1)
  hDr.SetLineColor(1)
  hDr.Draw("Same PE")
  # Add TLatex to ratio plot
  lat1 = ROOT.TLatex()
  lat1.SetTextFont(42)
  lat1.SetTextAlign(33)
  lat1.SetNDC(1)
  lat1.SetTextSize(0.045*padSizeRatio)
  lat1.DrawLatex(0.87,0.91,"B component subtracted")

  # Save canvas
  canv.Update()
  canv.SaveAs("./SplusBModels%s/%s_%s.png"%(options.ext,cat,options.xvar.split(",")[0]))
  canv.SaveAs("./SplusBModels%s/%s_%s.pdf"%(options.ext,cat,options.xvar.split(",")[0]))
  #raw_input("Press any key to continue...")
