import os
import glob
import re
from commonObjects import *

def run(cmd):
  print "%s\n\n"%cmd
  os.system(cmd)

def writePreamble(_file):
  _file.write("#!/bin/bash\n")
  _file.write("ulimit -s unlimited\n")
  _file.write("set -e\n")
  _file.write("cd %s/src\n"%os.environ['CMSSW_BASE'])
  _file.write("export SCRAM_ARCH=%s\n"%os.environ['SCRAM_ARCH'])
  _file.write("source /cvmfs/cms.cern.ch/cmsset_default.sh\n")
  _file.write("eval `scramv1 runtime -sh`\n")
  _file.write("cd %s\n"%dwd__)
  _file.write("export PYTHONPATH=$PYTHONPATH:%s/tools:%s/tools\n\n"%(cwd__,dwd__))

def writeCondorSub(_file,_exec,_queue,_nJobs,_jobOpts,doHoldOnFailure=True,doPeriodicRetry=True):
  _file.write("executable = %s.sh\n"%_exec)
  _file.write("arguments  = $(ProcId)\n")
  _file.write("output     = %s.$(ClusterId).$(ProcId).out\n"%_exec)
  _file.write("error      = %s.$(ClusterId).$(ProcId).err\n\n"%_exec)
  if _jobOpts != '':
    _file.write("# User specified job options\n")
    for jo in _jobOpts.split(":"): _file.write("%s\n"%jo)
    _file.write("\n")
  if doHoldOnFailure:
    _file.write("# Send the job to Held state on failure\n")
    _file.write("on_exit_hold = (ExitBySignal == True) || (ExitCode != 0)\n\n")
  if doPeriodicRetry:
    _file.write("# Periodically retry the jobs every 10 minutes, up to a maximum of 5 retries.\n")
    _file.write("periodic_release =  (NumJobStarts < 3) && ((CurrentTime - EnteredCurrentStatus) > 600)\n\n")
  _file.write('+AccountingGroup = "group_u_CMS.u_zh.users"\n')
  _file.write("+JobFlavour = \"%s\"\n"%_queue)
  _file.write("queue %g"%_nJobs)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def writeSubFiles(_opts):
  # Make directory to store sub files
  if not os.path.isdir("%s/yields_%s"%(dwd__,_opts['ext'])): os.system("mkdir %s/yields_%s"%(dwd__,_opts['ext']))
  if not os.path.isdir("%s/yields_%s/jobs"%(dwd__,_opts['ext'])): os.system("mkdir %s/yields_%s/jobs"%(dwd__,_opts['ext']))

  _jobdir = "%s/yields_%s/jobs"%(dwd__,_opts['ext'])
  # Remove current job files
  if len(glob.glob("%s/*"%_jobdir)): os.system("rm %s/*"%_jobdir)
  
  # CONDOR
  if "condor" in _opts['batch']:
    _executable = "condor_yields_%s"%_opts['ext']
    _f = open("%s/%s.sh"%(_jobdir,_executable),"w") # single .sh script split into separate jobs
    writePreamble(_f)

    # Loop over categories
    for cidx in range(_opts['nCats']):
      c = _opts['cats'].split(",")[cidx]
      _f.write("if [ $1 -eq %g ]; then\n"%cidx)
      _f.write("  python %s/makeYields.py --cat %s --procs %s --ext %s --mass %s --inputWSDirMap %s %s\n"%(dwd__,c,_opts['procs'],_opts['ext'],_opts['mass'],_opts['inputWSDirMap'],_opts['modeOpts']))
      _f.write("fi\n")
      
    # Close .sh file
    _f.close()
    os.system("chmod 775 %s/%s.sh"%(_jobdir,_executable))

    # Condor submission file
    _fsub = open("%s/%s.sub"%(_jobdir,_executable),"w")
    writeCondorSub(_fsub,_executable,_opts['queue'],_opts['nCats'],_opts['jobOpts'])
    _fsub.close()
    
  # SGE...
  if (_opts['batch'] == "IC")|(_opts['batch'] == "SGE")|(_opts['batch'] == "local" ):
    _executable = "sub_yields_%s"%_opts['ext']

    for cidx in range(_opts['nCats']):
      c = _opts['cats'].split(",")[cidx]
      _f = open("%s/%s_%s.sh"%(_jobdir,_executable,c),"w")
      writePreamble(_f)
      _f.write("python %s/makeYields.py --cat %s --procs %s --ext %s --mass %s --inputWSDirMap %s --sigModelWSDir %s --sigModelExt %s --bkgModelWSDir %s --bkgModelExt %s %s\n"%(dwd__,c,_opts['procs'],_opts['ext'],_opts['mass'],_opts['inputWSDirMap'],_opts['sigModelWSDir'],_opts['sigModelExt'],_opts['bkgModelWSDir'],_opts['bkgModelExt'],_opts['modeOpts']))
      _f.close()
      os.system("chmod 775 %s/%s_%s.sh"%(_jobdir,_executable,c))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Function for submitting files to batch system
def submitFiles(_opts):
  _jobdir = "%s/yields_%s/jobs"%(dwd__,_opts['ext'])
  # CONDOR
  if "condor" in _opts['batch']:
    _executable = "condor_yields_%s"%_opts['ext']
    if _opts['batch'] == "condor_lxplus": cmdLine = "cd %s; condor_submit -spool %s.sub; cd %s"%(_jobdir,_executable,dwd__)
    elif _opts['batch'] == "condor": cmdLine = "cd %s; condor_submit %s.sub; cd %s"%(_jobdir,_executable,dwd__)
    else: print "PROBLEM: Only condor_lxplus or condor allowed as condor-like settings for batch. Please check your settings."
    run(cmdLine)
    print "  --> Finished submitting files"

  # SGE
  elif _opts['batch'] in ['IC','SGE']:
    _executable = "sub_yields_%s"%_opts['ext']

    # Extract job opts
    jobOptsStr = _opts['jobOpts']

    for cidx in range(_opts['nCats']):
      c = _opts['cats'].split(",")[cidx]
      _subfile = "%s/%s_%s"%(_jobdir,_executable,c)
      cmdLine = "qsub -q hep.q %s -o %s.log -e %s.err %s.sh"%(jobOptsStr,_subfile,_subfile,_subfile)
      run(cmdLine)
    print "  --> Finished submitting files"
  
  # Running locally
  elif _opts['batch'] == 'local':
    _executable = "sub_yields_%s"%_opts['ext']
    for cidx in range(_opts['nCats']):
      c = _opts['cats'].split(",")[cidx]
      _subfile = "%s/%s_%s"%(_jobdir,_executable,c)
      cmdLine = "bash %s.sh"%_subfile
      run(cmdLine)
    print "  --> Finished running files"

 
