###################################################################################################
# 3 September 2020                                                                                                 
# Abe Tishelman-Charny 
#
# The purpose of this module is to run fggfinalfit steps 
#
# Example Usage:
# 
# Signal: (run twice)
# python HHWWggFinalFitScript.py --Step Signal --mode std --physics SM --finalStates SL --years 2016 --dirTypes Signal --note AllCats
# python HHWWggFinalFitScript.py --Step Signal --mode std --physics SM --finalStates SL --years 2016 --dirTypes Signal --note AllCats
# 
# Background:
# python HHWWggFinalFitScript.py --Step Background --mode fTestOnly --physics SM --finalStates SL --years 2016 --dirTypes Data --note AllCats 
# python HHWWggFinalFitScript.py --Step Background --mode bkgPlotsOnly --physics SM --finalStates SL --years 2016 --dirTypes Data --note AllCats
#
# Datacard:
# python HHWWggFinalFitScript.py --Step Datacard --mode datacard --physics SM --finalStates SL,FH,FL --years 2016,2017,2018 --note AllCats --dirTypes Datacard
#
# Combine: 
# python HHWWggFinalFitScript.py --Step Combine --mode combine --physics SM --finalStates SL,FL,FH --years 2016,2017,2018 --note AllCats --dirTypes Combine --combineInd
# python HHWWggFinalFitScript.py --Step Combine --mode combine --physics SM --finalStates FH,SL --years 2018 --note AllCats --dirTypes Combine --combineInd
# 
# python HHWWggFinalFitScript.py --Step Combine --mode combine --physics SM --finalStates SL,FL,FH --years 2016,2017,2018 --note AllCats --dirTypes Combine --Run2
# python HHWWggFinalFitScript.py --Step Combine --mode combine --physics SM --finalStates FH,SL --years 2016,2017,2018 --note AllCats --dirTypes Combine --Run2
#
# Plot:
# python HHWWggFinalFitScript.py --Step Plot --physicsCases SM --finalStates SL --years all --note Plot
# python HHWWggFinalFitScript.py --Step Plot --mode Plot --physicsCases Plot --finalStates Plot --years Plot --note Plot
#
###################################################################################################

import os 
import argparse 
import subprocess
# import CMS_lumi, tdrstyle

from HHWWggFinalFitScript_Tools import * 

parser = argparse.ArgumentParser()

parser.add_argument("--Step",type=str, default="", help="Fggfinalfit step to run", required=False)
parser.add_argument("--mode",type=str, default="", help="Fggfinalfit mode to run", required=False)
parser.add_argument("--physicsCases",type=str, default="", help="Comma separated list of physics cases to run. Ex: SM", required=False)
parser.add_argument("--finalStates",type=str, default="", help="Comma separated list of physics cases to run. Ex: SL,FH,FL", required=False)
parser.add_argument("--years",type=str, default="", help="Comma separated list of years to run. Ex: 2016,2017,2018", required=False)
parser.add_argument("--dirTypes",type=str, default="", help="Comma separated list of dirTypes to run. Ex: Signal,Data", required=False)
parser.add_argument("--note",type=str, default="HHWWggAnalysis", help="Note for ext variable", required=False)
parser.add_argument("--HH_limit", action="store_true", default=False, help="Plot HH limits", required=False)
parser.add_argument("--Run2", action="store_true", default=False, help="Compute combined Run 2 limits ", required=False)
parser.add_argument("--combineAll", action="store_true", default=False, help="Compute limits from all inputs combined", required=False)
parser.add_argument("--combineInd", action="store_true", default=False, help="Compute limits for individual cases", required=False)

args = parser.parse_args()

ntupleDirec = "/eos/user/a/atishelm/ntuples"
baseDirec = "HHWWgg_Combination"
outputDirec = "/eos/user/a/atishelm/www/HHWWgg/Combination"
note = args.note 
mode = args.mode 

##-- Get Loop params 
loopParams = ["physicsCases","finalStates","years","dirTypes"]
for loopParam in loopParams:
  exec("%s = args.%s.split(',')"%(loopParam,loopParam))
  exec("print'%s:',%s"%(loopParam,loopParam))

##-- Setup For Combine Step
if(args.Step=="Combine"): 
  # For each case X finalState X year, setup datacard, signal and background model locations
  os.system('mkdir -p Combine/%s'%(args.note))
  os.system('mkdir -p Combine/%s/Models'%(args.note))

