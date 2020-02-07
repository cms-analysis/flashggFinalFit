# Script to convert flashgg trees to RooWorkspace (compatible for finalFits)

print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG TREES 2 WS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
import os, sys
import re
from optparse import OptionParser
import ROOT
import pandas as pd

import uproot
f = uproot.open("output_numEvent10.root")
tree = f["tagsDumper/trees/ggh_125_13TeV_RECO_0J_PTH_GT10_Tag0"]

data = tree.arrays(["THU_ggH_MuDown01sigma","pdfWeights"], outputtype=pd.DataFrame)

# Read pdfWeights, scaleWeights separately and then merge dataframes


