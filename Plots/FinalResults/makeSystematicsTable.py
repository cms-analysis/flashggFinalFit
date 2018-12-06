#!/usr/bin/env python
import os
import numpy
import sys

from optparse import OptionParser
from optparse import OptionGroup
from collections import OrderedDict as ordict
import ROOT as r

parser = OptionParser()
parser.add_option('--makeTable',      default=False, action='store_true',   help='Make the table instead of submitting jobs')
parser.add_option('--makePlot',       default=False, action='store_true',   help='Make pretty plot (requires both observed and expected)')
parser.add_option('--dryRun',         default=False, action='store_true',   help='Do not submit jobs')
parser.add_option('--observed',       default=False, action='store_true',   help='Observed, rather than expected, uncertainties')
parser.add_option('--relToStat',      default=False, action='store_true',   help='Compute the uncertainties as the increase relative to stat only fit, rather than decrease relative to full fit')
parser.add_option('--setParams',      default=None,                           help='Optional extra options to pass to combine (e.g. to set background indices)')
parser.add_option('--pois',           default=None, dest='POIs',            help='Parameters of interest')
parser.add_option('--nuisanceGroups', default=None, dest='nuisance_groups', help='Parameters of interest')
parser.add_option('--folderName',     default='Expected')
parser.add_option('--folderExt',      default='')
(opts,args) = parser.parse_args()
if opts.observed: opts.folderName = 'Observed'
if opts.folderExt != '': opts.folderName += '_%s'%opts.folderExt

if not opts.nuisance_groups:
  #default
  #opts.nuisance_groups = ['all','none','QCD_scale_yield','ggF_contamination_in_VBF_categories','QCD_scale_migrations','PDF_and_alphaS_yield','PDF_migrations','AlphaS_migrations','Branching_ratio','Integrated_luminosity','Jet_energy_scale_and_resolution','UE_and_PS','Lepton_reconstruction_and_btag_efficiencies','MET','ggF_contamination_in_ttH_categories','Photon_identification','Per_photon_energy_resolution_estimate','Photon_energy_scale_and_smearing','Shower_shape_corrections','Nonlinearity_of_detector_response','Nonuniformity_of_light_collection','Modelling_of_material_budget','Modelling_of_detector_response_in_GEANT4','Trigger_efficiency','Photon_preselection','Diphoton_MVA_preselection','Electron_veto','Vertex_finding_efficiency']
  
  #new
  #opts.nuisance_groups = ['all','none','new_ggF_QCDscales','new_ggF_contamination_in_VBF_categories','new_ggF_pt','new_ggF_qmtop','non_ggH_QCD_scale_yield','non_ggH_QCD_scale_migrations','PDF_and_alphaS_yield','PDF_migrations','AlphaS_migrations','Branching_ratio','Integrated_luminosity','Jet_energy_scale_and_resolution','UE_and_PS','Lepton_reconstruction_and_btag_efficiencies','MET','ggF_contamination_in_ttH_categories','Photon_identification','Per_photon_energy_resolution_estimate','Photon_energy_scale_and_smearing','Shower_shape_corrections','Nonlinearity_of_detector_response','Nonuniformity_of_light_collection','Modelling_of_material_budget','Modelling_of_detector_response_in_GEANT4','Trigger_efficiency','Photon_preselection','Diphoton_MVA_preselection','Electron_veto','Vertex_finding_efficiency']
  opts.nuisance_groups = ['all','none','new_ggF_QCDscales','new_ggF_contamination_in_VBF_categories','new_ggF_pt','new_ggF_qmtop','non_ggH_QCD_scale_yield','non_ggH_QCD_scale_migrations','PDF_and_alphaS_yield','PDF_migrations','AlphaS_migrations','Branching_ratio','Integrated_luminosity','Jet_energy_scale_and_resolution','Lepton_reconstruction_and_btag_efficiencies','MET','ggF_contamination_in_ttH_categories','Photon_identification','Per_photon_energy_resolution_estimate','Photon_energy_scale_and_smearing','Shower_shape_corrections','Nonlinearity_of_detector_response','Nonuniformity_of_light_collection','Modelling_of_material_budget','Modelling_of_detector_response_in_GEANT4','Trigger_efficiency','Photon_preselection','Diphoton_MVA_preselection','Electron_veto','Vertex_finding_efficiency'] #FIXME
  
  #new granular
  #opts.nuisance_groups = ['all','none','new_ggF_Mu','new_ggF_Res','new_ggF_Mig01','new_ggF_Mig12','new_ggF_VBF2j','new_ggF_VBF3j','new_ggF_pt60','new_ggF_pt120','new_ggF_qmtop','non_ggH_QCD_scale_yield','non_ggH_QCD_scale_migrations','PDF_and_alphaS_yield','PDF_migrations','AlphaS_migrations','Branching_ratio','Integrated_luminosity','Jet_energy_scale_and_resolution','UE_and_PS','Lepton_reconstruction_and_btag_efficiencies','MET','ggF_contamination_in_ttH_categories','Photon_identification','Per_photon_energy_resolution_estimate','Photon_energy_scale_and_smearing','Shower_shape_corrections','Nonlinearity_of_detector_response','Nonuniformity_of_light_collection','Modelling_of_material_budget','Modelling_of_detector_response_in_GEANT4','Trigger_efficiency','Photon_preselection','Diphoton_MVA_preselection','Electron_veto','Vertex_finding_efficiency']
