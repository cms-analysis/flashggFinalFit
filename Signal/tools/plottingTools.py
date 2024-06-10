# Functions for plotting 
import ROOT
import json
from collections import OrderedDict as od
from commonObjects import *

def LoadTranslations(jsonfilename):
    with open(jsonfilename) as jsonfile:
        return json.load(jsonfile)
def Translate(name, ndict):
    return ndict[name] if name in ndict else name

# Function to extract the sigma effective of a histogram
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

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Ftest: plots
# Plot possible nGauss fits and chi2 values
def plotFTest(ssfs,_opt=1,_outdir='./',_extension='',_proc='',_cat='',_mass='125'):
  canv = ROOT.TCanvas()
  canv.SetLeftMargin(0.15)
  LineColorMap = {'1':ROOT.kAzure+1,'2':ROOT.kRed-4,'3':ROOT.kGreen+2,'4':ROOT.kMagenta-9,'5':ROOT.kOrange}
  pdfs = od()
  hists = od()
  hmax, hmin = 0, 0
  # Loop over nGauss fits
  for k,ssf in ssfs.items():
    ssf.MH.setVal(int(_mass))
    hists[k] = ssf.Pdfs['final'].createHistogram("h_%s_%s"%(k,_extension),ssf.xvar,ROOT.RooFit.Binning(1600))
    if int(k.split("_")[-1]) == _opt: hists[k].SetLineWidth(3)
    else: hists[k].SetLineWidth(1)
    hists[k].SetLineColor(LineColorMap[k.split("_")[-1]])
    hists[k].SetTitle("")
    hists[k].GetXaxis().SetTitle("m_{#gamma#gamma} [GeV]")
    hists[k].SetMinimum(0)
    if hists[k].GetMaximum()>hmax: hmax = hists[k].GetMaximum()
    if hists[k].GetMinimum()<hmin: hmin = hists[k].GetMinimum()
    hists[k].GetXaxis().SetRangeUser(115,140)
  # Extract data histogram
  hists['data'] = ssf.xvar.createHistogram("h_data%s"%_extension,ROOT.RooFit.Binning(ssf.nBins))
  ssf.DataHists[_mass].fillHistogram(hists['data'],ROOT.RooArgList(ssf.xvar))
  hists['data'].Scale(float(ssf.nBins)/1600)
  hists['data'].SetMarkerStyle(20)
  hists['data'].SetMarkerColor(1)
  hists['data'].SetLineColor(1)
  hists['data'].SetTitle("")
  hists['data'].GetXaxis().SetTitle("m_{#gamma#gamma} [GeV]")
  hists['data'].SetMinimum(0)
  hists['data'].GetXaxis().SetRangeUser(115,140)
  if hists['data'].GetMaximum()>hmax: hmax = hists['data'].GetMaximum()
  if hists['data'].GetMinimum()<hmin: hmin = hists['data'].GetMinimum()

  # Loop over histograms and plot
  hists['data'].SetMaximum(1.2*hmax)
  hists['data'].SetMinimum(1.2*hmin)
  hists['data'].Draw("PE")
  for k,h in hists.items():
    if k == "data": continue
    h.Draw("HIST SAME")

  # Legend & Text
  leg = ROOT.TLegend(0.55,0.3,0.86,0.8)
  leg.SetFillStyle(0)
  leg.SetLineColor(0)
  leg.SetTextSize(0.03)
  leg.AddEntry(hists['data'],"Simulation","ep")
  for k,ssf in ssfs.items(): 
    if int(k.split("_")[-1]) == _opt: leg.AddEntry(hists[k],"#bf{N_{gauss} = %s}: #chi^{2}/n(dof) = %.4f"%(k.split("_")[-1],ssf.getReducedChi2()),"L")
    else: leg.AddEntry(hists[k],"N_{gauss} = %s: #chi^{2}/n(dof) = %.4f"%(k.split("_")[-1],ssf.getReducedChi2()),"L")
  leg.Draw("Same")
  # Add Latex
  lat = ROOT.TLatex()
  lat.SetTextFont(42)
  lat.SetTextAlign(31)
  lat.SetNDC()
  lat.SetTextSize(0.03)
  lat.DrawLatex(0.9,0.92,"( %s , %s , %s )"%(_extension,_proc,_cat))

  canv.Update()
  canv.SaveAs("%s/fTest_%s_%s_%s.png"%(_outdir,_cat,_proc,_extension))
  canv.SaveAs("%s/fTest_%s_%s_%s.pdf"%(_outdir,_cat,_proc,_extension))

