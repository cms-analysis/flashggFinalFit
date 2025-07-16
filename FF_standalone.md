# FinalFits standalone setup instructions



## Setup FinalFits

```bash
mkdir src
cd src
FINALFIT_TAG=higgsdnafinalfit
git clone -b $FINALFIT_TAG https://github.com/cms-analysis/flashggFinalFit.git
cd flashggFinalFit
source setup_standalone.sh
```

## Install the environment

```bash
micromamba create -f environment.yaml
micromamba activate flashggFinalFit
```

## Build the Background modelling code

```bash
cd Background
make clean
make -j 8
cd -
```

## Download data from the lhc-hxswg (NOT optional, needed for the tutorial's physics model)

```bash
mkdir -p $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/data/lhc-hxswg
cd $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/data/lhc-hxswg
curl -L -o lhc-hxswg.tar.gz "https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit/archive/refs/heads/main.tar.gz"
tar -xzf lhc-hxswg.tar.gz --strip-components=3 HiggsAnalysis-CombinedLimit-main/data/lhc-hxswg
rm lhc-hxswg.tar.gz
cd -
```
