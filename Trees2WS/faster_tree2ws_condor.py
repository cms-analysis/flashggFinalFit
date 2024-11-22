import os
import time
from commonObjects import *
from commonTools import *
import subprocess, glob
import errno


# Define an array of input masses
input_masses = [120, 125, 130]

# Define an array of eras
eras = ["preEE", "postEE"]

# Define an array of production modes and corresponding process strings
production_modes = [
    ("ggh", "GluGluHtoGG"),
    ("vbf", "VBFHtoGG"),
    ("vh", "VHtoGG"),
    ("tth", "ttHtoGG")
]

# Function to safely create a directory
def safe_mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
        
        
def submit_jobs(directory):
    sub_files = glob.glob("%s/*.sub"%(directory))
    for current_file in sub_files:
        subprocess.call(["condor_submit", "-spool", current_file])
    
def write_sh(mode, process, mass_era_list):
    variable = mass_era_list[0][2] # Fetch variable
    
    # Make directory to store sub files
    if not os.path.isdir("%s/jobs_%s"%(twd__, variable)): os.system("mkdir %s/jobs_%s"%(twd__, variable))
    
    _jobdir = "%s/jobs_%s"%(twd__, variable)
    _executable = "condor_%s_%s"%(variable, mode)
    _f = open("%s/%s.sh"%(_jobdir,_executable),"w") # single .sh script split into separate jobs
    
    _f.write("#!/bin/bash\n")
    _f.write("ulimit -s unlimited\n")
    _f.write("set -e\n")
    _f.write("cd %s/src\n"%os.environ['CMSSW_BASE'])
    _f.write("export SCRAM_ARCH=%s\n"%os.environ['SCRAM_ARCH'])
    _f.write("source /cvmfs/cms.cern.ch/cmsset_default.sh\n")
    _f.write("eval `scramv1 runtime -sh`\n")
    _f.write("cd %s\n"%twd__)
    _f.write("export PYTHONPATH=$PYTHONPATH:%s/commonTools:%s/T2WSTools\n\n"%(cwd__,twd__))
    
    i = 0
    for mass, era, variable, path_to_root_files in mass_era_list:
        output_dir = "../input_output_{}_2022{}".format(variable, era)
        safe_mkdir(output_dir)  # Create output directory if it doesn't exist
    
        cmd = "python3 {twd}/trees2ws.py --inputMass {mass} --productionMode {mode} --year 2022{era} --doSystematics --doDiffSplitting --inputConfig {twd}/config/config_2022_{variable}.py --inputTreeFile '{path_to_root_files}/{process}_M-{mass}_{era}/'*.root --outputWSDir {output_dir}".format(
            twd=twd__, mass=mass, mode=mode, era=era, variable=variable, path_to_root_files=path_to_root_files, process=process, output_dir=output_dir)
        
        _f.write("if [ $1 -eq %g ]; then\n"%i)
        _f.write(" %s\n"%cmd)
        _f.write("fi\n")
        
        print(cmd)
        
        
        i += 1
        
    # Close .sh file
    _f.close()
    os.system("chmod 775 %s/%s.sh"%(_jobdir,_executable))
    
    
    # Condor submission file
    _fsub = open("%s/%s.sub"%(_jobdir,_executable),"w")
    
    _fsub.write("executable = %s/%s.sh\n"%(_jobdir,_executable))
    _fsub.write("arguments  = $(ProcId)\n")
    _fsub.write("output     = %s/%s.$(ClusterId).$(ProcId).out\n"%(_jobdir,_executable))
    _fsub.write("error      = %s/%s.$(ClusterId).$(ProcId).err\n\n"%(_jobdir,_executable))
    _fsub.write("# Send the job to Held state on failure\n")
    _fsub.write("on_exit_hold = (ExitBySignal == True) || (ExitCode != 0)\n\n")
    _fsub.write("# Periodically retry the jobs every 10 minutes, up to a maximum of 5 retries.\n")
    _fsub.write("periodic_release =  (NumJobStarts < 3) && ((CurrentTime - EnteredCurrentStatus) > 600)\n\n")
    _fsub.write("+JobFlavour = \"longlunch\"\n")
    _fsub.write("queue %g"%i)
    _fsub.close()

# Main function to parallelize tasks
def main(variable, path_to_root_files):
    
    
    mass_era_list = [
        (mass, era, variable, path_to_root_files)
        for era in eras
        for mass in input_masses
    ]
    
    proc_list = [
        (mode, process)
        for mode, process in production_modes
    ]
    
    # Lets benchmark the time:
    start_time = time.time()  

    for mode, process in proc_list:
        write_sh(mode, process, mass_era_list)
        
    # Submitting files to condor
    job_dir = '%s/jobs_%s'%(twd__, variable)
    submit_jobs(job_dir)

    end_time = time.time()  

    # Calculate and print the duration
    duration = end_time - start_time
    print("Process {:.2f} seconds.".format(duration))

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: <script.py> <variable> <path_to_root_files>")
        sys.exit(1)
    
    variable = sys.argv[1]
    path_to_root_files = sys.argv[2]
    main(variable, path_to_root_files)