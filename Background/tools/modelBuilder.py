import ROOT
import json
import numpy as np
from scipy.optimize import minimize
import scipy.stats
from collections import OrderedDict as od
from array import array

from backgroundFunctions import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class modelBuilder:
  # Constructor
  def __init__(self,_name,_cat,_xvar,_data,_functionFamilies,_nBins,verbose=False):
    self.name = _name
    self.cat = _cat
    self.xvar = _xvar
    self.data = _data
    self.functionFamilies = _functionFamilies
    self.nBins = _nBins
    self.params = od()
    self.formulas = od()
    self.functions = od()
    self.pdfs = od()
    self.envelopePdfs = od()
    self.minNLL = 1e10
    self.bestfitPdfIndex = 0
    self.bestfitSnapshot = None
    self.maxTries = 3
  
  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # Function to build pdf
  def buildPdf(self,funcType,order):
    prefix = "%s_%s%g"%(self.name,self.functionFamilies[funcType]['name'][1],order)
    return getPdf(self,prefix,funcType,order)

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # Function to fit pdf to data
  # FIXME: only consider datapoints in sidebands, also replace Minuit with scipy.optimize
  def runFit(self,_pdf):
    # Extract pdf params
    aset = ROOT.RooArgSet()
    pset = _pdf.getParameters(aset)
    # Repeat fit until status = 0, or until tries > self.maxTries
    status = 1.
    minnll = 1e10
    ntries = 0
    reachedMaxTries = False
    while( status != 0. )&( reachedMaxTries is False ):
      if ntries >= self.maxTries: reachedMaxTries = True
      else: 
        fit = _pdf.fitTo( self.data, ROOT.RooFit.Save(1), ROOT.RooFit.Minimizer("Minuit2","minimize"), ROOT.RooFit.SumW2Error(ROOT.kTRUE) )
        status = fit.status()
        minnll = fit.minNll()
        
        # If status != 0, randomize parameter values and fit again
        if status != 0: pset.assignValueOnly( fit.randomizePars() )
        ntries += 1
    
    return minnll, status        


  # Function to extract goodness-of-fit from pdf to data
  # FIXME: only consider datapoints in sidebands
  def extractGOF(self,_pdf):

    # Reweight dataset to have sum entries = 1
    drw = self.data.emptyClone()
    sumw = self.data.sumEntries()
    self.params['weight'] = ROOT.RooRealVar("weight","weight",-10000,10000)
    for i in range(0,self.data.numEntries()):
      self.xvar.setVal(self.data.get(i).getRealValue(self.xvar.GetName()))
      self.params['weight'].setVal((1./sumw)*self.data.weight())
      drw.add(ROOT.RooArgSet(self.xvar,self.params['weight']),self.params['weight'].getVal())
    
    # Get chi2 value from plotting (reweighted) data and pdf
    fr = self.xvar.frame()
    self.data.plotOn(fr,ROOT.RooFit.Binning(self.nBins),ROOT.RooFit.Name("data"))
    _pdf.plotOn(fr,ROOT.RooFit.Name("pdf"))
    aset = ROOT.RooArgSet()
    nparams = _pdf.getParameters(aset).getSize()
    # TODO: only calculate over data sidebands, may require chi2 function from signal fitting
    chi2 = fr.chiSquare("pdf","data",nparams)
    pval = ROOT.TMath.Prob(chi2*(self.nBins-nparams),self.nBins-nparams)

    print " --> Calculating GOF for pdf: %s"%_pdf.GetName()
    print "    * Number of params: %g"%int(nparams)
    print "    * Observed chi2 = %.6f"%(chi2*(self.nBins-nparams))
    print "    * GOF pval = %.6f"%pval
    
    return pval 
    # TODO: option to extract gof from toys


  # Function to return prob for fTest: asymptotic or using toys
  def getProbabilityFTest(self,dchi2,ndof):
    prob_asymptotic = ROOT.TMath.Prob(dchi2,ndof)
    return prob_asymptotic
    # TODO: option for extract pval from toys


  # Function to calculate norm of bkg functions
  #def getNormalisation():
 
  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  # Function to perform fTest: save functions that pass to self.functions
  def fTest(self,_maxOrder=6,_pvalFTest=0.05):

    # Loop over function families
    for ff in functionFamilies:
      prevNLL, prob = 0., 0.
      order, prevOrder = 1, 1

      # Loop over orders in function until pval stopping criterion is reached
      while(( prob < _pvalFTest )&( order < _maxOrder+1 )):
        # Build PDF
        bkgPdf = self.buildPdf(ff,order)
        if not bkgPdf:
          # Order not allowed
          order += 1
        else:
          # Run fit and save info
          print "\n --------------------------------------------------------------------"
          print " --> Running fit for bkg pdf: %s\n"%bkgPdf.GetName()
          NLL, fitStatus = self.runFit(bkgPdf)
          # Add to pdfs container
          self.pdfs[(ff,order)] = od()
          self.pdfs[(ff,order)]['name'] = bkgPdf.GetName()
          self.pdfs[(ff,order)]['pdf'] = bkgPdf
          self.pdfs[(ff,order)]['status'] = fitStatus
          self.pdfs[(ff,order)]['NLL'] = NLL
          self.pdfs[(ff,order)]['family'] = ff
          self.pdfs[(ff,order)]['order'] = order

          # Extract norm of function

          # If fit status is not zero: fit has failed
          if self.pdfs[(ff,order)]['status'] != 0:
            print " --> [WARNING] fit did NOT converge successfully for pdf: %s"%self.pdfs[(ff,order)]['name']
            print "     * Assumes NLL > 1e10 --> will not attempt higher orders"
          
          # Calculate dChi2 between this order and previous          
          if order > 1:
            dchi2 = 2.*(prevNLL-NLL) if prevNLL>NLL else 0.
            prob = self.getProbabilityFTest(dchi2,order-prevOrder)
          else:
            prob = 0

          # Add label to dict if order passes fTest
          if prob < _pvalFTest: self.pdfs[(ff,order)]['ftest'] = True
          else: self.pdfs[(ff,order)]['ftest'] = False
          
          print "\n --> (%s, order=%g): Prob( chi2 > chi2(data) ) = %.10f"%(ff,order,prob)
          print " --------------------------------------------------------------------"

          # Store vals and add one to order
          prevNLL = NLL
          prevOrder = order
          order += 1

  
  # Function to loop over possible pdfs which pass the Ftest and implement goodness of fit criteria
  def goodnessOfFit(self,_gofCriteria):
    # Loop over pdfs in model and select those passing fTest
    for k, v in self.pdfs.iteritems():
      if v['ftest']:
        gof = self.extractGOF(v['pdf'])
        if gof > _gofCriteria:
          print " --> Adding pdf to envelope: (%s,%s)\n"%(k[0],k[1])
          self.envelopePdfs[k] = v
        else:
          print " --> Not adding pdf to envelope: (%s,%s)\n"%(k[0],k[1])

  # Function to build envelope of bkg functions using RooMultiPdf class
  def buildEnvelope(self,_extension=""):
    # Check if zero pdfs have satisfied fit criteria
    if len(self.envelopePdfs) == 0:
      print " --> [ERROR] No bkg functions satisfy the fit criteria. Try to increase opt.pvalFTest or decrease opt.gofCriteria"
      sys.exit(1)

    # Create pdf index to label pdf in envelope
    pdfIndexName = "pdfindex_%s%s"%(self.cat,_extension)
    self.pdfIndex = ROOT.RooCategory(pdfIndexName,"c")

    # Loop over pdfs in envelope and store in container
    pdflist = ROOT.RooArgList()
    for k,v in self.envelopePdfs.iteritems(): pdflist.add(v['pdf'])

    # Create RooMultiPdf
    self.multipdf = ROOT.RooMultiPdf("CMS_hgg_%s%s_bkgshape"%(self.cat,_extension),"Envelope",self.pdfIndex,pdflist)


  # Function to calculate the best-fit bkg model function and set at nominal function in envelope
  def getBestfit(self,verbose=True):
    bfIndex = 0
    NLL_min = 1e10
    snap, clean, aset = ROOT.RooArgSet(), ROOT.RooArgSet(), ROOT.RooArgSet()
    params = self.multipdf.getParameters(aset)
    params.remove(self.pdfIndex)
    params.snapshot(clean)
    params.snapshot(snap)
    # Loop over functions in envelope
    for i in range(self.pdfIndex.numTypes()):
      params.assignValueOnly(clean)
      self.pdfIndex.setIndex(i)
      # Run fit
      NLL, fitStatus = self.runFit(self.multipdf)
      # Add penalty term for number of free parameters in model
      NLL += self.multipdf.getCorrection()

      if verbose:
        print "  --> Function: %s"%self.multipdf.getCurrentPdf().GetName()
        print "    * Penalty term: %g"%self.multipdf.getCorrection()
        print "    * NLL + penalty = %.3f"%NLL

      # If NLL<NLL_min set bestfit
      if NLL < NLL_min:
        NLL_min = NLL
        snap.assignValueOnly(params)
        self.bestfitPdfIndex = i

    # Set pdfindex 
    self.pdfIndex.setIndex(self.bestfitPdfIndex)
    params.assignValueOnly(snap)
    self.bestfitSnapshot = params

    if verbose:
      print " --> Best-fit function: %s (index=%g)"%(self.multipdf.getCurrentPdf().GetName(),self.pdfIndex.getIndex())

  # Function to calculate norm of background function
  def getNorm(self,index=None):
    # If index = None then use pre-calculated best-fit
    
  
    
      
