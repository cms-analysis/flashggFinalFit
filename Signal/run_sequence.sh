python RunSignalScripts.py --inputConfig config_test_2017.py --mode fTest --modeOpts "--xvar dipho_mass --doPlots --outdir plots" --printOnly
python RunSignalScripts.py --inputConfig config_test_2017.py --mode signalFit --modeOpts="--skipSystematics --xvar dipho_mass --doPlots --outdir plots" --printOnly
python RunPackager.py --cats auto --inputWSDir cards/cards_fithgg/2017/ --exts test1_2017 --mergeYears --printOnly
python RunPlotter.py --procs all --cats all --years 2017 --ext packaged --outdir plots

