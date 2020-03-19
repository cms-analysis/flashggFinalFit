#!/bin/bash
#
#########################################################################################
# Abraham Tishelman-Charny                                                              #
# 11 March 2020                                                                         #
#                                                                                       #
# The purpose of this script is to run all fggfinalfit steps for the HHWWgg analysis    #
#########################################################################################

cmsenv 
#-- Background 
# cd Background 
# python RunBackgroundScripts.py --inputConfig config_HHWWgg_v2-3_2017_2Cats.py

#-- Signal
# cd Signal
# python RunSignalScripts.py --inputConfig config_HHWWgg_2017_2Cats.py # signal models 
# cd .. 

python RunCombineScripts.py datacard --inputConfig combine_config_HHWWgg_v2-3_2017_2Cats.py # Make datacard 
# python RunCombineScripts.py combine --inputConfig combine_config_HHWWgg_v2-3_2017.py # Run combine  

# cd Plots/FinalResults/
# python plot_limits.py -a # all points  
# python plot_limits.py -AC # atlas compare 
# python plot_limits.py -CMSC # cms compare 
# python plot_limits.py -SM # standard model 

# cd ../../ 