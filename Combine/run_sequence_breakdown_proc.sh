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

fits=( "ALT_0PH" )
ext2=("GGH")




if [[ $STEP == "txt" ]];then
   for fit in ${fits[*]}
   do 
    combineCards.py Datacard_${fit}_NO_SYST.txt --ic=".*J_.*|.*RECO_PTH.*|.*VBFLIKEGGH.*" > Datacard_${fit}_GGH.txt
    awk '!/pdfindex/ || /.*J_.*|.*RECO_PTH.*|.*VBFLIKEGGH.*/' Datacard_${fit}_GGH.txt > test.txt && mv test.txt Datacard_${fit}_GGH.txt

    combineCards.py Datacard_${fit}_NO_SYST.txt --ic=".*TTH.*" > Datacard_${fit}_TTH.txt
    awk '!/pdfindex/ || /.*TTH.*/' Datacard_${fit}_TTH.txt > test.txt && mv test.txt Datacard_${fit}_TTH.txt

    combineCards.py Datacard_${fit}_NO_SYST.txt --ic=".*VHHAD.*" > Datacard_${fit}_VHHAD.txt
    awk '!/pdfindex/ || /.*VHHAD.*/' Datacard_${fit}_VHHAD.txt > test.txt && mv test.txt Datacard_${fit}_VHHAD.txt

    combineCards.py Datacard_${fit}_NO_SYST.txt --ic=".*VBFTOPO_ACVBF.*|.*VBFTOPO_ACGGH.*" > Datacard_${fit}_VBF.txt
    awk '!/pdfindex/ || /.*VBFTOPO_ACVBF.*|.*VBFTOPO_ACGGH.*/' Datacard_${fit}_VBF.txt > test.txt && mv test.txt Datacard_${fit}_VBF.txt

    combineCards.py Datacard_${fit}_NO_SYST.txt --ic=".*VH_MET.*" > Datacard_${fit}_VHMET.txt
    awk '!/pdfindex/ || /.*VH_MET.*/' Datacard_${fit}_VHMET.txt > test.txt && mv test.txt Datacard_${fit}_VHMET.txt

    combineCards.py Datacard_${fit}_NO_SYST.txt --ic=".*_LEP_Tag.*" > Datacard_${fit}_VHLEP.txt
    awk '!/pdfindex/ || /.*_LEP_Tag.*/' Datacard_${fit}_VHLEP.txt > test.txt && mv test.txt Datacard_${fit}_VHLEP.txt
   done
elif [[ $STEP == "t2w" ]]; then
  for fit in ${fits[*]}
    do 
        for ext in ${ext2[*]}
            do 
                echo python RunText2Workspace.py --ext ${fit}_${ext} --mode ${fit}
                python RunText2Workspace.py --ext ${fit}_${ext} --mode ${fit}
            done
    done

elif [[ $STEP == "fit" ]]; then

for fit in ${fits[*]}
    do
    for obs in " " 
    # " --doObserved "
        do
            for ext in ${ext2[*]}
                        do
                        echo python RunFits.py --inputJson inputs.json --ext ${fit}_${ext} --mode $fit  ${DROPT} $obs
                        python RunFits.py --inputJson inputs.json --ext ${fit}_${ext} --mode ${fit}  ${DROPT} $obs
                        done 
        done
    done
elif [[ $STEP == "collect" ]]; then
    for obs in " "
    # " --doObserved "
    do
	for fit in ${fits[*]}
	do
            for ext in ${ext2[*]}
            do
	            python CollectFits.py --inputJson inputs.json --ext ${fit}_${ext} --mode $fit $obs
	done
   done
   done
elif [[ $STEP == "plot" ]]; then
    for obs in " " 
   #" --doObserved "
    do
        for fit in ${fits[*]}
        do
           string="runFits${fit}_TTH_${fit}/profile1D_syst_${fit}_TTH_CMS_zz4l_fai1.root:TTH:2 runFits${fit}_VBF_${fit}/profile1D_syst_${fit}_VBF_CMS_zz4l_fai1.root:VBF:3 runFits${fit}_VHHAD_${fit}/profile1D_syst_${fit}_VHHAD_CMS_zz4l_fai1.root:VHHAD:4  runFits${fit}_VHMET_${fit}/profile1D_syst_${fit}_VHMET_CMS_zz4l_fai1.root:VH-MET:9 runFits${fit}_VHLEP_${fit}/profile1D_syst_${fit}_VHLEP_CMS_zz4l_fai1.root:VH-LEP:46"
           plot1DScan.py runFits${fit}_GGH_${fit}/profile1D_syst_${fit}_GGH_CMS_zz4l_fai1.root   --y-cut 30 --y-max 30 -o  plots/Breakdown --POI CMS_zz4l_fai1 --main-label GGH --translate ../Plots/pois_fa3.json --others $string
        done
    done
else
    echo "Step $STEP is not one among t2w,fit,plot. Exiting."
fi

