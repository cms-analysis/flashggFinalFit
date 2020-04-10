# Script to package individual signal models for a single category in one ROOT file
import os, re, sys
import glob
import ROOT
from optparse import OptionParser

mergedYear_cats = ['RECO_0J_PTH_0_10_Tag0', 'RECO_0J_PTH_0_10_Tag1', 'RECO_0J_PTH_0_10_Tag2', 'RECO_0J_PTH_GT10_Tag0', 'RECO_0J_PTH_GT10_Tag1', 'RECO_0J_PTH_GT10_Tag2', 'RECO_1J_PTH_0_60_Tag0', 'RECO_1J_PTH_0_60_Tag1', 'RECO_1J_PTH_0_60_Tag2', 'RECO_1J_PTH_120_200_Tag0', 'RECO_1J_PTH_120_200_Tag1', 'RECO_1J_PTH_120_200_Tag2', 'RECO_1J_PTH_60_120_Tag0', 'RECO_1J_PTH_60_120_Tag1', 'RECO_1J_PTH_60_120_Tag2', 'RECO_GE2J_PTH_0_60_Tag0', 'RECO_GE2J_PTH_0_60_Tag1', 'RECO_GE2J_PTH_0_60_Tag2', 'RECO_GE2J_PTH_120_200_Tag0', 'RECO_GE2J_PTH_120_200_Tag1', 'RECO_GE2J_PTH_120_200_Tag2', 'RECO_GE2J_PTH_60_120_Tag0', 'RECO_GE2J_PTH_60_120_Tag1', 'RECO_GE2J_PTH_60_120_Tag2', 'RECO_PTH_200_300_Tag0', 'RECO_PTH_200_300_Tag1', 'RECO_PTH_300_450_Tag0', 'RECO_PTH_300_450_Tag1', 'RECO_PTH_450_650_Tag0', 'RECO_PTH_GT650_Tag0', 'RECO_THQ_LEP', 'RECO_TTH_HAD_PTH_0_60_Tag0', 'RECO_TTH_HAD_PTH_0_60_Tag1', 'RECO_TTH_HAD_PTH_0_60_Tag2', 'RECO_TTH_HAD_PTH_0_60_Tag3', 'RECO_TTH_HAD_PTH_120_200_Tag0', 'RECO_TTH_HAD_PTH_120_200_Tag1', 'RECO_TTH_HAD_PTH_120_200_Tag2', 'RECO_TTH_HAD_PTH_120_200_Tag3', 'RECO_TTH_HAD_PTH_60_120_Tag0', 'RECO_TTH_HAD_PTH_60_120_Tag1', 'RECO_TTH_HAD_PTH_60_120_Tag2', 'RECO_TTH_HAD_PTH_60_120_Tag3', 'RECO_TTH_HAD_PTH_GT200_Tag0', 'RECO_TTH_HAD_PTH_GT200_Tag1', 'RECO_TTH_HAD_PTH_GT200_Tag2', 'RECO_TTH_HAD_PTH_GT200_Tag3', 'RECO_TTH_LEP_PTH_0_60_Tag0', 'RECO_TTH_LEP_PTH_0_60_Tag1', 'RECO_TTH_LEP_PTH_0_60_Tag2', 'RECO_TTH_LEP_PTH_0_60_Tag3', 'RECO_TTH_LEP_PTH_120_200_Tag0', 'RECO_TTH_LEP_PTH_120_200_Tag1', 'RECO_TTH_LEP_PTH_60_120_Tag0', 'RECO_TTH_LEP_PTH_60_120_Tag1', 'RECO_TTH_LEP_PTH_GT200_Tag0', 'RECO_TTH_LEP_PTH_GT200_Tag1', 'RECO_VBFLIKEGGH_Tag0', 'RECO_VBFLIKEGGH_Tag1', 'RECO_VBFTOPO_BSM_Tag0', 'RECO_VBFTOPO_BSM_Tag1', 'RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag0', 'RECO_VBFTOPO_JET3VETO_HIGHMJJ_Tag1', 'RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag0', 'RECO_VBFTOPO_JET3VETO_LOWMJJ_Tag1', 'RECO_VBFTOPO_JET3_HIGHMJJ_Tag0', 'RECO_VBFTOPO_JET3_HIGHMJJ_Tag1', 'RECO_VBFTOPO_JET3_LOWMJJ_Tag0', 'RECO_VBFTOPO_JET3_LOWMJJ_Tag1', 'RECO_VBFTOPO_VHHAD_Tag0', 'RECO_VBFTOPO_VHHAD_Tag1', 'RECO_VH_MET_Tag0', 'RECO_VH_MET_Tag1', 'RECO_WH_LEP_HIGH_Tag0', 'RECO_WH_LEP_HIGH_Tag1', 'RECO_WH_LEP_HIGH_Tag2', 'RECO_WH_LEP_LOW_Tag0', 'RECO_WH_LEP_LOW_Tag1', 'RECO_WH_LEP_LOW_Tag2', 'RECO_ZH_LEP_Tag0', 'RECO_ZH_LEP_Tag1']

