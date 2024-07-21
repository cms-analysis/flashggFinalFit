# Script for running background fitting jobs for flashggFinalFit

from optparse import OptionParser
from collections import OrderedDict as od
from tools import *
import numpy as np
import os
import concurrent.futures
from biasUtils import *
import os
from optparse import OptionParser
from submissionTools import writeCondorSub


# Import tools

from commonTools import *
from commonObjects import *

import ROOT as r
r.gROOT.SetBatch(True)
r.gStyle.SetOptStat(2211)

def get_options():
  parser = OptionParser()
  parser.add_option('--step', dest='step', default='Fit', help="Toy or Fit")
  parser.add_option('--nToys', dest='nToys', default='100', help="Create a number of Toys")
  parser.add_option('--ext', dest='ext', default='24_06_04', help="Estensione che vuoi per i jobs")
  parser.add_option('--poi', dest='poi', default='muf', help="parameter of interest")
  parser.add_option('--expectSignal', dest='expectSignal', default=0, help="expectSignal")
  parser.add_option('--printOnly', dest='printOnly', default=False, action="store_true", help="Dry run: print submission files only")
  return parser.parse_args() 
(opt,args) = get_options()

print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ RUNNING TOYS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
def leave():
  print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ RUNNING TOYS (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
  sys.exit(1)



toy_jobDir = "NominalToys_%s"%(opt.ext)
toy_outputDir = "/eos/home-f/fderiggi/AC/BiasStudy/Output"+toy_jobDir

fit_jobDir = "NominalFits_%s_%s"%(opt.ext, opt.poi) 
fit_outputDir = "/eos/home-f/fderiggi/AC/BiasStudy/Output_NominalFits_%s_%s"%(opt.ext, opt.poi )




if opt.step == "Toy":
 
  cmdLine = "mkdir -p  %s"%(toy_jobDir)
  run(cmdLine)

  cmdLine = "mkdir -p  %s"%(toy_outputDir )
  run(cmdLine)
  _executable = "sub_%s"%(opt.ext)

 

  _subcmd = 'bsub' 


  _f = open("%s/Toys.txt"%(toy_jobDir),"w")
  for n in range(eval(opt.nToys)):
      _cmd = "combine -m 125.3800 -d ../../Datacard_ALT_0M.root -M GenerateOnly  -s -1 --saveToys   -t 1 -n split%s --setParameters muV=1.,CMS_zz4l_fai1=0.,muf=1.,fa3_ggH=0. ;mv higgsCombine*split%s* %s_%s/biasStudy_split%s_toys.root"%(n,n,_outputDir,opt.ext,n)
      _f.write("%s\n"%_cmd)
  _f.close()

  writeSubFiles('OutputBias'+opt.step+'_Jobs',"%s/Toys.txt"%(toy_jobDir), batch = 'condor')

  print "  --> Finished submitting files"

elif opt.step == "Fit":

  cmdLine = "mkdir -p  %s"%(fit_jobDir)
  run(cmdLine)
  _executable = "sub_%s"%(opt.ext)
  cmdLine = "mkdir -p  %s"%(fit_outputDir)
  run(cmdLine)

  FToy = os.listdir(toy_outputDir)

  _f = open("%s/Fit_%s.txt"%(fit_jobDir,opt.poi),"w")



  for i,f in enumerate(FToy):
      if not (i > 100 and i < 200)  : continue
      _cmd = "combine -m 125.3800 -d ../../Datacard_ALT_0M.root -M MultiDimFit -P %s --algo singles  --floatOtherPOIs 1  --redefineSignalPOIs muV,muf,fa3_ggH,fa3_ggH,CMS_zz4l_fai1  --setParameters muV=1.,CMS_zz4l_fai1=0.,muf=1.,fa3_ggH=0. --robustFit=1 --setRobustFitAlgo=Minuit2,Migrad  --X-rtd FITTER_NEW_CROSSING_ALGO  --setRobustFitTolerance=0.5 --X-rtd FITTER_NEVER_GIVE_UP --X-rtd FITTER_BOUND --cminFallbackAlgo Minuit2,0:1.  --saveInactivePOI 1  --saveWorkspace --cminDefaultMinimizerStrategy 0  --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants  --X-rtd MINIMIZER_multiMin_maskConstraints  --X-rtd MINIMIZER_multiMin_maskChannels=2  --setParameterRanges muV=0.0,4.0:muf=0.0,10.0:fa3_ggH=-0.5.,0.5.:CMS_zz4l_fai1=-0.001.,0.001  -t 1 -n _%ssplit%s_  --toysFile=%s/%s; mv higgsCombine*_%ssplit%s_* %s/biasStudy_split%s_fits.root"%(opt.poi,opt.poi,i,toy_outputDir,f,opt.poi,i,fit_outputDir,i)
     # _cmd = "combine -m 125.3800 -d ../../Datacard_ALT_0M.root -M MultiDimFit -P %s --algo singles  --floatOtherPOIs 1  --redefineSignalPOIs muV,muf,fa3_ggH,fa3_ggH,CMS_zz4l_fai1  --setParameters muV=1.,CMS_zz4l_fai1=0.,muf=1.,fa3_ggH=0.,n_exp_binRECO_WH_LEP_Tag0_proc_bkg_mass=4 --robustFit=1 --setRobustFitAlgo=Minuit2,Migrad  --X-rtd FITTER_NEW_CROSSING_ALGO  --setRobustFitTolerance=0.5 --X-rtd FITTER_NEVER_GIVE_UP --X-rtd FITTER_BOUND --cminFallbackAlgo Minuit2,0:1.  --saveInactivePOI 1  --saveWorkspace --cminDefaultMinimizerStrategy 0  --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants  --X-rtd MINIMIZER_multiMin_maskConstraints  --X-rtd MINIMIZER_multiMin_maskChannels=2  --setParameterRanges muV=0.0,4.0:muf=0.0,10.0:fa3_ggH=-0.5.,0.5.:CMS_zz4l_fai1=-0.001.,0.001  -t 1 -n _%ssplit%s_  --toysFile=%s/%s; mv higgsCombine*_%ssplit%s_* %s/biasStudy_split%s_fits.root"%(opt.poi,opt.poi,i,toy_outputDir,f,opt.poi,i,fit_outputDir,i)
      _f.write("%s\n"%_cmd)

     

  _f.close()
  writeSubFiles('OutputBias'+opt.step+'_Jobs_%s'%(opt.poi),"%s/Fit_%s.txt"%(fit_jobDir,opt.poi), batch = 'condor')
     

elif opt.step == "Plot":

  #_outputDir_Fit =['Output_NominalFits_24_06_04/biasStudy_split455_fits.root']

 
  
  label_dict = {"muf":r'\frac{2(\mu_{V}-1)}{\sigma^{+} + \sigma^{-}} ' ,
                "muV":r'\frac{2(\mu_{f}-1)}{\sigma^{+} + \sigma^{-}} ' ,
                "CMS_zz4l_fai1":r'\frac{2f_{a3}}{\sigma^{+} + \sigma^{-}} '}

  label_color = {"CMS_zz4l_fai1":ROOT.kMagenta-9,
  "muf":ROOT.kAzure+8,
  "muV":ROOT.kOrange+6}

  pullHist = r.TH1F(' ', ' ', 20, -5., 5.)
  pullHist.GetXaxis().SetTitle(label_dict[opt.poi])
  pullHist.GetYaxis().SetTitle('Entries')
  pullHist.GetXaxis().SetTitleOffset(1.)


 
  print(fit_outputDir)


  for i,FitFile in enumerate(os.listdir(fit_outputDir)):
        

        tfile = r.TFile(fit_outputDir +'/'+FitFile)
        #tfile = r.TFile(FitFile )
         
        tree = tfile.Get('limit')

        tree.GetEntry(0)
        if not getattr(tree,'quantileExpected')==-1: 
                #raiseFailError(itoy,True) 
                continue
        bf = getattr(tree, opt.poi)
   
        tree.GetEntry(1)
        if not abs(getattr(tree,'quantileExpected')--0.32)<0.001: 
                raiseFailError(itoy,True) 
                continue
        lo = getattr(tree, opt.poi)

        tree.GetEntry(2)
        if not abs(getattr(tree,'quantileExpected')-0.32)<0.001: 
                raiseFailError(itoy,True) 
                continue
     
        hi = getattr(tree, opt.poi)
        diff = bf - eval(opt.expectSignal)
        unc = 0.5 * (hi-lo)
        mean = []
        if unc > 0.: 
            if abs(diff/unc)< 0.05 : print(diff/unc, fit_outputDir +'/'+FitFile)
            pullHist.Fill(diff/unc)
     
        
            mean.append(diff/unc)
        if  unc == 0.: print("")
             #print(unc, _outputDir_Fit +'/'+FitFile)


  pullHist.SetFillColor(label_color[opt.poi])
  pullHist.SetLineColor(label_color[opt.poi])
  pullHist.SetLineWidth(2)
  print("mean calcolata senza gaussiana = %s"%(sum(mean)/len(mean)))      
  canv = r.TCanvas()
  canv.SetBottomMargin(0.15);
  pullHist.Draw()
  
  r.gStyle.SetOptFit(11111)
  pullHist.Fit('gaus')
  canv.SaveAs('BiasStudy_%s.pdf'%(opt.poi))
  canv.SaveAs('BiasStudy_%s.png'%(opt.poi))

 


   
