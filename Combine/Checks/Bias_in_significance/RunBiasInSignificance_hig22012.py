import ROOT
import os
import glob
import re
from optparse import OptionParser
import subprocess
import json

def rooiter(x):
  iter = x.iterator()
  ret = iter.Next()
  while ret:
    yield ret
    ret = iter.Next()

def write_preamble(_file):
    _file.write("#!/bin/bash\n")
    _file.write("ulimit -s unlimited\n")
    _file.write("set -e\n")
    _file.write("cd %s/src\n"%os.environ['CMSSW_BASE'])
    _file.write("export SCRAM_ARCH=%s\n"%os.environ['SCRAM_ARCH'])
    _file.write("source /cvmfs/cms.cern.ch/cmsset_default.sh\n")
    _file.write("eval `scramv1 runtime -sh`\n")
    _file.write("cd %s\n"%os.environ['PWD'])

def get_options():
    parser = OptionParser()
    parser.add_option('--MH', dest='MH', default='125.38', help="MH")
    parser.add_option('--initial-fit-param', dest='initial_fit_param', default='lumi_13TeV_2016', help="Initial fit parameters")
    parser.add_option('--nToys', dest='nToys', default=2000, type='int', help="Number of toys")
    parser.add_option('--nJobs', dest='nJobs', default=10, type='int', help="Number of jobs")
    parser.add_option('--mode', dest='mode', default="setup", help="[setup,generate,fixed,envelope,hadd]")
    return parser.parse_args()
(opt,args) = get_options()

if opt.mode == "setup":

    os.system("cp %s/Combine/Datacard/Datacard_ggtt_resonant_mx%smy%s.txt %s"%(opt.inputDir,opt.MX,opt.MY,run_dir))

    if not os.path.isdir("Models%s"%ext_str):
        os.system("cp -rp %s/Combine/Models ./Models%s"%(opt.inputDir,ext_str))

    # Make stat only datacard and delete pdf indices
    with open("%s/Datacard_ggtt_resonant_mx%smy%s.txt"%(run_dir,opt.MX,opt.MY), "r") as f:
        lines = f.readlines()

    new_lines_all = []
    for line in lines:
        line = re.sub("\./Models", "%s/Models%s"%(os.environ['PWD'],ext_str), line)
        new_lines_all.append(line)
    with open("%s/Datacard.txt"%run_dir, "w") as f:
        for line in new_lines_all:
           f.write(line)

    cmd = "cd %s; text2workspace.py Datacard.txt -m %s higgsMassRange=65,150; cd .."%(run_dir,opt.MH)
    print(cmd)
    os.system(cmd)

    # Get list of pdfindeices
    f = ROOT.TFile("%s/Datacard.root"%run_dir)
    w = f.Get("w")
    cats = w.allCats()
    pdf_index = []
    for cat in rooiter(cats):
        if "pdfindex" in cat.GetName(): pdf_index.append(cat.GetName()) 
    f.Close()
   
    # Initial fit fixing params to be zero
    cmd = "cd %s; combine -m %s -d Datacard.root -M MultiDimFit --cminDefaultMinimizerStrategy 0 --setParameters MH=%s,MY=%s,MX=%s,r=0 --freezeParameters MH,MX,MY,r -P %s -n _initial --setParameterRanges r=0,0.5 --saveWorkspace --saveSpecifiedIndex %s --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2; cd .."%(run_dir,opt.MH,opt.MH,opt.MY,opt.MX,opt.initial_fit_param,",".join(pdf_index))
    print(cmd)
    os.system(cmd)

    # Save best fit pdf indices to json file
    f_res = ROOT.TFile("%s/higgsCombine_initial.MultiDimFit.mH%s.root"%(run_dir,opt.MH))
    t = f_res.Get("limit")
    t.GetEntry(0)
    pdf_index_bf = {}
    for index in pdf_index: pdf_index_bf[index] = getattr(t,index)
    f_res.Close()
    with open("%s/pdfindex.json"%run_dir,"w") as jf:
        json.dump(pdf_index_bf, jf)

if opt.mode == "generate":

    if not os.path.isdir("toys"):
        os.system("mkdir -p toys")

    if not os.path.isdir("jobs_toys"):
        os.system("mkdir -p jobs_toys")
    else:
        # Remove previous jobs
        os.system("rm jobs_toys/sub*")

    for i_job in range( opt.nJobs ):
        f_sub_name = "jobs_toys/sub_%g.sh"%(i_job)
        f_sub = open(f_sub_name, "w")
        write_preamble(f_sub)
        f_sub.write("combine -m %s -d higgsCombine_initial.MultiDimFit.mH%s.root -M GenerateOnly --setParameters MH=%s --freezeParameters MH --expectSignal 0 -n _toy_%g_ --saveToys --snapshotName MultiDimFit -t %s -s -1\n\n"%(opt.MH,opt.MH,opt.MH,i_job,opt.nToys))
        # Move toy to toys folder
        f_sub.write("mv higgsCombine_toy_%g_* toys/toy_%g.root"%(i_job,i_job))
        f_sub.close()

        os.system("chmod 775 %s"%f_sub_name)

        f_out_name = "%s/%s"%(os.environ['PWD'],re.sub("\.sh",".out",f_sub_name))
        f_err_name = "%s/%s"%(os.environ['PWD'],re.sub("\.sh",".err",f_sub_name))
        cmd = "qsub -q hep.q -l h_rt=1:0:0 -o %s -e %s %s"%(f_out_name,f_err_name,f_sub_name)
        print(cmd)
        os.system(cmd)

