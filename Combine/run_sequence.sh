python RunText2Workspace.py --ext CP --mode mu_simple_sm --batch local
python RunFits.py --inputJson inputs.json --ext CP --mode mu_simple_sm --dryRun

combine --floatOtherPOIs 1 --expectSignal 1 -t -1 -P r_VBF --algo grid --alignEdges 1 --saveSpecifiedNuis all --saveInactivePOI 1 --cminApproxPreFitTolerance=10 --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -M MultiDimFit -m 125 -d /afs/cern.ch/work/e/emanuele/hc/vbfhgg/fit/CMSSW_10_2_13/src/flashggFinalFit/Combine/Datacard_mu_simple.root -n _profile1D_syst_r_ggH

combine --floatOtherPOIs 1 --expectSignal 1 -t -1 -P r_ggH --algo grid --alignEdges 1 --saveSpecifiedNuis all --saveInactivePOI 1 --cminApproxPreFitTolerance=10 --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -M MultiDimFit -m 125 -d /afs/cern.ch/work/e/emanuele/hc/vbfhgg/fit/CMSSW_10_2_13/src/flashggFinalFit/Combine/Datacard_mu_simple.root -n _profile1D_syst_r_VBF

plot1DScan.py higgsCombine_profile1D_syst_r_VBF.MultiDimFit.mH125.root --y-cut 20 --y-max 20 --output plots/fits/output_r_VBF --POI r_VBF --translate ../Plots/pois_mu.json --logo-sub "Preliminary"


### CP part
python RunText2Workspace.py --ext CP --mode cp           --batch local

# this floats mu, so x (f_CP) is not relevant
combine -M MultiDimFit -m 125 -d DatacardCP_cp.root --floatOtherPOIs 1 -t -1 -n _profile1D_syst_r -P r --algo grid --points 40 --alignEdges 1 --setParameters r=1 --setParameterRanges r=0,2 --saveSpecifiedNuis all --saveInactivePOI 1 --cminApproxPreFitTolerance=10 --freezeParameters MH --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2

plot1DScan.py higgsCombine_profile1D_syst_r.MultiDimFit.mH125.root --y-cut 40 --y-max 40 --output plots/fits2022-04-28_run2_CP/output_mu_inclusive --POI r --translate ../Plots/pois_cp.json --logo-sub "Preliminary"

# this fits only f_CP, floating the global mu
combine -M MultiDimFit -m 125 -d DatacardCP_cp.root -t -1 -n _profile1D_syst_cp --algo grid --points 20 --alignEdges 1 --setParameters r=1 --setParameterRanges r=0,1 --saveSpecifiedNuis all --freezeParameters MH --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints

plot1DScan.py higgsCombine_profile1D_syst_cp.MultiDimFit.mH125.root --y-cut 60 --y-max 60 --output plots/fits2022-04-28_run2_CP/output_fcp --POI x --translate ../Plots/pois_cp.json --logo-sub "Preliminary"

