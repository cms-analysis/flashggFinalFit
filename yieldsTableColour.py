#!/usr/bin/env python

import os
import fnmatch
import sys
import time
import ROOT as r
import math

sqrts=13
lumi=35.9

from optparse import OptionParser
parser = OptionParser()
parser.add_option("-d","--dir")
parser.add_option("--factor",default=1.)
parser.add_option("-i","--input",default="numbers.txt")
parser.add_option("-s","--siginput",default="signumbers.txt")
parser.add_option("-w","--workspaces",default="")
parser.add_option("-v","--sigworkspaces",default="")
parser.add_option("-u","--bkgworkspaces",default="")
parser.add_option("-o","--order",default="",help="tell teh script what order to print tags and procs in. Usage proc1,proc2,proc3..:tag1,tag2,tag3...")
parser.add_option("-f","--flashggCats",default="UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,VBFTag_0,VBFTag_1,VBFTag_2,TTHHadronicTag,TTHLeptonicTag,ZHLeptonicTag,WHLeptonicTag,VHLeptonicLooseTag,VHHadronicTag,VHMetTag")
parser.add_option("-t","--total",dest="total",default=False,action="store_true",help="do total line in colour plot (always on in table)")
parser.add_option("--verbose",default=0)
(options,args) = parser.parse_args()

if not (options.workspaces ==""):
  #tpMap = {"GG2H":"ggh","VBF":"vbf","TTH":"tth","QQ2HLNU":"wh","QQ2HLL":"zh","WH2HQQ":"wh","ZH2HQQ":"zh"}
  tpMap = {"GG2H":"ggh","VBF":"vbf","TTH":"tth","QQ2HLNU":"wh","QQ2HLL":"zh","WH2HQQ":"wh","ZH2HQQ":"zh","testBBH":"bbh","testTHQ":"th","testTHW":"th"}
  #stage 1 ggH
  #tpMap = {"GG2H_FWDH":"ggh","GG2H_VBFTOPO_JET3VETO":"ggh","GG2H_VBFTOPO_JET3":"ggh","GG2H_0J":"ggh",
  #         "GG2H_1J_PTH_0_60":"ggh","GG2H_1J_PTH_60_120":"ggh","GG2H_1J_PTH_120_200":"ggh","GG2H_1J_PTH_GT200":"ggh",
  #         "GG2H_GE2J_PTH_0_60":"ggh","GG2H_GE2J_PTH_60_120":"ggh", "GG2H_GE2J_PTH_120_200":"ggh", "GG2H_GE2J_PTH_GT200":"ggh",
  #         "VBF":"vbf","TTH":"tth","QQ2HLNU":"wh","QQ2HLL":"zh","WH2HQQ":"wh","ZH2HQQ":"zh","testBBH":"bbh","testTHQ":"th","testTHW":"th"}
  for ws in options.workspaces.split(","):
    oldProc = ""
    newProc = ""
    #if "M125" not in ws: continue #shouldn't be any but just in case
    for stxsProc in tpMap:
      if "%s.root"%stxsProc in ws:
        if newProc != "": 
          print ws
          print stxsProc
          print newProc
          exit("more than one STXS process name found in file name - wtf, shouldn't happen, exiting...")
        newProc = stxsProc
        oldProc = tpMap[stxsProc]
    print "\nrunning the yields code for process",newProc
    os.system("./Signal/bin/SignalFit -i %s --checkYield 1 | grep Tag | grep _125_ > %s.%s.old"%(ws,options.input,newProc))
    oldFile = open("%s.%s.old"%(options.input,newProc),'r')
    newFile = open("%s.%s.new"%(options.input,newProc),'w')
    for line in oldFile.readlines():
      line = line.replace(oldProc,newProc)
      newFile.write(line)
    oldFile.close()
    newFile.close()
  os.system("rm %s*.old"%(options.input))
  os.system("cat %s*.new > %s"%(options.input,options.input))
  os.system("rm %s*.new"%(options.input))

procs=[]
tags=[]
_tags=options.flashggCats.split(",")
weights=[]
entries=[]
yields=[]
perTagYields={}
perProcYields={}
matrix1={}
matrix2={}
Arr={}

effSigma={}
hmSigma={}
bkgYield={}
options.factor=float(options.factor)
with open(options.input) as i:
  lines  = i.readlines()
  for line in lines:
    #print line
    if "intLumi" in line: lumi=float(line[line.find("value")+6:])
    if "pdfWeight" in line : continue 
    if "NoTag" in line : continue 
    line=line.replace("Tag_","Tag ")
    line=line.replace("Tag"," Tag")
    #line=line.replace("TTH","TTH ")
    #line=line.replace("WH","WH ")
    #line=line.replace("ZH","ZH ")
    #line=line.replace("VH","VH ")
    line=line.replace("TTHL","TTH L")
    line=line.replace("TTHH","TTH H")
    line=line.replace("WHL","WH L")
    line=line.replace("ZHL","ZH L")
    line=line.replace("VH","VH ")
    line=line.replace(",","_ ")
    line=line.replace("\n","")
    words=line.split("_")
    #words=line.split("_125_13TeV_")
    procs.append(words[0])
    tags.append(words[3])
    #morewords = words[1].split("_")
    #tags.append(morewords[0])
    weights.append(float(words[4]))
    #weights.append(float(morewords[1]))
    entries.append(float(words[4]))
    #entries.append(float(morewords[1]))
    list=[words[0],words[3],options.factor*float(words[4])]
    #list=[words[0],morewords[0],options.factor*float(morewords[1])]
    yields.append(list)
    continue

