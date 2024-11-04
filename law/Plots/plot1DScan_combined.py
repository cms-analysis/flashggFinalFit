#!/usr/bin/env python
import ROOT
import math
from functools import partial
import CombineHarvester.CombineTools.plotting as plot
import json
import argparse
import os.path

ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(ROOT.kTRUE)

plot.ModTDRStyle(width=700, l=0.13)
ROOT.gStyle.SetNdivisions(510, "XYZ")
ROOT.gStyle.SetMarkerSize(0.7)

NAMECOUNTER = 0

def read(scan, param, files, ycut):
    goodfiles = [f for f in files if plot.TFileIsGood(f)]
    limit = plot.MakeTChain(goodfiles, 'limit')
    graph = plot.TGraphFromTree(limit, param, '2*deltaNLL', 'quantileExpected > -1.5')
    graph.SetName(scan)
    graph.Sort()
    plot.RemoveGraphXDuplicates(graph)
    plot.RemoveGraphYAbove(graph, ycut)
    # graph.Print()
    return graph


def Eval(obj, x, params):
    return obj.Eval(x[0])


def BuildScan(scan, param, files, color, yvals, ycut):
    graph = read(scan, param, files, ycut)
    if graph.GetN() <= 1:
        graph.Print()
        raise RuntimeError('Attempting to build %s scan from TGraph with zero or one point (see above)' % files)
    bestfit = None
    for i in range(graph.GetN()):
        if graph.GetY()[i] == 0.:
            bestfit = graph.GetX()[i]
    graph.SetMarkerColor(color)
    spline = ROOT.TSpline3("spline3", graph)
    global NAMECOUNTER
    func_method = partial(Eval, spline)
    func = ROOT.TF1('splinefn'+str(NAMECOUNTER), func_method, graph.GetX()[0], graph.GetX()[graph.GetN() - 1], 1)
    func._method = func_method
    NAMECOUNTER += 1
    func.SetLineColor(color)
    func.SetLineWidth(3)
    assert(bestfit is not None)
    crossings = {}
    cross_1sig = None
    cross_2sig = None
    other_1sig = []
    other_2sig = []
    val = None
    val_2sig = None
    for yval in yvals:
        crossings[yval] = plot.FindCrossingsWithSpline(graph, func, yval)
        for cr in crossings[yval]:
            cr["contains_bf"] = cr["lo"] <= bestfit and cr["hi"] >= bestfit
    for cr in crossings[yvals[0]]:
        if cr['contains_bf']:
            val = (bestfit, cr['hi'] - bestfit, cr['lo'] - bestfit)
            cross_1sig = cr
        else:
            other_1sig.append(cr)
    if len(yvals) > 1:
        for cr in crossings[yvals[1]]:
            if cr['contains_bf']:
                val_2sig = (bestfit, cr['hi'] - bestfit, cr['lo'] - bestfit)
                cross_2sig = cr
            else:
                other_2sig.append(cr)
    else:
        val_2sig = (0., 0., 0.)
        cross_2sig = cross_1sig
    return {
        "graph"     : graph,
        "spline"    : spline,
        "func"      : func,
        "crossings" : crossings,
        "val"       : val,
        "val_2sig": val_2sig,
        "cross_1sig" : cross_1sig,
        "cross_2sig" : cross_2sig,
        "other_1sig" : other_1sig,
        "other_2sig" : other_2sig
    }

parser = argparse.ArgumentParser()

