#!/usr/bin/env python
# Simple script to make Effiency X Acceptance plot from Binned Baseline/Massfac analysis
# run with python makeEffAcc.py CMS-HGG.root
import ROOT as r
import sys
import re
import string
import random
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
   return ''.join(random.choice(chars) for _ in range(size))
###############################################################################
##  Get Systematics ########################################################
###############################################################################
#individual numbers for each proc/cat
def getStatError(dataVector,inWS):
  th1f = r.TH1F("dummy","dummy",1,110,150)
  th1f.Sumw2()
  mass = inWS.var("CMS_hgg_mass")
  weight = r.RooRealVar("weight","weight",0)
  for data in dataVector:
    for i in range(0,int(data.numEntries())):
      mass.setVal(data.get(i).getRealValue("CMS_hgg_mass"))
      w_nominal =data.weight()
      th1f.Fill(mass.getVal(),w_nominal)
      #print "CHECK data " , "suEntries", data.sumEntries(), " numEntries" ,data.numEntries()
      #print "CHECK Th1F " , "suEntries", th1f.Integral(), " numEntries", th1f.GetEntries()
  #for j in range(0,th1f.GetNbinsX()):
    #print "CHECK Th1F " , "statError in bin  ", j, " == " , th1f.GetBinError(j)

  return th1f.GetBinError(0) 

