#!/usr/bin/env python
import os
import numpy
import sys

from optparse import OptionParser
from optparse import OptionGroup
import ROOT as r

parser = OptionParser()
parser.add_option("--makeTable",default=False,action="store_true",help="Make the table instead of submitting jobs")
parser.add_option("--dryRun",default=False,action="store_true",help="Do not submit jobs")
(opts,args) = parser.parse_args()

def getUpDownUncertainties(directory,nuisance_group,POI):
    tf = r.TFile('%s/higgsCombine%s.MultiDimFit.mH125.root'%(directory,nuisance_group))
    tree = tf.Get('limit')
    centralValue=-1
    loValue=-1
    hiValue=-1
    print "nuisance group is %s" %nuisance_group
    for i in range(tree.GetEntries()):
      tree.GetEntry(i)
      quantile =  getattr(tree,'quantileExpected')
      poival =    getattr(tree,POI)
      if (quantile ==-1) : centralValue=poival
    for i in range(tree.GetEntries()):
      tree.GetEntry(i)
      quantile =  getattr(tree,'quantileExpected')
      poival =    getattr(tree,POI)
      if (poival==-1) : continue
      if (poival >= centralValue) : hiValue=poival
      if (poival <= centralValue) : loValue=poival
    tf.Close()
    up= hiValue - centralValue
    down = loValue - centralValue
    symm = (up-down)/2
    return up,down, symm

def writeJobFileAndSubmit(directory,nuisance_group,POI="r"):
    filename = '%s/sub_job.%s.sh'%(directory,nuisance_group)
    sub_file = open(filename,'w')
    sub_file.write('#!/bin/bash\n')
    sub_file.write('ulimit -s unlimited\n')
    sub_file.write('cd %s\n'%directory)
    sub_file.write('export SCRAM_ARCH=slc6_amd64_gcc491\n')
    sub_file.write('eval `scramv1 runtime -sh`\n')
    sub_file.write('cd %s\n'%directory)
    #sub_file.write('touch %s/sub_job.%s.sh.run\n'%(directory,nuisance_group))
    freezeNuisancesCommand=""
    if "all" in nuisance_group: freezeNuisancesCommand="--freezeNuisances all"
    elif not "none" in nuisance_group: freezeNuisancesCommand=" --freezeNuisanceGroups=%s"%nuisance_group
    if (POI=="r") : sub_file.write('eval combine  CMS-HGG_mva_13TeV_datacard.root -M MultiDimFit --robustFit 1 -t -1 --expectSignal 1 -m125 --setPhysicsModelParameters pdfindex_UntaggedTag_0_13TeV=1,pdfindex_UntaggedTag_1_13TeV=3,pdfindex_UntaggedTag_2_13TeV=2,pdfindex_UntaggedTag_3_13TeV=1,pdfindex_VBFTag_0_13TeV=2,pdfindex_VBFTag_1_13TeV=1,pdfindex_VBFTag_2_13TeV=4,pdfindex_TTHHadronicTag_13TeV=0,pdfindex_TTHLeptonicTag_13TeV=1,pdfindex_ZHLeptonicTag_13TeV=0,pdfindex_WHLeptonicTag_13TeV=1,pdfindex_VHLeptonicLooseTag_13TeV=2,pdfindex_VHHadronicTag_13TeV=1,pdfindex_VHMetTag_13TeV=0 --algo singles --cl=0.68 --minimizerAlgoForMinos Minuit2,Migrad -n %s %s\n'%(nuisance_group,freezeNuisancesCommand))
    else         :  sub_file.write('eval combine  CMS-HGG_mva_13TeV_datacard.perProc.root -M MultiDimFit --robustFit 1 -t -1 --redefineSignalPOIs %s -P %s --floatOtherPOIs 1 --expectSignal 1 -m125 --setPhysicsModelParameterRanges r_ggH=0.00,2.00:r_qqH=0.00,2.00:r_ttH=0.00,2.00:r_VH=-1.00,3.00 --setPhysicsModelParameters pdfindex_UntaggedTag_0_13TeV=1,pdfindex_UntaggedTag_1_13TeV=3,pdfindex_UntaggedTag_2_13TeV=2,pdfindex_UntaggedTag_3_13TeV=1,pdfindex_VBFTag_0_13TeV=2,pdfindex_VBFTag_1_13TeV=1,pdfindex_VBFTag_2_13TeV=4,pdfindex_TTHHadronicTag_13TeV=0,pdfindex_TTHLeptonicTag_13TeV=1,pdfindex_ZHLeptonicTag_13TeV=0,pdfindex_WHLeptonicTag_13TeV=1,pdfindex_VHLeptonicLooseTag_13TeV=2,pdfindex_VHHadronicTag_13TeV=1,pdfindex_VHMetTag_13TeV=0 --algo singles --cl=0.68 --minimizerAlgoForMinos Minuit2,Migrad -n %s %s\n'%(POI,POI,nuisance_group,freezeNuisancesCommand))
    sub_file.close()
    os.system(' chmod +x %s'%(filename))
    exec_line='qsub %s -l h_rt=0:59:00 -q hep.q -o %s.log -e %s.err'%(filename,filename,filename)
    #exec_line='qsub -q hep.q -l h_rt=0:59:00 -o %s%s'%(filename)
    print exec_line
    if not opts.dryRun : os.system(exec_line)



