import ROOT 
from array import array 
import Combine.CMS_lumi as CMS_lumi
import Combine.tdrstyle as tdrstyle 

def GetBR(finalState_):
  # https://pdglive.lbl.gov/Particle.action?node=S043&init=0
  WW_BR_ndigits = 3 # Rounding precision of final state branching ratios 
  HH_BR_ndigits = 6 # For HH->WWgg BR (expect a few zeroes)
  BR_W_qq = 0.6741 
  BR_W_enu = 0.1071
  BR_W_munu = 0.1063
  BR_W_taunu = 0.1138
  BR_Wlnu = BR_W_enu + BR_W_munu + BR_W_taunu

  BR_WW_qqlnu = round(2 * BR_Wlnu * BR_W_qq, WW_BR_ndigits)
  BR_WW_lnulnu = round(BR_Wlnu * BR_Wlnu, WW_BR_ndigits)
  BR_WW_qqqq = round(BR_W_qq * BR_W_qq, WW_BR_ndigits) 

  # HH BR
  # CMS Higgs BRs: https://twiki.cern.ch/twiki/bin/view/LHCPhysics/CERNYellowReportPageBR
  # Higgs mass: https://pdglive.lbl.gov/Particle.action?node=S126&init=0
  BR_H_gammagamma = 0.00227
  BR_H_WW = 0.2154 

  BR_HH_WWgammagamma = round(2 * BR_H_gammagamma * BR_H_WW, HH_BR_ndigits)

  BR_dict = {
    "SL" : BR_WW_qqlnu,
    "FL" : BR_WW_lnulnu,
    "FH" : BR_WW_qqqq,
    "HH_WWgg" : BR_HH_WWgammagamma
  }

  return BR_dict[finalState_]

def FinalStateCats(FS_):
  fsCatDict = {
    "SL" : "HHWWggTag_0,HHWWggTag_1",
    "FH" : "HHWWggTag_2",
    "FL" : "HHWWggTag_3"
  }
  return fsCatDict[FS_]

def GetPlotDir(mode_):
    plotDirDict = {
        "fTestOnly" : ["bkgfTest-Data"],
        "bkgPlotsOnly" : ["bkgPlots-Data"],
        "std" : ["sigfTest","sigfit","sigplots"] ##-- signal std  ##-- sigfit sigplots 
    }
    return plotDirDict[mode_]

def GetFitDirec(dirType_):
    fitDirDict = {
        "Signal" : "Signal",
        "Data" : "Background",
        "Datacard" : "Datacard",
        "Combine" : "Combine"
    }
    return fitDirDict[dirType_]    

def GetConfigParams(dirType_):
    configParamsDict = {
        "Signal" : ["inputWSDir","cats","ext","year","mode","FinalStateParticles","usrprocs","analysis_type"],
        "Data" : ["inputWSDir","cats","ext","year","mode","FinalStateParticles"],
        "Datacard" : ["inputWSDir","cats","ext","year","mode","FinalStateParticles","usrprocs","analysis_type","note"]
        # "Combine" : ["inputWSDir","cats","ext","year","mode","FinalStateParticles","usrprocs","analysis_type","note"]
    }
    return configParamsDict[dirType_]

def GetAnalysisType(physicsCase_):
    analysisTypeDict = {
        "SM" : "EFT" ##-- should change EFT --> NON-RES in all fitting scripts 
    }
    return analysisTypeDict[physicsCase_]

def GetUsrProcs(physicsCase_):
    usrProcsDict = {
        "SM" : "GluGluToHHTo"
    }
    return usrProcsDict[physicsCase_]

def GetFinalStateParticles(FS_):
    fsParticlesDict = {
        "SL" : "qqlnu",
        "FH" : "qqqq",
        "FL" : "lnulnu"
    }
    return fsParticlesDict[FS_]

# GET limits from root file
def getLimits(file_name):

    # print'file_name = ',file_name 
    file = ROOT.TFile(file_name)
    tree = file.Get("limit")
 
    limits = [ ]
    # for quantile in tree:
        # if(args.unit == "fb"):
            # limits.append(tree.limit) # value is already in fb because multiplied by arb. XS = 1fb 
        # elif(args.unit == "pb"):
            # limits.append(tree.limit/1000.) # pb
	# elif(args.SM_Point):
	    # limits.append(tree.limit)

    for quantil in tree:
        limits.append(tree.limit)
    # print limits 
 
    return limits[:6]