with open(options.siginput) as i:
  lines  = i.readlines()
  for line in lines:
    if not "TABLE" in line: continue
    if not "sig_mass" in line: continue
    line=line.replace("m125_","=")
    line=line.replace("Tag_","Tag ")
    line=line.replace("AllCats","Total")
    line=line.replace("Tag"," Tag")
    line=line.replace("TTH","TTH ")
    line=line.replace("WH","WH ")
    line=line.replace("ZH","ZH ")
    line=line.replace("VH","VH ")
    words=line.split("=")  
    print words
    effSigma[words[1]]=words[3]
    hmSigma[words[1]]=words[5]

print effSigma
print hmSigma

flashggCats=""
for x in effSigma.keys():
  if (flashggCats==""):
    flashggCats=x
  else:
    flashggCats=flashggCats+","+x
counter=0;
for x in effSigma.keys():
  
  exec_line='$CMSSW_BASE/src/flashggFinalFit/Background/bin/makeBkgPlots -b %s -o tmp.root -d tmp -c %d --sqrts 13 --intLumi 2.610000 --massStep 1.000 --nllTolerance 0.050 -L 125 -H 125 --higgsResolution %f --isMultiPdf --useBinnedData --doBands -f %s| grep TABLE > bkg.tmp'%(options.bkgworkspaces,counter,float(effSigma[x]),flashggCats.replace("Tag ","Tag_").replace(" Tag","Tag").replace("TTH ","TTH").replace("WH ","WH").replace("ZH ","ZH").replace("VH ","VH"))
  print exec_line
  os.system(exec_line)
  counter=counter+1

  with open('bkg.tmp') as i:
    lines  = i.readlines()
    for line in lines:
      if not "TABLE" in line: continue
      line=line.replace("Tag_","Tag ")
      line=line.replace("Tag"," Tag")
      line=line.replace("TTH","TTH ")
      line=line.replace("WH","WH ")
      line=line.replace("ZH","ZH ")
      line=line.replace("VH","VH ")
      print "LCDEBUG ", line
      words=line.split(',')
      print "LCDEBUG ", words[1], ", ", words[3]  
      bkgYield[words[1]]=float(words[3])
      print "LCDEBUG ", bkgYield
bkgAllYield=0
for x in bkgYield.values(): bkgAllYield=bkgAllYield+x
bkgYield["Total"]=bkgAllYield

print "DEBUG bkg YIELD"
bkgYield

'''      
print "INTLUMI ", lumi, "/pb"
print "PROC     YIELD    WEIGHT"
# yields by process
for proc in sorted(set(procs)):
  perProcYield=0.
  perProcWeight=0.
  #print "----> ", proc, "<-----"
  for i in range(0,len(procs)):
    #print procs[i] , " -- ", proc
    if (procs[i]==proc) :
      perProcYield = perProcYield + entries[i]
      perProcWeight = perProcWeight + weights[i]
  if "_" in proc :
    print proc, "  ", perProcYield, "    ", perProcWeight
  else :
    print proc, "    ", perProcYield, "    ", perProcWeight

print  

print "TAG     YIELD (M125)    WEIGHT (M125)"
# yields by process
for tag in sorted(set(tags)):
  perTagYield=0.
  perTagWeight=0.
  #print "----> ", proc, "<-----"
  for i in range(0,len(tags)):
    #print procs[i] , " -- ", proc
    if (tags[i]==tag and ("125" in procs[i]) ):
      perTagWeight = perTagWeight + weights[i]
      perTagYield = perTagYield + entries[i]
      #print i, entries[i], ", ",weights[i]
  if "_" in proc :
    print tag, "  ", perTagYield, "    ",perTagWeight
  else :
    print tag, "    ", perTagYield, "    ",perTagWeight
'''  
for proc in sorted(set(procs)):
  print 
  print  "TAG ONLY - " , proc 
  print "TAG     YIELD     WEIGHT"
  # yields by process
  perTagWeightAll=0
  for tag in sorted(set(tags)):
    perTagWeight=0.
    #print "----> ", proc, "<-----"
    for i in range(0,len(tags)):
      #print procs[i] , " -- ", proc
      if (tags[i]==tag and procs[i]==proc ):
        perTagWeight = perTagWeight + weights[i]
    print tag, "    ",perTagWeight
    perTagWeightAll=perTagWeightAll+perTagWeight

