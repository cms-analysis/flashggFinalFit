python RunYields.py --cats auto --inputWSDirMap 2016=cards/cards_current/signal_2016,2017=cards/cards_current/signal_2017,2018=cards/cards_current/signal_2018 --procs auto --ext 2022-04-12 --batch condor --queue espresso --printOnly
python makeDatacard.py --years 2016,2017,2018 --ext 2022-04-12 --prune
cd Models ; rm signal background ; ln -s ../../Signal/outdir_packaged signal; ln -s ../../Background/outdir_2022-04-12 background

