#!/usr/bin/env python

# Usual reasons to love python imports
import os
import sys
import shlex
from array import array
import ROOT as r

file0="itLedger_superloopTest.txt"
if (len(sys.argv) >1) : file0=sys.argv[1]
mh = r.TGraphAsymmErrors()
mu = r.TGraphAsymmErrors()
exppval = r.TGraphAsymmErrors()
obspval = r.TGraphAsymmErrors()
mh_h = r.TH1F("mh","mh",50,-3,3)
mu_h = r.TH1F("mu","mu",50,-3,3)
pval_h = r.TH1F("pval","pval",50,-0.06,0.06)
c = r.TCanvas()
r.gStyle.SetOptStat(111111)

d = open(file0)
countermh=0
countermu=0
pexpval=0.
pobsval=0.
for line in d.readlines():
    if line.startswith('#'): continue
    if line=='\n': continue
    words=line.split(' ')
    if words[0]=="mh":
      mhvalue = (float(words[2]))
      mhvalueX =(float(countermh))
      mherrorsLo = (float(words[3]))
      mherrorsHi = (float(words[4]))
      mherrorsXLo = (0.)
      mherrorsXHi = (0.)
      mh.SetPoint(int(words[1]),mhvalueX,mhvalue)
      mh.SetPointError(int(words[1]),mherrorsXLo,mherrorsXHi,mherrorsLo,mherrorsHi)
      dmH=(mhvalue -125.)/(mherrorsLo+mherrorsHi)
      mh_h.Fill(dmH)
      print words[1], "MH: ",mherrorsLo ,", ", mhvalue ,", ", mherrorsHi, "deltaMh/sigma ",dmH
      countermh+=1
    if words[0]=="mu":
      muvalue = (float(words[2]))
      muvalueX =(float(countermu))
      muerrorsLo = (float(words[3]))
      muerrorsHi = (float(words[4]))
      muerrorsXLo = (0.)
      muerrorsXHi = (0.)
      #if (muvalue == 0) : continue
      mu.SetPoint(int(words[1]),muvalueX,muvalue)
      mu.SetPointError(int(words[1]),muerrorsXLo,muerrorsXHi,muerrorsLo,muerrorsHi)
      dmu=(muvalue -1.)/(muerrorsLo+muerrorsHi)
      mu_h.Fill(dmu)
      print words[1], "MU: ",muerrorsLo ,", ", muvalue ,", ", muerrorsHi, "dmu/sigma ", dmu
      countermu+=1
    if words[0]=="Expected_mh125_13TeV":
      exppval.SetPoint(int(words[1]),int(words[1]),float(words[2])  )
      pexpval =float(words[2]) 
    if words[0]=="Observed_13TeV":
      obspval.SetPoint(int(words[1]),int(words[1]),float(words[2])  )
      pobsval =float(words[2])
      dpval=pexpval - pobsval
      pval_h.Fill(dpval)
      print words[1]," PVAL obs ", pobsval, ", exp ", pexpval, ", dpval ", dpval


l = r.TLine(0.,125,countermh+1,125)
l.SetLineColor(13)
l.SetLineStyle(1)
l.SetLineWidth(2)
mh.SetMarkerColor(r.kRed)
#mh.SetMarkerSize(2)
mh.SetMarkerStyle(20)
mh.SetLineColor(r.kRed)
mh.SetLineWidth(2)
mh.GetXaxis().SetRangeUser(-1,countermh+1)
mh.SetName("MH")
mh.Draw("AP")
mh.GetYaxis().SetTitle("mH")
#c.SetGrid(0)
c.SetLogy(0)
#r.gStyle.SetGridStyle(0)
l.Draw()
c.SaveAs("superloopPlotMH.pdf")
c.SaveAs("superloopPlotMH.png")

l = r.TLine(0.,1,countermu+1,1)
l.SetLineColor(13)
l.SetLineStyle(1)
l.SetLineWidth(2)
mu.SetMarkerColor(r.kBlue)
#mu.SetMarkerSize(2)
mu.SetMarkerStyle(20)
mu.SetLineColor(r.kBlue)
mu.SetLineWidth(2)
mu.SetName("MU")
mu.GetXaxis().SetRangeUser(-1,countermu+1)
mu.GetYaxis().SetTitle("mu")
c.SetLogy(0)
#c.SetGrid(0)
#r.gStyle.SetGridStyle(0)
mu.Draw("AP")
l.Draw()
c.SaveAs("superloopPlotMU.pdf")
c.SaveAs("superloopPlotMU.png")

c.Clear()
#c.SetGrid(0)
#r.gStyle.SetGridStyle(0)
obspval.SetMarkerColor(r.kGreen)
#obspval.SetMarkerSize(2)
obspval.SetMarkerStyle(20)
obspval.SetLineColor(r.kGreen)
obspval.SetLineWidth(2)
obspval.GetXaxis().SetRangeUser(-1,countermu+1)
obspval.GetYaxis().SetTitle("Observed p value")
c.SetLogy(1)
#c.SetGrid(0)
#r.gStyle.SetGridStyle(0)

obspval.Draw("APL")
c.SaveAs("superloopPlotobspval.pdf")
c.SaveAs("superloopPlotobspval.png")

c.Clear()
#c.SetGrid(0)
#r.gStyle.SetGridStyle(0)

c.SetLogy(1)
exppval.SetMarkerColor(r.kGreen)
exppval.SetLineStyle(2)
exppval.SetMarkerStyle(24)
exppval.SetLineColor(r.kGreen)
exppval.SetLineWidth(2)
exppval.GetYaxis().SetTitle("expected(125) p value")
exppval.GetYaxis().SetRangeUser(0,0.0001)
exppval.Draw("ALP")
c.SaveAs("superloopPlotexppval.pdf")
c.SaveAs("superloopPlotexppval.png")

c.Clear()
c.SetLogy(0)
mh_h.Draw()
c.SaveAs("superloopPlotDmH.pdf")
c.SaveAs("superloopPlotDmH.png")

c.Clear()
c.SetLogy(0)
mu_h.Draw()
c.SaveAs("superloopPlotDmu.pdf")
c.SaveAs("superloopPlotDmu.png")

c.Clear()
c.SetLogy(0)
pval_h.Draw()
c.SaveAs("superloopPlotDpval.pdf")
c.SaveAs("superloopPlotDpval.png")



c.Clear()
c = r.TCanvas("","",1000,2000)
c.Divide(0,4)
c.cd(1)
c.SetGrid(0)
r.gStyle.SetGridStyle(1)
mh.Draw("AP")
l.DrawLine(0.,125,countermh+1,125)
c.cd(2)
c.SetGrid(0)
r.gStyle.SetGridStyle(1)
mu.Draw("A P")
l.DrawLine(0.,1,countermu+1,1)
c.cd(3)
c.SetGrid(0)
c.SetLogy()
r.gStyle.SetGridStyle(1)
obspval.Draw("APL")
c.cd(4)
c.SetGrid(0)
r.gStyle.SetGridStyle(1)
c.SetLogy(1)
exppval.Draw("APL")
c.SaveAs("superloopPlot.pdf")
c.SaveAs("superloopPlot.png")


#raw_input("Looks ok?") 
