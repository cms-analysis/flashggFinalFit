#!/usr/bin/env python

import os
import sys
import shlex
from array import array
import ROOT as r
from optparse import OptionParser

def get_options():
  parser = OptionParser()
  parser.add_option("--year", dest='year', default='2016', help="Dataset year")
  parser.add_option("--tagSet", dest='tagSet', default='tagsetone', help="Tag set")
  return parser.parse_args()
(opt,args) = get_options()

catsSplittingScheme = {
  'tagsetone':['RECO_0J_PTH_0_10_Tag0', 'RECO_0J_PTH_0_10_Tag1', 'RECO_0J_PTH_0_10_Tag2', 'RECO_0J_PTH_GT10_Tag0', 'RECO_0J_PTH_GT10_Tag1', 'RECO_0J_PTH_GT10_Tag2', 'RECO_1J_PTH_0_60_Tag0', 'RECO_1J_PTH_0_60_Tag1', 'RECO_1J_PTH_0_60_Tag2', 'RECO_1J_PTH_60_120_Tag0', 'RECO_1J_PTH_60_120_Tag1', 'RECO_1J_PTH_60_120_Tag2', 'RECO_1J_PTH_120_200_Tag0', 'RECO_1J_PTH_120_200_Tag1', 'RECO_1J_PTH_120_200_Tag2', 'RECO_GE2J_PTH_0_60_Tag0', 'RECO_GE2J_PTH_0_60_Tag1', 'RECO_GE2J_PTH_0_60_Tag2', 'RECO_GE2J_PTH_60_120_Tag0', 'RECO_GE2J_PTH_60_120_Tag1', 'RECO_GE2J_PTH_60_120_Tag2', 'RECO_GE2J_PTH_120_200_Tag0', 'RECO_GE2J_PTH_120_200_Tag1', 'RECO_GE2J_PTH_120_200_Tag2'],
  'tagsettwo':['RECO_PTH_200_300_Tag0', 'RECO_PTH_200_300_Tag1', 'RECO_PTH_300_450_Tag0', 'RECO_PTH_300_450_Tag1', 'RECO_PTH_450_650_Tag0', 'RECO_PTH_450_650_Tag1', 'RECO_PTH_GT650_Tag0', 'RECO_PTH_GT650_Tag1', 'RECO_VBFTOPO_VHHAD_Tag0', 'RECO_VBFTOPO_VHHAD_Tag1', 'RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag0', 'RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag1', 'RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag0', 'RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag1', 'RECO_VBFTOPO_JET3_LOWMJJ_Tag0', 'RECO_VBFTOPO_JET3_LOWMJJ_Tag1', 'RECO_VBFTOPO_JET3_HIGHMJJ_Tag0', 'RECO_VBFTOPO_JET3_HIGHMJJ_Tag1', 'RECO_VBFTOPO_BSM_Tag0', 'RECO_VBFTOPO_BSM_Tag1', 'RECO_VBFLIKEGGH_Tag0', 'RECO_VBFLIKEGGH_Tag1'],
  'tagsetthree':['RECO_TTH_HAD_LOW_Tag0', 'RECO_TTH_HAD_LOW_Tag1', 'RECO_TTH_HAD_LOW_Tag2', 'RECO_TTH_HAD_LOW_Tag3', 'RECO_TTH_HAD_HIGH_Tag0', 'RECO_TTH_HAD_HIGH_Tag1', 'RECO_TTH_HAD_HIGH_Tag2', 'RECO_TTH_HAD_HIGH_Tag3', 'RECO_WH_LEP_LOW_Tag0', 'RECO_WH_LEP_LOW_Tag1', 'RECO_WH_LEP_LOW_Tag2', 'RECO_WH_LEP_HIGH_Tag0', 'RECO_WH_LEP_HIGH_Tag1', 'RECO_WH_LEP_HIGH_Tag2', 'RECO_ZH_LEP_Tag0', 'RECO_ZH_LEP_Tag1', 'RECO_TTH_LEP_LOW_Tag0', 'RECO_TTH_LEP_LOW_Tag1', 'RECO_TTH_LEP_LOW_Tag2', 'RECO_TTH_LEP_LOW_Tag3', 'RECO_TTH_LEP_HIGH_Tag0', 'RECO_TTH_LEP_HIGH_Tag1', 'RECO_TTH_LEP_HIGH_Tag2', 'RECO_TTH_LEP_HIGH_Tag3', 'RECO_THQ_LEP']
  }

ext = 'stage1_2_%s_%s'%(opt.tagSet,opt.year)

baseFilePath  = '/vols/cms/jl2117/hgg/ws/Feb20_unblinding/stage1_2_%s/%s/'%(opt.year,opt.tagSet)
cats = ",".join(catsSplittingScheme[opt.tagSet])
cats  = cats.split(',')

r.gSystem.Load("libHiggsAnalysisCombinedLimit")
r.gSystem.Load("libHiggsAnalysisGBRLikelihood")

#setup files 
fileNames     = []
for root,dirs,files in os.walk(baseFilePath):
  for fileName in files: 
    if not fileName.startswith('output_'): continue
    if not fileName.endswith('.root'):     continue
    fileNames.append(fileName)
fullFileNames = '' 
for fileName in fileNames: fullFileNames += baseFilePath+fileName+','
fullFileNames = fullFileNames[:-1]
files125 = ''
for fileName in fileNames: 
  if 'M125' in fileName: files125 += baseFilePath+fileName+','
files125 = files125[:-1]

#define processes and categories
procs         = ''
for fileName in fileNames: 
  if 'M125' not in fileName: continue
  procs += fileName.split('pythia8_')[1].split('.root')[0]
  procs += ','
procs = procs[:-1]
procs = procs.split(',')
print 'with processes: %s'%procs
print 'and categories: %s'%cats
rvwv=['rv','wv']

for proc in procs:
  for cat in cats:
    f = r.TFile("outdir_%s/CMS-HGG_sigfit_%s_%s_%s.root"%(ext,ext,proc,cat))
    w = f.Get("wsig_13TeV")
    #w.Print();
    #exit(1)
    try:
      MH = w.var("MH")
    except:
      print 'ED DEBUG: oh dear failed to get MH in the workspace for proc, cat of %s, %s'%(proc,cat)
    mass = w.var("CMS_hgg_mass")
    for v in rvwv:
     print " consider ", proc, cat, v
     nGaussian=-1
     coeffs=[]
     #dynamiccaly get nGaussians
     print 'ED DEBUG about to get pdf with name hggpdfsmrel_%s_13TeV_%s_%s_%s_13TeV_%s'%(opt.year,proc,cat,v,opt.year)
     pdf= w.pdf("hggpdfsmrel_%s_13TeV_%s_%s_%s_13TeV_%s"%(opt.year,proc,cat,v,opt.year));
     print 'ED DEBUG printing pdf with name hggpdfsmrel_%s_13TeV_%s_%s_%s_13TeV_%s'%(opt.year,proc,cat,v,opt.year)
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
    #exit
     
