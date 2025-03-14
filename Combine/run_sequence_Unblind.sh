

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

fits=("ALT_L1" "ALT_L1Zg" "ALT_0PH" "ALT_0M" "xsec")



if [[ $STEP == "fit" ]]; then
    for obs in " --doObserved " " "
    do
        for fit in ${fits[*]}
        do
            python RunFits.py --inputJson inputs_impact_Unblind.json  --ext ${fit} --mode $fit  ${DROPT} $obs
        done
    done
elif [[ $STEP == "collect" ]]; then
    for obs in " --doObserved " " "
    do
	for fit in ${fits[*]}
	do
	    python CollectFits.py --inputJson inputs_impact_Unblind.json  --ext  ${fit} --mode $fit $obs
	done
   done

elif [[ $STEP == "plot" ]]; then
 for fit in ${fits[*]}
        do
    if [[ $fit == "xsec" ]]; then 
	    pois=("r_ggH" "r_VBF" "r_VH" "r_top")
	    translate="pois_mu.json"
   else 
       pois=("CMS_zz4l_fai1")
       translate="pois_${fit}.json"
	fi
       
          for poi in ${pois[*]}
            do
            string="runFits${fit}_${fit}/profile1D_statonly_obs_${fit}_${poi}.root:Stat_Only:2"
            #python plot1DScanBug.py runFits${fit}_GGH_${fit}/profile1D_syst_${fit}_GGH_CMS_zz4l_fai1.root   --y-cut 4 --y-max 4 -o  plots_breakdown/Breakdown_${fit} --POI CMS_zz4l_fai1 --main-label GGH --translate ../Plots/pois_fa3.json --others $string
             plot1DScan.py runFits${fit}_${fit}/profile1D_syst_obs_${fit}_${poi}.root --y-cut 10 --y-max 10  -o   plots/Breakdown_SystStat_${poi}_${fit} --POI ${poi} --main-label Observed --translate ../Plots/${translate} --others $string
        done
    done

elif [[ $STEP == "impacts-initial" ]]; then
    for fit in ${fits[*]} 
    do
	python RunImpacts.py  --doObserved --inputJson inputs_impact.json --ext $fit --mode $fit --queue workday   ${DROPT}
    done
elif [[ $STEP == "impacts-scans" ]]; then
    for fit in ${fits[*]}
    do
	python RunImpacts.py --doObserved --inputJson inputs_impact.json --ext ${fit} --mode $fit --doFits  --queue tomorrow  ${DROPT}
    done
elif [[ $STEP == "impacts-collect" ]]; then
    for fit in ${fits[*]}
    do
	#cd runImpacts${fit}_${fit}
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
	   #combineTool.py -M Impacts -n _bestfit_syst_obs_${fit}_initialFit -d ../Datacard_${fit}.root -i impacts_${fit}.json -m 125.38 -o impacts_${poi}.json --doObserved 
	   echo " combineTool.py -M Impacts -n _bestfit_syst_${fit}_initialFit -d ../Datacard_${fit}.root -i impacts_${fit}.json -m 125.38 -o impacts_${poi}"
	   echo "    ===> Producing impact plots for the *** main-only *** systematics for fit: === $fit === and POI: == $poi === "
       cd - 
	
	   echo "python3 ../Plots/correctImpacts.py --impactsJson runImpacts${fit}_${fit}/impacts_${poi}.json --dropBkgModelParams    --frozenParam MH"
       #python3 ../Plots/correctImpacts.py --impactsJson runImpacts${fit}_${fit}/impacts_${poi}.json --dropBkgModelParams    --frozenParam MH
       #python3 ../Plots/correctImpacts.py --impactsJson runImpacts${fit}_${fit}/impacts_${poi}.json --dropBkgModelParams --frozenParam MH
       plotImpacts.py -i runImpacts${fit}_${fit}/impacts_${poi}.json  -o  ./impacts_obs_${poi}_${fit}  --POI ${poi}   --translate "../Plots/${translate}" --blind  --max-pages 1
       plotImpacts.py -i runImpacts${fit}_${fit}/impacts_${poi}.json -o  ./impacts_obs_${poi}_${fit}_allpages  --POI ${poi}   --translate "../Plots/${translate}" --blind  
       

	done
    done

    elif [[ $STEP == "plot_ExpObserved" ]]; then
        for fit in ${fits[*]}
        do 
        
        	if [[ $fit == "xsec" ]]; then 
       
	        pois=("r_ggH" "r_VBF" "r_VH" "r_top")
	        translate="pois_mu.json"
            else 
            pois=("CMS_zz4l_fai1")
            translate="pois_${fit}.json"
	        fi

            if [[ $fit == "ALT_0M" ]]; then 
            string="runFits${fit}_${fit}/profile1D_syst_obs_${fit}_${pois}.root:Observed:2"
            python plot1DScanBug.py runFits${fit}_${fit}/profile1D_syst_${fit}_${pois}.root   --y-cut 30 --y-max 30 -o  plots/Obs_Exp_${fit}_${pois} --POI ${pois} --main-label Expected --translate "../Plots/${translate}"  --others $string
            else
	        for poi in ${pois[*]}
	            do              
                 string="runFits${fit}_${fit}/profile1D_syst_obs_${fit}_${poi}.root:Observed:2"
                 plot1DScan.py runFits${fit}_${fit}/profile1D_syst_${fit}_${poi}.root   --y-cut 30 --y-max 30 -o  plots/Obs_Exp_${fit}_${poi} --POI ${poi} --main-label Expected --translate "../Plots/${translate}"  --others $string
                done
            fi
    done



else
    echo "Step $STEP is not one among t2w,fit,plot. Exiting."
fi

