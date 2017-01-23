#!/usr/bin/env python

import os
import numpy
import sys
import time

import fnmatch
from copy import deepcopy as copy
import re
import ROOT as r
from array import array


r.gROOT.ProcessLine(".L $CMSSW_BASE/lib/$SCRAM_ARCH/libHiggsAnalysisCombinedLimit.so")
r.gROOT.ProcessLine(".L $CMSSW_BASE/lib/$SCRAM_ARCH/libdiphotonsUtils.so")
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
parser.add_option("--nEvents",default="801:1479",help="how many events in EBEE:EBEB")
parser.add_option("--nTrueArray",default="",help="")
parser.add_option("--exoEA",default="",help="")
parser.add_option("--mhLow",default="120",help="mh Low")
parser.add_option("--mhHigh",default="130",help="mh High")
parser.add_option("--mh",default="750",help="mh")
parser.add_option("--method",default="bias",help="or use nEvents")
parser.add_option("-k",default=None,help="with of signal")
parser.add_option("-q","--queue",help="Which batch queue")
parser.add_option("--runLocal",default=False,action="store_true",help="Run locally")
parser.add_option("--drawCorrected",default=False,action="store_true",help="Apply stupid correction")
parser.add_option("--skipMerged",default=False,action="store_true",help="When using the hadd option, do not re-merge already merged files")
parser.add_option("--useMCBkgShape",default=False,action="store_true",help="Use MC rooHistPdf as bkg shape instead")
parser.add_option("--parametric",default=True,action="store_true",help="submit parameteric jobs")
parser.add_option("--batch",default="LSF",help="Which batch system to use (LSF,IC)")
parser.add_option("--lumi",default="10.0")
parser.add_option("-o","--outfilename",default=None)
parser.add_option("-p","--outDir",default="./")
parser.add_option("--hadd",default=None)
parser.add_option("--grep",default=None)
parser.add_option("--deleteFailures",default=None)
parser.add_option("--resubmit",default=None)
parser.add_option("--makePlots",default=None)
parser.add_option("--pdfNameDict",default=None)
parser.add_option("--procs",default=None)
parser.add_option("-f","--flashggCats",default=None)
parser.add_option("--expected",type="int",default=None)
parser.add_option("--splitDatacard",default=None,help="Split thsi datacard by process")
parser.add_option("--justSplit",default=False,action="store_true",help="Split thsi datacard by process")
(opts,args) = parser.parse_args()

defaults = copy(opts)

print "INFO - queue ", opts.queue
def system(exec_line):
  #print "[INFO] defining exec_line"
  #if opts.verbose: print '\t', exec_line
  os.system(exec_line)

def getNTrue( tagVals):
  EBEB={640: 60.405126880114324, 1600: 1.4751467248586732, 3800: 0.007345152962756264, 520: 127.28420003780167, 3600: 0.012799576709727471, 2200: 0.28361241927857966, 1300: 3.826475516861353, 920: 15.119460261895224, 800: 26.286248223492223, 1200: 5.261878120378314, 1700: 1.1187437599780707, 680: 48.9875026350166, 3500: 0.016660729929997488, 560: 97.75728601183536, 1800: 0.8163921742255122, 950: 13.368499906128484, 3000: 0.04596295244134684, 960: 12.851162943343581, 4000: 0.005018618675885605, 2500: 0.13796915483552347, 840: 21.875762291499903, 1100: 7.523503108305666, 720: 39.98326089058199, 760: 32.35691931311009, 850: 20.90110422798945, 600: 75.62520402805687, 1500: 2.0312851853525054, 2400: 0.1759416516467292, 2000: 0.5126358473436861, 3400: 0.019851404748589114, 1000: 10.898541574148801, 3200: 0.02953177373484743, 1900: 0.6261959822504424, 750: 33.96120172324244, 880: 18.374624154483836, 2600: 0.10858421975112088, 1400: 2.786724695175136, 4500: 0.0019166520568878276, 2800: 0.0718994069816369}
  EBEE={640: 102.29758106878622, 1600: 2.1670373550767157, 3800: 0.005748154298231124, 520: 194.2836816620703, 3600: 0.010516661364708923, 2200: 0.3443674415744314, 1300: 6.066253444243402, 920: 27.46425842189874, 800: 47.37332587944921, 560: 155.9070169654501, 1700: 1.556780514406653, 680: 82.21464188087775, 3500: 0.013676643621872726, 1200: 8.693311986514344, 1800: 1.1653503833197683, 950: 23.770871589953565, 3000: 0.04391463084856518, 960: 22.69232284354254, 4000: 0.0038056433933624837, 2500: 0.1527507129741505, 840: 38.973239589953565, 1100: 12.717035469809064, 720: 67.98125078661722, 760: 56.61440124524604, 850: 36.91962055296787, 600: 126.07813518872332, 1500: 3.0449230221875254, 2400: 0.20082750401243005, 2000: 0.6367117203511232, 3400: 0.017073541319887697, 1000: 18.91949608021327, 3200: 0.0259420421864104, 1900: 0.8898658680897452, 750: 59.461632541987356, 880: 32.286346848027776, 2600: 0.11734941847708553, 1400: 4.328596632892303, 4500: 0.0012623033208031807, 2800: 0.07348755560888187}
  res={}
  res["EBEB"]=EBEB
  res["EBEE"]=EBEE
  return res
  f = r.TFile("bias_study_input.root")
  tree = f.Get("tree_mctruth_pp_cic2_%s"%tag)
  trueYields={}
  trueYields["EBEB"]=4573.2
  trueYields["EBEE"]=2297.7
  counter={}
  counterAll=0.
  mXList=[520]
  res ={}
  nevents= -1
  for event in tree:
    nevents =nevents+1
    if (nevents%10000==0) :print "ev ", nevents, "/", tree.GetEntries(),"  mass " , event.mass, " wight ", event.weight
    
    counterAll= counterAll+event.weight
    for mX in mXList:
      Integralrange =[0.95*mX,1.05*mX]
      if (event.mass > Integralrange[0] and event.mass < Integralrange[1]):
        if not mX in counter: counter[mX]=0. 
        counter[mX]= counter[mX]+event.weight
  factor= trueYields[tag]/counterAll
  for mX in mXList:
    print " total number of events around " , mX, "  is " , counter[mX]," TOTAL for that tree is " , counterAll
    print " total normalized of events in range around " , mX, "  is " , counter[mX]*factor," TOTAL for that tree is " , counterAll*factor
    counter[mX]=counter[mX]*factor 
  print counter
  exit(1)
  return  counter

def getExoEA():
  names=["EBEB","EBEE"]
  #names=["EBEB"]
  eaArray={}
  for name in names:
    f = r.TFile("ea%s.root"%name)
    print " opening file for", name 
    c = f.Get("c1")
    for item in c.GetListOfPrimitives():
      if (item.InheritsFrom("RooCurve")):
      #print "minimum ", item.GetMinimum()
        print "========================="
        item.GetName()
        print
        item.Print()
        array={}
        for i in range(500,4510,10):
          print "bin ", i , " contents ", item.Eval(float(i))
          array[float(i)]=item.Eval(float(i))
        eaArray[name]=array
        break
    f.Close()
  return eaArray


def getExoBSResults():
  names=["EBEB","EBEE"]
  skipFirst=False
  tGraphsArray={}
  for name in names:
    if (opts.method=="bias"): f = r.TFile("profile_pull_%s_dijet.root"%name)
    if (opts.method=="nEvents"): f = r.TFile("profile_nEvents.root")
    if name=="EBEE": skipFirst=True
    print " opening file for", name 
    if (opts.method=="nEvents") :c = f.Get("profile_bias")
    if (opts.method=="bias") :c = f.Get("profile_pull_%s_dijet"%name)
    for item in c.GetListOfPrimitives():
      if (item.InheritsFrom("TGraph")):
        if skipFirst: 
          skipFirst=False
          continue
        print "========== ", name," ==============="
        item.GetName()
        print
        item.Print()
        tGraphsArray[name]=item.Clone(name)
        break
    f.Close()
  return tGraphsArray