parser.add_argument('main', help='Main input file for the scan')
parser.add_argument('--y-cut', type=float, default=7., help='Remove points with y > y-cut')
parser.add_argument('--y-max', type=float, default=8., help='y-axis maximum')
parser.add_argument('--output', '-o', help='output name without file extension', default='scan')
parser.add_argument('--POI', help='use this parameter of interest', default='r')
parser.add_argument('--translate', default=None, help='json file with POI name translation')
parser.add_argument('--main-label', default='Observed', type=str, help='legend label for the main scan')
parser.add_argument('--main-color', default=1, type=int, help='line and marker color for main scan')
parser.add_argument('--observed', nargs='*', required=True, help='Add scans: FILE:LABEL:COLOR grouped together in group 1')
parser.add_argument('--expected', nargs='*', required=True, help='Add scans: FILE:LABEL:COLOR grouped together in group 2')
parser.add_argument('--breakdown1', help='do quadratic error subtraction using --others')
parser.add_argument('--breakdown2', help='do quadratic error subtraction using --others')
parser.add_argument('--logo', default='CMS')
parser.add_argument('--logo-sub', default='Preliminary')
args = parser.parse_args()

print('--------------------------------------')
print( args.output)
print('--------------------------------------')

fixed_name = args.POI
if args.translate is not None:
    with open(args.translate) as jsonfile:
        name_translate = json.load(jsonfile)
    if args.POI in name_translate:
        fixed_name = name_translate[args.POI]

yvals = [1., 4.]

main_scan = BuildScan(args.output, args.POI, [args.main], args.main_color, yvals, args.y_cut)

observed_scans = [ ]
observed_scans_opts = [ ]
if args.observed is not None:
    for oargs in args.observed:
        splitargs = oargs.split(':')
        observed_scans_opts.append(splitargs)
        observed_scans.append(BuildScan(args.output, args.POI, [splitargs[0]], int(splitargs[2]), yvals, args.y_cut))
        
expected_scans = [ ]
expected_scans_opts = [ ]
if args.expected is not None:
    for oargs in args.expected:
        splitargs = oargs.split(':')
        expected_scans_opts.append(splitargs)
        expected_scans.append(BuildScan(args.output, args.POI, [splitargs[0]], int(splitargs[2]), yvals, args.y_cut))


canv = ROOT.TCanvas(args.output, args.output)
pads = plot.OnePad()
main_scan['graph'].SetMarkerColor(1)
main_scan['graph'].Draw('AP')

axishist = plot.GetAxisHist(pads[0])

axishist.SetMaximum(args.y_max)
axishist.SetMinimum(0)
axishist.GetYaxis().SetTitle("- 2 #Delta ln L")
axishist.GetXaxis().SetTitle("%s" % fixed_name)

new_min = axishist.GetXaxis().GetXmin()
new_max = axishist.GetXaxis().GetXmax()
mins = []
maxs = []
for other in observed_scans:
    mins.append(other['graph'].GetX()[0])
    maxs.append(other['graph'].GetX()[other['graph'].GetN()-1])

if len(observed_scans) > 0:
    if min(mins) < main_scan['graph'].GetX()[0]:
        new_min = min(mins) - (main_scan['graph'].GetX()[0] - new_min)
    if max(maxs) > main_scan['graph'].GetX()[main_scan['graph'].GetN()-1]:
        new_max = max(maxs) + (new_max - main_scan['graph'].GetX()[main_scan['graph'].GetN()-1])
    
new_min2 = axishist.GetXaxis().GetXmin()
new_max2 = axishist.GetXaxis().GetXmax()
mins2 = []
maxs2 = []
for other in expected_scans:
    mins2.append(other['graph'].GetX()[0])
    maxs2.append(other['graph'].GetX()[other['graph'].GetN()-1])

if len(expected_scans) > 0:
    if min(mins2) < main_scan['graph'].GetX()[0]:
        new_min2 = min(mins2) - (main_scan['graph'].GetX()[0] - new_min2)
    if max(maxs2) > main_scan['graph'].GetX()[main_scan['graph'].GetN()-1]:
        new_max2 = max(maxs2) + (new_max2 - main_scan['graph'].GetX()[main_scan['graph'].GetN()-1])

axishist.GetXaxis().SetLimits(min(new_min, new_min2), max(new_max, new_max2))
    
for other in observed_scans:
    if args.breakdown1 is not None:
        other['graph'].SetMarkerSize(0.4)
    other['graph'].Draw('PSAME')
    
