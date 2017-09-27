#!/usr/bin/env python

# Usual reasons to love python imports
import os
import sys
import shlex
import array 
from math import sqrt

from optparse import OptionParser
parser = OptionParser()
parser.add_option("-d","--datfile",dest="datfile",help="Read from datfile")
parser.add_option("-f","--file",dest="files",default=[],action="append",help="Add a file")
parser.add_option("-o","--outname",dest="outname",help="Name of output pdf/png/C")
parser.add_option("-c","--color",dest="colors",default=[],action="append",help="Set color")
parser.add_option("-s","--style",dest="styles",default=[],action="append",help="Set style")
parser.add_option("-w","--width",dest="widths",default=[],action="append",help="Set width")
parser.add_option("-n","--name",dest="names",default=[],action="append",help="Set name")
parser.add_option("-g","--gname",dest="groupnames",default=[],action="append",help="Set (group) name -for channel compat")
parser.add_option("","--groups",dest="groups",default=1,type="int",help="Set Number of groups")
parser.add_option("-t","--text",dest="text",type="string",default="",help="Add Text")
parser.add_option("","--MHtext",dest="MHtext",default=[],action='append',help="Add more text (eg mh=XXX for chan-compat plots etc). Modify NDC position by ruing  X:Y:text")
parser.add_option("","--blacklistMH",dest="blacklistMH",default=[],action='append',type='float',help="Kill an MH value (limits, pvals, Mu vs MH etc)")

parser.add_option("","--xlab",dest="xlab",type="string",default="",help="Label for x-axis")
parser.add_option("","--xvar",dest="xvar",type="string",default=[],action="append",help="Branch in TTree to pick up as 'x'")
parser.add_option("-e","--expected",dest="expected",default=False,action="store_true",help="Expected only")
parser.add_option("-m","--method",dest="method",type="string",help="Method to run")
parser.add_option("-l","--legend",dest="legend",type="string",help="Legend position - x1,y1,x2,y2")
parser.add_option("--box",dest="box",type="string",help="Legend position - x1,y1,x2,y2,TColor")
parser.add_option("-x","--xaxis",dest="xaxis",type="string",help="x-axis range - x1,x2")
parser.add_option("-y","--yaxis",dest="yaxis",type="string",help="y-axis range - y1,y2")
parser.add_option("","--xbinning",dest="xbinning",type="string",help="force x binning (b,l,h)")
parser.add_option("","--ybinning",dest="ybinning",type="string",help="force y binning (b,l,h)")
parser.add_option("","--groupentry",dest="groupentry",type="string",help="In ch compat, put per XXX (channel,group,etc)")
parser.add_option("","--canv",dest="canv",type="string",default="700,700",help="Canvas size x,y")
parser.add_option("","--chcompLine",dest="chcompLine",type="int",help="For ChannelComp plot put line here splitting two year")
parser.add_option("","--chcompShift",dest="chcompShift",type="float",help="For ChannelComp Asimov - shift to this value")
parser.add_option("","--do1sig",dest="do1sig",default=False,action="store_true",help="For ChannelComp plot only 1 sigma errors")
parser.add_option("","--noComb",dest="noComb",default=False,action="store_true",help="Don't assume the first line is the combined one")
parser.add_option("","--mhval",dest="mhval",default="125.09",help="Don't assume the first line is the combined one")
parser.add_option("","--smoothNLL",dest="smoothNLL",default=False,action="store_true",help="Smooth 1D likelihood scans")
parser.add_option("","--shiftNLL",dest="shiftNLL",type="float",help="Correct NLL to this value")
parser.add_option("","--correctNLL",dest="correctNLL",default=False,action="store_true",help="Correct NLL (occasionally required for failed jobs)")
parser.add_option("","--cleanNLL",dest="cleanNll",default=False,action="store_true",help="Try to remove pike from NLL curve")
parser.add_option("","--addSM",dest="addSM",default=False,action="store_true",help="Add SM Diamond to 2D plot")
parser.add_option("","--limit",dest="limit",default=False,action="store_true",help="Do limit plot")
parser.add_option("","--pval",dest="pval",default=False,action="store_true",help="Do p-value plot")
parser.add_option("","--maxlh",dest="maxlh",default=False,action="store_true",help="Do best fit mu plot")
parser.add_option("","--mh",dest="mh",default=False,action="store_true",help="Do NLL mass scan plot")
parser.add_option("","--mu",dest="mu",default=False,action="store_true",help="Do NLL mu scan plot")
parser.add_option("","--pdf",dest="pdf",default=False,action="store_true",help="Do NLL pdf scan plot")
parser.add_option("","--rv",dest="rv",default=False,action="store_true",help="Do NLL rv scan plot")
parser.add_option("","--rf",dest="rf",default=False,action="store_true",help="Do NLL rf scan plot")
parser.add_option("","--draw2dhist",dest="draw2dhist",default=False,action="store_true",help="Ue 2D hist drawing for the 2D NLL")
parser.add_option("","--get2dhist",dest="get2dhist",default="",help="Get a h2d from the file, separate with : for name of hist (default is h2d)")
parser.add_option("","--bf2d",dest="bf2d",default="",help="Put the best fit point here, dont read from ROOT file. use x,y")
parser.add_option("","--mumh",dest="mumh",default=False,action="store_true",help="Do NLL mu vs mh scan plot")
parser.add_option("","--rvrf",dest="rvrf",default=False,action="store_true",help="Do NLL rv vs rf scan plot")
parser.add_option("","--cvcf",dest="cvcf",default=False,action="store_true",help="Do NLL cv vs cf scan plot")
parser.add_option("","--kglukgam",dest="kglukgam",default=False,action="store_true",help="Do NLL kgluon vs kgamma scan plot")
parser.add_option("","--xdm",dest="xdm",default=False,action="store_true",help="Do NLL x vs delta(m) degenerate")
parser.add_option("","--zmax",dest="zmax",default=10.,type='float',help="Maximum on 2D plots for the Z axis")
parser.add_option("","--mpdfchcomp",dest="mpdfchcomp",default=False,action="store_true",help="Do MultiPdf channel compatbility plot")
parser.add_option("","--perprocchcomp",dest="perprocchcomp",default=False,action="store_true",help="Do PerProc channel compatbility plot")
parser.add_option("","--percatchcomp",dest="percatchcomp",default=False,action="store_true",help="Do per cat modifications (use with --perprocchcomp)")
parser.add_option("","--mpdfmaxlh",dest="mpdfmaxlh",default=False,action="store_true",help="Do MultiPdf best fit mu as a function of MH plot")
parser.add_option("","--stxs",dest="stxs",default=False,action="store_true",help="Do plots for simplified template cross-section processes")
parser.add_option("-v","--verbose",dest="verbose",default=False,action="store_true")
parser.add_option("-b","--batch",dest="batch",default=False,action="store_true")
parser.add_option("--it",dest="it",type="string",help="if using superloop, index of iteration")
parser.add_option("--itLedger",dest="itLedger",type="string",help="ledger to keep track of values of each iteration if using superloop")
parser.add_option("--specifyX",dest="specifyX",type="string",help="use a specific variable name in mu plots (eg r_Untagged_Tag_0)")
parser.add_option("--paperStyle",dest="paperStyle",default=False,action="store_true",help="Make plots in paper style (without preliminary etc)")
(options,args)=parser.parse_args()

print "[INFO] Processing Files :"
print " --> raw input :", options.files
if (len(options.files)==1) : options.files=options.files[0].split(",")
print " --> output  :", options.files

# Required for back compatbility and current compatibility it seems
if options.limit: options.method='limit'
if options.pval: options.method='pval'
if options.maxlh: options.method='maxlh'
if options.mh: options.method='mh'
if options.mu: options.method='mu'
if options.pdf: options.method='pdf'
if options.rv: options.method='rv'
if options.rf: options.method='rf'
if options.mumh: options.method='mumh'
if options.rvrf: options.method='rvrf'
if options.cvcf: options.method='cvcf'
if options.kglukgam: options.method='kglukgam'
if options.xdm: options.method='xdm'
if options.mpdfchcomp: options.method='mpdfchcomp'
if options.perprocchcomp: options.method='perprocchcomp'
if options.mpdfmaxlh: options.method='mpdfmaxlh'
if not options.outname: options.outname=options.method

allowed_methods=['pval','limit','maxlh','mh','mu','pdf','mumh','rv','rf','rvrf','cvcf','kglukgam','xdm','mpdfchcomp','perprocchcomp','mpdfmaxlh']
if not options.datfile and options.method not in allowed_methods:
  print 'Invalid method : ' , options.method , '. Must set one of: ', allowed_methods
  sys.exit()

import ROOT as r
outf = r.TFile('%s.root'%options.outname,'RECREATE')

# Load and use the Hgg Paper style
#r.gROOT.ProcessLine(".x hggPaperStyle.C")

if options.batch: r.gROOT.SetBatch()
r.gStyle.SetOptStat(0)

def is_float_try(str):
    try:
      float(str)
      return True
    except ValueError:
      return False
# very fine-grained colour palettee
def set_palette(ncontours=999):
    style=2
    if (style==1):
     # default palette, looks cool
     stops = [0.00, 0.34, 0.61, 0.84, 1.00]
     red   = [0.00, 0.00, 0.77, 0.85, 0.90]
     green = [0.00, 0.81, 1.00, 0.20, 0.00]
     blue  = [0.51, 1.00, 0.12, 0.00, 0.00]

     st = array.array('d', stops)
     re = array.array('d', red)
     gr = array.array('d', green)
     bl = array.array('d', blue)
    elif (style==3):
     
     red   = [ 0.00, 0.90, 1.00] 
     blue  = [ 1.00, 0.50, 0.00] 
     green = [ 0.00, 0.00, 0.00] 
     stops = [ 0.00, 0.50, 1.00] 
     st = array.array('d', stops)
     re = array.array('d', red)
     gr = array.array('d', green)
     bl = array.array('d', blue)

    elif (style==2):
     # blue palette, looks cool
     #stops = [0.00, 0.14, 0.34, 0.61, 0.84, 1.00]
     #red   = [1.00, 1.00, 1.00, 1.00, 1.00, 1.00]
     #green = [1.00, 1.00, 1.00, 1.00, 1.00, 1.00]
     #blue  = [1.00, 0.80, 0.6, 0.4, 0.2, 1.0]
     stops = [0.00,1.00 ]
     red   = [1.00,0.220 ]
     green = [1.00,0.27 ]
     blue  = [1.00,0.57 ]

     st = array.array('d', stops)
     re = array.array('d', red)
     gr = array.array('d', green)
     bl = array.array('d', blue)

    npoints = len(st)
    r.TColor.CreateGradientColorTable(npoints, st, re, gr, bl, ncontours)
    r.gStyle.SetNumberContours(ncontours)

# set defaults for colors etc.
if len(options.colors):
  for i in range(len(options.colors)): 
  	if "r.k" not in options.colors[i]: options.colors[i]=int(options.colors[i])
	else :
	  lcolst = options.colors[i].split(".")[1]
	  add = 0
	  if "+" in lcolst: 
	  	add=int(lcolst.split("+")[1])
		lcolst = lcolst.split("+")[0]
	  if "-" in lcolst: 
	  	add=int(lcolst.split("-")[1])
		lcolst = lcolst.split("-")[0]
	  lcol = int(getattr(r,lcolst))
	  options.colors[i]=lcol+add
while len(options.files)>len(options.colors): options.colors.append(1)
while len(options.files)>len(options.styles): options.styles.append(1)
while len(options.files)>len(options.widths): options.widths.append(1)
while len(options.files)>len(options.names): options.names.append('')
while len(options.files)>len(options.xvar): options.xvar.append("")
while len(options.files)>len(options.groupnames): options.groupnames.append("")

# mh text options, this is just an excuse to dump some text somewhere
mhTextX = []
mhTextY = []
mhTextSize = []
MHtexts = []
for MH in options.MHtext:
  mhtextoptions = MH.split(":")
  MHtexts.append(mhtextoptions[2])
  mhTextX.append(float(mhtextoptions[0]))
  mhTextY.append(float(mhtextoptions[1]))
  if len(mhtextoptions)>3:
    mhTextSize.append(float(mhtextoptions[3]))
  else:
    mhTextSize.append(-1)