def getBScorrectionFactors(dijetNew, dijetOld ):
  correctionsArray={}
  print "DEBUG A"
  dijetOld.Print()
  print "DEBUG B"
  dijetNew.Print()
  for i in range(dijetNew.GetN()):
    minDist=9999
    XvalNew=dijetNew.GetX()[i]
    YvalNew=dijetNew.GetY()[i]
    correctionsArray[XvalNew]=9999
    for j in range(dijetOld.GetN()):
      XvalOld=dijetOld.GetX()[j]
      YvalOld=dijetOld.GetY()[j]
      print "new entry ", i, " at ", XvalNew ," : old entry ", j," at ", XvalOld ," distance ", abs(XvalNew-XvalOld), " min dist ", minDist  
      if abs(XvalNew-XvalOld) < minDist:
        print " --> found new closest point ! YValNew ", YvalNew, " YvalOld ", YvalOld
        minDist= abs(XvalNew-XvalOld)
        if float(YvalNew)==0 : 
          print "error, Yval New is 0"
          exit(1) 
          #correctionsArray[XvalNew]=0
        else :correctionsArray[XvalNew] = float(YvalOld)/float(YvalNew)
  print "DEBUG LC this is my correction array:"
  print correctionsArray
  return correctionsArray

def applyCorrections(tgraph, correctionArray):
  tgraphCorr = r.TGraphErrors()
  for i in range(tgraph.GetN()):
    xval= tgraph.GetX()[i]
    yval= tgraph.GetY()[i]
    tgraphCorr.SetPoint(i,xval,yval*correctionArray[xval])
    #tgraphCorr.SetPointError(i,xval,yval*correctionArray[xval])
  return tgraphCorr

def writePreamble(sub_file,mu,mh,cat,truthPdf,fitPdf,index):
  #print "[INFO] writing preamble"
  sub_file.write('#!/bin/bash\n')
  sub_file.write('touch %s.run\n'%os.path.abspath(sub_file.name))
  sub_file.write('cd %s\n'%os.getcwd())
  sub_file.write('eval `scramv1 runtime -sh`\n')
  #if (opts.batch == "IC" ) : sub_file.write('cd $TMPDIR\n')
  #sub_file.write('number=$RANDOM\n')
  #sub_file.write('mkdir -p scratch_$number\n')
  #sub_file.write('cd scratch_$number\n')
  sub_file.write('MU=%.2f \n'%mu)
  sub_file.write('MHhat=%d \n'%opts.mh)
  sub_file.write('NTOYS=50 \n')
  
  if (mh>1500):
    sub_file.write('MINR=-1 \n')
  else:
    sub_file.write('MINR=-60 \n')
  sub_file.write('PDF=%d \n'%truthPdf)
  sub_file.write('FITPDF=%d \n'%fitPdf)
  sub_file.write('EXTRAOPT="-L libdiphotonsUtils"\n')
  if (opts.batch == "IC"):
    sub_file.write('index=$SGE_TASK_ID\n')
  sub_file.write('TAG=%s \n'%cat)
  sub_file.write('JOBPATH=%s\n'%os.path.abspath(sub_file.name).split("sub")[0])
  #sub_file.write('PULLJOBPATH=%s\n'%os.path.abspath(sub_file.name).split("/sub")[0].replace("DeltaL","Pulls"))
  sub_file.write('cd $TMPDIR\n')
  sub_file.write('cp %s/biasStudyWS_k%s_m%d_%s.root biasStudyWS_%s.root \n'%(os.getcwd(),opts.k,int(opts.mh),cat,cat))
  sub_file.write('cp %s/biasStudyWS_k%s_m%d_%s_gen.root biasStudyWS_%s_gen.root \n'%(os.getcwd(),opts.k,int(opts.mh),cat,cat))
  name=None
  if (index=="Pulls"):
    name="biasStudyJobTemplatePulls.sh"
  else:
    name="biasStudyJobTemplate.sh"
  f= open(name)
  sub_file.write(f.read())
  f.close()

def writePostamble(sub_file):

  sub_file.write('rm -f %s.run\n'%os.path.abspath(sub_file.name))
  #sub_file.write('rm -rf scratch_$number\n')
  sub_file.close()
  system('chmod +x %s'%os.path.abspath(sub_file.name))
  if opts.queue:
    print "DEBUG opts.queue ", opts.queue
    system('rm -f %s.done'%os.path.abspath(sub_file.name))
    system('rm -f %s.*fail'%os.path.abspath(sub_file.name))
    system('rm -f %s.log'%os.path.abspath(sub_file.name))
    system('rm -f %s.err'%os.path.abspath(sub_file.name))
    if (opts.batch == "LSF") : system('bsub -q %s -o %s.log %s'%(opts.queue,os.path.abspath(sub_file.name),os.path.abspath(sub_file.name)))
    if (opts.batch == "IC") : 
        print "DEBUG opts.batch ", opts.batch
        if (opts.parametric):
          system('qsub -q %s -o %s.log -e %s.err -t 1-10:1  -l h_rt=2:55:0 %s'%(opts.queue,os.path.abspath(sub_file.name),os.path.abspath(sub_file.name),os.path.abspath(sub_file.name)))
          print  "system(",'qsub -q %s -o %s.log -e %s.err -t 1-3:1  -l h_rt=2:55:0 %s'%(opts.queue,os.path.abspath(sub_file.name),os.path.abspath(sub_file.name),os.path.abspath(sub_file.name))
        else:
           system('qsub -q %s -o %s.log -e %s.err -l h_rt=2:55:0  %s'%(opts.queue,os.path.abspath(sub_file.name),os.path.abspath(sub_file.name),os.path.abspath(sub_file.name)))
  if opts.runLocal:
     system('bash %s'%os.path.abspath(sub_file.name))


#######################################
def update_progress(progress):
  barLength = 20 # Modify this to change the length of the progress bar
  status = ""
  if isinstance(progress, int):
    progress = float(progress)
  if not isinstance(progress, float):
      progress = 0
      status = "error: progress var must be float\r\n"
  if progress < 0:
        progress = 0
        status = "Halt...\r\n"
  if progress >= 1:
        progress = 1
        status = "Done...\r\n"
  block = int(round(barLength*progress))
  text = "\rProgress: [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), round(progress*100,2), status)
  sys.stdout.write(text)
  sys.stdout.flush()

def trawlHadd():
  print "[INFO] trawling hadd"
  list_of_dirs=set()
  #for root, dirs, files in os.walk(opts.hadd):
  #  for x in files:
  for root in os.listdir(opts.hadd): 
    listx = os.listdir('%s/%s'%(opts.hadd,root))
    skip =False
    if (opts.skipMerged): 
      for x in listx:
         if "merged.root" in x : 
          skip =True
          break
    if (skip) : continue
    for x in listx:
      if 'higgsCombine' in x and '.root' in x:
        if (opts.grep==None) or (opts.grep in "%s/%s"%(root,x)):
          list_of_dirs.add('%s/%s'%(opts.hadd,root))
      if 'mlfit' in x and '.root' in x: 
        if (opts.grep==None) or (opts.grep in "%s/%s"%(root,x)):
          print "add dir ", '%s/%s'%(opts.hadd,root)
          list_of_dirs.add('%s/%s'%(opts.hadd,root))
  #for i in range (0,len(list_of_dirs)):
  #  interval = (imax+10)/100
  #  #print "i, max, interval" , i, imax, interval 
  #  if (i%interval==0):# update the bar
  #    time.sleep(0.1)
  #    #sys.stdout.write("-")
  #    #sys.stdout.flush()
  #update_progress(1)
  #sys.stdout.write("\n") 
  
  counter =0.
  imax= len(list_of_dirs)
  for dir in list_of_dirs:
    #print "DEBUG considerign dir for hadding ", dir
    list_of_files_DeltaL=''
    list_of_files_Pulls=''
    for filename in os.listdir(dir):
      #print "DEBUG considerign dir/file for hadding ", dir, " / ", filename
      #for file in files:
      #  list_of_files_DeltaL += ' '+os.path.join(dir,'%s'%file)
      #for file in files:
      if not 'mlfit' in filename: continue
      if not '.root' in filename: continue
      list_of_files_Pulls += ' '+os.path.join(dir,'%s'%filename)
    #print dir, ' -- ', len(list_of_files_DeltaL.split())
    #print 'hadd -f %s/%s.merged.root%s > /dev/null'%(dir,os.path.basename(dir),list_of_files_DeltaL)
    #exec_line = 'hadd -f %s/%s.merged.root%s > /dev/null'%(dir,os.path.basename(dir),list_of_files_DeltaL)
    #print dir, ' -- ', len(list_of_files_Pulls.split())
    #print  'hadd -f %s/%s.merged.root%s > /dev/null'%(dir,os.path.basename(dir),list_of_files_Pulls)
    exec_line = 'hadd -f %s/%s.merged.root%s > /dev/null'%(dir,os.path.basename(dir),list_of_files_Pulls)
    update_progress(float(counter)/float(imax))
    counter =counter+1
    #if opts.verbose: print exec_line
    system(exec_line)
  update_progress(1)

