#!/bin/bash
#
#########################################################################################
# Abraham Tishelman-Charny                                                              #
# 11 March 2020                                                                         #
#                                                                                       #
# The purpose of this script is to run all fggfinalfit steps for the HHWWgg analysis    #
#                                                                                       #
# Example usage:                                                                        #
# . HHWWggFinalFitScript.sh background                                                  #
# . HHWWggFinalFitScript.sh signal                                                      #
#########################################################################################

step=$1

cmsenv 
#-- Background 
if [ $step == "backgroundftest" ]; then 
    cd Background 
    # python RunBackgroundScripts.py fTestOnly --inputConfig config_HHWWgg_v2-3_2017.py
    python RunBackgroundScripts.py fTestOnly --inputConfig config_HHWWgg_v2-3_2017_2Cats.py
    cd .. 
fi

if [ $step == "backgroundplots" ]; then 
    cd Background 
    python RunBackgroundScripts.py bkgPlotsOnly --inputConfig config_HHWWgg_v2-3_2017.py
    # python RunBackgroundScripts.py bkgPlotsOnly --inputConfig config_HHWWgg_v2-3_2017_2Cats.py
    cd .. 
fi

#-- Signal
if [ $step == "signal" ]; then 
    cd Signal
    # python RunSignalScripts.py --inputConfig config_HHWWgg_2017.py # signal models 
    python RunSignalScripts.py --inputConfig config_HHWWgg_2017_2Cats.py # signal models 
    cd .. 
fi

#-- Datacards
if [ $step == "datacard" ]; then 
    python RunCombineScripts.py datacard --inputConfig combine_config_HHWWgg_v2-3_2017_2Cats.py # Make datacard 
    # python RunCombineScripts.py datacard --inputConfig combine_config_HHWWgg_v2-3_2017.py # Make datacard 
fi

#-- Combine 
if [ $step == "combine" ]; then 
    python RunCombineScripts.py combine --inputConfig combine_config_HHWWgg_v2-3_2017_2Cats.py # Run combine   
    # python RunCombineScripts.py combine --inputConfig combine_config_HHWWgg_v2-3_2017.py # Run combine   
fi

#-- Plots 
if [ $step == "plot" ]; then
    cd Plots/FinalResults/
    tagLabel="2TotCatsCOMBINEDWithSyst"
    # SecondTagLabel="2TotCatsCOMBINEDWithoutSyst"
    # tagLabel="2TotCatsTag0WithSyst"
    # SecondTagLabel="2TotCatsTag0WithoutSyst"    

    ##- Grid 
    # python plot_limits.py -a -g --GridLabels 2TotCatsCOMBINEDWithSyst 2TotCatsCOMBINEDWithoutSyst 2TotCatsTag0WithSyst 2TotCatsTag0WithoutSyst 2TotCatsTag1WithSyst 2TotCatsTag1WithoutSyst 1TotCatWithSyst 1TotCatWithoutSyst
    #  python plot_limits.py -a -g --GridLabels 2TotCatsTag0WithoutSyst 2TotCatsTag0WithSyst 2TotCatsTag1WithoutSyst 2TotCatsTag1WithSyst 1TotCatWithoutSyst 1TotCatWithSyst 2TotCatsCOMBINEDWithoutSyst 2TotCatsCOMBINEDWithSyst
    #python plot_limits.py -a -g --GridLabels 2TotCatsTag0WithSyst 2TotCatsTag1WithSyst 1TotCatWithSyst 2TotCatsCOMBINEDWithSyst

    ##- Ratio plots 
     #python plot_limits.py -a --HHWWggCatLabel $tagLabel --systematics 
     #python plot_limits.py -a --HHWWggCatLabel $SecondTagLabel 
     #python plot_limits.py -a -r --HHWWggCatLabel $tagLabel --SecondHHWWggCatLabel $SecondTagLabel # ratio of all points
     #python plot_limits.py -SM --HHWWggCatLabel $tagLabel --systematics
     #python plot_limits.py -SM --HHWWggCatLabel $SecondTagLabel 
     #python plot_limits.py -SM -r --HHWWggCatLabel $tagLabel --SecondHHWWggCatLabel $SecondTagLabel # ratio of SM   
    
    ##- Comparison plots 
    # python plot_limits.py -AC --HHWWggCatLabel  $tagLabel --systematics --campaign HHWWgg_v2-3_2017 --resultType WWgg --unit pb --ymin 1.000001 --ymax 1 --yboost 0.09 # atlas compare 
    # python plot_limits.py -CMSC --HHWWggCatLabel  $tagLabel --systematics --campaign HHWWgg_v2-3_2017 --resultType HH --unit fb --ymin 10 --ymax 1e5 --yboost -0.2 # atlas compare 
    # python plot_limits.py --EFT --HHWWggCatLabel $tagLabel --systematics --campaign HHWWgg_v2-3_2017 --resultType HH --unit fb --ymin 10 --ymax 1e6 --yboost -0.225 # standard model 
    python plot_limits.py --NMSSM --HHWWggCatLabel $tagLabel --systematics --campaign HHWWgg_v2-4_2017 --resultType HH --unit fb --ymin 10 --ymax 1e6 --yboost -0.225 # standard model 
    # NMSSM: 2TotCatsCOMBINEDWithSyst_limits/HHWWgg_v2-4_2017_MX300_MY170_2TotCatsCOMBINEDWithSyst_HHWWgg_qqlnu.root
    # EFT: 2TotCatsCOMBINEDWithSyst_limits/HHWWgg_v2-3_2017_node2_2TotCatsCOMBINEDWithSyst_HHWWgg_qqlnu.root
    cd ../../ 
fi
