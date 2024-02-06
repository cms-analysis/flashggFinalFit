#!/usr/bin/env bash

set -e

sig_model=$1
res_bkg_model=$2
m=$3
mh=$4
mx=$5
my=$6
dy_bkg_model=$7
procTemplate=$8
indir=$9

get_last_cat() {
  for cat in $(grep "bin " $1 ) ; do
    last_cat=$cat
  done
  echo $last_cat
}

pushd Datacard
  if [ $dy_bkg_model = 0 ]; then 
    python makeDatacardGGTT_new.py -o Datacard_${procTemplate}_${m}.txt --n-in-sideband $indir/../CatOptim/N_in_sidebands.json --MH $mh --MX $mx --MY $my --procTemplate ${procTemplate} --prune --do-res-bkg --sig-syst $indir/../Interpolation/systematics.json

    #python makeDatacardGGTT_new.py -o Datacard_${procTemplate}_${m}.txt --MH $mh --MX $mx --MY $my --prune --sig-syst ${sig_model}/systematics.json --res-bkg-syst ${res_bkg_model}/systematics.json --do-res-bkg
    #python makeDatacardGGTT_new.py -o Datacard_${procTemplate}_${m}.txt --MH $mh --MX $mx --MY $my --prune --sig-syst ${sig_model}/systematics.json --res-bkg-syst ${res_bkg_model}/systematics.json --doABCD
  else
    python makeDatacardGGTT_new.py -o Datacard_${procTemplate}_${m}.txt --n-in-sideband $indir/../CatOptim/N_in_sidebands.json --MH $mh --MX $mx --MY $my --procTemplate ${procTemplate} --prune --do-res-bkg --sig-syst $indir/../Interpolation/systematics.json --doABCD
    #python makeDatacardGGTT_new.py -o Datacard_${procTemplate}_${m}.txt --n-in-sideband $indir/../CatOptim/N_in_sidebands.json --MH $mh --MX $mx --MY $my --procTemplate ${procTemplate} --prune --sig-syst ${sig_model}/systematics.json --res-bkg-syst ${res_bkg_model}/systematics.json --do-res-bkg --doABCD
    #python makeDatacardGGTT_new.py -o Datacard_${procTemplate}_${m}.txt --MH $mh --MX $mx --MY $my --prune --sig-syst ${sig_model}/systematics.json --res-bkg-syst ${res_bkg_model}/systematics.json
  fi
popd