def trawlResubmit():
  print "[INFO] trawling hadd"
  list_of_files=[]
  #for root, dirs, files in os.walk(opts.resubmit):
    #for x in files:
  for root in os.listdir(opts.resubmit):
    for x in os.listdir('%s/%s'%(opts.resubmit,root)):
      if '.sh.fail' in x: 
        print "adding", opts.resubmit+"/"+root+"/"+x.split(".fail")[0] 
        list_of_files.append(opts.resubmit+"/"+root+"/"+x.split(".fail")[0])
      if '.sh.run' in x: 
        print "adding", opts.resubmit+"/"+root+"/"+x.split(".run")[0] 
        list_of_files.append(opts.resubmit+"/"+root+"/"+x.split(".run")[0])
  for f in list_of_files:
    #print f
    f = f.replace(".run","").replace(".fail","")
    index = f.split("sub")[1].split(".")[0]
    if (index==""): continue
    #print "index is ", int(index)
    f0 = f.replace("sub%d"%int(index),"sub")
    #print "so, opening ",f0
    job0 = open(f0,"r")
    job = open(f,"w") 
    for line in job0.readlines():
      if "$SGE_TASK_ID" in line:
        job.write(line.replace("$SGE_TASK_ID","%d"%int(index)))
      elif "NTOYS=200" in line:
        job.write(line.replace("NTOYS=200","NTOYS=50"))
      else :
        job.write(line)
    print "resubmitting", job
    opts.parametric=False
    writePostamble(job)

def deleteFailures():
  print "[INFO] trawling hadd"
  list_of_files=[]
  #for root, dirs, files in os.walk(opts.deleteFailures):
    #for x in files:
  for root in os.listdir(opts.deleteFailures):
    for x in os.listdir('%s/%s'%(opts.deleteFailures,root)):
      if '.sh.fail' in x: 
        print "adding", root+"/"+x.split(".fail")[0] 
        list_of_files.append(root+"/"+x.split(".fail")[0])
  for f in list_of_files:
    os.system("rm %s.fail*"%f)
    dir=f.split("/sub")[0]
    jobid=f.split("sub")[1].split(".sh")[0]
    os.system("rm %s/*job_%s.*"%(dir,jobid))
    print "delete *",f.split("sub")[1].split(".sh")[0],"* from ",f.split("/sub")[0]

def getAveragePullNew(f,mX,muTrue,pdfTrue,pdfFit,tag):
  
  tf = r.TFile.Open(f)
  #f= f.split("/")[-1]
  #ttree = tf.Get("tree_fit_sb")
  #ttree = tf.Get("tree_fit_b")
  ttree = tf.Get("tree_fit_sb")
  r.gStyle.SetOptStat(0)
  #tagName = f.split("_13TeV")[0]
  #mu = float(f.split("mu_")[1].split("_")[0])
  #pdf = int(f.split("pdf_")[1].split(".merged")[0])
  #print pullList
  
  r.gROOT.SetBatch(1)
  #print 'ttree = tf.Get("tree_fit_sb")'
  c = r.TCanvas("c","c",500,500)
  #ttree.Draw("(mu-%f)/muHiErr>>htemp(10,-4,4)"%muTrue)
  #print 'ttree.Draw("(mu-%f)/muHiErr>>htemp"'%muTrue,')'
  #ttree.Draw("(mu-%f)/muErr>>htemp"%muTrue)
  #ttree.Draw("(mu-%f)/muErr>>htemp(500,-10,10)"%muTrue,"fit_status>0 ")
  #nTrue = opts.nTrueArray[tag][mX]/0.94
  nTrue = opts.nTrueArray[tag][mX]
  ttree.Draw("nBkgTrue>>htempnTrue","")
  #htempnTrue = r.gROOT.FindObject("htempnTrue")
  #nTrueFromTree= htempnTrue.GetMean()
 
  #print " LC DEBUG nTRUE" , nTrue , " nTrueFromTree ", nTrueFromTree 
  #ttree.Draw("(nBkg-%f)/nBkgErr>>htemp(501,-5.005,5.005)"%nTrue,"nBkgErr>0")
  #ttree.Draw("(nBkg-%f)/nBkgErr>>htemp(501,-5.005,5.005)"%nTrueFromTree,"nBkgErr>0")
  #ttree.Draw("(nBkg-%f)/nBkgErr>>htemp()"%nTrue,"nBkgErr>0 && fit_status>0")
  #tree.Draw("(mu-%f)/muErr>>htemp"%muTrue,"fit_status>0")
  #print "(((mu-%f)/muErr)*%f)/%f>>htemp"%(muTrue,opts.exoEA[tag][mX],2.35*0.01*0.01*float(mX))
  #ttree.Draw("(((mu-%f)/muErr)*%f)/%f>>htemp"%(muTrue,opts.exoEA[tag][mX],2.35*0.01*0.01*float(mX)),"fit_status>0")
  #ttree.Draw("(((mu-%f)/muErr)*%f)>>htemp"%(muTrue,opts.exoEA[tag][mX]),"fit_status>0")
  #ttree.Draw("-1*(((mu-%f)/muErr))>>htemp"%(muTrue),"fit_status>0")
  if (opts.method=="bias") :ttree.Draw("-1*(((mu-%f)/muErr))>>htemp"%(muTrue),"fit_status>0")
  if (opts.method=="nEvents") :ttree.Draw("(((mu-%f)))>>htemp"%(muTrue),"fit_status>0")
  #print 'ttree.Draw("(((mu-%f)/muErr)*%f)>>htemp,"fit_status>0")"'%(muTrue,opts.exoEA[tag][mX])
  #exit(1)
  #ttree.Draw("(mu)/muErr>>htemp(10,-4,4)")
  htemp = r.gROOT.FindObject("htemp")
  #norm  = 1/float(htemp.GetEntries())
  #print " DEBUG norm ", norm
  #ttree.Draw("(mu-%f)>>htemp2"%muTrue,"(mu>-20) *%d"%norm)
  print "fitting"
  #htemp.Fit("gaus","")
  pullLists={}
  #if (htemp.GetEntries() <100 ) : return pullLists
  if (htemp.GetEntries() <1 ) : return pullLists
  if (htemp.GetSumOfWeights()  <1 ) : return pullLists
  htemp.DrawNormalized()
  r.gStyle.SetOptStat(1111)
  r.gStyle.SetOptFit(111)
  htemp.Fit("gaus","q")
  print htemp
  fit = htemp.GetFunction("gaus")
  print fit
  gausmean = fit.GetParameter(1)
  #xq = [0.5]
  #xq = r.vector(float)(1)
  #yq = r.vector(float)(1)
  xq = array('d',[ -999. ])
  yq = array('d',[ -999. ])
  xq[0] =0.5001
  yq[0] = -999
  pull = htemp.GetQuantiles(1,yq,xq)
  print pull,opts.lumi, opts.exoEA[tag][int(mX)], 2.35, 0.01,mX
  ea=opts.exoEA[tag][int(mX)]
  print "QUANTILES (MEDIAN) yq", yq
  median= yq[0]

  #if (opts.method=="nEvents"): pull =abs(float(median)*float(opts.lumi)*float(ea)/(2.35*0.01*mX))
  if (opts.method=="nEvents"): 
    #pull =abs(float(median)*float(opts.lumi)*float(ea)/(2.35*0.01*mX))
    pull =float(median)
  if (opts.method=="bias"): pull =float(median)
  arr = r.TArrow(median,-1,median,0,0.05,"|>")
  #arr = r.TArrow(pull,-1,pull,0,0.05,"|>")
  arr.Draw()
  tlat = r.TLatex()
  tlat.SetNDC()
  tlat.DrawLatex(0.1,0.001,"median %s"%(median))
  tlat.SetTextAlign(22)
  c.SaveAs("histo_%s.pdf"%f.split("/")[1])
  c.SaveAs("histo_%s.png"%f.split("/")[1])
  #pull = htemp.GetMean()
  print pull
  print " DEBUGXXX] file ", f, " median is ",pull, " gaus mean is ",  gausmean
  if pull==0.0 : 
    print "ERROR pull is identically zero!"
    exit(1)
  if not pdfFit in pullLists.keys(): pullLists[pdfFit]=None
  pullLists[pdfFit]=pull
  tf.Close()
  wf=open("log.txt","a")
  wf.write("%s mean %.2f meadian %.2f \n"%(f,gausmean,pull))
  wf.close()

  #for pdf in pullLists.keys():
  #  print " final average pull for tag ",tag, " pdf ", pdf
  #  pullLists[pdf]= (sum(pullLists[pdf]) / float(len(pullLists[pdf])))
  return pullLists