if opt.mode == "fixed":

    if not os.path.isdir("fits_fixed"):
        os.system("mkdir -p fits_fixed")

    if not os.path.isdir("jobs_fits_fixed"):
        os.system("mkdir -p jobs_fits_fixed")
    else:
        # Remove previous jobs
        os.system("rm jobs_fits_fixed/sub*")

    # Get pdf index and the best fit values
    with open("pdfindex.json", "r") as jf:
        pdf_index_bf = json.load(jf)
 
    pdf_index_save = ",".join(list(pdf_index_bf.keys()))
    pdf_index_freeze = ",".join(list(pdf_index_bf.keys()))
    pdf_index_set = ""
    for k,v in list(pdf_index_bf.items()): pdf_index_set += "%s=%s,"%(k,v)
    pdf_index_set = pdf_index_set[:-1]

    for i_job in range( opt.nJobs ):
        f_sub_name = "jobs_fits_fixed/sub_%g.sh"%(i_job)
        f_sub = open(f_sub_name, "w")
        write_preamble(f_sub)
        f_sub.write("combine -m %s -d higgsCombine_initial.MultiDimFit.mH%s.root -M Significance --snapshotName MultiDimFit --cminDefaultMinimizerStrategy 0 --setParameters MH=%s,%s --expectSignal 0 --freezeParameters MH,%s --trackCats %s -n _fixed_%g_ -t %s --setParameterRanges r=0,50 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 --toysFile toys/toy_%g.root --X-rtd ADDNLL_RECURSIVE=1\n\n"%(opt.MH,opt.MH,opt.MH,pdf_index_set,pdf_index_freeze,pdf_index_save,i_job,opt.nToys,i_job))
        # Move toy to toys folder
        f_sub.write("mv higgsCombine_fixed_%g_* fits_fixed/fit_fixed_%g.root"%(i_job,i_job))
        f_sub.close()

        os.system("chmod 775 %s"%f_sub_name)

        f_out_name = "%s/%s"%(os.environ['PWD'],re.sub("\.sh",".out",f_sub_name))
        f_err_name = "%s/%s"%(os.environ['PWD'],re.sub("\.sh",".err",f_sub_name))
        cmd = "qsub -q hep.q -l h_rt=2:0:0 -o %s -e %s %s"%(f_out_name,f_err_name,f_sub_name)
        print(cmd)
        os.system(cmd)

if opt.mode == "envelope":

    if not os.path.isdir("fits_envelope"):
        os.system("mkdir -p fits_envelope")

    if not os.path.isdir("jobs_fits_envelope"):
        os.system("mkdir -p jobs_fits_envelope")
    else:
        # Remove previous jobs
        os.system("rm jobs_fits_envelope/sub*")

    # Get pdf index and the best fit values
    with open("pdfindex.json", "r") as jf:
        pdf_index_bf = json.load(jf)
 
    pdf_index_save = ",".join(list(pdf_index_bf.keys()))

    for i_job in range( opt.nJobs ):
        f_sub_name = "jobs_fits_envelope/sub_%g.sh"%(i_job)
        f_sub = open(f_sub_name, "w")
        write_preamble(f_sub)
        f_sub.write("combine -m %s -d higgsCombine_initial.MultiDimFit.mH%s.root -M Significance --snapshotName MultiDimFit --cminDefaultMinimizerStrategy 0 --setParameters MH=%s --expectSignal 0 --freezeParameters MH --trackCats %s -n _envelope_%g_ -t %s --setParameterRanges r=0,50 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 --toysFile toys/toy_%g.root --X-rtd ADDNLL_RECURSIVE=1\n\n"%(opt.MH,opt.MH,opt.MH,pdf_index_save,i_job,opt.nToys,i_job))
        # Move toy to toys folder
        f_sub.write("mv higgsCombine_envelope_%g_* fits_envelope/fit_envelope_%g.root"%(i_job,i_job))
        f_sub.close()

        os.system("chmod 775 %s"%f_sub_name)

        f_out_name = "%s/%s"%(os.environ['PWD'],re.sub("\.sh",".out",f_sub_name))
        f_err_name = "%s/%s"%(os.environ['PWD'],re.sub("\.sh",".err",f_sub_name))
        cmd = "qsub -q hep.q -l h_rt=2:0:0 -o %s -e %s %s"%(f_out_name,f_err_name,f_sub_name)
        print(cmd)
        os.system(cmd)



if opt.mode == "hadd":

    cmd = "hadd -f fit_fixed.root fits_fixed/fit_fixed_*.root"
    print(cmd)
    os.system(cmd)

    cmd = "hadd -f fit_envelope.root fits_envelope/fit_envelope_*.root"
    print(cmd)
    os.system(cmd)
