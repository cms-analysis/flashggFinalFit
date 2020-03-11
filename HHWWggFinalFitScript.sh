#!/bin/bash
#
#########################################################################################
# Abraham Tishelman-Charny                                                              #
# 11 March 2020                                                                         #
#                                                                                       #
# The purpose of this script is to run all fggfinalfit steps for the HHWWgg analysis    #
#########################################################################################

cmsenv 
# Background 
# python RunBackgroundScripts.py --inputConfig config_HHWWgg_v2-3_2017.py

# Signal
cd Signal
python RunSignalScripts.py --inputConfig config_HHWWgg_2017.py # signal models 

cd .. 
python RunCombineScripts.py datacard --inputConfig combine_config_HHWWgg_v2-3_2017.py # Make datacard 
python RunCombineScripts.py combine --inputConfig combine_config_HHWWgg_v2-3_2017.py # Run combine  

python plot_limits.py -AC 
python plot_limits.py -CMSC
python plot_limits.py -SM 

cd ../../ 