#nuisance_groups = ["all","none","AlphaS_migrations","Branching_ratio","Diphoton_MVA_preselection","Electron_veto","Integrated_luminosity","Jet_energy_scale_and_resolution","Lepton_reconstruction_and_btag_efficiencies","Modelling_of_detector_response_in_GEANT4","Modelling_of_material_budget","Nonlinearity_of_detector_response","Nonuniformity_of_light_collection","PDF_and_alphaS_yield","PDF_migrations","Per_photon_energy_resolution_estimate","Photon_energy_scale_and_smearing","Photon_identification","Photon_preselection","QCD_scale_migrations","QCD_scale_yield","Shower_shape_corrections","Trigger_efficiency","UE_and_PS","Vertex_finding_efficiency","ggF_contamination_in_VBF_categories","ggF_contamination_in_ttH_categories","MET"]
#nuisance_groups = ["all","none","AlphaS_migrations","Branching_ratio","Diphoton_MVA_preselection","Electron_veto","Integrated_luminosity","Jet_energy_scale_and_resolution","Lepton_reconstruction_and_btag_efficiencies","Modelling_of_detector_response_in_GEANT4","Modelling_of_material_budget","Nonlinearity_of_detector_response","Nonuniformity_of_light_collection","PDF_and_alphaS_yield","PDF_migrations","Per_photon_energy_resolution_estimate","Photon_energy_scale_and_smearing","Photon_identification","Photon_preselection","QCD_scale_migrations","QCD_scale_yield","Shower_shape_corrections","Trigger_efficiency","UE_and_PS","Vertex_finding_efficiency","ggF_contamination_in_VBF_categories","ggF_contamination_in_ttH_categories","MET","other_new_ggF"]
nuisance_groups = ["all","none","AlphaS_migrations","Branching_ratio","Diphoton_MVA_preselection","Electron_veto","Integrated_luminosity","Jet_energy_scale_and_resolution","Lepton_reconstruction_and_btag_efficiencies","Modelling_of_detector_response_in_GEANT4","Modelling_of_material_budget","Nonlinearity_of_detector_response","Nonuniformity_of_light_collection","PDF_and_alphaS_yield","PDF_migrations","Per_photon_energy_resolution_estimate","Photon_energy_scale_and_smearing","Photon_identification","Photon_preselection","QCD_scale_migrations","QCD_scale_yield","Shower_shape_corrections","Trigger_efficiency","UE_and_PS","Vertex_finding_efficiency","ggF_contamination_in_ttH_categories","MET","new_ggF_qmtop","new_ggF_pt","new_ggF_Mig","new_ggF_VBF","new_ggF_ResMu"]
POIs =["r","r_ggH","r_qqH","r_VH","r_ttH"]
#POIs =["r_ggH","r_qqH","r_VH","r_ttH"]
print "considering the following POIs: ",POIs
print "With",len(nuisance_groups),"nuisance groups"
print "which are ",nuisance_groups

