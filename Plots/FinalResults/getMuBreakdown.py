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
parser.add_option("--inputfiles",default="rootfiles.txt")
parser.add_option("-i","--inputvalues",default="values.txt")
(options,args) = parser.parse_args()




os.system("find %s | grep root | grep -v higgs > %s "%(options.dir,options.inputfiles))
os.system("rm %s "%(options.inputvalues))
values={}
with open(options.inputfiles) as i:
  lines  = i.readlines()
  for line  in lines:
    line = line.replace("\n","")
    if not 'root' in line : continue
    print line
    print ("./makeCombinePlots.py --mu -f %s  -b | grep MU "%(line))
    os.system("./makeCombinePlots.py --mu -f %s  -b | grep MU > %s "%(line,options.inputvalues))
    with open(options.inputvalues) as j:
     jlines = j.readlines()
     for jline in jlines:
       central=float(jline.split("= ")[-1].split(" +")[0])
       up=float(jline.split(" +")[-1].split(" -")[0])
       down=float(jline.split(" -")[-1].split("\n")[0])
       name =""
       if "AllSyst" in line : name = "all"
       if "NoSyst" in line : name = "statonly"
       if "NoTheo" in line : name = "notheory"
       values[name]=[central,abs(up+down)/2,up,down]
       print "LC DEBUG ", name, central, up, down


up = (values["all"][2]**2-values["notheory"][2]**2)**(0.5)
down = (values["all"][3]**2-values["notheory"][3]**2)**(0.5)
values["theoryonly"]=[central,abs(up+down)/2,up,down]
up = (values["all"][2]**2-values["theoryonly"][2]**2-values["statonly"][2]**2)**(0.5)
down = (values["all"][3]**2-values["theoryonly"][3]**2-values["statonly"][3]**2)**(0.5)
values["systonly"]=[central,abs(up+down)/2,up,down]

print "%%%%%%%%%%%%%%%%%%%%%%%%"
print values
print "%%%%%%%%%%%%%%%%%%%%%%%%"

#print " MU = %.2f +/- %.2f = %.2f (stat.) ^{+%.2f}_{-%.2f} (syst.) ^{+%.2f}_{-%.2f} (theo.) "%(values["all"][0], values["all"][1], values["statonly"][1],values["systonly"][2],values["systonly"][3],values["theoryonly"][2],values["theoryonly"][3])
print " MU = $%.2f \pm %.2f = %.2f \pm  %.2f \\text{~(stat.)~} ^{+%.2f}_{-%.2f} \\text{~(syst.)~} ^{+%.2f}_{-%.2f} \\text{~(theo.)}$"%(values["all"][0], values["all"][1],values["all"][0], values["statonly"][1],values["systonly"][2],values["systonly"][3],values["theoryonly"][2],values["theoryonly"][3])
exit(1)