# make canvas and dummy hist
#canv = r.TCanvas("c","c",int(options.canv.split(',')[0]),int(options.canv.split(',')[1]))
#canv = r.TCanvas("c","c",900,750) # use the default canvas style
canv = r.TCanvas("c","c") # use the default canvas style
canv.SetTicks(1,1)

if (options.xaxis):
  if ("," in options.xaxis): options.xaxis = options.xaxis.split(',')
if not options.xaxis: dummyHist = r.TH1D("dummy","",1,115,135)
else: 
  dummyHist =  r.TH1D("dummy","",1,float(options.xaxis[0]),float(options.xaxis[1]))
dummyHist.GetXaxis().SetTitle('m_{H} (GeV)')
dummyHist.GetXaxis().SetTitleSize(0.05)
dummyHist.GetXaxis().SetTitleOffset(0.9)

# make a helful TLatex box
lat = r.TLatex()
lat.SetTextFont(42)
lat.SetTextSize(0.045)
lat.SetLineWidth(2)
lat.SetTextAlign(11)
lat.SetNDC()
##########################

# Draw the usual propaganda 
def drawGlobals(canv,shifted="False"):

  # draw text 
  
  if (shifted=="True"):
   #print "AM I SHIFTED ? YES"
   #lat.DrawLatex(0.129+0.03,0.93,"CMS Unpublished H#rightarrow#gamma#gamma")
   #lat.DrawLatex(0.129+0.03,0.93,"CMS H#rightarrow#gamma#gamma")
   if not options.paperStyle: lat.DrawLatex(0.129+0.085,0.93,"#bf{CMS} #scale[0.75]{#it{Preliminary}}")
   else:
     lat.SetTextSize(0.07)
     lat.DrawLatex(0.129+0.085,0.93,"#bf{CMS}")
   lat.SetTextSize(0.045)
   lat.DrawLatex(0.129+0.085+0.04,0.85,"H#rightarrow#gamma#gamma")
   #lat.DrawLatex(0.71,0.92,options.text)
   lat.DrawLatex(0.7,0.93,options.text)

  elif shifted=="2D":
   #print "AM I SHIFTED ? 2D"
   lat.SetTextSize(0.05)
   if not options.paperStyle: lat.DrawLatex(0.1,0.92,"#bf{CMS} #scale[0.75]{#it{Preliminary}}")
   else: lat.DrawLatex(0.1,0.92,"#bf{CMS}")
   #lat.DrawLatex(0.129+0.04,0.85,"H#rightarrow#gamma#gamma")
   #lat.DrawLatex(0.13,0.85,"H#rightarrow#gamma#gamma")
   #lat.SetTextSize(0.07)
   lat.SetTextSize(0.045)
   lat.DrawLatex(0.61,0.92,options.text)

  else:
   #print "AM I SHIFTED ? NO"
   #lat.DrawLatex(0.129,0.93,"CMS Unpublished H#rightarrow#gamma#gamma")
   #lat.DrawLatex(0.129,0.93,"CMS H#rightarrow#gamma#gamma")
   #lat.DrawLatex(0.173,0.85,"#splitline{#bf{CMS}}{#it{Preliminary}}")
   #lat.DrawLatex(0.129,0.93,"#bf{CMS} #scale[0.75]{#it{Preliminary}}")
   lat.SetTextSize(0.05)
   if not options.paperStyle: lat.DrawLatex(0.1,0.92,"#bf{CMS} #scale[0.75]{#it{Preliminary}}")
   else: 
     lat.SetTextSize(0.07)
     lat.DrawLatex(0.1,0.92,"#bf{CMS}")
   #lat.DrawLatex(0.129+0.04,0.85,"H#rightarrow#gamma#gamma")
   lat.SetTextSize(0.05)
   lat.DrawLatex(0.13,0.83,"H#rightarrow#gamma#gamma") #LHCP17
   #lat.DrawLatex(0.12,0.82,"H#rightarrow#gamma#gamma")
   #lat.DrawLatex(0.77,0.83,"H#rightarrow#gamma#gamma") #used only for new MuScan
   #lat.SetTextSize(0.07)
   lat.SetTextSize(0.045)
   lat.DrawLatex(0.69,0.92,options.text)

  for mi,MH in enumerate(MHtexts):
    if mhTextSize[mi]>0:
      lat.SetTextSize(mhTextSize[mi])
    lat.DrawLatex(mhTextX[mi],mhTextY[mi],MH)

def cleanSpikes1D(rfix):

 # cindex is where deltaNLL = 0 (pre anything)
 MAXDER = 1.0
 #for i,r,m in enumerate(rfix):
 for i,r in enumerate(rfix):
   if abs(r[1]) <0.001: cindex = i

 lhs = rfix[0:cindex]; lhs.reverse()
 rhs= rfix[cindex:-1]
 keeplhs = []
 keeprhs = []

 #for i,lr,m in enumerate(lhs): 
 for i,lr in enumerate(lhs): 
   if i==0: 
   	prev = lr[1]
	idiff = 1
   if abs(lr[1]-prev) > MAXDER :
   	idiff+=1
   	continue 
   keeplhs.append(lr)
   prev = lr[1]
   idiff=1
 keeplhs.reverse()

 #for i,rr,m in enumerate(rhs):
 for i,rr in enumerate(rhs):
   if i==0: 
   	prev = rr[1]
	idiff = 1
   if abs(rr[1]-prev) > MAXDER : 
   	idiff+=1
   	continue 
   keeprhs.append(rr)
   prev = rr[1]
   idiff=1
 
 rfix = keeplhs+keeprhs
 
 rkeep = []
 #now try to remove small jagged spikes
 #for i,r,m in enumerate(rfix):
 for i,r in enumerate(rfix):
   if i==0 or i==len(rfix)-1: 
   	rkeep.append(r)
   	continue
   tres = [rfix[i-1][1],r[1],rfix[i+1][1]]
   mean = float(sum(tres))/3.
   mdiff = abs(max(tres)-min(tres))
   if abs(tres[1] - mean) > 0.6*mdiff :continue
   rkeep.append(r)
 return rkeep

# Plot 1 - P-values plot 
def pvalPlot(allVals):
  
  canv.Clear()
  canv.SetLogy(True)

  if options.verbose: print 'Plotting pvalue...'
  mg = r.TMultiGraph()
  if not options.legend: leg = r.TLegend(0.14,0.30,0.4,0.7)
  #if not options.legend: leg = r.TLegend(0.6,0.35,0.89,0.45)
  else:
    options.legend[-1]=options.legend[-1].replace("\n","")
    leg = r.TLegend(float(options.legend[0]),float(options.legend[1]),float(options.legend[2]),float(options.legend[3]))
  #leg.SetFillColor(0)
  leg.SetBorderSize(0)
  # make graphs from values
  for k, values in enumerate(allVals):
    minpvalue=99999.
    minpvalueX=99999.
    pvalat125=999999.
    graph = r.TGraph()
    p=0
    for j in range(len(values)):
      if (values[j][1]<10e-150): continue
      graph.SetPoint(p,values[j][0],values[j][1])
      p=p+1
      if (minpvalue > values[j][1]): 
        minpvalue = values[j][1]
        minpvalueX =values[j][0]
      if options.verbose or abs(values[j][0]-125.09)<0.1 or  values[j][0]==126.0 : 
        print options.names[k] ,' at ', values[j][0], " signif ",  r.RooStats.PValueToSignificance(values[j][1])
        pvalat125=values[j][1]
      #print "debug minpval  for ",options.names[k], " at ", values[j][0], " ", minpvalue, "   " , r.RooStats.PValueToSignificance(minpvalue), "values[j][1] " , values[j][1], " ", r.RooStats.PValueToSignificance(values[j][1])
    
  #  with open(options.itLedger, "a") as myfile:
  #      myfile.write("%s %f %f\n" % ( (options.names[k].replace(" ","_"))+" "+options.it, minpvalue,minpvalueX ))
  #      if ("Obs" in options.names[k] ) :
  #        myfile.write("%s %f %f\n" % ( (options.names[k].replace(" ","_"))+"_at125"+" "+options.it, pvalat125,125. ))

    graph.SetLineColor(int(options.colors[k]))
    graph.SetLineStyle(int(options.styles[k]))
    graph.SetLineWidth(int(options.widths[k]))
    if options.names[k]!="-1": leg.AddEntry(graph,options.names[k],'L')
    mg.Add(graph)
    mg.Draw("A")
    canv.Print("debug%d.pdf"%j)
    
  # draw dummy hist and multigraph
  dummyHist.GetYaxis().SetTitle('Local p-value')
  dummyHist.GetYaxis().SetTitleSize(0.05)
  mg.Draw("A")
  canv.Print("debug.pdf")
  if (options.xaxis) :
      print mg.GetXaxis()
      #mg.GetXaxis().SetLimits(float(options.xaxis[0]),float(options.xaxis[1]))
      dummyHist.SetAxisRange(float(options.xaxis[0]),float(options.xaxis[1]))
      #canv.Modified()
      print mg.GetXaxis().GetXmin() 
  if not options.yaxis:
    print "LC DEBUG A mg.GetYaxis().GetXmin() ", mg.GetYaxis().GetXmin()
    print "LC DEBUG A mg.GetYaxis().GetXmax() ", mg.GetYaxis().GetXmax()
    dummyHist.SetMinimum(mg.GetYaxis().GetXmin())
    dummyHist.SetMaximum(1e0)
  else:
    print "LC DEBUG B"
    dummyHist.SetMinimum(float(options.yaxis.split(',')[0]))
    dummyHist.SetMaximum(float(options.yaxis.split(',')[1]))
    #print "y1,y2", options.yaxis.split(',')[0], " , ", options.yaxis.split(',')[1]
  print "DEBUG SimultaneousFit A"  
  dummyHist.SetLineColor(0)
  dummyHist.SetStats(0)
  dummyHist.Draw("AXIS")
  mg.Draw("L")
  dummyHist.Draw("AXIGSAME")

  print "DEBUG SimultaneousFit b"  
  # draw sigma lines
  #sigmas=[1,2,3,4,5,6]
  sigmas=[1,2,3,4,5,6,7,8,9,10]
  lines=[]
  labels=[]
  for i,sig in enumerate(sigmas):
    y = r.RooStats.SignificanceToPValue(sig)
    if options.verbose: print sig, y
    if not options.xaxis:  lines.append(r.TLine(115,y,135,y))
    else : 
        axmin = float(options.xaxis[0])
        axmax = float(options.xaxis[1])
        #print "set line at  " ,axmin, " " , axmax
        lines.append(r.TLine(axmin,y,axmax,y))

    lines[i].SetLineWidth(2)
    lines[i].SetLineStyle(2)
    lines[i].SetLineColor(13) # greay Lines 
    labels.append(r.TLatex(132+1, y * 1.1, "%d #sigma" % (i+1)))
    labels[i].SetTextColor(13)
    labels[i].SetTextAlign(11);
    if not options.yaxis:
      #if y<=mg.GetYaxis().GetXmax() and y>=mg.GetYaxis().GetXmin():
      #  lines[i].Draw('SAME')
      #  labels[i].Draw('SAME')
      lines[i].Draw('SAME')
      labels[i].Draw('SAME')
    else:
      if y<=float(options.yaxis.split(',')[1]) and y>=float(options.yaxis.split(',')[0]):
        lines[i].Draw('SAME')
        labels[i].Draw('SAME')
  # draw legend
  print "DEBUG SimultaneousFit c"  
  leg.Draw()
  print "DEBUG SimultaneousFit c1"  
  #canv.RedrawAxis()
  print "DEBUG SimultaneousFit c2"  
  drawGlobals(canv)
  print "DEBUG SimultaneousFit c3"  
  # print canvas
  print "DEBUG SimultaneousFit c4"  
  canv.Update()
  print "DEBUG SimultaneousFit d"  
  if not options.batch: raw_input("Looks ok?")
  canv.Print('%s.pdf'%options.outname)
  canv.Print('%s.root'%options.outname)
  canv.Print('%s.png'%options.outname)
  canv.Print('%s.C'%options.outname)
  canv.SetName(options.outname)
  outf.cd()
  canv.Write()
  print "DEBUG SimultaneousFit e"  

