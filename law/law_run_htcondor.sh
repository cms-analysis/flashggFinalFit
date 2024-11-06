if [ $# -ne 1 ]; then
  echo "Usage: $0 <variable, eg. pt>"
  exit 1
fi

differential_variable="$1"
workers=2

law run Trees2WS --workers $workers --variable $differential_variable; law run Background --workers $workers --variable $differential_variable; law run FTest --workers $workers --variable $differential_variable; law run CalcPhotonSyst --workers $workers --variable $differential_variable; law run SignalFit --workers $workers --variable $differential_variable; law run SignalPackaging --workers $workers --variable $differential_variable; law run MakeYields --workers $workers --variable $differential_variable; law run MakeDatacard --workers $workers --variable $differential_variable; law run PrepareTheDirectory --variable $differential_variable; law run RunText2Workspace --workers $workers --variable $differential_variable; law run CreateAsimovFitFirstStep --workers $workers --variable $differential_variable; law run CreateAsimovFit --workers $workers --variable $differential_variable