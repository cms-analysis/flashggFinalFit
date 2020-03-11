##############################################################################
# Abraham Tishelman-Charny
# 11 March 2020
#
# The purpose of this python module is to plot limits vs Radion mass for the HHWWgg analysis 
############################################################################## 


# Example usage:
#
# python plot_limits.py -AC # compare to ATLAS 2016 semileptonic result 
# python plot_limits.py -CMSC # compare to CMS 2016 results 
# python plot_limits.py -SM # standard model point only 

import ROOT
from ROOT import TFile, TTree, TCanvas, TGraph, TMultiGraph, TGraphErrors, TLegend, kBlack, TLatex, gPad
import CMS_lumi, tdrstyle
import subprocess # to execute shell command

import argparse

# ol = '/afs/cern.ch/work/a/atishelm/private/ecall1algooptimization/PileupMC_v2/Plot/ntuples/'
#ol = '/eos/user/a/atishelm/www/EcalL1Optimization/BX-1/'
ol = '/eos/user/a/atishelm/www/HHWWgg_Analysis/fggfinalfit/limits'

parser = argparse.ArgumentParser()
parser.add_argument("-AC","--atlas_compare", action="store_true", default=False, help="Display limits in way to compare to ATLAS HHWWgg limits", required=False)
parser.add_argument("-CMSC","--CMS_compare", action="store_true", default=False, help="Display limits in way to compare to CMS HH limits", required=False)
parser.add_argument("-SM","--SM_Radion",action="store_true", default=False, help="Display SM limits", required=False)
args = parser.parse_args()

ROOT.gROOT.SetBatch(ROOT.kTRUE)
 
# CMS style
CMS_lumi.cmsText = "CMS"
CMS_lumi.extraText = "Preliminary"
CMS_lumi.cmsTextSize = 0.65
CMS_lumi.outOfFrame = True
tdrstyle.setTDRStyle()
 

 
 
# CREATE datacards
def createDataCardsThetaB(labels,values):
 
    datacard_lines = [ "# automatic generated counting experiment",
                       "imax 1  number of channels",
                       "jmax 1  number of backgrounds",
                       "kmax 2  number of nuisance parameters (sources of systematical uncertainties)",
                       "------------",
                       "bin 1",
                       "observation 0",
                       "------------",
                       "bin              1     1    ",
                       "process         HH   ttbar  ",
                       "process          0     1    ",
                       "rate            107  52861  ",
                       "------------",
                       #"lumi    lnN    1.10  1.10   luminosity",
                       "xs_HH   lnN    1.02    -    cross section + signal efficiency + other minor ones",
                       #"ttbar   lnN      -   1.02   ",
                      ]
 
    # make datacards for differents values of theta_B
    for label, theta_B in zip(labels,values):
        datacard = open("datacard_"+label+".txt", 'w')
        for line in datacard_lines:
            datacard.write(line+"\n")
        theta_B_formatted = ("%.3f" % (1+theta_B/100)).rstrip('0').rstrip('.') # format
        datacard.write("ttbar   lnN      -   %s   " % theta_B_formatted)
        datacard.close()
        print ">>>   datacard_"+label+".txt created"
 
    return labels
 
 
