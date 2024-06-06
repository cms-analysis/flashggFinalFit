import os
import glob
import re
from commonObjects import *
from commonTools import *

def run(cmd):
  print("%s\n\n"%cmd)
  os.system(cmd)

def writePreamble(_file,_otherBase=None):
  _file.write("#!/bin/bash\n")
  _file.write("ulimit -s unlimited\n")
  _file.write("set -e\n")
  if _otherBase is not None: _file.write("cd %s\n"%_otherBase)
  else: _file.write("cd %s/src\n"%os.environ['CMSSW_BASE'])
  _file.write("export SCRAM_ARCH=%s\n"%os.environ['SCRAM_ARCH'])
  _file.write("source /cvmfs/cms.cern.ch/cmsset_default.sh\n")
  _file.write("eval `scramv1 runtime -sh`\n")
  _file.write("cd %s\n"%twd__)
  _file.write("export PYTHONPATH=$PYTHONPATH:%s/tools:%s/tools\n\n"%(cwd__,twd__))

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
  _file.write("+JobFlavour = \"%s\"\n"%_queue)
  _file.write("queue %g"%_nJobs)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def writeSubFiles(_opts):
  # Make directory to store sub files
  if not os.path.isdir("%s/outdir_%s"%(twd__,_opts['ext'])): os.system("mkdir %s/outdir_%s"%(twd__,_opts['ext']))
  if not os.path.isdir("%s/outdir_%s/%s"%(twd__,_opts['ext'],_opts['mode'])): os.system("mkdir %s/outdir_%s/%s"%(twd__,_opts['ext'],_opts['mode']))
  if not os.path.isdir("%s/outdir_%s/%s/jobs"%(twd__,_opts['ext'],_opts['mode'])): os.system("mkdir %s/outdir_%s/%s/jobs"%(twd__,_opts['ext'],_opts['mode']))

  _jobdir = "%s/outdir_%s/%s/jobs"%(twd__,_opts['ext'],_opts['mode'])
  # Remove current job files
  if len(glob.glob("%s/*"%_jobdir)): os.system("rm %s/*"%_jobdir)
  
  # CONDOR
  if _opts['batch'] == "condor":
    _executable = "condor_%s_%s"%(_opts['mode'],_opts['ext'])
    _f = open("%s/%s.sh"%(_jobdir,_executable),"w") # single .sh script split into separate jobs
    writePreamble(_f)

    # Write details depending on mode
    if( _opts['mode'] == "trees2ws" ):
      # Extract list of files
      tfiles = glob.glob("%s/*.root"%_opts['inputDir'])
      # Run separate command per file
      for tfidx,tf in enumerate(tfiles):
        # Extract production mode (and decay extension if required)
        p, d = signalFromFileName(tf)
        m = massFromFileName(tf)
        _cmd = "python3 %s/trees2ws.py --inputConfig %s --inputTreeFile %s --inputMass %s --productionMode %s --year %s"%(twd__,_opts['inputConfig'],tf,m,p,_opts['year'])
        if d is not None: _cmd += " --decayExt %s"%d
        if _opts['modeOpts'] != '': _cmd += " %s"%_opts['modeOpts']
        _f.write("if [ $1 -eq %g ]; then\n"%tfidx)
        _f.write(" %s\n"%_cmd)
        _f.write("fi\n")
         
    elif( _opts['mode'] == "trees2ws_data" ):
      # Extract list of files
      tfiles = glob.glob("%s/*.root"%_opts['inputDir'])
      # Run separate command per file
      for tfidx,tf in enumerate(tfiles):
        _cmd = "python3 %s/trees2ws_data.py --inputConfig %s --inputTreeFile %s"%(twd__,_opts['inputConfig'],tf)
        if _opts['modeOpts'] != '': _cmd += " %s"%_opts['modeOpts']
        _f.write("if [ $1 -eq %g ]; then\n"%tfidx)
        _f.write(" %s\n"%_cmd)
        _f.write("fi\n")

    elif( _opts['mode'] == "mass_shift" ):
      # Extract list of ws files
      wsfiles = glob.glob("%s/*.root"%_opts['inputDir'])
      # Separate submission per ws file
      for fidx,f in enumerate(wsfiles):
        _f.write("if [ $1 -eq %g ]; then\n"%tfidx)
        # Add command per target mass
        for tm in _opts['targetMasses'].split(","):
          _f.write("python3 %s/mass_shifter.py --inputWSFile %s --inputMass %s --targetMass %s %s\n"%(twd__,f,_opts['inputMass'],tm,_opts['modeOpts']))
        _f.write("fi\n")

    # Close .sh file
    _f.close()
    os.system("chmod 775 %s/%s.sh"%(_jobdir,_executable))

    # Condor submission file
    _fsub = open("%s/%s.sub"%(_jobdir,_executable),"w")
    if( _opts['mode'] == "trees2ws" )|( _opts['mode'] == "trees2ws_data" ): writeCondorSub(_fsub,_executable,_opts['queue'],len(tfiles),_opts['jobOpts'])
    elif( _opts['mode'] == "mass_shift" ): writeCondorSub(_fsub,_executable,_opts['queue'],len(wsfiles),_opts['jobOpts'])
    _fsub.close()
    
  # SGE...
  if (_opts['batch'] == "IC")|(_opts['batch'] == "SGE")|(_opts['batch'] == "local" ):
    _executable = "sub_%s_%s"%(_opts['mode'],_opts['ext'])

    # Write details depending on mode
    if( _opts['mode'] == "trees2ws" ):
      # Extract list of files
      tfiles = glob.glob("%s/*.root"%_opts['inputDir'])
      # Create separate submission file per script
      for tfidx,tf in enumerate(tfiles):
        _f = open("%s/%s_%g.sh"%(_jobdir,_executable,tfidx),"w")
        writePreamble(_f)
        # Extract production mode (and decay extension if required)
        m = massFromFileName(tf)
        p, d = signalFromFileName(tf)
        _cmd = "python3 %s/trees2ws.py --inputConfig %s --inputTreeFile %s --inputMass %s --productionMode %s --year %s"%(twd__,_opts['inputConfig'],tf,m,p,_opts['year'])
        if d is not None: _cmd += " --decayExt %s"%d
        if _opts['modeOpts'] != '': _cmd += " %s"%_opts['modeOpts'] 
        _f.write("%s\n"%_cmd)
        _f.close()
        os.system("chmod 775 %s/%s_%g.sh"%(_jobdir,_executable,tfidx))
        
    elif( _opts['mode'] == "trees2ws_data" ):
      # Extract list of files
      tfiles = glob.glob("%s/*.root"%_opts['inputDir'])
      # Create separate submission file per script
      for tfidx,tf in enumerate(tfiles):
        _f = open("%s/%s_%g.sh"%(_jobdir,_executable,tfidx),"w")
        writePreamble(_f)
        _cmd = "python3 %s/trees2ws_data.py --inputConfig %s --inputTreeFile %s"%(twd__,_opts['inputConfig'],tf)
        if _opts['modeOpts'] != '': _cmd += " %s"%_opts['modeOpts']
        _f.write("%s\n"%_cmd)
        _f.close()
        os.system("chmod 775 %s/%s_%g.sh"%(_jobdir,_executable,tfidx))
        
    elif( _opts['mode'] == "mass_shift" ):
      # Extract list of ws files
      wsfiles = glob.glob("%s/*.root"%_opts['inputDir'])
      # Separate submission job per file
      for fidx,f in enumerate(wsfiles):
        _f = open("%s/%s_%g.sh"%(_jobdir,_executable,fidx),"w")
        writePreamble(_f)
        # Add a command per target mass
        for tm in _opts['targetMasses'].split(","):
          _f.write("python3 %s/mass_shifter.py --inputWSFile %s --inputMass %s --targetMass %s %s\n"%(twd__,f,_opts['inputMass'],tm,_opts['modeOpts']))
        _f.close()
        os.system("chmod 775 %s/%s_%g.sh"%(_jobdir,_executable,fidx))
 
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Function for submitting files to batch system
def submitFiles(_opts):
  _jobdir = "%s/outdir_%s/%s/jobs"%(twd__,_opts['ext'],_opts['mode'])
  # CONDOR
  if _opts['batch'] == "condor":
    _executable = "condor_%s_%s"%(_opts['mode'],_opts['ext'])
    if os.environ['PWD'].startswith("/eos"):
      cmdLine = "cd %s; condor_submit -spool %s.sub; cd %s"%(_jobdir,_executable,twd__)
    else:
      cmdLine = "cd %s; condor_submit %s.sub; cd %s"%(_jobdir,_executable,twd__)
    run(cmdLine)
    print("  --> Finished submitting files")

  # SGE
  elif _opts['batch'] in ['IC','SGE']:
    _executable = "sub_%s_%s"%(_opts['mode'],_opts['ext'])

    # Extract job opts
    jobOptsStr = _opts['jobOpts']

    if( _opts['mode'] == "trees2ws" )|( _opts['mode'] == 'trees2ws_data' ):
      tfiles = glob.glob("%s/*.root"%_opts['inputDir'])
      for tfidx in range(len(tfiles)):
        _subfile = "%s/%s_%g"%(_jobdir,_executable,tfidx)
        cmdLine = "qsub -q %s %s -o %s.log -e %s.err %s.sh"%(_opts['queue'],jobOptsStr,_subfile,_subfile,_subfile)
        run(cmdLine)

    elif( _opts['mode'] == 'mass_shift' ):
      wsfiles = glob.glob("%s/*.root"%_opts['inputDir'])
      for fidx in range(len(wsfiles)):
        _subfile = "%s/%s_%g"%(_jobdir,_executable,fidx)
        cmdLine = "qsub -q %s %s -o %s.log -e %s.err %s.sh"%(_opts['queue'],jobOptsStr,_subfile,_subfile,_subfile)
        run(cmdLine)

    print("  --> Finished submitting files")
  
  # Running locally
  elif _opts['batch'] == 'local':
    _executable = "sub_%s_%s"%(_opts['mode'],_opts['ext'])

    if( _opts['mode'] == "trees2ws" )|( _opts['mode'] == 'trees2ws_data' ):
      tfiles = glob.glob("%s/*.root"%_opts['inputDir'])
      for tfidx in range(len(tfiles)):
        _subfile = "%s/%s_%g"%(_jobdir,_executable,tfidx)
        cmdLine = "bash %s.sh"%(_subfile)
        run(cmdLine)

    elif( _opts['mode'] == 'mass_shift' ):
      wsfiles = glob.glob("%s/*.root"%_opts['inputDir'])
      for fidx in range(len(wsfiles)):
        _subfile = "%s/%s_%g"%(_jobdir,_executable,fidx)
        cmdLine = "bash %s.sh"%(_subfile)
        run(cmdLine)

    print("  --> Finished running files")