for i in range(0,len(yields)):
 procKey=yields[i][0]
 tagKey=yields[i][1]
 w=yields[i][2]
 
 if tagKey in Arr:
   if procKey in Arr[tagKey]:
     print "should not haptagKeyen"
   else:
     Arr[tagKey][procKey]=w 
 else:
  Arr[tagKey]={procKey:w}




#print "perTagYields ", perTagYields
#print "perProcYields ", perProcYields

line=""
for p in Arr :
  line="Procecces    " 
  for t in Arr[p]:
    line=line+"  "+t
  break
print line


Arr["Total"]={"Total":0}
#for x in Arr.values()[1].keys():
for x in Arr.values()[0].keys():
#for x in Arr.values()[2].keys():
  Arr["Total"][x]=0

print Arr["Total"]




line=""
for t in Arr :
  Arr[t]["Total"]=0
  print " consider tag " ,t , " looping through", Arr[t]
  for p in Arr[t]:
    if p=="Total": continue
    Arr[t]["Total"]= Arr[t]["Total"]+Arr[t][p]
  line=line+" "+str('Total'+":"+'%.2f'%Arr[t]["Total"])

'''
for t in Arr :
  #print p
  line=t+"    " 
  Arr[t]["All"]=0
  for p in Arr[t]:
    #print t
    if p=="All": continue
    line = line+" "+str(p+":"+'%.2f'%Arr[t][p])
    Arr[t]["All"]= Arr[t]["All"]+Arr[t][p]
    print line
  line=line+" "+str('All'+":"+'%.2f'%Arr[t]["All"])
  print line
'''

nProcs=len(Arr.values()[0])
nTags=len(Arr.keys()[0])

for x in Arr.keys():
   for y in Arr.values()[0].keys() :
      if x == "Total": continue
      Arr["Total"][y] = Arr["Total"][y] +Arr[x][y]

print " Done : Arr[Total]", Arr["Total"]

print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
line="\\begin{tabular}{ |r | c | c  | c|"
for x in range(0,nProcs):
 line = line + " c | "
line = line + "}"
print line
print "\\hline"
#print "\\multicolumn{%d}{|l|}{Expected Signal} \\\\"%(nProcs+3)
print "\\hline"
print "\\hline"
print "\\multirow{2}{*}{Event Categories} &\multicolumn{%d}{|l|}{SM 125GeV Higgs boson expected signal} & Bkg\\\\ \\cline{2-%d}"%(nProcs+2,nProcs+3)
line="  &  "
for p in Arr.values()[0].keys() :
 #print p
  line=line+ p + " & "
line =line+"  $\\sigma_{eff} $(GeV)  & $\\sigma_{HM} $ (GeV) & (GeV$^-1$) \\\\ "
print line 
print "\\hline"
print "\\hline"

dataLines=[]
for t in Arr :
  #if t=='Total': continue #ED MUST FIX
  #print p
  lineCat=t+" &   " 
  line=""
  for p in Arr[t]:
    if p=="Total": continue
    line = line+" &  "+str('%.2f'%Arr[t][p])
  Allline=" "+str('%.2f'%Arr[t]["Total"])
  #dataLines.append( lineCat + Allline+ " "+line+ " & & &" )#+"& %s & %s & %.2f\\\\"%(effSigma[t],hmSigma[t],float(bkgYield[t]) ))
  print "\neffSigma is\n",effSigma,"\n"
  esig =effSigma[t]
  hmsig =hmSigma[t]
  bkgy=0
  #bkgy=bkgYield[t]
  dataLines.append( lineCat + Allline+ " "+line+ "& %s & %s & %.2f\\\\"%(effSigma[t],hmSigma[t],bkgy ))

dataLines.sort()
for l in dataLines :
  print l

print "\\hline"
print "\\hline"
print "\end{tabular}"

print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
line="\\begin{tabular}{ |r | c | c | c  |"
for x in range(0,nProcs):
 line = line + " c | "
line = line + "}"
print line
print "\\hline"
i#print "\\multicolumn{%d}{|l|}{Expected Signal} \\\\"%(nProcs+3)
print "\\hline"
print "\\hline"
print "\\multirow{2}{*}{Event Categories} &\multicolumn{%d}{|l|}{SM 125GeV Higgs boson expected signal} & Bkg \\\\ \\cline{2-%d}"%(nProcs+2,nProcs+3)
line="  &  "

procList=[]
if (options.order==""): procList=Arr.values()[0].keys() 
else : procList = options.order.split(":")[0].split(",")
print "procList", procList
for p in procList:
 #print p
  line=line+ p + " & "
line =line+"  $\\sigma_{eff} $  & $\\sigma_{HM} $ & (GeV$^{-1}$) \\\\ "
print line 
print "\\hline"
print "\\hline"

dataLines=[]
tagList=[]
if (options.order==""): 
  tagList=Arr 
else : 
  tagList = options.order.split(":")[1].split(",")