# EXECUTE datacards
def executeDataCards(labels):
 
    for label in labels:
        file_name = "datacard_"+label+".txt"
        combine_command = "combine -M AsymptoticLimits -m 125 -n %s %s" % (label,file_name)
        print ""
        print ">>> " + combine_command
        p = subprocess.Popen(combine_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            print line.rstrip("\n")
        print ">>>   higgsCombine"+label+".AsymptoticLimits.mH125.root created"
        retval = p.wait()
 
 
# GET limits from root file
def getLimits(file_name):

    # print'file_name = ',file_name 
    file = TFile(file_name)
    tree = file.Get("limit")
 
    limits = [ ]
    # print'tree = ',tree
    for quantile in tree:
        # print'quantile = ',quantile 
        if(args.atlas_compare):
            limits.append(tree.limit)
        elif(args.CMS_compare):
            limits.append(tree.limit*1000.) # fb 
        # print ">>>   %.2f" % limits[-1]
 
    return limits[:6]
 
 
# PLOT upper limits
def plotUpperLimits(labels,values):
    # see CMS plot guidelines: https://ghm.web.cern.ch/ghm/plots/
 
    N = len(labels)
    yellow = TGraph(2*N)    # yellow band
    green = TGraph(2*N)     # green band
    median = TGraph(N)      # median line
 
    up2s = [ ]
    for i in range(N):
        # file_name = "higgsCombine"+labels[i]+"AsymptoticLimits.mH125.root"
        #file_name = "higgsCombine.AsymptoticLimits.mH125." + labels[i] +  ".root"
        
        file_name = "HHWWgg_v2-3_2017_" + labels[i] + "_HHWWgg_qqlnu.root"
        limit = getLimits(file_name)
        # print'limit = ',limit
        # print'values[i] = ',values[i] 
        up2s.append(limit[4])
        yellow.SetPoint(    i,    values[i], limit[4] ) # + 2 sigma
        green.SetPoint(     i,    values[i], limit[3] ) # + 1 sigma
        median.SetPoint(    i,    values[i], limit[2] ) # median
        green.SetPoint(  2*N-1-i, values[i], limit[1] ) # - 1 sigma
        yellow.SetPoint( 2*N-1-i, values[i], limit[0] ) # - 2 sigma
 
    W = 800
    H  = 600
    T = 0.08*H
    B = 0.12*H
    L = 0.12*W
    R = 0.04*W
    c = TCanvas("c","c",100,100,W,H)
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
    frame.GetYaxis().SetTitleOffset(0.9)
    frame.GetXaxis().SetNdivisions(508)
    frame.GetYaxis().CenterTitle(True)
    # frame.GetYaxis().SetTitle("95% upper limit on #sigma / #sigma_{SM}")
    
    if(args.atlas_compare):
        frame.GetYaxis().SetTitle("95% CL limits on #sigma(gg#rightarrow X)#times B(X#rightarrow HH) [pb]")
    elif(args.CMS_compare):
        frame.GetYaxis().SetTitle("95% CL limit on #sigma(gg#rightarrow X#rightarrow HH) (fb)")
#    frame.GetYaxis().SetTitle("95% upper limit on #sigma #times BR / (#sigma #times BR)_{SM}")
    # frame.GetXaxis().SetTitle("background systematic uncertainty [%]")
    #if(args.SM_Radion): frame.GetXaxis.SetTitle("Standard Model")
    #else: frame.GetXaxis().SetTitle("Radion Mass (GeV)")
    # frame.SetMinimum(0)
    # frame.SetMinimum(1) # need Minimum > 0 for log scale 
    frame.SetMinimum(1.000001) # need Minimum > 0 for log scale 
    # frame.SetMaximum(max(up2s)*1.05)
    # frame.SetMaximum(max(up2s)*2)
    # frame.SetMaximum(1000.)
    
    if(args.atlas_compare):
        frame.SetMaximum(7*1e2) # ATLAS
    elif(args.CMS_compare):
        frame.SetMaximum(8*1e4) # CMS HH 
    frame.GetXaxis().SetLimits(min(values),max(values))
    # frame.SetLogy()
    # frame.GetXaxis().SetLimits(min(values)-10,max(values)+10)
 
    yellow.SetFillColor(ROOT.kOrange)
    yellow.SetLineColor(ROOT.kOrange)
    yellow.SetFillStyle(1001)
    yellow.Draw('F')
 
    green.SetFillColor(ROOT.kGreen+1)
    green.SetLineColor(ROOT.kGreen+1)
    green.SetFillStyle(1001)
    green.Draw('Fsame')
 
    median.SetLineColor(1)
    median.SetLineWidth(2)
    median.SetLineStyle(2)
    median.Draw('Lsame')
 
    CMS_lumi.CMS_lumi(c,4,11)
    ROOT.gPad.SetTicks(1,1)
    frame.Draw('sameaxis')
 
    # yboost = 0.075
    yboost = -0.2

    x1 = 0.15
    x2 = x1 + 0.24
    y2 = 0.76 + yboost
    y1 = 0.60 + yboost
    legend = TLegend(x1,y1,x2,y2)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)
    legend.SetTextSize(0.041)
    legend.SetTextFont(42)
    legend.AddEntry(median, "AsymptoticLimits CL_{s} expected",'L')
    legend.AddEntry(green, "#pm 1 std. deviation",'f')
#    legend.AddEntry(green, "AsymptoticLimits CL_{s} #pm 1 std. deviation",'f')
    legend.AddEntry(yellow,"#pm 2 std. deviation",'f')
    # legend.AddEntry("","STAT Only","")
#    legend.AddEntry(green, "AsymptoticLimits CL_{s} #pm 2 std. deviation",'f')
    legend.Draw()

    label = TLatex()
    label.SetNDC()
    label.SetTextAngle(0)
    label.SetTextColor(kBlack)
    label.SetTextFont(42)
    label.SetTextSize(0.045)
    label.SetLineWidth(2)
    label.DrawLatex(0.7,0.7 + yboost,"SYST + STAT");
    print " "
    # c.SaveAs("UpperLimit.png")
    
    outFile = ''
    outFile += ol + '/'
    if(args.CMS_compare):
        outFile += "CMS_Compare_"
    if(args.atlas_compare):
        outFile += "atlas_Compare_"


    if args.SM_Radion: outFile += "SM_"

    c.SaveAs(outFile + "UpperLimit.pdf")
    c.SaveAs(outFile + "UpperLimit.png")
    c.SaveAs(outFile + "UpperLimit.C")
    c.Close()
 
 
# RANGE of floats
def frange(start, stop, step):
    i = start
    while i <= stop:
        yield i
        i += step
 
 
# MAIN
def main():
 
    f = TFile()

    labels = [ ]
    values = [ ]
    if args.SM_Radion: 
        labels.append("SM")
        labels.append("SM")
        values.append(-1)
        values.append(1)
    else:       
	    if(args.CMS_compare): masses = [250, 260, 270, 280, 300, 320, 350, 400, 500, 550, 600, 650, 700, 800, 850, 900, 1000] 
	    
            if(args.atlas_compare): masses = [250, 260, 270, 280, 300, 320, 350, 400, 500]
	    for m in masses:
		labels.append("X" + str(m))
		values.append(m)


    # for theta_B in frange(0.0,5.0,1):
    #     values.append(theta_B)
    #     label = "%d" % (theta_B*10)
    #     labels.append(label)
 
    # createDataCardsThetaB(labels,values)
    # executeDataCards(labels)
    plotUpperLimits(labels,values)
 
 
 
if __name__ == '__main__':
    main()
