workers=2

if [ -n "$differential_variable" ]; then

  differential_variable="$1"

  law run CreateUnblindedFit --workers $workers --variable $differential_variable; law run UnblindedImpactFirstStep --workers $workers --variable $differential_variable; law run UnblindedImpactSecondStep --workers $workers --variable $differential_variable; law run UnblindedImpactThirdStep --workers $workers --variable $differential_variable; law run MggBestFit --workers $workers --variable $differential_variable --workflow local --version $differential_variable; law run MggDistribution --workers $workers --variable $differential_variable --is-postfit False; law run MggDistribution --workers $workers --variable $differential_variable --is-postfit True
else
  law run CreateUnblindedFit --workers $workers; law run UnblindedImpactFirstStep --workers $workers; law run UnblindedImpactSecondStep --workers $workers; law run UnblindedImpactThirdStep --workers $workers, law run MggBestFit --workers $workers --workflow local --version r; law run MggDistribution --workers $workers --is-postfit False; law run MggDistribution --workers $workers --is-postfit True 
fi