else:
  opts.nuisance_groups = opts.nuisance_groups.split(',')

if not opts.POIs:
  opts.POIs = ['r','r_ggH','r_qqH','r_VH','r_ttH']
else:
  opts.POIs = opts.POIs.split(',')


def getUpDownUncertainties(directory,nuisance_group,POI):
  tf = r.TFile('%s/higgsCombine_%s.MultiDimFit.mH125.root'%(directory,nuisance_group))
  tree = tf.Get('limit')
  centralValue=-1
  loValue=-1
  hiValue=-1
  #print 'nuisance group is %s' %nuisance_group
  for i in range(tree.GetEntries()):
    tree.GetEntry(i)
    quantile =  getattr(tree,'quantileExpected')
    poival   =  getattr(tree,POI)
    if (quantile ==-1) : centralValue=poival
  for i in range(tree.GetEntries()):
    tree.GetEntry(i)
    quantile =  getattr(tree,'quantileExpected')
    poival   =  getattr(tree,POI)
    if (poival==-1) : continue
    if (poival >= centralValue) : hiValue=poival
    if (poival <= centralValue) : loValue=poival
  tf.Close()
  up   = hiValue - centralValue
  down = loValue - centralValue
  symm = (up-down)/2
  return up,down,symm


def writeJobFileAndSubmit(directory,nuisance_group,POI='r'):
  filename = '%s/sub_job.%s.sh'%(directory,nuisance_group)
  sub_file = open(filename,'w')
  sub_file.write('#!/bin/bash\n')
  sub_file.write('ulimit -s unlimited\n')
  sub_file.write('cd %s\n'%directory)
  sub_file.write('export SCRAM_ARCH=slc6_amd64_gcc630\n')
  sub_file.write('eval `scramv1 runtime -sh`\n')
  sub_file.write('cd %s\n'%directory)
  freezeCmd = ''
  if not opts.relToStat:
    if 'all' in nuisance_group: freezeCmd = ' --freezeParameters all'
    elif not 'none' in nuisance_group: freezeCmd = ' --freezeNuisanceGroups=%s'%nuisance_group
  else:
    if 'all' in nuisance_group: freezeCmd = ' --freezeParameters all'
    elif 'none' in nuisance_group: freezeCmd = ''
    else:
      freezeCmd = ' --freezeNuisanceGroups='
      for ng in opts.nuisance_groups:
        if 'none' in ng or 'all' in ng: continue
        if not ng==nuisance_group:
          freezeCmd += '%s,'%ng
      freezeCmd = freezeCmd[:-1]
      freezeCmd += ' '
  if opts.setParams:
    freezeCmd += ' %s '%opts.setParams

  if (POI=='r') : 
    if opts.observed:
      sub_file.write('eval combine  CMS-HGG_mva_13TeV_datacard.root -M MultiDimFit --saveWorkspace -n _postFitForTable_%s --robustFit 1 -m 125 --algo singles --cl=0.68  \n'%nuisance_group)
      sub_file.write('eval combine  higgsCombine_postFitForTable_%s.MultiDimFit.mH125.root  -M MultiDimFit --snapshotName MultiDimFit --robustFit 1 -m 125  --algo singles --cl=0.68  -n _%s %s\n'%(nuisance_group, nuisance_group, freezeCmd))
    else:
      sub_file.write('eval combine  CMS-HGG_mva_13TeV_datacard.root -M MultiDimFit --robustFit 1 -t -1 --expectSignal 1 -m 125  --algo singles --cl=0.68  -n _%s %s\n'%(nuisance_group, freezeCmd))

  else:  
    if opts.observed:
      sub_file.write('eval combine  CMS-HGG_mva_13TeV_datacard.perProc.root -M MultiDimFit --saveWorkspace -n _postFitForTable_%s --robustFit 1 --redefineSignalPOIs %s -P %s --floatOtherPOIs 1 -m 125 --setParameterRanges r_ggH=0.00,2.00:r_qqH=0.00,2.00:r_ttH=0.00,2.00:r_VH=-1.00,3.00  --algo singles --cl=0.68  \n'%(nuisance_group, POI, POI))
      sub_file.write('eval combine  higgsCombine_postFitForTable_%s.MultiDimFit.mH125.root -M MultiDimFit --snapshotName MultiDimFit --robustFit 1 --redefineSignalPOIs %s -P %s --floatOtherPOIs 1 -m 125 --setParameterRanges r_ggH=0.00,2.00:r_qqH=0.00,2.00:r_ttH=0.00,2.00:r_VH=-1.00,3.00  --algo singles --cl=0.68  -n _%s %s\n'%(nuisance_group, POI, POI, nuisance_group, freezeCmd))
    else:
      sub_file.write('eval combine  CMS-HGG_mva_13TeV_datacard.perProc.root -M MultiDimFit --robustFit 1 -t -1 --redefineSignalPOIs %s -P %s --floatOtherPOIs 1 --expectSignal 1 -m 125 --setParameterRanges r_ggH=0.00,2.00:r_qqH=0.00,2.00:r_ttH=0.00,2.00:r_VH=-1.00,3.00  --algo singles --cl=0.68  -n _%s %s\n'%(POI, POI, nuisance_group, freezeCmd))
  sub_file.close()
  os.system(' chmod +x %s'%(filename))
  exec_line='qsub -l h_rt=0:59:00 -q hep.q -o %s.log -e %s.err %s'%(filename, filename, filename)
  print exec_line
  if not opts.dryRun: os.system(exec_line)


