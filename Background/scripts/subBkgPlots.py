#!/usr/bin/env python

from optparse import OptionParser
parser = OptionParser()
parser.add_option("-b","--bkgfilename",help="Data and background workspace file")
parser.add_option("-s","--sigfilename",help="Signal file (can be binned or parametric) or left blank")
parser.add_option("-d","--outDir",default="BkgPlots",help="Out directory for plots default: %default")
parser.add_option("-c","--cats",type="int",help="Number of categories to run")
parser.add_option("-f","--flashggCats",help="flashggCats : UntaggedTag_0,UntaggedTag_1,UntaggedTag_2,UntaggedTag_3,UntaggedTag_4,VBFTag_0,VBFTag_1,VBFTag_2,TTHHadronicTag,TTHLeptonicTag,VHHadronicTag,VHTightTag,VHLooseTag,VHEtTag")
parser.add_option("-l","--catLabels",default="mk_default",help="Category labels (comma separated) default will use Category %cat")
parser.add_option("-S","--sqrts",type='int',default=8,help="Sqrt(S) COM energy for finding strings etc")
parser.add_option("--intLumi",type='float',default=0.,help="integrated lumi")
parser.add_option("--year",default='2016',help="Dataset year")
parser.add_option("-H","--high",type='int',default=100,help="Sqrt(S) COM energy for finding strings etc")
parser.add_option("-L","--low",type='int',default=180,help="Sqrt(S) COM energy for finding strings etc")
parser.add_option("--isMultiPdf",default=False,action="store_true",help="Use for multipdf workspaces")
parser.add_option("--doBands",default=False,action="store_true",help="Use to draw bands")
parser.add_option("--useBinnedData",default=False,action="store_true",help="Use binned data")
parser.add_option("--makeCrossCheckProfPlots",default=False,action="store_true",help="Make some cross check plots - this is very slow!!")
parser.add_option("--massStep",type="float",default=0.5,help="Mass step for calculating bands. Use a large number like 5 for quick running")
parser.add_option("--nllTolerance",type="float",default=0.05,help="Tolerance for nll calc in %")
parser.add_option("--higgsResolution",type='float',default=1.,help="Resolution of Higgs to calculate bakg in 1sigma range around signal")
parser.add_option("--unblind",default=False,action="store_true",help="Blind the mass spectrum in the range [115,135]")
parser.add_option("--runLocal",default=False,action="store_true",help="Run locally")
parser.add_option("--dryRun",default=False,action="store_true",help="Dont submit jobs")
parser.add_option("-q","--queue",default="espresso",help="Which batch queue")
parser.add_option("--batch",default="HTCONDOR",help="Which batch system to use (HTCONDOR,IC)")
parser.add_option("-v","--verbose",default=False,action="store_true",help="Print more output")
(options,args) = parser.parse_args()

import os
import subprocess

os.system('mkdir -p %s'%options.outDir)

vcats = options.flashggCats.split(',') 
ncats = len(vcats)
print 'Considering ',ncats,' catgeories :', vcats

if options.catLabels=='mk_default':
  options.catLabels=[]
  #for cat in range(options.cats):
  for cat in range(ncats):
    options.catLabels.append('Category %d'%cat)
else:
  options.catLabels = options.catLabels.split(',')
print ""
print options.catLabels
print ""

#for cat in range(options.cats):
for cat in range(ncats):
  
  f = open('%s/sub%d.sh'%(options.outDir,cat),'w')
  f.write('#!/bin/bash\n')
  f.write('cd %s\n'%os.getcwd())
  f.write('eval `scramv1 runtime -sh`\n')
  print "nCats = ",ncats
  print "cat = ",cat
  print "nCatLabels = ",len(options.catLabels)
  print ""
  execLine = '$CMSSW_BASE/src/flashggFinalFit/Background/bin/makeBkgPlots -f %s -b %s -o %s/BkgPlots_cat%d.root -d %s -c %d -l \"%s\"'%(options.flashggCats,options.bkgfilename,options.outDir,cat,options.outDir,cat,options.catLabels[cat])
#  execLine = '$PWD -b %s -s %s -o %s/BkgPlots_cat%d.root -d %s -c %d -l \"%s\"'%(options.bkgfilename,options.sigfilename,options.outDir,cat,options.outDir,cat,options.catLabels[cat])
  execLine += " --sqrts %d "%options.sqrts
  execLine += " --intLumi %f "%options.intLumi
  execLine += " --year %s "%options.year
  print "LC DEBUG echo intlumi ",options.intLumi
  if options.doBands:
    execLine += ' --doBands --massStep %5.3f --nllTolerance %5.3f -L %d -H %d'%(options.massStep,options.nllTolerance,options.low,options.high)
  if options.higgsResolution:
    execLine += ' --higgsResolution %s'%(options.higgsResolution)
  if options.sigfilename:
    execLine += ' -s %s'%(options.sigfilename.replace('.root','_%s.root')%options.catLabels[cat])
  if options.unblind:
    execLine += ' --unblind'
  if options.isMultiPdf:
    execLine += ' --isMultiPdf'
  if options.useBinnedData:
    execLine += ' --useBinnedData'
  if options.makeCrossCheckProfPlots:
    execLine += ' --makeCrossCheckProfPlots'
  if options.verbose:
    execLine += ' --verbose'
  f.write('%s\n'%execLine);
  f.close()
  print execLine
  
  os.system('chmod +x %s'%f.name)
  if options.runLocal: os.system('./%s'%f.name)
  else:
    if (options.batch == "IC") : os.system('qsub -q %s -o %s.log %s'%(options.queue,os.path.abspath(f.name),os.path.abspath(f.name)))
    elif( options.batch == "HTCONDOR" ):
      sub_file_name = re.sub("\.sh","",os.path.abspath(f.name))
      HTCondorSubfile = open("%s.sub"%sub_file_name,'w')
      HTCondorSubfile.write('+JobFlavour = "%s"\n'%(options.queue))
      HTCondorSubfile.write('\n')
      HTCondorSubfile.write('executable  = %s.sh\n'%sub_file_name)
      HTCondorSubfile.write('output  = %s.out\n'%sub_file_name)
      HTCondorSubfile.write('error  = %s.err\n'%sub_file_name)
      HTCondorSubfile.write('log  = %s.log\n'%sub_file_name)
      HTCondorSubfile.write('\n')
      HTCondorSubfile.write('max_retries = 1\n')
      HTCondorSubfile.write('queue 1\n')
      subprocess.Popen("condor_submit "+HTCondorSubfile.name,
                             shell=True, # bufsize=bufsize,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             close_fds=True)
    else: print "Batch %s is not supported. Exiting..."%options.batch