def getAveragePull(f,muTrue,pdfTrue,pdfFit,tag):
  
  tf = r.TFile.Open(f)
  #f= f.split("/")[-1]
  limit = tf.Get("limit")
  r.gStyle.SetOptStat(0)
  #tagName = f.split("_13TeV")[0]
  #mu = float(f.split("mu_")[1].split("_")[0])
  #pdf = int(f.split("pdf_")[1].split(".merged")[0])
  muTrue=1
  muArray ={}
  pdfArray ={}
  for ev in range(limit.GetEntries()):
   limit.GetEntry(ev)
   #uniqueRef=float((getattr(limit,"t_cpu")))
   #print uniqueRef
   uniqueRef="%d_%f_%f"%((getattr(limit,"iToy")),1000*(getattr(limit,"t_real")),1000*(getattr(limit,"t_cpu")))
   #print uniqueRef
   mu= (getattr(limit,"r"))
   pdf= (getattr(limit,"pdfindex_%s"%tag))
   if uniqueRef not in muArray.keys():
    muArray[uniqueRef]=[] 
    pdfArray[uniqueRef]=[] 
    muArray.get(uniqueRef).append(mu)
    pdfArray.get(uniqueRef).append(pdf)
   else:
    muArray.get(uniqueRef).append(mu)
    pdfArray.get(uniqueRef).append(pdf)
  
  pullLists={}
  print "printing contents"
  counter=0
  for k in muArray.keys() :
    if (len(muArray[k])!=3)  : continue
    #print counter, k
    muList =sorted((muArray[k]))
    pdfList =sorted((pdfArray[k]))
    mu =muList[1]
    print "mu List" ,muList
    pdf =pdfList[1]
    errLo = abs(mu -muList[0])
    errHi = abs(mu -muList[2])
    pull=0
    print "mu = ", mu ," + ", errHi, " - ", errLo
    if (muTrue < mu) :
      if (abs(errHi)< 10e-4) : continue
      pull = (muTrue -mu)/errHi
      #pull = (muTrue -mu)
      print "muTrue -mu ", muTrue -mu , " errHi ", errHi , " pull " ,pull
      if not pdf in pullLists.keys(): pullLists[pdf]=[]
      pullLists[pdf].append(pull)
    else:
      #if (abs(errLo)  < 10e-4): continue
      pull = (muTrue -mu)/errHi
      #pull = (muTrue -mu)
      if not pdf in pullLists.keys(): pullLists[pdf]=[]
      pullLists[pdf].append(pull)
  #print pullList
  for pdf in pullLists.keys():
    print " final average pull for tag ",tag, " pdf ", pdf
    pullLists[pdf]= (sum(pullLists[pdf]) / float(len(pullLists[pdf])))
  return pullLists

def makePlotsDeltaL():
  list_of_files=[]
  r.gROOT.SetBatch(1)
  #for root, dirs, files in os.walk(opts.makePlots):
    #for x in files:
  for root in os.listdir(opts.makePlots):
    for x in os.listdir('%s/%s'%(opts.makePlots,root)):
      if 'merged.root' in x and "Delta" in x: 
        print "adding", root+"/"+x.split(".fail")[0] 
        list_of_files.append(root+"/"+x.split(".fail")[0])
  for f in list_of_files:
    print f
    tf = r.TFile.Open(f)
    f= f.split("/")[-1]
    limit = tf.Get("limit")
    r.gStyle.SetOptStat(0)
    tagName = f.split("_13TeV")[0]
    mu = float(f.split("mu_")[1].split("_")[0])
    pdf = int(f.split("pdf_")[1].split("_")[0])
    limit.Draw("2*deltaNLL>>htemp(50,0,10)","quantileExpected>0 && quantileExpected<1")
    limit.Draw("2*deltaNLL>>htempRF(50,0,10)","quantileExpected>0 && quantileExpected<1 &&  pdfindex_%s==%d"%(tagName,pdf))
    limit.Draw("2*deltaNLL>>htempWF(50,0,10)","quantileExpected>0 && quantileExpected<1 &&  pdfindex_%s!=%d"%(tagName,pdf))
    htemp = r.gROOT.FindObject("htemp")
    htempRF = r.gROOT.FindObject("htempRF")
    htempWF = r.gROOT.FindObject("htempWF")
    htemp.SetLineColor(r.kBlue)
    htemp.SetFillColor(r.kBlue)
    htemp.SetFillStyle(3003)
    htempWF.SetLineColor(r.kRed)
    htempWF.SetFillColor(r.kRed)
    htempWF.SetFillStyle(3002)
    htempRF.SetLineColor(r.kGreen)
    htempRF.SetFillColor(r.kGreen)
    htempRF.SetFillStyle(3001)
    chi2shape= r.TF1("chi2shape","[0]*x^(-1/2)*TMath::Exp(-x/2)", 0, 10)
    chi2shapeRF= r.TF1("chi2shapeRF","[0]*x^(-1/2)*TMath::Exp(-x/2)", 0, 10)
    chi2shapeWF= r.TF1("chi2shapeWF","[0]*x^(-1/2)*TMath::Exp(-x/2)", 0, 10)
    chi2shapeDummy= r.TF1("chi2shapeDummy","[0]*x^(-1/2)*TMath::Exp(-x/2)", 0, 10)
    chi2shape.SetLineColor(r.kBlue-1)
    chi2shapeRF.SetLineColor(r.kGreen-1)
    chi2shapeWF.SetLineColor(r.kRed-1)
    htemp.Fit(chi2shape)
    htempRF.Fit(chi2shapeRF)
    htempWF.Fit(chi2shapeWF)
    tleg = r.TLegend(0.1,0.5,0.9,0.9)
    tleg.SetFillColor(r.kWhite)
    tleg.AddEntry(htemp,"All Toys","f")
    tleg.AddEntry(htempRF,"Truth PDF chosen","f")
    tleg.AddEntry(htempWF,"Other PDF chosen","f")
    tleg.AddEntry(chi2shapeDummy,"Normalised #chi^{2} (n d.o.f=1)  shapes","l")

    c1 = r.TCanvas("c1","c1",500,500)
    c1.SetLogy()
    htemp.Draw()
    htempWF.Draw("same")
    htempRF.Draw("same")
    chi2shape.Draw("same")
    chi2shapeRF.Draw("same")
    chi2shapeWF.Draw("same")
    tleg.Draw("same")

    tlat = r.TLatex()
    tlat.SetNDC()
    tlat.DrawLatex(0.13,0.85,"%s X(%d GeV)"%(tagName,opts.mh))
    tlat.DrawLatex(0.13,0.8,"XS_{truth} = %d"%mu)
    #tlat.DrawLatex(0.13,0.73,"PDF_{truth} = %d"%pdf)
    #print opts.pdfNameDict[tagName]
    tlat.DrawLatex(0.13,0.73,"PDF_{truth} = %s"%opts.pdfNameDict[tagName][pdf])
    c1.SaveAs("biasStudyPlot_%s_mu_%.2f_pdf_%s.pdf"%(tagName,mu,opts.pdfNameDict[tagName][pdf]))
    c1.SaveAs("biasStudyPlot_%s_mu_%.2f_pdf_%s.png"%(tagName,mu,opts.pdfNameDict[tagName][pdf]))

