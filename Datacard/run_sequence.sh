python RunYields.py --cats VBFTag_1,VBFTag_3,VBFTag_5,VBFTag_6,VBFTag_7 --inputWSDirMap 2016=cards/cards_current/signal_2016,2017=cards/cards_current/signal_2017,2018=cards/cards_current/signal_2018 --procs auto --mergeYears --doSystematics --ext 2022-04-12 --batch condor --queue espresso --printOnly
python makeDatacard.py --years 2016,2017,2018 --ext 2022-04-12 --prune --doSystematics
cd Models ; rm signal background ; ln -s ../../Signal/outdir_packaged signal; ln -s ../../Background/outdir_2022-04-12 background

# for mu-simple: exclude ALT processes
python RunYields.py --cats VBFTag_1,VBFTag_3,VBFTag_5,VBFTag_6,VBFTag_7 --inputWSDirMap 2016=cards/cards_current/signal_2016,2017=cards/cards_current/signal_2017,2018=cards/cards_current/signal_2018 --procs GG2H,TTH,VBF,VH --mergeYears --doSystematics --ext 2022-04-12 --batch condor --queue espresso --printOnly
