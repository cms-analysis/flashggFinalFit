import ROOT
import re
from optparse import OptionParser
import os, sys

from commonTools import *
from commonObjects import *

parser = OptionParser()
parser.add_option("--inputWSFile", dest="inputWSFile", default="/vols/cms/es811/FinalFits/ws_ReweighAndNewggHweights/output_GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8_GG2H.root", help="Input file")
parser.add_option("--inputMass", dest="inputMass", default=125, type='int', help="Input mass")
parser.add_option("--xvar", dest="xvar", default="CMS_hgg_mass:100:180", help="Input mass variable (name:xmin:xmax)")
parser.add_option("--targetMass", dest="targetMass", default=130, type='int', help="Target mass")
parser.add_option("--verbose", dest="verbose", default=0, type='int', help="Verbose output")
(opt,args) = parser.parse_args()

verbose = opt.verbose
xvar = opt.xvar

if not os.path.exists( opt.inputWSFile ): 
  print " --> [ERROR] input file %s does not exist. Leaving..."%(opt.inputWSFile)
  sys.exit(1)

if str(opt.inputMass) not in opt.inputWSFile: 
  print " --> [ERROR] input file %s does not correspond to input mass (%s). Leaving..."%(opt.inputWSFile,str(opt.inputMass))

# Calculate shift
shift = float(opt.inputMass-opt.targetMass)
  
# Extract input file and workspace
f = ROOT.TFile( opt.inputWSFile )
ws = f.Get( inputWSName__ )

# Define output workspace + workaround for importing in pyroot
wsout = ROOT.RooWorkspace(inputWSName__.split("/")[-1],inputWSName__.split("/")[-1])
wsout.imp = getattr(wsout,"import")

# Import all vars from original ws
allVars = {}
for _var in rooiter(ws.allVars()): allVars[_var.GetName()] = _var
for _varName, _var in allVars.iteritems():  
  wsout.imp(_var, ROOT.RooFit.RecycleConflictNodes(), ROOT.RooFit.Silence() )

# Extract datasets from original workspace
allData = ws.allData()

# Loop over datasets and define new shifted datasets
shifted_datasets = {}
weight = ROOT.RooRealVar("weight","weight",-100000,1000000)
m = ROOT.RooRealVar(xvar.split(":")[0],xvar.split(":")[0],int(xvar.split(":")[1]),int(xvar.split(":")[2]))

for d_orig in allData:

  # Extract names of original an shifted datasets: of the form {prod}_{mass}_{sqrts}_{cat}
  n_orig = d_orig.GetName()

  n_components = n_orig.split("_%s_"%sqrts__)  
  n_shift = re.sub(str(opt.inputMass),str(opt.targetMass),n_components[0])+"_%s_"%sqrts__+n_components[-1]
  if verbose: print "%s --> %s"%(n_orig,n_shift)

  # Create an empty clone of original dataset
  shifted_datasets[n_shift] = d_orig.emptyClone( n_shift )

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # For RooDataHist
  if d_orig.ClassName() == 'RooDataHist':
    for i in range(d_orig.numEntries()):
      
      #Clone bin and extract weight
      p = d_orig.get(i).Clone()
      weight.setVal(d_orig.weight())

      # Extract centre of bin
      binCentre = p.getRealValue(xvar.split(":")[0])

      # If binCentre +- shift is outside allowed range then skip
      if( (binCentre-shift) < m.getMin() )|( (binCentre-shift) > m.getMax() ): continue
      else:
        # Shift binCentre and set new value
        p.setRealValue(xvar.split(":")[0], (d_orig.get(i).getRealValue(xvar.split(":")[0])-shift) )
        # Add to shifted datahist
        shifted_datasets[n_shift].add(p,weight.getVal())

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # For RooDataSet
  else:
    # Loop over entries in original dataset
    for i in range(d_orig.numEntries()):

      # Clone datapoint, with same weight
      p = d_orig.get(i).Clone()
      weight.setVal(d_orig.weight())

      # If data point contains Higgs mass then shift
      if p.contains(m):

        value = p.getRealValue(xvar.split(":")[0])

        # If value - shift is outside allowed range then skip
        if( (value-shift) < m.getMin() )|( (value-shift) > m.getMax() ): continue
        else:
          # Set ot new shifted value
          p.setRealValue(xvar.split(":")[0], (d_orig.get(i).getRealValue(xvar.split(":")[0])-shift) )
          # Add to shifted dataset
          shifted_datasets[n_shift].add(p,weight.getVal())
    
      # For pdfWeights: keep same points
      else: shifted_datasets[n_shift].add(p,weight.getVal())

# Import all shifted datasets to output ws
for d_shift in shifted_datasets.itervalues(): wsout.imp( d_shift, ROOT.RooFit.RecycleConflictNodes() )

# Configure output file and write output ws
fout_name = re.sub("M%s"%str(opt.inputMass),"M%s"%str(opt.targetMass), opt.inputWSFile)
fout = ROOT.TFile.Open(fout_name, "RECREATE")
dir_ws = fout.mkdir(inputWSName__.split("/")[0])
dir_ws.cd()
wsout.Write()

