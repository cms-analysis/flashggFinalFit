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
  #dataNOMINAL.Print()
  if (isWeight ==None):
    dataDOWN =  inWS.data("%s_%d_13TeV_%s_%sDown01sigma"%(proc,mass,cat,syst)) # will exist if teh systematic is an asymetric uncertainty not strore as event weights
    #dataDOWN.Print()

    dataUP =  inWS.data("%s_%d_13TeV_%s_%sUp01sigma"%(proc,mass,cat,syst))# will exist if teh systematic is an asymetric uncertainty not strore as event weights
    #dataUP.Print()
    if (dataDOWN==None): dataSYMMETRIC =  inWS.data("%s_%d_13TeV_%s_%s"%(proc,mass,cat,syst)) #Will exist if the systematic is a symmetric uncertainty not stored as event weights
  if (dataSYMMETRIC==None):
    if( (dataUP==None) or  (dataDOWN==None)) :
      asymmetric=True
      eventweight=True
    else:
      asymmetric=True
      eventweight=False
  else:
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
    zeroWeightEvents=0.
    for i in range(0,int(dataNOMINAL.numEntries())):
      mass.setVal(dataNOMINAL.get(i).getRealValue("CMS_hgg_mass"))
      w_nominal =dataNOMINAL.weight()
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
    
    dataUP =  data_up  #repalce UP/DOwn histograms defined outside scope of this "if"
    dataDOWN =  data_down  #repalce UP/DOwn histograms defined outside scope of this "if"
    dataNOMINAL =  data_nom_new  #repalce UP/DOwn histograms defined outside scope of this "if"
    #if (printDetails) :
      #dataUP.Print()
      #dataNOMINAL.Print()
      #dataDOWN.Print()

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
        f = r.TFile.Open(fn) 
        self.fileList.append(f)
        thing = f.Get(wsname)
        self.wsList.append(self.fileList[-1].Get(wsname))
        f.Close()

   def convertTemplatedName(self,dataName):
        theProcName = ""
        theDataName = ""
        tpMap = {"GG2H":"ggh","VBF":"vbf","TTH":"tth","QQ2HLNU":"wh","QQ2HLL":"zh","WH2HQQ":"wh","ZH2HQQ":"zh"}
        for stxsProc in tpMap:
          if dataName.startswith(stxsProc):
            theProcName = stxsProc
            theDataName = dataName.replace(stxsProc,tpMap[stxsProc],1)
        return [theDataName,theProcName]

   def data(self,dataName):
        thePair = self.convertTemplatedName(dataName)
        newDataName = thePair[0]
        newProcName = thePair[1]
        result = None
        complained_yet = 0 
        for i in range(len(self.fnList)):
          if self.fnList[i]!="current file":
            if newProcName not in self.fnList[i] and newProcName!="": continue
            this_result_obj = self.wsList[i].data(newDataName);
            if ( result and this_result_obj and (not complained_yet) ):
              complained_yet = True;
            if this_result_obj: # [3]
               result = this_result_obj
        return result 
   
   def var(self,varName):
        result = None
        complained_yet =0 
        for i in range(len(self.fnList)):
          this_result_obj = self.wsList[i].var(varName);
          if this_result_obj: # [3]
             result = this_result_obj
        return result 


###############################################################################

#procOrder=('ggh', 'vbf', 'wzh', 'wh', 'zh', 'tth')
procOrder=('GG2H', 'VBF', 'TTH', 'QQ2HLNU', 'QQ2HLL', 'WH2HQQ', 'ZH2HQQ')