def getSystHisto(proc,cat,syst,mass,inWS):
  printDetails=(proc=="tth")
  asymmetric=False 
  eventweight=False
  dataSYMMETRIC=None
  dataDOWN=None
  dataUP=None
  dataNOMINAL=None
  isWeight = None
  isWeight = inWS.var("%sUp01sigma"%syst)
  dataNOMINAL =  inWS.data("%s_%d_13TeV_%s"%(proc,mass,cat)) #Nominal RooDataSet,. May contain required weights if UP/DOWN/SYMMETRIC roodatahists do not exist (ie systematic stored as event weigths)
  print "DEBUG 1 dataNOMINAL"
  dataNOMINAL.Print()
  if (isWeight ==None):
    print "===========> SYST notWeight ", syst ," PROC ", proc , ", TAG ", cat
    dataDOWN =  inWS.data("%s_%d_13TeV_%s_%sDown01sigma"%(proc,mass,cat,syst)) # will exist if teh systematic is an asymetric uncertainty not strore as event weights
    print "DEBUG 1 dataDOWN"
    dataDOWN.Print()

    dataUP =  inWS.data("%s_%d_13TeV_%s_%sUp01sigma"%(proc,mass,cat,syst))# will exist if teh systematic is an asymetric uncertainty not strore as event weights
    print "DEBUG 1 dataUP"
    dataUP.Print()
    if (dataDOWN==None): dataSYMMETRIC =  inWS.data("%s_%d_13TeV_%s_%s"%(proc,mass,cat,syst)) #Will exist if the systematic is a symmetric uncertainty not stored as event weights
  #print " ", ("%s_125_13TeV_%s_%s"%(proc,cat,syst))," ", dataSYMMETRIC, "data==None" , (dataSYMMETRIC==None), " data is None ", (dataSYMMETRIC is None)
  #print " ", ("%s_125_13TeV_%s"%(proc,cat)) ," ",  dataNOMINAL, "data==None" , (dataNOMINAL==None), " data is None ", (dataNOMINAL is None)
  #print "  ", ("%s_125_13TeV_%s_%sDown01sigma"%(proc,cat,syst)), " ", dataDOWN, "data==None" , (dataDOWN==None), " data is None ", (dataDOWN is None)
  #print " ", ("%s_125_13TeV_%s_%sUp01sigma"%(proc,cat,syst)), " ", dataUP, "data==None" , (dataUP==None), " data is None ", (dataUP is None)
  if (dataSYMMETRIC==None):
    if( (dataUP==None) or  (dataDOWN==None)) :
      #print "[INFO] Systematic ", syst," stored as asymmetric event weights in RooDataSet"
      asymmetric=True
      eventweight=True
    else:
      #print "[INFO] Systematic ", syst," stored as asymmetric rooDataHists"
      asymmetric=True
      eventweight=False
  else:
      #print "[INFO] Systematic ", syst," stored as symmetric rooDataHist"
      asymmetric=False
      eventweight=False
  
  if (asymmetric and eventweight) : 
    data_up = dataNOMINAL.emptyClone()
    data_down = dataNOMINAL.emptyClone()
    data_nom_new = dataNOMINAL.emptyClone()
    mass = inWS.var("CMS_hgg_mass")
    weight = r.RooRealVar("weight","weight",0)
    weight_up = inWS.var("%sUp01sigma"%syst)
    #weight_down = inWS.var("%sDown01sigma"%sys)
    weight_down = r.RooRealVar("%sDown01sigma"%syst,"%sDown01sigma"%syst,-1.)
    weight_central = inWS.var("centralObjectWeight")
    #print "mass ", mass," weight_up ", weight_up , " weight_down ", weight_down , " data_up ", data_up, " data_down ", data_down
    zeroWeightEvents=0.
    for i in range(0,int(dataNOMINAL.numEntries())):
      mass.setVal(dataNOMINAL.get(i).getRealValue("CMS_hgg_mass"))
      w_nominal =dataNOMINAL.weight()
      #print " w_down components dataNOMINAL ", dataNOMINAL , " weight_down ", weight_down , "weight_down.name() ", weight_down.GetName() 
      #w_down = dataNOMINAL.get(i).getRealValue(("%sDown01sigma"%syst))
      #print " mass, ", mass, " w_nominal " , w_nominal , " w down ", w_down , "test ", (("%sDown01sigma"%syst))
      #sys.exit(1) 
      w_down = dataNOMINAL.get(i).getRealValue(weight_down.GetName())
      w_up = dataNOMINAL.get(i).getRealValue(weight_up.GetName())
      w_central = dataNOMINAL.get(i).getRealValue(weight_central.GetName())
      if (w_central==0.) :
        zeroWeightEvents=zeroWeightEvents+1.0
        if (zeroWeightEvents%1000==0):
          print "[WARNING] skipping one event where weight is identically 0, causing  a seg fault, occured in ",(zeroWeightEvents/dataNOMINAL.numEntries())*100 , " percent of events"
          print "[WARNING]  syst " , syst , " w_nom ", w_nominal , "  w_up " , w_up , " w_ down " , w_down, "w_central ", w_central 
        continue
      weight_down.setVal(w_nominal*(w_down/w_central))
      weight_up.setVal(w_nominal*(w_up/w_central))
    #  print "mass ", mass," weight_up ", weight_up , " weight_down ", weight_down , " data_up ", data_up, " data_down ", data_down
      data_up.add(r.RooArgSet(mass,weight_up),weight_up.getVal())
      data_down.add(r.RooArgSet(mass,weight_down),weight_down.getVal())
      data_nom_new.add(r.RooArgSet(mass,weight),w_nominal)
    #print "dataNOMINAL " , dataNOMINAL.sumEntries()
    #print "data_up ", data_up.sumEntries()
    #print "data_down ", data_down.sumEntries()
    dataUP =  data_up  #repalce UP/DOwn histograms defined outside scope of this "if"
    dataDOWN =  data_down  #repalce UP/DOwn histograms defined outside scope of this "if"
    dataNOMINAL =  data_nom_new  #repalce UP/DOwn histograms defined outside scope of this "if"
    #if (printDetails) :
    print "LC DEBUG DATASET DETAILS"
    dataUP.Print()
    dataNOMINAL.Print()
    dataDOWN.Print()

  return [dataUP, dataNOMINAL, dataDOWN]
###############################################################################
## WSTFileWrapper  ############################################################
###############################################################################