for t in tagList :
  #if t=='Total': continue #ED MUST FIX
  #print p
  lineCat=t+" &   " 
  line=""
  for p in procList:
    if p=="Total": continue
    print "Arr[t]",Arr[t]
    line = line+" &  "+str('%.2f \%%'%(100*Arr[t][p]/Arr[t]["Total"]))
  Allline=" "+str('%.2f'%Arr[t]["Total"])
  #bkgy=0
  if not t in bkgYield.keys():
    print "ERROR COULD NOT FIND KEY ", t , " in list of Bkg Numbers:"
    print bkgYield
    exit(1)
  bkgy=bkgYield[t]
  dataLines.append( lineCat + Allline+ " "+line+"& %.2f & %.2f & %.2f \\\\"%(float(effSigma[t]),float(hmSigma[t]),bkgy))
  #dataLines.append( lineCat + Allline+ " "+line+ "& & &")#"& %.2f & %.2f & %.2f \\\\"%(float(effSigma[t]),float(hmSigma[t]),float(bkgYield[t])))

#dataLines.sort()
for l in dataLines :
  print l

print "\\hline"
print "\\hline"
print "\end{tabular}"

print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"

print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
line="\\begin{tabular}{ |r | c | c | c  | c |"
for x in range(0,nProcs):
 line = line + " c | "
line = line + "}"
print line
print "\\hline"
i#print "\\multicolumn{%d}{|l|}{Expected Signal} \\\\"%(nProcs+3)
print "\\hline"
print "\\hline"
print "\\multirow{2}{*}{Event Categories} &\multicolumn{%d}{|l|}{SM 125GeV Higgs boson expected signal} & Bkg & S/(S+B) \\\\ \\cline{2-%d}"%(nProcs+2,nProcs+3)
line="  &  "

procList=[]
if (options.order==""): procList=Arr.values()[0].keys() 
else : procList = options.order.split(":")[0].split(",")
for p in procList:
 #print p
  line=line+ p + " & "
line =line+"  $\\sigma_{eff} $  & $\\sigma_{HM} $ & (GeV$^{-1}$) & \\\\ "
print line 
print "\\hline"
print "\\hline"

dataLines=[]
tagList=[]
if (options.order==""): 
  tagList=Arr 
else : 
  tagList = options.order.split(":")[1].split(",")

naiveExpecteds=[]
for t in tagList :
  #print p
  if t=="Total" : continue
  lineCat=t+" &   " 
  line=""
  for p in procList:
    if p=="Total": continue
    line = line+" &  "+str('%.2f \%%'%(100*Arr[t][p]/Arr[t]["Total"]))
  Allline=" "+str('%.2f'%Arr[t]["Total"])
  #bkgy=0
  if not t in bkgYield.keys():
    print "ERROR COULD NOT FIND KEY ", t , " in list of Bkg Numbers:"
    print bkgYield
    exit(1)
  bkgy=bkgYield[t]
  naiveExp=(0.68*Arr[t]["Total"])/(2*float(effSigma[t])*bkgy + 0.68*Arr[t]["Total"] )
  dataLines.append( lineCat + Allline+ " "+line+"& %.2f & %.2f & %.2f & %.2f\\\\"%(float(effSigma[t]),float(hmSigma[t]),bkgy,naiveExp ))
  naiveExpecteds.append(naiveExp)

# now do total line
t=="Total" 
lineCat=t+" &   " 
line=""
for p in procList:
   if p=="Total": continue
   line = line+" &  "+str('%.2f \%%'%(100*Arr[t][p]/Arr[t]["Total"]))
Allline=" "+str('%.2f'%Arr[t]["Total"])
  #bkgy=0
if not t in bkgYield.keys():
    print "ERROR COULD NOT FIND KEY ", t , " in list of Bkg Numbers:"
    print bkgYield
    exit(1)
bkgy=bkgYield[t]
totalNaiveExp=0.
for n in naiveExpecteds:
  totalNaiveExp=totalNaiveExp+(n**2)
totalNaiveExp=(totalNaiveExp)**(0.5)
#dataLines.append( lineCat + Allline+ " "+line+"& %.2f & %.2f & %.2f & %.2f\\\\"%((2.0),(2.0),bkgy,totalNaiveExp)) #ED MUST FIX (original line below)
dataLines.append( lineCat + Allline+ " "+line+"& %.2f & %.2f & %.2f & %.2f\\\\"%(float(effSigma[t]),float(hmSigma[t]),bkgy,totalNaiveExp))
  #dataLines.append( lineCat + Allline+ " "+line+ "& & &")#"& %.2f & %.2f & %.2f \\\\"%(float(effSigma[t]),float(hmSigma[t]),float(bkgYield[t])))

#dataLines.sort()
for l in dataLines :
  print l

print "\\hline"
print "\\hline"
print "\end{tabular}"

print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"

doTotals = options.total
if doTotals:
  s_sb_hist= r.TH1F("s_sb","",len(tagList),0,len(tagList)-1)
  sigmaEff_hist= r.TH1F("sigEff","",len(tagList),0,len(tagList)-1)
  sigmaHM_hist= r.TH1F("sigHM","",len(tagList),0,len(tagList)-1)
