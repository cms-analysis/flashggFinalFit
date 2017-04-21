#!/usr/bin/env python

# Usual reasons to love python imports
import os
import sys
import shlex
from array import array
import ROOT as r

ext='ws919'

r.gSystem.Load("libHiggsAnalysisCombinedLimit")
r.gSystem.Load("libHiggsAnalysisGBRLikelihood")
#procs=['ggh','vbf','zh','wh','tth']
procs=['GG2H','VBF','TTH','QQ2HLNU','QQ2HLL','WH2HQQ','ZH2HQQ','testBBH','testTHQ','testTHW']
cats=['UntaggedTag_0','UntaggedTag_1','UntaggedTag_2','UntaggedTag_3','VBFTag_0','VBFTag_1','VBFTag_2','TTHLeptonicTag','TTHHadronicTag','ZHLeptonicTag','WHLeptonicTag','VHLeptonicLooseTag','VHHadronicTag','VHMetTag']
rvwv=['rv','wv']

for proc in procs:
  for cat in cats:
    f = r.TFile("outdir_%s/CMS-HGG_sigfit_%s_%s_%s.root"%(ext,ext,proc,cat))
    w = f.Get("wsig_13TeV")
    #w.Print();
    #exit(1)
    MH = w.var("MH")
    mass = w.var("CMS_hgg_mass")
    for v in rvwv:
     print " consider ", proc, cat, v
     nGaussian=-1
     coeffs=[]
     #dynamiccaly get nGaussians
     pdf= w.pdf("hggpdfsmrel_13TeV_%s_%s_%s_13TeV"%(proc,cat,v));
     #pdf= r.RooDoubleCBFast(w.pdf("dcb_%s_%s_%s_13TeV"%(proc,cat,v)),"test");
     pdf.Print()
     #exit (1)
     d=119.9
     increment=0.1
     while (d<130.0):
       d=d+increment
       MH.setVal(d)
       m=179.875
       #norm = pdf.createIntegral(r.RooArgSet(mass,MH))
       #thisint= norm.getVal()
       h =pdf.createHistogram("htemp_%.2f_%.2f_%s_%s_%s"%(d,m,proc,cat,v),mass)
       h.Print()
       #print "integral " , thisint
       #while (m<179.9):
        #mass.setVal(m)
        #print " this is the value of ", pdf.GetName() , " at mh= ", d , " and mgg= ", m ,  "  : " ,  
        #thiseval =pdf.evaluate(), " norm ", 
        #m=m+increment
    #exit(1)
     
