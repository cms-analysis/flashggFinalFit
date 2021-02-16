# Class for performing simultaneous signal fit
import ROOT
import json
import numpy as np
from scipy.optimize import minimize
import scipy.stats
from collections import OrderedDict as od
from array import array

# Parameter lookup table for initialisation
# So far defined up to MHPolyOrder=2
pLUT = od()
pLUT['DCB'] = od()
pLUT['DCB']['dm_p0'] = [0.1,-2.5,2.5]
pLUT['DCB']['dm_p1'] = [0.0,-0.1,0.1]
pLUT['DCB']['dm_p2'] = [0.0,-0.001,0.001]
pLUT['DCB']['sigma_p0'] = [2.,1.,20.]
pLUT['DCB']['sigma_p1'] = [0.0,-0.1,0.1]
pLUT['DCB']['sigma_p2'] = [0.0,-0.001,0.001]
pLUT['DCB']['n1_p0'] = [20.,1.00001,500]
pLUT['DCB']['n1_p1'] = [0.0,-0.1,0.1]
pLUT['DCB']['n1_p2'] = [0.0,-0.001,0.001]
pLUT['DCB']['n2_p0'] = [20.,1.00001,500]
pLUT['DCB']['n2_p1'] = [0.0,-0.1,0.1]
pLUT['DCB']['n2_p2'] = [0.0,-0.001,0.001]
pLUT['DCB']['a1_p0'] = [1.,1.,10.]
pLUT['DCB']['a1_p1'] = [0.0,-0.1,0.1]
pLUT['DCB']['a1_p2'] = [0.0,-0.001,0.001]
pLUT['DCB']['a2_p0'] = [1.,1.,20.]
pLUT['DCB']['a2_p1'] = [0.0,-0.1,0.1]
pLUT['DCB']['a2_p2'] = [0.0,-0.001,0.001]
pLUT['Gaussian_wdcb'] = od()
pLUT['Gaussian_wdcb']['dm_p0'] = [0.1,-1.5,1.5]
pLUT['Gaussian_wdcb']['dm_p1'] = [0.01,-0.01,0.01]
pLUT['Gaussian_wdcb']['dm_p2'] = [0.01,-0.01,0.01]
pLUT['Gaussian_wdcb']['sigma_p0'] = [1.5,1.0,4.]
pLUT['Gaussian_wdcb']['sigma_p1'] = [0.0,-0.1,0.1]
pLUT['Gaussian_wdcb']['sigma_p2'] = [0.0,-0.001,0.001]
pLUT['Frac'] = od()
pLUT['Frac']['p0'] = [0.25,0.01,0.99]
pLUT['Frac']['p1'] = [0.,-0.05,0.05]
pLUT['Frac']['p2'] = [0.,-0.0001,0.0001]
pLUT['Gaussian'] = od()
pLUT['Gaussian']['dm_p0'] = [0.1,-5.,5.]
pLUT['Gaussian']['dm_p1'] = [0.0,-0.01,0.01]
pLUT['Gaussian']['dm_p2'] = [0.0,-0.01,0.01]
pLUT['Gaussian']['sigma_p0'] = ['func',0.5,10.0]
pLUT['Gaussian']['sigma_p1'] = [0.0,-0.01,0.01]
pLUT['Gaussian']['sigma_p2'] = [0.0,-0.01,0.01]
pLUT['FracGaussian'] = od()
pLUT['FracGaussian']['p0'] = ['func',0.01,0.99]
pLUT['FracGaussian']['p1'] = [0.01,-0.005,0.005]
pLUT['FracGaussian']['p2'] = [0.00001,-0.00001,0.00001]

# Function to convert sumw2 variance to poisson interval
def poisson_interval(x,eSumW2,level=0.68):
  neff = x**2/(eSumW2**2)
  scale = abs(x)/neff
  l = scipy.stats.gamma.interval(level, neff, scale=scale,)[0]
  u = scipy.stats.gamma.interval(level, neff+1, scale=scale,)[1]
  # protect against no effective entries
  l[neff==0] = 0.
  # protect against no variance
  l[eSumW2==0.] = 0.
  u[eSumW2==0.] = np.inf
  # convert to upper and lower errors
  eLo, eHi = abs(l-x),abs(u-x)
  return eLo, eHi