else:
  s_sb_hist= r.TH1F("s_sb","",len(tagList)-1,0,len(tagList)-2)
  sigmaEff_hist= r.TH1F("sigEff","",len(tagList)-1,0,len(tagList)-2)
  sigmaHM_hist= r.TH1F("sigHM","",len(tagList)-1,0,len(tagList)-2)
content_hists={}
for i in range(0,nProcs):
 pName=Arr.values()[0].keys()[i]
 if not doTotals and pName=="Total":
   print "ED DEBUG ============================================="
   print "pName is",pName
   print "ED DEBUG ============================================="
   continue
 print "making hist with name " , pName
 if doTotals: content_hists[pName]=r.TH1F("content_%s"%pName,"content_%s"%pName,len(tagList),0,len(tagList)-1)
 else: content_hists[pName]=r.TH1F("content_%s"%pName,"content_%s"%pName,len(tagList)-1,0,len(tagList)-2)

print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
#print "\\resizebox{\\textwidth}{!}{"
line="\\begin{tabular}{ |r | c | c | c  | c | c |"
for x in range(0,nProcs):
 line = line + " c | "
line = line + "}"
print line
print "\\hline"
i#print "\\multicolumn{%d}{|l|}{Expected Signal} \\\\"%(nProcs+3)
print "\\hline"
print "\\hline"
print "\\multirow{2}{*}{Event Categories} &\multicolumn{%d}{|l|}{SM 125GeV Higgs boson expected signal} & Bkg & Bkg &naive expected\\\\ \\cline{2-%d}"%(nProcs+2,nProcs+3)
#print "\\multirow{2}{*}{Event Categories} &\multicolumn{%d}{|l|}{SM 125GeV Higgs boson expected signal} & Bkg & Bkg &wise expected\\\\ \\cline{2-%d}"%(nProcs+2,nProcs+3)
line="  &  "

procList=[]
if (options.order==""): procList=Arr.values()[0].keys() 
else : procList = options.order.split(":")[0].split(",")
for p in procList:
 #print p
  line=line+ p + " & "
#line =line+"  $\\sigma_{eff} $  & $\\sigma_{HM} $ & (GeV$^{-1}$) & (GeV$^{-1}$ fb^{-1} )& \\\\ "
line =line+"  $\\sigma_{eff} $  & $\\sigma_{HM} $ & (GeV$^{-1}$) & (GeV$^{-1}$ $fb^{-1}$ )& \\\\ "
print line 
print "\\hline"
print "\\hline"

dataLines=[]
tagList=[]
if (options.order==""): 
  tagList=Arr 
else : 
  tagList = options.order.split(":")[1].split(",")
  
naiveExpecteds=[]
iTag=0
vbfTotals = [0.,0.,0.,0.,0.]
for t in tagList :
  #print p
  if t=="Total" : continue
  lineCat=t+" &   " 
  line=""
  for p in procList:
    if p=="Total": continue
    val=100*Arr[t][p]/Arr[t]["Total"]
    line = line+" &  "+str('%.2f \%%'%(val))
    if options.verbose: print " filling content hist ", p, " for bin ", len(tagList)-iTag, " =", tagList[iTag], " ==", val
    if doTotals: content_hists[p].SetBinContent(len(tagList)-iTag,val)
    else: content_hists[p].SetBinContent(len(tagList)-1-iTag,val)
    #content_hists[p].GetXaxis().SetBinLabel(iTag,'%s'%t)
  Allline=" "+str('%.2f'%Arr[t]["Total"])
  #content_hists[p].GetXaxis().SetBinLabel(iTag,'Total')
  #bkgy=0
  if not t in bkgYield.keys():
    print "ERROR COULD NOT FIND KEY ", t , " in list of Bkg Numbers:"
    print bkgYield
    exit(1)
  bkgy=bkgYield[t]
  naiveExp=(0.68*Arr[t]["Total"])/(2*float(effSigma[t])*bkgy)**(0.5) #think should be s/sqrt(s+b), rather than s/sqrt(b)
  oldNaiveExp=(0.68*Arr[t]["Total"])/(2*float(effSigma[t])*bkgy)**(0.5)
  #naiveExp=(0.68*Arr[t]["Total"])/((2*float(effSigma[t])*bkgy) + 0.68*Arr[t]["Total"])**(0.5)
  vbfNaiveExp=(0.68*Arr[t]["VBF"])/((2*float(effSigma[t])*bkgy) + 0.68*Arr[t]["GG2H"] + 0.68*Arr[t]["VBF"])**(0.5)
  fancyExp=(2*( (0.68*Arr[t]["Total"]+2*float(effSigma[t])*bkgy) * math.log(1 + 0.68*Arr[t]["Total"]/(2*float(effSigma[t])*bkgy)) - 0.68*Arr[t]["Total"] ))**0.5 #2*((s+b)ln(1+s/b)-s)
  vbfFancyExp=(2*( (0.68*Arr[t]["VBF"]+2*float(effSigma[t])*bkgy+0.68*Arr[t]["GG2H"]) * math.log(1 + 0.68*Arr[t]["VBF"]/(2*float(effSigma[t])*bkgy+0.68*Arr[t]["GG2H"])) - 0.68*Arr[t]["VBF"] ))**0.5
  if "VBF" in t and options.verbose:
    print "\nfor tag",t
    print "oldNaiveExp =",oldNaiveExp
    vbfTotals[0] += oldNaiveExp**2
    print "naiveExp =",naiveExp
    vbfTotals[1] += naiveExp**2
    print "vbfNaiveExp =",vbfNaiveExp
    vbfTotals[2] += vbfNaiveExp**2
    print "fancyExp =",fancyExp
    vbfTotals[3] += fancyExp**2
    print "vbfFancyExp =",vbfFancyExp
    vbfTotals[4] += vbfFancyExp**2
  s_sb_value=(0.68*Arr[t]["Total"])/(0.68*Arr[t]["Total"] + 2*float(effSigma[t])*bkgy)
  dataLines.append( lineCat + Allline+ " "+line+"& %.2f & %.2f & %.2f & %.2f & %.2f\\\\"%(float(effSigma[t]),float(hmSigma[t]),bkgy,bkgy/options.factor,naiveExp ))
  #dataLines.append( lineCat + Allline+ " "+line+"& %.2f & %.2f & %.2f & %.2f & %.2f\\\\"%(float(effSigma[t]),float(hmSigma[t]),bkgy,bkgy/options.factor,fancyExp ))
  if doTotals:
    sigmaEff_hist.SetBinContent(len(tagList)-iTag,float(effSigma[t]))
    sigmaHM_hist.SetBinContent(len(tagList)-iTag,float(hmSigma[t]))
    s_sb_hist.SetBinContent(len(tagList)-iTag,float(s_sb_value))
  else:
    sigmaEff_hist.SetBinContent(len(tagList)-1-iTag,float(effSigma[t]))
    sigmaHM_hist.SetBinContent(len(tagList)-1-iTag,float(hmSigma[t]))
    s_sb_hist.SetBinContent(len(tagList)-1-iTag,float(s_sb_value))
  naiveExpecteds.append(naiveExp)
  #naiveExpecteds.append(fancyExp)
  iTag=iTag+1
