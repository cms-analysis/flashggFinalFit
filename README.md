 ```
 cmsrel CMSSW_7_1_5
 cd CMSSW_7_1_5/src
 cmsenv
 git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
 git clone git@github.com:sethzenz/flashggFinalFit.git flashggFinalFit
 scram b -j 9
 ```

Two packages need to be built with their own makefiles, if needed.  Please note that there will be verbose warnings from BOOST etc:

 ```
 cd ${CMSSW_BASE}/src/flashggFinalFit/Background
 make
 cd ${CMSSW_BASE}/src/flashggFinalFit/Signal
 make
 ```