def makePlotsPulls():
  list_of_graphs={}
  pull_vs_mX_graphs={}
  wf=open("log.txt","w")
  wf.close()
  list_of_files=[]
  r.gROOT.SetBatch(1)
  #for root, dirs, files in os.walk(opts.makePlots):
  #  for x in files:
  for root in os.listdir(opts.makePlots):
    for x in os.listdir('%s/%s'%(opts.makePlots,root)):
      if 'merged.root' in x and "Pulls" in x: 
        if (opts.grep==None) or (opts.grep in "%s/%s"%(root,x)):
          print "adding", (opts.makePlots+"/"+root+"/"+x.split(".fail")[0]) 
          list_of_files.append(opts.makePlots+"/"+root+"/"+x.split(".fail")[0])
  for f in list_of_files:
    print f
    #tf = r.TFile.Open(f)
    fshort= f.split("/")[-1]
    #limit = tf.Get("limit")
    #r.gStyle.SetOptStat(0)
    tagName = fshort.split("_mu")[0].replace("_13TeV","")
    mu = float(fshort.split("mu_")[1].split("_")[0])
    mX = float(fshort.split("mh_")[1].split("_")[0])
    kval = (fshort.split("k_")[1].split("_")[0])
    truthPdf = int(fshort.split("truthPdf_")[1].split("_")[0])
    fitPdf = int(fshort.split("fitPdf_")[1].split("_")[0])
    label="%s_mX_%d_k_%s"%(tagName,mX,kval)+"_bkg_%s"%opts.pdfNameDict[tagName][truthPdf]
    label_pull_vs_mx="%s_k_%s"%(tagName,kval)+"_bkg_%s"%opts.pdfNameDict[tagName][truthPdf]
    #if tagName not in "UntaggedTag_2": continue
    #if mu!=1.: continue
    #print f,tagName,mu,pdf
    #pulls_by_fitted_pdf=getAveragePull(f,mu,,truthPdf,fitPdf,tagName)
    pulls_by_fitted_pdf = getAveragePullNew(f,mX,mu,truthPdf,fitPdf,tagName)
    if (mu==0.):
    #if (mu==2.5):
    #if (mu==5.):
        if not label_pull_vs_mx in pull_vs_mX_graphs: pull_vs_mX_graphs[label_pull_vs_mx]={}
        for fitPdf in pulls_by_fitted_pdf.keys():
            if not fitPdf in pull_vs_mX_graphs[label_pull_vs_mx]:pull_vs_mX_graphs[label_pull_vs_mx][fitPdf] =r.TGraphErrors()
            g1 = pull_vs_mX_graphs[label_pull_vs_mx][fitPdf]
            point = g1.GetN()
            g1.SetPoint(point ,mX, pulls_by_fitted_pdf[fitPdf])
            g1.SetPointError( point, 0,0)

    print pulls_by_fitted_pdf
    if not truthPdf in opts.pdfNameDict[tagName].keys(): continue 
    graphname= "%s_%s"%(label,opts.pdfNameDict[tagName][truthPdf])
    if "_750_" in graphname: graphname= graphname.replace("_750_","_0750_")
    if "_500_" in graphname: graphname= graphname.replace("_500_","_0500_")
    if not graphname in list_of_graphs: list_of_graphs[graphname]={}
    for fitPdf in pulls_by_fitted_pdf.keys():
      if not fitPdf in list_of_graphs[graphname]:list_of_graphs[graphname][fitPdf] =r.TGraphErrors()
      g =list_of_graphs[graphname][fitPdf]
      print "g.SetPoint( ",g.GetN(),mu, pulls_by_fitted_pdf[fitPdf],")"
      point = g.GetN()
      g.SetPoint(point ,mu, pulls_by_fitted_pdf[fitPdf])
      g.SetPointError( point, 1.25,0)
      print "setting point for graphname ", graphname , " fitPdf ", fitPdf , " mu ", mu, " pull ", pulls_by_fitted_pdf[fitPdf]

  print list_of_graphs
  colorList=[r.kBlack,r.kRed,r.kGreen,r.kBlue,r.kMagenta,r.kCyan,r.kOrange,r.kViolet,r.kGray,r.kYellow,r.kPink ,r.kAzure, r.kTeal, r.kSpring]
  
  mg_array={}
  tleg_array={}
  tlat_array={}
  print sorted(list_of_graphs.keys())
  for k in sorted(list_of_graphs.keys()):
    c1 = r.TCanvas("c1","c1",600,200)
    tag_graphs=list_of_graphs[k]
    mg = r.TMultiGraph()

    counter=0
    tleg = r.TLegend(0.1,0.7,0.9,0.9)
    tleg.SetNColumns(len(tag_graphs.keys()))
    tleg.SetHeader("Fit Function")
    tleg.SetFillColor(r.kWhite)
    for fitPdf in tag_graphs.keys():
      g =tag_graphs[fitPdf]
      g.SetMarkerColor(colorList[counter])
      g.SetMarkerSize(0.9)
      if not fitPdf in opts.pdfNameDict[k.split("_")[0]].keys(): continue 
      fitPdfString= opts.pdfNameDict[k.split("_")[0]][fitPdf]
      if (fitPdfString==k.rsplit("_",1)[1]):
        g.SetMarkerStyle(21)
      elif (fitPdf==-1):
        g.SetMarkerStyle(20)
      else:
        g.SetMarkerStyle(4)
      counter +=1
      mg.Add(g)
      mean = g.GetMean(2)
      #if not "%_%"%(k,opts.pdfNameDict[k.split("_")[0]][fitPdf]) 
      tleg.AddEntry(g,opts.pdfNameDict[k.split("_")[0]][fitPdf],"p")
    mg.Draw("AP")
    if (mg.GetYaxis()==None): continue
    print mg,mg.GetYaxis() 
    mg.GetYaxis().SetRangeUser(-1.1,1.1)
    #mg.GetXaxis().SetLimits(-1.2,2.2)
    mg.GetXaxis().SetLimits(-7.51,17.6)
    #mg.GetXaxis().SetRangeUser(-1.2,2.2)
    mg.GetXaxis().SetRangeUser(-7.51,17.6)
    mg.GetXaxis().SetTitle("XS");
    mg.GetXaxis().SetTitleSize(0.055);
    if (opts.method=="bias"): mg.GetYaxis().SetTitle("median(XS{fit} - XS_{true}/#sigma_{XS}) ");
    if (opts.method=="nEvents"): mg.GetYaxis().SetTitle("|n_{fit} - n_{true}|/GeV ");
    mg.GetYaxis().SetTitleSize(0.055);
    mg.Draw("AP")
    print " value of k = ", k
    print " value of k.rsplit(_)[0] = ", k.rsplit("_",1)[0]
    print " value of k = ", k
    mX = k.rsplit("_",1)[0].split("mX_")[1].split("_")[0] 
    label = k.rsplit("_",1)[0].replace("mX_%s"%mX,"")
    #label = k.rsplit("_",1)[0].replace("mX_%s"%mX,"")+"_bkg_%s"%(k.rsplit("_",1)[1])
    print " LC DEBUG label ",label
    #exit(1)
    if not label  in mg_array.keys() : mg_array[label] = []
    if not label  in tleg_array.keys() : tleg_array[label] = []
    if not label  in tlat_array.keys() : tlat_array[label] = []
    tleg_array[label].append(tleg)
    tlat_array[label].append("m_{X} = %s"%mX) 
    #mg_array[k.rsplit("_",1)[0]].append(mg)
    mg_array[label].append(mg) 
    #line = r.TLine(-1.1,0,2.2,0)
    line = r.TLine(-7.5,0,17.5,0)
    if (opts.method=="bias"): line.SetLineStyle(r.kDashed)
    line.Draw()
    tleg.Draw()
    tlat = r.TLatex()
    tlat.SetNDC()
    tlat.SetTextSize(0.055)
    tlat.DrawLatex(0.15,0.9,'#bf{%s}'%k.rsplit("_",1)[0])
   # tlat.DrawLatex(0.15,0.79,"#bf{PDF_{truth} = %s}"%k.rsplit("_",1)[1])
    mg.SetTitle(k)
    #tlat.DrawLatex(0.13,0.73,"PDF_{truth} = %d"%pdf)
    #print opts.pdfNameDict[tagName]
    c1.SaveAs("pulls_test_%s.pdf"%k)
    c1.SaveAs("pulls_test_%s.png"%k)
  
  print mg_array
  for tag in mg_array.keys():
    print "LC DEBUG mg_array.keys() ", mg_array.keys()
    #exit(1)
    r.gStyle.SetPadTopMargin(0.2)
    c2 = r.TCanvas("c2","c2",600, (len(mg_array[tag])+1)*200 )
    #c2.Divide(0,len(mg_array[tag]),0.01,0,r.kBlue)
    c2.Divide(0,len(mg_array[tag]),0.01,0.005)
    c2.cd(0)
    r.gPad.SetTopMargin(0.1)
    #c2.SetFrameBorderMode(0)
    #for mg_i in range(len(mg_array[tag])-1,-1,-1):
    for mg_i in range(0,len(mg_array[tag])):
      print mg_i
      c2.cd(mg_i+1)
      mg_array[tag][mg_i].Draw("AP")
      mg_array[tag][mg_i].GetYaxis().SetTitleOffset(0.35);
      mg_array[tag][mg_i].GetXaxis().SetTitleOffset(0.3);
      mg_array[tag][mg_i].GetYaxis().SetTitleSize(0.11);
      mg_array[tag][mg_i].GetYaxis().SetLabelSize(0.07);
      mg_array[tag][mg_i].GetXaxis().SetTitleSize(0.11);
      mg_array[tag][mg_i].GetXaxis().SetLabelSize(0.07);
      #line = r.TLine(-1.1,0,2.2,0)
      line = r.TLine(-7.5,0,17.5,0)
      if (opts.method=="bias"): line.SetLineStyle(r.kDashed)
      line.SetLineWidth(1)
      #line.Draw()
      #line.DrawLine(-1.1,0,2.2,0)
      line.DrawLine(-7.5,0,17.5,0)
      tlat = r.TLatex()
      tlat.SetNDC()
      tlat.SetTextSize(0.1)
      #tlat.DrawLatex(0.15,0.85,'#bf{%s}'%tag)
      #tlat.DrawLatex(0.15,0.79,"%s"%tlat_array[tag][mg_i])
      tlat.SetTextAngle(90)
      tlat.DrawLatex(0.94,0.1,"%s"%tlat_array[tag][mg_i])
      #tlat.Draw("")
      tleg_array[tag][mg_i].Draw("")
    c2.cd(1)
    tlat2= r.TLatex()
    tlat2.SetNDC()
    tlat2.SetTextSize(0.1)
    tlat2.DrawLatex(0.1,0.93,'#bf{%s}'%tag)
    #line = r.TLine(-1.1,0,2.2,0)
    #line.SetLineStyle(r.kDashed)
    #line.SetLineWidth(2)
    #line.Draw()
    #line.DrawLine(-1.1,0,2.2,0)
    c2.SaveAs("pulls_by_tag_%s.pdf"%tag)
    c2.SaveAs("pulls_by_tag_%s.png"%tag)
  print "SORTED KEYS" 
  print sorted(pull_vs_mX_graphs.keys())
  for k in sorted(pull_vs_mX_graphs.keys()):
    print " LC DEBUG start of this loop.."
    tag_graphs=pull_vs_mX_graphs[k]
    exoBSresult = getExoBSResults()[k.split("_")[0]]
    print "LC DEBUG TEST"
    dijetIndex=9999
    if opts.drawCorrected:
      for i in tag_graphs.keys():
        if "dijet2" in opts.pdfNameDict[k.split("_")[0]][i]:
          dijetIndex=i
          break
      if (dijetIndex==9999):
        print "ERROR, you can only make this comparison if you have dijet2 in your fitPDFs!"
        exit(1)
      print "DEBUG LC (tag_graphs[dijetIndex] "
      (tag_graphs[dijetIndex]).Print()
      tag_graphs[dijetIndex]
    if opts.drawCorrected: correctionFactors = getBScorrectionFactors(tag_graphs[dijetIndex],exoBSresult)
    print "EXO BS result : " , exoBSresult
    exoBSresult.Print()
    exoBSresult.SetMarkerStyle(29)
    exoBSresult.SetMarkerColor(13)
    exoBSresult.SetLineColor(13)
    height=200
    if(opts.method=="nEvents"): height=600
    c1 = r.TCanvas("c1","c1",600,height)
    mg = r.TMultiGraph()
    if opts.drawCorrected: mgCorrected = r.TMultiGraph()
    mg.Add(exoBSresult)
    if opts.drawCorrected: mgCorrected.Add(exoBSresult.Clone())

    counter=0
    tleg = r.TLegend(0.1,0.7,0.9,0.9)
    tleg.SetNColumns(1+len(tag_graphs.keys()))
    tleg.SetHeader("Fit Function")
    tleg.SetFillColor(r.kWhite)
    tleg.AddEntry(exoBSresult,"dijet2 (EXO BS)","p")
    for fitPdf in tag_graphs.keys():
      g =tag_graphs[fitPdf]
      if opts.drawCorrected: correctedGraph = applyCorrections(g,correctionFactors)
      g.SetMarkerColor(colorList[counter])
      if opts.drawCorrected: correctedGraph.SetMarkerColor(colorList[counter])
      g.SetMarkerSize(0.9)
      if opts.drawCorrected: correctedGraph.SetMarkerSize(0.9)
      if not fitPdf in opts.pdfNameDict[k.split("_")[0]].keys(): continue 
      fitPdfString= opts.pdfNameDict[k.split("_")[0]][fitPdf]
      if (fitPdf==0):
        g.SetMarkerStyle(21)
        g.SetMarkerSize(1.3)
        if opts.drawCorrected: correctedGraph.SetMarkerStyle(21)
        if opts.drawCorrected: correctedGraph.SetMarkerSize(1.3)
      elif (fitPdf==-1):
        g.SetMarkerStyle(20)
        if opts.drawCorrected: correctedGraph.SetMarkerStyle(20)
      else:
        g.SetMarkerStyle(4)
        if opts.drawCorrected: correctedGraph.SetMarkerStyle(4)
      counter +=1
      mg.Add(g)
      if opts.drawCorrected: mgCorrected.Add(correctedGraph)
      #print "LC DEBUG pritn corrected graph"
      #correctedGraph.Print()
      tleg.AddEntry(g,opts.pdfNameDict[k.split("_")[0]][fitPdf],"p")
    mg.Draw("AP")
    mg.GetXaxis().SetTitle("mX");
    mg.GetXaxis().SetTitleSize(0.055);
    if (opts.method=="bias") :mg.GetYaxis().SetTitle("median((XS_{fit} - XS_{true})/#sigma_{XS}) ");
    if (opts.method=="nEvents") :mg.GetYaxis().SetTitle("|n_{fit}-n_{true}|/GeV ");
    mg.GetYaxis().SetTitleSize(0.055);
    mg.GetYaxis().SetTitleSize(0.055);
    mg.GetYaxis().SetLimits(-3.0,3.50)
    mg.GetYaxis().SetRangeUser(-3.0,3.50)
    if (opts.method=="nEvents"):
      #mg.GetYaxis().SetLimits(10e-5,2)
      #mg.GetYaxis().SetRangeUser(10e-5,2)
      #c1.SetLogy(1)
      mg.GetYaxis().SetLimits(-10,10)
      mg.GetYaxis().SetRangeUser(-10,10)
      c1.SetLogy(0)
      
    mg.Draw("AP")
    exoBSresult.Draw("same P")
    line = r.TLine(-7.5,0,17.5,0)
    box = r.TBox(250,-0.5,5500,0.5)
    box.SetFillStyle(3003)
    box.SetFillColor(r.kBlack)
    if (opts.method=="bias"): 
      box.DrawBox(250,-0.5,5500,0.5)
      line.SetLineStyle(r.kDashed)
      line.Draw()
    tleg.Draw()
    tlat = r.TLatex()
    tlat.SetNDC()
    tlat.SetTextSize(0.055)
    tlat.DrawLatex(0.15,0.9,'#bf{%s}'%k.rsplit("_",1)[0])
    mg.SetTitle(k)
    if (opts.method=="bias"):
      c1.SaveAs("pulls_vs_mX_%s.pdf"%k)
      c1.SaveAs("pulls_vs_mX_%s.png"%k)
    if (opts.method=="nEvents"):
      c1.SaveAs("nEvents_vs_mX_%s.pdf"%k)
      c1.SaveAs("nEvents_vs_mX_%s.png"%k)
    c1.SetLogy(0)
    c1.Clear()
    if opts.drawCorrected:
      mgCorrected.Draw("AP")
      mgCorrected.GetXaxis().SetTitle("mX");
      mgCorrected.GetXaxis().SetTitleSize(0.055);
      mgCorrected.GetYaxis().SetTitle("<(XS - #hat{XS})/#sigma_{XS} > (corrected) ");
      mgCorrected.GetYaxis().SetTitleSize(0.055);
      mgCorrected.GetYaxis().SetLimits(-1.0,1.50)
      mgCorrected.GetYaxis().SetRangeUser(-1.0,1.50)
      #mgCorrected.GetXaxis().SetLimits(-1.2,2.2)
      #mgCorrected.GetXaxis().SetLimits(-7.51,17.6)
      #mgCorrected.GetXaxis().SetRangeUser(-1.2,2.2)
      #mgCorrected.GetXaxis().SetRangeUser(-7.51,17.6)
      mgCorrected.Draw("AP")
      line.Draw()
      tleg.Draw()
      tlat.DrawLatex(0.15,0.9,'#bf{%s}'%k.rsplit("_",1)[0])
      box.DrawBox(250,-0.5,5500,0.5)
      mgCorrected.SetTitle(k+" (Corrected)")
      c1.SaveAs("pulls_vs_mX_%s_corrected.pdf"%k)
      c1.SaveAs("pulls_vs_mX_%s_corrected.png"%k)
  print "DEBUG lc0"
  