def run():
  print 'considering the following POIs: ',opts.POIs
  print 'With',len(opts.nuisance_groups),'nuisance groups'
  print 'which are ',opts.nuisance_groups

  if not opts.makeTable and not opts.makePlot:
    print 'text2workspace.py  CMS-HGG_mva_13TeV_datacard.txt -m 125 -o CMS-HGG_mva_13TeV_datacard.root'
    os.system('text2workspace.py  CMS-HGG_mva_13TeV_datacard.txt -m 125 -o CMS-HGG_mva_13TeV_datacard.root')
    print 'done text2workspace.py'
    print 'text2workspace.py  CMS-HGG_mva_13TeV_datacard.txt -m 125 -o CMS-HGG_mva_13TeV_datacard.perProc.root -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO map=.*/qqH_hgg.*:r_qqH[1,-5,5] --PO map=.*/ggH_hgg.*:r_ggH[1,-5,5] --PO map=.*/ttH_hgg.*:r_ttH[1,-5,5] --PO map=.*/WH_lep_hgg.*:r_VH[1,-5,5] --PO map=.*/ZH_lep_hgg.*:r_VH[1,-5,5] --PO map=.*/WH_had_hgg.*:r_VH[1,-5,5] --PO map=.*/ZH_had_hgg.*:r_VH[1,-5,5] --PO higgsMassRange=122,128'
    os.system('text2workspace.py  CMS-HGG_mva_13TeV_datacard.txt -m 125 -o CMS-HGG_mva_13TeV_datacard.perProc.root -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO map=.*/qqH_hgg.*:r_qqH[1,-5,5] --PO map=.*/ggH_hgg.*:r_ggH[1,-5,5] --PO map=.*/ttH_hgg.*:r_ttH[1,-5,5] --PO map=.*/WH_lep_hgg.*:r_VH[1,-5,5] --PO map=.*/ZH_lep_hgg.*:r_VH[1,-5,5] --PO map=.*/WH_had_hgg.*:r_VH[1,-5,5] --PO map=.*/ZH_had_hgg.*:r_VH[1,-5,5] --PO higgsMassRange=122,128')
    print 'done text2workspace.py'
  
    for POI in opts.POIs:
      os.system('mkdir -p SystematicsTable%s/%s'%(opts.folderName,POI))
      os.system('cp CMS-HGG_mva_13TeV_datacard.root SystematicsTable%s/%s/.'%(opts.folderName,POI))    
      os.system('cp CMS-HGG_mva_13TeV_datacard.perProc.root SystematicsTable%s/%s/.'%(opts.folderName,POI))    
      for ng in opts.nuisance_groups:
        writeJobFileAndSubmit('%s/SystematicsTable%s/%s'%(os.getcwd(),opts.folderName,POI),ng,POI)
  
  if opts.makeTable:
    overall_array = {}
    sumInQuad = {}
    for POI in opts.POIs:
      sumInQuad[POI] = 0.
      #poi_array = {}
      poi_array = ordict()
      directory='%s/SystematicsTable%s/%s'%(os.getcwd(),opts.folderName,POI)
      if not opts.relToStat:
        nominalValues = getUpDownUncertainties(directory,'none',POI)
      else:
        nominalValues = getUpDownUncertainties(directory,'all',POI)
      for ng in opts.nuisance_groups:
        values = getUpDownUncertainties(directory,ng,POI)
        #print ng, nominalValues, values
        thisUpWrtCentral   = (abs(nominalValues[0]**2 - values[0]**2))**(0.5)
        thisDownWrtCentral = (abs(nominalValues[1]**2 - values[1]**2))**(0.5)
        thisSymmWrtCentral = (abs(nominalValues[2]**2 - values[2]**2))**(0.5)
        poi_array[ng]=[thisUpWrtCentral,thisDownWrtCentral,thisSymmWrtCentral]
        if ng != 'all' and ng!='none':
          sumInQuad[POI] += thisSymmWrtCentral**2
      #valueMap={}
      valueMap=ordict()
      #for this_ng in sorted(poi_array.items(),key=lambda e: e[1][2], reverse=True):
      for this_ng in poi_array.items():
        valueMap[this_ng[0]]=100*this_ng[1][2]
      overall_array[POI]=valueMap
    #now make final table:
    table_definition= '\\begin{tabular} { |l | '
    for POI in opts.POIs : table_definition = table_definition + ' c | '
    table_definition = table_definition + ' }'
    print table_definition
    print '\\hline'
    print '\multicolumn{%d}{|l|}{Expected relative uncertainty for SM Higgs boson ($m_{\\text{H}} = 125 GeV$) } \\\\ '%(len(opts.POIs)+1)
    print '\\hline'
    column_headers = ' Systematic   '
    for POI in opts.POIs :
      fancyPOIName = POI.replace('r','\\mu')
      if (len(POI.split('_'))>1) : fancyPOIName=POI.split('_')[0]+'_{\\text{'+POI.split('_')[1]+'}}' 
      column_headers = column_headers + ' & $' + fancyPOIName.replace('r','\\mu') + '$'
    column_headers = column_headers +' \\\\'
    print column_headers
    print '\\hline'
    #for this_ng in sorted(overall_array[POIs[0]].items(),key=lambda e: e[1], reverse=True):
    for this_ng in overall_array[opts.POIs[0]].items():
      if (this_ng[0] == 'none') : continue
      if (this_ng[0] == 'all') : continue
      print_line= this_ng[0].replace('_',' ') + ' '
      for POI in opts.POIs   : print_line = print_line + ' &  %.2f \%%'% overall_array[POI][this_ng[0]]
      print_line = print_line + ' \\\\ '
      print print_line
    print '\\hline'
    print_line = 'Sum '
    for POI in opts.POIs: 
      total = 100.*((sumInQuad[POI])**(0.5))
      print_line = print_line + ' &  %.2f \%%'% total
    print_line = print_line + ' \\\\ '
    print print_line
    print_line = 'Total '
    for POI in opts.POIs: 
      fullVal = overall_array[POI]['all']
      print_line = print_line + ' &  %.2f \%%'% fullVal
    print_line = print_line + ' \\\\ '
    print print_line
    print '\\hline'
    print '\end{tabular}' 
  
  if opts.makePlot:
    #plotNuisances = ['UE_and_PS','PDF_and_alphaS_yield','non_ggH_QCD_scale_migrations','non_ggH_QCD_scale_yield','new_ggF_contamination_in_VBF_categories','new_ggF_pt','new_ggF_QCDscales','Branching_ratio','Integrated_luminosity','Jet_energy_scale_and_resolution','Per_photon_energy_resolution_estimate','Photon_energy_scale_and_smearing','Photon_identification']
    plotNuisances = ['PDF_and_alphaS_yield','non_ggH_QCD_scale_migrations','non_ggH_QCD_scale_yield','new_ggF_contamination_in_VBF_categories','new_ggF_pt','new_ggF_QCDscales','Branching_ratio','Integrated_luminosity','Jet_energy_scale_and_resolution','Per_photon_energy_resolution_estimate','Photon_energy_scale_and_smearing','Photon_identification'] #FIXME
    exp_overall_array = {}
    obs_overall_array = {}
    for POI in opts.POIs:
      exp_poi_array = ordict()
      obs_poi_array = ordict()
      exp_directory='%s/SystematicsTable%s/%s'%(os.getcwd(),opts.folderName.replace('Observed','Expected'),POI)
      #obs_directory='%s/SystematicsTable%s/%s'%(os.getcwd(),opts.folderName.replace('Expected','Observed'),POI)
      obs_directory='%s/SystematicsTable%s/%s'%(os.getcwd(),opts.folderName.replace('Observed','Expected'),POI) #FIXME
      if not opts.relToStat:
        expNominalValues = getUpDownUncertainties(exp_directory,'none',POI) 
        obsNominalValues = getUpDownUncertainties(obs_directory,'none',POI) 
      else:
        expNominalValues = getUpDownUncertainties(exp_directory,'all',POI) 
        obsNominalValues = getUpDownUncertainties(obs_directory,'all',POI) 
      for ng in plotNuisances:
        expValues= getUpDownUncertainties(exp_directory,ng,POI)
        obsValues= getUpDownUncertainties(obs_directory,ng,POI)
        #print ng, nominalValues, values
        thisUpWrtCentral   = (abs(expNominalValues[0]**2 - expValues[0]**2))**(0.5)
        thisDownWrtCentral = (abs(expNominalValues[1]**2 - expValues[1]**2))**(0.5)
        thisSymmWrtCentral = (abs(expNominalValues[2]**2 - expValues[2]**2))**(0.5)
        exp_poi_array[ng]  = [thisUpWrtCentral,thisDownWrtCentral,thisSymmWrtCentral]
        thisUpWrtCentral   = (abs(obsNominalValues[0]**2 - obsValues[0]**2))**(0.5)
        thisDownWrtCentral = (abs(obsNominalValues[1]**2 - obsValues[1]**2))**(0.5)
        thisSymmWrtCentral = (abs(obsNominalValues[2]**2 - obsValues[2]**2))**(0.5)
        obs_poi_array[ng]  = [thisUpWrtCentral,thisDownWrtCentral,thisSymmWrtCentral]
      expValueMap=ordict()
      obsValueMap=ordict()
      for this_ng in exp_poi_array.items():
        expValueMap[this_ng[0]]=this_ng[1][2]
      for this_ng in obs_poi_array.items():
        obsValueMap[this_ng[0]]=this_ng[1][2]
      exp_overall_array[POI]=expValueMap
      obs_overall_array[POI]=obsValueMap
    r.gROOT.SetBatch(True)
    r.gStyle.SetOptStat(0)
    numNuis = len(plotNuisances)
    plotPOIs =['r','r_qqH','r_ttH']
    expHists = {}
    obsHists = {}
    legends = {}
    for POI in plotPOIs:
      expHists[POI] = r.TH1F('expHist_%s'%POI, 'expHist_%s'%POI, 2*numNuis+1, 0, 2*numNuis)
      expHists[POI].SetFillStyle(0)
      expHists[POI].SetLineStyle(1)
      expHists[POI].SetMarkerStyle(1)
      obsHists[POI] = r.TH1F('obsHist_%s'%POI, 'obsHist_%s'%POI, 2*numNuis+1, 0, 2*numNuis)
      obsHists[POI].SetLineColor(0)
      obsHists[POI].SetTitle('')
      obsHists[POI].GetYaxis().SetNdivisions(2,5,0)
      if POI == plotPOIs[0]:
        legends[POI] = r.TLegend(0.7,0.15,0.88,0.25)
        expHists[POI].GetYaxis().SetTickLength(0.06)
        obsHists[POI].GetYaxis().SetTickLength(0.06)
        expHists[POI].GetYaxis().SetLabelSize(0.025)
        obsHists[POI].GetYaxis().SetLabelSize(0.025)
        legends[POI].SetTextSize(0.03)
        legends[POI].SetTextSize(0.03)
      else:
        legends[POI] = r.TLegend(0.5,0.15,0.86,0.25)
        expHists[POI].GetYaxis().SetTickLength(0.03)
        obsHists[POI].GetYaxis().SetTickLength(0.03)
        expHists[POI].GetYaxis().SetLabelSize(0.05)
        obsHists[POI].GetYaxis().SetLabelSize(0.05)
        #expHists[POI].GetYaxis().SetLabelOffset(0.0001)
        #obsHists[POI].GetYaxis().SetLabelOffset(0.0001)
        #expHists[POI].GetYaxis().SetTitleOffset(0.5)
        #obsHists[POI].GetYaxis().SetTitleOffset(0.5)
        legends[POI].SetTextSize(0.06)
        legends[POI].SetTextSize(0.06)
      legends[POI].SetBorderSize(0)
      legends[POI].AddEntry(obsHists[POI],' Observed','F')
      legends[POI].AddEntry(expHists[POI],' Expected','F')
    nuisCounter = 1
    for this_ng in exp_overall_array[opts.POIs[0]].items():
      if this_ng[0] not in plotNuisances: continue
      #nuisLabel = this_ng[0].replace('_',' ') + ' '
      #expHists[plotPOIs[0]].GetXaxis().SetBinLabel(nuisCounter, nuisLabel)
      for POI in plotPOIs:
        expHists[POI].Fill( nuisCounter, exp_overall_array[POI][this_ng[0]] )
      nuisCounter += 2
    nuisCounter = 1
    for this_ng in obs_overall_array[opts.POIs[0]].items():
      if this_ng[0] not in plotNuisances: continue
      #plotNuisances = ['new_ggF_qmtop','new_ggF_contamination_in_VBF_categories','new_ggF_pt','new_ggF_QCDscales','non_ggH_QCD_scale_yield','non_ggH_QCD_scale_migrations','PDF_and_alphaS_yield','Branching_ratio','Integrated_luminosity','Jet_energy_scale_and_resolution','UE_and_PS','Photon_identification','Per_photon_energy_resolution_estimate','Photon_energy_scale_and_smearing']
      nuisLabel = this_ng[0].replace('_',' ') + ' '
      nuisLabel = nuisLabel.replace('non ggH','Other processes')
      nuisLabel = nuisLabel.replace('QCDscales','QCD scale')
      nuisLabel = nuisLabel.replace('new ggF','ggH')
      nuisLabel = nuisLabel.replace('pt','p_{T} modelling')
      nuisLabel = nuisLabel.replace('contamination in VBF categories','jet multiplicity')
      nuisLabel = nuisLabel.replace('UE and PS','Underlying event and parton shower')
      nuisLabel = nuisLabel.replace('alphaS','#alpha_{s}')
      obsHists[plotPOIs[0]].GetXaxis().SetBinLabel(nuisCounter+1, nuisLabel)
      for POI in plotPOIs:
        obsHists[POI].Fill( nuisCounter, obs_overall_array[POI][this_ng[0]] )
      nuisCounter += 2
    canv = r.TCanvas('canv','canv',700,400)
    pad1 = r.TPad('pad1','pad1',0.0, 0.,0.5 ,1.)
    pad2 = r.TPad('pad2','pad2',0.5, 0.,0.75,1.)
    pad3 = r.TPad('pad3','pad3',0.75,0.,1.,  1.)
    #pad1.SetBottomMargin(10)
    #pad1.SetTopMargin(10)
    #pad1.SetRightMargin(0.02)
    pad1.SetLeftMargin(0.5)
    #pad2.SetBottomMargin(10)
    #pad2.SetTopMargin(10)
    #pad2.SetRightMargin(0.05)
    #pad2.SetLeftMargin(0.01)
    #pad3.SetBottomMargin(10)
    #pad3.SetTopMargin(10)
    #pad3.SetRightMargin(0)
    #pad3.SetLeftMargin(0.05)
    pad1.SetTickx(2)
    pad2.SetTickx(2)
    pad3.SetTickx(2)
    pad1.Draw()
    pad2.Draw()
    pad3.Draw()
    pad1.cd()
    expHists[plotPOIs[0]].SetLineColor(r.kBlue)
    #expHists[plotPOIs[0]].SetLineColor(r.kBlack)
    expHists[plotPOIs[0]].SetMinimum(0.)
    expHists[plotPOIs[0]].SetMaximum(0.1)
    expHists[plotPOIs[0]].GetXaxis().SetTickSize(0.)
    obsHists[plotPOIs[0]].SetFillColorAlpha(r.kBlue,0.5)
    obsHists[plotPOIs[0]].SetMinimum(0.)
    obsHists[plotPOIs[0]].SetMaximum(0.1)
    obsHists[plotPOIs[0]].GetXaxis().SetTickSize(0.)
    obsHists[plotPOIs[0]].Draw('hbar')
    expHists[plotPOIs[0]].Draw('hbar,same')
    legends[plotPOIs[0]].Draw()
    pad2.cd()
    expHists[plotPOIs[1]].SetLineColor(r.kGreen+2)
    #expHists[plotPOIs[1]].SetLineColor(r.kBlack+2)
    expHists[plotPOIs[1]].SetMinimum(0.)
    expHists[plotPOIs[1]].SetMaximum(0.3)
    expHists[plotPOIs[1]].GetXaxis().SetTickSize(0.)
    expHists[plotPOIs[1]].GetXaxis().SetLabelSize(0.)
    obsHists[plotPOIs[1]].SetFillColorAlpha(r.kGreen+2,0.5)
    obsHists[plotPOIs[1]].SetMinimum(0.)
    obsHists[plotPOIs[1]].SetMaximum(0.3)
    obsHists[plotPOIs[1]].GetYaxis().SetNdivisions(3,5,0)
    obsHists[plotPOIs[1]].GetXaxis().SetTickSize(0.)
    obsHists[plotPOIs[1]].GetXaxis().SetLabelSize(0.)
    #obsHists[plotPOIs[1]].GetYaxis().SetLabelOffset(0.0001)
    obsHists[plotPOIs[1]].Draw('hbar')
    expHists[plotPOIs[1]].Draw('hbar,same')
    legends[plotPOIs[1]].Draw()
    pad3.cd()
    expHists[plotPOIs[2]].SetLineColor(r.kMagenta-7)
    #expHists[plotPOIs[2]].SetLineColor(r.kBlack)
    expHists[plotPOIs[2]].SetMinimum(0.)
    expHists[plotPOIs[2]].SetMaximum(0.15)
    expHists[plotPOIs[2]].GetXaxis().SetTickSize(0.)
    expHists[plotPOIs[2]].GetXaxis().SetLabelSize(0.)
    obsHists[plotPOIs[2]].SetFillColorAlpha(r.kMagenta-7,0.5)
    obsHists[plotPOIs[2]].SetMinimum(0.)
    obsHists[plotPOIs[2]].SetMaximum(0.15)
    obsHists[plotPOIs[2]].GetYaxis().SetNdivisions(3,5,0)
    obsHists[plotPOIs[2]].GetXaxis().SetTickSize(0.)
    obsHists[plotPOIs[2]].GetXaxis().SetLabelSize(0.)
    #obsHists[plotPOIs[2]].GetYaxis().SetLabelOffset(0.0001)
    obsHists[plotPOIs[2]].Draw('hbar')
    expHists[plotPOIs[2]].Draw('hbar,same')
    legends[plotPOIs[2]].Draw()
    canv.cd()
    lat = r.TLatex()
    lat.SetTextFont(42)
    lat.SetTextSize(0.06)
    #lat.SetLineWidth(2)
    #lat.SetTextAlign(31)
    lat.DrawLatex(0.01,0.93,'#bf{CMS}  H#rightarrow#gamma#gamma')
    lat.SetTextSize(0.03)
    #lat.DrawLatex(0.3,0.96,'Uncertainty on #mu')
    #lat.DrawLatex(0.55,0.96,'Uncertainty on #mu VBF')
    #lat.DrawLatex(0.8,0.96,'Uncertainty on #mu ttH')
    lat.DrawLatex(0.27,0.96,'Uncertainty on overall #mu')
    lat.DrawLatex(0.57,0.96,'Uncertainty on #mu_{VBF}')
    lat.DrawLatex(0.82,0.96,'Uncertainty on #mu_{ttH}')
    canv.SaveAs('testSystematicsPlot.pdf')
    canv.SaveAs('testSystematicsPlot.png')