if not opts.makeTable:
   print "text2workspace.py  CMS-HGG_mva_13TeV_datacard.txt -m125 -o CMS-HGG_mva_13TeV_datacard.root"
   os.system("text2workspace.py  CMS-HGG_mva_13TeV_datacard.txt -m125 -o CMS-HGG_mva_13TeV_datacard.root")
   print "done text2workspace.py"
   #os.system("text2workspace.py  CMS-HGG_mva_13TeV_datacard.txt -m125 -o CMS-HGG_mva_13TeV_datacard.perProc.root -P HiggsAnalysis.CombinedLimit.PhysicsModel:floatingXSHiggs --PO modes=ggH,qqH,ttH,VH --PO higgsMassRange=122,128")
   print "text2workspace.py  CMS-HGG_mva_13TeV_datacard.txt -m125 -o CMS-HGG_mva_13TeV_datacard.perProc.root -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO map=.*/qqH_hgg:r_qqH[1,-5,5] --PO map=.*/ggH_hgg:r_ggH[1,-5,5] --PO map=.*/ttH_hgg:r_ttH[1,-5,5] --PO map=.*/WH_lep_hgg:r_VH[1,-5,5] --PO map=.*/ZH_lep_hgg:r_VH[1,-5,5] --PO map=.*/WH_had_hgg:r_VH[1,-5,5] --PO map=.*/ZH_had_hgg:r_VH[1,-5,5] --PO higgsMassRange=122,128"
   os.system("text2workspace.py  CMS-HGG_mva_13TeV_datacard.txt -m125 -o CMS-HGG_mva_13TeV_datacard.perProc.root -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO map=.*/qqH_hgg:r_qqH[1,-5,5] --PO map=.*/ggH_hgg:r_ggH[1,-5,5] --PO map=.*/ttH_hgg:r_ttH[1,-5,5] --PO map=.*/WH_lep_hgg:r_VH[1,-5,5] --PO map=.*/ZH_lep_hgg:r_VH[1,-5,5] --PO map=.*/WH_had_hgg:r_VH[1,-5,5] --PO map=.*/ZH_had_hgg:r_VH[1,-5,5] --PO higgsMassRange=122,128")
   print "done text2workspace.py"

   for POI in POIs:
     os.system("mkdir -p SystematicsTable/%s"%POI)
     os.system("cp CMS-HGG_mva_13TeV_datacard.root SystematicsTable/%s/."%POI)    
     os.system("cp CMS-HGG_mva_13TeV_datacard.perProc.root SystematicsTable/%s/."%POI)    
     for ng in nuisance_groups:
       writeJobFileAndSubmit("%s/SystematicsTable/%s"%(os.getcwd(),POI),ng,POI)

if opts.makeTable:
  overall_array = {}
  sumInQuad = {}
  for POI in POIs:
     sumInQuad[POI] = 0.
     poi_array = {}
     directory="%s/SystematicsTable/%s"%(os.getcwd(),POI)
     nominalValues = values= getUpDownUncertainties(directory,"none",POI) 
     for ng in nuisance_groups:
       values= getUpDownUncertainties(directory,ng,POI)
       #print ng, nominalValues, values
       thisUpWrtCentral = (abs(nominalValues[0] **2 - values[0]**2))**(0.5)
       thisDownWrtCentral = (abs(nominalValues[1] **2 - values[1]**2))**(0.5)
       thisSymmWrtCentral = (abs(nominalValues[2] **2 - values[2]**2))**(0.5)
       poi_array[ng]=[thisUpWrtCentral,thisDownWrtCentral,thisSymmWrtCentral]
       if ng != "all":
         sumInQuad[POI] += thisSymmWrtCentral**2
     valueMap={}
     for this_ng in sorted(poi_array.items(),key=lambda e: e[1][2], reverse=True):
       #print this_ng, this_ng[1][2]
       valueMap[this_ng[0]]=100*this_ng[1][2]
     overall_array[POI]=valueMap
  #now make final table:
  print " \\resizebox{\\textwidth}{!}{"
  table_definition= " \\begin{tabular} { |l | "
  for POI in POIs : table_definition = table_definition + " c | "
  table_definition = table_definition + " }"
  print table_definition
  print "\\hline"
  print "\multicolumn{%d}{|l|}{Expected relative uncertainty for SM Higgs boson ($m_{\\text{H}} = 125 GeV$) } \\\\ "%(len(POIs)+1)
  print "\\hline"
  column_headers = " Systematic   "
  for POI in POIs :
     fancyPOIName = POI.replace("r","\\mu")
     if (len(POI.split("_"))>1) : fancyPOIName=POI.split("_")[0]+"_{\\text{"+POI.split("_")[1]+"}}" 
     column_headers = column_headers + " & $" + fancyPOIName.replace("r","\\mu") + "$"
  column_headers = column_headers +" \\\\"
  print column_headers
  print "\\hline"
  #for this_ng in sorted(overall_array[POIs[0]].items(),key=lambda e: e[1], reverse=True):
  #for this_ng in sorted(overall_array[POIs[1]].items(),key=lambda e: e[1], reverse=True):
  for this_ng in sorted(overall_array[POIs[2]].items(),key=lambda e: e[1], reverse=True):
      if (this_ng[0] == "none") : continue
      if (this_ng[0] == "all") : continue
      print_line= this_ng[0].replace("_"," ") + " "
      for POI in POIs   : print_line = print_line + " &  %.2f \%%"% overall_array[POI][this_ng[0]]
      print_line = print_line + " \\\\ "
      print print_line
  print "\\hline"
  print_line = "Sum "
  for POI in POIs: 
    total = 100.*((sumInQuad[POI])**(0.5))
    print_line = print_line + " &  %.2f \%%"% total
  print_line = print_line + " \\\\ "
  print print_line
  print_line = "Total "
  for POI in POIs: 
    fullVal = overall_array[POI]["all"]
    print_line = print_line + " &  %.2f \%%"% fullVal
  print_line = print_line + " \\\\ "
  print print_line
  print "\\hline"
  print "\end{tabular}}" 
  



