#!/usr/bin/env python

# Usual reasons to love python imports
import os
import sys
import shlex
from array import array
import ROOT as r



r.gSystem.Load("libHiggsAnalysisCombinedLimit")
r.gSystem.Load("libHiggsAnalysisGBRLikelihood")
procs=['ggh','vbf','zh','wh','tth']
cats=['UntaggedTag_0','UntaggedTag_1','UntaggedTag_2','UntaggedTag_3','VBFTag_0','VBFTag_1','TTHLeptonicTag','TTHHadronicTag']
rvwv=['rv','wv']


for proc in procs:
  for cat in cats:
    f = r.TFile("outdir_HggAnalysis_SimultaneousSignalFit_stage2/CMS-HGG_sigfit_HggAnalysis_SimultaneousSignalFit_stage2_%s_%s.root"%(proc,cat))
    w = f.Get("wsig_13TeV")
    MH = w.var("MH")
    for v in rvwv:
     print " consider ", proc, cat, v
     nGaussian=-1
     coeffs=[]
     #dynamiccaly get nGaussians
     for n in range(0,5):
        c=w.obj("frac_g%d_%s_%s_%s_13TeV"%(n,proc,cat,v)) 
        #print "is c an empty ppinter?", (c==None)
        if (c==None): 
          nGaussian=n-1
          break
        coeffs.append(c)
     #print " --> now check each param"
     for n in range(1,nGaussian):
      func = w.function("hggpdfsmrel_13TeV_%s_%s_%s_13TeV_recursive_fraction_gaus_g%d_%s_%s_%s_13TeV"%(proc,cat,v,n,proc,cat,v))
      print " checking param ", func.GetName()
      d=119.9
      numberOfSuccessive0Or1Values=0
      while (d<130.0):
        d=d+0.1
        MH.setVal(d)
        if (func.getVal()<0 or func.getVal()>1):
          print "ERROR one of the parameters has gone bonkers at mh ", d, "! ", func.GetName(), func.getVal()
          for c in coeffs:
            print "value of this coef" , c.GetName(), c.getVal()
          exit(1)
        if (func.getVal()==0 or func.getVal()>0.99):
          #print " mh= ", d," param  ",func.GetName(), " has dodgy value", func.getVal()
          numberOfSuccessive0Or1Values=numberOfSuccessive0Or1Values+1
      if (numberOfSuccessive0Or1Values>2):
         print "ERROR too many 0 or 1 values in a row ! try reducing number of gaussians for " , proc, cat, v
         #exit(1)

          




exit(1)
