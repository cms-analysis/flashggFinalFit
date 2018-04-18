#!/usr/bin/env python
# code to make first-pass stxs transfer matrix plots

import os
import ROOT as r

#from optparse import OptionParser
#parser = OptionParser()
#parser.add_option('-k', '--key', default='GluGluHToGG', help='choose the sample to run on')
#parser.add_option('-d', '--doLoose', default=False, action='store_true', help='use loose photons (default false, ie use only tight photons)')
#(opts,args) = parser.parse_args()

r.gROOT.SetBatch(True)

stage1procMap = {}
stage1procMap[0]   = (0  ,"unknown")
stage1procMap[100] = (-1 ,"GG2H_FWDH")
stage1procMap[101] = (1  ,"GG2H_VBFTOPO_JET3VETO")
stage1procMap[102] = (2  ,"GG2H_VBFTOPO_JET3")
stage1procMap[103] = (3  ,"GG2H_0J  ")
stage1procMap[104] = (4  ,"GG2H_1J_PTH_0_60")
stage1procMap[105] = (5  ,"GG2H_1J_PTH_60_120")
stage1procMap[106] = (6  ,"GG2H_1J_PTH_120_200")
stage1procMap[107] = (7  ,"GG2H_1J_PTH_GT200")
stage1procMap[108] = (8  ,"GG2H_GE2J_PTH_0_60")
stage1procMap[109] = (9  ,"GG2H_GE2J_PTH_60_120")
stage1procMap[110] = (10 ,"GG2H_GE2J_PTH_120_200")
stage1procMap[111] = (11 ,"GG2H_GE2J_PTH_GT200")
stage1procMap[200] = (-2 ,"QQ2HQQ_FWDH")
stage1procMap[201] = (12 ,"QQ2HQQ_VBFTOPO_JET3VETO")
stage1procMap[202] = (13 ,"QQ2HQQ_VBFTOPO_JET3")
stage1procMap[203] = (14 ,"QQ2HQQ_VH2JET")
stage1procMap[204] = (15 ,"QQ2HQQ_REST")
stage1procMap[205] = (16 ,"QQ2HQQ_PTJET1_GT200")
stage1procMap[300] = (-3 ,"QQ2HLNU_FWDH")
stage1procMap[301] = (17 ,"QQ2HLNU_PTV_0_150")
stage1procMap[302] = (18 ,"QQ2HLNU_PTV_150_250_0J")
stage1procMap[303] = (19 ,"QQ2HLNU_PTV_150_250_GE1J")
stage1procMap[304] = (20 ,"QQ2HLNU_PTV_GT250")
stage1procMap[400] = (-4 ,"QQ2HLL_FWDH")
stage1procMap[401] = (21 ,"QQ2HLL_PTV_0_150")
stage1procMap[402] = (22 ,"QQ2HLL_PTV_150_250_0J")
stage1procMap[403] = (23 ,"QQ2HLL_PTV_150_250_GE1J")
stage1procMap[404] = (24 ,"QQ2HLL_PTV_GT250")
stage1procMap[500] = (-5 ,"GG2HLL_FWDH")
stage1procMap[501] = (25 ,"GG2HLL_PTV_0_150")
stage1procMap[502] = (26 ,"GG2HLL_PTV_GT150_0J")
stage1procMap[503] = (27 ,"GG2HLL_PTV_GT150_GE1J")
stage1procMap[600] = (-6 ,"TTH_FWDH")
stage1procMap[601] = (28 ,"TTH")
stage1procMap[700] = (-7 ,"BBH_FWDH")
stage1procMap[701] = (29 ,"BBH")
stage1procMap[800] = (-8 ,"TH_FWDH")
stage1procMap[801] = (30 ,"TH")

stage1tagMap = { 0:'LOGICERROR', 1:'RECO_0J', 2:'RECO_1J_PTH_0_60', 3:'RECO_1J_PTH_60_120', 4:'RECO_1J_PTH_120_200', 5:'RECO_1J_PTH_GT200', 
                             6:'RECO_GE2J_PTH_0_60', 7:'RECO_GE2J_PTH_60_120', 8:'RECO_GE2J_PTH_120_200', 9:'RECO_GE2J_PTH_GT200', 10:'RECO_VBFTOPO_JET3VETO', 11:'RECO_VBFTOPO_JET3', 12:'RECO_VH2JET',
                             13:'RECO_0LEP_PTV_0_150', 14:'RECO_0LEP_PTV_150_250_0J', 15:'RECO_0LEP_PTV_150_250_GE1J', 16:'RECO_0LEP_PTV_GT250', 
                             17:'RECO_1LEP_PTV_0_150', 18:'RECO_1LEP_PTV_150_250_0J', 19:'RECO_1LEP_PTV_150_250_GE1J', 20:'RECO_1LEP_PTV_GT250', 
                             21:'RECO_2LEP_PTV_0_150', 22:'RECO_2LEP_PTV_150_250_0J', 23:'RECO_2LEP_PTV_150_250_GE1J', 24:'RECO_2LEP_PTV_GT250',
                             25:'RECO_TTH_LEP', 26:'RECO_TTH_HAD' }