adHocFactors={
#  'ggh': 1.0,
#  'vbf': 1.0,
#  'wzh': 1.0,
#  'wh': 1.0,
#  'zh': 1.0,
#  'tth': 1.0,
  'GG2H': 1.0,
  'VBF': 1.0,
  'TTH': 1.0,
  'QQ2HLNU': 1.0,
  'QQ2HLL': 1.0,
  'WH2HQQ': 1.0,
  'ZH2HQQ': 1.0,
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
    for name in procs:
      #print " LOOKING FOR dataset %s%s"%(name,suffix)
      #ws.data(name+suffix).Print()
      print "name+suffix", name+suffix
      ws.data(name+suffix).Print()
    slurpDic = { name : ws.data(name+suffix) for name in procs}
    # filter out histos that are null pointers
    return { k : v for k, v in slurpDic.iteritems() if v }



r.gSystem.Load("Signal/lib/libSimultaneousSignalFit.so")
r.gSystem.Load("libHiggsAnalysisCombinedLimit")
from ROOT import Normalization_8TeV
norm = Normalization_8TeV()  # Should be checking if 7TeV or 8TeV signal, default is 13TeV
GetBR = lambda x : norm.GetBR(float(x))
GetXsection = lambda x : norm.GetXsection(float(x))
GetProcXsection = lambda x,y : norm.GetXsection(x,y)

r.gROOT.SetBatch(1)

# Global Setup, Modify with each Reload
systematics = ["TriggerWeight","MvaShift","MCScaleLowR9EB","MCScaleHighR9EB","MCScaleLowR9EE","MCScaleHighR9EE","MCSmearLowR9EBRho","MCSmearHighR9EBRho","MCSmearLowR9EERho","MCSmearHighR9EERho","MCSmearLowR9EBPhi","MCSmearHighR9EBPhi","MCSmearLowR9EEPhi","MCSmearHighR9EEPhi","FracRVWeight"] # These are the main contributions to eff*Acc
#systematics = ["TriggerWeight"] # These are the main contributions to eff*Acc
#systematics = ["FracRVWeight"] # These are the main contributions to eff*Acc
Masses = range(120,135,5) 
#Masses = [125] 
#Masses = range(120) 
# -------------------------------------------------------------

#procs=["ggh","vbf","wh","zh","tth"]
procs=["GG2H","VBF","TTH","QQ2HLNU","QQ2HLL","WH2HQQ","ZH2HQQ"]
masses=[120.,125.,130.]
cats=["UntaggedTag_0","UntaggedTag_1","UntaggedTag_2","UntaggedTag_3","VBFTag_0","VBFTag_1","VBFTag_2","TTHLeptonicTag","TTHHadronicTag","ZHLeptonicTag","WHLeptonicTag","VHLeptonicLooseTag","VHHadronicTag","VHMetTag"]
sqrts = 13
print "guessing breaks here"
ws = WSTFileWrapper(sys.argv[1],"tagsDumper/cms_hgg_%sTeV"%sqrts)
print "maybe not"
extraFile=sys.argv[2]
#lumi = 3710

#if len(sys.argv)==4 : lumi = 1000* float(sys.argv[3])
lRRV = ws.var("IntLumi")
#lumi = lRRV.getVal()
lumi = 1000.
norm.Init(int(sqrts))


# Some helpful output
print "File - ", sys.argv[1]
print 'Processes found:  ' + str(procs)
print 'Masses found:     ' + str(masses)
print 'Categories found: ' + str(cats)


efficiency=r.TGraphAsymmErrors()
efficiencyPAS=r.TGraphAsymmErrors()
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
  printLine = "Signal M%3.1f: "%M
  Sum = 0
  dataVector= []
  for i in cats:
    if int(M)==M:
      suffix = '_%d_13TeV_%s'%(int(M),i)
      histos = getSigHistos(ws, procs, suffix)

      #integrals = { proc : h.Integral() for (proc, h) in histos.iteritems()}
      integrals = { proc : h.sumEntries() for (proc, h) in histos.iteritems()}
      #print "integralsf for M ",M ," ", integrals

      procLine = 'cat %s, mH=%3.1f:'%(i, M)
      for proc in procs:
        integral = integrals[proc]
        procLine += '   %s %.5f'% (proc, integral )

      hs = [ h for (proc, h) in histos.iteritems() ]
      for (proc,h) in histos.iteritems():
        dataVector.append(h)
      h=hs[0].emptyClone("dummy dataset"+str(id_generator()))
      
      for j in hs:
        #h.Print()
        h.append(j)
        #h.Print()
    
    Sum += h.sumEntries()
    printLine+="%3.5f "%h.sumEntries()
  printLine+="tot=%3.5f"%Sum
  
  xsecs = [ GetProcXsection(M,proc)*adHocFactors[proc] for proc in procs ]
  sm = GetBR(M) * sum(xsecs)
  
  effAcc = 100*Sum/(sm*lumi) # calculate Efficiency at mH
  print "EFF x ACC", effAcc
  #exit(1)
  centralsmooth.SetPoint(point,M,effAcc)
  central.SetPoint(point,M,effAcc)
  efficiency.SetPoint(point,M,effAcc)
  efficiencyE0.SetPoint(point,M,effAcc)
  #efficiencyTH1.Fill(M,effAcc)
  sigmaUp = 0
  sigmaDown = 0
  sigmaNom = 0
  for s in systematics:
    print "considering syst ", s
    syssumup=0
    syssumnom=0
    syssumdn=0
    for cat in cats:
      for proc in procs:
         if int(M)==M:
          [hup,hnom,hdn]=getSystHisto(proc,cat,s,M,ws)
          #print
          #print "syst " , s , " cat ", cat ,", proc ", proc, "hup.sumEntries() ", hup.sumEntries()
          #hup.Print()
          #print "syst " , s , " cat ", cat ,", proc ", proc, "hnom.sumEntries() ", hnom.sumEntries() 
          #hnom.Print()
          #print "syst " , s , " cat ", cat ,", proc ", proc, "hdn.sumEntries() ", hdn.sumEntries()      
          #hdn.Print()
          #print
          syssumup+=hup.sumEntries()
          syssumnom+=hnom.sumEntries()
          syssumdn+=hdn.sumEntries()


    # We make 3-sigma templates so need to scale back by 1/3
    #print "total event yield for systematic ", s ," UP at mh=",M," is " ,syssumup
    #print "total event yield for systematic ", s ," NOM at mh=",M," is " ,syssumnom
    #print "total event yield for systematic ", s ," DN at mh=",M," is " ,syssumdn
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
  
  print "Setting error of pt ", point , " to [",sigmaDown,",",sigmaUp,"]"
  efficiency.SetPointError(point,0,0,sigmaDown,sigmaUp)
  efficiencyPAS.SetPointError(point,0,0,sigmaDown,sigmaUp)
  #efficiency.SetPointError(point,0,0,sigma_ea,sigma_ea)

  print printLine

#centralsmooth.Fit(cenfunc,"R,0,EX0","")
#efficiencyup.Fit(upfunc,"R,0,EX0","")
#efficiencydn.Fit(dnfunc,"R,0,EX0","")

#for point,M in enumerate(Masses):
#  central.SetPoint(point,M,cenfunc.Eval(M))
#  efficiency.SetPoint(point,M,cenfunc.Eval(M))

leg=r.TLegend(0.40,0.16,0.89,0.42)
leg.SetFillColor(0)
leg.SetBorderSize(0)
#leg.AddEntry(central,"Higgs Signal #varepsilon #times Acc","L")
#leg.AddEntry(efficiency,"#pm 1 #sigma syst. error","F")
#leg.AddEntry(efficiencyPAS,"#pm 1 #sigma syst. error","F")

mytext = r.TLatex()
mytext.SetTextSize(0.05)
mytext.SetNDC()

listy = []

MG=r.TMultiGraph()
can =None
can = r.TCanvas("c","c",600,600)
can.SetTicks(1,1)
if ("root" in extraFile):
  #print "got graph!"
  _file0 = r.TFile(extraFile)
  graph=r.TGraph(_file0.Get("effAccGraph"))
  graph.SetLineColor(r.kBlack)
if (graph!=None): 
  print "drawing graph"
  point =0
  for i in range (0,graph.GetN()): 
    graph.GetY()[i] *= 100
    if (graph.GetX()[i] == 120) or (graph.GetX()[i] ==125) or (graph.GetX()[i]==130):
      efficiencyPAS.SetPoint(point,graph.GetX()[i],graph.GetY()[i])
      point =point+1
  #graph.Draw("same")
else :
  print "not drawing graph"
efficiency.SetFillColor(r.kOrange)
efficiencyPAS.SetFillColor(r.kOrange)
efficiency.SetLineWidth(2)
efficiencyPAS.SetLineWidth(2)
central.SetLineWidth(2)
#central.SetMarkerSize(2)
central.SetMarkerColor(r.kBlack)
central.SetMarkerStyle(22)
#MG.Add(efficiency)
MG.Add(efficiencyPAS)
#MG.Add(central)
MG.Add(graph)
leg.AddEntry(graph,"Signal model #varepsilon #times A","l")
leg.AddEntry(efficiencyPAS,"#pm 1 #sigma syst. uncertainty","F")
MG.Draw("APL3")
MG.GetXaxis().SetTitle("m_{H} (GeV)")
MG.GetXaxis().SetTitleSize(0.045)
MG.GetXaxis().SetTitleOffset(0.9)
MG.GetXaxis().SetRangeUser(120.1,129.9)
#MG.GetXaxis().SetRangeUser(120.0,130)
MG.GetYaxis().SetTitle("Efficiency #times Acceptance (%)")
#MG.GetYaxis().SetRangeUser(35.1,45.9)
MG.GetYaxis().SetRangeUser(36.6,45.4)
#MG.GetYaxis().SetTitleSize(0.055)
MG.GetYaxis().SetTitleSize(0.045)
MG.GetYaxis().SetTitleOffset(0.9)
#mytext.DrawLatex(0.1,0.92,"#scale[1.15]{CMS} #bf{#it{Simulation Preliminary}}") #for some reason the bf is reversed??
#mytext.DrawLatex(0.1,0.92,"#scale[1.05]{CMS} #bf{#it{Simulation Preliminary}}") #for some reason the bf is reversed??
mytext.DrawLatex(0.1,0.92,"#scale[1.05]{CMS} #bf{#it{Simulation}}") #for the paper
mytext.DrawLatex(0.75,0.92,"#bf{13#scale[1.1]{ }TeV}")
mytext.DrawLatex(0.129+0.03,0.82,"#bf{H#rightarrow#gamma#gamma}")
can.Update()
can.RedrawAxis()
leg.Draw("same")
print "Int Lumi from workspace ", lumi
#raw_input("Looks OK?")

can.Update()
print "Saving plot as effAcc_vs_mass.pdf"
can.SaveAs("effAcc_vs_mass.C")
can.SaveAs("effAcc_vs_mass.pdf")
can.SaveAs("effAcc_vs_mass.png")
can.SaveAs("effAcc_vs_mass.root")

 
#(r.TVirtualFitter.GetFitter()).GetConfidenceIntervals(efficiencyE0)

#can2 = r.TCanvas()
#efficiencyE0.Draw("E0")
#can2.SaveAs("effAcc_vs_mass_E0.pdf")
  