# def CreateYieldsTables(cutBatchTag_pairs,dataNevents_list,MC_names,MC_Nevents_lists,MC_Nevents_noweight_lists,ol_):
def CreateLimitTable(HH_limit):
    ROOT.gROOT.SetBatch(ROOT.kTRUE) # do not output upon draw statement 
    print'Creating grid of limit values'
    ol = '/eos/user/a/atishelm/www/HHWWgg/Combination/'
    
    xLabels = ['2016','2017','2018','Run2']
    yLabels = ['SL','FH','FL']
    nXGridLabels = len(xLabels)
    nYGridLabels = len(yLabels)
    h_grid = ROOT.TH2F('h_grid','',nXGridLabels,0,nXGridLabels,nYGridLabels,0,nYGridLabels)
    h_grid.SetStats(0) 
    for yli, yl in enumerate(yLabels):
        h_grid.GetYaxis().SetBinLabel(yli+1,yl) 

    for xl_i,xl in enumerate(xLabels):
        h_grid.GetXaxis().SetBinLabel(xl_i+1,xl)
        year = xl
        for ifs,finalState in enumerate(yLabels):        
            file_name = "Limits/HHWWgg_SM-%s_%s_AllCats_limits.root"%(finalState,year)   # gl + "_limits/HHWWgg_v2-3_2017_" + ml + "_" + gl + "_HHWWgg_qqlnu.root"
            limit = getLimits(file_name) ## WWgg limit 
            if(HH_limit): 
                limit = [l*1.0307153 for l in limit]
            median = limit[2] 
            h_grid.Fill(xl_i,ifs,median)
        
    h_grid.SetMarkerSize(2)
    h_grid.GetXaxis().SetLabelSize(0.04)
    h_grid.GetYaxis().SetLabelSize(0.04)

    label = ROOT.TLatex()
    label.SetNDC()
    label.SetTextAngle(0)
    label.SetTextColor(ROOT.kBlack)
    label.SetTextFont(42)
    label.SetTextSize(0.045)
    label.SetLineWidth(2)
    if(HH_limit):
        outNamepng = "%s/sigmaHH_grid.png"%(ol)
        outNamepdf = "%s/sigmaHH_grid.pdf"%(ol)
    else: 
        outNamepng = "%s/grid.png"%(ol)
        outNamepdf = "%s/grid.pdf"%(ol)
    c_tmp = ROOT.TCanvas('c_tmp','c_tmp',800,600)
    c_tmp.SetRightMargin(0.15)
    c_tmp.SetLeftMargin(0.1)
    c_tmp.SetBottomMargin(0.15)
    c_tmp.SetTopMargin(0.1)
    h_grid.Draw("text COL1")
    if(HH_limit): label.DrawLatex(0.3,0.95,"#sigma_{HH} 95% CL Limit Medians [pb]")
    else: label.DrawLatex(0.3,0.95,"#sigma(HH#rightarrow WW#gamma#gamma) 95% CL Limit Medians [fb]")
    
    c_tmp.SaveAs(outNamepng)
    c_tmp.SaveAs(outNamepdf)

