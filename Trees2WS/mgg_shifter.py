import ROOT
import re
from optparse import OptionParser
import os, sys

parser = OptionParser()
parser.add_option("--inputFile", dest="inputFile", default="/vols/cms/es811/FinalFits/ws_ReweighAndNewggHweights/output_GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8_GG2H.root", help="Input file")
parser.add_option("--inputMass", dest="inputMass", default=125, type='int', help="Input mass")
parser.add_option("--targetMass", dest="targetMass", default=130, type='int', help="Target mass")
parser.add_option("--verbose", dest="verbose", default=0, type='int', help="Verbose output")
(opt,args) = parser.parse_args()

verbose = opt.verbose

def rooiter(x):
  iter = x.iterator()
  ret = iter.Next()
  while ret:
    yield ret
    ret = iter.Next()

if not os.path.exists( opt.inputFile ): 
  print " --> [ERROR] input file %s does not exist. Leaving..."%(opt.inputFile)
  sys.exit(1)

if str(opt.inputMass) not in opt.inputFile: 
  print " --> [ERROR] input file %s does not correspond to input mass (%s). Leaving..."%(opt.inputFile,str(opt.inputMass))

# Calculate shift
shift = float(opt.inputMass-opt.targetMass)
  
# Extract input file and workspace
f = ROOT.TFile( opt.inputFile )
ws = f.Get("tagsDumper/cms_hgg_13TeV")

# Define output workspace + workaround for importing in pyroot
wsout = ROOT.RooWorkspace("cms_hgg_13TeV","cms_hgg_13TeV")
wsout.imp = getattr(wsout,"import")

# Import all vars from original ws
allVars = {}
for _var in rooiter(ws.allVars()): allVars[_var.GetName()] = _var
for _varName, _var in allVars.iteritems():  
  wsout.imp(_var, ROOT.RooFit.RecycleConflictNodes(), ROOT.RooFit.Silence() )

#allFunctions = {}
#for _func in rooiter(ws.allFunctions()): allFunctions[_func.GetName()] = _func
#for _funcName, _func in allFunctions.iteritems(): 
#  wsout.imp(_func, ROOT.RooFit.RecycleConflictNodes(), ROOT.RooFit.Silence() )
#allPdfs = {}
#for _pdf in rooiter(ws.allPdfs()): allPdfs[_pdf.GetName()] = _pdf
#for _pdf in allPdfs.itervalues(): 
#  wsout.imp(_pdf, ROOT.RooFit.RecycleConflictNodes(), ROOT.RooFit.Silence() )

# Extract datasets from original workspace
allData = ws.allData()

# Loop over datasets and define new shifted datasets
shifted_datasets = {}
weight = ROOT.RooRealVar("weight","weight",-100000,1000000)
m = ROOT.RooRealVar("CMS_hgg_mass","m",100,180)

for d_orig in allData:

  # Extract names of original an shifted datasets
  n_orig = d_orig.GetName()
  if "RECO" in n_orig:
    n_orig_split = n_orig.split("RECO")
    n_shift_split_0 = re.sub(str(opt.inputMass),str(opt.targetMass),n_orig_split[0])
    n_shift = n_shift_split_0 + "RECO" + n_orig_split[-1]
  else: n_shift = re.sub(str(opt.inputMass),str(opt.targetMass),n_orig)
  if verbose: print "%s --> %s"%(n_orig,n_shift)

  # Create an empty clone of original dataset
  #shifted_datasets[n_shift] = d_shift = d_orig.emptyClone( n_shift )
  shifted_datasets[n_shift] = d_orig.emptyClone( n_shift )

  # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # For RooDataHist
  if d_orig.ClassName() == 'RooDataHist':
    for i in range(d_orig.numEntries()):
      
      #Clone bin and extract weight
      p = d_orig.get(i).Clone()
      weight.setVal(d_orig.weight())

      # Extract centre of bin
      binCentre = p.getRealValue("CMS_hgg_mass")

      # If binCentre +- shift is outside allowed range then skip
      if( (binCentre-shift) < m.getMin() )|( (binCentre-shift) > m.getMax() ): continue
      else:
        # Shift binCentre and set new value
        p.setRealValue("CMS_hgg_mass", (d_orig.get(i).getRealValue("CMS_hgg_mass")-shift) )
        # Add to shifted datahist
        #shifted_datasets[n_shift].add(p,weight.getVal())
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

        value = p.getRealValue("CMS_hgg_mass")

        # If value - shift is outside allowed range then skip
        if( (value-shift) < m.getMin() )|( (value-shift) > m.getMax() ): continue
        else:
          # Set ot new shifted value
          p.setRealValue("CMS_hgg_mass", (d_orig.get(i).getRealValue("CMS_hgg_mass")-shift) )
          # Add to shifted dataset
          shifted_datasets[n_shift].add(p,weight.getVal())
    
      # For pdfWeights: keep same points
      else: shifted_datasets[n_shift].add(p,weight.getVal())

# Import all shifted datasets to output ws
for d_shift in shifted_datasets.itervalues(): wsout.imp( d_shift, ROOT.RooFit.RecycleConflictNodes() )

# Configure output file and write output ws
fout_name = re.sub("M%s"%str(opt.inputMass),"M%s"%str(opt.targetMass), opt.inputFile)
fout = ROOT.TFile.Open(fout_name, "RECREATE")
dir_ws = fout.mkdir("tagsDumper")
dir_ws.cd()
wsout.Write()

