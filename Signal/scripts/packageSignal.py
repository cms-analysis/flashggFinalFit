# Script to package individual signal models for a single category in one ROOT file
# Option to merge different extensions (years)

import os, re, sys
import glob
import ROOT
from optparse import OptionParser

def get_options():
  parser = OptionParser()
  parser.add_option("--cat", dest='cat', default='RECO_0J_PTH_0_10_Tag0', help="RECO category to package")
  parser.add_option("--exts", dest='exts', default='', help="Comma separate list of extensions")
  parser.add_option("--outputExt", dest='outputExt', default='packaged', help="Output extension")
  parser.add_option("--massPoints", dest='massPoints', default='120,125,130', help="Comma separated list of mass points")
  parser.add_option("--mergeYears", dest='mergeYears', default=False, action="store_true", help="Merge specified categories across years")
  parser.add_option("--year", dest="year", default="2016", help="If not merging, then specify year for output file name")
  return parser.parse_args()
(opt,args) = get_options()

def rooiter(x):
  iter = x.iterator()
  ret = iter.Next()
  while ret:
    yield ret
    ret = iter.Next()

# Extract all files to be merged
fNames = {}
for ext in opt.exts.split(","): fNames[ext] = glob.glob("outdir_%s/signalFit/output/CMS-HGG_sigfit_%s_*_%s.root"%(ext,ext,opt.cat))

# Define ouput packaged workspace
print " --> Packaging output workspaces"
packagedWS = ROOT.RooWorkspace("wsig_13TeV","wsig_13TeV")
packagedWS.imp = getattr(packagedWS,"import")

# Extract merged datasets
data_merged = {}
data_merged_names = []
for mp in opt.massPoints.split(","): 
  data_merged["m%s"%mp] = ROOT.TFile(fNames[opt.exts.split(",")[0]][0]).Get("wsig_13TeV").data("sig_mass_m%s_%s"%(mp,opt.cat)).emptyClone("sig_mass_m%s_%s"%(mp,opt.cat))
  data_merged_names.append( data_merged["m%s"%mp].GetName() )

for ext, fNames_by_ext in fNames.iteritems():
  for fName in fNames_by_ext:
    for mp in opt.massPoints.split(","):
      d = ROOT.TFile(fName).Get("wsig_13TeV").data("sig_mass_m%s_%s"%(mp,opt.cat))
      for i in range(d.numEntries()):
        p = d.get(i)
        w = d.weight()
        data_merged["m%s"%mp].add(p,w)
  
for _data in data_merged.itervalues(): packagedWS.imp(_data)
        
# Loop over input signal fit workspaces
for ext, fNames_by_ext in fNames.iteritems():
  for fName in fNames_by_ext:
    fin = ROOT.TFile(fName)
    wsin = fin.Get("wsig_13TeV")
    if not wsin: continue
    allVars, allFunctions, allPdfs = {}, {}, {}
    for _var in rooiter(wsin.allVars()): allVars[_var.GetName()] = _var
    for _func in rooiter(wsin.allFunctions()): allFunctions[_func.GetName()] = _func
    for _pdf in rooiter(wsin.allPdfs()): allPdfs[_pdf.GetName()] = _pdf
    allData = wsin.allData()

    # Import objects into output workspace
    for _varName, _var in allVars.iteritems(): packagedWS.imp(_var,ROOT.RooFit.RecycleConflictNodes(),ROOT.RooFit.Silence())
    for _funcName, _func in allFunctions.iteritems(): packagedWS.imp(_func,ROOT.RooFit.RecycleConflictNodes(),ROOT.RooFit.Silence())
    for _pdfName, _pdf in allPdfs.iteritems(): packagedWS.imp(_pdf,ROOT.RooFit.RecycleConflictNodes(),ROOT.RooFit.Silence())

    for _data in allData:
      # Skip merged datasets
      if _data.GetName() in data_merged_names: continue
      else: packagedWS.imp(_data)

# Save to file
if not os.path.isdir("outdir_%s"%opt.outputExt): os.system("mkdir outdir_%s"%opt.outputExt)
if opt.mergeYears:
  print " --> Writing to: ./outdir_%s/CMS-HGG_sigfit_%s_%s.root"%(opt.outputExt,opt.outputExt,opt.cat)
  f = ROOT.TFile("./outdir_%s/CMS-HGG_sigfit_%s_%s.root"%(opt.outputExt,opt.outputExt,opt.cat),"RECREATE")
else:
  print " --> Writing to: ./outdir_%s/CMS-HGG_sigfit_%s_%s_%s.root"%(opt.outputExt,opt.outputExt,opt.cat,opt.year)
  f = ROOT.TFile("./outdir_%s/CMS-HGG_sigfit_%s_%s_%s.root"%(opt.outputExt,opt.outputExt,opt.cat,opt.year),"RECREATE")

packagedWS.Write()
packagedWS.Delete()
f.Delete()
f.Close()