#PDF_migrations group = CMS_hgg_pdfWeight_0 CMS_hgg_pdfWeight_1 CMS_hgg_pdfWeight_2 CMS_hgg_pdfWeight_3 CMS_hgg_pdfWeight_4 CMS_hgg_pdfWeight_5 CMS_hgg_pdfWeight_6 CMS_hgg_pdfWeight_7 CMS_hgg_pdfWeight_8 CMS_hgg_pdfWeight_9 CMS_hgg_pdfWeight_10 CMS_hgg_pdfWeight_11 CMS_hgg_pdfWeight_12 CMS_hgg_pdfWeight_13 CMS_hgg_pdfWeight_14 CMS_hgg_pdfWeight_15 CMS_hgg_pdfWeight_16 CMS_hgg_pdfWeight_17 CMS_hgg_pdfWeight_18 CMS_hgg_pdfWeight_19 CMS_hgg_pdfWeight_20 CMS_hgg_pdfWeight_21 CMS_hgg_pdfWeight_22 CMS_hgg_pdfWeight_23 CMS_hgg_pdfWeight_24 CMS_hgg_pdfWeight_25 CMS_hgg_pdfWeight_26 CMS_hgg_pdfWeight_27 CMS_hgg_pdfWeight_28 CMS_hgg_pdfWeight_29 CMS_hgg_pdfWeight_30 CMS_hgg_pdfWeight_31 CMS_hgg_pdfWeight_32 CMS_hgg_pdfWeight_33 CMS_hgg_pdfWeight_34 CMS_hgg_pdfWeight_35 CMS_hgg_pdfWeight_36 CMS_hgg_pdfWeight_37 CMS_hgg_pdfWeight_38 CMS_hgg_pdfWeight_39 CMS_hgg_pdfWeight_40 CMS_hgg_pdfWeight_41 CMS_hgg_pdfWeight_42 CMS_hgg_pdfWeight_43 CMS_hgg_pdfWeight_44 CMS_hgg_pdfWeight_45 CMS_hgg_pdfWeight_46 CMS_hgg_pdfWeight_47 CMS_hgg_pdfWeight_48 CMS_hgg_pdfWeight_49 CMS_hgg_pdfWeight_50 CMS_hgg_pdfWeight_51 CMS_hgg_pdfWeight_52 CMS_hgg_pdfWeight_53 CMS_hgg_pdfWeight_54 CMS_hgg_pdfWeight_55 CMS_hgg_pdfWeight_56 CMS_hgg_pdfWeight_57 CMS_hgg_pdfWeight_58 CMS_hgg_pdfWeight_59
#PDF_and_alphaS_yield group = pdf_Higgs_qqbar pdf_Higgs_gg pdf_Higgs_ttH
#AlphaS_migrations group = CMS_hgg_alphaSWeight_0
#QCD_scale_yield group = QCDscale_ggH QCDscale_qqH QCDscale_ttH QCDscale_VH
#QCD_scale_migrations group = CMS_hgg_scaleWeight_0 CMS_hgg_scaleWeight_1 CMS_hgg_scaleWeight_2
#ggF_contamination_in_ttH_categories group = CMS_hgg_tth_parton_shower CMS_hgg_tth_gluon_splitting CMS_hgg_tth_mc_low_stat 
#ggF_contamination_in_VBF_categories group = CMS_hgg_JetVeto_migration0 CMS_hgg_JetVeto_migration1 CMS_hgg_JetVeto_migration2
#Branching_ratio group = BR_hgg
#UE_and_PS group = CMS_hgg_UE CMS_hgg_PS
#Photon_energy_scale_and_smearing group = CMS_hgg_nuisance_HighR9EB_13TeVscale CMS_hgg_nuisance_HighR9EE_13TeVscale CMS_hgg_nuisance_LowR9EB_13TeVscale CMS_hgg_nuisance_LowR9EE_13TeVscale CMS_hgg_nuisance_HighR9EBPhi_13TeVsmear CMS_hgg_nuisance_HighR9EBRho_13TeVsmear CMS_hgg_nuisance_HighR9EEPhi_13TeVsmear CMS_hgg_nuisance_HighR9EERho_13TeVsmear CMS_hgg_nuisance_LowR9EBPhi_13TeVsmear  CMS_hgg_nuisance_LowR9EBRho_13TeVsmear CMS_hgg_nuisance_LowR9EEPhi_13TeVsmear CMS_hgg_nuisance_LowR9EERho_13TeVsmear 
#Modelling_of_material_budget group = CMS_hgg_nuisance_MaterialCentral_scale CMS_hgg_nuisance_MaterialForward_scale
#Nonlinearity_of_detector_response group = CMS_hgg_nuisance_NonLinearity_13TeVscale 
#Nonuniformity_of_light_collection group = CMS_hgg_nuisance_FNUFEE_scale CMS_hgg_nuisance_FNUFEB_scale
#Per_photon_energy_resolution_estimate group = CMS_hgg_SigmaEOverEShift 
#Modelling_of_detector_response_in_GEANT4 group = CMS_hgg_nuisance_Geant4_13TeVscale
#Photon_preselection group =  CMS_hgg_PreselSF
#Shower_shape_corrections group = CMS_hgg_nuisance_ShowerShapeHighR9EE_scale CMS_hgg_nuisance_ShowerShapeHighR9EB_scale CMS_hgg_nuisance_ShowerShapeLowR9EE_scale CMS_hgg_nuisance_ShowerShapeLowR9EB_scale 
#Integrated_luminosity group = lumi_13TeV
#Trigger_efficiency group = CMS_hgg_TriggerWeight
#Vertex_finding_efficiency group = CMS_hgg_nuisance_deltafracright
#Jet_energy_scale_and_resolution group = CMS_hgg_JER_TTH CMS_hgg_JEC_TTH CMS_hgg_JER_migration0 CMS_hgg_JER_migration1 CMS_hgg_JER_migration2 CMS_hgg_JEC_migration0 CMS_hgg_JEC_migration1 CMS_hgg_JEC_migration2
#Lepton_reconstruction_and_btag_efficiencies group = CMS_eff_b CMS_eff_m CMS_eff_m_MiniIso CMS_eff_e CMS_hgg_BTagReshape_TTH
#Photon_identification group = CMS_hgg_phoIdMva
#Diphoton_MVA_preselection group = CMS_hgg_LooseMvaSF
#Electron_veto group = CMS_hgg_electronVetoSF
#MET group = CMS_hgg_MET_JEC CMS_hgg_MET_JER CMS_hgg_MET_Unclustered CMS_hgg_MET_PhotonScale
#Rejections_of_jets_from_pileup group = CMS_hgg_PUJIDShift_migration0

#alternatives
#ggF_contamination_in_VBF_categories group = CMS_hgg_THU_ggH_VBF3j CMS_hgg_THU_ggH_Res CMS_hgg_THU_ggH_Mig12 CMS_hgg_THU_ggH_VBF2j CMS_hgg_THU_ggH_Mig01 CMS_hgg_THU_ggH_Mu
#other_new_ggF group = CMS_hgg_THU_ggH_qmtop CMS_hgg_THU_ggH_PT120 CMS_hgg_THU_ggH_PT60

#new_ggF_qmtop group = CMS_hgg_THU_ggH_qmtop
#new_ggF_pt group = CMS_hgg_THU_ggH_PT120 CMS_hgg_THU_ggH_PT60
#new_ggF_Mig group = CMS_hgg_THU_ggH_Mig12 CMS_hgg_THU_ggH_Mig01
#new_ggF_VBF group = CMS_hgg_THU_ggH_VBF3j CMS_hgg_THU_ggH_VBF2j
#new_ggF_ResMu group = CMS_hgg_THU_ggH_Res CMS_hgg_THU_ggH_Mu
