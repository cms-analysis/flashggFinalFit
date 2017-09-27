#!/usr/bin/env python

import os
import numpy
import sys
import fnmatch
from copy import deepcopy as copy
import re

from optparse import OptionParser
from optparse import OptionGroup


from Queue import Queue

from threading import Thread, Semaphore
from multiprocessing import cpu_count

class Wrap:
    def __init__(self, func, args, queue):
        self.queue = queue
        self.func = func
        self.args = args
        
    def __call__(self):
        ret = self.func( *self.args )
        self.queue.put( ret  )

    
class Parallel:
    def __init__(self,ncpu):
        self.running = Queue(ncpu)
        self.returned = Queue()
        self.njobs = 0
  
    def run(self,cmd,args):
        wrap = Wrap( self, (cmd,args), self.returned )
        self.njobs += 1
        thread = Thread(None,wrap)
        thread.start()
        
    def __call__(self,cmd,args):
        if type(cmd) == str:
            print cmd
            for a in args:
                cmd += " %s " % a
            args = (cmd,)
            cmd = commands.getstatusoutput
        self.running.put((cmd,args))
        ret = cmd( *args ) 
        self.running.get()
        self.running.task_done()
        return ret

def getFilesFromDatacard(datacard):
    card = open(datacard,"r")
    files = set()
    for l in card.read().split("\n"):
        if l.startswith("shape"):
            toks = [t for t in l.split(" ") if t != "" ]
            files.add(toks[3])
    files = list(files)
    ret = files[0]
    for f in files[1:]:
        ret += ",%s" % f
    return ret

parser = OptionParser()
parser.add_option("-i","--infile",help="Signal Workspace")
parser.add_option("-d","--datfile",help="dat file")
parser.add_option("-s","--systdatfile",help="systematics dat file")
parser.add_option("--mhLow",default="120",help="mh Low")
parser.add_option("--mhHigh",default="130",help="mh High")
parser.add_option("-q","--queue",help="Which batch queue")
parser.add_option("--runLocal",default=False,action="store_true",help="Run locally")
parser.add_option("--batch",default="LSF",help="Which batch system to use (LSF,IC)")
parser.add_option("--changeIntLumi",default="1.")
parser.add_option("-o","--outfilename",default=None)
parser.add_option("-p","--outDir",default="./")
parser.add_option("--procs",default=None)
parser.add_option("--useDCB_1G",default="0")
parser.add_option("--useSSF",default="0")
parser.add_option("--massList",default="120,125,130")
parser.add_option("-f","--flashggCats",default=None)
parser.add_option("--bs",default=5.14)
parser.add_option("--expected",type="int",default=None)
(opts,args) = parser.parse_args()

defaults = copy(opts)
print "INFO - queue ", opts.queue
def system(exec_line):
  #print "[INFO] defining exec_line"
  #if opts.verbose: print '\t', exec_line
  os.system(exec_line)

def writePreamble(sub_file):
  #print "[INFO] writing preamble"
  sub_file.write('#!/bin/bash\n')
  sub_file.write('sleep $[ ( $RANDOM % 10 )  + 1 ]s\n')
  sub_file.write('touch %s.run\n'%os.path.abspath(sub_file.name))
  sub_file.write('cd %s\n'%os.getcwd())
  sub_file.write('eval `scramv1 runtime -sh`\n')
  sub_file.write('number=$RANDOM\n')
  sub_file.write('mkdir -p scratch_$number\n')
  sub_file.write('cd scratch_$number\n')

def writePostamble(sub_file, exec_line):

  #print "[INFO] writing to postamble"
  sub_file.write('\t echo "PREPARING TO RUN "\n')
  sub_file.write('if ( %s ) then\n'%exec_line)
  #sub_file.write('\t mv higgsCombine*.root %s\n'%os.path.abspath(opts.outDir))
  sub_file.write('\t echo "DONE" \n')
  sub_file.write('\t touch %s.done\n'%os.path.abspath(sub_file.name))
  sub_file.write('else\n')
  sub_file.write('\t echo "FAIL" \n')
  sub_file.write('\t touch %s.fail\n'%os.path.abspath(sub_file.name))
  sub_file.write('fi\n')
  sub_file.write('cd -\n')
  sub_file.write('\t echo "RM RUN "\n')
  sub_file.write('rm -f %s.run\n'%os.path.abspath(sub_file.name))
  sub_file.write('rm -rf scratch_$number\n')
  sub_file.close()
  system('chmod +x %s'%os.path.abspath(sub_file.name))
  if opts.queue:
    system('rm -f %s.done'%os.path.abspath(sub_file.name))
    system('rm -f %s.fail'%os.path.abspath(sub_file.name))
    system('rm -f %s.log'%os.path.abspath(sub_file.name))
    system('rm -f %s.err'%os.path.abspath(sub_file.name))
    if (opts.batch == "LSF") : system('bsub -q %s -o %s.log %s'%(opts.queue,os.path.abspath(sub_file.name),os.path.abspath(sub_file.name)))
    if (opts.batch == "IC") : 
      system('qsub -q %s -l h_rt=0:20:0 -o %s.log -e %s.err %s'%(opts.queue,os.path.abspath(sub_file.name),os.path.abspath(sub_file.name),os.path.abspath(sub_file.name)))
      #print "system(",'qsub -q %s -o %s.log -e %s.err %s '%(opts.queue,os.path.abspath(sub_file.name),os.path.abspath(sub_file.name),os.path.abspath(sub_file.name)),")"
  if opts.runLocal:
     system('bash %s'%os.path.abspath(sub_file.name))


#######################################

  
system('mkdir -p %s/SignalFitJobs/outputs'%opts.outDir)
print ('mkdir -p %s/SignalFitJobs/outputs'%opts.outDir)
counter=0
for proc in  opts.procs.split(","):
  for cat in opts.flashggCats.split(","):
    print "job ", counter , " - ", proc, " - ", cat
    file = open('%s/SignalFitJobs/sub%d.sh'%(opts.outDir,counter),'w')
    writePreamble(file)
    counter =  counter+1
    bsRW=0
    if (float(opts.bs)==0):
      bsRW=0
    else:
      bsRW=1
    exec_line = "%s/bin/SignalFit --verbose 0 -i %s -d %s/%s  --mhLow=%s --mhHigh=%s -s %s/%s --procs %s -o  %s/%s -p %s/%s -f %s --changeIntLumi %s --binnedFit 1 --nBins 320 --split %s,%s --beamSpotReweigh %d --dataBeamSpotWidth %f --massList %s --useDCBplusGaus %s --useSSF %s -C -1" %(os.getcwd(), opts.infile,os.getcwd(),opts.datfile,opts.mhLow, opts.mhHigh, os.getcwd(),opts.systdatfile, opts.procs,os.getcwd(),opts.outfilename.replace(".root","_%s_%s.root"%(proc,cat)), os.getcwd(),opts.outDir, opts.flashggCats ,opts.changeIntLumi, proc,cat,bsRW,float(opts.bs), opts.massList, opts.useDCB_1G, opts.useSSF)
    #print exec_line
    writePostamble(file,exec_line)