# Plot reduced chi2 vs nGauss
def plotFTestResults(ssfs,_opt,_outdir="./",_extension='',_proc='',_cat='',_mass='125'):
  canv = ROOT.TCanvas()
  gr = ROOT.TGraph()
  # Loop over nGuassians
  p = 0
  xmax = 1
  ymax = -1
  for k,ssf in ssfs.items():
    ssf.MH.setVal(int(_mass))
    x = int(k.split("_")[-1])
    if x > xmax: xmax = x
    y = ssf.getReducedChi2()
    if y > ymax: ymax = y
    gr.SetPoint(p,x,y)
    p += 1

  # Draw axes
  haxes = ROOT.TH1F("h_axes_%s_%s"%(_proc,_extension),"h_axes_%s_%s"%(_proc,_extension),xmax+1,0,xmax+1)
  haxes.SetTitle("")
  haxes.GetXaxis().SetTitle("N_{gauss}")
  haxes.GetXaxis().SetTitleSize(0.05)
  haxes.GetXaxis().SetTitleOffset(0.85)
  haxes.GetXaxis().SetLabelSize(0.035)
  haxes.GetYaxis().SetTitle("#chi^{2} / n(dof)")
  haxes.GetYaxis().SetTitleOffset(0.85)
  haxes.GetYaxis().SetTitleSize(0.05)
  haxes.SetMaximum(1.2*ymax)
  haxes.SetMinimum(0)
  haxes.Draw()
  # Draw graph
  if "RV" in _extension: gr.SetLineColor(ROOT.kRed-4)
  elif "WV" in _extension: gr.SetLineColor(ROOT.kAzure+1)
  else: gr.SetLineColor(1)
  gr.SetMarkerColor(1)
  gr.SetMarkerStyle(20)
  gr.Draw("Same PL")
  # Add Latex
  lat = ROOT.TLatex()
  lat.SetTextFont(42)
  lat.SetTextAlign(31)
  lat.SetNDC()
  lat.SetTextSize(0.03)
  lat.DrawLatex(0.9,0.92,"( %s , %s , %s )"%(_extension,_proc,_cat))
  lat.DrawLatex(0.6,0.75,"Optimum N_{gauss} = %s"%_opt)
  canv.Update()
  canv.SaveAs("%s/fTest_%s_%s_%s_chi2_vs_nGauss.png"%(_outdir,_cat,_proc,_extension))
  canv.SaveAs("%s/fTest_%s_%s_%s_chi2_vs_nGauss.pdf"%(_outdir,_cat,_proc,_extension))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Signal fit plots
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
  #hists['final'].GetXaxis().SetRangeUser(115,140)
  hists['final'].GetXaxis().SetRangeUser(100,150)
  # Create data histogram
  hists['data'] = ssf.xvar.createHistogram("h_data%s"%_extension,ROOT.RooFit.Binning(ssf.nBins))
  ssf.DataHists['125'].fillHistogram(hists['data'],ROOT.RooArgList(ssf.xvar))
  hists['data'].SetTitle("")
  hists['data'].GetXaxis().SetTitle("m_{#gamma#gamma} [GeV]")
  hists['data'].SetMinimum(0)
  #hists['data'].GetXaxis().SetRangeUser(115,140)
  hists['data'].GetXaxis().SetRangeUser(100,150)
  hists['data'].Scale(float(ssf.nBins)/1600)
  hists['data'].SetMarkerStyle(20)
  hists['data'].SetMarkerColor(1)
  hists['data'].SetLineColor(1)
  if hists['data'].GetMaximum()>hmax: hmax = hists['data'].GetMaximum()
  if hists['data'].GetMinimum()<hmin: hmin = hists['data'].GetMinimum()
  # Draw histograms
  hists['data'].SetMaximum(1.2*hmax)
  hists['data'].SetMinimum(1.2*hmin)
  hists['data'].Draw("PE")
  hists['final'].Draw("Same HIST")
  # Individual Gaussian histograms
  for k,v in ssf.Pdfs.items():
    if k == 'final': continue
    pdfs[k] = v
  if len(pdfs.keys())!=1:
    pdfItr = 0
    for k,v in pdfs.items():
      if pdfItr == 0:
        if "gaus" in k: frac = ssf.Pdfs['final'].getComponents().getRealValue("frac_g0_constrained")
        else: frac = ssf.Pdfs['final'].getComponents().getRealValue("frac_constrained")
      else:
        frac = ssf.Pdfs['final'].getComponents().getRealValue("%s_%s_recursive_fraction_%s_%s"%(ssf.proc,ssf.cat,k,pdfItr+1))
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
    for k,v in pdfs.items(): leg1.AddEntry(hists[k],k,"L")
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

