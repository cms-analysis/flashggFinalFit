#! /usr/bin/env python

#=====================================#
#                                     #
#  Original Authors:                  #
#      Alberto Zucchetta              #
#      Jacopo Pazzini                 #
#                                     #
#  2017-07-25                         #
#                                     #
#=====================================#

import os, copy, math
from array import array
from ROOT import ROOT, gROOT, gStyle, gPad, gRandom, TSystemDirectory
from ROOT import TFile, TChain, TTree, TCut, TH1, TH1F, TH2F, THStack, TGraph, TGraphAsymmErrors
from ROOT import TStyle, TCanvas, TPad
from ROOT import TLegend, TLatex, TText, TLine, TBox

gStyle.SetOptStat(0)
#gStyle.SetOptTitle(0) #FIXME

def setCanvas(split=False):

    # create canvas
    #can = TCanvas("can", "can", 800, 800 if split else 600)    
    can = TCanvas("can", "can", 800, 495)    
    if split:
        can.Divide(1, 2)        
        can.GetPad(1).SetPad('Top', '', 0., 0.25, 1.0, 1.0, 0, -1, 0)
        can.GetPad(1).SetTopMargin(0.069)
        can.GetPad(1).SetBottomMargin(0.0184)
        can.GetPad(1).SetRightMargin(0.046)
        can.GetPad(1).SetLeftMargin(0.138)
        can.GetPad(1).SetTicks(1, 1)        
        can.GetPad(2).SetPad("Bottom", '', 0., 0., 1.0, 0.25, 0, -1, 0)
        can.GetPad(2).SetTopMargin(0.0092)
        can.GetPad(2).SetBottomMargin(0.368)
        can.GetPad(2).SetRightMargin(0.046)
        can.GetPad(2).SetLeftMargin(0.138)
        can.GetPad(2).SetTicks(1, 1)     
    else:   
        #can.GetPad(0).SetTopMargin(0.069)
        #can.GetPad(0).SetRightMargin(0.046)
        #can.GetPad(0).SetLeftMargin(0.138)
        #can.GetPad(0).SetBottomMargin(0.15)
        can.GetPad(0).SetTopMargin(0.12)
        can.GetPad(0).SetRightMargin(0.18)
        can.GetPad(0).SetLeftMargin(0.23)
        can.GetPad(0).SetBottomMargin(0.26)
        can.GetPad(0).SetTicks(1, 1)

    can.cd(1)

    return can

def setCanvasCorr(stage='0',split=False): 
 
    # create canvas 
    if stage == '1p2': can = TCanvas("can", "can", 800, 1000 if split else 900)     
    else: can = TCanvas("can", "can", 800, 1000 if split else 800)
    if split: 
        can.Divide(1, 2)         
        can.GetPad(1).SetPad('Top', '', 0., 0.25, 1.0, 1.0, 0, -1, 0) 
        can.GetPad(1).SetTopMargin(0.069) 
        can.GetPad(1).SetBottomMargin(0.0184) 
        can.GetPad(1).SetRightMargin(0.046) 
        can.GetPad(1).SetLeftMargin(0.138) 
        can.GetPad(1).SetTicks(1, 1)         
        can.GetPad(2).SetPad("Bottom", '', 0., 0., 1.0, 0.25, 0, -1, 0) 
        can.GetPad(2).SetTopMargin(0.0092) 
        can.GetPad(2).SetBottomMargin(0.368) 
        can.GetPad(2).SetRightMargin(0.046) 
        can.GetPad(2).SetLeftMargin(0.138)
        can.GetPad(2).SetTicks(1, 1)
    else:
        #can.GetPad(0).SetTopMargin(0.069)
        #can.GetPad(0).SetRightMargin(0.046)
        #can.GetPad(0).SetLeftMargin(0.138)
        #can.GetPad(0).SetBottomMargin(0.15)
        #can.GetPad(0).SetTopMargin(0.14)
        can.GetPad(0).SetRightMargin(0.14)
        if stage == '1p2':
          can.GetPad(0).SetLeftMargin(0.18)
          can.GetPad(0).SetBottomMargin(0.2)
        else:
          can.GetPad(0).SetLeftMargin(0.15)
          can.GetPad(0).SetBottomMargin(0.15)
        can.GetPad(0).SetTicks(1, 1)

    can.cd(1)

    return can

