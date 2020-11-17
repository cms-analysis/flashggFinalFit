import os, sys
import glob
import re
import ROOT
import math
from collections import OrderedDict as od
from commonObjects import *

# Functions for manip RooDataSets
def reduceDataset(_d,_argset): return _d.reduce(_argset)

def splitRVWV(_d,_argset,mode="RV"):
  # Split into RV/WV senario at dZ = 1cm
  if mode == "RV": return _d.reduce(_argset,"abs(dZ)<=1.")
  elif mode == "WV": return _d.reduce(_argset,"abs(dZ)>1.")
  else:
    print " --> [ERROR] unrecognised mode (%s) in splitRVWV function"%mode
    return 0

def beamspotReweigh(d,widthData,widthMC,_xvar,_dZ,_x='CMS_hgg_mass',preserveNorm=True):
  isumw = d.sumEntries()
  drw = d.emptyClone()
  rw = ROOT.RooRealVar("weight","weight",-100000,1000000)
  for i in range(0,d.numEntries()):
    x, dz = d.get(i).getRealValue(_x), d.get(i).getRealValue("dZ")
    f = 1.
    if abs(dz) < 0.1: f = 1.
    else:
      mcBeamspot = ROOT.TMath.Gaus(dz,0,math.sqrt(2)*widthMC,True)
      dataBeamspot = ROOT.TMath.Gaus(dz,0,math.sqrt(2)*widthData,True)
      f = dataBeamspot/mcBeamspot
    # Set weights and vars
    rw.setVal(f*d.weight())
    _xvar.setVal(x)
    _dZ.setVal(dz)
    # Add point to dataset
    drw.add( ROOT.RooArgSet(_xvar,_dZ), rw.getVal() )

  # If preserve norm of original dataset
  if preserveNorm:
    fsumw = drw.sumEntries()
    drw_pn = d.emptyClone()
    for i in range(0,drw.numEntries()):
      x, dz = drw.get(i).getRealValue(_x), drw.get(i).getRealValue("dZ")
      f = isumw/fsumw if fsumw!=0. else 1.
      rw.setVal(f*drw.weight())
      _xvar.setVal(x)
      _dZ.setVal(dz)
      # Add point to dataset
      drw_pn.add( ROOT.RooArgSet(_xvar,_dZ), rw.getVal() )
    # Set reweighted dataset
    drw = drw_pn.Clone()

  # Return reweighted dataset
  return drw
