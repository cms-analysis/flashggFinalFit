import ROOT
import json
import numpy as np
from scipy.optimize import minimize
import scipy.stats
from collections import OrderedDict as od
from array import array

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Function for NLL fit
# def NLL(X,model,verbose=False):
#   # X: vector of fit parameter values (updated with minimize function)
#   # Loop over parameters and set vals
#   for i in range(len(X)): model.FitParameters[i].setVal(X[i])
#   nParams = len(model.FitParameters)

#   # Counter for bins entering fit
#   k = 0

#   # Using numpy
#   bins, nPdf, nData = [], [], []
#   # Loop over bins
#   for i in range(model.DataHist.numEntries()):
#     p = model.DataHist.get(i)
#     model.xvar.setVal(p.getRealValue(model.xvar.GetName()))
#     # Skip if in blinding region
#     if( model.blind )&( ( model.xvar.getVal() > model.blindingRegion[0] )&( model.xvar.getVal() < model.blindingRegion[1] ) ): continue
#     ndata = model.DataHist.weight()
#     npdf = model.FitPDF.getVal( ROOT.RooArgSet(model.xvar) )*model.DataHist.binVolume() # Un-normalised
#     bins.append(i)
#     nPdf.append(npdf)
#     nData.append(ndata)
#     k += 1

#   # Convert to numpy array
#   nPdf = np.asarray(nPdf)
#   nData = np.asarray(nData)
#   ni = np.linspace(0,len(nData)-1,len(nData))

#   # Re-normalise pdf to have same yield as data: accounts for blinding region
#   normFactor = nData.sum()/nPdf.sum()
#   nPdf = nPdf*normFactor

#   # Calculate -NLL terms: final term = 0 for zero entries
#   terms_nonzero = nPdf[nData>0]-nData[nData>0]+nData[nData>0]*np.log(nData[nData>0]/nPdf[nData>0])
#   terms_zero = nPdf[nData==0]-nData[nData==0]

#   if verbose:
#     for i in range(len(nData)):
#       if i in ni[nData>0]: t, idx = terms_nonzero, np.where(ni[nData>0]==i)[0][0]
#       else: t, idx = terms_zero, np.where(ni[nData==0]==i)[0][0]
#       print " --> [DEBUG] Bin %g : nPdf = %.6f, nData = %.6f --> NLL = %.6f"%(bins[i],nPdf[i],nData[i],t[idx])

#   # Sum terms
#   NLL = terms_nonzero.sum()+terms_zero.sum()

#   # Set n(degrees of freedom)
#   model.setNdof(k-nParams)
#   return NLL

def NLL(X,model,verbose=False,useDataHistFit=False):
  # X: vector of fit parameter values (updated with minimize function)
  # Loop over parameters and set vals
  for i in range(len(X)): model.FitParameters[i].setVal(X[i])
  nParams = len(model.FitParameters)

  # Counter for bins entering fit
  k = 0

  if useDataHistFit:
    DataHist = model.DataHistFit
  else:
    DataHist = model.DataHist

  # Using numpy
  bins, nPdf, nData = [], [], []
  # Loop over bins
  for i in range(DataHist.numEntries()):
    p = DataHist.get(i)
    #print(p.getRealValue(model.xvar.GetName()))
    model.xvar.setVal(p.getRealValue(model.xvar.GetName()))
    # Skip if in blinding region
    if( model.blind )&( ( model.xvar.getVal() > model.blindingRegion[0] )&( model.xvar.getVal() < model.blindingRegion[1] ) ): continue
    ndata = DataHist.weight()
    npdf = model.FitPDF.getVal( ROOT.RooArgSet(model.xvar) )*DataHist.binVolume() # Un-normalised
    bins.append(i)
    nPdf.append(npdf)
    nData.append(ndata)
    k += 1

  # Convert to numpy array
  nPdf = np.asarray(nPdf)
  nData = np.asarray(nData)
  ni = np.linspace(0,len(nData)-1,len(nData))

  # Re-normalise pdf to have same yield as data: accounts for blinding region
  normFactor = nData.sum()/nPdf.sum()
  nPdf = nPdf*normFactor

  # Calculate -NLL terms: final term = 0 for zero entries
  terms_nonzero = nPdf[nData>0]-nData[nData>0]+nData[nData>0]*np.log(nData[nData>0]/nPdf[nData>0])
  terms_zero = nPdf[nData==0]-nData[nData==0]

  if verbose:
    for i in range(len(nData)):
      if i in ni[nData>0]: t, idx = terms_nonzero, np.where(ni[nData>0]==i)[0][0]
      else: t, idx = terms_zero, np.where(ni[nData==0]==i)[0][0]
      print " --> [DEBUG] Bin %g : nPdf = %.6f, nData = %.6f --> NLL = %.6f"%(bins[i],nPdf[i],nData[i],t[idx])

  # Sum terms
  NLL = terms_nonzero.sum()+terms_zero.sum()

  # Set n(degrees of freedom)
  model.setNdof(k-nParams)
  return NLL

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Functions for chi2 fit
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

def Chi2(X,model,verbose=False):
  # X: vector of fit parameter values (updated with minimize function)
  # Loop over parameters and set vals
  for i in range(len(X)): model.FitParameters[i].setVal(X[i])
  nParams = len(model.FitParameters)

  # Counter for bins entering fit
  k = 0
  normFactor = model.DataHist.sumEntries()
  # Using numpy and poisson error
  bins, nPdf, nData, eDataSumW2 = [], [], [], []
  # Loop over bins
  for i in range(model.DataHist.numEntries()):
    p = model.DataHist.get(i)
    model.xvar.setVal(p.getRealValue(model.xvar.GetName()))
    # Skip if in blinding region
    if( model.blind )&( ( model.xvar.getVal() > model.blindingRegion[0] )&( model.xvar.getVal() < model.blindingRegion[1] ) ): continue
    ndata = model.DataHist.weight()
    npdf = model.FitPDF.getVal( ROOT.RooArgSet(model.xvar) )*normFactor*model.DataHist.binVolume()
    eLo, eHi = ROOT.Double(), ROOT.Double()
    model.DataHist.weightError(eLo,eHi,ROOT.RooAbsData.SumW2)
    bins.append(i)
    nPdf.append(npdf)
    nData.append(ndata)
    eDataSumW2.append(eHi) if npdf>ndata else eDataSumW2.append(eLo)
    k += 1

  # Convert to numpy array
  nPdf = np.asarray(nPdf)
  nData = np.asarray(nData)
  eDataSumW2 = np.asarray(eDataSumW2)

  #eDataSumW2 = (nData==0)*1+eDataSumW2
  #e = eDataSumW2

  # Change error to poisson intervals
  eLo,eHi = poisson_interval(nData,eDataSumW2,level=0.68)
  eDataPoisson = (nPdf>nData)*eHi + (nPdf<=nData)*eLo
  #eDataPoisson = np.maximum(eHi,eLo)
  e = eDataPoisson

  terms = (nPdf-nData)**2/(e**2)

  if verbose:
    for i in range(len(terms)):
      print " --> [DEBUG] Bin %g : nPdf = %.6f, nData = %.6f, e(poisson) = %.6f --> chi2 term = %.6f"%(bins[i],nPdf[i],nData[i],e[i],terms[i])

  # Sum terms
  chi2 = terms.sum()

  # Set n(degrees of freedom)
  model.setNdof(k-nParams)
  return chi2