class WSTFileWrapper:
   #self.fnList = [] # filename list
   #self.fileList = [] #file list
   #self.wsList = [] #workspace list

   def __init__(self, files,wsname):
    self.fnList = files.split(",") # [1]       
    self.fileList = []
    self.wsList = [] #now list of ws names...
    #print files
    for fn in self.fnList: # [2]
        #print fn
        f = r.TFile.Open(fn) 
        self.fileList.append(f)
        #print " debug r.TFile.Open(fn) ", r.TFile.Open(fn)
        thing = f.Get(wsname)
        #print "r.RooWorkspace(self.fileList[-1].Get(wsname) " , thing
        #self.wsList.append(r.RooWorkspace(thing))
        self.wsList.append(self.fileList[-1].Get(wsname))
        #self.wsList.append(wsname)
        #print self.wsList
        f.Close()

   def data(self,dataName):
        result = None
        complained_yet =0 
        for i in range(len(self.fnList)):
          #f = r.TFile.Open(self.fnList[i])  
          this_result_obj = self.wsList[i].data(dataName);
          #print "this_result_obj = f.Get(%s).data(%s) "%(self.wsList[i],dataName);
          #this_ws=f.Get(self.wsList[i])
          #print this_ws 
          #this_result_obj = this_ws.data(dataName);
          if ( result and this_result_obj and (not complained_yet) ):
            print "[WSTFileWrapper] Uh oh, multiple RooAbsDatas from the file list with the same name: ",  dataName 
            complained_yet = true;
            exit(1)
          if this_result_obj: # [3]
             result = this_result_obj
            # print "[WSTFileWrapper]  YES Successfully found the RooAbsData with name ",  dataName 
                      #   [ ... straightforward checks for multiple results etc ... ]
        #if (not result) :
              #print "[WSTFileWrapper] Uh oh, never got a good RooAbsData with name " ,dataName 
        return result 
   
   def var(self,varName):
        result = None
        complained_yet =0 
        for i in range(len(self.fnList)):
          this_result_obj = self.wsList[i].var(varName);
         # if ( result and this_result_obj and (not complained_yet) ):
         #   print "[WSTFileWrapper] Uh oh, multiple RooAbsDatas from the file list with the same name: ",  dataName 
         #   complained_yet = true;
          if this_result_obj: # [3]
             result = this_result_obj
                      #   [ ... straightforward checks for multiple results etc ... ]
          #if (not result) :
              #print "[WSTFileWrapper] Uh oh, never got a good RooRealData with name " ,varName 
                
        return result 


###############################################################################

procOrder=('ggh', 'vbf', 'wzh', 'wh', 'zh', 'tth')

adHocFactors={
  'ggh': 1.0,
  'vbf': 1.0,
  'wzh': 1.0,
  'wh': 1.0,
  'zh': 1.0,
  'tth': 1.0,
}


def preFlight(f):
  foundSplit = foundMerged = False
  procs = set()
  masses = set()
  cats = set()
  for i in f.GetListOfKeys():
    match = re.search('sig_(?P<proc>\w+)_mass_m(?P<mass>[0-9]*\.?[0-9]+)_.*_cat(?P<cat>[0-9]+)$', i.GetName())
    if match:
      d = match.groupdict()
      float(d['mass'])
      procs.add(d['proc'])
      masses.add(d['mass'])
      cats.add(d['cat'])

  if 'wzh' in procs and ('wh' in procs or 'zh' in procs) :
    raise RuntimeError('Bailing out: found both wh/zh and wzh in '+f.GetName())

  massesRet = sorted([ float(m) for m in masses ])
  catsRet = sorted([ int(cat) for cat in cats ])
  procsRet = sorted(procs, key=lambda x: procOrder.index(x))
  return (procsRet, massesRet, catsRet)
  
  
def getSigHistos(ws, procs, suffix): #ok so they are not histos anymore but roodatasets
    mass = ws.var("CMS_hgg_mass")
  #  print "mass ", mass
  #  print " ROOT.RooCmdArg.none() " , r.RooCmdArg.none()
    #no = RooCmdArg
    #slurpDic ={}
    #for name in procs:
    #  print name+suffix
    #  step1 =ws.data(name+suffix)
    #  print "step1 ", step1
    #  slurpDic[name]=step1.binnedClone(name+suffix,name+suffix)

    #slurpDic = { name : ws.data(name+suffix).binnedClone(name+suffix,name+suffix) for name in procs}
    for name in procs:
      print "DEBUG getSigHistosws.data(name+suffix) ", ws.data(name+suffix)
      ws.data(name+suffix).Print()
    slurpDic = { name : ws.data(name+suffix) for name in procs}
    # filter out histos that are null pointers
    return { k : v for k, v in slurpDic.iteritems() if v }



