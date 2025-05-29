outdate=`date +%F` 

STEP=0
usage(){
    echo "Script to run fits and plots of fit output. dryRun option is for the fitting only, that can be run in batch."
    echo "options:"
    
    echo "-h|--help) "
    echo "-s|--step) "
    echo "-d|--dryRun) "
}
# options may be followed by one colon to indicate they have a required argument
if ! options=$(getopt -u -o s:hd -l help,step:,dryRun -- "$@")
then
# something went wrong, getopt will put out an error message for us
exit 1
fi
set -- $options
while [ $# -gt 0 ]
do
case $1 in
-h|--help) usage; exit 0;;
-s|--step) STEP=$2; shift ;;
-d|--dryRun) DR=$2; shift ;;
(--) shift; break;;
(-*) usage; echo "$0: error - unrecognized option $1" 1>&2; usage >> /dev/stderr; exit 1;;
(*) break;;
esac
shift
done

DROPT=""
if [[ $DR ]]; then
    DROPT=" --dryRun "
fi


fits2D=("ALT_0M_ALT_0PH" "ALT_0M_ALT_L1" "ALT_0M_ALT_L1Zg" )
#"ALT_0PH_ALT_L1"  "ALT_0PH_ALT_L1Zg"  "ALT_L1_ALT_L1Zg" )
#fits=("ALT_0PH" )
fits=("ALT_0PH"  "ALT_L1" "ALT_L1Zg" "ALT_0M" )
fits=( "ALT_0M")
#"ALT_0M_ALT_L1" "ALT_0PH_ALT_L1Zg"  "ALT_0M_ALT_L1Zg" )

if [[ $STEP == "t2w" ]]; then
    for fit in ${fits[*]}
    do
        python RunText2Workspace.py --ext $fit --mode $fit --batch condor
    done

elif [[ $STEP == "t2w2D" ]]; then
    for fit in ${fits2D[*]}
    do
        python RunText2Workspace.py --ext $fit --mode $fit --batch condor
    done





elif [[ $STEP == "fit" ]]; then
    for obs in " "  #"--doObserved " 
    do
        for fit in ${fits[*]}
        do
            python RunFits.py --inputJson inputs_impact_Unblind_v2.json --queue tomorrow  --ext ${fit}  --mode $fit  ${DROPT} $obs
        done
    done
elif [[ $STEP == "fit2D" ]]; then
    for obs in "--doObserved " 
    do
        
        for fit in ${fits2D[*]}
        do
            python RunFits.py --inputJson inputs_impact_Unblind.json  --queue tomorrow --ext ${fit} --mode $fit  ${DROPT} $obs 
        done
    done

elif [[ $STEP == "collect" ]]; then
    for obs in   "--doObserved " " "
    do
	for fit in ${fits[*]}
	do
	    python CollectFits.py --inputJson inputs_impact_Unblind.json --ext ${fit} --mode $fit $obs
	done
   done

elif [[ $STEP == "collect2D" ]]; then
    for obs in   "--doObserved "
    do
	for fit in ${fits2D[*]}
	do 
        
	    python CollectFits.py --inputJson inputs_impact_Unblind.json --ext ${fit} --mode $fit $obs
	done
   done

elif [[ $STEP == "plot" ]]; then
   for fit in ${fits[*]}

    do

    if [[ $fit == "xsec" ]]; then 
       
	        pois=("r_ggH" "r_VBF" "r_VH" "r_top")
            pois=( "r_VH" )
	        translate="pois_mu.json"
            else 
            pois=("CMS_zz4l_fai1")
            translate="pois_${fit}.json"
	        fi


    cd runFits${fit}_${fit};  
    
    plot1DScan.py   profile1D_syst_${fit}_CMS_zz4l_fai1.root --y-cut 30 --y-max 30 -o ../plots/profile1D_syst_${fit}_CMS_zz4l_fai1${fit} --POI CMS_zz4l_fai1 --main-label Expected --translate /afs/cern.ch/work/f/fderiggi/private/CMSSW_10_2_13/src/flashggFinalFit/Plots/${translate=};
    plot1DScan.py   profile1D_syst_obs_${fit}_CMS_zz4l_fai1.root --y-cut 30 --y-max 30 -o ../plots/profile1D_syst_obs_${fit}_CMS_zz4l_fai1${fit} --POI CMS_zz4l_fai1 --main-label Expected --translate /afs/cern.ch/work/f/fderiggi/private/CMSSW_10_2_13/src/flashggFinalFit/Plots/${translate=};
    
     cd ..
	 
     

   done