def runStandard():
  config = []
  for k, f in enumerate(options.files):
    tf = r.TFile(f)
    print f
    tree = tf.Get('limit')
    values=[]
    for i in range(tree.GetEntries()):
      tree.GetEntry(i)
      skippoint = False
      for mhb in options.blacklistMH:
    	if abs(mhb-tree.mh)<0.01 : 
		skippoint = True
		break
      if skippoint: continue
      values.append([tree.mh, tree.limit])
    values.sort(key=lambda x: x[0])
    config.append(values)

  if options.method=='pval': pvalPlot(config)
  elif options.method=='limit': limitPlot(config)
  elif options.method=='maxlh': maxlhPlot(config)

def read1D(file,x,i,xtitle):
  tree = file.Get('limit')
  tree.Draw('2*deltaNLL:%s'%x,'','')
  gr = r.gROOT.FindObject('Graph').Clone('gr_%s_%d'%(x,i))
  gr.SetTitle("")
  gr.GetXaxis().SetTitle(xtitle)
  gr.GetYaxis().SetTitle("-2 #Delta LL")

  gr.Sort()
  last = None
  for i in range(gr.GetN(),0,-1):
    if gr.GetX()[i-1] == last:
      gr.RemovePoint(i-1)
    last = gr.GetX()[i-1]
  return gr

def findQuantile(pts,cl):

  #gr is a list of r,nll
  # start by walking along the variable and check if crosses a CL point
  
  if cl<=0:  
   min=pts[0][0]
   mincl=pts[0][1]
   for pt in pts: 
    if pt[1]<mincl: 
      mincl=pt[1]
      min = pt[0]
     
   return min,min
  min=pts[0][0]
  mincl=pts[0][1]
  bestfit_ci =0
  ci=0
  for pt in pts: 
    if pt[1]<mincl: 
      mincl=pt[1]
      min = pt[0]
      bestfit_ci=ci
  
    ci=ci+1

  #print min ," ", bestfit_ci   
  #print "determine corssbounds for cl ", cl
  #for pt in pts:
  #  print "--> pt[1] ", pt[1], " cl ", cl, " pt[1]-cl ", pt[1]-cl ," abs(pt[1]-cl)<0.5) " , (abs(pt[1]-cl)<0.5)
  #crossbound = [ pt[1]<=cl for pt in pts ]
  #crossbound = [ abs(pt[1]-cl)<0.5 for pt in pts ]
  crossbound =  [(True) for pt in pts ]
  #print crossbound
  #exit
  rcrossbound = crossbound[:]
  rcrossbound.reverse()

  minciUp = 0
  minciDown = 0
  maxciUp = len(crossbound)-1
  maxciDown = len(crossbound)-1
  min = pts[0][0]
  max = pts[maxciUp][0]
  #print crossbound
  for c_i,c in enumerate(crossbound): 
    #print c_i, c,  pts[c_i][0],  pts[c_i][1] ,pts[c_i+1][1]
    if c and pts[c_i][1]>cl  and pts[c_i+1][1]<cl : 
      minciUp=c_i
      minciDown=c_i+1
   #   break
    if  c_i > bestfit_ci:
      break
  
  for c_i,c in enumerate(rcrossbound):
    d_i = len(crossbound) -c_i-1 
    #print "reverse" ,c_i, c, pts[d_i][0], pts[d_i][1] ,pts[d_i-1][1]
    if c and pts[d_i][1]>cl  and pts[d_i-1][1]<cl:
      maxciUp=d_i
      maxciDown=d_i-1
      #maxci=len(rcrossbound)-c_i
    if d_i-1 < bestfit_ci:
    #if len(rcrossbound)-c_i < bestfit_ci:
      break

  #if minciUp>0: 
  if minciUp!=minciDown: 
    y0,x0 = pts[minciUp][0],pts[minciUp][1]
    y1,x1 = pts[minciDown][0],pts[minciDown][1]
    #print "x0, y0", x0, " ", y0
    #print "x1, y1", x1, " ", y1
    min = y0+((cl-x0)*y1 - (cl-x0)*y0)/(x1-x0)
    
  #if maxciDown<len(crossbound)-1: 
  if maxciDown!=maxciUp: 
    y0,x0 = pts[maxciUp][0],pts[maxciUp][1]
    y1,x1 = pts[maxciDown][0],pts[maxciDown][1]
    #print "x0, y0", x0, " ", y0
    #print "x1, y1", x1, " ", y1
    max = y0+((cl-x0)*y1 - (cl-x0)*y0)/(x1-x0)
  
  #print min, max
  if min > max :
    print "switch min ", min," and max ", max
    tmp = min
    min = max
    max =tmp
    
  return min,max

def smoothNLL(gr,res):

  minVal = min([re[0] for re in res])
  maxVal = max([re[0] for re in res])
  sp = r.TSpline3('sp_%s'%gr.GetName(),gr,"",minVal,maxVal)
  for p in range(100):
    x = minVal+p*((maxVal-minVal)/100.)
    y = sp.Eval(x)
    gr.SetPoint(p,x,y)

def shiftNLL(gr,bf):
  
  shift = options.shiftNLL - bf
  for p in range(gr.GetN()):
    x = r.Double()
    y = r.Double()
    gr.GetPoint(p,x,y)
    gr.SetPoint(p,x+shift,y)

# 1D Log-likelihood scans 
def plot1DNLL(returnErrors=False,xvar="", ext=""):

  if options.method=='mh':
    x = 'MH'
    #x = 'mh'
    xtitle = 'm_{H} (GeV)'
  elif options.method=='mu':
    x = "r"
    #xtitle = '#sigma / #sigma_{SM}'
    xtitle = '#mu'
    if options.specifyX:
      print "setting variable name in tree to",options.specifyX[0]
      x = options.specifyX[0]
      xtitle = '#mu_{%s}'%options.specifyX[0]
  elif options.method=='muProc':
    x = xvar
    #xtitle = '#sigma / #sigma_{SM}'
    xtitle = '#mu'
  elif options.method=='pdf':
    x = 'pdfindex_UntaggedTag3_13TeV'
    #xtitle = '#sigma / #sigma_{SM}'
    xtitle = 'chosen pdf index'
    if options.xlab: 
      xtitle = options.xlab
    if xvar:
      x = xvar
  elif options.method=='rv':
    x = 'RV'
    xtitle = '#mu_{qqH+VH}'
  elif options.method=='rf':
    x = 'RF'
    xtitle = '#mu_{ggH+ttH}'
  else:
    sys.exit('Method not recognised for 1D scan %s'%options.method)

  if not options.legend: leg  = r.TLegend(0.35,0.65,0.65,0.79)
  #if not options.legend: leg  = r.TLegend(0.05,0.05,0.4,0.4)
  else: leg = r.TLegend(float(options.legend.split(',')[0]),float(options.legend.split(',')[1]),float(options.legend.split(',')[2]),float(options.legend.split(',')[3]))
  #leg.SetFillColor(0)
  clean_graphs=[]
  leg.SetBorderSize(0)

  for k, f in enumerate(options.files):
    ntitle = options.names[k]
    tf = r.TFile(f)
    tree = tf.Get('limit')
    gr = r.TGraph()
    gr.SetName('gr_%d_%s'%(k,x))
    gr.SetLineColor((options.colors[k]))
    gr.SetLineStyle(int(options.styles[k]))
    gr.SetLineWidth(int(options.widths[k]))
    leg.AddEntry(gr,options.names[k],'L')
    
    res=[]
    for i in range(tree.GetEntries()):
      tree.GetEntry(i)
      xv = getattr(tree,x)
      if (hasattr(tree,"MH")):
        lcMH = getattr(tree,"MH")
      else:
        lcMH =-999
      # tree.quantileExpected==1: continue
      if tree.deltaNLL<0 and options.verbose: print "Warning, found -ve deltaNLL = ",  tree.deltaNLL, " at ", xv 
      if xv in [re[0] for re in res]: continue
      if 2*tree.deltaNLL < 100:
        res.append([xv,2*tree.deltaNLL,lcMH])
    res.sort()

    # remove weird points again
    rfix = []
    for re in res: 
      if re[1]<100: rfix.append(re) 
    
    # clean out spikes :(
    #print "rfix",rfix
    if options.cleanNll: rfix = cleanSpikes1D(rfix)

    res = rfix[:] 
    minNLL = min([re[1] for re in res])
    for re in res: 
      if options.correctNLL and re[1]==0.: re[1]=-1
      re[1]-=minNLL
  
    p=0
    lcMH_bestfit =0;
    lcmu_bestfit =0;
    lcMinNLL =9999;
    for re, nll,m in res: 
      if nll>=0.:
        gr.SetPoint(p,re,nll)
        if (nll < lcMinNLL ) :
          lcMinNLL = nll
          lcmu_bestfit = re
          lcMH_bestfit = m
        if options.verbose: print '\t', p, re, nll
        p+=1

    m,m1 = findQuantile(res,0);
    #l,h  = findQuantile(res,1);
    l,h  = findQuantile(res,r.TMath.ChisquareQuantile(0.68,1)); #now using this, for 68% CL. One-sigma line is above
    #l2,h2  = findQuantile(res,4);
    l2,h2  = findQuantile(res,r.TMath.ChisquareQuantile(0.95,1)); #now using this, for 68% CL. One-sigma line is above
    #l3,h3  = findQuantile(res,9);

    if options.shiftNLL:
      shiftNLL(gr,m)
      shift = options.shiftNLL - m
      m += shift
      m1 += shift
      l += shift
      l2 += shift
      h += shift
      h2 += shift

    if options.smoothNLL:
      smoothNLL(gr,res)
      clean_graphs.append(gr)
    else:
      clean_graphs.append(gr)

    
    xmin = m
    xmun_m = m
    eplus = h-m
    eminus = m-l
    eplus2 = h2-m
    eminus2 = m-l2
    #eplus3 = h3-m
    #eminus3 = m-l3

    print "%15s : %4.6f +%4.6g -%4.6g" % ( ntitle+" "+ext, xmin, eplus , eminus )
    if (options.method=="mu"):
      print "MU = %4.6f +%4.6g -%4.6g" % (  xmin, eplus , eminus )
    #Write in the ledger
    #with open(options.itLedger, "a") as myfile:
		#    myfile.write("%s %f %f %f\n" % ( options.method+" "+options.it, xmin, eplus , eminus ))

    canv.SetLogy(False)


    if returnErrors:
      return [xmin,eplus,eminus,eplus2,eminus2]
    
    if k==0:
      fit = xmin
      err = (abs(eplus)+abs(eminus))/2.
      eplus0 = eplus
      eminus0 = eminus

      axmin,axmax = findQuantile(res,6)
      #axmin,axmax = 120,130
      if options.xaxis:
        print "opts xaxis ", options.xaxis
        axmin = float(options.xaxis[0])
        axmax = float(options.xaxis[1])
      #lines = [r.TLine(axmin, 1, axmax, 1), r.TLine(xmin-eminus,  0, xmin-eminus,  1), r.TLine(xmin+eplus,  0, xmin+eplus,  1),
      #        r.TLine(axmin, 4, axmax, 4), r.TLine(xmin-eminus2, 0, xmin-eminus2, 4), r.TLine(xmin+eplus2, 0, xmin+eplus2, 4) ]
      #        ,r.TLine(axmin, 9, axmax, 9), r.TLine(xmin-eminus3, 0, xmin-eminus3, 9), r.TLine(xmin+eplus3, 0, xmin+eplus3, 9) ]
      the68CL = r.TMath.ChisquareQuantile(0.68,1)
      the95CL = r.TMath.ChisquareQuantile(0.95,1)
      lines = [r.TLine(axmin, the68CL, axmax, the68CL), r.TLine(xmin-eminus,  0, xmin-eminus,  the68CL), r.TLine(xmin+eplus,  0, xmin+eplus,  the68CL), 
              r.TLine(axmin, the95CL, axmax, the95CL), r.TLine(xmin-eminus2, 0, xmin-eminus2, the95CL), r.TLine(xmin+eplus2, 0, xmin+eplus2, the95CL) ] #updated for 68% CL
    
  dH = r.TH1D("dH","",1,axmin,axmax)
  dH.GetXaxis().SetTitle(xtitle)
  dH.GetXaxis().SetTitleSize(0.05)
  dH.GetYaxis().SetTitleSize(0.05)
  if options.method=='mh': dH.GetXaxis().SetNdivisions(505)
  dH.GetYaxis().SetTitle('-2 #Delta ln L')
  if not options.yaxis: dH.GetYaxis().SetRangeUser(0.,6)
  #if not options.yaxis: dH.GetYaxis().SetRangeUser(0.,10.)
  else: dH.GetYaxis().SetRangeUser(float(options.yaxis.split(',')[0]),float(options.yaxis.split(',')[1]))
  dH.SetLineColor(0)
  dH.SetStats(0)
  dH.Draw("AXIS")
    
  for gr in clean_graphs:
    gr.GetXaxis().SetRangeUser(axmin,axmax)
    if not options.yaxis: gr.GetYaxis().SetRangeUser(0.,6)
    else: gr.GetYaxis().SetRangeUser(float(options.yaxis.split(',')[0]),float(options.yaxis.split(',')[1]))
    gr.Draw("L")

  # draw legend
  if len(options.files)>1:
    leg.Draw('same')
        
  # draw intersection lines
  for l in lines:
    l.SetLineWidth(2)
    l.SetLineColor(13)
    l.Draw('same')  

  # draw fit value
  lat2 = r.TLatex()
  lat2.SetNDC()
  lat2.SetTextAlign(22)
  #if options.method=='mh': lat2.DrawLatex(0.5,0.85,"#hat{m}_{H} = %6.2f ^{#font[122]{+}%4.2f}_{#font[122]{-}%4.2f}"%(fit,eplus0,eminus0))
  if options.method=='mh': lat2.DrawLatex(0.48,0.83,"#hat{m}_{H} = %6.2f ^{#font[122]{+}%4.2f}_{#font[122]{-}%4.2f}"%(fit,eplus0,eminus0))
  elif ( options.method=='mu' or options.method=='muProc'): 
    #lat2.SetTextSize(0.045)
    #lat2.SetTextAlign(11)
    #lat2.DrawLatex(0.17,0.78,"#hat{#mu} = %4.2f ^{#font[122]{+}%4.2f}_{#font[122]{-}%4.2f}"%(fit,eplus0,eminus0))
    #lat2.DrawLatex(0.46,0.84,"#hat{#mu} = %4.2f ^{#font[122]{+}%4.2f}_{#font[122]{-}%4.2f}"%(fit,eplus0,eminus0))
    lat2.DrawLatex(0.52,0.84,"#hat{#mu} = %4.2f ^{#font[122]{+}%4.2f}_{#font[122]{-}%4.2f}"%(fit,eplus0,eminus0)) #LHCP17
    #lat2.DrawLatex(0.47,0.84,"#hat{#mu} = %4.2f ^{#font[122]{+}%4.2f}_{#font[122]{-}%4.2f}"%(fit,eplus0,eminus0))
  elif options.method=='rv': lat2.DrawLatex(0.5,0.85,"#hat{#mu}_{qqH+VH} = %4.2f ^{#font[122]{+}%4.2f}_{#font[122]{-}%4.2f}"%(fit,eplus0,eminus0))
  elif options.method=='rf': lat2.DrawLatex(0.5,0.85,"#hat{#mu}_{ggH+ttH} = %4.2f ^{#font[122]{+}%4.2f}_{#font[122]{-}%4.2f}"%(fit,eplus0,eminus0))

  #draw CL lines
  if options.method=='mu':
    lat3 = r.TLatex()
    lat3.SetNDC()
    lat3.SetTextAlign(22)
    lat2.DrawLatex(0.2,0.25,"#font[62]{#scale[0.6]{68% CL}}")
    lat2.DrawLatex(0.2,0.63,"#font[62]{#scale[0.6]{95% CL}}")

  drawGlobals(canv)
  canv.RedrawAxis()
  canv.Update()
  if not options.batch: raw_input("Looks ok?")
  canv.Print('%s.pdf'%options.outname)
  canv.Print('%s.png'%options.outname)
  canv.Print('%s.C'%options.outname)
  canv.SetName(options.outname)
  outf.cd()
  canv.Write()


