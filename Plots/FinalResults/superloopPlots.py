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
obspval_125 = r.TGraphAsymmErrors()
mh_h = r.TH1F("mh","mh",50,-3,3)
mu_h = r.TH1F("mu","mu",50,-3,3)
pval_h = r.TH1F("pval","pval",50,-0.06,0.06)
c = r.TCanvas()
r.gStyle.SetOptStat(111111)
list1=[]
index_vec=[]
mh_vec=[]
mu_vec=[]
obs_vec=[]
exp_125_vec=[]
exp_vec=[]

def drawSigmas(counter,c) :
  # draw sigma lines
  sigmas=[1,2,3,4,5,6]
  lines=[]
  labels=[]
  for i,sig in enumerate(sigmas):
    y = r.RooStats.SignificanceToPValue(sig)
    print "consider sigma " , i, " = ", sig ," sigma ie" , y ," in pval ","  counter " , counter
    lines.append(r.TLine(0,y,counter,y))
    #else : 
    #axmin = float(options.xaxis.split(',')[0])
    #axmax = float(options.xaxis.split(',')[1])
    #lines.append(r.TLine(axmin,y,axmax,y))
  
    lines[i].SetLineWidth(2)
    lines[i].SetLineStyle(2)
    lines[i].SetLineColor(13) # greay Lines 
    labels.append(r.TLatex(float(counter), y * 0.8, "%d #sigma" % (i+1)))
    labels[i].SetTextColor(13)
    labels[i].SetTextAlign(11);
    #if y<=mg.GetYaxis().GetXmax() and y>=mg.GetYaxis().GetXmin():
    #c.cd()
    lines[i].Draw('SAME')
    labels[i].Draw('SAME')
    c.SaveAs("test.pdf")

d = open(file0)
countermh=0
countermu=0
pexpval=0.
pobsval=0.
counter=-1
for line in d.readlines():
    if line.startswith('#'): continue
    if line=='\n': continue
    words=line.split(' ')
    #print "already considered", list1
    if (len(index_vec)-1)<int(words[1]) :
      index_vec.append(int(words[1]))
      mh_vec.append(-1.)
      mu_vec.append(-1.)
      obs_vec.append(-1.)
      exp_125_vec.append(-1.)
      exp_vec.append(-1.)
    #print "check if " ,words[1] , " is in list1" , (words[1] in list1)
    if (words[0]+words[1]) in list1 : continue
    list1.append(words[0]+words[1])
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
      mh_vec[int(words[1])]=mhvalue
      #print words[1], "MH: ",mherrorsLo ,", ", mhvalue ,", ", mherrorsHi, "deltaMh/sigma ",dmH
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
      mu_vec[int(words[1])]=muvalue
      #print words[1], "MU: ",muerrorsLo ,", ", muvalue ,", ", muerrorsHi, "dmu/sigma ", dmu
      countermu+=1
    if words[0]=="Expected_mh125_13TeV":
      exppval.SetPoint(int(words[1]),int(words[1]),float(words[2])  )
      pexpval =float(words[2]) 
      exp_125_vec[int(words[1])]= pexpval
    if words[0]=="Observed_13TeV":
      obspval.SetPoint(int(words[1]),int(words[1]),float(words[2])  )
      #if obspval_125.SetPoint(int(words[1]),int(words[1]),float(words[2])  )
      pobsval =float(words[2])
      dpval=pexpval - pobsval
      pval_h.Fill(dpval)
      obs_vec[int(words[1])]= pobsval
      #print words[1]," PVAL obs ", pobsval, ", exp ", pexpval, ", dpval ", dpval, " counter " , counter
      counter=counter+1


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
obspval.SetMaximum(0.2)
obspval.SetMinimum(10e-10)
obspval.GetYaxis().SetTitle("Observed p value")
c.SetLogy(1)
#c.SetGrid(0)
#r.gStyle.SetGridStyle(0)