##-- Run steps for each case 
if(args.Step!="Plot"):
  for physicsCase in physicsCases:
    for finalState in finalStates:
      for year in years:
        direc = "%s/%s/%s/%s"%(baseDirec,physicsCase,finalState,year)
        for dirType in dirTypes: 
          FitDir = GetFitDirec(dirType)
          if(args.Step=="Datacard"): 
            fullDirec = "%s_Signal"%(direc)
            inputWSDir = "%s/%s_Signal"%(ntupleDirec,direc)
          else: 
            fullDirec = "%s_%s"%(direc,dirType)
            inputWSDir = "%s/%s_%s"%(ntupleDirec,direc,dirType)

          if(args.Step=="Combine"): 
            # print"physics Case: ",physicsCase
            # print"finalState: ",finalState
            # print"year: ",year 
            # print"note: ",note 
            # For each case X finalState X year, setup datacard, signal and background model locations
            ext = "HHWWgg_%s-%s_%s_%s"%(physicsCase,finalState,year,note)
            FinalStateParticles = GetFinalStateParticles(finalState)
            # print"FinalStateParticles:",FinalStateParticles
            os.chdir('Combine')
            os.system('mkdir -p Models/%s'%(ext))
            os.system('cp ../Signal/outdir_%s_nodeSM_HHWWgg_%s/CMS-HGG_mva_13TeV_sigfit.root ./Models/%s/CMS-HGG_mva_13TeV_sigfit.root'%(ext,FinalStateParticles,ext))
            os.system('cp ../Background/CMS-HGG_multipdf_%s.root ./Models/%s/CMS-HGG_mva_13TeV_multipdf.root'%(ext,ext))
            os.system('cp ../Datacard/%s_%s_datacards/Datacard_13TeV_%s_nodeSM_HHWWgg_%s_cleaned.txt CMS-HGG_mva_13TeV_datacard_%s.txt'%(ext,args.note,ext,FinalStateParticles,ext))
            
            ##-- Add branching ratios to data card in form of rateParam
            # https://pdglive.lbl.gov/Particle.action?node=S043&init=0
            SL_BR = 0.4411
            FH_BR = 0.4544
            FL_BR = 0.1071
            datacardName = "CMS-HGG_mva_13TeV_datacard_%s.txt"%(ext)
            print "Creating datacard: ",datacardName
            datacard = open(datacardName,'a')
            datacard.write('\n')
            if(finalState == "SL"):
              datacard.write("br_WW_qqlnu rateParam HHWWggTag_0_%s GluGluToHHTo %s\n"%(year,SL_BR))
              datacard.write("br_WW_qqlnu rateParam HHWWggTag_1_%s GluGluToHHTo %s\n"%(year,SL_BR))
              datacard.write("nuisance edit freeze br_WW_qqlnu\n")
            elif(finalState == "FL"):
              datacard.write("br_WW_lnulnu rateParam HHWWggTag_3_%s GluGluToHHTo %s\n"%(year,FL_BR))
              datacard.write("nuisance edit freeze br_WW_lnulnu\n")            
            elif(finalState == "FH"):
              datacard.write("br_WW_qqqq rateParam HHWWggTag_2_%s GluGluToHHTo %s\n"%(year,FH_BR))
              datacard.write("nuisance edit freeze br_WW_qqqq\n")                  
            else: 
              print "Final state is not SL FL or FH. It's: %s"%(finalState)
              os.chdir('..')
              exit(1)
            os.chdir('..')

          else: 
            script = open('%s_Config_TEMPLATE.txt'%(FitDir)).read()
            cats = FinalStateCats(finalState)
            ext = "HHWWgg_%s-%s_%s_%s"%(physicsCase,finalState,year,note)
            configParams = GetConfigParams(dirType)
            FinalStateParticles = GetFinalStateParticles(finalState)

            if(dirType=="Signal" or dirType=="Datacard"):
              analysis_type = GetAnalysisType(physicsCase) ##-- get analysis type from physics case 
              usrprocs = GetUsrProcs(physicsCase)

            for param in configParams:
              exec("script = script.replace('{%s}',%s)"%(param,param))

            # print"script:"
            # print script

            scriptName = "%s_Config.py"%(ext)

            with open(scriptName, "w") as outScript:
              outScript.write(script)
            
            if(args.Step=="Datacard"):
              os.system('mv %s Configs'%(scriptName))
              os.system('python RunCombineScripts.py --inputConfig Configs/%s'%(scriptName))
            else: 
              os.system('mv %s %s/Configs'%(scriptName,FitDir))
              os.chdir('%s'%(FitDir))          
              os.system('python Run%sScripts.py --inputConfig Configs/%s'%(FitDir,scriptName))

            if(args.Step != "Datacard"):
              outDirec = '%s/%s/%s'%(outputDirec,ext,mode)
              os.system('mkdir -p %s'%(outDirec))
              os.system('cp %s/index.php %s/%s '%(outputDirec,outputDirec,ext))
              os.system('cp %s/index.php %s'%(outputDirec,outDirec))          
              plotDirs = GetPlotDir(mode)
              for plotDir in plotDirs: 
                if(dirType=="Signal"):
                  os.system('cp outdir_%s_nodeSM_HHWWgg_%s/%s/*.png %s'%(ext,FinalStateParticles,plotDir,outDirec))
                  os.system('cp outdir_%s_nodeSM_HHWWgg_%s/%s/*.pdf %s'%(ext,FinalStateParticles,plotDir,outDirec))
                else: 
                  os.system('cp outdir_%s/%s/*.png %s'%(ext,plotDir,outDirec))
                  os.system('cp outdir_%s/%s/*.pdf %s'%(ext,plotDir,outDirec))  
              if(dirType=="Signal"):
                sigExt = "%s_nodeSM_HHWWgg_%s"%(ext,FinalStateParticles)
                for cat in cats.split(','):
                # copy outfiles so they can be picked up by background plots 
                  sigExtwTag = "%s_%s"%(sigExt,cat)
                  os.system('cp outdir_%s/CMS-HGG_sigfit_%s.root outdir_%s/CMS-HGG_sigfit_%s.root'%(sigExt,sigExt,sigExt,sigExtwTag))
              if(FitDir!="Combine"): os.chdir('..')