elif [[ $STEP == "plot_ExpObserved" ]]; then
        for fit in ${fits[*]}
        do 
        
        	if [[ $fit == "xsec" ]]; then 
       
	        pois=("r_ggH" "r_VBF" "r_VH" "r_top")
            pois=( "r_VH" )
	        translate="pois_mu.json"
            else 
            pois=("CMS_zz4l_fai1")
            translate="pois_${fit}.json"
	        fi

            if [[ $fit == "ALT_0M" ]]; then 
            string="runFits${fit}_${fit}/profile1D_syst_obs_${fit}_CMS_zz4l_fai1.root:Observed:2"
            python plot1DScanBug.py runFits${fit}_${fit}/profile1D_syst_${fit}_${pois}.root   --y-cut 30 --y-max 30 -o  plots_breakdown/Obs_Exp_${fit}_${pois} --POI ${pois} --main-label Expected --translate "../Plots/${translate}"  --others $string --Not_showPoints --Not_show1sigma
            else
	        for poi in ${pois[*]}
	            do              
                 string="runFits${fit}_${fit}/profile1D_syst_obs_${fit}_${poi}.root:Observed:2"
                 python plot1DScanBug.py   runFits${fit}_${fit}/profile1D_syst_${fit}_${poi}.root   --y-cut 30 --y-max 30 -o  plots_breakdown/Obs_Exp_${fit}_${poi} --POI ${poi} --main-label Expected --translate "../Plots/${translate}"  --others $string --Not_showPoints --Not_show1sigma
                done
            fi
    done
elif [[ $STEP == "impacts-initial" ]]; then
    for fit in ${fits[*]} 
    do
	python RunImpacts.py  --doObserved --inputJson inputs_impact_Unblind.json --ext $fit --mode $fit --queue tomorrow   ${DROPT}
    done
elif [[ $STEP == "impacts-scans" ]]; then
    for fit in ${fits[*]}
    do
	python RunImpacts.py  --doObserved --inputJson inputs_impact_Unblind.json   --ext $fit --mode $fit --doFits  --queue tomorrow  ${DROPT}
    done
elif [[ $STEP == "impacts-collect" ]]; then
    for fit in ${fits[*]}
    do
	echo "Making JSON file for fit $fit It might take time, depending on the number of parameters..."
	if [[ $fit == "xsec" ]]; then 
	    pois=("r_ggH" "r_VBF" "r_VH" "r_top")
	    translate="pois_mu.json"
   else 
       pois=("CMS_zz4l_fai1")
       translate="pois_${fit}.json"
	fi
	for poi in ${pois[*]}
	do
      cd runImpacts${fit}_${fit} 
        combineTool.py -M Impacts -n _bestfit_syst_obs_${fit}_initialFit -d ../Datacard_${fit}.root -i impacts_${fit}.json -m 125.38 -o impacts_${poi}.json --doObserved 
	   # combineTool.py -M Impacts -n _bestfit_syst_${fit}_initialFit -d ../Datacard_${fit}.root -i impacts_${fit}.json -m 125.38 -o impacts_${poi}.json
	    echo " combineTool.py -M Impacts -n _bestfit_syst_${fit}_initialFit -d ../Datacard_${fit}.root -i impacts_${fit}.json -m 125.38 -o impacts_${poi}"
	    echo "    ===> Producing impact plots for the *** main-only *** systematics for fit: === $fit === and POI: == $poi === "
      cd - 
#	    combineTool.py -M Impacts -n _bestfit_syst_${fit}_initialFit -d ../Datacard_${fit}.root -i impacts_${fit}.json -m 125.38 -o impacts_${poi}.json
	    plotImpacts.py   -i runImpacts${fit}_${fit}/impacts_${poi}.json -o ./impacts_obs_${poi}_${fit}_allpages --POI ${poi}   --translate "../Plots/${translate}" --blind
	   # plotImpacts.py   -i runImpacts${fit}_${fit}/impacts_${poi}.json -o plot_impact/impacts_obs_${poi}_${fit}          --POI ${poi}   --translate "../Plots/${translate}" --blind  --max-pages 1
       echo "plotImpacts.py   -i impacts_${poi}.json -o ../plot_impact/impacts_${poi}_${fit}_all_pages --POI ${poi}   --translate "../../Plots/${translate}" --max-pages "1
	done
    done


    elif [[ $STEP == "plot_ScanProfile" ]]; then
    for obs in " " " --doObserved "
    do
        for fit in ${fits[*]}
        do
           translate="pois_${fit}.json"
           string="runFits${fit}_${fit}/profile1D_syst_${fit}_CMS_zz4l_fai1.root:floating:2"
           python plot1DScanBug.py runFits${fit}_${fit}/scan1D_syst_${fit}_CMS_zz4l_fai1.root   --y-cut 30 --y-max 30 -o  plots_scan/Profile_Scan_${fit} --POI CMS_zz4l_fai1 --main-label fix --translate "../Plots/${translate}"  --others $string
      
        done
    done

    

    elif [[ $STEP == "plot2D" ]]; then
    for obs in  "_obs"
   #" --doObserved "
    do 
        python plot_2D_scan.py  --mode ALT_0M  --ext ALT_0M  --outdir plots/Scan2D_ALT_0M_muV_ONLYVBF --poi  CMS_zz4l_fai1,muV --obs ${obs}
        for fit in ${fits2D[*]}
        do
            echo ok
           # python plot_2D_scan.py  --mode ${fit}  --ext ${fit}_NoTTH --outdir plots/Scan2D_${fit}  --obs ${obs}
        done
    done



else
    echo "Step $STEP is not one among t2w,fit,plot. Exiting."
fi

