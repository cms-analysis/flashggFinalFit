python RunText2Workspace.py --ext CP --mode mu_simple_sm --batch local
python RunText2Workspace.py --ext CP --mode cp           --batch local

python RunFits.py --inputJson inputs.json --mode mu_simple_sm --dryRun

combine --floatOtherPOIs 1 --expectSignal 1 -t -1 -P r_VBF --algo grid --alignEdges 1 --saveSpecifiedNuis all --saveInactivePOI 1 --cminApproxPreFitTolerance=10 --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -M MultiDimFit -m 125 -d /afs/cern.ch/work/e/emanuele/hc/vbfhgg/fit/CMSSW_10_2_13/src/flashggFinalFit/Combine/Datacard_mu_simple.root -n _profile1D_syst_r_ggH

combine --floatOtherPOIs 1 --expectSignal 1 -t -1 -P r_ggH --algo grid --alignEdges 1 --saveSpecifiedNuis all --saveInactivePOI 1 --cminApproxPreFitTolerance=10 --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -M MultiDimFit -m 125 -d /afs/cern.ch/work/e/emanuele/hc/vbfhgg/fit/CMSSW_10_2_13/src/flashggFinalFit/Combine/Datacard_mu_simple.root -n _profile1D_syst_r_VBF

plot1DScan.py higgsCombine_profile1D_syst_r_VBF.MultiDimFit.mH125.root --y-cut 20 --y-max 20 --output plots/fits/output_r_VBF --POI r_VBF --translate ../Plots/pois_mu.json --logo-sub "Preliminary"

