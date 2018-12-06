datacard=CMS-HGG_mva_13TeV_datacard.root
#datacard=CMS-HGG_mva_13TeV_datacard_PPCC_pMH_qqHPerProcessChannelCompatibility.root
#proc=qqH

dirname=r_impacts
mkdir $dirname 
cp $datacard $dirname/.
cd $dirname
echo "===============step 1========"
echo "combineTool.py -M Impacts -d $datacard -m 125 --doInitialFit --robustFit 1 -P r --expectSignal=1 -t -1"
echo "============================="
combineTool.py -M Impacts -d $datacard -m 125 --doInitialFit --robustFit 1 -P r --expectSignal=1 -t -1
echo "===============step 2========"
echo "combineTool.py -M Impacts -d $datacard -m 125 --robustFit 1 --redefineSignalPOIs r --doFits --expectSignal=1 -t -1 --job-mode SGE --task-name final --sub-opts='-q hep.q -l h_rt=3:00:0'"
echo "============================="
combineTool.py -M Impacts -d $datacard -m 125 --robustFit 1 --redefineSignalPOIs r --doFits --expectSignal=1 -t -1 --job-mode SGE --task-name final --sub-opts='-q hep.q -l h_rt=3:00:0'
RUN=1
while (( $RUN > 0 )) ; do
  RUN=`qstat |wc -l`
  echo "Running $RUN jobs"
  sleep 30
done
echo "===============step 3========"
echo "combineTool.py -M Impacts -d $datacard --redefineSignalPOIs r  --expectSignal=1 -t -1 -m 125 -o impacts.json"
echo "============================="
combineTool.py -M Impacts -d $datacard --redefineSignalPOIs r  --expectSignal=1 -t -1 -m 125 -o impacts.json
echo "===============step 4========"
echo "plotImpacts.py -i impacts.json -o impacts"
echo "============================="
plotImpacts.py -i impacts.json -o impacts
cd -
cp $dirname/impacts.pdf .