# 2DNLL plots, can input histos externally
def plot2DNLL(xvar="RF",yvar="RV",xtitle="#mu_{ggH+ttH}",ytitle="#mu_{qqH+VH}"):
  
  #if len(options.files)>1:  sys.exit('Just one file for 2D scans please')
  canv = r.TCanvas("%s_%s"%(xvar,yvar),"%s_%s"%(xvar,yvar),750,750)
  canv.SetTicks(1,1)
  BFgrs  = []
  CONT1grs = []
  CONT2grs  = []
  COLgrs = []
  
  if not options.legend: leg = r.TLegend(0.7,0.7,0.88,0.88)
  #if not options.legend: leg = r.TLegend(0.05,0.05,0.4,0.4)
  else: leg = r.TLegend(float(options.legend.split(',')[0]),float(options.legend.split(',')[1]),float(options.legend.split(',')[2]),float(options.legend.split(',')[3]))
  #leg.SetFillColor(10)

  smmarker = r.TMarker(1,1,33)
  smmarker.SetMarkerColor(97)
  smmarker.SetMarkerSize(2.5)
  smmarker2 = r.TMarker(1,1,33)
  smmarker2.SetMarkerColor(89)
  smmarker2.SetMarkerSize(1.4)
  smmarker_leg = smmarker.Clone("smmarker_leg")
  #smmarker_leg.SetMarkerStyle(27)
  smmarker_leg.SetMarkerSize(2.5)

  addBFtoLeg = False

  mems = []
  th2s = []
  th2nameinfile='h2d'
  if ':' in options.get2dhist : 
    options.get2dhist,th2nameinfile=((options.get2dhist).split(':'))
  for fi,file in enumerate(options.files):

    tf = r.TFile(file)
    mems.append(tf)
    tree = tf.Get('limit')
    if not options.get2dhist:
      xmin = tree.GetMinimum(xvar)
      xmax = tree.GetMaximum(xvar)
      ymin = tree.GetMinimum(yvar)
      ymax = tree.GetMaximum(yvar)

    if options.get2dhist:
      extfile = r.TFile(options.get2dhist)
      mems.append(extfile)
      th2f = extfile.Get('%s'%th2nameinfile).Clone();
      th2f.SetName("h")
      th2 = r.TH2F("h","hclean",th2f.GetNbinsX(),th2f.GetXaxis().GetXmin(),th2f.GetXaxis().GetXmax(),th2f.GetNbinsY(),th2f.GetYaxis().GetXmin(),th2f.GetYaxis().GetXmax())
      for bi in range(1,th2f.GetNbinsX()+1):
        for bj in range(1,th2f.GetNbinsY()+1):
           th2.SetBinContent(bi,bj,th2f.GetBinContent(bi,bj))
      tf.cd()
    else:
        #print "tree.Draw(\"%s>>h%d%s(10000,%1.4f,%1.4f\")"%(xvar,fi,xvar,xmin,xmax),",\"deltaNLL>0.\",\"goff\")"
        tree.Draw("%s>>h%d%s(10000,%1.4f,%1.4f)"%(xvar,fi,xvar,xmin,xmax),"deltaNLL>0.","goff")
        tempX = r.gROOT.FindObject('h%d%s'%(fi,xvar))
        tree.Draw("%s>>h%d%s(10000,%1.4f,%1.4f)"%(yvar,fi,yvar,ymin,ymax),"deltaNLL>0.","goff")
        tempY = r.gROOT.FindObject('h%d%s'%(fi,yvar))
    
       # x binning
        if options.xbinning: 
           xbins = int(options.xbinning.split(',')[0])
           xmin = float(options.xbinning.split(',')[1])
           xmax = float(options.xbinning.split(',')[2])
        else:
           xbins=0
           xmin = tree.GetMinimum(xvar)
           xmax = tree.GetMaximum(xvar)
           if options.xaxis:
             xmin = float(options.xaxis[0])
             xmax = float(options.xaxis[1])
           tree.Draw("%s>>h%d%s(10000,%1.4f,%1.4f)"%(xvar,fi,xvar,xmin,xmax),"deltaNLL>0.","goff")
           tempX = r.gROOT.FindObject('h%d%s'%(fi,xvar))
           for bin in range(1,tempX.GetNbinsX()+1):
                if tempX.GetBinContent(bin)!=0: 
                  xbins+=1
    
      # y binning
        if options.ybinning: 
           ybins = int(options.ybinning.split(',')[0])
           ymin = float(options.ybinning.split(',')[1])
           ymax = float(options.ybinning.split(',')[2])
        else:
           ybins=0
           ymin = tree.GetMinimum(yvar)
           ymax = tree.GetMaximum(yvar)
           if options.yaxis:
               ymin = float(options.yaxis.split(',')[0])
               ymax = float(options.yaxis.split(',')[1])
           tree.Draw("%s>>h%d%s(10000,%1.4f,%1.4f)"%(yvar,fi,yvar,ymin,ymax),"deltaNLL>0.","goff")
           tempY = r.gROOT.FindObject('h%d%s'%(fi,yvar))
           for bin in range(1,tempY.GetNbinsX()+1):
              if tempY.GetBinContent(bin)!=0: ybins+=1

        tree.Draw("2.*deltaNLL:%s:%s>>h%d%s%s(%d,%1.4f,%1.4f,%d,%1.4f,%1.4f)"%(yvar,xvar,fi,yvar,xvar,xbins,xmin,xmax,ybins,ymin,ymax),"deltaNLL>0.&&deltaNLL<10000.","prof")#remove inf points
        th2 = r.gROOT.FindObject('h%d%s%s'%(fi,yvar,xvar))

    if options.xaxis :
        xmin = float(options.xaxis[0])
        xmax = float(options.xaxis[1])
        th2.GetXaxis().SetRangeUser(xmin,xmax)
    if options.yaxis :
        ymin = float(options.yaxis.split(',')[0])
        ymax = float(options.yaxis.split(',')[1])
        th2.GetYaxis().SetRangeUser(ymin,ymax)
    
    ############## Simple spike killer ##########
    #print " Begin Spike killer"
    #prevBin=-999
    #for j in range (0,th2.GetNbinsY()):
    #  for i in range (0,th2.GetNbinsX()):
    #    if (prevBin < 0) : prevBin = th2.GetBinContent(i,j) 
    #    if (prevBin==0) : prevBin=1
    #    thisBin = th2.GetBinContent(i,j)
    #    fracChange= abs(prevBin - thisBin)/prevBin
    #    if  fracChange > 10 and i!=0 and j!=0:
    #      newContent = 0.5 * (th2.GetBinContent(i-1,j)+ th2.GetBinContent(i+1,j))
    #      th2.SetBinContent(i,j,newContent)
    #      factor=newContent/th2.GetBinContent(i,j) 
    #      th2.SetBinContent(i,j,newContent*factor)
    #    else:
    #      prevBin= th2.GetBinContent(i,j)
    ############## Simple spike killer ##########

    #spike killer above doesn't seem to work, to do with object being a TProfile2D with some methods overloaded and some not.
    # the section below is a horrible hack for the KGluKGam plot, making failed jobs the background colour
    if options.method=='kglukgam':
      for j in range (0,th2.GetNbinsY()+1):
        for i in range (0,th2.GetNbinsX()+1):
          if i+j>(0.75*(th2.GetNbinsX()+th2.GetNbinsY())): 
            th2.Fill(xmin+i*((xmax-xmin)/float(xbins)),ymin+j*((ymax-ymin)/float(ybins)),10.)

    gBF = r.TGraph()
    gSM = r.TGraph()
    xBF =-99999;
    yBF =-99999;
    contourPointsX= []
    contourPointsY= []
    contourPointsZ= []
    if (options.method=="rvrf") :gSM.SetPoint(0,1,1)
    if (options.method=="mumh") :gSM.SetPoint(0,1,125.09)
    printedOK = False
    if options.bf2d:
      if float(options.bf2d.split(',')[0]) > th2.GetXaxis().GetXmin() and \
        float(options.bf2d.split(',')[0]) < th2.GetXaxis().GetXmax() and \
        float(options.bf2d.split(',')[1]) > th2.GetYaxis().GetXmin() and \
        float(options.bf2d.split(',')[1]) < th2.GetYaxis().GetXmax() : addBFtoLeg = True

      gBF.SetPoint(0,float(options.bf2d.split(',')[0]),float(options.bf2d.split(',')[1]))
    else: 
     for ev in range(tree.GetEntries()):
      tree.GetEntry(ev)
      if tree.deltaNLL<0: continue
      #if abs(tree.deltaNLL -2.3*0.5) <0.1 : 
      if abs(tree.deltaNLL -1*0.5) <0.05 : 
        contourPointsX.append(getattr(tree,xvar))
        contourPointsY.append(getattr(tree,yvar))
        contourPointsZ.append((tree.deltaNLL))
      if tree.deltaNLL==0:
        if not printedOK : 
          print "Best Fit (%s) : "%(options.names[fi]),xvar,"=%.4f"%getattr(tree,xvar),", ",yvar,"=%.4f"%getattr(tree,yvar)
          printedOK=True
        if float(getattr(tree,xvar)) > th2.GetXaxis().GetXmin() and \
          float(getattr(tree,xvar)) < th2.GetXaxis().GetXmax() and \
    float(getattr(tree,yvar)) > th2.GetYaxis().GetXmin() and \
    float(getattr(tree,yvar)) < th2.GetYaxis().GetXmax() : addBFtoLeg = True
        gBF.SetPoint(0,getattr(tree,xvar),getattr(tree,yvar))
        xBF=getattr(tree,xvar)
        yBF=getattr(tree,yvar)

    ############## Get BF with uncertainties ##########
    xPlus =[-999.,-999.,-999.]
    xMinus =[-999.,-999.,-999.]
    yPlus =[-999.,-999.,-999.]
    yMinus = [-999.,999.,-999.]
    minDeltaXplus = 999.
    minDeltaXminus = 999.
    minDeltaYplus = 999.
    minDeltaYminus =999.
    for i in range(0,len(contourPointsX)):
       deltaX = contourPointsX[i] - xBF
       deltaY = contourPointsY[i] - yBF
       #gBF.SetPoint(1+i,contourPointsX[i],contourPointsY[i])
       if abs(deltaX) < minDeltaXplus and deltaY >0 :
          minDeltaXplus = abs(deltaX)
          yPlus= [contourPointsX[i] , contourPointsY[i],contourPointsZ[i]]
       if abs(deltaX) < minDeltaXminus and deltaY <0 :
          minDeltaXminus = abs(deltaX)
          yMinus= [contourPointsX[i] , contourPointsY[i],contourPointsZ[i]]
       if abs(deltaY) < minDeltaYplus and deltaX >0 :
          minDeltaYplus = abs(deltaY)
          xPlus= [contourPointsX[i] , contourPointsY[i],contourPointsZ[i]]
       if abs(deltaY) < minDeltaYminus and deltaX <0 :
          minDeltaYminus = abs(deltaY)
          xMinus= [contourPointsX[i] , contourPointsY[i],contourPointsZ[i]]
          
    #print "BF xBF= ", xBF , " yBF=",   yBF    
    #print "xPlus at ", xPlus
    #print "xMinus at ", xMinus
    #print "yPlus at ", yPlus
    #print "yMinus at ", yMinus

    xBF_up = abs(xBF - xPlus[0])
    xBF_down = abs(xBF - xMinus[0])
    yBF_up = abs (yBF - yPlus[1])
    yBF_down = abs( yBF - yMinus[1])
    
		#WARNING this is not the right way to calculate teh uncertainties: you should do a 1-D scan fo each variabel profiling the other. That is the correct way to get the uncertaainties!
		#print " Best fit rF = %2.2f + %2.2f - %2.2f"%( xBF ,  xBF_up , xBF_down)
    #print " Best fit X = %2.2f --> %2.2f--> %2.2f"%( xBF - xBF_down ,  xBF , xBF+ xBF_up)
    #print " Best fit rV = %2.2f + %2.2f - %2.2f"%( yBF ,  yBF_up , yBF_down)
    #print " Best fit Y = %2.2f --> %2.2f--> %2.2f"%( yBF - yBF_down ,  yBF , yBF+ yBF_up)
    #gBF.SetPoint(1,xPlus[0],xPlus[1])
    #gBF.SetPoint(2,yPlus[0],yPlus[1])
    #gBF.SetPoint(2,xMinus[0],xMinus[1])
    #gBF.SetPoint(4,yMinus[0],yMinus[1])
          #print " **DEBUG bin x=", i , " y=",j," have ", th2.GetBinContent(i,j)
    ##############Contour  ##########

    th2.SetTitle("")

    th2.SetMinimum(-0.0001)
    th2.SetMaximum(options.zmax)
    th2.GetXaxis().SetTitle(xtitle)
    th2.GetYaxis().SetTitle(ytitle)
    canv.SetRightMargin(0.15)
    canv.SetBottomMargin(0.15)
    th2.GetZaxis().SetTitle(("q(%s,%s)"%(xtitle,ytitle)))
    th2.GetZaxis().SetTitleOffset(0.85)
    th2.GetYaxis().SetTitleOffset(0.85)
    th2.GetXaxis().SetTitleOffset(0.9)
    th2.GetZaxis().SetTitleSize(0.05)
    th2.GetYaxis().SetTitleSize(0.05)
    th2.GetXaxis().SetTitleSize(0.05)
    if(options.method=='rvrf'): 
      th2.GetXaxis().SetTitleOffset(1.0)
      th2.GetXaxis().SetTitleSize(0.04)
      th2.GetXaxis().SetLabelSize(0.03)
      th2.GetYaxis().SetTitleOffset(1.0)
      th2.GetYaxis().SetTitleSize(0.04)
      th2.GetYaxis().SetLabelSize(0.03)
    th2s.append(th2.Clone())

    if options.xaxis: th2.GetXaxis().SetRangeUser(float(options.xaxis[0]),float(options.xaxis[1]))
    if options.yaxis: th2.GetYaxis().SetRangeUser(float(options.yaxis.split(',')[0]),float(options.yaxis.split(',')[1]))

    cont_1sig = th2.Clone('cont_1_sig')
    cont_1sig.SetContour(2)
    #cont_1sig.SetContourLevel(1,2.3)
    cont_1sig.SetContourLevel(1,r.TMath.ChisquareQuantile(0.68,2))
    cont_1sig.SetLineColor((options.colors[fi]))
    cont_1sig.SetLineWidth(3)
    cont_1sig.SetLineStyle(1)
    cont_2sig = th2.Clone('cont_2_sig')
    cont_2sig.SetContour(2)
    #cont_2sig.SetContourLevel(1,6.18)
    cont_2sig.SetContourLevel(1,r.TMath.ChisquareQuantile(0.95,2))
    cont_2sig.SetLineColor((options.colors[fi]))
    cont_2sig.SetLineWidth(3)
    cont_2sig.SetLineStyle(2)
    if options.get2dhist: 
      cont_2sig.SetLineStyle(1)
      cont_2sig.SetLineWidth(2)

     

    gBF.SetMarkerStyle(34)
    gBF.SetMarkerSize(2.0)
    gBF.SetMarkerColor((options.colors[fi]))
    gBF.SetLineColor((options.colors[fi]))
    
    gSM.SetMarkerStyle(33)
    gSM.SetMarkerSize(2.0)
    gSM.SetMarkerColor((r.kRed))
    gSM.SetLineColor((1))

    COLgrs.append(th2.Clone())
    BFgrs.append(gBF.Clone())
    CONT1grs.append(cont_1sig.Clone())
    CONT2grs.append(cont_2sig.Clone())

    r.gStyle.SetOptStat(0)

    if len(options.files)==1 :
       #if options.expected : leg.AddEntry(0,"Expected SM Higgs","") 
        if options.expected : leg.SetHeader("Expected SM H") 
        if addBFtoLeg: leg.AddEntry(gBF,"Best Fit","P")
        if (options.method=="rvrf") :leg.AddEntry(gSM,"SM","P")
        if (options.method=="mumh") :leg.AddEntry(gSM,"#mu=1, m_H=125.09 GeV","P")
        #leg.AddEntry(cont_1sig,"1#sigma","L")
        #leg.AddEntry(cont_2sig,"2#sigma","L")
        leg.AddEntry(cont_1sig,"68% CL","L") #for paper, CL requested
        leg.AddEntry(cont_2sig,"95% CL","L") #for paper, CL requested
    else :
      leg.AddEntry(BFgrs[-1],options.names[fi],"P")
  leg.SetBorderSize(0)
  if options.addSM: 
      # leg.AddEntry(smgraph,"SM","P")
      smentry =  leg.AddEntry(smmarker_leg,"SM","P")

  # Now Draw them 
  print COLgrs
  if len(options.files)==1:
    for fi in range(len(options.files)):
     #th2.SetContour(10000)
     set_palette(ncontours=255);
     #r.gStyle.SetPalette(100,86);
     th2.Draw("colz9")
     gBF_underlay = gBF.Clone()
     gBF_underlay.SetMarkerColor(r.kWhite)
     gBF_underlay.SetMarkerSize(2.6)
     gBF_underlay.Draw("Psame")
     gBF.Draw("Psame")
     gSM_underlay = gSM.Clone()
     gSM_underlay.SetMarkerColor(r.kWhite)
     gSM_underlay.SetMarkerSize(2.6)
     gSM_underlay.Draw("Psame")
     gSM.Draw("Psame")
     cont_1sig.SetLineColor(1);
     cont_2sig.SetLineColor(1);
     cont_1sig.Draw("cont3same9")
     cont_2sig.Draw("cont3same9")
    if options.addSM:
      smmarker.Draw()
    #if (len(options.box.split(",")>1)):
    if (options.box):
      print "DRAWING BOX with option.bix", options.box
      boxp= options.box.split(",")
      box = r.TPave(float(boxp[0]),float(boxp[1]),float(boxp[2]),float(boxp[3]),0,"NDC")
      #box.SetFillColor(int(boxp[4]))
      box.SetFillColor(r.kWhite)
      #box.DrawPave(float(boxp[0]),float(boxp[1]),float(boxp[2]),float(boxp[3]),0,"NBNDC")
      box.Draw()

    leg.SetFillColor(r.kWhite)
    leg.Draw()
    drawGlobals(canv,"2D")
    canv.RedrawAxis()
    canv.Modified()
    canv.Update()

    if not options.batch: raw_input("Looks ok?")
    if not options.outname: options.outname = '%s_%s'%(xvar,yvar)
    canv.Print('%s_col.pdf'%options.outname)
    canv.Print('%s_col.png'%options.outname)
    canv.Print('%s_col.C'%options.outname)
    canv.SetName('%s_col'%options.outname)
    canv.SetRightMargin(0.1)
    canv.SetBottomMargin(0.1)

  # Now the main one
  #canv.Clear()
  for fi in range(len(options.files)):
    th2 = COLgrs[fi]
    gBF = BFgrs[fi]
    cont_1sig = CONT1grs[fi]
    cont_2sig = CONT2grs[fi]
    r.gStyle.SetOptStat(0)
    if fi==0: th2.Draw("axis")
    gBF.Draw("Psame")
    gSM.Draw("Psame")
    cont_1sig.Draw("cont3same9")
    cont_2sig.Draw("cont3same9")

  leg.Draw()

  if options.addSM:
        smmarker.Draw()
      

  drawGlobals(canv,"2D")
  canv.RedrawAxis()
  if not options.batch: raw_input("Looks ok?")
  canv.Print('%s.pdf'%options.outname) 
  canv.Print('%s.png'%options.outname)
  canv.Print('%s.C'%options.outname)
  canv.SetName(options.outname)
  outf.cd()
  canv.Write()
  newout = r.TFile("%s_hists2D.root"%options.outname,"RECREATE")
  for k,th2tmp in enumerate(th2s):
        
   th2tmp.SetName("h2_%d"%k)
   newout.WriteTObject(th2tmp)
  print "Saved 2D hists to %s"%newout.GetName()
  newout.Close()
  mems = []