def PlotLimitBands():
    # CMS style
    CMS_lumi.cmsText = "CMS"
    CMS_lumi.extraText = "Preliminary"
    CMS_lumi.cmsTextSize = 0.65
    CMS_lumi.outOfFrame = True

    # year = args.year 

    # if(year=="2016"): CMS_lumi.lumi_sqrtS = "35.9 fb^{-1}"
    # elif(year=="2017"): CMS_lumi.lumi_sqrtS = "41.5 fb^{-1}"
    # elif(year=="2018"): CMS_lumi.lumi_sqrtS = "59.8 fb^{-1}"
    # elif(year=="Run2"): CMS_lumi.lumi_sqrtS = "137.2 fb^{-1}"
    # else: CMS_lumi.lumi_sqrtS = "XXXX fb^{-1}"
    CMS_lumi.lumi_sqrtS = "35.9 fb^{-1} + 41.5 fb^{-1} + 59.8 fb^{-1}"

    # cmsLumiIndex = 0
    # tdrstyle.setTDRStyle()
    # tdrStyle.cd()

    # TDR style 

    
    thistdrstyle = tdrstyle.setTDRStyle()
    thistdrstyle.SetOptLogy(0)
    # if(args.Ratio) or (args.Grid): thistdrstyle.SetOptLogy(0)
    # else: thistdrstyle.SetOptLogy(1)

    thistdrstyle.cd()    
    ol = '/eos/user/a/atishelm/www/HHWWgg/Combination/'
    # labelTitle= args.HHWWggCatLabel
    # see CMS plot guidelines: https://ghm.web.cern.ch/ghm/plots/
    labels = []
    plotLabels = [] 
    # for fs in ['SL','FH','FL']:
    for fs in ['FL','FH','SL']:
        for year in ['2016','2017','2018','Run2']:
            labels.append("%s_%s"%(fs,year))
            plotLabels.append("%s_%s"%(fs,year))

    labels.append('All_Run2')
    plotLabels.append('All_Run2')

    N = len(labels) # should be same 
    yellow = ROOT.TGraph(2*N)    # yellow band
    green = ROOT.TGraph(2*N)     # green band
    median = ROOT.TGraph(N)      # median line
 
    # up2s = [ ]
    median_h = ROOT.TH1F("median_h","median_h",N,0,N)
    upperTwoSigs = array( 'd' )
    upperOneSig = array( 'd' )
    lowerOneSig = array( 'd' )
    lowerTwoSigs = array( 'd' )
    x = array ( 'd' )
    y = array ( 'd' )
    xerrorLow = array ( 'd' )
    xerrorHigh = array ( 'd' )

    # year = args.year

    # green_h = TH1F("")
    xvalues = []
    for i in range(N):
        xvalues.append(i)
    nonBRvals = [] 
    # HHWWgg_factor = 1.0307153 # for HH limits 
    HHWWgg_factor = 1.0307153/0.031 # for HH limits 
    # HHWWgg_factor = 1 
    for i in range(N):
        # direc = args.HHWWggCatLabel

        # file_name = "%s_limits/%s_%s_HHWWgg_qqlnu.root"%(direc,campaign,labels[i])
        # file_name = "Limits/HHWWgg_SM-%s_%s_AllCats_limits.root"%(finalState,year)
        file_name = "Limits/HHWWgg_SM-%s_AllCats_limits.root"%(labels[i])
        # file_name = "%s_limits/%s_%s_%s_HHWWgg_qqlnu.root"%(direc,campaign,year,labels[i])
        print"file name:",file_name
        # file_name = direc + "_limits/HHWWgg_v2-3_2017_" + labels[i] + "_HHWWgg_qqlnu.root"
        #print'file_name:',file_name
        limit = getLimits(file_name)
        yellow.SetPoint(    i,    xvalues[i], limit[4]*HHWWgg_factor ) # + 2 sigma
        green.SetPoint(     i,    xvalues[i], limit[3]*HHWWgg_factor ) # + 1 sigma
        # median_h.Fill(xvalues[i], limit[2]*HHWWgg_qqlnu_factor)
        median.SetPoint(    i,    xvalues[i], limit[2]*HHWWgg_factor ) # median
        green.SetPoint(  2*N-1-i, xvalues[i], limit[1]*HHWWgg_factor ) # - 1 sigma
        yellow.SetPoint( 2*N-1-i, xvalues[i], limit[0]*HHWWgg_factor ) # - 2 sigma

        # print("limit without HHWWgg factor:",limit[2])
        nonBRvals.append(limit[2])
        median_val = limit[2]*HHWWgg_factor
        # x.append(median_h.GetXaxis().GetBinCenter(i+1))
        x.append(median_h.GetXaxis().GetBinLowEdge(i+1))
        upperTwoSigs.append(abs(limit[4]*HHWWgg_factor-median_val))
        upperOneSig.append(abs(limit[3]*HHWWgg_factor-median_val))
        y.append(median_val)
        lowerOneSig.append(abs(limit[1]*HHWWgg_factor-median_val))
        lowerTwoSigs.append(abs(limit[0]*HHWWgg_factor-median_val))

        xerrorLow.append(0.5)
        xerrorHigh.append(0.5)

        median_h.GetXaxis().SetBinLabel(i+1,plotLabels[i])
        # print"labels[i]:",labels[i]
        median_h.Fill(x[i],median_val)

        # print"median_val:",median_val

    # print("masses:",xvalues)
    # print("nonBR limits:",nonBRvals)

    median_h.Draw("a")
    gr = ROOT.TGraphAsymmErrors(N,x,y,xerrorLow,xerrorHigh,lowerOneSig,upperOneSig)
    gr_yellow = ROOT.TGraphAsymmErrors(N,x,y,xerrorLow,xerrorHigh,lowerTwoSigs,upperTwoSigs)
    gr.SetMarkerStyle(21)
    gr_yellow.SetMarkerStyle(21)    

    W = 800
    H  = 600
    T = 0.08*H
    B = 0.12*H
    L = 0.12*W
    R = 0.04*W
    c = ROOT.TCanvas("c","c",100,100,W,H)
    c.SetFillColor(0)
    c.SetBorderMode(0)
    c.SetFrameFillStyle(0)
    c.SetFrameBorderMode(0)
    c.SetLeftMargin( L/W )
    c.SetRightMargin( R/W )
    c.SetTopMargin( T/H )
    c.SetBottomMargin( B/H )
    c.SetTickx(0)
    c.SetTicky(0)
    c.SetGrid()
    # c.SetLogy()
    # gPad.SetLogy()
    c.cd()
    # ROOT.gPad.SetLogy()
    # c.SetLogy()
    frame = c.DrawFrame(1.4,0.001, 4.1, 10)
    frame.GetYaxis().CenterTitle()
    frame.GetYaxis().SetTitleSize(0.05)
    frame.GetXaxis().SetTitleSize(0.05)
    frame.GetXaxis().SetLabelSize(0.04)
    frame.GetYaxis().SetLabelSize(0.04)
    # frame.GetYaxis().SetTitleOffset(0.9)
    frame.GetYaxis().SetTitleOffset(1.15)
    frame.GetXaxis().SetNdivisions(N)
    frame.GetYaxis().CenterTitle(True)

    # if(args.SM_Point or args.EFT):
        # process = "#sigma(gg#rightarrow HH"
    # else:
        # process = "#sigma(gg#rightarrow X)#times B(X#rightarrow HH"

    frame.GetYaxis().SetTitle("95% CL limits on #sigma(gg #rightarrow HH) / #sigma_{SM}")

    # if(args.SM_Point or args.EFT):
    #     if(args.unit == "pb"):
    #         if(resultType == "WWgg"): frame.GetYaxis().SetTitle("95% CL limits on #sigma(gg #rightarrow HH) #times B(HH #rightarrow WW#gamma#gamma) [pb]")    
    #         elif(resultType == "HH"): frame.GetYaxis().SetTitle("95% CL limits on #sigma(gg #rightarrow HH) [pb]")         
                
    #     elif(args.unit == "fb"):
    #         if(resultType == "WWgg"): frame.GetYaxis().SetTitle("95% CL limits on #sigma(gg #rightarrow HH) #times B(HH #rightarrow WW#gamma#gamma) [fb]")    
    #         elif(resultType == "HH"): frame.GetYaxis().SetTitle("95% CL limits on #sigma(gg #rightarrow HH) [fb]")          
    # else:
    #     if(args.unit == "pb"):
    #         if(resultType == "WWgg"): frame.GetYaxis().SetTitle("95% CL limits on #sigma(gg#rightarrow X)#times B(X#rightarrow HH#rightarrow WW#gamma#gamma) [pb]")    
    #         elif(resultType == "HH"): frame.GetYaxis().SetTitle("95% CL limits on #sigma(gg#rightarrow X)#times B(X#rightarrow HH) [pb]")         
                
    #     elif(args.unit == "fb"):
    #         if(resultType == "WWgg"): frame.GetYaxis().SetTitle("95% CL limits on #sigma(gg#rightarrow X)#times B(X#rightarrow HH#rightarrow WW#gamma#gamma) [fb]")    
    #         elif(resultType == "HH"): frame.GetYaxis().SetTitle("95% CL limits on #sigma(gg#rightarrow X)#times B(X#rightarrow HH) [fb]")          
 

    # if(resultType == "WWgg"): 
    #     frame.GetYaxis().SetTitleSize(0.04)
    #     frame.GetYaxis().SetTitleOffset(1.3)

    # frame.GetYaxis().SetTitle(Label_1 + " / " + Label_2)
    # frame.GetYaxis().SetRangeUser(0.8,1.2)
    # frame.GetYaxis().SetTitle("95% CL limits ratio: " + Label_1 + " / " + Label_2)

    # if(args.atlas_compare):
    #     frame.GetYaxis().SetTitle("95% CL limits on #sigma(gg#rightarrow X)#times B(X#rightarrow HH) [pb]")
    # elif(args.CMS_compare) or (args.All_Points):
    #     frame.GetYaxis().SetTitle("95% CL limit on #sigma(gg#rightarrow X#rightarrow HH) (fb)")
    # elif(args.SM_Point):
    #     frame.GetYaxis().SetTitle("95% CL limit on #sigma(gg#rightarrow X#rightarrow HH) (pb)")
	
    #frame.GetXaxis().Set
