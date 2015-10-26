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
parser.add_option("-i","--input",default="workspaceContents.txt")
parser.add_option("-r","--fromroot",default="")
parser.add_option("-f","--flashggCats",default="UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,UntaggedTag_4,VBFTag_0,VBFTag_1,VBFTag_2,TTHHadronicTag,TTHLeptonicTag,VHHadronicTag,VHTightTag,VHLooseTag,VHEtTag")
(options,args) = parser.parse_args()

if not (options.fromroot ==""):
	print "execute"
	os.system("./bin/workspaceTool -i %s --print 1 | grep RooData | grep it > %s"%(options.fromroot,options.input))
	os.system("./bin/workspaceTool -i %s --print 1 | grep intLumi >> %s"%(options.fromroot,options.input))

procs=[]
tags=[]
_tags=options.flashggCats.split(",")
weights=[]
entries=[]



with open(options.input) as i:
	lines  = i.readlines()
	for line in lines:
		if "intLumi" in line: lumi=float(line[line.find("value")+6:])
		#if not "entr" in line : continue 
		#print line
		for tag in _tags:
			#procs.append(line[line.find("::")+2:line.find(str(sqrts)+"TeV")-1])
			#print "tag ", tag
			if not tag in line : continue
			if "sigma" in line : continue  #don't want systematic variations
			procs.append(line[line.find("::")+2:line.find(str(tag))-1])
			#tags.append(line[line.find(str(sqrts)+"TeV")+4+len(str(sqrts)):line.find("[")])
			tags.append(tag)
			#print tags[-1], " ", procs[-1]
			#weights.append(float(line[line.find("entries")+9:line.find("weighted")-1]))
			#weightsStr =line[line.find("(")+1:line.find("weight")-1]
			weightsStr =line[line.find("(")+1:line.find(" wei")]
			entriesStr=line[line.find("=")+1:line.find("entri")-1]
			#print weightsStr, ", ", entriesStr
			if (not weightsStr == "" and len(weightsStr)<15): weights.append(float(weightsStr))
			else: weights.append(0.)
			if (not entriesStr == "" and len(entriesStr)<15): entries.append(float(entriesStr))
			else: entries.append(0.)
			
print "INTLUMI ", lumi, "/pb"
print "PROC 		YIELD		WEIGHT"
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
		print proc, "	", perProcYield, "		", perProcWeight
	else :
		print proc, "		", perProcYield, "		", perProcWeight

print	

print "TAG 		YIELD (M125)		WEIGHT (M125)"
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
		print tag, "	", perTagYield, "		",perTagWeight
	else :
		print tag, "		", perTagYield, "		",perTagWeight
	

for proc in sorted(set(procs)):
	print 
	print	"TAG ONLY - " , proc 
	print "TAG 		YIELD 		WEIGHT"
	# yields by process
	for tag in sorted(set(tags)):
		perTagYield=0.
		perTagWeight=0.
		#print "----> ", proc, "<-----"
		for i in range(0,len(tags)):
			#print procs[i] , " -- ", proc
			if (tags[i]==tag and procs[i]==proc ):
				perTagYield = perTagYield + entries[i]
				perTagWeight = perTagWeight + weights[i]
		if "_" in proc :
			print tag, "	", perTagYield, "		",perTagWeight
		else :
			print tag, "		", perTagYield, "		",perTagWeight