# Channe; compatibility for Envelope (correct errors)
def plotMPdfChComp(plottype="perTag"):

  print 'plotting mpdf ChannelComp'
  if not options.noComb: print '\t will assume first file is the global best fit'
  addDummyPoint =1
  points = []
  catNames = []
  skipFlags = []
  loffiles = options.files
  #loffiles.sort()
  #loffiles.reverse()
  print options.files
  k=0
  print " LC DEBUG A"
  ppergraph = len(loffiles)/options.groups
  if not options.noComb:  ppergraph = (len(loffiles)-1)/options.groups
  nFile = len(loffiles)
  print " LC DEBUG B"
  while len(loffiles)>0:
    ext=''
    if options.groups>1: 
    	gr=k/ppergraph
    	ext = options.groupnames[gr]

    options.files = [loffiles[0]]
    if plottype=="perTag":
      print " LC DEBUG C perTag"

      catName=loffiles[0].split("/")[-1].replace(".root","")
      if ("_" in catName):
         catName=catName.split("_",1)[-1] #eg r_ggH --> ggH
         options.xvar[k] = 'r_%s'%catName
         debugCatName=catName
      else: debugCatName=catName
      catName=catName.replace("TTHLeptonicTag","TTH Leptonic Tag")
      catName=catName.replace("TTHHadronicTag","TTH Hadronic Tag")
      catName=catName.replace("ZHLeptonicTag","ZH Leptonic Tag")
      catName=catName.replace("WHLeptonicTag","WH Leptonic Tag")
      catName=catName.replace("VHLeptonicLooseTag","VH Lep Loose Tag")
      catName=catName.replace("VHMetTag","VH MET Tag")
      catName=catName.replace("VHHadronicTag","VH Hadronic Tag")
      catName=catName.replace("_13TeV","")
      catName=catName.replace("Tag_","Tag ")
      catName=catName.replace("UntaggedTag","Untagged")
      catName=catName.replace("VBFTag ","VBF Tag")
      if (catName=="VBF") : catName=catName.replace("VBF","VBF Tags")
      if (catName=="TTH"): catName=catName.replace("TTH","TTH Tags")

      options.method = 'mu'
    if plottype=="perProc":
      catName=loffiles[0].split("/")[-1].replace(".root","") 
      print " LC DEBUG C perProc -- catname ",catName
      if ("_" in catName):
         catName=catName.split("_",1)[-1] #eg r_ggH --> ggH
         options.method = 'muProc'
         options.xvar[k] = 'r_%s'%catName
         debugCatName=catName
         
         #temp workaround, needs to be new method/changed 
         doStxs = options.stxs
         if doStxs:
           #if "ggH" in catName: catName ="#scale[1.5]{#sigma_{ggH}/#sigma_{theo}}"
           if "ggH" in catName: catName ="#scale[1.5]{GG2H}"
           if "GG2H" in catName: catName ="#scale[1.5]{ggH}"
           if "qqH" in catName: catName ="#scale[1.5]{VBF}"
           #if "ttH" in catName: catName ="#scale[1.5]{#sigma_{ttH}/#sigma_{theo}}"
           if "ttH" in catName: catName ="#scale[1.5]{TTH}"
           if "TTH" in catName: catName ="#scale[1.5]{ttH}"
           #if "VH"  in catName: catName ="#scale[1.5]{#sigma_{VH}}"
           if "VH2HQQ"  in catName: catName ="#scale[1.5]{VH2HQQ}"
           if "VH2HQQ"  in catName: catName ="#scale[1.5]{VH hadronic}"
           elif "VH"  in catName: catName ="#scale[1.5]{VH}"
           if "QQ2HLNU"  in catName: catName ="#scale[1.5]{QQ2HLNU}"
           if "QQ2HLNU"  in catName: catName ="#scale[1.5]{WH leptonic}"
           if "QQ2HLL"  in catName: catName ="#scale[1.5]{QQ2HLL}"
           if "QQ2HLL"  in catName: catName ="#scale[1.5]{ZH leptonic}"
           print "DEBUG LC b CATBAME ", catName

         else:
           if "ggH" in catName: catName ="#scale[1.5]{#mu_{ggH}}"
           #if "ggH" in catName: catName ="#scale[1.5]{#mu_{GG2H}}"
           if "qqH" in catName: catName ="#scale[1.5]{#mu_{VBF}}"
           if "ttH" in catName: catName ="#scale[1.5]{#mu_{ttH}}"
           #if "ttH" in catName: catName ="#scale[1.5]{#mu_{TTH}}"
           #if "VH"  in catName: catName ="#scale[1.5]{#mu_{VH}}"
           if "VH2HQQ"  in catName: catName ="#scale[1.5]{#mu_{VH2HQQ}}"
           if catName == "VH": catName ="#scale[1.5]{#mu_{VH}}"
           if "QQ2HLNU"  in catName: catName ="#scale[1.5]{#mu_{QQ2HLNU}}"
           if "QQ2HLL"  in catName: catName ="#scale[1.5]{#mu_{QQ2HLL}}"
      else:
         options.method = 'mu'
         debugCatName=catName
         #options.xvar[k] = 'r_%s'%catName
      catName=catName.replace("TTHLeptonicTag","ttH Leptonic")
      catName=catName.replace("TTHHadronicTag","ttH Hadronic")
      catName=catName.replace("ZHLeptonicTag","ZH Leptonic")
      catName=catName.replace("WHLeptonicTag","WH Leptonic")
      catName=catName.replace("VHLeptonicLooseTag","VH Lep Loose")
      catName=catName.replace("VHMetTag","VH MET")
      catName=catName.replace("VHHadronicTag","VH Hadronic")
      catName=catName.replace("_13TeV","")
      catName=catName.replace("Tag_","Tag ")
      catName=catName.replace("UntaggedTag","Untagged")
      catName=catName.replace("VBFTag","VBF Tag")
      if (catName=="VBF") : catName=catName.replace("VBF","VBF Tags")
      if (catName=="TTH"): catName=catName.replace("TTH","TTH Tags")
    r.gROOT.SetBatch()
    print 'name %15s'%options.names[k],
    print 'method %15s'%options.method,
    ps = plot1DNLL(True,options.xvar[k],ext) #return the  uncertainties
    cache=options.outname
    options.outname=options.outname+"_debug_"+debugCatName.replace(" ","_")
    #print "CATNAME " , catName, " -- > ", ps
    plot1DNLL(False,options.xvar[k],ext) #print debug plot
    options.outname=cache
    ps.insert(0,options.names[k])
    points.append(ps)
    catNames.append(catName)
    k+=1
    loffiles.pop(0)
    options.outname=cache
  
  rMin=1000.
  rMax=-1000.
  if addDummyPoint : 
    catNames.append("Dummy")
    points.append(["",0,0,0,0,0])
    if options.percatchcomp: #for spacing the now very busy per cat mu plot
      catNames.append("DummySecond")
      points.append(["",0,0,0,0,0])
      catNames.insert(1,"DummyThird")
      points.insert(1,["",0,0,0,0,0])
  if not options.noComb:  catNames=catNames[1:]

  r.gROOT.SetBatch(options.batch)
  for point in points:
    #print point 
    if options.do1sig:
      if point[1]+point[2]>rMax: rMax=point[1]+point[2]
      print " point[1] ", point[1] , " point[2] ", point[2] , " point[1]+point[2] ", point[1]+point[2] , " rMax ", rMax
      if point[1]-point[3]<rMin: rMin=point[1]-point[3]
    else:
      if point[1]+point[4]>rMax: rMax=point[1]+point[4]
      if point[1]-point[5]<rMin: rMin=point[1]-point[5]
    if options.verbose:
      print point[0], ':', point[1:]
  
  rMin = rMin - 0.7*r.TMath.Abs(rMin)
  rMax = rMax + 0.5*r.TMath.Abs(rMax)
  if options.xaxis: 
    rMin = float(options.xaxis[0])
    rMax = float(options.xaxis[1])
  if options.verbose:
    print 'ChComp PlotRange: ', rMin, '-', rMax

  bestFit = points[0]
  catFits = points[1:]
  if options.noComb: catFits = points[0:] # dont assume a combined fit
  ppergraph = len(catFits)/options.groups

  if options.verbose:
    print bestFit
    print catFits


  #xtitle = "#sigma/#sigma_{sm}"
  #xtitle = "#mu"
  xtitle = "#hat{#mu}"
  if doStxs: xtitle = "#sigma_{proc}/#sigma_{theo}"
  #xtitle = "#mu = #sigma/#sigma_{sm}"
  if options.xlab: 
      xtitle = options.xlab
  dummyHist = r.TH2F("dummy",";%s;"%xtitle,1,rMin,rMax,ppergraph,0,ppergraph)
  dummyHist.GetXaxis().SetTitleSize(0.05)
  catGraph1sig = [r.TGraphAsymmErrors() for gr in range(options.groups)]
  catGraph2sig = [r.TGraphAsymmErrors() for gr in range(options.groups)]

  runningChi2 = 0
  ndof = 0 # should be number of categories - 1

  nofitlines = []

  for p, point in enumerate(catFits):
    grIndex = p//ppergraph
    pIndex  = p%ppergraph
    if options.groups==1: yshift=0.5

    elif options.groups%2==0 : # Even
      if grIndex+0.5 > float(options.groups)/2: yshift = 0.5 + (grIndex)*(0.2/options.groups)
      else: yshift = 0.5 - (grIndex+1)*(0.2/options.groups)
    else :
      if grIndex == (options.groups-1)/2 :yshift=0.5
      elif grIndex > float(options.groups)/2: yshift = 0.5 + grIndex*0.2/options.groups
      else :yshift = 0.5 - (grIndex+1)*0.2/options.groups
    if options.chcompShift:
      catGraph1sig[grIndex].SetPoint(pIndex,options.chcompShift,pIndex+yshift)
      catGraph2sig[grIndex].SetPoint(pIndex,options.chcompShift,pIndex+yshift)
    else:
      if ("Dummy" in catNames[p] ): 
        catGraph1sig[grIndex].SetPoint(pIndex,-999,pIndex+yshift)
        catGraph2sig[grIndex].SetPoint(pIndex,-999,pIndex+yshift)
      else:
        catGraph1sig[grIndex].SetPoint(pIndex,point[1],pIndex+yshift)
        catGraph2sig[grIndex].SetPoint(pIndex,point[1],pIndex+yshift)


    catGraph1sig[grIndex].SetPointError(pIndex,point[3],point[2],0.,0.)
    catGraph2sig[grIndex].SetPointError(pIndex,point[5],point[4],0.,0.)
    
    #if point[0]=='': binlabel = 'cat%d'%p
    if point[0]=='' and len(catFits)<=10: 
      if ( "Dummy" in catNames[p]) :
        binlabel = ""
      elif catNames[p]=="VH MET":
        #binlabel = "%s      %.2f ^{+%.2f}_{-%.2f}"%(catNames[p],point[1],point[2],point[1])
        binlabel =   "%s        %.1f ^{+%.1f}_{-%.1f}"%(catNames[p],point[1],point[2],point[1])
      else:
        if (point[2]<0.354 or point[3]<0.354):
          binlabel = "%s      %.2f ^{+%.2f}_{-%.2f}"%(catNames[p],point[1],point[2],point[3])
          if (point[1]<0.001): 
            binlabel = "%s        %.1f ^{+%.1f}_{-%.1f}"%(catNames[p],point[1],point[2],point[3])
        else:
          binlabel = "%s        %.1f ^{+%.1f}_{-%.1f}"%(catNames[p],point[1],point[2],point[3])
    elif point[0]=='' and len(catFits)>10: 
      if ( "Dummy" in catNames[p]) :
        binlabel = ""
      elif catNames[p]=="VH MET":
        #binlabel =   "%s        %.1f ^{+%.1f}_{-%.1f}  "%(catNames[p],point[1],point[2],point[1])
        binlabel =   "%s        %.1f ^{_{+%.1f}}_{^{-%.1f}} "%(catNames[p],point[1],point[2],point[1])
      else:
        if (point[2]<0.354 or point[3]<0.354):
          #binlabel = "%s       %.2f ^{+%.2f}_{-%.2f}"%(catNames[p],point[1],point[2],point[3])
          binlabel = "%s       %.2f ^{_{+%.2f}}_{^{-%.2f}}"%(catNames[p],point[1],point[2],point[3])
          if (point[1]<0.001): 
            #binlabel = "%s        %.1f ^{+%.1f}_{-%.1f}  "%(catNames[p],point[1],point[2],point[3])
            binlabel = "%s        %.1f ^{_{+%.1f}}_{^{-%.1f}} "%(catNames[p],point[1],point[2],point[3])
        else:
          #binlabel = "%s        %.1f ^{+%.1f}_{-%.1f}  "%(catNames[p],point[1],point[2],point[3])
          binlabel = "%s        %.1f ^{_{+%.1f}}_{^{-%.1f}} "%(catNames[p],point[1],point[2],point[3])

    else: binlabel = point[0]
    dummyHist.GetYaxis().SetBinLabel(p+1,binlabel)
    dummyHist.GetYaxis().SetLabelOffset(-0.045)
    dummyHist.GetYaxis().SetLabelSize(0.05)
    if options.percatchcomp: dummyHist.GetYaxis().SetTickSize(0.02)

    catGraph1sig[grIndex].SetLineColor(int(options.colors[grIndex]))
    catGraph1sig[grIndex].SetLineWidth(2)
    catGraph1sig[grIndex].SetMarkerStyle(21)
    catGraph1sig[grIndex].SetMarkerColor(int(options.colors[grIndex]))
    catGraph1sig[grIndex].SetMarkerSize(1.5)
  
    catGraph2sig[grIndex].SetLineColor(int(options.colors[grIndex]))
    catGraph2sig[grIndex].SetLineWidth(2)
    catGraph2sig[grIndex].SetLineStyle(2)
    catGraph2sig[grIndex].SetMarkerStyle(21)
    catGraph2sig[grIndex].SetMarkerColor(int(options.colors[grIndex]))
    catGraph2sig[grIndex].SetMarkerSize(1.5)

    # for chi2 
    pcen   = bestFit[1]
    ppoint = point[1]
    skipFlag=0
    if "TTHL" in catNames[p]: skipFlag=1
    if "Dummy" in catNames[p]: 
      skipFlag=1
      catNames[p]=""
    if options.chcompShift: ppoint = options.chcompShift
    if options.noComb : pcen = 1.
    chierr = 0
    if ppoint > pcen : chierr = point[3]
    else : chierr = point[2]
    additive = 0
    if (ppoint > rMax or ppoint < rMin or skipFlag):
      #tmpline = r.TLine(rMin,pIndex+yshift,rMax,pIndex+yshift)
      tmpline = r.TBox(rMin,pIndex+yshift-0.2,rMax,pIndex+yshift+0.2)
      #tmpline.SetLineWidth(3)
      #tmpline.SetLineColor(13)
      tmpline.SetFillColor(13)
      tmpline.SetFillStyle(3002)
      #nofitlines.append(tmpline.Clone())
    if chierr != 0 and  (ppoint<rMax and ppoint>rMin): 
    	ndof+=1
    	runningChi2 += ((ppoint-pcen)/chierr)**2
	additive = ((ppoint-pcen)/chierr)**2
    skipFlags.append(skipFlag)

  if not options.noComb:
  	print "Compatibility Chi2 (ndof) = ", runningChi2, ndof-1, " p-val = ", r.TMath.Prob(runningChi2,ndof-1)

  dummyHist.SetLineColor(r.kBlack)
  dummyHist.SetFillColor(r.kGreen-3)

  dummyHist2 = dummyHist.Clone('%s2'%dummyHist.GetName())
  dummyHist2.SetFillColor(r.kGreen)

  if not options.legend: 
    leg = r.TLegend(0.68,0.7,0.94,0.88)

  else: leg = r.TLegend(float(options.legend.split(',')[0]),float(options.legend.split(',')[1]),float(options.legend.split(',')[2]),float(options.legend.split(',')[3]))
  #leg.SetFillColor(0)
  leg.SetTextAlign(12)
  leg.SetBorderSize(0)
  leg.SetTextAlign(12)
  #if not options.noComb: leg.AddEntry(dummyHist,"Combined #pm 1#sigma","LF")
  if not options.noComb: leg.AddEntry(dummyHist,"Combined 68% CL","LF")
  if not options.do1sig and not options.noComb: leg.AddEntry(dummyHist2,"Combined #pm 2#sigma","LF")
  #if not options.noComb: leg.AddEntry(catGraph1sig[0],"Per %s #pm 1#sigma"%options.groupentry,"LP");
  #if plottype =="perTag": leg.AddEntry(catGraph1sig[0],"Per category #pm 1#sigma","LP")
  if plottype =="perTag": leg.AddEntry(catGraph1sig[0],"Per category 68% CL","LP")
  #elif plottype =="perProc" and options.percatchcomp: leg.AddEntry(catGraph1sig[0],"Per category #pm 1#sigma","LP")
  #elif plottype =="perProc": leg.AddEntry(catGraph1sig[0],"Per process #pm 1#sigma","LP")
  elif plottype =="perProc" and options.percatchcomp: leg.AddEntry(catGraph1sig[0],"Per category 68% CL","LP")
  elif plottype =="perProc": leg.AddEntry(catGraph1sig[0],"Per process 68% CL","LP")
  if not options.do1sig and not options.noComb: 
    if plottype =="perTag":
      leg.AddEntry(catGraph2sig[0],"Per category #pm 2#sigma","LP");
    if plottype =="perProc":
      leg.AddEntry(catGraph2sig[0],"Per process #pm 2#sigma","LP");

  if options.groups>1: 
    for gr in range(options.groups):
      leg.AddEntry(catGraph1sig[gr],options.groupnames[gr],"L")

  bestFitBand1 = r.TBox(bestFit[1]-bestFit[3],0.,bestFit[1]+bestFit[2],len(catFits)-0.005) # ROOT is bad at colouring inside the lines!
  bestFitBand1.SetFillColor(r.kGreen-3)
  bestFitBand1.SetLineStyle(0)

  bestFitBand2 = r.TBox(bestFit[1]-bestFit[5],0.,bestFit[1]+bestFit[4],len(catFits))
  bestFitBand2.SetFillColor(r.kGreen)
  bestFitBand2.SetLineStyle(0)

  bestFitLine = r.TLine(bestFit[1],0.,bestFit[1],len(catFits))
  bestFitLine.SetLineWidth(2)
  bestFitLine.SetLineColor(r.kBlack)

  r.gStyle.SetOptStat(0)
  cacheErrSize = r.gStyle.GetEndErrorSize()
  cachePadLeft = canv.GetLeftMargin()
  cachePadRight = canv.GetRightMargin()
  r.gStyle.SetEndErrorSize(8.)
  canv.SetLeftMargin(cachePadLeft+0.03); # was 0.18
  canv.SetRightMargin(cachePadRight-0.03); # was 0.05
  canv.SetGridx(False)
  canv.SetGridy(False)
 

  dummyHist.Draw()
  if not options.noComb:
    if not options.do1sig: bestFitBand2.Draw()
    bestFitBand1.Draw()
    bestFitLine.Draw()

  #temporary, to grey out the ZH leptonic tag because has no data in signal region
  #deprecated, use hatching instead. 
  #doGreying = True
  doGreying = False
  if doGreying:
    #greyBox = r.TBox(-3.,3.,0.,4.)
    greyBox = r.TBox(-2.,1.,0.,2.)
    greyBox.SetFillStyle(3004)
    greyBox.SetFillColor(15)
    greyBox.Draw("same")

  #show below zero is excluded
  #doHatching = True
  doHatching = False
  if doStxs or options.percatchcomp:
    doHatching = True
  if doHatching:
    hatchBox = r.TBox(-0.2,0.,0.,len(catFits))
    hatchBox.SetFillStyle(3004)
    hatchBox.SetFillColor(r.kBlack)
    hatchBox.Draw("same")
    hatchLine = r.TLine(0.,0.,0.,len(catFits))
    hatchLine.SetLineStyle(1)
    hatchLine.SetLineWidth(1)
    hatchLine.SetLineColor(r.kBlack)
    hatchLine.Draw("same")
  
  line = r.TLine(1.0,0.,1.0,len(catFits))
  line.SetLineColor(r.kRed)
  line.SetLineWidth(5)
  line.SetLineStyle(7)
  if not doStxs: 
    leg.AddEntry(line,"#mu=#mu_{SM}","L")
  else: 
    line.SetLineStyle(1)
    line.SetLineWidth(1)
    line.SetLineColor(r.kBlack)
    legendLine = r.TLine(3.75,5.23,3.75,5.85)
    legendLine.SetLineStyle(1)
    legendLine.SetLineWidth(3)
    legendLine.SetLineColor(r.kBlack)
    #leg.AddEntry(line,"#sigma=#sigma_{SM}","L")

    procUncertMap = {"GG2H"   :[sqrt(0.032*0.032+0.039*0.039), sqrt(0.032*0.032+0.039*0.039)], #sum in quadrature of uncerts removed, plus then minus
                     "VBF"    :[sqrt(0.004*0.004+0.021*0.021), sqrt(0.003*0.003+0.021*0.021)],
                     "TTH"    :[sqrt(0.058*0.058+0.036*0.036), sqrt(0.092*0.092+0.036*0.036)],
                     "QQ2HLNU":[sqrt(0.005*0.005+0.019*0.019), sqrt(0.007*0.007+0.019*0.019)],
                     "QQ2HLL" :[sqrt(0.038*0.038+0.016*0.016), sqrt(0.030*0.030+0.016*0.016)]}
    procUncertMap["VH2HQQ"] =  [sqrt(procUncertMap["QQ2HLNU"][0]*procUncertMap["QQ2HLNU"][0]+procUncertMap["QQ2HLL"][0]*procUncertMap["QQ2HLL"][0]),
                                sqrt(procUncertMap["QQ2HLNU"][1]*procUncertMap["QQ2HLNU"][1]+procUncertMap["QQ2HLL"][1]*procUncertMap["QQ2HLL"][1])]
    boxIndexMap = {"GG2H":5,"VBF":4,"TTH":3,"QQ2HLNU":2,"QQ2HLL":1,"VH2HQQ":0} #order of processes
    smBoxes = {}
    for proc in procUncertMap.keys():
      uncertVal =  procUncertMap[proc]
      index =  boxIndexMap[proc]
      smBoxes[proc] = r.TBox(1.-uncertVal[1],index,1.+uncertVal[0],index+1)
      smBoxes[proc].SetFillStyle(1001)
      #smBoxes[proc].SetFillColor(r.kGreen-3) #default darkish green
      #smBoxes[proc].SetFillColor(r.kGray+1)
      smBoxes[proc].SetFillColor(9) #blue chosen for LHCP17 PAS
      #smBoxes[proc].SetFillColor(r.kOrange+6)
      #if proc=="GG2H":
      #  smBoxes[proc].SetLineStyle(1)
      #  smBoxes[proc].SetLineWidth(1)
      #  smBoxes[proc].SetLineColor(r.kBlack)
      smBoxes[proc].Draw("same")
    leg.AddEntry(smBoxes["GG2H"],"SM Prediction","F")
  line.Draw("same")

  # draw fit value
  lat2 = r.TLatex()
  lat2.SetNDC()
  lat2.SetTextAlign(12)
  #lat2.SetTextSize(0.035)
  lat2.SetTextSize(0.04)
  if not doStxs: lat2.DrawLatex(0.57,0.59,"#hat{#mu}_{combined} = %6.2f ^{#font[122]{+}%4.2f}_{#font[122]{-}%4.2f}"%(bestFit[1],bestFit[2],bestFit[3]))
  #else: lat2.DrawLatex(0.57,0.59,"#sigma_{combined}/#sigma_{theo} = %6.2f ^{#font[122]{+}%4.2f}_{#font[122]{-}%4.2f}"%(bestFit[1],bestFit[2],bestFit[3]))
  if (options.mhval==None):
    lat2.DrawLatex(0.57,0.50,"m_{H} = 125.09 GeV")
  else:
    if (is_float_try(options.mhval)): 
      lat2.DrawLatex(0.57,0.50,"m_{H} = %s GeV"%options.mhval)
    else:
      if not doStxs: lat2.DrawLatex(0.57,0.50,"m_{H} %s"%options.mhval)
      else: lat2.DrawLatex(0.57,0.64,"m_{H} %s"%options.mhval)

  for gr in range(options.groups):
    #print gr
    if not options.do1sig: catGraph2sig[gr].Draw("EPsame")
    catGraph1sig[gr].Draw("EPsame")

  if options.chcompLine:
    line = r.TLine(rMin,options.chcompLine,rMax,options.chcompLine)
    line.SetLineWidth(3)
    line.SetLineStyle(r.kDashed)
    line.Draw("same")
    label1=r.TText()
    label1.SetNDC()
    label1.SetText(0.26,0.4,"8TeV")
    label1.SetTextAngle(90)
    label2=r.TText()
    label2.SetNDC()
    label2.SetText(0.26,0.75,"7TeV")
    label2.SetTextAngle(90)
    label1.Draw("same")
    label2.Draw("same")
  for tmp in nofitlines: tmp.Draw()
  #if options.groups>1 or not options.noComb: leg.Draw("same")
  leg.Draw("same")
  if doStxs: legendLine.Draw("same")

  drawGlobals(canv,"True") # shift the CMS text etc at the top 
  canv.SetFillColor(0)
  canv.SetBorderMode(0)
  canv.SetBorderSize(2)
  canv.SetLeftMargin(0.2155525)
  canv.SetRightMargin(0.07094134)
  canv.SetTopMargin(0.08392603)
  canv.SetBottomMargin(0.1209104)
  canv.Modified()
  canv.Update()
  canv.RedrawAxis()

  if not options.batch: raw_input("Looks ok?")
  canv.Print('%s.pdf'%options.outname)
  canv.Print('%s.png'%options.outname)
  canv.Print('%s.C'%options.outname)
  canv.SetName(options.outname)
  outf.cd()
  canv.Write()
  
  r.gStyle.SetEndErrorSize(cacheErrSize)
  canv.SetLeftMargin(cachePadLeft);
  canv.SetRightMargin(cachePadRight);

