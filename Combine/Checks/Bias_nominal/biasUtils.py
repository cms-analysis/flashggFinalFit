#!/usr/bin/env python
import os 
from submissionTools import writeCondorSub


def rooArgSetToList(argset): ## taken from Andrea Marini's great repo here: https://github.com/amarini/rfwsutils/blob/master/wsutils.py#L300-L313
    """creates a python list with the contents of argset (which should be a RooArgSet)"""
    it = argset.createIterator()

    retval = []
    while True:
        obj = it.Next()

        if obj == None:
            break

        retval.append(obj)

    return retval

def raiseMultiError(lax=False):
    raise RuntimeError('Found more than one multipdf here - please create a workspace with just one for these bias studies. You can use "combineCards.py Datacard.txt --ic cat_name" for this)')

def raiseFailError(itoy, lax=False):
    text = 'some fits have failed, wrong quantile for toy number %g'%itoy
    if not lax: raise RuntimeError('ERROR %s'%text)
    else: print 'WARNING %s'%text

def shortName(name):
    return name.split('_')[-1]

def toyName(name, split=None):
    retval = 'BiasToys/biasStudy_%s_toys.root'%name
    if split is not None: 
        split = int(split)
        retval = retval.replace(name,'%s_split%g'%(name,split))
    return retval

def toyName2(name, split=None):
    retval = 'biasStudy_%s_toys.root'%name
    if split is not None: 
        split = int(split)
        retval = retval.replace(name,'%s_split%g'%(name,split))
    return retval

def fitName(name, split=None):
    retval = 'BiasFits/biasStudy_%s_fits.root'%name
    if split is not None: 
        split = int(split)
        retval = retval.replace(name,'%s_split%g'%(name,split))
    return retval
def fitName2(name, split=None):
    retval = 'biasStudy_%s_fits.root'%name
    if split is not None: 
        split = int(split)
        retval = retval.replace(name,'%s_split%g'%(name,split))
    return retval

def plotName(name):
    return 'BiasPlots/biasStudy_%s_pulls'%name

def run(cmd, dry=False):
   print cmd
   if not dry: os.system(cmd)


def writePreamble(_file,_otherBase=None):
  twd__ = os.getcwd()
  _file.write("#!/bin/bash\n")
  _file.write("ulimit -s unlimited\n")
  #_file.write("set -e\n")
  if _otherBase is not None: _file.write("cd %s\n"%_otherBase)
  else: _file.write("cd %s/src\n"%os.environ['CMSSW_BASE'])
  _file.write("export SCRAM_ARCH=%s\n"%os.environ['SCRAM_ARCH'])
  _file.write("source /cvmfs/cms.cern.ch/cmsset_default.sh\n")
  _file.write("cmsenv\n")
  _file.write("cd %s\n"%twd__)
  _file.write("export PYTHONPATH=$PYTHONPATH:/afs/cern.ch/user/f/fderiggi/CMSSW_10_2_13/src/flashggFinalFit/tools:/afs/cern.ch/user/f/fderiggi/CMSSW_10_2_13/src/flashggFinalFit/Trees2WS/tools\n\n")

def writeSubFiles(ext,file, batch = 'condor'):
  twd__ = os.getcwd()
  
  # print("mkdir -p %s/outdir_%s/jobs"%(twd__,_opts.ext))
  # Make directory to store sub files
  os.system("mkdir -p  %s/outdir_OutputBias_Jobs/outdir_%s"%(twd__,ext))
  os.system("mkdir -p %s/outdir_OutputBias_Jobs/outdir_%s/jobs"%(twd__,ext))
 
  _jobdir = "%s/outdir_OutputBias_Jobs/outdir_%s/jobs"%(twd__,ext)
  # Remove current job files
#  if len(glob.glob("%s/*"%_jobdir)): os.system("rm %s/*"%_jobdir)
 
  # CONDOR
  if batch == "condor":
    _executable = "condor_%s"%(ext)
    _f = open("%s/%s.sh"%(_jobdir,_executable),"w") # single .sh script split into separate jobs
    writePreamble(_f)

  # Write details depending on mode
   # Extract list of files
   # Run separate command per file
   
    with open(file, 'r') as f:
    # Leggi il file riga per riga
         i = 0
         for _cmd in f:
            if _cmd == '': continue
            _f.write("if [ $1 -eq %g ]; then\n"%i)
            _f.write(" %s\n"%_cmd)
            _f.write("fi\n")
            i = i+1
    
  _f.close()
  os.system("chmod 775 %s/%s.sh"%(_jobdir,_executable))
  #SUB file
  _fsub = open("%s/%s.sub"%(_jobdir,_executable),"w")
  writeCondorSub(_fsub,_executable,"workday",i,'')
  cmdLine = "cd %s; condor_submit %s.sub; cd %s"%(_jobdir,_executable,twd__)
  print(cmdLine)
  #run(cmdLine)