#### r.gr.ProcessLine(".L Normalization_7TeV.C++")
### r.gr.ProcessLine(".L Normalization_8TeV.C++")
### from r import GetBR
### from r import GetXsection
### GetProcXsection = GetXsection
#print "debug1"
#r.gSystem.Load("libflashggFinalFitSignal")
r.gSystem.Load("Signal/lib/libSimultaneousSignalFit.so")
#print "debug2"
r.gSystem.Load("libHiggsAnalysisCombinedLimit")
#print "debug3"
from ROOT import Normalization_8TeV
#print "debug4"
norm = Normalization_8TeV()  # Should be checking if 7TeV or 8TeV signal, default is 8TeV here
#print "debug5"
#norm.Init(8)
GetBR = lambda x : norm.GetBR(float(x))
GetXsection = lambda x : norm.GetXsection(float(x))
GetProcXsection = lambda x,y : norm.GetXsection(x,y)

# r Setup
r.gROOT.SetStyle("Plain")
r.gROOT.SetBatch(1)

# Global Setup, Modify with each Reload
##### NCAT = 5
##### lumi = 5089
#lumi=3770
#systematics = ["vtxEff","idEff","E_scale","E_res","triggerEff","regSig","phoIdMva"] # These are the main contributions to eff*Acc
#systematics = ["vtxEff","idEff","E_scale","E_res","triggerEff"] # These are the main contributions to eff*Acc
systematics = ["TriggerWeight","MvaShift","MCScaleLowR9EB","MCScaleHighR9EB","MCScaleLowR9EE","MCScaleHighR9EE","MCSmearLowR9EB","MCSmearHighR9EB","MCSmearLowR9EE","MCSmearHighR9EE","FracRVWeight"] # These are the main contributions to eff*Acc
#systematics = ["TriggerWeight","MvaShift","MCScaleLowR9EB","MCScaleHighR9EB"] # These are the main contributions to eff*Acc
#systematics = ["MCScaleHighR9EB"] # These are the main contributions to eff*Acc
#systematics = ["MCScaleLowR9EE","MCScaleHighR9EE","MCSmearLowR9EB","MCSmearHighR9EB","MCSmearLowR9EE","MCSmearHighR9EE","FracRVWeight"] # These are the main contributions to eff*Acc
#systematics = [] # These are the main contributions to eff*Acc
## Masses = range(110,152,2) 
Masses = range(120,135,5) 
# -------------------------------------------------------------

#f = r.TFile(sys.argv[1])

#(procs, masses, cats) = preFlight(f)
procs=["ggh","vbf","wh","zh","tth"]
#procs=["ggh","vbf","wh","zh"] #tth is bugged for now
#procs=["tth"]
masses=[120.,125.,130.]
cats=["UntaggedTag_0","UntaggedTag_1","UntaggedTag_2","UntaggedTag_3","VBFTag_0","VBFTag_1","TTHLeptonicTag","TTHHadronicTag"]
#cats=["UntaggedTag_0"]
# Get The lumi from the workspace!
#ws = f.Get("tagsDumper/cms_hgg_13TeV")
sqrts = 13
ws = WSTFileWrapper(sys.argv[1],"tagsDumper/cms_hgg_%sTeV"%sqrts)
extraFile=sys.argv[2]
#if "root" in extraFile:
#print ws
#lRRV = ws.var("IntLumi")
lRRV = ws.var("IntLumi")
lumi = lRRV.getVal()
#lumi=2610
#sqrts = (ws.var("Sqrts")).getVal()
#print sqrts
norm.Init(int(sqrts))


# Some helpful output
print "File - ", sys.argv[1]
print 'Processes found:  ' + str(procs)
print 'Masses found:     ' + str(masses)
print 'Categories found: ' + str(cats)

#printLine = "Data:      "
#Sum = 0
#for i in cats:
#  h = f.Get("th1f_data_mass_cat%d"%i)
#  print "%d   %4.0f    %4.0f" % (i, h.Integral(1,160), h.Integral(21,100) )
#  Sum+=h.Integral()
#  printLine+="%3.0f"%(h.Integral())+" "
#printLine+="tot=%d"%Sum
#print printLine


efficiency=r.TGraphAsymmErrors()
efficiencyE0=r.TGraphErrors()
#efficiencyTH1=r.TH1F("t","t",10,120,130)
central=r.TGraphAsymmErrors()
efficiencyup=r.TGraphAsymmErrors()
efficiencydn=r.TGraphAsymmErrors()
centralsmooth=r.TGraphAsymmErrors()