# Standard Max LH plot
def plotMPdfMaxLH():

  points = []
  loffiles = options.files
  addRunIMH=0;
  #addRunIMH=1;
  k=0
  while len(loffiles)>0:
    options.files = [loffiles[0]]
    tf = r.TFile(options.files[0])
    print tf.GetName()
    tree = tf.Get('limit')
    tree.GetEntry(0)
    mh = tree.mh
    tf.Close()
    skippoint = False
    for mhb in options.blacklistMH:
    	if abs(mhb-mh)<0.01 : 
		skippoint = True
		break
    if skippoint: continue
    options.method = 'mu'
    r.gROOT.SetBatch()
    #print "debug plot1DNLL(True,options.xvar[k]) ", 'plot1DNLL(True,%s)'%options.xvar[k]
    ps = plot1DNLL(True,options.xvar[k])
    catName=loffiles[0].split("/")[-1].replace(".root","").replace("_13TeV","")
    cache=options.outname
    options.outname=options.outname+"_debug_"+catName
    cachexaxis = options.xaxis
    cacheyaxis = options.yaxis
    options.xaxis=None
    options.yaxis=None
    plot1DNLL(False,"r")
    options.xaxis=cachexaxis
    options.yaxis=cacheyaxis
    ps.insert(0,mh)
    points.append(ps)
    k+=1
    loffiles.pop(0)
    options.outname=cache

  points.sort(key=lambda x: x[0])

  bestFit = r.TGraph()
  oneSigma = r.TGraphAsymmErrors()
  twoSigma = r.TGraphAsymmErrors()
  
  for p,point in enumerate(points):
    bestFit.SetPoint(p,point[0],point[1])
    oneSigma.SetPoint(p,point[0],point[1])
    twoSigma.SetPoint(p,point[0],point[1])
    oneSigma.SetPointError(p,0.,0.,point[3],point[2])
    twoSigma.SetPointError(p,0.,0.,point[5],point[4])
  
  bestFit.SetLineColor(r.kBlack)
  bestFit.SetLineWidth(3)
  bestFit.SetLineStyle(1)

  twoSigma.SetLineColor(r.kBlack)
  twoSigma.SetLineStyle(1)
  twoSigma.SetLineWidth(3)
  twoSigma.SetFillColor(r.kGreen)

  oneSigma.SetLineColor(r.kBlack)
  oneSigma.SetLineStyle(1)
  oneSigma.SetLineWidth(3)
  oneSigma.SetFillColor(r.kGreen-3)

  if not options.legend: leg = r.TLegend(0.58,0.66,0.85,0.89)
  else: leg = r.TLegend(float(options.legend.split(',')[0]),float(options.legend.split(',')[1]),float(options.legend.split(',')[2]),float(options.legend.split(',')[3]))
  #leg.SetFillColor(0)
  #leg.SetTextSize(0.045)
  leg.SetTextAlign(12)
  leg.SetBorderSize(0)
  #leg.AddEntry(oneSigma,"#pm 1 #sigma uncertainty","FL")
  leg.AddEntry(oneSigma,"68% CL","FL")
  #if not options.do1sig : leg.AddEntry(twoSigma,"#pm 2 #sigma uncert","FL")
  if not options.do1sig : leg.AddEntry(twoSigma,"95% CL","FL")

  dummyHist.SetStats(0)
  #dummyHist.GetYaxis().SetTitle("#sigma/#sigma_{SM}")
  dummyHist.GetYaxis().SetTitle("#hat{#mu}")
  dummyHist.GetYaxis().SetTitleSize(0.05)
  dummyHist.GetYaxis().SetTitleOffset(0.7)
  #dummyHist.GetYaxis().SetTitle("#mu = #sigma/#sigma_{SM} ")

  dummyHist.GetYaxis().SetRangeUser(twoSigma.GetMinimum(),twoSigma.GetMaximum())

  if options.xaxis: 
    dummyHist.GetXaxis().SetRangeUser(float(options.xaxis[0]),float(options.xaxis[1]))
  if options.yaxis: dummyHist.GetYaxis().SetRangeUser(float(options.yaxis.split(',')[0]),float(options.yaxis.split(',')[1]))

  dummyHist.Draw("AXISG")
  canv.SaveAs("lc_debug.pdf")
  if not options.do1sig:  twoSigma.Draw("LE3same")
  oneSigma.Draw("LE3same")
  if options.xaxis:
        axmin = float(options.xaxis[0])
        axmax = float(options.xaxis[1])
  else:
    axmin = 115
    axmax = 135
  line = r.TLine(axmin,1.,axmax,1.)
  line.SetLineColor(13)
  line.SetLineWidth(3)
  line.Draw("same")
  line0 = r.TLine(axmin,0.,axmax,0.)
  line0.SetLineColor(13)
  line0.SetLineStyle(2)
  line0.SetLineWidth(3)
  line0.Draw("same")
  bestFit.Draw("Lsame")

  drawGlobals(canv)
  
  if (addRunIMH):
    bestFitBand1 = r.TBox(125.09-0.24,float(options.yaxis.split(",")[0]),125.09+0.24,float(options.yaxis.split(",")[1])) # ROOT is bad at colouring inside the lines!
    bestFitBand1.SetFillColor(38)
    bestFitBand1.SetFillStyle(3001)
    bestFitBand1.SetLineStyle(3)
    bestFitBand1.SetLineColor(38)
  
    bestFitLine = r.TLine(125.09,float(options.yaxis.split(",")[0]),125.09,float(options.yaxis.split(",")[1]))
    bestFitLine.SetLineWidth(2)
    bestFitLine.SetLineColor(r.kBlack)

    dummy = r.TBox(0,0,0,0);
    dummy.SetFillColor(38)
    dummy.SetFillStyle(3001)
    dummy.SetLineWidth(2)
    dummy.SetLineColor(r.kBlack)
    bestFitBand1.Draw("LE3same ")
    bestFitLine.Draw("same ")
    leg.AddEntry(dummy,"m_{H} = 125.09 #pm 0.24 GeV","FL")
  # draw legend
  leg.Draw()
  canv.SetGrid()
  canv.SetTicks(1,1)
  canv.RedrawAxis()

  # print canvas
  canv.Update()
  if not options.batch: raw_input("Looks ok?")
  canv.Print('%s.pdf'%options.outname)
  canv.Print('%s.png'%options.outname)
  canv.Print('%s.C'%options.outname)
  canv.SetName(options.outname)
  outf.cd()
  canv.Write()