# Function to calc chi2 for binned fit given pdf, RooDataHist and xvar as inputs
#def calcChi2(x,pdf,d,errorType="Sumw2",_verbose=False,fitRange=[100,180]):
#def calcChi2(x,pdf,d,errorType="Poisson",_verbose=False,fitRange=[110,140]):
def calcChi2(x,pdf,d,errorType="Poisson",_verbose=False,fitRange=[105,150]):

  k = 0. # number of non empty bins (for calc degrees of freedom)
  normFactor = d.sumEntries()
  
  # Using numpy and poisson error
  bins, nPdf, nData, eDataSumW2 = [], [],[],[]
  for i in range(d.numEntries()):
    p = d.get(i)
    x.setVal(p.getRealValue(x.GetName()))
    if( x.getVal() < fitRange[0] )|( x.getVal() > fitRange[1] ): continue
    ndata = d.weight()
    if ndata*ndata == 0: continue
    npdf = pdf.getVal(ROOT.RooArgSet(x))*normFactor*d.binVolume()
    eLo, eHi = ROOT.Double(), ROOT.Double()
    d.weightError(eLo,eHi,ROOT.RooAbsData.SumW2)
    bins.append(i)
    nPdf.append(npdf)
    nData.append(ndata)
    eDataSumW2.append(eHi) if npdf>ndata else eDataSumW2.append(eLo)
    k += 1

  # Convert to numpy array
  nPdf = np.asarray(nPdf)
  nData = np.asarray(nData)
  eDataSumW2 = np.asarray(eDataSumW2)

  if errorType == 'Poisson':
    # Change error to poisson intervals: take max interval as error
    eLo,eHi = poisson_interval(nData,eDataSumW2,level=0.68)
    #eDataPoisson = 0.5*(eHi+eLo)
    eDataPoisson = np.maximum(eHi,eLo) 
    #eDataPoisson = (nPdf>nData)*eHi + (nPdf<=nData)*eLo 
    e = eDataPoisson
    # Calculate chi2 terms
    terms = (nPdf-nData)**2/(eDataPoisson**2)
  elif errorType == "Expected":
    # Change error to sqrt pdf entries
    eExpected = np.sqrt(nPdf)
    e = eExpected
    # Calculate chi2 terms
    terms = (nPdf-nData)**2/(eExpected**2)
  else:
    # Use SumW2 terms to calculate chi2
    e = eDataSumW2
    terms = (nPdf-nData)**2/(eDataSumW2**2)
   
  # If verbose: print to screen
  if _verbose:
    for i in range(len(terms)):
      print " --> [DEBUG] Bin %g : nPdf = %.6f, nData = %.6f, e(%s) = %.6f --> chi2 term = %.6f"%(bins[i],nPdf[i],nData[i],errorType,e[i],terms[i])

  # Sum terms
  result = terms.sum()

  return result,k

