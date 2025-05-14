workers=24

if [ -n "$1" ]; then

  differential_variable="$1"

  law run Trees2WS --workers $workers --variable $differential_variable --year 2023; law run Background --workers $workers --variable $differential_variable --year 2023; law run FTest --workers $workers --variable $differential_variable --year 2023; law run CalcPhotonSyst --workers $workers --variable $differential_variable --year 2023; law run SignalFit --workers $workers --variable $differential_variable --year 2023; law run SignalPackaging --workers $workers --variable $differential_variable --year 2023; law run MakeYields --workers $workers --variable $differential_variable --year 2023; law run MakeDatacard --workers $workers --variable $differential_variable --year 2023; law run PrepareTheDirectory --variable $differential_variable --year 2023; law run RunText2Workspace --workers $workers --variable $differential_variable --year 2023; law run CreateAsimovFitFirstStep --workers $workers --variable $differential_variable --year 2023; law run CreateAsimovFit --workers $workers --variable $differential_variable --year 2023
else
  law run RunText2Workspace --workers $workers
  # law run Trees2WS --workers $workers ; law run Background --workers $workers ; law run FTest --workers $workers ; law run CalcPhotonSyst --workers $workers ; law run SignalFit --workers $workers ; law run SignalPackaging --workers $workers ; law run MakeYields --workers $workers ; law run MakeDatacard --workers $workers ; law run PrepareTheDirectory ; law run RunText2Workspace --workers $workers ; law run CreateAsimovFitFirstStep --workers $workers ; law run CreateAsimovFit --workers $workers 
fi