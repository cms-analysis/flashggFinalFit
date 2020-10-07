# Class for performing simultaneous signal fit
import ROOT
import numpy as np
from scipy.optimize import minimize
from collections import OrderedDict as od

# Parameter lookup table for initialisation
# So far defined up to MHPolyOrder=2
pLUT = od()
pLUT['DCB'] = od()
pLUT['DCB']['dm_p0'] = [0.1,-5.,5.]
pLUT['DCB']['dm_p1'] = [0.0,-0.1,0.1]
pLUT['DCB']['dm_p2'] = [0.0,-0.001,0.001]
pLUT['DCB']['sigma_p0'] = [2.,1.,20.]
pLUT['DCB']['sigma_p1'] = [0.0,-0.1,0.1]
pLUT['DCB']['sigma_p2'] = [0.0,-0.001,0.001]
pLUT['DCB']['n1_p0'] = [20.,2.00001,500]
pLUT['DCB']['n1_p1'] = [0.0,-0.1,0.1]
pLUT['DCB']['n1_p2'] = [0.0,-0.001,0.001]
pLUT['DCB']['n2_p0'] = [20.,2.00001,500]
pLUT['DCB']['n2_p1'] = [0.0,-0.1,0.1]
pLUT['DCB']['n2_p2'] = [0.0,-0.001,0.001]
pLUT['DCB']['a1_p0'] = [5.,1.,20.]
pLUT['DCB']['a1_p1'] = [0.0,-0.1,0.1]
pLUT['DCB']['a1_p2'] = [0.0,-0.001,0.001]
pLUT['DCB']['a2_p0'] = [5.,1.,20.]
pLUT['DCB']['a2_p1'] = [0.0,-0.1,0.1]
pLUT['DCB']['a2_p2'] = [0.0,-0.001,0.001]
pLUT['Gaussian_wdcb'] = od()
pLUT['Gaussian_wdcb']['dm_p0'] = [0.1,-5.,5.]
pLUT['Gaussian_wdcb']['dm_p1'] = [0.01,-0.01,0.01]
pLUT['Gaussian_wdcb']['dm_p2'] = [0.01,-0.01,0.01]
pLUT['Gaussian_wdcb']['sigma_p0'] = [2.,1.,3.]
pLUT['Gaussian_wdcb']['sigma_p1'] = [0.0,-0.1,0.1]
pLUT['Gaussian_wdcb']['sigma_p2'] = [0.0,-0.001,0.001]
pLUT['Frac'] = od()
pLUT['Frac']['p0'] = [0.5,0.01,0.99]
pLUT['Frac']['p1'] = [0.,-0.05,0.05]
pLUT['Frac']['p2'] = [0.,-0.0001,0.0001]
pLUT['Gaussian'] = od()
pLUT['Gaussian']['dm_p0'] = [0.1,-5.,5.]
pLUT['Gaussian']['dm_p1'] = [0.01,-0.01,0.01]
pLUT['Gaussian']['dm_p2'] = [0.01,-0.01,0.01]
pLUT['Gaussian']['sigma_p0'] = ['func',0.5,10.0]
pLUT['Gaussian']['sigma_p1'] = [0.01,-0.01,0.01]
pLUT['Gaussian']['sigma_p2'] = [0.01,-0.01,0.01]
pLUT['FracGaussian'] = od()
pLUT['FracGaussian']['p0'] = ['func',0.01,0.99]
pLUT['FracGaussian']['p1'] = [0.01,-0.005,0.005]
pLUT['FracGaussian']['p2'] = [0.00001,-0.00001,0.00001]

# Function to add chi2 for multiple mass points
def nChi2Addition(X,ssf):
  # X: vector of param values (updated with minimise function)
  # Loop over parameters and set RooVars
  for i in range(len(X)): ssf.Chi2Vars[i].setVal(X[i])
  # Loop over chi2map: adding chi2 for each mass point
  chi2sum = 0
  for mp,chi2 in ssf.Chi2Map.iteritems():
    ssf.MH.setVal(int(mp))
    chi2sum += chi2.getVal()
  return chi2sum 


