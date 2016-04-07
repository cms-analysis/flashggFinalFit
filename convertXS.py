#!/usr/bin/env python

import os
import fnmatch
import sys
import time

targetSqrts=13
lumi=0.

initialSqrts=8
procs=["ggH","vbfH","WH","ZH","ttH"]
targetValues=[43.92,3.748,1.380,0.8696,0.5085] #at 125.
#initialValues=[]
transportFactors=[]

from optparse import OptionParser
parser = OptionParser()
parser.add_option("-d","--dir",default="")
parser.add_option("-i","--input",default="workspaceContents.txt")
parser.add_option("-r","--fromroot",default="")
parser.add_option("-f","--flashggCats",default="UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,UntaggedTag_4,VBFTag_0,VBFTag_1,VBFTag_2,TTHHadronicTag,TTHLeptonicTag,VHHadronicTag,VHTightTag,VHLooseTag,VHEtTag")
(options,args) = parser.parse_args()

has13TeV=False
with open(options.dir+"../HiggsAnalysis/CombinedLimit/python/PhysicsModel.py") as i:
  lines = i.readlines()
  for line in lines:
    if "13TeV" in line:
      print "[INFO] The required files already contain 13TeV"
      has13TeV=True
      break
if (has13TeV):
  print "[INFO] Nothing to be done, exit"
  exit(0)
else:
  print "[INFO] Adding 13TeV to list of allowed sqrt(s)"
  os.system('sed -i \"s/\'14TeV\'/\'13TeV\',\'14TeV\'/g\"  ../HiggsAnalysis/CombinedLimit/python/PhysicsModel.py')  

#procCounter=-1
#for proc in procs:
#  procCounter=procCounter+1
#  xsFile=options.dir+"../HiggsAnalysis/CombinedLimit/data/lhc-hxswg/sm/xs/"+str(initialSqrts)+"TeV/"+str(initialSqrts)+"TeV-"+proc+".txt"
#  with open(xsFile) as i:
#    lines = i.readlines()
#    for line in lines:
#      words=line.split("	")
#      if not ("125.0" in words[0]) : continue
#      print "proc " , proc , " found ", words[0], " xs ", words[1]
#      xs=(float(words[1]))
#      #initialValues.append(xs)
#      transportFactors.append(targetValues[procCounter]/xs)
#
#
#procCounter=-1
#for proc in procs:
#  procCounter=procCounter+1
#  if not os.path.exists(options.dir+"../HiggsAnalysis/CombinedLimit/data/lhc-hxswg/sm/xs/"+str(targetSqrts)+"TeV"):
#      os.mkdir(options.dir+"../HiggsAnalysis/CombinedLimit/data/lhc-hxswg/sm/xs/"+str(targetSqrts)+"TeV")
#  xsFile=options.dir+"../HiggsAnalysis/CombinedLimit/data/lhc-hxswg/sm/xs/"+str(initialSqrts)+"TeV/"+str(initialSqrts)+"TeV-"+proc+".txt"
#  outFile=options.dir+"../HiggsAnalysis/CombinedLimit/data/lhc-hxswg/sm/xs/"+str(targetSqrts)+"TeV/"+str(targetSqrts)+"TeV-"+proc+".txt"
#  os.system('mkdir -p "../HiggsAnalysis/CombinedLimit/data/lhc-hxswg/sm/xs/%sTeV/"'%str(targetSqrts))  
#  f = open(outFile, 'w')
#  f.write("mH_GeV  XS_pb    Err_Hi     Err_Lo Sca_Hi  Sca_Lo  Pdf_Hi  Pdf_Lo\n")
#  with open(xsFile) as i:
#    lines = i.readlines()
#    for line in lines:
#      if  ("mH" in line) : continue
#      words=line.split("	")
#      #if not("0" in line ) : continue
#      #print line
#      oldxs=(float(words[1]))
#      newxs=oldxs * transportFactors[procCounter]
#      print "proc " , proc , " found ", words[0], " xs ", oldxs, " new XS ",newxs
#      f.write(line.replace(str(oldxs),str("%2.2f"%newxs)))
#  f.close()