fitstring = "[0] + [1]*x + [2]*x*x"
cenfunc = r.TF1("cenfunc",fitstring,109.75,140.25)
upfunc = r.TF1("upfunc",fitstring,109.75,140.25)
dnfunc = r.TF1("dnfunc",fitstring,109.75,140.25)

for point,M in enumerate(Masses):
#for point,M in enumerate(masses):
  printLine = "Signal M%3.1f: "%M
  Sum = 0
  dataVector= []
  for i in cats:
    if int(M)==M:
      suffix = '_%d_13TeV_%s'%(int(M),i)
      histos = getSigHistos(ws, procs, suffix)

      #integrals = { proc : h.Integral() for (proc, h) in histos.iteritems()}
      integrals = { proc : h.sumEntries() for (proc, h) in histos.iteritems()}
      print "integralsf for M ",M ," ", integrals

      procLine = 'cat %s, mH=%3.1f:'%(i, M)
      for proc in procs:
        integral = integrals[proc]
        #procLine += '   %s %.5f'% (proc, 100*integral/(GetBR(M)*( GetProcXsection(M,proc)*adHocFactors[proc] )*lumi) )
        procLine += '   %s %.5f'% (proc, integral )
      #print procLine

      hs = [ h for (proc, h) in histos.iteritems() ]
      for (proc,h) in histos.iteritems():
        dataVector.append(h)
      h=hs[0].emptyClone("dummy dataset"+str(id_generator()))
      
      #for j in hs[1:]:
      for j in hs:
        print "DEBUG LC this would be stupid before " 
        h.Print()
        h.append(j)
        print "DEBUG LC this would be stupid after" 
        h.Print()
      #test = getStatError(hs,ws) 
    #else:
    #
    #  h = f.Get("th1f_sig_mass_m%.1f_cat%d"%(M,i))
    
    #Sum += h.Integral()
    Sum += h.sumEntries()
    #printLine+="%3.5f "%h.Integral()
    printLine+="%3.5f "%h.sumEntries()
  printLine+="tot=%3.5f"%Sum
  
  xsecs = [ GetProcXsection(M,proc)*adHocFactors[proc] for proc in procs ]
  sm = GetBR(M) * sum(xsecs)
  #print xsecs
  
  effAcc = 100*Sum/(sm*lumi) # calculate Efficiency at mH
  #print "[INFO] effAcc setting point ", M, " with value ", effAcc , " = 100* ",Sum ,"/( ",GetBR(M), " * ", sum(xsecs)  ," * ",lumi ,")"
  centralsmooth.SetPoint(point,M,effAcc)
  central.SetPoint(point,M,effAcc)
  efficiency.SetPoint(point,M,effAcc)
  efficiencyE0.SetPoint(point,M,effAcc)
  #efficiencyTH1.Fill(M,effAcc)
  sigmaUp = 0
  sigmaDown = 0
  sigmaNom = 0
  for s in systematics:
    syssumup=0
    syssumnom=0
    syssumdn=0
    for cat in cats:
      for proc in procs:
         if int(M)==M:
          print "DEBUG pre-getSystHisto proc " , proc, " cat ", cat ,", s " ,s , " M ", M, " ws " , ws
          [hup,hnom,hdn]=getSystHisto(proc,cat,s,M,ws)
          #hdn=getSystHisto(proc,cat,s,ws)[1]
          print
          print "syst " , s , " cat ", cat ,", proc ", proc, "hup.sumEntries() ", hup.sumEntries()
          hup.Print()
          print "syst " , s , " cat ", cat ,", proc ", proc, "hnom.sumEntries() ", hnom.sumEntries() 
          hnom.Print()
          print "syst " , s , " cat ", cat ,", proc ", proc, "hdn.sumEntries() ", hdn.sumEntries()      
          hdn.Print()
          print
          syssumup+=hup.sumEntries()
          syssumnom+=hnom.sumEntries()
          syssumdn+=hdn.sumEntries()
          print "partial event yield for systematic ", s ," UP at mh=",M," is " ,syssumup, ", ", syssumnom,", ",syssumdn


    # We make 3-sigma templates so need to scale back by 1/3
    print "total event yield for systematic ", s ," UP at mh=",M," is " ,syssumup
    print "total event yield for systematic ", s ," NOM at mh=",M," is " ,syssumnom
    print "total event yield for systematic ", s ," DN at mh=",M," is " ,syssumdn
    #delUp+=abs(syssumup-Sum)
    #delDown+=abs(syssumdn-Sum)
    xplus= max(syssumup,syssumdn,syssumnom) -syssumnom
    xminus= min(syssumup,syssumdn,syssumnom) -syssumnom
    sigmaUp += xplus*xplus
    sigmaDown += xminus*xminus
    print "total event yield for systematic ", s ," xUp ", xplus, "xDown", xminus, " sigmaUp ", sigmaUp**0.5 , " sigmaDown ", sigmaDown**0.5
  


  sigmaUp=100*(sigmaUp**0.5)/(sm*lumi)
  sigmaDown=100*(sigmaDown**0.5)/(sm*lumi)
  efficiencyup.SetPoint(point,M,sigmaUp)
  efficiencydn.SetPoint(point,M,sigmaDown)
  centralsmooth.SetPointError(point,0,0,0,0)
  #sigma_N = 1/ (Sum)**0.5
  #sigma_N = getStatError(dataVector,ws) 
  #sigma_ea = 100 * sigma_N /(sm*lumi)
  print "Setting error of pt ", point , " to [",sigmaDown,",",sigmaUp,"]"
  efficiency.SetPointError(point,0,0,sigmaDown,sigmaUp)
  #efficiency.SetPointError(point,0,0,sigma_ea,sigma_ea)

  print printLine