if options.verbose:
  print "\nVBF total significances"
  print "oldNaive",(vbfTotals[0])**0.5
  print "naive",(vbfTotals[1])**0.5
  print "vbfNaive",(vbfTotals[2])**0.5
  print "fancy",(vbfTotals[3])**0.5
  print "vbfFancy",(vbfTotals[4])**0.5
  
# now do total line
#print "Are we doing totals?",doTotals
t=="Total" 
lineCat=t+" &   " 
line=""
for p in procList:
   if p=="Total": continue
   val=100*Arr[t][p]/Arr[t]["Total"]
   line = line+" &  "+str('%.2f \%%'%(100*Arr[t][p]/Arr[t]["Total"]))
   #print " filling content hist ", p, " for bin ", 1, " =", t, " ==", val
   if doTotals: content_hists[p].SetBinContent(1,val)
Allline=" "+str('%.2f'%Arr[t]["Total"])
  #bkgy=0
if not t in bkgYield.keys():
    print "ERROR COULD NOT FIND KEY ", t , " in list of Bkg Numbers:"
    print bkgYield
    exit(1)
bkgy=bkgYield[t]
totalNaiveExp=0.
for n in naiveExpecteds:
  totalNaiveExp=totalNaiveExp+(n**2)
totalNaiveExp=(totalNaiveExp)**(0.5)
#dataLines.append( lineCat + Allline+ " "+line+"& %.2f & %.2f & %.2f & %.2f & %.2f\\\\"%((2.0),(2.0),bkgy,bkgy/options.factor,totalNaiveExp)) #ED MUST FIX
dataLines.append( lineCat + Allline+ " "+line+"& %.2f & %.2f & %.2f & %.2f & %.2f\\\\"%(float(effSigma[t]),float(hmSigma[t]),bkgy,bkgy/options.factor,totalNaiveExp))
  #dataLines.append( lineCat + Allline+ " "+line+ "& & &")#"& %.2f & %.2f & %.2f \\\\"%(float(effSigma[t]),float(hmSigma[t]),float(bkgYield[t])))
#sigmaEff_hist.SetBinContent(1,(2.0)) #ED MUST FIX
if doTotals: sigmaEff_hist.SetBinContent(1,float(effSigma[t]))
#sigmaHM_hist.SetBinContent(1,(2.0))
if doTotals: sigmaHM_hist.SetBinContent(1,float(hmSigma[t]))
#s_sb_hist.SetBinContent(1,float(totalNaiveExp))
#s_sb_value=(0.68*Arr[t]["Total"])/(0.68*Arr[t]["Total"] + 2*(2.0)*bkgy) #ED MUST FIX
s_sb_value=(0.68*Arr[t]["Total"])/(0.68*Arr[t]["Total"] + 2*float(effSigma[t])*bkgy)
if doTotals: s_sb_hist.SetBinContent(len(tagList)-iTag,float(s_sb_value))