# Plot final pdf for each mass point
def plotInterpolation(_finalModel,_outdir='./',_massPoints='120,121,122,123,124,125,126,127,128,129,130'):

  canv = ROOT.TCanvas()
  colors = [ROOT.kRed,ROOT.kCyan,ROOT.kBlue+1,ROOT.kOrange-3,ROOT.kMagenta-7,ROOT.kGreen+1,ROOT.kYellow-7,ROOT.kViolet+6,ROOT.kTeal+1,ROOT.kPink+1,ROOT.kAzure+1]
  colorMap = {}
  for i, mp in enumerate(_massPoints.split(",")): colorMap[mp] = colors[i]
  # Set luminosity
  _finalModel.intLumi.setVal(lumiScaleFactor*float(lumiMap[_finalModel.year]))
  # Total pdf histograms
  dh = od()
  hists = od()
  hmax = 0.0001 
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
  haxes = hists[list(hists.keys())[0]].Clone()
  haxes.GetXaxis().SetTitle("m_{#gamma#gamma} [GeV]")
  haxes.GetYaxis().SetTitle("Events / %.2f GeV"%((_finalModel.xvar.getMax()-_finalModel.xvar.getMin())/_finalModel.xvar.getBins()))
  haxes.SetMinimum(0)
  haxes.SetMaximum(hmax*1.2)
  haxes.GetXaxis().SetRangeUser(100,150)
  haxes.Draw("AXIS")

  # Draw rest of histograms
  for k,h in hists.items(): 
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
  _finalModel.intLumi.setVal(lumiScaleFactor*float(lumiMap[_finalModel.year]))
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
  for x, gr in grs.items(): 
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

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Function for plotting final signal model: neat
def plotSignalModel(_hists,_opt,_outdir=".",offset=0.02):
  colorMap = {'2016':38,'2017':30,'2018':46,'2022preEE':38,'2022postEE':30}
  canv = ROOT.TCanvas("c","c",650,600)
  canv.SetBottomMargin(0.12)
  canv.SetLeftMargin(0.15)
  canv.SetTickx()
  canv.SetTicky()
  h_axes = _hists['data'].Clone()
  h_axes.Reset()
  h_axes.SetMaximum(_hists['data'].GetMaximum()*1.2)
  h_axes.SetMinimum(0.)
  h_axes.GetXaxis().SetRangeUser(105,140)
  h_axes.SetTitle("")
  h_axes.GetXaxis().SetTitle("%s (%s)"%(_opt.xvar.split(":")[1],_opt.xvar.split(":")[2]))
  h_axes.GetXaxis().SetTitleSize(0.05)
  h_axes.GetXaxis().SetTitleOffset(1.)
  h_axes.GetYaxis().SetTitleSize(0.05)
  h_axes.GetYaxis().SetTitleOffset(1.2)
  h_axes.Draw()
    
  # Extract effSigma
  effSigma = getEffSigma(_hists['pdf'])
  effSigma_low, effSigma_high = _hists['pdf'].GetMean()-effSigma, _hists['pdf'].GetMean()+effSigma
  h_effSigma = _hists['pdf'].Clone()
  h_effSigma.GetXaxis().SetRangeUser(effSigma_low,effSigma_high)

  # Legend
  if len(_opt.years.split(","))>1:
    leg0 = ROOT.TLegend(0.15+offset,0.6,0.5+offset,0.82)
    leg0.SetFillStyle(0)
    leg0.SetLineColor(0)
    leg0.SetTextSize(0.03)
    leg0.AddEntry(_hists['data'],"Simulation","ep")
    leg0.AddEntry(_hists['pdf'],"#splitline{Parametric}{model}","l")
    leg0.Draw("Same")

    leg1 = ROOT.TLegend(0.17+offset,0.45,0.4+offset,0.61)
    leg1.SetFillStyle(0)
    leg1.SetLineColor(0)
    leg1.SetTextSize(0.03)
    for year in _opt.years.split(","): leg1.AddEntry(_hists['pdf_%s'%year],"%s: #scale[0.8]{#sigma_{eff} = %1.2f GeV}"%(year,getEffSigma(_hists['pdf_%s'%year])),"l")
    leg1.Draw("Same")

    leg2 = ROOT.TLegend(0.15+offset,0.3,0.5+offset,0.45)
    leg2.SetFillStyle(0)
    leg2.SetLineColor(0)
    leg2.SetTextSize(0.03)
    leg2.AddEntry(h_effSigma,"#sigma_{eff} = %1.2f GeV"%(0.5*(effSigma_high-effSigma_low)),"fl")
    leg2.Draw("Same")
  else:
    year = _opt.years
    leg = ROOT.TLegend(0.15+offset,0.4,0.5+offset,0.82)
    leg.SetFillStyle(0)
    leg.SetLineColor(0)
    leg.SetTextSize(0.03)
    leg.AddEntry(_hists['data'],"Simulation","lep")
    leg.AddEntry(_hists['pdf'],"#splitline{Parametric}{model (%s)}"%year,"l")
    leg.AddEntry(h_effSigma,"#sigma_{eff} = %1.2f GeV"%(0.5*(effSigma_high-effSigma_low)),"fl")
    leg.Draw("Same")    

  # Set style effSigma
  h_effSigma.SetLineColor(15)
  h_effSigma.SetFillStyle(1001)
  h_effSigma.SetFillColor(19)
  h_effSigma.Draw("Same Hist F")
  vline_effSigma_low = ROOT.TLine(effSigma_low,0,effSigma_low,_hists['pdf'].GetBinContent(_hists['pdf'].FindBin(effSigma_low)))
  vline_effSigma_high = ROOT.TLine(effSigma_high,0,effSigma_high,_hists['pdf'].GetBinContent(_hists['pdf'].FindBin(effSigma_high)))
  vline_effSigma_low.SetLineColor(15)
  vline_effSigma_high.SetLineColor(15)
  vline_effSigma_low.SetLineWidth(2)
  vline_effSigma_high.SetLineWidth(2)
  vline_effSigma_low.Draw("Same")
  vline_effSigma_high.Draw("Same")

  # Extract FWHM and set style
  if _opt.doFWHM:
    fwhm_low = _hists['pdf'].GetBinCenter(_hists['pdf'].FindFirstBinAbove(0.5*_hists['pdf'].GetMaximum()))
    fwhm_high = _hists['pdf'].GetBinCenter(_hists['pdf'].FindLastBinAbove(0.5*_hists['pdf'].GetMaximum()))
    fwhmArrow = ROOT.TArrow(fwhm_low,0.5*_hists['pdf'].GetMaximum(),fwhm_high,0.5*_hists['pdf'].GetMaximum(),0.02,"<>")
    fwhmArrow.SetLineWidth(2)
    fwhmArrow.Draw("Same <>")
    fwhmText = ROOT.TLatex()
    fwhmText.SetTextFont(42)
    fwhmText.SetTextAlign(11)
    fwhmText.SetNDC()
    fwhmText.SetTextSize(0.03)
    fwhmText.DrawLatex(0.17+offset,0.25,"FWHM = %1.2f GeV"%(fwhm_high-fwhm_low))

  # Set style pdf
  _hists['pdf'].SetLineColor(4)
  _hists['pdf'].SetLineWidth(2)
  _hists['pdf'].Draw("Same Hist C")
  if len(_opt.years.split(","))>1:
    for year in _opt.years.split(","):
      _hists['pdf_%s'%year].SetLineColor( colorMap[year] )  
      _hists['pdf_%s'%year].SetLineStyle(2)
      _hists['pdf_%s'%year].SetLineWidth(2)
      _hists['pdf_%s'%year].Draw("Same Hist C")
  # Set style: data
  _hists['data'].SetMarkerStyle(25)
  _hists['data'].SetMarkerColor(1)
  _hists['data'].SetLineColor(1)
  _hists['data'].SetLineWidth(2)
  _hists['data'].Draw("Same PE")
  
  # Add TLatex to plot
  lat0 = ROOT.TLatex()
  lat0.SetTextFont(42)
  lat0.SetTextAlign(11)
  lat0.SetNDC()
  lat0.SetTextSize(0.045)
  lat0.DrawLatex(0.15,0.92,"#bf{CMS} #it{%s}"%_opt.label)
  lat0.DrawLatex(0.77,0.92,"%s TeV"%(sqrts__.split("TeV")[0]))
  lat0.DrawLatex(0.16+offset,0.83,"H #rightarrow #gamma#gamma")

  # Load translations
  translateCats = {} if _opt.translateCats is None else LoadTranslations(_opt.translateCats)
  translateProcs = {} if _opt.translateProcs is None else LoadTranslations(_opt.translateProcs)

  lat1 = ROOT.TLatex()
  lat1.SetTextFont(42)
  lat1.SetTextAlign(33)
  lat1.SetNDC(1)
  lat1.SetTextSize(0.035)
  if _opt.procs == 'all': procStr, procExt = "", ""
  elif len(_opt.procs.split(","))>1: procStr, procExt = "Multiple processes", "_multipleProcs"
  else: procStr, procExt = Translate(_opt.procs,translateProcs), "_%s"%_opt.procs
 
  if len(_opt.years.split(","))>1: yearStr, yearExt = "", ""
  else: yearStr, yearExt = _opt.years, "_%s"%_opt.years

  if _opt.cats == 'all': catStr, catExt = "All categories", "all"
  elif _opt.cats == 'wall': catStr, catExt = "#splitline{All categories}{S/(S+B) weighted}", "wall"
  elif len(_opt.cats.split(","))>1: procStr, procExt = "Multiple categories", "multipleCats"
  else: catStr, catExt = Translate(_opt.cats,translateCats), _opt.cats
 
  lat1.DrawLatex(0.85,0.86,"%s"%catStr)
  lat1.DrawLatex(0.83,0.8,"%s %s"%(procStr,yearStr))

  canv.Update()

  # Write effSigma to file
  if len(_opt.years.split(",")) >1:
    es = {}
    es['combined'] = effSigma
    for year in _opt.years.split(","): es[year] = getEffSigma(_hists['pdf_%s'%year])
    with open("%s/effSigma_%s.json"%(_outdir,catExt),"w") as jf: json.dump(es,jf)

  # Save canvas
  canv.SaveAs("%s/smodel_%s%s%s.pdf"%(_outdir,catExt,procExt,yearExt))
  canv.SaveAs("%s/smodel_%s%s%s.png"%(_outdir,catExt,procExt,yearExt))
