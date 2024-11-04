import ROOT
import argparse

ROOT.gROOT.SetBatch(True)

parser = argparse.ArgumentParser(description="Plot r vs pdfindex for a given category")
parser.add_argument("--cat", type=str, help="Category to plot (e.g., best_resolution)")
args = parser.parse_args()

# Open file with fits
f = ROOT.TFile("../Combine/higgsCombineTEST.MultiDimFit.mH125.38.root")
t = f.Get("limit")

r, pdfindex = [], []

for ev in t:
    r.append(getattr(ev, "r"))
    pdfindex.append(getattr(ev, "pdfindex_%s_2022_13TeV" % args.cat))

gr = ROOT.TGraph()
for i in range(len(r)):
    gr.SetPoint(gr.GetN(), r[i], pdfindex[i])

gr.GetXaxis().SetTitle("r")
gr.GetYaxis().SetTitle("pdfindex_%s_2022_13TeV" % args.cat)

gr.SetMarkerStyle(20)
gr.SetMarkerSize(1.5)
gr.SetLineWidth(0)

canv = ROOT.TCanvas()
gr.Draw()

canv.Update()

canv.SaveAs("r_vs_pdfindex_%s.png" % args.cat)