#dataLines.sort()
for l in dataLines :
  print l

print "\\hline"
print "\\hline"
#print "\end{tabular}}"
print "\end{tabular}"

print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"

r.gROOT.SetBatch()
r.gStyle.SetOptStat(0)
hstack = r.THStack("hs","")
#colorList=[r.kViolet-7, r.kRed+2, r.kSpring, r.kOrange+7, r.kSpring-7, r.kSpring+3, r.kBlue, r.kBlue+3, r.kAzure+10, r.kAzure+7] #set for ggH,VBF,ttH-type,VH-type
colorList=[r.kBlue, r.kGreen+2, r.kMagenta-7, r.kBlue+3, r.kMagenta-3, r.kMagenta+2, r.kRed, r.kRed+1, r.kOrange+1, r.kOrange+7] #set for ggH,VBF,ttH-type,WH-type,ZH-type (ZZ colors and order)
iColor=0
print "content_hists ", content_hists
numProcs = len(options.order.split(":")[0].split(","))-1
l1 = r.TLegend(0.0,0.94,1.0,0.98)
lExtra = r.TLegend(0.0,0.90,1.0,0.94)
l2 = r.TLegend(0.0,0.9,1.0,0.95)
l3 = r.TLegend(0.0,0.9,1.0,0.95)
nProcLim = 6
if numProcs<=nProcLim:
  l1.SetNColumns(numProcs)
else:
  l1.SetNColumns(nProcLim)
  lExtra.SetNColumns(numProcs-nProcLim)
l2.SetNColumns(2)
l3.SetNColumns(1)
l1.SetTextSize(0.03)
lExtra.SetTextSize(0.03)
l2.SetTextSize(0.09)
l3.SetTextSize(0.07)
l1.SetBorderSize(0)
lExtra.SetBorderSize(0)
l2.SetBorderSize(0)
l3.SetBorderSize(0)
for ih in options.order.split(":")[0].split(","):
 print "DBG ih =" , ih
 if ih=="Total" : continue
 h=content_hists[ih]
 h.SetFillColor(colorList[iColor])
 h.SetLineColor(0)
 h.SetMarkerColor(colorList[iColor])
 h.SetBarWidth(0.9)
 ih = ih.replace("test","")
 ih = ih.replace("TTH","ttH")
 ih = ih.replace("GG2H","ggH")
 ih = ih.replace("BBH","bbH")
 ih = ih.replace("THQ","tHq")
 ih = ih.replace("THW","tHW")
 ih = ih.replace("WH2HQQ","WH hadronic")
 ih = ih.replace("QQ2HLNU","WH leptonic")
 ih = ih.replace("ZH2HQQ","ZH hadronic")
 ih = ih.replace("QQ2HLL","ZH leptonic")
 if iColor<=nProcLim-1: l1.AddEntry(h," "+ih,"f")
 else: lExtra.AddEntry(h," "+ih,"f")
 hstack.Add(h)
 iColor=iColor+1
l2.AddEntry(sigmaEff_hist," #sigma_{eff}","F")
l2.AddEntry(sigmaHM_hist," #sigma_{HM}","F")

l3.AddEntry(s_sb_hist," S/(S+B)","F")

if doTotals: dummyHist= r.TH2F("h1","",100,0.01,100,len(tagList),0,len(tagList)-1)
else: dummyHist= r.TH2F("h1","",100,0.01,100,len(tagList)-1,0,len(tagList)-2)
dummyHist2= r.TH2F("h2","",100,0.01,1.2*sigmaEff_hist.GetMaximum(),len(tagList),0,len(tagList)-1)
dummyHist3= r.TH2F("h2","",100,0.01,1.2*s_sb_hist.GetMaximum(),len(tagList),0,len(tagList)-1)
#dummyHist= r.TH2F("h1","h1",15,0,15,100,0.01,100)
#hstack.Draw()
#hstack.GetYaxis().SetRangeUser(0.001,100)
canv = r.TCanvas("c","c",700,400)
#for i in range(0,len(tagList)-1):
  #if tagList[i]=="Total": continue
  #xax=hstack.GetXaxis()
  #xax.SetBinLabel(xax.FindBin(i),tagList[i])
  #dummyHist.GetYaxis().SetBinLabel(i, tagList[i])
 