if(args.Step=="Combine"): 
  # run all possible combine combinations 
  # Columns: year --> Run 2 
  # Rows: SL, FH, FL --> Combine 
  os.chdir('Combine')
  command = "combineCards.py "
  datacards = []
  
  ##-- Individual limits 
  if(args.combineInd):
    for physicsCase in physicsCases:
      for ifs,finalState in enumerate(finalStates):
        for iy,year in enumerate(years):
          if(iy==len(years)-1 and ifs == len(finalStates)-1): 
            print "Skipping:"
            print year 
            print finalState
            continue 
          # print"combine final state:",finalState
          # print"combine year:",year
          ext = "HHWWgg_%s-%s_%s_%s"%(physicsCase,finalState,year,note)
          dCardName = "CMS-HGG_mva_13TeV_datacard_%s"%(ext)
          dCardtxt = "%s.txt"%(dCardName)
          dCardWorkspace = "%s.root"%(dCardName)
          datacards.append(dCardtxt)
          print "Computing limits for %s ..."%(ext)
          # print "Using datacard: %s"%(dCardWorkspace)
          # os.system('text2workspace.py %s'%(dCardtxt))
          # os.system('combine -M AsymptoticLimits -m 125 --freezeParameters allConstrainedNuisances --expectSignal 1 --cminDefaultMinimizerStrategy 0 -d %s --run blind -t -1'%(dCardWorkspace))
          # os.system('combine %s -m 125 -M AsymptoticLimits --run=blind'%(dCardWorkspace))
          combineCommand = 'combine %s -m 125 -M AsymptoticLimits --run=blind'%(dCardtxt)
          # combineCommands.append(combineCommand)
          # print "combine Command: ",combineCommand
          os.system(combineCommand)
          # os.system('rm higgsCombineTest.AsymptoticLimits.mH125.root')
          # subprocess.call(combineCommand, shell=True)
          os.system('mv higgsCombineTest.AsymptoticLimits.mH125.root Limits/%s_limits.root'%(ext))

  # for com in combineCommands:
    # os.chdir('..')
    # os.chdir('Combine')
    # os.system(com)

  if(args.Run2):
    ##-- Run 2 Limits 
    for physicsCase in physicsCases:
      for ifs,finalState in enumerate(finalStates):
        run2_datacards = []

        for year in years:
          # run2_datacards = []
          ext = "HHWWgg_%s-%s_%s_%s"%(physicsCase,finalState,year,note)
          dCardName = "CMS-HGG_mva_13TeV_datacard_%s"%(ext)
          # dCard = "CMS-HGG_mva_13TeV_datacard_%s.txt"%(ext)
          dCardtxt = "%s.txt"%(dCardName)
          dCardWorkspace = "%s.root"%(dCardName)
          run2_datacards.append(dCardtxt)

        if(ifs==len(finalStates)-1): 
          print "Skipping"
          print finalState
          continue 
        print "Computing Full Run 2 limits for final state: %s"%(finalState)

        run2_ext = "HHWWgg_%s-%s_%s_%s"%(physicsCase,finalState,"Run2",note)
        run2_command = "combineCards.py "
        for run2_datacard in run2_datacards: run2_command += ' %s '%(run2_datacard)
        run2_datacardName_txt = "run2_datacard_%s.txt"%(finalState)
        run2_datacardName_root = "run2_datacard_%s.root"%(finalState)
        run2_command += " >> %s "%(run2_datacardName_txt)
        print"run2 combine command: ",run2_command
        os.system('rm %s'%(run2_datacardName_txt))
        os.system('rm %s'%(run2_datacardName_root))
        os.system(run2_command)
        os.system('text2workspace.py %s'%(run2_datacardName_txt))
        # os.system('combine -M AsymptoticLimits -m 125 --freezeParameters allConstrainedNuisances --expectSignal 1 --cminDefaultMinimizerStrategy 0 -d %s --run blind -t -1'%(run2_datacardName_root))
        os.system('combine %s -m 125 -M AsymptoticLimits --run=blind'%(run2_datacardName_root))
        os.system('mv higgsCombineTest.AsymptoticLimits.mH125.root Limits/%s_limits.root'%(run2_ext))

          # print "Computing limits for %s ..."%(ext)
          # os.system('text2workspace.py %s'%(dCardtxt))
          # os.system('combine -M AsymptoticLimits -m 125 --freezeParameters allConstrainedNuisances --expectSignal 1 --cminDefaultMinimizerStrategy 0 -d %s --run blind -t -1'%(dCardWorkspace))
          # os.system('combine %s -m 125 -M AsymptoticLimits --run=blind'%(dCard))
          # os.system('mv higgsCombineTest.AsymptoticLimits.mH125.root Limits/%s_limits.root'%(ext))

  # ##-- Channel Combined Limits 
  # for physicsCase in physicsCases:
  #   for finalState in finalStates:
  #     for year in years:
  #       ext = "HHWWgg_%s-%s_%s_%s"%(physicsCase,finalState,year,note)
  #       dCardName = "CMS-HGG_mva_13TeV_datacard_%s"%(ext)
  #       # dCard = "CMS-HGG_mva_13TeV_datacard_%s.txt"%(ext)
  #       dCardtxt = "%s.txt"%(dCardName)
  #       dCardWorkspace = "%s.root"%(dCardName)
  #       print "Computing limits for %s ..."%(ext)
  #       os.system('text2workspace.py %s'%(dCardtxt))
  #       os.system('combine -M AsymptoticLimits -m 125 --freezeParameters allConstrainedNuisances --expectSignal 1 --cminDefaultMinimizerStrategy 0 -d %s --run blind -t -1'%(dCardWorkspace))
  #       # os.system('combine %s -m 125 -M AsymptoticLimits --run=blind'%(dCard))
  #       os.system('mv higgsCombineTest.AsymptoticLimits.mH125.root Limits/%s_limits.root'%(ext))

  if(args.combineAll):
    datacards = [] 
    for finalState in finalStates:
      for year in years:   
        ext = "HHWWgg_%s-%s_%s_%s"%(physicsCase,finalState,year,note)
        dCardName = "CMS-HGG_mva_13TeV_datacard_%s"%(ext)
        dCardtxt = "%s.txt"%(dCardName)        
        datacards.append(dCardtxt)
    for datacard in datacards: command += " %s "%(datacard)
    command += " >> Datacard_Combined.txt "

    print "For full combination, run these commands:"
    print "1) cd Combine"
    print "2)",command 
    print "3) text2workspace.py Datacard_Combined.txt"
    print "4) combine Datacard_Combined.txt -m 125 -M AsymptoticLimits --run=blind"
    # print "Command: ",command
    # print "Computing combined limit..."
    # print "Command: ",command
    # # os.chdir('Combine')

    # os.system('rm Datacard_Combined.txt')
    # os.system('rm higgsCombineTest.AsymptoticLimits.mH125.root')

    # os.system(command)
    # os.system('text2workspace.py Datacard_Combined.txt')
    # os.system('combine -M AsymptoticLimits -m 125 --freezeParameters allConstrainedNuisances --expectSignal 1 --cminDefaultMinimizerStrategy 0 -d Datacard_Combined.root --run blind -t -1')
    # os.system('combine Datacard_Combined.txt -m 125 -M AsymptoticLimits --run=blind')
    
  # https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit/issues/543  ##-- Object is duplicated info -- should be ok 

    # os.system('combine Datacard_Combined.txt -m 125 -M AsymptoticLimits --run=blind')
    # # os.system('combine DataCard_Combined.txt -m 125 -M AsymptoticLimits --run=blind')
    # os.system('combine -M AsymptoticLimits -m 125 --freezeParameters allConstrainedNuisances --expectSignal 1 --cminDefaultMinimizerStrategy 0 -d DataCard_Combined.txt --run blind -t -1')
    # # os.system('mv higgsCombineTest.AsymptoticLimits.mH125.root Limits/limits.root')

  # os.chdir('..')

if(args.Step=="Plot"): 
  os.chdir('Combine')
  print "Creating limit table ..."
  CreateLimitTable(args.HH_limit)
  PlotLimitBands()
  os.chdir('..')