for other in expected_scans:
    if args.breakdown2 is not None:
        other['graph'].SetMarkerSize(0.4)
    other['graph'].Draw('PSAME')

line = ROOT.TLine()
line.SetLineColor(16)
# line.SetLineStyle(7)
for yval in yvals:
    plot.DrawHorizontalLine(pads[0], line, yval)
    if (len(observed_scans) == 0):
        for cr in main_scan['crossings'][yval]:
            if cr['valid_lo']: line.DrawLine(cr['lo'], 0, cr['lo'], yval)
            if cr['valid_hi']: line.DrawLine(cr['hi'], 0, cr['hi'], yval)

main_scan['func'].Draw('same')
for other in observed_scans:
    if args.breakdown1 is not None:
        other['func'].SetLineStyle(2)
        other['func'].SetLineWidth(2)
    other['func'].Draw('SAME')

for i, other in enumerate(expected_scans):
    if args.breakdown2 is not None:
        if i == 0:
            other['func'].SetLineStyle(1)
        else:
            other['func'].SetLineStyle(2)
        other['func'].SetLineWidth(2)
    other['func'].Draw('SAME')



box = ROOT.TBox(axishist.GetXaxis().GetXmin(), 0.625*args.y_max, axishist.GetXaxis().GetXmax(), args.y_max)
box.Draw()
pads[0].GetFrame().Draw()
pads[0].RedrawAxis()

crossings = main_scan['crossings']
val_nom = main_scan['val']
val_2sig = main_scan['val_2sig']

crossings2 = expected_scans[0]['crossings']
val_nom2 = expected_scans[0]['val']
val_2sig2 = expected_scans[0]['val_2sig']


textfit = '%s = %.3f{}^{#plus %.3f}_{#minus %.3f}' % (fixed_name, val_nom[0], val_nom[1], abs(val_nom[2]))
print(textfit)

pt = ROOT.TPaveText(0.59, 0.87 - len(observed_scans)*0.08, 0.95, 0.91, 'NDCNB')
pt2 = ROOT.TPaveText(0.59, 0.87 - len(expected_scans)*0.08, 0.95, 0.79, 'NDCNB')
#pt.AddText(textfit)

if args.breakdown1 is None:
    for i, other in enumerate(observed_scans):
        textfit = '#color[%s]{%s = %.3f{}^{#plus %.3f}_{#minus %.3f}}' % (observed_scans_opts[i][2], fixed_name, other['val'][0], other['val'][1], abs(other['val'][2]))
        pt.AddText(textfit)
        
    for i, other in enumerate(expected_scans):
        textfit = '#color[%s]{%s^{Expected} = %.3f{}^{#plus %.3f}_{#minus %.3f}}' % (expected_scans_opts[i][2], fixed_name, other['val'][0], other['val'][1], abs(other['val'][2]))
        pt2.AddText(textfit)


if args.breakdown1 is not None:
    pt.SetX1(0.50)
    if len(observed_scans) >= 3:
        pt.SetX1(0.19)
        pt.SetX2(0.88)
        pt.SetY1(0.66)
        pt.SetY2(0.82)
    breakdown1 = args.breakdown1.split(',')
    v_hi = [val_nom[1]]
    v_lo = [val_nom[2]]
    for other in observed_scans:
        v_hi.append(other['val'][1])
        v_lo.append(other['val'][2])
    assert(len(v_hi) == len(breakdown1))
    textfit = '%s = %.3f' % (fixed_name, val_nom[0])
    for i, br in enumerate(breakdown1):
        if i < (len(breakdown1) - 1):
            if (abs(v_hi[i+1]) > abs(v_hi[i])):
                print('ERROR SUBTRACTION IS NEGATIVE FOR %s HI' % br)
                hi = 0.
            else:
                hi = math.sqrt(v_hi[i]*v_hi[i] - v_hi[i+1]*v_hi[i+1])
            if (abs(v_lo[i+1]) > abs(v_lo[i])):
                print('ERROR SUBTRACTION IS NEGATIVE FOR %s LO' % br)
                lo = 0.
            else:
                lo = math.sqrt(v_lo[i]*v_lo[i] - v_lo[i+1]*v_lo[i+1])
        else:
            hi = v_hi[i]
            lo = v_lo[i]
        textfit += '{}^{#plus %.3f}_{#minus %.3f}(%s)' % (hi, abs(lo), br)
    pt.AddText(textfit)