pad1 = r.TPad("pad1","pad1",0.15,0.0,0.52,0.95)
pad2 = r.TPad("pad2","pad2",0.53,0.0,0.71,0.95)
pad3 = r.TPad("pad3","pad3",0.73,0.0,0.97,0.95)
#pad1.SetFillColor(r.kRed)
#pad2.SetFillColor(r.kPink)
#pad3.SetFillColor(r.kBlue)
pad1.SetBottomMargin(10)
pad1.SetTopMargin(10)
pad1.SetRightMargin(0.02)
pad1.SetLeftMargin(0)
pad2.SetBottomMargin(10)
pad2.SetTopMargin(10)
pad2.SetRightMargin(0.05)
pad2.SetLeftMargin(0.01)
pad3.SetBottomMargin(10)
pad3.SetTopMargin(10)
pad3.SetRightMargin(0)
pad3.SetLeftMargin(0.05)
pad1.Draw()
pad2.Draw()
pad3.Draw()
pad2.cd()
sigmaEff_hist.SetFillColor(r.kBlue-3)
sigmaEff_hist.GetXaxis().SetLabelSize(0.1)
sigmaEff_hist.GetYaxis().SetLabelSize(0.06)
sigmaEff_hist.GetYaxis().SetLabelOffset(-0.01)
sigmaEff_hist.GetXaxis().SetLabelOffset(9999)
sigmaEff_hist.SetBarWidth(0.4)
sigmaEff_hist.SetBarOffset(0.5)
sigmaEff_hist.SetLineColor(0)
sigmaHM_hist.SetBarWidth(0.4)
sigmaHM_hist.SetBarOffset(0.1)
sigmaHM_hist.SetLineColor(0)
#sigmaHM_hist.SetLineColor(r.kRed+2)
#sigmaHM_hist.SetLineWidth(10)
#sigmaHM_hist.SetLineColor(r.kBlack)
sigmaHM_hist.SetFillColor(r.kRed+2)
#sigmaHM_hist.SetFillStyle(3004)
#sigmaHM_hist.SetBarWidth(0.9)
#dummyHist2.Draw()
sigmaEff_hist.Draw("hbar")
sigmaHM_hist.Draw("hbar same ")
l2.Draw()
#hist2.Draw()
pad3.cd()
s_sb_hist.SetFillColor(r.kRed-3)
s_sb_hist.GetXaxis().SetLabelSize(0.1)
s_sb_hist.GetYaxis().SetLabelSize(0.06)
s_sb_hist.GetYaxis().SetLabelOffset(-0.01)
s_sb_hist.GetXaxis().SetLabelOffset(99999)
s_sb_hist.SetBarWidth(0.9)
s_sb_hist.SetLineColor(0)
#dummyHist2.Draw()
s_sb_hist.Draw("hbar")
l3.Draw()
#hist1.Draw()
pad1.cd()
dummyHist.Draw()
#hstack.Draw("")
#hstack.GetYaxis().SetLimits(0.001,100)
#hstack.GetXaxis().SetLimits(0.001,100)
hstack.Draw("hbar same")
#hstack.GetYaxis().SetRangeUser(0.001,100)
pad1.RedrawAxis()
#hstack.GetXaxis().SetRangeUser(0.001,100)
#hstack.Draw("hbar")
l1.Draw()
lExtra.Draw()
#hist1.SetTitle("x;y;z")
#hist1.Fill(0.5,0.5,1)
#hist1.Draw()
#hist2 = r.TH1F("h2","h2",10,0,1)
#hist2.Fill(0.5)
canv.cd()
lat = r.TLatex()
lat.SetTextFont(42)
lat.SetTextSize(0.025)
lat.SetLineWidth(2)
lat.SetTextAlign(31)
#lat.SetNDC()
offset=0.0
for ih in options.order.split(":")[1].split(","):
 print "DBG ih =" , ih
 if not doTotals and ih=="Total": continue
 lat.SetTextAlign(31)
 tagLabel = ih.replace("TTH","ttH")
 tagLabel = tagLabel.replace(" Tag","")
 tagLabel = tagLabel.replace("Met","MET")
 lat.DrawLatex(0.14,0.82-offset,tagLabel)
 evtCount = "#color[0]{%.1f expected events}"%Arr[ih]["Total"]
 lat.SetTextAlign(11)
 lat.DrawLatex(0.16,0.82-offset,evtCount)
 if doTotals: offset=offset+((0.82-0.05)/len(tagList))
 else: offset=offset+((0.82-0.05)/(len(tagList)-1))

lat.SetTextAlign(31)
lat.SetTextSize(0.04)
lat.DrawLatex(0.5,0.02,"Signal Fraction (%)")
lat.DrawLatex(0.71,0.02,"Width (GeV)")
lat.DrawLatex(0.95,0.02,"S/(S+B) in #pm #sigma_{eff}")
lat.SetTextSize(0.05)
#lat.SetTextSize(0.07)
lat.SetTextAlign(11)
#lat.DrawLatex(0.05,0.95,"#bf{CMS} #it{Preliminary}   H#rightarrow#gamma#gamma")
lat.DrawLatex(0.05,0.95,"#bf{CMS} #it{Simulation}     H#rightarrow#gamma#gamma")
lat.SetTextAlign(31)
#lat.SetTextSize(0.05)
lat.SetTextSize(0.045)
lat.DrawLatex(0.95,0.95,"%.1f fb^{-1} (13 TeV)"%lumi)
pad1.RedrawAxis()
canv.SaveAs("yieldsTablePlot.pdf")
canv.SaveAs("yieldsTablePlot.png")
canv.SaveAs("yieldsTablePlot.root")
canv.SaveAs("yieldsTablePlot.C")