def getPdfNameDict(tags):
  pdfNameDict={} 
  f="multipdf_all_ho_%s.ALLFUNCTIONS.root"%opts.lumi
  tf = r.TFile.Open(f)
  #f= f.split("/")[-1]
  w = tf.Get("wtemplates")
  for tag in tags:
   #mpdf= w.obj("model_bkg_%s_LC"%tag)
   mpdf= w.obj("model_bkg_%s"%tag)
   mpdf.Print()
   nPdfs = mpdf.getNumPdfs()
   #pdfNameDict[tag]=[]
   pdfNameDict[tag]={}
   for i in range (0,nPdfs):
     print "pdf ",i, " name " ,mpdf.getPdf(i).GetName()
     #pdfNameDict[tag].append(mpdf.getPdf(i).GetName().split("_")[-1])
     pdfNameDict[tag][i]=mpdf.getPdf(i).GetName().split("_")[-1]
   #pdfNameDict[tag].append(mpdf.getPdf(i).GetName().split("_")[-1])
   pdfNameDict[tag][-1]="envelope"
   pdfNameDict[tag][-2]="mc_bkg"
  return  pdfNameDict

def makeSplittedDatacards(datacard):
  path="./"
  if "/" in datacard:
    path = datacard.rsplit("/",1)[0]
    datacard = datacard.rsplit("/",1)[1] 

  print "path =" ,path
  print "datacard =" ,datacard
  system('cp %s/* .'%(path))

  f = open(datacard)
  allCats = set()
  for line in f.readlines():
   if line.startswith('bin'):
    for el in line.split()[1:]:
       allCats.add(el)
  f.close()
  print ' [INFO] -->Found these categories in card: ', allCats
  veto = ""
  for cat in allCats:
    veto="ch1_"+cat
    splitCardName = 'datacard%s.txt'%cat
    system('combineCards.py --ic="%s" %s > %s'%(veto,datacard,splitCardName))
    print ('combineCards.py --ic="%s" %s > %s'%(veto,datacard,splitCardName))
    card = open('%s'%(splitCardName),'r')
    newCard = open('tempcard.txt','w')
    newCard_gen = open('tempcard_gen.txt','w') # this one is for the case where toys are generated from a fixed RooHistPdf
    for line in card.readlines():
       if 'discrete' in line:
         if cat in line: 
          newCard.write(line.replace("750","%s"%opts.mh))
          # no need to add the "discrete" to the newCard_gen
       else: 
        newline =line.replace("750","%s"%opts.mh)
        newline_gen =line.replace("750","%s"%opts.mh)
        #if opts.useMCBkgShape : 
        if "shapes" in line and "bkg" in line :
            #newline_gen = newline.replace("multipdf_all_ho.root wtemplates:model_bkg_%s"%cat,"mctruth_7415v2_v5_mc_roohistpdf.root roohistpdfs:pdf_reduced_mctruth_pp_cic2_%s_binned"%cat)
            newline = "shapes bkg  ch1_%s multipdf_all_ho_%s.ALLFUNCTIONS.root wtemplates:model_bkg_%s \n"%(cat,opts.lumi,cat)
            #newline = "shapes bkg  ch1_%s multipdf_all_ho_%s.root wtemplates:model_bkg_%s_LC \n"%(cat,opts.lumi,cat)
          #if "rate" in line :
            #if cat=="EBEE" : newline_gen = "rate  1.000   %d\n"%(int(opts.nEvents.split(":")[0]))
            #if cat=="EBEB" : newline_gen = "rate  1.000   %d\n"%(int(opts.nEvents.split(":")[1]))
          #if "shapes" in line and "data_obs" in line :
            #newline_gen = newline.replace("multipdf_all_ho.root wtemplates:data_%s"%cat,"mctruth_7415v2_v5_mc_roohistpdf.root roohistpdfs:reduced_mctruth_pp_cic2_%s_binned"%cat)#.replace("data","data_cic2")
            #newline = newline.replace("data_%s"%cat,"data_cic2_%s"%cat)
        newCard.write(newline)
        newCard_gen.write(newline_gen)
    card.close()
    newCard.write("pdfindex_%s discrete"%cat)
    newCard.close()
    newCard_gen.close()
    system('mv %s %s'%(newCard.name,card.name))
    system('mv %s %s'%(newCard_gen.name,card.name.replace(".txt","_gen.txt")))
    print "new datacard done ", card.name
    print "new datacard done ", card.name.replace(".txt","_gen.txt")
    print 'text2workspace.py %s  -o biasStudyWS_k%s_m%d_%s.root -L libdiphotonsUtils'%(card.name,opts.k, int(opts.mh), cat)
    system('text2workspace.py %s  -o biasStudyWS_k%s_m%d_%s.root -L libdiphotonsUtils'%(card.name,opts.k, int(opts.mh), cat))
    print 'text2workspace.py %s  -o biasStudyWS_k%s_m%d_%s_gen.root -L libdiphotonsUtils'%(card.name.replace(".txt","_gen.txt"),opts.k, int(opts.mh), cat)
    system('text2workspace.py %s  -o biasStudyWS_k%s_m%d_%s_gen.root -L libdiphotonsUtils'%(card.name.replace(".txt","_gen.txt"),opts.k, int(opts.mh), cat))
    print "new datacard done ", card.name, " aka  biasStudyWS_k%s_m%d_%s.root"%(opts.k, int(opts.mh),cat)
    print "new gen datacard done ", card.name.replace(".txt","_gen.txt"), " aka  biasStudyWS_k%s_m%d_%s_gen.root"%(opts.k, int(opts.mh),cat)