if __name__ == '__main__':
  run()
  

#default groupings
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

#alternative
#PDF_migrations group = CMS_hgg_pdfWeight_0 CMS_hgg_pdfWeight_1 CMS_hgg_pdfWeight_2 CMS_hgg_pdfWeight_3 CMS_hgg_pdfWeight_4 CMS_hgg_pdfWeight_5 CMS_hgg_pdfWeight_6 CMS_hgg_pdfWeight_7 CMS_hgg_pdfWeight_8 CMS_hgg_pdfWeight_9 CMS_hgg_pdfWeight_10 CMS_hgg_pdfWeight_11 CMS_hgg_pdfWeight_12 CMS_hgg_pdfWeight_13 CMS_hgg_pdfWeight_14 CMS_hgg_pdfWeight_15 CMS_hgg_pdfWeight_16 CMS_hgg_pdfWeight_17 CMS_hgg_pdfWeight_18 CMS_hgg_pdfWeight_19 CMS_hgg_pdfWeight_20 CMS_hgg_pdfWeight_21 CMS_hgg_pdfWeight_22 CMS_hgg_pdfWeight_23 CMS_hgg_pdfWeight_24 CMS_hgg_pdfWeight_25 CMS_hgg_pdfWeight_26 CMS_hgg_pdfWeight_27 CMS_hgg_pdfWeight_28 CMS_hgg_pdfWeight_29 CMS_hgg_pdfWeight_30 CMS_hgg_pdfWeight_31 CMS_hgg_pdfWeight_32 CMS_hgg_pdfWeight_33 CMS_hgg_pdfWeight_34 CMS_hgg_pdfWeight_35 CMS_hgg_pdfWeight_36 CMS_hgg_pdfWeight_37 CMS_hgg_pdfWeight_38 CMS_hgg_pdfWeight_39 CMS_hgg_pdfWeight_40 CMS_hgg_pdfWeight_41 CMS_hgg_pdfWeight_42 CMS_hgg_pdfWeight_43 CMS_hgg_pdfWeight_44 CMS_hgg_pdfWeight_45 CMS_hgg_pdfWeight_46 CMS_hgg_pdfWeight_47 CMS_hgg_pdfWeight_48 CMS_hgg_pdfWeight_49 CMS_hgg_pdfWeight_50 CMS_hgg_pdfWeight_51 CMS_hgg_pdfWeight_52 CMS_hgg_pdfWeight_53 CMS_hgg_pdfWeight_54 CMS_hgg_pdfWeight_55 CMS_hgg_pdfWeight_56 CMS_hgg_pdfWeight_57 CMS_hgg_pdfWeight_58 CMS_hgg_pdfWeight_59
#PDF_and_alphaS_yield group = pdf_Higgs_qqbar pdf_Higgs_gg pdf_Higgs_ttH
#AlphaS_migrations group = CMS_hgg_alphaSWeight_0
#non_ggH_QCD_scale_yield group = QCDscale_qqH QCDscale_ttH QCDscale_VH
#non_ggH_QCD_scale_migrations group = CMS_hgg_scaleWeight_0 CMS_hgg_scaleWeight_1 CMS_hgg_scaleWeight_2
#ggF_contamination_in_ttH_categories group = CMS_hgg_tth_parton_shower CMS_hgg_tth_gluon_splitting CMS_hgg_tth_mc_low_stat 
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
#new_ggF_contamination_in_VBF_categories group = CMS_hgg_THU_ggH_VBF3j CMS_hgg_THU_ggH_Mig12 CMS_hgg_THU_ggH_VBF2j CMS_hgg_THU_ggH_Mig01
#new_ggF_QCDscales group = CMS_hgg_THU_ggH_Res CMS_hgg_THU_ggH_Mu
#new_ggF_qmtop group = CMS_hgg_THU_ggH_qmtop
#new_ggF_pt group = CMS_hgg_THU_ggH_PT120 CMS_hgg_THU_ggH_PT60

#alternative granular
#new_ggF_Mig01 group = CMS_hgg_THU_ggH_Mig01
#new_ggF_Mig12 group = CMS_hgg_THU_ggH_Mig12
#new_ggF_VBF2j group = CMS_hgg_THU_ggH_VBF2j
#new_ggF_VBF3j group = CMS_hgg_THU_ggH_VBF3j
#new_ggF_Res group = CMS_hgg_THU_ggH_Res
#new_ggF_Mu group = CMS_hgg_THU_ggH_Mu
#new_ggF_qmtop group = CMS_hgg_THU_ggH_qmtop
#new_ggF_pt60 group = CMS_hgg_THU_ggH_PT60
#new_ggF_pt120 group = CMS_hgg_THU_ggH_PT120