def main():
  #theDir = 'Systematics/test/sig_jobs_125_stage1_recoTagTest/'
  theDir = 'Systematics/test/sig_jobs_125_stage1_recoTagWithTTH/'

  #setup histos
  theHists = {}
  totProcHist = r.TH2F('totProcHist','totProcHist', 39,-8.5,30.5, 27,-0.5,26.5 )
  totTagHist = r.TH2F('totTagHist','totTagHist', 39,-8.5,30.5, 27,-0.5,26.5 )
  for key,pair in stage1procMap.iteritems():
    totProcHist.GetXaxis().SetBinLabel(pair[0]+9,pair[1])
    totProcHist.GetXaxis().SetLabelSize(0.01)
    totTagHist.GetXaxis().SetBinLabel( pair[0]+9,pair[1])
    totTagHist.GetXaxis().SetLabelSize(0.01)
  for key,name in stage1tagMap.iteritems():
    totProcHist.GetYaxis().SetBinLabel(key+1,name)
    totProcHist.GetYaxis().SetLabelSize(0.01)
    totTagHist.GetYaxis().SetBinLabel( key+1,name)
    totTagHist.GetYaxis().SetLabelSize(0.01)

  #theProcs = ['GluGluHToGG']
  theProcs = ['GluGluHToGG', 'VBFHToGG','ttHJetToGG','WHToGG','ZHToGG']
  procMap = {'GluGluHToGG':'ggh', 'VBFHToGG':'vbf','ttHJetToGG':'tth','WHToGG':'wh','ZHToGG':'zh'}
  #theTags = ['UntaggedTag_0', 'UntaggedTag_1', 'UntaggedTag_2', 'UntaggedTag_3', 'VBFTag_0', 'VBFTag_1', 'VBFTag_2']
  theTags = ['UntaggedTag_0', 'UntaggedTag_1', 'UntaggedTag_2', 'UntaggedTag_3', 'VBFTag_0', 'VBFTag_1', 'VBFTag_2',  'TTHHadronicTag', 'TTHLeptonicTag', 
             'VHLeptonicLooseTag', 'VHHadronicTag', 'VHMetTag', 'WHLeptonicTag', 'ZHLeptonicTag']
  theTrees = {}
  print 'getting trees'
  for theProc in theProcs:
    for theTag in theTags: 
      theTrees[(theProc,theTag)] = r.TChain('tagsDumper/trees/%s_125_13TeV_%s'%(procMap[theProc],theTag))
      for root, dirs, files in os.walk(theDir):
        for fileName in files:
          if not theProc in fileName: continue
          if not '.root' in fileName: continue
          theTrees[(theProc,theTag)].Add(theDir+fileName)
  print 'got trees'

  #main code starts here
  procNormMap = {}
  tagNormMap  = {}
  for i in range(-10,35):
    procNormMap[i] = 0.
    tagNormMap[i] = 0.
  print 'beginning normalisation'
  for theProc in theProcs:
    for theTag in theTags: 
      print 'processing %s %s'%(procMap[theProc],theTag)
      for i,ev in enumerate(theTrees[(theProc,theTag)]):
        stage1proc = getattr(ev,'stage1cat')
        stage1proc = stage1procMap[stage1proc][0]
        stage1tag  = getattr(ev,'stage1recoEnum')
        weight = getattr(ev,'weight')
        if stage1proc>30 or stage1tag>26: continue
        if stage1proc<-8 or stage1tag<0: continue
        procNormMap[stage1proc] += weight
        tagNormMap[stage1tag]   += weight
  print 'done normalisation'

  print 'beginning filling hists'
  for theProc in theProcs:
    for theTag in theTags: 
      print 'processing %s %s'%(procMap[theProc],theTag)
      for i,ev in enumerate(theTrees[(theProc,theTag)]):
        stage1proc = getattr(ev,'stage1cat')
        stage1proc = stage1procMap[stage1proc][0]
        stage1tag  = getattr(ev,'stage1recoEnum')
        weight = getattr(ev,'weight')
        if stage1proc>30 or stage1tag>26: continue
        if stage1proc<-8 or stage1tag<0: continue
        procWeight = 0.
        tagWeight  = 0.
        if procNormMap[stage1proc] > 0.: procWeight = weight / procNormMap[stage1proc]
        if tagNormMap[stage1tag]   > 0.: tagWeight  = weight / tagNormMap[stage1tag]
        totProcHist.Fill( stage1proc, stage1tag, procWeight)
        totTagHist.Fill(  stage1proc, stage1tag, tagWeight)
  print 'done filling hists'

  #draw hists, send to web
  canv = r.TCanvas('canv','canv')
  r.gStyle.SetPaintTextFormat('2.0f')
  totProcHist.SetStats(0)
  totProcHist.GetXaxis().SetLabelSize(0.015)
  totProcHist.GetYaxis().SetLabelSize(0.015)
  totProcHist.Scale(100.)
  totProcHist.SetMinimum(-0.00001)
  totProcHist.SetMaximum(100.)
  totProcHist.Draw('colz,text')
  canv.Print('totProcHist.pdf')
  canv.Print('totProcHist.png')
  totTagHist.SetStats(0)
  totTagHist.GetXaxis().SetLabelSize(0.015)
  totTagHist.GetYaxis().SetLabelSize(0.015)
  totTagHist.Scale(100.)
  totTagHist.SetMinimum(-0.00001)
  totTagHist.SetMaximum(100.)
  totTagHist.Draw('colz,text')
  canv.Print('totTagHist.pdf')
  canv.Print('totTagHist.png')
  #save hists
  outFile = r.TFile('stxsStage1Hists.root','RECREATE')
  totProcHist.Write()
  totTagHist.Write()
  outFile.Close()


if __name__ == '__main__':
  main()