def draw(hist, drawhist=False, ratio=False, log=False):
        
    # create canvas
    can = setCanvas(ratio)
    if log:
        can.GetPad(ratio).SetLogy()
        
    # draw histograms
    drawOption = 'HIST' if drawhist else 'E'
    for ih, h in enumerate(hist):
        h.Draw(drawOption if ih == 0 else drawOption+', SAME')
        formatHisto(h)          

    # create ratio wrt hist[0]
    unc = hist[0].Clone('unc')
    unc.SetFillColor(1)
    unc.SetFillStyle(3005)
    unc.SetMarkerSize(0)
    hratio = {}
    if ratio :
        hist[0].GetXaxis().SetLabelOffset(hist[0].GetXaxis().GetLabelOffset()*10)
        can.cd(2)
        unc.SetTitle('')
        unc.GetYaxis().SetTitle('Ratio')
        unc.GetYaxis().CenterTitle()
        for i in range(1, unc.GetNbinsX()+1):
            unc.SetBinContent(i, 1)
            if hist[0].GetBinContent(i) > 0:
                unc.SetBinError(i, hist[0].GetBinError(i)/hist[0].GetBinContent(i))
        formatRatio(unc)
        unc.Draw('E2')        
        for ih, h in enumerate(hist[1:]):
            hratio[ih] = h.Clone('hratio_%d'%ih)
            hratio[ih].Divide(hist[0])
            hratio[ih].Draw('PE0, SAME')

    can.Update()
    can.GetPad(ratio).RedrawAxis()    
    can.cd(ratio)
    
    # return objects created by the draw() function:
    # can    -> TCanvas
    # unc    -> TH1 with uncertainty on hist[0]     (meaningful only if ratio = True)
    # hratio -> dictionary of TH1 ratio wrt hist[0] (meaningful only if ratio = True)
    return can, unc, hratio

def formatHisto(hist):
    hist.GetXaxis().SetTitleSize(0.0462874993682)
    hist.GetXaxis().SetTitleOffset(1.0)
    hist.GetXaxis().SetLabelSize(0.0462874993682)
    hist.GetXaxis().SetLabelOffset(0.0100567853078)

    hist.GetYaxis().SetTitleSize(0.0462874993682)
    hist.GetYaxis().SetTitleOffset(1.32249999046)
    hist.GetYaxis().SetLabelSize(0.0462874993682)
    hist.GetYaxis().SetLabelOffset(0.005)

    hist.GetZaxis().SetTitleSize(0.0462874993682)
    hist.GetZaxis().SetTitleOffset(1.14999997616)
    hist.GetZaxis().SetLabelSize(0.0462874993682)

def formatRatio(h):
    h.GetXaxis().SetTitleSize(0.138862490654)
    h.GetXaxis().SetTitleOffset(1.0)
    h.GetXaxis().SetLabelSize(0.138862490654)
    h.GetXaxis().SetLabelOffset(0.0150851774961)
    
    h.GetYaxis().SetTitleSize(0.138862490654)
    h.GetYaxis().SetLabelSize(0.138862490654)
    h.GetYaxis().SetTitleOffset(0.440833330154)
    h.GetYaxis().SetTitleOffset(0.440833330154)
    
    h.GetYaxis().SetNdivisions(505)
    h.GetYaxis().SetRangeUser(0.4, 1.6)

def drawCMS(onTop=False):
    #text='#bf{CMS} #it{Simulation}  H#rightarrow#gamma#gamma'
    text='#bf{CMS} #scale[0.75]{#it{Simulation Preliminary}  H#rightarrow#gamma#gamma}'
    latex = TLatex()
    latex.SetNDC()
    latex.SetTextFont(42)
    latex.SetTextSize(0.05)
    latex.DrawLatex(0.1, 0.85 if not onTop else 0.93, text)
    
def drawEnPu(pileup=None, lumi=None):
    latex = TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.046)
    latex.SetTextColor(1)
    latex.SetTextFont(42)
    latex.SetTextAlign(31)
    tex = '(13 TeV)'
    if pileup: tex += ', {0} PU'.format(pileup)
    if lumi: tex = '{0} '.format(lumi) + tex
    latex.DrawLatex(0.95, 0.93, tex)

def drawEnYear(pileup=None, year=None):
    latex = TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.046)
    latex.SetTextColor(1)
    latex.SetTextFont(42)
    latex.SetTextAlign(31)
    tex = '13 TeV'
    if pileup: tex += ', {0} PU'.format(pileup)
    if year: tex = tex + ' ({0})'.format(year) 
    latex.DrawLatex(0.95, 0.93, tex)
