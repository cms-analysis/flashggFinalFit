if [ $# -ne 1 ]; then
  echo "Usage: $0 <variable, eg. pt>"
  exit 1
fi

differential_variable="$1"

law run Trees2WS --workers 8 --variable $differential_variable; law run Background --workers 8 --variable $differential_variable; law run FTest --workers 8 --variable $differential_variable; law run CalcPhotonSyst --workers 8 --variable $differential_variable; law run SignalFit --workers 8 --variable $differential_variable; law run SignalPackaging --workers 8 --variable $differential_variable; law run MakeYields --workers 8 --variable $differential_variable; law run MakeDatacard --workers 8 --variable $differential_variable