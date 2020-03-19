import ROOT
from ROOT import *

import sys
import os

inDir = sys.argv[1]
mass = sys.argv[2]
HHWWgg_Label = sys.argv[3]
cats_ = sys.argv[4]


# print'***************************************************'
# print'cats: ',cats
# print'***************************************************'

cats = cats_.split(",") # turn to list 

# exit(1)

#print'in python, mass:',mass
outDir = inDir + '_' + 'interpolation/'
if not os.path.exists(outDir):
    os.makedirs(outDir) 
# outDir += "interpolation/"
#mass = [250] # radion mass 
#masses = []
#masses.append(mass)
#for m in mass:
m = mass

print "Looking at Radion mass = ", m
values = [-5,0,5]
higgs_mass = 125

ws_name = 'tagsDumper/cms_hgg_13TeV'
# dataset_name = 'ggF_' + str(HHWWgg_Label) + '_13TeV_HHWWggTag_0' 
# dataset_name = 'ggF_125_13TeV_SL'
#temp_ws = TFile(inDir+'testWS.root').Get(ws_name)
temp_ws = TFile(inDir+'/'+str(m)+'_HHWWgg_qqlnu.root').Get(ws_name)

# cats = ['0','1'] # HHWWggTag categories 

# temp_ws.Print()
for value in values:
	print'mass shift:',value 
	shift = value + higgs_mass

	output = TFile(outDir + 'X_signal_'+str(m)+'_'+str(shift)+'_HHWWgg_qqlnu.root','RECREATE')
	output.mkdir("tagsDumper")
	output.cd("tagsDumper")
	ws_new = ROOT.RooWorkspace("cms_hgg_13TeV")

	for cat in cats: 
		dataset_name = 'ggF_' + str(HHWWgg_Label) + '_13TeV_' + cat 

		dataset = (temp_ws.data(dataset_name)).Clone(dataset_name + '_' + str(shift)) # includes process and category 
		dataset.Print()
		dataset.changeObservableName('CMS_hgg_mass','CMS_hgg_mass_old')
		higgs_old = dataset.get()['CMS_hgg_mass_old']
		higgs_new = RooFormulaVar( 'CMS_hgg_mass', 'CMS_hgg_mass', "(@0+%.1f)"%value,RooArgList(higgs_old) );
		dataset.addColumn(higgs_new).setRange(105,145)
		dataset.Print()

		getattr(ws_new,'import')(dataset,RooCmdArg())

	ws_new.Write()

	output.Close()
	print'finished mass shift: ',value 