#getExoBSResults()
#exit(1)
#muValues = [0.,1.,2.]
#muValues = [-1.0,-0.75,-0.5,-0.25,0.,0.25,0.5,0.75,1.,1.25,1.5,1.75,2.]
#muValues = [-1.0,-0.5,0.,0.5,1.,1.5,2.]
#muValues = [-1.0,0.0,1.0,2.]
#muValues = [-0.75,-0.5,-0.25,0.25,0.5,0.75,1.25,1.5,1.75]
#muValues = [-1.0,-0.5,-0.25,0.0,0.25,0.5,0.75,1.0,1.25,1.5,1.75,2.0]
#muValues = [0.25,0.5,0.75,1.0,1.25,1.5,1.75,2]
muValues = [0]
#muValues = [0,2.5,5]
#muValues = [-5,-2.5,0,2.5,5,7.5,10,12.5,15]
#muValues = [5]
#muValues = [2]
#muValues = [0.25,0.5,1.0,1.5,2]
#muValues = [-]
#catValues = ["UntaggedTag_0","UntaggedTag_1","UntaggedTag_2","UntaggedTag_3","VBFTag_0","VBFTag_1","TTHLeptonicTag","TTHHadronicTag"]
catValues = ["EBEB","EBEE"]
#catValues = ["EBEB"]

