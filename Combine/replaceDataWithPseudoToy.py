# Script to replace data_obs in workspace with a pseudoToy
import os, sys
import re
from optparse import OptionParser
import ROOT
import glob

def run(cmd):
    print("[>>>]$ %s"%cmd)
    os.system(cmd)

def get_options():
  parser = OptionParser()
  parser.add_option("--inputWSFile", dest="inputWSFile", default=None, help="Input RooWorkspace file. If loading snapshot then use a post-fit workspace where the option --saveWorkspace was set")
  parser.add_option("--loadSnapshot", dest="loadSnapshot", default=None, help="Load best-fit snapshot name")
  parser.add_option('--mass', dest='mass', default='125.38', help="Higgs mass")
  parser.add_option('--seed', dest='seed', default='-1', help="Random seed")
  return parser.parse_args()
(opt,args) = get_options()

# Generate toy from workspace
gen_cmd = f"combine {opt.inputWSFile} -m {opt.mass} -M GenerateOnly -t 1 -s {opt.seed} -n _gen_pseudoToy --saveToys --expectSignal 1"
if opt.loadSnapshot:
    gen_cmd += f" --snapshotName {opt.loadSnapshot}"
run(gen_cmd)

# Replace data_obs in the workspace
# Load workspace
f = ROOT.TFile(opt.inputWSFile)
w = f.Get("w")

# Get data object and delete
data_obs = w.data("data_obs")
data_obs.Delete()
w.RecursiveRemove(data_obs)

# Load toy
ftoy_name = glob.glob(f"higgsCombine_gen_pseudoToy.GenerateOnly.mH{opt.mass}.*.root")[0]
ftoy = ROOT.TFile(ftoy_name)
data_toy = ftoy.Get("toys/toy_1").Clone("data_obs")
# Add toy to workspace with name "data_obs"
w.imp = getattr(w,"import")
w.imp(data_toy)

# Write modified workspace to new file
f_out_name = re.sub("Datacard", "DatacardPseudoToy", opt.inputWSFile)
w.writeToFile(f_out_name)

# Delete toys file
del_cmd = f"rm {ftoy_name}"
run(del_cmd)