class SimultaneousFit:
  def __init__(self,_proc,_cat,_datasetForFit,_xvar,_MH,_MHLow,_MHHigh,_massPoints,_nBins,_MHPolyOrder,_minimizerMethod,_minimizerTolerance,_outdir,_doPlots=False):
    self.proc = _proc
    self.cat = _cat
    self.datasetForFit = _datasetForFit
    self.normDatahistForFit = od()
    self.xvar = _xvar
    self.MH = _MH
    self.MHLow = _MHLow
    self.MHHigh = _MHHigh
    self.massPoints = _massPoints
    self.nBins = _nBins
    self.MHPolyOrder = _MHPolyOrder
    self.minimizerMethod = _minimizerMethod
    self.minimizerTolerance = _minimizerTolerance
    self.outdir = _outdir
    self.doPlots = _doPlots
    self.verbose = True
    # Prepare vars
    self.MH.setConstant(False)
    self.MH.setVal(125)
    self.MH.setBins(10)
    self.xvar.setVal(125)
    self.xvar.setBins(self.nBins)
    # Dicts to store all fit vars, polynomials, pdfs and DataHists
    self.Vars = od()
    self.Varlists = od()
    self.Polynomials = od()
    self.Pdfs = od()
    self.Coeffs = od()
    self.DataHists = od()
    self.Chi2Map = od()
    self.Chi2Vars = None
    self.Chi2 = None
    self.FitResult = None
    self.dMH = ROOT.RooFormulaVar("dMH","dMH","@0-125.0",ROOT.RooArgList(self.MH)) 

    # Prepare normalised DataHists
    self.prepareDataHists()

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   
  # Function to extract param bounds
  def extractXBounds(self):
    XBounds = []
    for i in range(len(self.Chi2Vars)): XBounds.append((self.Chi2Vars[i].getMin(),self.Chi2Vars[i].getMax()))
    return np.asarray(XBounds)

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   
  # Function to extract initial param value vector
  def extractX0(self):
    X0 = []
    for i in range(len(self.Chi2Vars)): X0.append(self.Chi2Vars[i].getVal())
    return np.asarray(X0)

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   
  # Function to normalise datasets and convert to RooDataHists for calc chi2
  def prepareDataHists(self):
    # Loop over datasets and normalise to 1
    for k,d in self.datasetForFit.iteritems():
      sumw = d.sumEntries()
      drw = d.emptyClone()
      self.Vars['weight'] = ROOT.RooRealVar("weight","weight",-10000,10000)
      for i in range(0,d.numEntries()):
        self.xvar.setVal(d.get(i).getRealValue(self.xvar.GetName()))
        self.Vars['weight'].setVal((1/sumw)*d.weight())
        drw.add(ROOT.RooArgSet(self.xvar,self.Vars['weight']),self.Vars['weight'].getVal())
      # Convert to RooDataHist
      self.DataHists[k] = ROOT.RooDataHist("%s_hist"%d.GetName(),"%s_hist"%d.GetName(),ROOT.RooArgSet(self.xvar),drw)
  
  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   
  def buildDCBplusGaussian(self,_recursive=True):

    # DCB
    # Define polynominal functions (in dMH)
    for f in ['dm','sigma','n1','n2','a1','a2']: 
      k = "%s_dcb"%f
      self.Varlists[k] = ROOT.RooArgList("%s_coeffs"%k)
      # Create coeff for polynominal of order MHPolyOrder: y = a+bx+cx^2+...
      for po in range(0,self.MHPolyOrder+1):
        self.Vars['%s_p%g'%(k,po)] = ROOT.RooRealVar("%s_p%g"%(k,po),"%s_p%g"%(k,po),pLUT['DCB']["%s_p%s"%(f,po)][0],pLUT['DCB']["%s_p%s"%(f,po)][1],pLUT['DCB']["%s_p%s"%(f,po)][2])
	self.Varlists[k].add( self.Vars['%s_p%g'%(k,po)] ) 
      # Define polynominal
      self.Polynomials[k] = ROOT.RooPolyVar(k,k,self.dMH,self.Varlists[k])
    # Mean function
    self.Polynomials['mean_dcb'] = ROOT.RooFormulaVar("mean_dcb","mean_dcb","(@0+@1)",ROOT.RooArgList(self.MH,self.Polynomials['dm_dcb']))
    # Build DCB
    self.Pdfs['dcb'] = ROOT.RooDoubleCBFast("dcb","dcb",self.xvar,self.Polynomials['mean_dcb'],self.Polynomials['sigma_dcb'],self.Polynomials['a1_dcb'],self.Polynomials['n1_dcb'],self.Polynomials['a2_dcb'],self.Polynomials['n2_dcb'])

    # Gaussian
    # Define polynomial function for sigma (in dMH). Gaussian defined to have same mean as DCB
    f = "sigma"
    k = "%s_gaus"%f
    self.Varlists[k] = ROOT.RooArgList("%s_coeffs"%k)    
    # Create coeff for polynominal of order MHPolyOrder: y = a+bx+cx^2+...
    for po in range(0,self.MHPolyOrder+1):
      self.Vars['%s_p%g'%(k,po)] = ROOT.RooRealVar("%s_p%g"%(k,po),"%s_p%g"%(k,po),pLUT['Gaussian_wdcb']["%s_p%s"%(f,po)][0],pLUT['Gaussian_wdcb']["%s_p%s"%(f,po)][1],pLUT['Gaussian_wdcb']["%s_p%s"%(f,po)][2])
      self.Varlists[k].add( self.Vars['%s_p%g'%(k,po)] )
    # Define polynomial
    self.Polynomials[k] = ROOT.RooPolyVar(k,k,self.dMH,self.Varlists[k])
    # Build Gaussian
    self.Pdfs['gaus'] = ROOT.RooGaussian("gaus","gaus",self.xvar,self.Polynomials['mean_dcb'],self.Polynomials['sigma_gaus'])
        
    # Relative fraction: also polynomial of order MHPolyOrder
    self.Varlists['frac'] = ROOT.RooArgList("frac_coeffs")
    for po in range(0,self.MHPolyOrder+1):
      self.Vars['frac_p%g'%po] = ROOT.RooRealVar("frac_p%g"%po,"frac_p%g"%po,pLUT['Frac']['p%g'%po][0],pLUT['Frac']['p%g'%po][1],pLUT['Frac']['p%g'%po][2])
      self.Varlists['frac'].add( self.Vars['frac_p%g'%po] )
    # Define Polynomial
    self.Polynomials['frac'] = ROOT.RooPolyVar('frac','frac',self.dMH,self.Varlists['frac'])
    # Constrain fraction to not be above 1 or below 0
    self.Polynomials['frac_constrained'] = ROOT.RooFormulaVar("frac_constrained","frac_constrained","(@0>0)*(@0<1)*@0+(@0>1.0)*0.9999",ROOT.RooArgList(self.Polynomials['frac']))
    self.Coeffs['frac_constrained'] = self.Polynomials['frac_constrained' ]

    # Define total PDF
    _pdfs, _coeffs = ROOT.RooArgList(), ROOT.RooArgList()
    for pdf in ['dcb','gaus']: _pdfs.add(self.Pdfs[pdf])
    _coeffs.add(self.Coeffs['frac_constrained'])
    self.Pdfs['final'] = ROOT.RooAddPdf("%s_%s"%(self.proc,self.cat),"%s_%s"%(self.proc,self.cat),_pdfs,_coeffs,_recursive)
    
  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   
  def buildNGaussians(self,nGaussians,_recursive=True):

    # Loop over NGaussians
    for g in range(0,nGaussians):
      # Define polynominal functions for mean and sigma (in MH)
      for f in ['dm','sigma']: 
	k = "%s_g%g"%(f,g)
	self.Varlists[k] = ROOT.RooArgList("%s_coeffs"%k)
	# Create coeff for polynominal of order MHPolyOrder: y = a+bx+cx^2+...
	for po in range(0,self.MHPolyOrder+1):
          # p0 value of sigma is function of g (creates gaussians of increasing width)
          if(f == "sigma")&(po==0): 
            self.Vars['%s_p%g'%(k,po)] = ROOT.RooRealVar("%s_p%g"%(k,po),"%s_p%g"%(k,po),(g+1)*1.0,pLUT['Gaussian']["%s_p%s"%(f,po)][1],pLUT['Gaussian']["%s_p%s"%(f,po)][2])
	  else:
            self.Vars['%s_p%g'%(k,po)] = ROOT.RooRealVar("%s_p%g"%(k,po),"%s_p%g"%(k,po),pLUT['Gaussian']["%s_p%s"%(f,po)][0],pLUT['Gaussian']["%s_p%s"%(f,po)][1],pLUT['Gaussian']["%s_p%s"%(f,po)][2])
	  self.Varlists[k].add( self.Vars['%s_p%g'%(k,po)] ) 
	# Define polynominal
	self.Polynomials[k] = ROOT.RooPolyVar(k,k,self.dMH,self.Varlists[k])
      # Mean function
      self.Polynomials['mean_g%g'%g] = ROOT.RooFormulaVar("mean_g%g"%g,"mean_g%g"%g,"(@0+@1)",ROOT.RooArgList(self.MH,self.Polynomials['dm_g%g'%g]))
      # Build Gaussian
      self.Pdfs['gaus_g%g'%g] = ROOT.RooGaussian("gaus_g%g"%g,"gaus_g%g"%g,self.xvar,self.Polynomials['mean_g%g'%g],self.Polynomials['sigma_g%g'%g])

      # Relative fractions: also polynomials of order MHPolyOrder (define up to n=nGaussians-1)
      if g < nGaussians-1:
	self.Varlists['frac_g%g'%g] = ROOT.RooArgList("frac_g%g_coeffs"%g)
	for po in range(0,self.MHPolyOrder+1):
	  if po == 0:
	    self.Vars['frac_g%g_p%g'%(g,po)] = ROOT.RooRealVar("frac_g%g_p%g"%(g,po),"frac_g%g_p%g"%(g,po),0.5-0.05*g,pLUT['FracGaussian']['p%g'%po][1],pLUT['FracGaussian']['p%g'%po][2])
	  else:
	    self.Vars['frac_g%g_p%g'%(g,po)] = ROOT.RooRealVar("frac_g%g_p%g"%(g,po),"frac_g%g_p%g"%(g,po),pLUT['FracGaussian']['p%g'%po][0],pLUT['FracGaussian']['p%g'%po][1],pLUT['FracGaussian']['p%g'%po][2])
	  self.Varlists['frac_g%g'%g].add( self.Vars['frac_g%g_p%g'%(g,po)] )
	# Define Polynomial
	self.Polynomials['frac_g%g'%g] = ROOT.RooPolyVar("frac_g%g"%g,"frac_g%g"%g,self.dMH,self.Varlists['frac_g%g'%g])
	# Constrain fraction to not be above 1 or below 0
	self.Polynomials['frac_g%g_constrained'%g] = ROOT.RooFormulaVar('frac_g%g_constrained'%g,'frac_g%g_constrained'%g,"(@0>0)*(@0<1)*@0+ (@0>1.0)*0.9999",ROOT.RooArgList(self.Polynomials['frac_g%g'%g]))
	self.Coeffs['frac_g%g_constrained'%g] = self.Polynomials['frac_g%g_constrained'%g]
    # End of loop over n Gaussians
    
    # Define total PDF
    _pdfs, _coeffs = ROOT.RooArgList(), ROOT.RooArgList()
    for g in range(0,nGaussians): 
      _pdfs.add(self.Pdfs['gaus_g%g'%g])
      if g < nGaussians-1: _coeffs.add(self.Coeffs['frac_g%g_constrained'%g])
    self.Pdfs['final'] = ROOT.RooAddPdf("%s_%s"%(self.proc,self.cat),"%s_%s"%(self.proc,self.cat),_pdfs,_coeffs,_recursive)
    

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   
  def runFit(self):
    # Create chi2 map: RooChi2Var for each mass point
    for k, d in self.DataHists.iteritems(): 
      self.Chi2Map[k] = ROOT.RooChi2Var("chi2_%s"%k,"chi2_%s"%k,self.Pdfs['final'],d,ROOT.RooFit.DataError(ROOT.RooAbsData.Poisson))
      # Add vars
      if self.Chi2Vars is None:
        self.Chi2Vars = ROOT.RooArgList()
        self.Chi2Vars.add(self.Chi2Map[k].getVariables())
    
    # Create initial vector of parameters and calculate initial Chi2
    x0 = self.extractX0()
    xbounds = self.extractXBounds()
    self.Chi2 = nChi2Addition(x0,self)
    # Print parameter pre-fit values
    if self.verbose:
      print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
      print " -> Pre-fit parameter values:" # Skip MH
      for i in range(1,len(self.Chi2Vars)): print "    * %-20s = %.6f"%(self.Chi2Vars[i].GetName(),self.Chi2Vars[i].getVal())
      print "    ~~~~~~~~~~~~~~~~"
      print "    * chi2 = %.6f"%self.Chi2
      print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
 
    # Run fit
    self.FitResult = minimize(nChi2Addition,x0,args=self,bounds=xbounds,method=self.minimizerMethod)
    self.Chi2 = nChi2Addition(self.FitResult['x'],self)
    # Print parameter pre-fit values
    if self.verbose:
      print "\n ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
      print " -> Post-fit parameter values:" # Skip MH
      for i in range(1,len(self.Chi2Vars)): print "    * %-20s = %.6f"%(self.Chi2Vars[i].GetName(),self.Chi2Vars[i].getVal())
      print "    ~~~~~~~~~~~~~~~~"
      print "    * chi2 = %.6f"%self.Chi2
      print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

    # Clean up
    for k, chi2 in self.Chi2Map.iteritems(): chi2.Delete() 

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   
  def plotModel(self):
    LineColorMap = {'120':ROOT.kRed,'125':ROOT.kGreen+1,'130':ROOT.kAzure+1}
    MarkerColorMap = {'120':ROOT.kRed+3,'125':ROOT.kGreen+3,'130':ROOT.kAzure+3}
    pl = self.xvar.frame()
    for k, d in self.DataHists.iteritems():
      self.MH.setVal(int(k))
      self.Pdfs['final'].plotOn(pl,ROOT.RooFit.LineColor(LineColorMap[k]))
      d.plotOn(pl,ROOT.RooFit.MarkerColor(MarkerColorMap[k]))
    pl.Draw()

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   
  def plotPdfs(self):
    canv = ROOT.TCanvas("canv","canv",800,600)
    canv.SetLeftMargin(0.15)
    self.MH.setVal(125)
    LineColorMap = {0:ROOT.kAzure+1,1:ROOT.kRed-4,2:ROOT.kOrange,3:ROOT.kGreen+2,4:ROOT.kMagenta-9}
    pdfs = od()
    hists = od()
    hmax, hmin = 0, 0
    # Total pdf histogram
    hists['final'] = self.Pdfs['final'].createHistogram("h_final",self.xvar,ROOT.RooFit.Binning(1600))
    hists['final'].SetLineWidth(2)
    hists['final'].SetLineColor(1)
    hists['final'].SetTitle("")
    hists['final'].GetXaxis().SetTitle("m_{#gamma#gamma} [GeV]")
    hists['final'].SetMinimum(0)
    if hists['final'].GetMaximum()>hmax: hmax = hists['final'].GetMaximum()
    if hists['final'].GetMinimum()<hmin: hmin = hists['final'].GetMinimum()
    # Create data histogram
    hists['data'] = self.xvar.createHistogram("h_data",ROOT.RooFit.Binning(self.nBins))
    self.DataHists['125'].fillHistogram(hists['data'],ROOT.RooArgList(self.xvar))
    hists['data'].Scale(float(self.nBins)/1600)
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
    for k,v in self.Pdfs.iteritems(): 
      if k == 'final': continue
      pdfs[k] = v
    if len(pdfs.keys())!=1:
      pdfItr = 0
      for k,v in pdfs.iteritems():
	if pdfItr == 0: 
	  if "gaus" in k: frac = self.Pdfs['final'].getComponents().getRealValue("frac_g0_constrained")
	  else: frac = frac = self.Pdfs['final'].getComponents().getRealValue("frac_constrained")
	else:
	  frac = frac = self.Pdfs['final'].getComponents().getRealValue("%s_%s_recursive_fraction_%s"%(self.proc,self.cat,k))
	# Create histogram with 1600 bins
	hists[k] = v.createHistogram("h_%s"%k,self.xvar,ROOT.RooFit.Binning(1600))
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
    leg1 = ROOT.TLegend(0.6,0.4,0.86,0.6)
    leg1.SetFillStyle(0)
    leg1.SetLineColor(0)
    leg1.SetTextSize(0.035)
    for k,v in pdfs.iteritems(): leg1.AddEntry(hists[k],k,"L")
    leg1.Draw("Same")
    canv.Update()
    raw_input("Press any key to continue...")