pt.SetTextAlign(11)
pt.SetTextFont(42)
pt.Draw()

if args.breakdown2 is not None:
    pt2.SetX1(0.50)
    if len(expected_scans) >= 3:
        pt2.SetX1(0.19)
        pt2.SetX2(0.88)
        pt2.SetY1(0.66)
        pt2.SetY2(0.82)
    breakdown2 = args.breakdown2.split(',')
    v_hi = [val_nom2[1]]
    v_lo = [val_nom2[2]]
    for i, other in enumerate(expected_scans):
        if i == 0: continue #Skip first entry, as its already in v_hi and v_lo
        v_hi.append(other['val'][1])
        v_lo.append(other['val'][2])
    assert(len(v_hi) == len(breakdown2))
    textfit = '%s^{Exp.} = %.3f' % (fixed_name, val_nom2[0])
    for i, br in enumerate(breakdown2):
        if i < (len(breakdown2) - 1):
            if (abs(v_hi[i+1]) > abs(v_hi[i])):
                print('ERROR SUBTRACTION IS NEGATIVE FOR %s HI' % br)
                hi = 0.
            else:
                hi = math.sqrt(v_hi[i]*v_hi[i] - v_hi[i+1]*v_hi[i+1])
            if (abs(v_lo[i+1]) > abs(v_lo[i])):
                print('ERROR SUBTRACTION IS NEGATIVE FOR %s LO' % br)
                lo = 0.
            else:
                lo = math.sqrt(v_lo[i]*v_lo[i] - v_lo[i+1]*v_lo[i+1])
        else:
            hi = v_hi[i]
            lo = v_lo[i]
        textfit += '{}^{#plus %.3f}_{#minus %.3f}(%s)' % (hi, abs(lo), br)
    pt2.AddText(textfit)


pt2.SetTextAlign(11)
pt2.SetTextFont(42)
pt2.Draw()

plot.DrawCMSLogo(pads[0], args.logo, args.logo_sub, 10, 0.055, 0.035, 1.2,  cmsTextSize = 1.) 
lumi_com = ROOT.TPaveText(0.75, 0.945, 0.97, 0.98, 'NDCNB')
lumi_com.AddText("34.7 fb^{-1} (13.6 TeV)")
lumi_com.SetTextAlign(11)
lumi_com.SetTextFont(42)
lumi_com.Draw()

legend_l = 0.69
if len(observed_scans) > 0:
    legend_l = legend_l - len(observed_scans) * 0.04
legend = ROOT.TLegend(0.15, legend_l, 0.45, 0.78, '', 'NBNDC')
if len(observed_scans) >= 3:
        legend = ROOT.TLegend(0.46, 0.83, 0.95, 0.93, '', 'NBNDC')
        legend.SetNColumns(2)


legend.AddEntry(main_scan['func'], args.main_label, 'L')
for i, other in enumerate(observed_scans):
    legend.AddEntry(other['func'], observed_scans_opts[i][1], 'L')
for i, other in enumerate(expected_scans):
    legend.AddEntry(other['func'], expected_scans_opts[i][1], 'L')
legend.Draw()

save_graph = main_scan['graph'].Clone()
save_graph.GetXaxis().SetTitle('%s = %.3f %+.3f/%+.3f' % (fixed_name, val_nom[0], val_nom[2], val_nom[1]))
outfile = ROOT.TFile(args.output+'.root', 'RECREATE')
outfile.WriteTObject(save_graph)
outfile.Close()
canv.Print('.pdf')
canv.Print('.png')