#    frame.GetYaxis().SetTitle("95% upper limit on #sigma #times BR / (#sigma #times BR)_{SM}")
    # frame.GetXaxis().SetTitle("background systematic uncertainty [%]")

    # if(args.SM_Point): frame.GetXaxis().SetTitle("Standard Model")
    # else: frame.GetXaxis().SetTitle("Radion Mass (GeV)")

    # frame.SetMinimum(0)
    # frame.SetMinimum(1) # need Minimum > 0 for log scale 
    
    # frame.SetMinimum(args.ymin) # need Minimum > 0 for log scale 
    frame.SetMinimum(0.1) # need Minimum > 0 for log scale 

    frame.SetMaximum(1000)
    frame.GetXaxis().SetLimits(-0.5,N-0.5)
    # frame.GetXaxis().CenterLabels(True)

    # print"n bins:",frame.GetNbinsX()
    # nLabels = len(N)

    for i in range(N):
        frame.GetXaxis().SetBinLabel(int(1000.*(2*i+1)/(2*N)),plotLabels[i])
    if(N > 3): frame.GetXaxis().SetLabelSize(0.03)
    else: frame.GetXaxis().SetLabelSize(0.12)

    # frame.LabelsOption("h","X")
    # frame.LabelsOption("h","X")
    # frame.GetXaxis().CenterLabels(True)

    # if(args.NMSSM): 
	# frame.GetXaxis().SetTitle("(M_{X},M_{Y}) [GeV]")
	#print"title offset:",frame.GetXaxis().GetTitleOffset()
	# frame.GetXaxis().SetTitleOffset(1.1)

    # frame.SetLogy()
    # frame.GetXaxis().SetLimits(min(values)-10,max(values)+10)
 
    yellow.SetFillColor(ROOT.kOrange)
    green.SetFillColor(ROOT.kGreen+1)
    gr_yellow.SetFillColor(ROOT.kOrange)
    gr_yellow.Draw("P2")

    gr.SetFillColor(ROOT.kGreen+1)
    gr.Draw("P2same")

    CMS_lumi.CMS_lumi(c,4,11)
    ROOT.gPad.SetTicks(1,1)
    frame.Draw('sameaxis')
    # yboost = args.yboost 
    yboost = 0.1

    x1 = 0.15
    x2 = x1 + 0.24
    y2 = 0.76 + yboost
    y1 = 0.60 + yboost
    legend = ROOT.TLegend(x1,y1,x2,y2)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)
    legend.SetTextSize(0.041)
    legend.SetTextFont(42)
    legend.AddEntry(gr, "AsymptoticLimits CL_{s} expected",'P')
    legend.AddEntry(green, "#pm 1 std. deviation",'f')
    legend.AddEntry(yellow,"#pm 2 std. deviation",'f')

    legend.Draw('same')

    label = ROOT.TLatex()
    label.SetNDC()
    label.SetTextAngle(0)
    label.SetTextColor(ROOT.kBlack)
    label.SetTextFont(42)
    label.SetTextSize(0.045)
    label.SetLineWidth(2)

    # if(args.systematics): label.DrawLatex(0.7,0.7 + yboost,"SYST + STAT")
    # else: label.DrawLatex(0.7,0.7 + yboost,"STAT ONLY")
    label.DrawLatex(0.7,0.7 + yboost,"SM Non-Res")
    label.DrawLatex(0.7,0.6 + yboost,"STAT ONLY")
    
    print " "
    # c.SaveAs("UpperLimit.png")
    
    outFile = ''
    outFile += ol + '/'
    # if(args.CMS_compare):
        # outFile += "CMS_Compare_"
    # if(args.All_Points):
	# outFile += "All_Points_"
    # if(args.atlas_compare):
        # outFile += "atlas_Compare_"

    # if args.SM_Point: outFile += "SM_"
    # elif args.EFT: outFile += "EFT_"
    # elif args.NMSSM: outFile += "NMSSM_"

    # outFile += Label_1 + "_" + Label_2 + "_"

    # outFile += "%s_"%("testestest")

    outFile = "%s/limitBands_"%(ol)

    c.SaveAs(outFile + "UpperLimit.pdf")
    c.SaveAs(outFile + "UpperLimit.png")
    c.SaveAs(outFile + "UpperLimit.C")
    c.Close()     