#centralsmooth.Fit(cenfunc,"R,0,EX0","")
#efficiencyup.Fit(upfunc,"R,0,EX0","")
#efficiencydn.Fit(dnfunc,"R,0,EX0","")

#for point,M in enumerate(Masses):
#  central.SetPoint(point,M,cenfunc.Eval(M))
#  efficiency.SetPoint(point,M,cenfunc.Eval(M))

leg=r.TLegend(0.70,0.16,0.89,0.39)
leg.SetFillColor(0)
leg.SetBorderSize(0)
leg.AddEntry(central,"Higgs Signal #varepsilon #times Acc","L")
#leg.AddEntry(efficiency,"#pm 1 #sigma syst. error","F")
leg.AddEntry(efficiency,"#pm 1 #sigma syst. error","F")

mytext = r.TLatex()
mytext.SetTextSize(0.04)
mytext.SetNDC()

listy = []

MG=r.TMultiGraph()
can =None
can = r.TCanvas()

if ("root" in extraFile):
  print "got graph!"
  _file0 = r.TFile(extraFile)
  graph=r.TGraph(_file0.Get("effAccGraph"))
  graph.SetLineColor(r.kRed)
if (graph!=None): 
  print "drawign graph"
  for i in range (0,graph.GetN()): graph.GetY()[i] *= 100
  #graph.Draw("same")
else :
  print "not drawign graph"
efficiency.SetFillColor(r.kOrange)
efficiency.SetLineWidth(2)
central.SetLineWidth(2)
#central.SetMarkerSize(2)
central.SetMarkerColor(r.kBlack)
central.SetMarkerStyle(22)
MG.Add(efficiency)
MG.Add(central)
MG.Add(graph)
leg.AddEntry(graph,"Overal Signal Model","l")
MG.Draw("APL3")
MG.GetXaxis().SetTitle("m_{H} GeV")
MG.GetYaxis().SetTitle("Efficiency #times Acceptance - %")
mytext.DrawLatex(0.15,0.8,"CMS Simulation")
can.Update()
leg.Draw("same")
print "Int Lumi from workspace ", lumi
#raw_input("Looks OK?")

can.Update()
print "Saving plot as effAcc_vs_mass.pdf"
can.SaveAs("effAcc_vs_mass.pdf")
can.SaveAs("effAcc_vs_mass.png")
can.SaveAs("effAcc_vs_mass.root")

 
#(r.TVirtualFitter.GetFitter()).GetConfidenceIntervals(efficiencyE0)

#can2 = r.TCanvas()
#efficiencyE0.Draw("E0")
#can2.SaveAs("effAcc_vs_mass_E0.pdf")
  
