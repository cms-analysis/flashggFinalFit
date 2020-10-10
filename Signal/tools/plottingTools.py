# Functions for plotting 
import ROOT
from collections import OrderedDict as od

# Plot final pdf + data for each mass point
def plotModel(ssf,_outdir='./',_extension=''):
  canv = ROOT.TCanvas()
  LineColorMap = {'120':ROOT.kRed,'125':ROOT.kGreen+1,'130':ROOT.kAzure+1}
  MarkerColorMap = {'120':ROOT.kRed+3,'125':ROOT.kGreen+3,'130':ROOT.kAzure+3}
  pl = ssf.xvar.frame()
  for k, d in ssf.DataHists.iteritems():
    ssf.MH.setVal(int(k))
    ssf.Pdfs['final'].plotOn(pl,ROOT.RooFit.LineColor(LineColorMap[k]))
    d.plotOn(pl,ROOT.RooFit.MarkerColor(MarkerColorMap[k]))
  pl.Draw()
  canv.SaveAs("%s/%sshape_vs_mH_%s_%s.png"%(_outdir,_extension,ssf.proc,ssf.cat))
  canv.SaveAs("%s/%sshape_vs_mH_%s_%s.pdf"%(_outdir,_extension,ssf.proc,ssf.cat))

# Plot final pdf at MH = 125 (with data) + individual Pdf components
def plotPdfComponents(ssf,_outdir='./',_extension=''):
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
  lat.DrawLatex(0.9,0.92,"( %s , %s , %s )"%(ssf.name,ssf.proc,ssf.cat))
  lat1 = ROOT.TLatex()
  lat1.SetTextFont(42)
  lat1.SetTextAlign(11)
  lat1.SetNDC()
  lat1.SetTextSize(0.04)
  lat1.DrawLatex(0.65,0.3,"#chi^{2} = %.4f"%ssf.getChi2())

  canv.Update()
  canv.SaveAs("%s/%spdf_components_%s_%s.png"%(_outdir,_extension,ssf.proc,ssf.cat))
  canv.SaveAs("%s/%spdf_components_%s_%s.pdf"%(_outdir,_extension,ssf.proc,ssf.cat))