def run():
  if options.verbose:
    print options.method
    print options.files
    print options.colors
    print options.styles
    print options.widths
    print options.names

  if options.method=='pval' or options.method=='limit' or options.method=='maxlh':
    runStandard()
  elif options.method=='mh' or options.method=='mu' or options.method=='rv' or options.method=='rf' or options.method=='mpdfchcomp'  or options.method=='perprocchcomp' or options.method=='mpdfmaxlh':
    path = os.path.expandvars('$CMSSW_BASE/src/flashggFinalFit/Plots/FinalResults/rootPalette.C')
    if not os.path.exists(path):
      sys.exit('ERROR - Can\'t find path: '+path) 
    r.gROOT.ProcessLine(".x "+path)
    path = os.path.expandvars('$CMSSW_BASE/src/flashggFinalFit/Plots/FinalResults/ResultScripts/GraphToTF1.C')
    if not os.path.exists(path):
      sys.exit('ERROR - Can\'t find path: '+path) 
    r.gROOT.LoadMacro(path)
    if options.method=='mpdfchcomp':
      plotMPdfChComp("perTag")
    if options.method=='perprocchcomp':
      plotMPdfChComp("perProc")
    elif options.method=='mpdfmaxlh':
      plotMPdfMaxLH()
    else:
      if len(options.xvar)>0:
        plot1DNLL(False,options.xvar[0])
      else:
        plot1DNLL(False)
  elif options.method=='mumh':
    #plot2DNLL("MH","r","m_{H} (GeV)","#sigma/#sigma_{SM}")
    plot2DNLL("MH","r","m_{H} (GeV)","#mu")
  elif options.method=='rvrf':
    plot2DNLL("RF","RV","#mu_{ggH,ttH}","#mu_{VBF,VH}")
  elif options.method=='cvcf':
    plot2DNLL("kappa_V","kappa_F","#kappa_{V}","#kappa_{f}")
  elif options.method=='xdm':
    plot2DNLL("x","deltaM","x","#Delta m (GeV)")
  elif options.method=='kglukgam':
    plot2DNLL("kappa_gam","kappa_g","#kappa_{#gamma}","#kappa_{g}")

# __MAIN__

if options.datfile:
  d = open(options.datfile)
  for line in d.readlines():
    if line.startswith('#'): continue
    if line=='\n': continue
    config={}
    line = line.replace('\=','EQUALS')
    for opt in line.split(':'):
      #print opt.split('=')[0]
      config[opt.split('=')[0]] = opt.split('=')[1].replace('EQUALS','=').strip('\n').split(',')
      #print line 
      #print opt.split('=')[0], " " , opt.split('=')[1].replace('EQUALS','=').strip('\n').split(',')  
    for opt in ['colors','styles','widths']:
      if opt in config.keys():
        config[opt] = [int(x) for x in config[opt]]
    
    for key, item in config.items():
      if len(item)==1 and key in ['method','text','outname','legend','yaxis','xaxis']:
        item=item[0].strip('\n')
      setattr(options,key,item)

    if options.verbose: print options
    run()


else:
  run()

print 'All canvases written to:', outf.GetName()
outf.Close()
