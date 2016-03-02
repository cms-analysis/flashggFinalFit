#!/usr/bin/env python

import os
import fnmatch
import sys
import time

sqrts=13
lumi=0.

from optparse import OptionParser
parser = OptionParser()
parser.add_option("-d","--dir")
parser.add_option("--factor",default=1.)
parser.add_option("-i","--input",default="numbers.txt")
parser.add_option("-s","--siginput",default="signumbers.txt")
parser.add_option("-w","--workspaces",default="")
parser.add_option("-v","--sigworkspaces",default="")
parser.add_option("-u","--bkgworkspaces",default="")
parser.add_option("-f","--flashggCats",default="UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,UntaggedTag_4,VBFTag_0,VBFTag_1,VBFTag_2,TTHHadronicTag,TTHLeptonicTag,VHHadronicTag,VHTightTag,VHLooseTag,VHEtTag")
(options,args) = parser.parse_args()

if not (options.workspaces ==""):
  print "execute"
  if (len(options.workspaces.split(","))>1) :
    os.system("./Signal/bin/SignalFit -i %s --checkYield 1 | grep Tag | grep _125_ > %s"%(options.workspaces,options.input))
  else:
    os.system("./Background/bin/workspaceTool -i %s --print 1 | grep RooData | grep it > %s"%(options.workspaces,options.input))
    os.system("./Background/bin/workspaceTool -i %s --print 1 | grep intLumi >> %s"%(options.workspaces,options.input))

  if (len(options.workspaces.split(","))>1) :
    os.system("./Signal/bin/SignalFit -i %s --checkYield 1 | grep Tag | grep _125_ > %s"%(options.workspaces,options.input))
  else:
    os.system("./Background/bin/workspaceTool -i %s --print 1 | grep RooData | grep it > %s"%(options.workspaces,options.input))
    os.system("./Background/bin/workspaceTool -i %s --print 1 | grep intLumi >> %s"%(options.workspaces,options.input))

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
    line=line.replace("Tag_","Tag ")
    line=line.replace(",","_ ")
    line=line.replace("\n","")
    words=line.split("_")  
    print words
    procs.append(words[0])
    tags.append(words[3])
    weights.append(float(words[4]))
    entries.append(float(words[4]))
    list=[words[0],words[3],options.factor*float(words[4])]
    yields.append(list)
    continue

with open(options.siginput) as i:
  lines  = i.readlines()
  for line in lines:
    if not "TABLE" in line: continue
    line=line.replace("m125_","=")
    line=line.replace("Tag_","Tag ")
    line=line.replace("AllCats","All")
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
  
  exec_line='$CMSSW_BASE/src/flashggFinalFit/Background/bin/makeBkgPlots -b %s -o tmp.root -d tmp -c %d --sqrts 13 --intLumi 2.610000 --massStep 1.000 --nllTolerance 0.050 -L 125 -H 125 --higgsResolution %f --isMultiPdf --useBinnedData --doBands -f %s| grep TABLE > bkg.tmp'%(options.bkgworkspaces,counter,float(effSigma[x]),flashggCats.replace(" ","_"))
  print exec_line
  os.system(exec_line)
  counter=counter+1

  with open('bkg.tmp') as i:
    lines  = i.readlines()
    for line in lines:
      if not "TABLE" in line: continue
      line=line.replace("Tag_","Tag ")
      print "LCDEBUG ", line
      words=line.split(',')
      print "LCDEBUG ", words[1], ", ", words[3]  
      bkgYield[words[1]]=float(words[3])
      print "LCDEBUG ", bkgYield
bkgAllYield=0
for x in bkgYield.values(): bkgAllYield=bkgAllYield+x
bkgYield["All"]=bkgAllYield

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


Arr["All"]={"All":0}
for x in Arr.values()[1].keys():
  Arr["All"][x]=0

print Arr["All"]




line=""
for t in Arr :
  Arr[t]["All"]=0
  for p in Arr[t]:
    if p=="All": continue
    Arr[t]["All"]= Arr[t]["All"]+Arr[t][p]
  line=line+" "+str('All'+":"+'%.2f'%Arr[t]["All"])

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
      Arr["All"][y] = Arr["All"][y] +Arr[x][y]

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
  #print p
  lineCat=t+" &   " 
  line=""
  for p in Arr[t]:
    if p=="All": continue
    line = line+" &  "+str('%.2f'%Arr[t][p])
  Allline=" "+str('%.2f'%Arr[t]["All"])
  #dataLines.append( lineCat + Allline+ " "+line+ " & & &" )#+"& %s & %s & %.2f\\\\"%(effSigma[t],hmSigma[t],float(bkgYield[t]) ))
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
for p in Arr.values()[0].keys() :
 #print p
  line=line+ p + " & "
line =line+"  $\\sigma_{eff} $  & $\\sigma_{HM} $ & (GeV$^{-1}$) \\\\ "
print line 
print "\\hline"
print "\\hline"

dataLines=[]
for t in Arr :
  #print p
  lineCat=t+" &   " 
  line=""
  for p in Arr[t]:
    if p=="All": continue
    line = line+" &  "+str('%.2f \%%'%(100*Arr[t][p]/Arr[t]["All"]))
  Allline=" "+str('%.2f'%Arr[t]["All"])
  #bkgy=0
  bkgy=bkgYield[t]
  dataLines.append( lineCat + Allline+ " "+line+"& %.2f & %.2f & %.2f \\\\"%(float(effSigma[t]),float(hmSigma[t]),bkgy))
  #dataLines.append( lineCat + Allline+ " "+line+ "& & &")#"& %.2f & %.2f & %.2f \\\\"%(float(effSigma[t]),float(hmSigma[t]),float(bkgYield[t])))

dataLines.sort()
for l in dataLines :
  print l

print "\\hline"
print "\\hline"
print "\end{tabular}"

print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"



