# prefit (all mu=1)
python makeSplusBModelPlot.py --inputWSFile ../Combine/Datacard_sm_mu_simple.root --cats VBFTag_1,VBFTag_3,VBFTag_5,VBFTag_6,VBFTag_7 --doZeroes --pdir plots/2022-08-31-fits --ext _test --translateCats cats.json --unblind

# postfit
python makeSplusBModelPlot.py --inputWSFile plots/2022-08-31-fits/sm_mu_simple/bestfit_syst_r_VBF.root --loadSnapshot MultiDimFit --cats VBFTag_1,VBFTag_3,VBFTag_5,VBFTag_6,VBFTag_7 --doZeroes --pdir plots/2022-08-31-fits --ext _test --translateCats cats.json --unblind

# get category weights
python getCatInfo.py --inputWSFile ../Combine/Datacard_sm_mu_simple.root --cats all --doBkgRenormalization --saveCatInfo --ext _allCats

# make bands with toys
python makeToys.py --inputWSFile plots/2022-08-31-fits/sm_mu_simple/bestfit_syst_r_VBF.root --loadSnapshot MultiDimFit --nToys 500 --POIs r_ggH,r_VBF,r_top,r_VH --batch condor --queue workday --ext _test_with_bands
python makeSplusBModelPlot.py --inputWSFile plots/2022-08-31-fits/sm_mu_simple/bestfit_syst_r_VBF.root --loadSnapshot MultiDimFit --cats all --doZeroes --pdir plots/2022-08-31-fits --ext _test_with_bands --translateCats cats.json --unblind --doBands --saveToyYields --doSumCategories --doCatWeights --saveWeights # first time, with bands calculation
python makeSplusBModelPlot.py --inputWSFile plots/2022-08-31-fits/sm_mu_simple/bestfit_syst_r_VBF.root --loadSnapshot MultiDimFit --cats all --doZeroes --pdir plots/2022-08-31-fits --ext _test_with_bands --translateCats cats.json --unblind --doBands --loadToyYields SplusBModels_test_with_bands/toys/toyYields_CMS_hgg_mass.pkl --doSumCategories --doCatWeights --saveWeights

# make tables with yields
python makeYieldsTables.py --inputPklDir ../Datacard/yields_2022-09-01_xsec --loadCatInfo pkl/catInfo_allCats.pkl --group qqh_ac --translateCats cats.json