opts.exoEA=getExoEA()

opts.nTrueArray= getNTrue(catValues)

if opts.splitDatacard:
  makeSplittedDatacards(opts.splitDatacard)
  exit(1)

if (opts.k and opts.mh):
  print "DEBUG LC 1"
  #opts.splitDatacard="datacardsNew/k%s/datacard_full_analysis_moriond16v1_sync_v4_data_cic2_lc_bias_study_spin2_wnuis_lumi_2.69_grav_%s_750.txt"%(opts.k,opts.k)
  #file_path="%s/%s"%(opts.splitDatacard.rsplit("/",1)[0],"full_analysis_moriond16v1_sync_v4_data_cic2_lc_bias_study_spin2_wnuis_lumi_2.69.root")
  opts.splitDatacard="datacardsNew_v2/k%s/datacard_full_analysis_moriond16v1_sync_v4_data_cic2_lc_bias_study_v2_spin2_wnuis_lumi_%s_grav_%s_750.txt"%(opts.k,opts.lumi,opts.k)
  file_path="%s/%s"%(opts.splitDatacard.rsplit("/",1)[0],"full_analysis_moriond16v1_sync_v4_data_cic2_lc_bias_study_v2_spin2_wnuis_lumi_%s.root"%opts.lumi)
  if (os.path.isfile(file_path)):
    print "[INFO] copied datacard"
  else:
    print "[ERROR] could not find ", file_path
    exit (1)
  os.system("cp %s ."%(file_path))
  print "DEBUG LC 2"
  makeSplittedDatacards(opts.splitDatacard)
  print "DEBUG LC 3"
  if (opts.justSplit) : exit(1)


opts.pdfNameDict = getPdfNameDict(catValues)
if opts.hadd:
  trawlHadd()
  exit(1)

if opts.resubmit:
  trawlResubmit()
  exit(1)

if opts.makePlots:
  #makePlotsDeltaL()
  makePlotsPulls()
  print "DEBUG lc01"
  exit(1)

if opts.deleteFailures:
  deleteFailures()
  exit(1)

opts.mh = int(opts.mh)

system('mkdir -p biasStudyJobs')
for mu in muValues:
  for cat in catValues:
    pdfValues=opts.pdfNameDict[cat].keys()
    #for truthPdf in pdfValues:
    for truthPdf in [-2]:
      for fitPdf in pdfValues:
        if (fitPdf==-2): continue
        counter=0
        system('mkdir -p biasStudyJobs/%s_mu_%.2f_mh_%d_k_%s_truthPdf_%d_fitPdf_%d_Pulls'%(cat,mu,opts.mh,opts.k,truthPdf,fitPdf))
        #system('rm biasStudyJobs/%s_mu_%d_pdf_%d/sub*'%(cat,mu,pdf))
        if (opts.batch == "IC"):
           #submit paramtetric 
           file = open('%s/biasStudyJobs/%s_mu_%.2f_mh_%d_k_%s_truthPdf_%d_fitPdf_%d_Pulls/sub.sh'%(opts.outDir,cat,mu,opts.mh,opts.k,truthPdf,fitPdf),'w')
           print " making", ('%s/biasStudyJobs/%s_mu_%.2f_mh_%d_k_%s_truthPdf_%d_fitPdf_%d_Pulls/sub.sh'%(opts.outDir,cat,mu,opts.mh,opts.k,truthPdf,fitPdf),'w')
           writePreamble(file,mu,opts.mh,cat,truthPdf,fitPdf,"Pulls")
           writePostamble(file)
'''
for mu in muValues:
  for cat in catValues:
    for pdf in pdfValues:
        counter=0
        system('mkdir -p biasStudyJobs/%s_mu_%.2f_mh_%d_pdf_%d_DeltaL'%(cat,mu,opts.mh,pdf))
        #system('mkdir -p biasStudyJobs/%s_mu_%.2f_mh_%d_pdf_%d_Pulls'%(cat,mu,opts.mh,pdf))
        #system('rm biasStudyJobs/%s_mu_%.2f_pdf_%d/sub*'%(cat,mu,pdf))
        if (opts.batch == "IC"):
           #submit paramtetric 
           file = open('%s/biasStudyJobs/%s_mu_%.2f_mh_%d_pdf_%d_DeltaL/sub.sh'%(opts.outDir,cat,mu,opts.mh,pdf),'w')
           print "making file  biasStudyJobs/%s_mu_%.2f_mh_%d_pdf_%d_DeltaL/sub.sh"%(cat,mu,opts.mh,pdf)
           writePreamble(file,mu,cat,pdf,-999,"DeltaL")
           writePostamble(file)
        else :
          for counter in range(0,20):
           file = open('%s/biasStudyJobs/%s_mu_%.2f_mh_%d_pdf_%d_DeltaL/sub%d.sh'%(opts.outDir,cat,mu,opts.mh,pdf,counter),'w')
           print "making file  biasStudyJobs/%s_mu_%.2f_mh_%d_pdf_%d_DeltaL/sub%d.sh"%(cat,mu,opts.mh,pdf,counter)
           writePreamble(file,mu,cat,pdf,-999,"DeltaL")
           #print exec_line
           writePostamble(file)
           counter =  counter+1
'''
  
  
  