obspval.Draw("APL")
#drawSigmas(counter,c)
sigmas=[1,2,3,4,5,6]
lines=[]
labels=[]
for i,sig in enumerate(sigmas):
  y = r.RooStats.SignificanceToPValue(sig)
  print "consider sigma " , i, " = ", sig ," sigma ie" , y ," in pval ","  counter " , counter
  lines.append(r.TLine(0,y,counter,y))
  #else : 
  #axmin = float(options.xaxis.split(',')[0])
  #axmax = float(options.xaxis.split(',')[1])
  #lines.append(r.TLine(axmin,y,axmax,y))

  lines[i].SetLineWidth(2)
  lines[i].SetLineStyle(2)
  lines[i].SetLineColor(13) # greay Lines 
  labels.append(r.TLatex(float(counter), y * 0.8, "%d #sigma" % (i+1)))
  labels[i].SetTextColor(13)
  labels[i].SetTextAlign(11);
  #if y<=mg.GetYaxis().GetXmax() and y>=mg.GetYaxis().GetXmin():
  #c.cd()
  lines[i].Draw('SAME')
  labels[i].Draw('SAME')
  c.SaveAs("test.pdf")

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
#exppval.GetYaxis().SetRangeUser(0,0.0001)
exppval.SetMaximum(0.2)
exppval.SetMinimum(10e-10)
exppval.Draw("ALP")
#drawSigmas(counter,c)
sigmas=[1,2,3,4,5,6]
lines=[]
labels=[]
for i,sig in enumerate(sigmas):
  y = r.RooStats.SignificanceToPValue(sig)
  print "consider sigma " , i, " = ", sig ," sigma ie" , y ," in pval ","  counter " , counter
  lines.append(r.TLine(0,y,counter,y))
  #else : 
  #axmin = float(options.xaxis.split(',')[0])
  #axmax = float(options.xaxis.split(',')[1])
  #lines.append(r.TLine(axmin,y,axmax,y))

  lines[i].SetLineWidth(2)
  lines[i].SetLineStyle(2)
  lines[i].SetLineColor(13) # greay Lines 
  labels.append(r.TLatex(float(counter), y * 0.8, "%d #sigma" % (i+1)))
  labels[i].SetTextColor(13)
  labels[i].SetTextAlign(11);
  #if y<=mg.GetYaxis().GetXmax() and y>=mg.GetYaxis().GetXmin():
  #c.cd()
  lines[i].Draw('SAME')
  labels[i].Draw('SAME')
  c.SaveAs("test.pdf")
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

print "###################################"
print "index_vec"
print index_vec
print "mh_vec"
print mh_vec
print "mu_vec"
print mu_vec
print "obs_vec"
print obs_vec
print "exp_vec"
print exp_vec
print "exp_125_vec"
print exp_125_vec
print "###################################"

#f = r.TFile( 'test.root', 'recreate' )
f = r.TFile( file0.replace("txt","root"), 'recreate' )
tree = r.TTree("t1","t1") 
maxn = len(index_vec)
lindex = array( 'i', [ 0 ] )
lmh = array( 'f', [ 0. ] )
lmu = array( 'f', [ 0. ] )
lexp_125 = array( 'f', [ 0. ] )
lexp_125_sigma = array( 'f', [ 0. ] )
lobs = array( 'f', [ 0. ] )
lobs_sigma = array( 'f', [ 0. ] )
tree.Branch( 'index', lindex, 'index/I' )
tree.Branch( 'mh', lmh, 'mh/F' )
tree.Branch( 'mu', lmu, 'mu/F' )
tree.Branch( 'exp_125', lexp_125, 'exp_125/F' )
tree.Branch( 'exp_125_sigma', lexp_125_sigma, 'exp_125_sigma/F' )
tree.Branch( 'obs', lobs, 'obs/F' )
tree.Branch( 'obs_sigma', lobs_sigma, 'obs_sigma/F' )

for i in range(maxn):
  lindex[0] = int(index_vec[i])
  lmh[0] = mh_vec[i]
  lmu[0] = mu_vec[i]
  lexp_125[0] = exp_125_vec[i]
  lexp_125_sigma[0] = r.RooStats.PValueToSignificance(exp_125_vec[i])
  lobs[0] = obs_vec[i]
  lobs_sigma[0] = r.RooStats.PValueToSignificance(obs_vec[i])
  print "exp_125 : ", lexp_125[0] , " ie " , lexp_125_sigma[0] ," sigma , obs " , lobs[0] , " ie " , lobs_sigma[0] ," sigma"
  tree.Fill()

f.Write()
f.Close()
