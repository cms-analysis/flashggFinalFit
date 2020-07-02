####################################################################################################################################
# Abe Tishelman-Charny 
#
# The purpose of this python module is to artificially shift the HHWWgg CMS_hgg_mass distribution left and right 5 GeV
# in order to be compatabile with the fggfinalfit framework, as the standard Hgg analysis
# uses an interpolation technique with Hgg mass points ~ 110->130 GeV  
#
# We only have a 125 GeV Higgs mass point for HHWWgg, so we must do this artifial shift.
#
####################################################################################################################################

import ROOT
from ROOT import *

import sys
import os

inDir = sys.argv[1]
ID = sys.argv[2]
HHWWgg_Label = sys.argv[3]
cats_ = sys.argv[4]
analysis_type = sys.argv[5] # Res, EFT, NMSSM 
proc = sys.argv[6]
finalState = sys.argv[7] # qqlnu, lnulnu, qqqq 

cats = cats_.split(",") # turn to list 

outDir = inDir + '_' + 'interpolation/'
if not os.path.exists(outDir):
    os.makedirs(outDir) 
print "Looking at HHWWgg ID:", ID
values = [-5,0,5]
higgs_mass = 125

ws_name = 'tagsDumper/cms_hgg_13TeV'

temp_ws = TFile("%s/%s_HHWWgg_%s.root"%(inDir,str(ID),finalState)).Get(ws_name)

# Res: ID_HHWWgg_<finalState>.root 
# EFT: nodeX_HHWWgg_<finalState>.root
# NMSSM: MX<xmass>_MY<ymass>_HHWWgg_<finalState>.root 

for value in values:
	print'mass shift:',value 
	shift = value + higgs_mass

	# output = TFile(outDir + 'X_signal_'+str(ID)+'_'+str(shift)+'_HHWWgg_qqlnu.root','RECREATE')

	output = TFile("%s/X_signal_%s_%s_HHWWgg_%s.root"%(outDir,str(ID),str(shift),finalState),'RECREATE')
	output.mkdir("tagsDumper")
	output.cd("tagsDumper")
	ws_new = ROOT.RooWorkspace("cms_hgg_13TeV")

	for cat in cats: 
		if(analysis_type == "NMSSM"): dataset_name = str(HHWWgg_Label) + '_13TeV_' + cat
		else: dataset_name = str(proc) + '_' + str(HHWWgg_Label) + '_13TeV_' + cat

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