def get_options():
  parser = OptionParser() 
  parser.add_option("--cat", dest='cat', default='RECO_0J_PTH_0_10_Tag0', help="RECO category to package")
  parser.add_option("--ext", dest='ext', default='', help="Extension (minus year tag)")
  parser.add_option("--massPoints", dest='massPoints', default='120,125,130', help="Comma separated list of mass points")
  parser.add_option("--mergeYears", dest='mergeYears', default=False, action="store_true", help="Merge specified categories across years")
  parser.add_option("--years", dest="years", default="2016,2017,2018", help="Years to process")
  return parser.parse_args()
(opt,args) = get_options()

def rooiter(x):
  iter = x.iterator()
  ret = iter.Next()
  while ret:
    yield ret
    ret = iter.Next()

if opt.mergeYears: 
  if opt.cat in mergedYear_cats: 
    print " --> Will merge cat (%s) across years"%opt.cat
    if opt.years != '2016,2017,2018': print " --> [WARNING] You are merging a category but only using the following years: %s"%opt.years

# Extract all files corresponding to cat:
fNames = {}
for year in opt.years.split(","): fNames[year] = glob.glob("outdir_%s_%s/CMS-HGG_sigfit_%s_%s_*_%s.root"%(opt.ext,year,opt.ext,year,opt.cat))

if(opt.mergeYears)&(opt.cat in mergedYear_cats): 
  print " --> Packaging output workspaces: merged"
  packagedWS = ROOT.RooWorkspace("wsig_13TeV","wsig_13TeV")
  packagedWS.imp = getattr(packagedWS,"import")
  # Define ouput packaged workspace
  data_merged = {}
  for mp in opt.massPoints.split(","): data_merged["m%s"%mp] = ROOT.TFile(fNames[opt.years.split(",")[0]][0]).Get("wsig_13TeV").data("sig_mass_m%s_%s"%(mp,opt.cat)).emptyClone("sig_mass_m%s_%s"%(mp,opt.cat))

  # Loop over input signal fit workspaces
  for year, fNames_by_year in fNames.iteritems():
    for fName in fNames_by_year:
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
	# If data has no process name in then add points to merged ws, else import straight to output WS
	if _data.GetName().count("sig_mass"): 
	  # Extract mass point
	  mp = _data.GetName().split("mass_m")[-1].split("_RECO")[0]
	  for i in range(_data.numEntries()):
	    p = _data.get(i)
	    w = _data.weight()
	    data_merged["m%s"%mp].add(p,w)
	else: packagedWS.imp(_data)

  # Add merged datasets
  for _data in data_merged.itervalues(): packagedWS.imp(_data)

  # Save to file
  if not os.path.isdir("outdir_%s"%opt.ext): os.system("mkdir outdir_%s"%opt.ext)
  print " --> Writing to: ./outdir_%s/CMS-HGG_sigfit_%s_%s.root"%(opt.ext,opt.ext,opt.cat)
  f = ROOT.TFile("./outdir_%s/CMS-HGG_sigfit_%s_%s.root"%(opt.ext,opt.ext,opt.cat),"RECREATE")
  packagedWS.Write()
  packagedWS.Delete()
  f.Delete()
  f.Close()

else:
  for year in opt.years.split(","): 

    print " --> Packaging output workspaces: %s"%year
    # Define ouput packaged workspace
    packagedWS = ROOT.RooWorkspace("wsig_13TeV","wsig_13TeV")
    packagedWS.imp = getattr(packagedWS,"import")

    # Merged datasets for category
    data_merged = {}
    for mp in opt.massPoints.split(","): data_merged["m%s"%mp] = ROOT.TFile(fNames[year][0]).Get("wsig_13TeV").data("sig_mass_m%s_%s"%(mp,opt.cat)).emptyClone("sig_mass_m%s_%s_%s"%(mp,opt.cat,year))

    # Loop over input signal fit workspaces for specific year and extract objects
    for fName in fNames[year]:
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
	# If data has no process name in then add points to merged ws, else import straight to output WS
	if _data.GetName().count("sig_mass"): 
	  # Extract mass point
	  mp = _data.GetName().split("mass_m")[-1].split("_RECO")[0]
	  for i in range(_data.numEntries()):
	    p = _data.get(i)
	    w = _data.weight()
	    data_merged["m%s"%mp].add(p,w)
	else: packagedWS.imp(_data)

    # Add merged datasets
    for _data in data_merged.itervalues(): packagedWS.imp(_data)


    # Save to file
    print " --> Writing to: ./outdir_%s_%s/CMS-HGG_sigfit_%s_%s_%s.root"%(opt.ext,year,opt.ext,opt.cat,year)
    f = ROOT.TFile("./outdir_%s_%s/CMS-HGG_sigfit_%s_%s_%s.root"%(opt.ext,year,opt.ext,opt.cat,year),"RECREATE")
    packagedWS.Write()
    packagedWS.Delete()
    f.Delete()
    f.Close()