# Function to add chi2 for multiple mass points
def nChi2Addition(X,ssf,verbose=False):
  # X: vector of param values (updated with minimise function)
  # Loop over parameters and set RooVars
  for i in range(len(X)): ssf.FitParameters[i].setVal(X[i])
  # Loop over datasets: adding chi2 for each mass point
  chi2sum = 0
  K = 0 # number of non empty bins
  C = len(X)-1 # number of fit params (-1 for MH)
  for mp,d in ssf.DataHists.iteritems():
    ssf.MH.setVal(int(mp))
    chi2, k  = calcChi2(ssf.xvar,ssf.Pdfs['final'],d,_verbose=verbose)
    chi2sum += chi2
    K += k
  # N degrees of freedom
  ndof = K-C
  ssf.setNdof(ndof)
  return chi2sum

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   
class SimultaneousFit:
  # Constructor
  def __init__(self,_name,_proc,_cat,_datasetForFit,_xvar,_MH,_MHLow,_MHHigh,_massPoints,_nBins,_MHPolyOrder,_minimizerMethod,_minimizerTolerance,verbose=True):
    self.name = _name
    self.proc = _proc
    self.cat = _cat
    self.datasetForFit = _datasetForFit
    self.xvar = _xvar
    self.MH = _MH
    self.MHLow = _MHLow
    self.MHHigh = _MHHigh
    self.massPoints = _massPoints
    self.nBins = _nBins
    self.MHPolyOrder = _MHPolyOrder
    self.minimizerMethod = _minimizerMethod
    self.minimizerTolerance = _minimizerTolerance
    self.verbose = verbose
    # Prepare vars
    self.MH.setConstant(False)
    self.MH.setVal(125)
    self.MH.setBins(10)
    self.dMH = ROOT.RooFormulaVar("dMH","dMH","@0-125.0",ROOT.RooArgList(self.MH)) 
    self.xvar.setVal(125)
    self.xvar.setBins(self.nBins)
    # Dicts to store all fit vars, polynomials, pdfs and splines
    self.nGaussians = 1
    self.Vars = od()
    self.Varlists = od()
    self.Polynomials = od()
    self.Pdfs = od()
    self.Coeffs = od()
    self.Splines = od()
    # Prepare RooDataHists for fit
    self.DataHists = od()
    self.prepareDataHists()
    # Fit containers
    self.FitParameters = None
    self.Ndof = None
    self.Chi2 = None
    self.FitResult = None

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   
  # Function for setting N degrees of freedom
  def setNdof(self,_ndof): self.Ndof = _ndof  
  
  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   
  # Function to extract param bounds
  def extractXBounds(self):
    XBounds = []
    for i in range(len(self.FitParameters)): XBounds.append((self.FitParameters[i].getMin(),self.FitParameters[i].getMax()))
    return np.asarray(XBounds)

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   
  # Function to extract initial param value vector
  def extractX0(self):
    X0 = []
    for i in range(len(self.FitParameters)): X0.append(self.FitParameters[i].getVal())
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

    # Set number of gaussians
    self.nGaussians = nGaussians

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
    # Extract fit variables: remove xvar from fit parameters
    fv = self.Pdfs['final'].getVariables().Clone()
    fv.remove(self.xvar)
    self.FitParameters = ROOT.RooArgList(fv)
    
    # Create initial vector of parameters and calculate initial Chi2
    if self.verbose: print "\n --> (%s) Initialising fit parameters"%self.name
    x0 = self.extractX0()
    xbounds = self.extractXBounds()
    self.Chi2 = self.getChi2()
    # Print parameter pre-fit values
    if self.verbose: self.printFitParameters(title="Pre-fit")

    # Run fit
    if self.verbose: print " --> (%s) Running fit"%self.name
    self.FitResult = minimize(nChi2Addition,x0,args=self,bounds=xbounds,method=self.minimizerMethod)
    self.Chi2 = self.getChi2()
    #self.Chi2 = nChi2Addition(self.FitResult['x'],self)
    # Print parameter post-fit values
    if self.verbose: self.printFitParameters(title="Post-fit")

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   
  # Function build RooSpline1D from Polynomials to model MH dependence on fit params
  def buildSplines(self):
    # Loop over polynomials
    for k, poly in self.Polynomials.iteritems():
      _x, _y = [], []
      _mh = 100.
      while(_mh<180.1):
        self.MH.setVal(_mh)
        _x.append(_mh)
        _y.append(poly.getVal())
        _mh += 0.1
      # Convert to arrays
      arr_x, arr_y = array('f',_x), array('f',_y)
      # Create spline and save to dict
      self.Splines[k] = ROOT.RooSpline1D(poly.GetName(),poly.GetName(),self.MH,len(_x),arr_x,arr_y)
           
  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   
  # Function to print fit values
  def printFitParameters(self,title="Fit"):
    print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    print " --> (%s) %s parameter values:"%(self.name,title)
    # Skip MH
    for i in range(1,len(self.FitParameters)): print "    * %-20s = %.6f"%(self.FitParameters[i].GetName(),self.FitParameters[i].getVal())
    print "    ~~~~~~~~~~~~~~~~"
    print "    * chi2 = %.6f, n(dof) = %g --> chi2/n(dof) = %.3f"%(self.getChi2(),int(self.Ndof),self.getChi2()/int(self.Ndof))
    print "    ~~~~~~~~~~~~~~~~"
    print "    * [VERBOSE] chi2 = %.6f"%(self.getChi2(verbose=True))
    print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   
  # Function to set vars from json file
  def setVars(self,_json):
    with open(_json,"r") as jf: _vals = json.load(jf)
    for k,v in _vals.iteritems(): self.Vars[k].setVal(v)

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   
  # Function to re-calculate chi2 after setting vars
  def getChi2(self,verbose=False):
    x = self.extractX0()
    self.Chi2 = nChi2Addition(x,self,verbose=verbose)
    return self.Chi2

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   
  # Function to re-calculate chi2/ndof after setting vars
  def getReducedChi2(self):
    x = self.extractX0()
    self.Chi2 = nChi2Addition(x,self)
    return self.Chi2/int(self.Ndof)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  

