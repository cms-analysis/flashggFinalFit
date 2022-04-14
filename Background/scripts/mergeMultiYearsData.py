#!/usr/bin/env python                                                                                                                                                                                                                    

import sys
import glob
import ROOT
from optparse import OptionParser
from commonTools import *

def get_options():
    parser = OptionParser()
    parser.add_option("-i","--inputdir", dest="idir", default="cards/cards_current", help="Input directory")
    parser.add_option("-o","--outfile", dest="outfile", default="allData.root", help="Outputfile")
    parser.add_option("--years", dest="years", default="2016,2017,2018", help="Merge the datasets of the following years")
    return parser.parse_args()
(opt,args) = get_options()

files = args[:]


#Extract all files to be merged                                                                                                                                                                                                          
fNames = {}
for year in opt.years.split(","): fNames[year] = glob.glob("%s/data_%s/output_Data_13TeV.root"%(opt.idir,year))

cats = extractListOfCats(fNames[opt.years.split(",")[0]]).split(',')

# Define ouput merged workspace
print " --> Merging output workspaces"
mergedWS = ROOT.RooWorkspace("cms_hgg_13TeV","cms_hgg_13TeV")
mergedWS.imp = getattr(mergedWS,"import")

# Extract merged datasets
data_merged = {}
data_merged_names = []
for cat in cats:
    data_merged["Data_13TeV_%s" % cat] = ROOT.TFile(fNames[opt.years.split(",")[0]][0]).Get("tagsDumper/cms_hgg_13TeV").data("Data_13TeV_%s" % cat).emptyClone("Data_13TeV_%s" % cat)
    data_merged_names.append( data_merged["Data_13TeV_%s" % cat].GetName() )

for year, fNames in fNames.iteritems():
    for fName in fNames:
        for cat in cats:
            d = ROOT.TFile(fName).Get("tagsDumper/cms_hgg_13TeV").data("Data_13TeV_%s" % cat)
            print "YEAR = %-6s, CAT = %-30s, n = %d" % (year,cat,d.numEntries())
            for i in range(d.numEntries()):
                p = d.get(i)
                data_merged["Data_13TeV_%s" % cat].add(p)

print " --> Writing to: %s"%(opt.outfile)
f = ROOT.TFile(opt.outfile,"RECREATE")
f.mkdir("tagsDumper")
f.cd("tagsDumper")
for _data in data_merged.itervalues(): mergedWS.imp(_data)
mergedWS.Write()
f.Close()
